> Cópia histórica desde 19/09/2026. O AnimAI agora tem raiz própria.
> Fonte atual: [docs/desenvolvimento/planos/06-geracao-kimodo.md](../../../AnimAI/docs/desenvolvimento/planos/06-geracao-kimodo.md).
> O conteúdo abaixo foi preservado para consulta e não governa trabalho novo.

# E6 — Geração Kimodo opcional Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Acrescentar geração de bases de movimento sem transformar edição, inspeção ou publicação em operações dependentes de modelos carregados.

**Architecture:** Kimodo é fornecedor isolado de fontes. Resultado neural é materializado, convertido, adaptado e verificado pelas mesmas etapas existentes. Cache e reservas de recursos tornam inicialização e reedição previsíveis.

**Tech Stack:** API oficial Kimodo em ambiente isolado Linux/WSL quando necessário, encoder compatível com cache, workers E4, retarget E2 e inspeção/publicação E3–E5.

**Spec:** [Contrato](../CONTRATO.md), [interfaces](INTERFACES.md), [mestre](README.md) e [referências](REFERENCIAS.md).

## Global Constraints

Valem as [restrições globais](README.md#global-constraints). “Descoberta não
carrega modelos nem instala dependências.” “O jogo recebe assets convencionais.”
E5 homologada no projeto de prova é pré-condição; adoção no Jogo01 não bloqueia
E6. Sem acesso legítimo aos pesos, E1–E5 continuam utilizáveis; não contornar
restrições nem reinstalar componentes antigos indiscriminadamente.

---

## G1 — Registro do gerador e conversão de sua saída

Arquivos: criar `src/animai/integracoes/kimodo.py`,
`workers/kimodo/main.py`, `workers/kimodo/conversao.py`,
`ambientes/kimodo/environment.yml` e lock compatível,
`tests/unit/test_kimodo_conversion.py`, `tests/integration/test_kimodo.py`,
`docs/desenvolvimento/modulos/kimodo.md`; completar fonte `generator` em movimentos.

Interfaces: `KimodoClient(settings: dict)` implementa WorkerClient com
`probe`, `encode`, `generate`, `release`. `motion.build` aceita
`source.kind='generator'`, `backend='kimodo'`, `prompt`, `duration_s`, `seed`
e controles tipados, mais `mapping_id` e base do destino quando necessários.
Retorno é bundle, proveniência, capacidades efetivas e limitações.

- [ ] Criar saída SOMA sintética pequena com unidades/orientações conhecidas e teste que não confunda juntas extras com dedos gerados.

```python
def test_generator_output_does_not_claim_finger_motion(kimodo_conversion_case):
    out = kimodo_conversion_case.convert_fixture()
    assert out["units"] == "m"
    assert out["generated_fingers"] is False
    assert out["source_joint_count"] == kimodo_conversion_case.source_joint_count
    assert out["requires_target_hand_recipe"] is True
```

- [ ] Definir helper `kimodo_conversion_case` em `tests/support/kimodo.py`, com `convert_fixture()` e `source_joint_count`; criar fixture a partir do formato auditado, sem distribuir pesos/dataset. Rodar `uv run pytest tests/unit/test_kimodo_conversion.py -v`; confirmar falha.
- [ ] Inventariar apenas ambientes/pesos configurados pelo usuário e reutilizar os íntegros. Registrar licença separada para código, pesos SOMA, encoder e dados; downloads ausentes exigem autorização e verificação de espaço/hash. Credenciais ficam em mecanismo local apropriado, nunca nos manifests públicos ou logs.
- [ ] Implementar API oficial em worker próprio, pós-processamento explicitamente ativado e conversão canônica. Tipos de controles, horizonte e esqueleto são consultados do adaptador homologado; tipo ausente retorna `UNSUPPORTED_CONDITION`, sem ignorar o controle.

```python
if condition_kind not in capabilities["condition_kinds"]:
    raise DomainError("UNSUPPORTED_CONDITION", "Gerador não suporta este controle",
                      {"condition_kind": condition_kind}, False)
```

- [ ] Testar eixo, repouso, unidade, expansão de esqueleto, duração e fonte com orientação insuficiente. Persistir saída neural original e bundle convertido. Retarget usa M4; dedos vêm da base/receita aprovada, não de uma alegação de geração completa.
- [ ] Executar probe real sem geração e teste curto de condicionamento quando recursos/acesso estiverem disponíveis. Registrar checkpoint e disponibilidade real; probe não aprova qualidade de movimento.

## G2 — Cache, residência e alocação sem surpresas

Arquivos: criar `workers/kimodo/cache_textual.py`,
`workers/kimodo/recursos.py`, `tests/unit/test_embedding_cache.py`,
`tests/integration/test_kimodo_recursos.py`, `docs/uso/gerar-base.md`;
integrar `core/cache.py`, `core/recursos.py` e journal O1.

Interfaces: `embedding_key(prompt: str, encoder: dict) -> str` e
`get_or_encode(prompt: str, encoder: dict, cache_dir: Path) -> dict` no cache.
`encoder` inclui identidade, pesos/revisão, tokenizer, adaptadores, precisão
e versão de normalização. Retorno aponta artefato íntegro, com hash e shape.
Modelo/encoder devem obedecer às reservas do coordenador.

- [ ] Escrever teste de cache com alteração de precisão e pesos, além de prompt repetido.

```python
from animai.integracoes.kimodo import embedding_key

def test_embedding_key_includes_actual_encoder_configuration(encoder_manifest):
    base = embedding_key("raise the left hand", encoder_manifest)
    assert base == embedding_key("raise the left hand", dict(encoder_manifest))
    changed = {**encoder_manifest, "precision": "different-precision"}
    assert base != embedding_key("raise the left hand", changed)
    changed = {**encoder_manifest, "weights_hash": "different-weights"}
    assert base != embedding_key("raise the left hand", changed)
```

- [ ] Expor função pura de chave também no cliente Kimodo, sem carregar modelo; fixture `encoder_manifest` pertence a `tests/support/kimodo.py`. Rodar `uv run pytest tests/unit/test_embedding_cache.py -v`; confirmar falha.
- [ ] Injetar cache no encoder usado pela API real. Hash abrange exatamente a configuração utilizada, e a normalização de texto também é entrada versionada. Embedding errado/arquivo parcial é descartado como cache inválido, não entregue ao modelo.

```python
fingerprint = {"prompt": normalized_prompt, "encoder": encoder_manifest}
key = hashlib.sha256(json.dumps(fingerprint, sort_keys=True,
                               separators=(",", ":")).encode("utf-8")).hexdigest()
```

- [ ] Configurar uma vez os papéis `encoder`, `generator`, `render` no perfil local. Preferir core/edição na CPU; GPU do gerador é UUID explícito. A escolha inicial pode usar 5070 para geração e CPU/cache para encoder, mas só após conferir memória livre e compatibilidade. Não ativar duas cargas na 2080 por fallback. Configuração já homologada pode ser reaproveitada com recibo compatível.
- [ ] Serializar etapas pesadas quando o orçamento de RAM exigir; descarregar encoder antes da geração e modelo antes de render/publicação quando configurado. Testar CPU/GPU insuficiente, cancelamento durante encode/generate e reinício com embedding pronto. Contadores devem provar cache hit sem nova carga do encoder.
- [ ] Registrar tempo frio, tempo com cache, VRAM/RAM observadas e checkpoint. Não prometer inicialização instantânea ou performance de 27B como prova de compatibilidade deste encoder.

## G3 — Gerar, corrigir e publicar pelo mesmo ciclo

Arquivos: criar `tests/acceptance/test_geracao_reedicao.py`,
`tests/acceptance/test_geracao_publicacao.py` e
`docs/uso/criar-acao-com-gerador.md`; completar registro técnico do adaptador.

Interfaces: consumir somente operações públicas existentes, sem uma tool
especial que contorne preservação. Helper `generated_case` em
`tests/support/kimodo.py` expõe `generate_short_action()`,
`release_models()`, `edit_existing()` e contadores de carga/inferência.

- [ ] Escrever teste do requisito principal: depois de gerar, editar não reinicia inferência.

```python
def test_materialized_clip_is_editable_without_models(generated_case):
    generated_case.generate_short_action()
    generated_case.release_models()
    before = generated_case.inference_count
    out = generated_case.edit_existing()
    assert out["status"] == "ready"
    assert generated_case.inference_count == before
    assert generated_case.resident_model_count == 0
```

- [ ] Rodar teste com fonte sintética para verificar o fluxo e depois com geração real explicitamente habilitada no gate E6. Mock não conta como homologação do gerador. A ação de prova tem até três segundos, seed registrada e um controle suportado verificável.
- [ ] Integrar geração→conversão→retarget→correção→inspeção→publicação candidata. Geração neural só cria proposta; copiar canais permitidos e medir preservações depois. Materializar clipe, receita, hashes de pesos/ambientes e saída original; mesma seed não é garantia de bytes iguais em outro hardware.

```python
revision = studio.call("motion.build", generation_request)
if revision["quality"]["technical"] != "passed":
    return revision
# Publicação recebe revision_id validado e destino candidato explicitamente autorizado.
```

- [ ] Fazer segunda correção sobre o resultado, reverter e reiniciar os processos; conferir que o movimento persistido permanece idêntico e editável. Repetir prompt com cache para medir ausência de recarga do encoder. Verificar mãos, contato e continuidade no destino, sem exigir que o modelo sozinho acerte a atuação.
- [ ] Rodar `uv run --locked --extra mcp python -m animai.gates --stage E6 --report artifacts/E6.json`; gate exige geração real e E1–E5. Entregar comparações visuais e relatório de recursos; registrar limitações artísticas separadas de falhas técnicas.

## Saída de E6 e encerramento do primeiro programa

A oficina aceita tanto movimentos existentes quanto bases geradas. O ciclo
de correção permanece utilizável sem modelos carregados. O usuário recebe
uma ação publicada como candidata e evidências de preservação, reversão e
recuperação. Aprovação artística e adoção no jogo continuam explícitas.

Novos geradores, física de personagem, modelos de mãos ou animação neural em
runtime exigem um recorte posterior motivado por uma lacuna observada. Não
adicionar dependências só porque o programa inicial terminou.
