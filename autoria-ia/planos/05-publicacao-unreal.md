> Cópia histórica desde 19/09/2026. O AnimAI agora tem raiz própria.
> Fonte atual: [docs/desenvolvimento/planos/05-publicacao-unreal.md](../../../AnimAI/docs/desenvolvimento/planos/05-publicacao-unreal.md).
> O conteúdo abaixo foi preservado para consulta e não governa trabalho novo.

# E5 — Publicação Unreal Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Registrar um personagem da Unreal e publicar uma animação candidata verificável, sem perder metadados nem sobrescrever trabalho aprovado.

**Architecture:** Adaptador de editor pequeno para extrair dados e escrever/amostrar assets. A oficina externa continua sendo a fonte editável. Um projeto de prova e um cenário de avaliação persistido verificam o resultado antes de uso no Jogo01.

**Tech Stack:** Unreal 5.8.2 inicialmente instalada, Python de editor, pequeno plugin C++ de extração, workers externos de E4 e pytest coordenando integração real.

**Spec:** [Contrato](../CONTRATO.md), [interfaces](INTERFACES.md), [mestre](README.md) e [evidências locais](REFERENCIAS.md).

## Global Constraints

Valem as [restrições globais](README.md#global-constraints). “Jogo01 é
consumidor, com seus assets e perfis.” “O jogo recebe assets convencionais.”
E4 concluída é pré-condição. Não instalar dependências da oficina no Python
da Unreal. Não presumir que NullRHI avalie a deformação visual final.

---

## U1 — Aquisição de personagem e calibração do adaptador

Arquivos: criar `src/animai/integracoes/unreal.py`,
`workers/unreal/extrair.py`, `workers/unreal/probe.py`,
`integracoes/unreal/AnimAIEditor/AnimAIEditor.uplugin`,
`integracoes/unreal/AnimAIEditor/Source/AnimAIEditor/AnimAIEditor.Build.cs`,
`integracoes/unreal/AnimAIEditor/Source/AnimAIEditor/Public/AnimAIExportLibrary.h`,
`integracoes/unreal/AnimAIEditor/Source/AnimAIEditor/Private/AnimAIExportLibrary.cpp`,
`integracoes/unreal/AnimAIEditor/Source/AnimAIEditor/Private/AnimAIEditorModule.cpp`,
`tests/integration/test_unreal_registro.py`, `docs/desenvolvimento/modulos/unreal.md`.

Interfaces: `UnrealClient(settings: dict)` implementa WorkerClient, com
`probe`, `extract`, `publish`, `sample`, `capture`. Perfil local contém
executável, projeto autorizado, pasta de candidatos, LOD, cenário e modo
de execução. `actor.register` aceita `source.format='unreal'` e referência
explícita ao SkeletalMesh, nunca procura todos os projetos da máquina.

- [ ] Criar projeto descartável de integração em diretório próprio e importar a fixture GLB/FBX de E3. Criar teste comparando esqueleto/repouso/bind/skin extraídos ao pacote original.

```python
def test_unreal_extracts_the_registered_character(unreal_case):
    out = unreal_case.extract_fixture()
    assert out["status"] == "ready"
    assert out["data"]["joint_ids_match"] is True
    assert out["data"]["max_bind_error_m"] <= 0.0001
    assert out["data"]["skin_weights_match"] is True
    assert out["data"]["lod"] == 0
```

- [ ] Definir `unreal_case` em `tests/support/unreal.py`, com `extract_fixture()`, `publish_roundtrip()` e `capture_context()`; usar projeto/test assets exclusivos. Rodar `uv run pytest tests/integration/test_unreal_registro.py -v`; engine ausente é falha do gate, não aprovação por mock.
- [ ] Implementar leitura Python dos dados já expostos. Para mesh/skin não disponíveis com fidelidade, construir apenas a biblioteca C++ de extração. Sua interface pública será a função abaixo; implementá-la validando Mesh, LOD-fonte e caminho antes de gravar bundle.

```cpp
UFUNCTION(BlueprintCallable, Category="AnimAI|Export")
static bool WriteCharacterBundle(USkeletalMesh* Mesh, int32 LOD,
    const FString& OutputDirectory, FString& OutError);
```

- [ ] Extrair hierarquia, referências de skeleton, repouso, bind, pesos, malha, sockets e dados derivados; registrar LOD-fonte. Usar convenções reais da engine e converter para o canônico com teste assimétrico, sem negar componentes de quaternion por tentativa. Perfis de rig/skin têm assinatura e invalidação própria.
- [ ] Testar LOD gerado sem dados-fonte, virtual bones, socket herdado, mesh sem skin e escala incompatível. A extração preserva referência a ABP/Control Rig/deformadores; não afirma reproduzir externamente seu comportamento.
- [ ] Compilar plugin, executar teste real e conferir nenhuma alteração de assets fora do projeto de prova. Registrar versões, checkpoint e recibo de aquisição.

## U2 — AnimSequence candidata, metadados e leitura após escrita

Arquivos: criar `workers/unreal/publicar.py`, `workers/unreal/amostrar.py`,
`src/animai/publicacao/unreal.py`,
`src/animai/publicacao/diario_destino.py`,
`tests/integration/test_unreal_publicacao.py`, `docs/uso/publicar-unreal.md`.

Interfaces: `publish_unreal(studio: Studio, request: dict) -> dict` usa
`UnrealClient` e recibos B3; `DestinationJournal(workspace: Path)` fornece
`begin(request_id: str, destination: dict) -> dict`, `record(receipt: dict)`
e `reconcile(request_id: str) -> dict`. Destino é identificado por projeto,
asset e fingerprint esperado, não apenas pelo nome do arquivo.

- [ ] Criar teste com dedos animados, curva, notify, deslocamento de raiz e frame rate racional. Duplicar asset-fonte no projeto de prova e comparar o original antes/depois.

```python
def test_publication_is_a_verified_candidate(unreal_case):
    out = unreal_case.publish_roundtrip()
    assert out["data"]["source_unchanged"] is True
    assert out["data"]["candidate_reloaded"] is True
    assert out["data"]["events_preserved"] is True
    assert out["data"]["curves_preserved"] is True
    assert out["data"]["duration_error_s"] <= 1e-6
    assert out["data"]["raw_max_position_error_m"] <= 0.0001
    assert out["quality"]["destination"] == "not_evaluated"
```

- [ ] Rodar `uv run pytest tests/integration/test_unreal_publicacao.py -v`; confirmar falha. `destination='not_evaluated'` neste teste indica falta do contexto de reprodução U3, mesmo com dados reabertos corretos.
- [ ] Escrever canais locais já retargetados via AnimationDataController. Criar/adicionar trilhas, definir taxa/duração com número de intervalos correto, verificar todo retorno e salvar candidata. Não usar a API de escrita como se ela própria fizesse retarget.

```python
for bone_name, keys in tracks.items():
    if bone_name not in existing_tracks:
        if not controller.add_bone_curve(bone_name):
            raise RuntimeError(f"Não foi possível criar trilha: {bone_name}")
    if not controller.set_bone_track_keys(bone_name, keys["position"],
                                          keys["rotation"], keys["scale"]):
        raise RuntimeError(f"Não foi possível escrever trilha: {bone_name}")
```

- [ ] Implementar política explícita: curvas/eventos/root motion transportados; Skeleton/sockets/ABP/Control Rig referenciados; deformadores exclusivos avaliados no destino. Retiming usa o mapa M5 também para notifies. Metadado sem política bloqueia publicação; não recriar por nome nem aplicar corretivo duas vezes.
- [ ] Serializar escrita por projeto, inclusive contra editor aberto. Se não for possível garantir exclusão com um editor ativo ou existirem assets sujos, parar antes de escrever. Usar commandlet sem render só para APIs homologadas; processo renderizado isolado para captura. Reconciliar efeito após queda antes de repetir gravação.
- [ ] Recarregar candidata em processo independente e comparar dados raw e reprodução comprimida, registrando erros separadamente. Usar tolerância raw de 0,1 mm/0,1 grau e perfil de compressão explicitamente medido; não aumentar tolerância ao falhar. Testar duas gravações concorrentes, cancelamento, asset existente e metadado desconhecido. Registrar checkpoint.

## U3 — Cenário de reprodução e adoção pelo consumidor

Arquivos: criar `workers/unreal/capturar.py`,
`src/animai/publicacao/contexto.py`, `tests/integration/test_unreal_contexto.py`,
`tests/acceptance/test_unreal_end_to_end.py`, `docs/uso/validar-no-jogo.md`.
O mapa/fixtures de teste ficam no projeto de integração, fora do núcleo Git;
receitas de criação e hashes ficam em `tests/fixtures/unreal/`.

Interfaces: `validate_context(studio: Studio, receipt: dict,
profile: dict) -> dict` em contexto. Perfil inclui mapa, atores/objetos,
ABP/slot, estado inicial, aquecimento, relógio fixo e câmeras. Asset isolado
e gameplay são contextos diferentes e aparecem no recibo.

- [ ] Escrever teste em que a reprodução isolada funciona, mas o ABP altera o braço e viola o contato. O sistema deve detectar a diferença em vez de aprovar pelo arquivo AnimSequence.

```python
def test_destination_approval_requires_requested_context(unreal_case):
    report = unreal_case.capture_context(mode="abp_changes_arm")
    assert report["quality"]["destination"] == "failed"
    assert any(v["code"] == "CONTACT_VIOLATION" for v in report["violations"])
    assert report["data"]["evaluated_context"] == "abp_changes_arm"
```

- [ ] Implementar cenário próprio com captura repetível; rodar `uv run pytest tests/integration/test_unreal_contexto.py -v`; confirmar falha.
- [ ] Automatizar captura e medição após aquecimento, com render disponível quando necessário. Mostrar corpo e mãos, objeto, raiz e apoios. Não usar NullRHI como prova geral de pele. Ausência de cenário solicitado retorna `CONTEXT_NOT_EVALUATED` e impede promoção que o exija.

```python
if requested_context != receipt["evaluated_context"]:
    raise DomainError("CONTEXT_NOT_EVALUATED", "Contexto solicitado não foi verificado",
                      {"requested": requested_context}, False)
```

- [ ] Homologar o ciclo no projeto de prova. Depois, mediante seleção explícita do usuário, registrar um personagem e perfil do Jogo01 por leitura e publicar somente na pasta candidata configurada. Não alterar ABP, personagem de gameplay ou animação aprovada automaticamente.
- [ ] Preparar A/B no motor e instrução breve do que o usuário deve observar: contato, mãos, cotovelo, apoio, continuidade e root motion. Marcar avaliação artística separadamente; promoção ao conteúdo aprovado exige autorização e fingerprint ainda igual.
- [ ] Rodar `uv run --locked --extra mcp python -m animai.gates --stage E5 --report artifacts/E5.json`. Registrar checkpoint, origem do perfil consumidor e limites comprovados. Demonstrar que o jogo recebe somente assets, sem modelos ou workers da oficina.

## Saída de E5

Oficina externa integrada ao motor com aquisição, publicação e evidência no
contexto solicitado. Projeto de prova pode estar homologado enquanto adoção
no Jogo01 aguarda escolha do consumidor; registrar esses estados separadamente.
