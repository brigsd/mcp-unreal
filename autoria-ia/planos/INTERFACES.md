> Cópia histórica desde 19/09/2026. O AnimAI agora tem raiz própria.
> Fonte atual: [docs/desenvolvimento/interfaces.md](../../../AnimAI/docs/desenvolvimento/interfaces.md).
> O conteúdo abaixo foi preservado para consulta e não governa trabalho novo.

# Interfaces de implementação — v1

Especificação técnica do [plano](README.md), subordinada ao
[contrato](../CONTRATO.md). Nada deste documento está implementado ainda.
As assinaturas são nossas fronteiras; não supõem APIs equivalentes nos fornecedores.

## API e tipos compartilhados

AnimAI é a identidade do conjunto; `animai` é o pacote Python planejado e
`animai.describe` a descoberta pública. São nomes futuros, não comandos já
instalados. A referência pública de uso será gerada dos schemas; este documento
pertence à trilha de desenvolvimento, não é leitura obrigatória para operar.

Implementar em `src/animai/api.py`:

```python
from pathlib import Path

class Studio:
    def __init__(self, workspace: Path, settings: dict | None = None):
        self.workspace = workspace
        self.settings = settings or {}

    def call(self, operation: str, payload: dict) -> dict:
        request = self.registry.validate(operation, payload)
        return self.services.dispatch(operation, request)
```

`registry` e `services` são colaboradores inicializados pelo construtor em A1;
não são globais. `Registry.validate(operation: str, payload: dict) -> dict`
aplica Pydantic com `extra='forbid'`. `Services.dispatch(operation: str,
request: dict) -> dict` chama o serviço registrado; não usa `eval`, import pelo
usuário ou interpretação de código. Ambos serão definidos em
`core/catalogo.py` e `core/servicos.py`.

Requisição desconhecida ou inválida retorna erro estruturado, sem iniciar worker.
Uma operação planejada mas não disponível retorna `CAPABILITY_UNAVAILABLE`.
A descoberta informa `planned`, `unavailable` ou `available`, com motivo e
operações suportadas por backend/perfil. Disponível requer um recibo de
homologação compatível com versões atuais; ter um executável no PATH não basta.

Todos os dicionários abaixo terão modelos Pydantic e JSON Schemas exportados
em `schemas/`. Arrays não passam como listas gigantes no MCP: manifestos
referenciam artefatos numéricos carregados com `allow_pickle=False`.

### Envelope de resposta

```json
{
  "schema_version": "1.0",
  "operation": "motion.patch",
  "status": "ready",
  "job_id": "job-local-1",
  "motion_id": "motion-local-1",
  "base_revision_id": "rev-base",
  "revision_id": "rev-candidate",
  "data": {},
  "quality": {
    "technical": "passed",
    "visual": "not_reviewed",
    "destination": "not_evaluated"
  },
  "violations": [],
  "artifacts": [],
  "error": null
}
```

Estados da tarefa: `queued`, `running`, `validating`, `ready`, `failed`,
`cancelled`. IDs não pertinentes são `null`; `data` usa schema da operação.
`quality.technical` aceita `passed`, `failed`, `not_evaluated`; revisão visual
e avaliação de destino nunca são inferidas de um processo encerrado sem erro.
Erro contém `code`, `message`, `details` e `retryable`. Violações contêm `code`,
`parts`, `samples`, `measurement`, `limit`, `unit`, `reference` e `evidence_level`.

`ready` significa tarefa concluída, não aprovação artística. Uma edição só
recebe `revision_id` utilizável depois de passar todos os gates obrigatórios
solicitados; resultados reprovados ficam como artefatos de diagnóstico. Em
E2, a prova cobre esqueleto; quando o pedido exige superfície, a ausência de
B2 impede promoção e precisa ser declarada.

### Requisições das sete operações

