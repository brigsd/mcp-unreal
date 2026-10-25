> Cópia histórica desde 19/09/2026. O AnimAI agora tem raiz própria.
> Fonte atual: [docs/desenvolvimento/planos/01-base-e-revisoes.md](../../../AnimAI/docs/desenvolvimento/planos/01-base-e-revisoes.md).
> O conteúdo abaixo foi preservado para consulta e não governa trabalho novo.

# E1 — Base e revisões Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Estabelecer a identidade AnimAI e documentação/skills por papel, depois registrar personagens e movimentos, validar formatos e manter revisões recuperáveis através de serviços e CLI.

**Architecture:** Pacote Python leve, schemas fechados e armazenamento local com identidade por conteúdo. Catálogo anuncia somente o que existe. Nenhum worker pesado é necessário nesta etapa.

**Tech Stack:** Python 3.11, NumPy, Pydantic 2, SQLite, pytest, Ruff e uv.

**Spec:** [Contrato](../CONTRATO.md), [interfaces](INTERFACES.md) e [plano mestre](README.md).

## Global Constraints

As restrições globais do [plano mestre](README.md#global-constraints) são parte
deste plano. Em particular: “Revisões são imutáveis.” e “Descoberta não carrega
modelos nem instala dependências.” Arquivos são futuros e relativos à raiz
`oficina/` definida no mestre. Não alterar a raiz do plugin existente.

---

## A0 — Identidade, documentação e skills por papel

Arquivos: criar em `oficina/` os roteadores `README.md` e `AGENTS.md`,
`docs/manifesto.json`, `docs/uso/README.md`, `docs/desenvolvimento/README.md`,
`docs/desenvolvimento/contribuicao.md`, `tests/docs/test_documentacao.py`,
`scripts/doc_freshness.py`, `tests/docs/test_freshness.py`,
`tests/skills/cenarios.md`, `tests/skills/rubrica.md`;
criar separadamente `skills/animai-desenvolver/SKILL.md` e
`skills/animai-usar/SKILL.md` após seus baselines. Migrar documentos atuais
conforme [documentação e skills](DOCUMENTACAO-E-SKILLS.md), deixando
encaminhamentos compatíveis nos caminhos antigos.

Esta tarefa precede o runtime. Para o validador documental, usar ambiente de
teste isolado e declarado, sem instalar dependências globais; A1 incorpora
esse teste ao pacote, lock e gate. As provas comportamentais das skills têm
relatório próprio e não são substituídas pelo pytest.

O verificador segue a interface, precedência de estados, CLI e política do
[protocolo de atualização](../docs/desenvolvimento/ATUALIZACAO-E-HOOKS.md).
Os scripts são importáveis como namespace local em testes; não carregam o
runtime da oficina. O mesmo verificador será chamado em A1, sem reimplementação.

- [ ] Registrar cenários/rubrica por papel: nome AnimAI em contexto novo, operação indisponível, desenvolvimento de adaptador, diagnóstico sem implementação e pedido Mecanifica. Incluir pergunta macro literal/paráfrase, evidência vencida e pesquisa indisponível. Executar baseline sem cada skill; guardar observações reais sem escrever a skill antes do teste.
- [ ] Criar testes documentais para fonte única, manifesto, links/âncoras e roteamento. Usar fixtures com link quebrado, exemplo de operação planejada anunciado como disponível e referência fora do pacote; confirmar que a validação acusa cada defeito, não somente que passa numa árvore vazia.
- [ ] Criar os dois índices e roteadores; migrar fontes e ajustar links no mesmo checkpoint. Registrar `planned/draft` quando pertinente; não preencher comprovação fictícia. Copiar a árvore para pasta temporária e conferir referências sem acesso ao checkout hospedeiro.
- [ ] Escrever o teste de invalidação abaixo e os casos de limite temporal/fonte ausente definidos no protocolo; rodar `python -m pytest tests/docs/test_freshness.py -v` e confirmar falha antes de implementar. O exemplo é fixture de teste, não recibo de uma pesquisa real.

```python
from scripts.doc_freshness import evaluate_freshness

def test_local_change_reopens_document_without_editing_its_text():
    old_hash = "a" * 64
    doc = {
        "id": "formato", "status": "validated",
        "freshness": {
            "kind": "stable", "reviewed_at": "2026-09-19T12:00:00Z",
            "review_after": None, "source_fingerprints": {"schema.json": old_hash},
            "evidence_refs": ["test-01"], "reason": None,
        },
        "evidence_receipts": [{
            "id": "test-01", "reviewed_at": "2026-09-19T12:00:00Z",
            "document_ids": ["formato"],
            "source_fingerprints": {"schema.json": old_hash},
        }],
    }
    now = "2026-09-19T13:00:00Z"
    assert evaluate_freshness(doc, now, {"schema.json": old_hash})["state"] == "current"
    changed = evaluate_freshness(doc, now, {"schema.json": "b" * 64})
    assert changed["state"] == "stale"
    assert "SOURCE_CHANGED" in changed["reasons"]
```

- [ ] Implementar a função pura, resolução local de fontes/recibos e CLI de relatório/gate. Testar dependentes transitivos, fonte apagada, arquivo novo não rastreado, ausência de base Git e relógio no instante exato do vencimento. Nenhum caminho pode escapar da raiz documental/pacote permitida; nenhuma consulta externa ou atualização de datas é feita pelo script.
- [ ] Ler as skills de criação/validação disponíveis no ambiente. Criar e validar primeiro `animai-desenvolver`, com referências mínimas, repetindo seus cenários em contexto novo. Só depois criar/testar `animai-usar`, que nesta etapa reconhece a indisponibilidade do runtime. Refinar a partir das falhas observadas e revalidar cada skill alterada.
- [ ] Definir em contribuição a obrigação de atualizar docs, schemas, exemplos e referências das skills em cada tarefa. Registrar compatibilidade e critérios de migração; evitar regra de leitura obrigatória de desenvolvimento para quem apenas usa.
- [ ] Rodar `python -m pytest tests/docs/ -v` no ambiente declarado e registrar relatórios dos cenários independentes. Revisar diff e confirmar que não houve instalação de skills no cliente nem alteração do plugin existente. A0 só fecha com evidências; índices/instruções criados nesta rodada de planejamento não equivalem a A0 executada.

## A1 — Pacote executável, catálogo e erro estruturado

Arquivos: criar `pyproject.toml`, `.gitignore`, `src/animai/__init__.py`,
`api.py`, `cli.py`, `gates.py`, `core/catalogo.py`, `core/servicos.py`,
`core/respostas.py`, `interfaces/cli.py`, `tests/conftest.py`,
`tests/unit/test_catalogo.py`, `docs/desenvolvimento/modulos/README.md`,
`docs/desenvolvimento/arquitetura.md`, `docs/desenvolvimento/ambiente.md`
e `docs/desenvolvimento/testes.md`. Gerar `uv.lock`.
Nesta lista, caminhos sem prefixo após `src/animai/__init__.py` e antes de
`tests/` pertencem a `src/animai/`.

Interfaces: produzir `Studio.call`, `Registry.validate` e `Services.dispatch`
conforme INTERFACES. `animai.describe` retorna em `data.capabilities` uma
lista com `operation`, `state`, `reason` e `schema_ref`. `core/respostas.py`
define `Response` e `DomainError(code: str, message: str, details: dict,
retryable: bool=False)`. Erros de domínio são convertidos para o envelope na API.

- [ ] Criar o pacote mínimo e o teste abaixo; catálogo não pode dizer que todas as operações planejadas estão disponíveis.

```python
def test_discovery_is_light_and_truthful(studio):
    import sys
    out = studio.call("animai.describe", {})
    assert out["status"] == "ready"
    states = {c["operation"]: c["state"] for c in out["data"]["capabilities"]}
    assert states["animai.describe"] == "available"
    assert states["motion.patch"] == "planned"
    assert not {"torch", "bpy", "pymomentum"}.intersection(sys.modules)

def test_unknown_operation_does_not_execute(studio):
    out = studio.call("python.exec", {"code": "raise RuntimeError()"})
    assert out["status"] == "failed"
    assert out["error"]["code"] == "UNKNOWN_OPERATION"
```

- [ ] Rodar `uv run pytest tests/unit/test_catalogo.py -v`; confirmar falha. A fixture `studio` usa workspace temporário e permite leitura/escrita somente no `tmp_path` do teste.
- [ ] Implementar catálogo de contratos, registro explícito de serviços e roteamento. CLI: `call <operation> --json <json>` ou `--request <arquivo.json>`, nunca ambos. stdout JSON, stderr diagnóstico; saídas 0 para `ready/queued`, 2 para entrada inválida e 1 para falha de execução.

```python
def dispatch(self, operation: str, request: dict) -> dict:
    handler = self.handlers.get(operation)
    if handler is None:
        raise DomainError("CAPABILITY_UNAVAILABLE", "Operação indisponível", {}, False)
    return handler(request)
```

- [ ] Implementar `gates.py` com registro E1 e relatório de resultados/duração; grupos futuros não habilitados. Incorporar testes documentais e verificador de validade de A0 ao pacote/lock. O gate exige documentos da entrega consistentes e evidências atuais para decisões alteradas; pesquisa vencida fora do recorte gera aviso, não bloqueio global. Rodar teste, CLI em subprocesso e Ruff. Testar JSON inválido e campos extras sem criação de arquivos.
- [ ] Documentar comandos e estados reais, gerar referência de uso dos schemas e atualizar as referências de `animai-usar` para descoberta via CLI. Acrescentar ao manifesto exemplos reproduzíveis, versão e testes. Preparar checkpoint; não instalar Momentum, Blender ou modelos neste recorte.

## A2 — Pacote canônico e fixtures independentes

Arquivos: criar `src/animai/core/pacotes.py`, `core/hashes.py`,
`core/caminhos.py`, `personagens/schema.py`, `movimentos/schema.py` dentro
do mesmo pacote; criar `schemas/`, `tests/support/fabrica.py`,
`tests/support/__init__.py`, `tests/unit/test_pacotes.py`,
`tests/unit/test_caminhos.py` e `docs/desenvolvimento/modulos/formatos.md`;
completar `tests/conftest.py`.

Interfaces: consumir Response/DomainError; produzir `load_bundle`,
`save_bundle` e `Sample` de INTERFACES. Exportar schemas dos modelos,
sem duas definições manuais. Definir em hashes
`canonical_digest(manifest: dict, arrays: dict) -> str`.

- [ ] Criar os testes abaixo e casos negativos de shapes, árvore com ciclo, pesos inválidos e dtype object, cada um com erro específico.

```python
import numpy as np
import pytest
from animai.core.pacotes import load_bundle, save_bundle
from animai.core.respostas import DomainError

def test_bundle_roundtrip_has_no_extra_frame(sample, tmp_path):
    manifest, arrays = load_bundle(sample.motion_path)
    before = arrays["rotation_xyzw"].copy()
    save_bundle(tmp_path / "roundtrip", manifest, arrays)
    got, values = load_bundle(tmp_path / "roundtrip")
    assert got["sample_count"] == 61
    assert got["sample_rate"] == {"numerator": 30, "denominator": 1}
    assert np.array_equal(values["rotation_xyzw"], before)

def test_nan_is_refused(sample):
    bad = sample.arrays["translation"].copy()
    bad[0, 0, 0] = np.nan
    sample.rewrite_array("translation", bad)
    with pytest.raises(DomainError) as error:
        load_bundle(sample.motion_path)
    assert error.value.code == "NONFINITE_DATA"
```

- [ ] Rodar `uv run pytest tests/unit/test_pacotes.py tests/unit/test_caminhos.py -v`; confirmar falha antes da implementação.
- [ ] Implementar leitura, limites de tamanho antes de alocar, conversão explícita de entrada e hashes. Não renormalizar canais canônicos intocados ao salvar. Rejeitar arquivos fora de raízes permitidas, links/junctions que escapem e quantidades inconsistentes.

```python
with np.load(array_path, allow_pickle=False) as archive:
    arrays = {key: archive[key].copy() for key in required_keys}
if any(not np.isfinite(value).all() for value in arrays.values()):
    raise DomainError("NONFINITE_DATA", "Array contém valor não finito", {}, False)
```

- [ ] Implementar Sample e a cadeia analítica de INTERFACES. Testar troca da ordem dos ossos, FPS `30000/1001`, pose estática, quaternion nulo, escala não uniforme armazenada e shear recusado. Escala armazenável não significa IK habilitada.
- [ ] Rodar testes e gate E1; documentar tamanho máximo configurável e convenções. Registrar checkpoint.

## A3 — Registro e calibração reutilizável

Arquivos: criar `src/animai/personagens/registro.py`,
`src/animai/personagens/calibracao.py`,
`src/animai/personagens/capacidades.py`, `tests/unit/test_registro.py`,
`docs/desenvolvimento/modulos/personagens.md`; modificar `api.py` e `core/catalogo.py` no pacote.

Interfaces: consumir pacote A2; registrar serviço `actor.register` com
`data.actor_id`, `data.profile_id`, `data.calibration_status` e ambiguidades.
`register_actor(workspace: Path, request: dict) -> dict` fica em registro;
`calibrate(character: dict, profile: dict) -> dict`, em calibracao.

- [ ] Escrever teste para reuso, ambiguidade e invalidação por mudança de repouso.

```python
def test_registration_reuses_content_and_exposes_ambiguity(studio, sample):
    request = sample.actor_request()
    first = studio.call("actor.register", request)
    again = studio.call("actor.register", request)
    assert first["data"]["actor_id"] == again["data"]["actor_id"]
    assert first["data"]["calibration_status"] == "ready"
    ambiguous = sample.actor_request()
    ambiguous["request_id"] = "ambiguous-profile"
    ambiguous["profile"]["anchors"].pop("grip_r")
    result = studio.call("actor.register", ambiguous)
    assert result["data"]["calibration_status"] == "needs_input"
    assert "grip_r" in result["data"]["missing_anchors"]
```

- [ ] Rodar `uv run pytest tests/unit/test_registro.py -v` e observar falha.
- [ ] Implementar assinatura de hierarquia, repouso, malha e perfil. Reusar importação inalterada; revisão de perfil não altera pacote anterior. Perfil incompleto pode ser registrado, mas operação dependente retorna `CALIBRATION_REQUIRED`.

```python
missing = sorted(required_anchors.difference(profile["anchors"]))
calibration = {
    "status": "needs_input" if missing else "ready",
    "missing_anchors": missing,
}
```

- [ ] Testar homônimos, lados trocados e perfil de outra assinatura. Conferir que editar perfil não duplica malha nem invalida personagens diferentes.
- [ ] Rodar testes e gate E1; documentar resolução das ambiguidades restantes. Registrar checkpoint.

## A4 — Movimentos, revisões e conflitos

Arquivos: criar `src/animai/core/revisoes.py`, `core/artefatos.py`,
`core/idempotencia.py`, `movimentos/fontes.py` no pacote;
`tests/unit/test_revisoes.py`, `tests/unit/test_idempotencia.py`,
`docs/desenvolvimento/modulos/movimentos.md`; completar catálogo, roteamento e
fixtures `seeded`/`integrated`.

Interfaces: implementar RevisionStore de INTERFACES e `motion.build` para
fonte `bundle` e `revision`. Em artefatos definir
`put_artifact(workspace: Path, path: Path) -> dict`, com hash/tamanho/URI.
`motion.patch(mode='select_revision')` passa a disponível; `mode='apply'`
continua indisponível. Catálogo e teste de A1 passam a conferir modos.

- [ ] Escrever o teste de comparação da revisão esperada, imutabilidade e retorno a versão anterior.

```python
import pytest
from animai.core.revisoes import RevisionStore
from animai.core.pacotes import load_bundle
from animai.core.respostas import DomainError

def test_conflict_keeps_head_and_old_revision(tmp_path, sample):
    store = RevisionStore(tmp_path / "store")
    manifest, arrays = load_bundle(sample.motion_path)
    r1 = store.put("m", None, manifest, arrays, {"source": "fixture"})
    changed = {key: value.copy() for key, value in arrays.items()}
    changed["translation"][20, 0, 0] += 0.01
    r2 = store.put("m", r1, manifest, changed, {"source": r1})
    with pytest.raises(DomainError) as error:
        store.put("m", r1, manifest, arrays, {"stale": True})
    assert error.value.code == "REVISION_CONFLICT"
    assert store.head("m") == r2
    assert store.read(r1)[1]["translation"][20, 0, 0] == arrays["translation"][20, 0, 0]
    store.select("m", r2, r1)
    assert store.head("m") == r1
    assert store.read(r2)[0] == manifest
```

- [ ] Rodar `uv run pytest tests/unit/test_revisoes.py tests/unit/test_idempotencia.py -v`; confirmar falha.
- [ ] Implementar blobs em temporário no mesmo volume, flush e rename; depois transação SQLite para revisão/head/idempotência. Banco e arquivos não formam transação distribuída: órfãos podem existir, mas revisão não aponta para blob incompleto. Ao carregar, conferir hash e sinalizar corrupção.

```sql
BEGIN IMMEDIATE;
UPDATE motion_heads SET revision_id = :new WHERE motion_id = :motion AND revision_id = :expected;
-- Exigir rowcount == 1; caso contrário ROLLBACK e REVISION_CONFLICT.
COMMIT;
```

- [ ] Testar falha antes/depois do rename e antes do commit; duas chamadas concorrentes; request_id repetido com conteúdo igual e diferente. Canais/eventos da fonte continuam acessíveis após reversão.
- [ ] Rodar `uv run --locked python -m animai.gates --stage E1 --report artifacts/E1.json`. Exigir registro/importação/seleção via subprocesso CLI e ausência de imports pesados. Registrar evidência e checkpoint.

## Saída de E1

A entrega identifica o AnimAI em contexto novo, separa uso/desenvolvimento e
tem duas skills verificadas para as capacidades desta etapa. É também um
pacote funcional que sabe o que possui, recusa dados inválidos
e não perde revisões. Ainda não há animação corrigida. Próxima tarefa: E2/M1,
com os mesmos bundles e sem mudanças no Jogo01.
