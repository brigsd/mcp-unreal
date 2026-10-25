> Cópia histórica desde 19/09/2026. O AnimAI agora tem raiz própria.
> Fonte atual: [docs/desenvolvimento/planos/03-inspecao-e-intercambio.md](../../../AnimAI/docs/desenvolvimento/planos/03-inspecao-e-intercambio.md).
> O conteúdo abaixo foi preservado para consulta e não governa trabalho novo.

# E3 — Inspeção e primeira entrega Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fechar o primeiro ciclo utilizável: editar um movimento, conferir pele e antes/depois, desfazer e exportar.

**Architecture:** Blender em processo separado para aquisição, deformação e imagens. O núcleo conserva receitas, limita efeitos e combina medidas com evidências visuais. Arquivos exportados são produtos derivados, não a única fonte editável.

**Tech Stack:** Núcleo/worker de E2, Blender em background, JSON/NPZ, GLB e FBX por adaptadores; pytest para integração.

**Spec:** [Contrato](../CONTRATO.md), [interfaces](INTERFACES.md) e [mestre](README.md).

## Global Constraints

Valem as [restrições globais](README.md#global-constraints). “Jogo01 é
consumidor, com seus assets e perfis.” “Só promover uma candidata quando
cumprir os critérios obrigatórios do pedido.” B1 pode começar após E1;
B2/B3 exigem E2 aprovado. Não modificar pesos para esconder erro de animação.

---

## B1 — Worker Blender e importação fiel

Arquivos: criar `src/animai/integracoes/blender.py`,
`workers/blender/main.py`, `workers/blender/importar.py`,
`workers/blender/avaliar.py`, `workers/blender/fixture.py`,
`tests/integration/test_blender_import.py`, `docs/desenvolvimento/modulos/blender.md`.

Interfaces: `BlenderClient(settings: dict)` implementa WorkerClient.
Operações internas `probe`, `import`, `evaluate_mesh`, `render`, `export`.
`evaluate_mesh` devolve arrays de vértices/triângulos e matrizes de juntas
por amostra, por artefato; `import` devolve bundle canônico e relatório de
perdas. Catálogo só habilita operações efetivamente homologadas.

- [ ] Criar fixture de malha própria sobre o rig A2, com regiões identificadas de mão/rosto, pesos fixados e superfícies fechadas. Criar teste de importação com assimetria, offsets de bind e animação de dedos.

```python
def test_blender_import_preserves_bind_and_samples(blender_case):
    result = blender_case.import_and_compare()
    assert result["joint_ids_match"] is True
    assert result["sample_count"] == 61
    assert result["max_position_error_m"] <= 0.0001
    assert result["max_rotation_error_deg"] <= 0.1
    assert result["max_vertex_error_m"] <= 0.0001
```

- [ ] Definir `blender_case` em `tests/support/blender.py`, com `import_and_compare() -> dict`, usando fixture do worker e comparação independente com LBS analítico em poses conhecidas. Rodar `uv run pytest tests/integration/test_blender_import.py -v`; exigir executável configurado no gate.
- [ ] Implementar cliente sem shell, estado inicial limpo e falha Python propagada. Registrar versão/build Blender no recibo, nunca abrir arquivo privado por procura automática. Imports glTF/FBX convertem eixos, unidades e repouso uma única vez.

```python
args = [settings["blender"], "--background", "--factory-startup",
        "--python-exit-code", "1", "--python", str(settings["worker"]),
        "--", "--manifest", str(manifest_path), "--output", str(output_dir)]
```

- [ ] Avaliar o depsgraph por frame e extrair a malha avaliada; liberar malhas temporárias. Recusar armature ausente, skin ambíguo, constraints não assadas ou deformador não representável sem política. Um asset de usuário pode manter uma referência ao avaliador Blender sem prometer equivalência na Unreal.
- [ ] Testar escala/nomes/unidades, erro Python, timeout e resultado ausente apesar de saída zero. Rodar suíte, documentar formatos efetivos e registrar checkpoint.

## B2 — Superfície, câmeras e correção guiada por evidência

Arquivos: criar `src/animai/inspecao/superficie.py`,
`inspecao/relatorio.py`, `inspecao/vistas.py` no pacote;
`workers/blender/inspecao.py`, `workers/blender/render.py`,
`tests/integration/test_superficie.py`, `tests/integration/test_previas.py`,
`docs/uso/inspecionar.md`; ampliar `inspecao/metricas.py` e `edicao/compilador.py`.

Interfaces: `surface_report(meshes: dict, scene: dict, recipe: dict) -> dict`
em superficie; `build_views(character: dict, recipe: dict) -> list[dict]` em
vistas; `build_report(evaluations: list[dict], artifacts: list[dict]) -> dict`
em relatorio. `motion.inspect` passa a aceitar checks `surface` e `preview`.
Relatório traz `data.surface.min_clearance_m`, `penetrating_pairs` e cobertura.

- [ ] Escrever teste que acusa mão dentro do rosto e diferencia relação permitida mão–arma. Usar triângulos analíticos e fixture fechada, sem confiar apenas no teste de cápsulas do solver.

```python
def test_surface_gate_catches_a_kinematically_valid_collision(surface_case):
    bad = surface_case.inspect_original()
    assert bad["data"]["surface"]["penetrating_pairs"] > 0
    fixed = surface_case.apply_guard()
    assert fixed["status"] == "ready"
    assert fixed["data"]["surface"]["min_clearance_m"] >= 0.04
    assert fixed["data"]["surface"]["penetrating_pairs"] == 0
    assert fixed["data"]["preservation"]["max_grip_error_m"] <= 0.005
```

- [ ] Criar `surface_case` em `tests/support/superficie.py`, com `inspect_original()` e `apply_guard()` via Studio e workers reais. Rodar `uv run pytest tests/integration/test_superficie.py tests/integration/test_previas.py -v`; confirmar falha.
- [ ] Implementar distância entre superfícies e detecção de interseção/contenção com BVH disponível no worker Blender para selecionar pares candidatos. Na verificação fina, incluir triângulo–triângulo, aresta–aresta e contenção em malha fechada; testar cada caso com geometria analítica. Distância apenas vértice–vértice não atende ao gate. Superfície aberta/degenerada retorna `SURFACE_NOT_CERTIFIABLE` quando interior for obrigatório; distância unsigned não prova ausência de penetração.
- [ ] Para `surface_clearance`, obter ponto de colisão, região e direção de afastamento; converter em alvos do worker, compor e avaliar novamente. No máximo o orçamento da receita. Movimento rápido ganha amostras intermediárias com subdivisão adaptativa limitada; relatar amostragem, tolerância e trechos não certificados.

```python
if report["uncertified_intervals"] and recipe["requires_surface_gate"]:
    return {"passed": False, "code": "SURFACE_NOT_CERTIFIABLE"}
if report["min_clearance_m"] < recipe["minimum_m"]:
    return {"passed": False, "code": "CLEARANCE_VIOLATION"}
```

- [ ] Gerar frente, perfil, três quartos e detalhe com câmeras fixadas a partir da base; aplicar as mesmas câmeras à candidata. Gerar folha de contato e vídeo curto, marcando frames de pior erro. Testar igualdade das matrizes/capturas temporais A/B e existência/hash dos artefatos, não apenas o log do renderer.
- [ ] Rodar teste de cotovelo com pesos ruins: diagnóstico pode indicar deformação/skin, mas não corrigi-la automaticamente. Conferir que falta de evidência final impede promoção exigida. Registrar checkpoint e abrir as prévias reais para inspeção do agente.

## B3 — Exportar, reabrir e demonstrar o primeiro ciclo completo

Arquivos: criar `src/animai/publicacao/servico.py`,
`publicacao/recibos.py`, `publicacao/perdas.py` no pacote;
`workers/blender/exportar.py`, `tests/integration/test_exportacao.py`,
`tests/acceptance/test_oficina_local.py`, `docs/uso/primeiro-ciclo.md`.

Interfaces: `publish_candidate(studio: Studio, request: dict) -> dict` no
serviço; `verify_export(expected: dict, imported: dict, policy: dict) -> dict`
em recibos. `destination` contém `format`, `path`, `action='candidate'` e
`metadata_policy='sidecar'|'native_required'`. Sidecar é manifesto versionado
ligado ao hash do arquivo, nunca um aviso de perda silencioso.

- [ ] Escrever teste parametrizado GLB/FBX que exporta, reimporta em processo limpo e compara movimento, identidade e metadados.

```python
import pytest

@pytest.mark.parametrize("format_name", ["glb", "fbx"])
def test_export_is_verified_after_reopening(export_case, format_name):
    out = export_case.roundtrip(format_name)
    assert out["status"] == "ready"
    assert out["data"]["receipt"]["verified"] is True
    assert out["data"]["max_position_error_m"] <= 0.0001
    assert out["data"]["max_rotation_error_deg"] <= 0.1
    assert out["data"]["event_times_match"] is True
```

- [ ] Criar `export_case` em `tests/support/exportacao.py`, com `roundtrip(format_name)`, arquivo temporário permitido e amostragem canônica. Rodar `uv run pytest tests/integration/test_exportacao.py -v`; confirmar falha.
- [ ] Implementar exportação em cópia, sem simplificação de curvas por padrão, sem ossos de folha extras e com tempo/unidade explicitados. Preservar metadados no arquivo quando suportados; caso contrário exigir sidecar autorizado ou retornar `UNSUPPORTED_METADATA`. Publicação fora de raiz permitida e sobrescrita implícita falham antes do worker.

```python
if unsupported_metadata and policy == "native_required":
    raise DomainError("UNSUPPORTED_METADATA", "Destino não representa metadados", {
        "fields": sorted(unsupported_metadata)}, False)
```

- [ ] Reabrir e comparar poses em repouso, frames extremos, trecho alterado, duração e raiz. Testar sidecar ausente/trocado, falha entre arquivo e sidecar e asset já existente: manter fonte e registrar saída parcial sem recibo aprovado.
- [ ] Executar caso completo pela API/CLI: importar, corrigir mão–rosto, manter empunhadura, gerar A/B, fazer segundo ajuste sobre a nova revisão, reverter e exportar. A fixture visual deve passar também por M3; não aprovar apenas imagens bonitas.
- [ ] Rodar `uv run --locked python -m animai.gates --stage E3 --report artifacts/E3.json`, inspecionar vídeo em mais de um ângulo e preparar checkpoint. Entregar ao usuário a comparação, dizer exatamente o que olhar e registrar opinião artística separada do gate técnico.

## Saída de E3

Primeira entrega utilizável, ainda externa ao jogo. Evidências necessárias:
clip original e corrigido, vídeo A/B, detalhe de mãos, métricas, revisão
revertida e export reaberto. Uma falha superficial mantém E3 aberta; não
transferir a correção para um procedimento manual no editor.