| Operação | Campos obrigatórios e variantes |
| --- | --- |
| `animai.describe` | Payload vazio ou `module`; devolve catálogo, schemas e estado dos ambientes. Não inicia tarefas pesadas. |
| `actor.register` | `source` com `format` e `path`, `profile` e `request_id`. Formato inicial `bundle`; `gltf`, `fbx` e `unreal` só após seus gates. |
| `motion.build` | `actor_id`, `source`, `request_id`; fonte `bundle`, `revision`, `recipe` ou `generator`, habilitada por capacidade. Retarget exige `mapping_id` explícito. |
| `motion.patch` | `mode='apply'`, `motion_id`, `base_revision_id`, `expected_head`, `edit`, `request_id`; ou `mode='select_revision'`, `motion_id`, `revision_id`, `expected_head`, `request_id`. |
| `motion.inspect` | `revision_id`, `checks`, `request_id`; `base_revision_id`, `views` e `destination_profile` quando solicitados. |
| `motion.publish` | `revision_id`, `destination`, `request_id`; ação `candidate` ou `promote` explícita. `promote` exige recibo aprovado e referência esperada no destino. |
| `job.control` | `action='status'|'cancel'|'resume'|'release'`, `job_id`. `release` só alcança processos/reservas daquele job. |

`request_id` é chave de idempotência por workspace e operação. Repetição com o
mesmo conteúdo retorna a mesma tarefa; conteúdo diferente gera
`IDEMPOTENCY_CONFLICT`. `motion_id` identifica uma linhagem. `expected_head`
protege sua revisão de trabalho atual; aprovação artística é uma referência
separada e nunca muda implicitamente. Selecionar revisão altera somente a
referência de trabalho, sem apagar descendentes.

Publicação inicial escreve apenas candidatos. Promoção nunca é uma conclusão
automática da inspeção. Fonte externa é lida somente em raízes configuradas;
destino só pode ser escrito em raízes permitidas. Resolver caminhos e links
antes de conferir contenção, incluindo junctions no Windows. URI arbitrária,
download automático, scripts embutidos e execução Python fornecida pelo cliente
não fazem parte dessas operações.

## Pacote canônico

Manifesto JSON UTF-8 + arrays `.npz`, sem objetos serializados executáveis.
JSON canônico usa chaves ordenadas, sem NaN/Infinity; o hash combina manifesto
normalizado e bytes dos arrays com dtype/shape/ordem definidos, não timestamps
de ZIP. Armazenar o arquivo original e a versão convertida separadamente.

```text
character.json: schema_version, character_id, joints, rest, mesh, anchors,
                limits, coordinate_system, provenance, capabilities
motion.json:    schema_version, kind, actor_id, joint_ids, sample_rate, sample_count,
                arrays, curves, events, contacts, loop, provenance
arrays.npz:    translation[N,J,3], rotation_xyzw[N,J,4], scale[N,J,3]
mesh.npz:      vertices[V,3], triangles[T,3], inverse_bind[J,4,4],
                skin_joint_indices[V,K], skin_weights[V,K]
```

Usar metros, segundos, base destra, Y vertical, frente +Z, quatérnios XYZW.
Transformações locais são absolutas no espaço do pai; delta em relação ao
repouso é outra representação e exige conversão explícita. O root é uma junta
identificada; não somar sua translação de novo como trajetória separada.
`translation`, `rotation_xyzw`, `scale` usam float64 canônico; workers podem
usar float32 com erro medido. Índices usam inteiros e IDs estáveis fazem o
mapeamento; ordenar arrays não pode alterar identidade.

FPS é racional `numerator/denominator`; N amostras cobrem
`t[i]=i*denominator/numerator`, incluindo a última em `(N-1)/fps`. Pose
estática usa `kind='pose'` com uma amostra; clipe usa `kind='clip'` com N>=2.
Janelas são `[start,end)` em índices. Eventos/contatos usam segundos, com
fronteira final explicitamente incluída ou excluída. Loop registra período e
política da amostra de fechamento. Shear não representável é rejeitado com
`UNREPRESENTABLE_TRANSFORM`, nunca aproximado sem aviso.

`joints` contém `id`, `parent_id` e nome de origem; repouso, bind e pose não
são intercambiáveis. `anchors` contém tipo, joint_id e transform local ou
superfície identificada. Inferências semânticas têm confiança e confirmação;
o serviço retorna `CALIBRATION_REQUIRED` quando uma operação depende de um
mapeamento ambíguo. Perfis são versionados por assinatura de rig e malha.

## Edição, trabalhador e verificação

Exemplo canônico do pedido de aceitação, com IDs da fixture própria:

```json
{
  "window": [18,36],
  "authorized_window": [12,42],
  "editable_joint_ids": ["clavicle_l","upperarm_l","forearm_l","hand_l"],
  "operations": [{"type":"surface_clearance","part":"hand_l","other":"face","minimum_m":0.04}],
  "preserve": [{"type":"relative_transform","anchor":"grip_r","object":"weapon"}],
  "required_checks": ["preservation","limits","contacts","continuity","surface"],
  "tolerances": {"position_m":0.005,"rotation_deg":1.0,"roundtrip_position_m":0.0001,"roundtrip_rotation_deg":0.1},
  "budget": {"candidates":2,"corrections":3,"wall_seconds":60}
}
```

Na fixture de 30 fps, a janela principal cobre 0,6 s até antes de 1,2 s;
as margens autorizadas permitem transição. Exterior da janela autorizada e
canais protegidos são copiados exatamente da base canônica. O teste numérico
confere também a cinemática mundial; igualdade local não prova contato global.
O exemplo não autoriza alterar dedos, tronco, raiz, rig ou pesos.

Para E2, a fixture `guard_request(surface=False)` troca `surface_clearance`
por `anchor_target` e retira somente o check `surface`; essa variante é
explicitamente uma prova cinemática, não a aprovação final do caso visual.
Operações v1: `anchor_target`, `finger_pose`, `contact`, `retarget`, `retime`,
`mirror`, `root_motion`, `transition`. Canais e intervalos de cada operação
são declarados; o lote completo é validado antes de execução.

Fronteiras internas, com arquivos que serão criados nas respectivas tarefas:

```python
# core/pacotes.py — A2
def load_bundle(path: Path) -> tuple[dict, dict]: ...
def save_bundle(path: Path, manifest: dict, arrays: dict) -> str: ...

# core/revisoes.py — A4
class RevisionStore:
    def __init__(self, workspace: Path): ...
    def put(self, motion_id: str, expected_head: str | None,
            manifest: dict, arrays: dict, recipe: dict) -> str: ...
    def read(self, revision_id: str) -> tuple[dict, dict]: ...
    def head(self, motion_id: str) -> str | None: ...
    def select(self, motion_id: str, expected_head: str,
               revision_id: str) -> None: ...

# integracoes/protocolo.py — M1
class WorkerClient:
    def execute(self, operation: str, manifest_path: Path,
                output_dir: Path, budget: dict) -> dict: ...

# edicao/mascaras.py — M2
def compile_edit(character: dict, motion: dict, edit: dict) -> dict: ...
def compose_candidate(base: dict, proposed: dict, allowed: dict) -> dict: ...

# inspecao/metricas.py — M3; ampliado em B2
def evaluate(character: dict, base: dict, candidate: dict,
             recipe: dict, scene: dict) -> dict: ...

# core/tarefas.py — O1
class JobStore:
    def __init__(self, workspace: Path): ...
    def submit(self, operation: str, payload: dict) -> str: ...
    def status(self, job_id: str) -> dict: ...
    def cancel(self, job_id: str) -> dict: ...
    def resume(self, job_id: str) -> dict: ...
```

As reticências acima denotam assinaturas de interface, não implementações
aceitáveis. O comportamento está nas tarefas e nos schemas. `base`,
`candidate`, `proposed` são mapas de arrays canônicos; `allowed` contém máscara
booleana `[N,J]` por canal TRS e índices de contexto; `evaluate` retorna
`passed`, `violations` e medidas com cobertura. `scene` contém piso, objetos,
transforms e relações permitidas. `compile_edit` recusa campo sem semântica
implementada; não converte restrição obrigatória em preferência.

Worker recebe JSON por caminho e grava manifesto de saída com hashes. O
cliente inicia comando fixo com lista de argumentos, sem shell, timeout e
diretório temporário próprio; stdout estruturado e stderr de diagnóstico.
O núcleo valida hashes, schema, shapes, finitude e orçamento antes de aceitar.
Importar `animai` ou consultar catálogo não importa bibliotecas de worker.

## Fixtures comuns aos testes

Criar em A2 `tests/support/fabrica.py`, exposto pelo `tests/conftest.py` como
fixture `sample`. Sua classe `Sample` possui `actor_path: Path`,
`motion_path: Path`, `scene: dict`, `arrays: dict`, `root: Path`,
`actor_request() -> dict`, `build_request(actor_id: str) -> dict`,
`guard_request(surface: bool = True) -> dict` e
`rewrite_array(key: str, value) -> None` para produzir entradas inválidas.
`guard_request` devolve o campo `edit` do exemplo; os IDs de revisão são
adicionados pelo teste. Nenhum helper executa uma biblioteca externa.

A fixture `studio` cria `Studio(tmp_path/'workspace')`; `seeded` registra
`sample`, importa o movimento e devolve `(studio, actor_id, motion_id, rev_id)`.
`integrated` faz o mesmo habilitando os workers configurados em
`ANIMAI_TEST_SETTINGS`; ausência dessa variável só admite skip nas suítes
rápidas. Gates de integração requerem a variável e nenhum skip.

A fixture possui raiz/pelve, tronco/cabeça, duas cadeias de braço com comprimentos
diferentes, mãos com dedos e duas pernas; todos os IDs usados no pedido existem.
Produzir 61 amostras a 30 fps, raiz deslocando-se, dedos direitos animados,
arma acompanhando a empunhadura direita e mão esquerda próxima à cabeça.
Um segundo pacote troca nomes e proporções, mantendo mapa explícito de IDs
semânticos. Não usar dados de treinamento ou modelos humanos licenciados.

Adicionalmente A2 cria a cadeia analítica de três juntas, com offsets conhecidos
e rotação de 90 graus, cuja ponta tem posição calculável sem usar o mesmo
avaliador sob teste. `Sample` também expõe `analytic_actor_path: Path` e
`analytic_expected_positions: list[list[float]]`, calculadas diretamente na
fábrica para essa cadeia. B1 acrescenta malha própria simples, fechada nas regiões
de colisão, com pesos e IDs de superfície. Aparência de manequim é suficiente
para regressões; qualidade artística exige uma fonte de personagem autorizada.

## Comandos e gates a implementar

Executar na raiz futura `oficina/`, salvo indicação contrária:

```powershell
uv sync --group dev
uv run --locked pytest tests/unit -q
uv run --locked ruff check src tests
uv run --locked python -m animai.cli call animai.describe --json '{}'
uv run --locked python -m animai.gates --stage E1 --report artifacts/E1.json
```

`cli.py` será entrada fina para `interfaces/cli.py`. `gates.py` terá registro
por etapa: E1 unit; E2 inclui integração Momentum; E3 inclui Blender e ciclo
de exportação; E4 inclui subprocesso MCP e recuperação; E5 inclui Unreal real;
E6 inclui a geração real. Cada gate executa pré-requisitos, identifica worker
ausente como falha e escreve relatório mesmo quando um grupo falha.

Dados temporários, assets privados, logs e ambientes são ignorados pelo Git.
Somente fixtures pequenas próprias, schemas, código, manifests de dependência,
hashes e relatórios sem segredo entram em controle de versão. Tokens nunca
entram em receita, linha de comando persistida, exemplo ou log.
