> Cópia histórica desde 19/09/2026. O AnimAI agora tem raiz própria.
> Fonte atual: [docs/desenvolvimento/planos/02-edicao-e-momentum.md](../../../AnimAI/docs/desenvolvimento/planos/02-edicao-e-momentum.md).
> O conteúdo abaixo foi preservado para consulta e não governa trabalho novo.

# E2 — Edição com Momentum Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Corrigir movimento por trecho, preservar canais e relações, medir continuidade e adaptar uma fonte a outro personagem.

**Architecture:** O núcleo compila intenção, monta propostas e verifica o resultado completo. Um worker Momentum propõe soluções numéricas; revisões só são promovidas após medição independente. A representação do fornecedor não substitui os dados completos do personagem.

**Tech Stack:** Núcleo de E1; Momentum via `pymomentum.geometry`/`solver2` em ambiente isolado; NumPy e SciPy para conversões verificáveis, não para iniciar um resolvedor temporal próprio.

**Spec:** [Contrato](../CONTRATO.md), [interfaces](INTERFACES.md), [mestre](README.md) e [referências](REFERENCIAS.md).

## Global Constraints

Valem as [restrições globais](README.md#global-constraints). “Preservações e
tolerâncias são fixadas antes da execução, com unidade e referencial, e
conferidas no resultado.” “Só promover uma candidata quando cumprir os
critérios obrigatórios do pedido.” E1 concluída é pré-condição.

---

## M1 — Prova de integração e fidelidade, antes do editor completo

Arquivos: criar `ambientes/momentum/pixi.toml`, seu lock,
`workers/momentum/main.py`, `workers/momentum/conversao.py`,
`src/animai/integracoes/protocolo.py`,
`src/animai/integracoes/momentum.py`,
`tests/integration/test_momentum.py`, `docs/desenvolvimento/modulos/dependencias.md`.

Interfaces: WorkerClient de INTERFACES; operações internas `probe`, `fk` e
`solve`. `probe` devolve versões, imports, operações e limitações;
`fk` devolve `positions_m`, `rotation_xyzw` mundiais e hash da entrada; `solve` devolve
bundle candidato, medidas do fornecedor e tempo, sem promover revisão.
Cliente `MomentumClient(settings: dict)` implementa WorkerClient.

- [ ] Criar teste que importa os módulos no worker real e compara FK à cadeia analítica de A2, incluindo repouso assimétrico, raiz e mão rotacionada.

```python
import numpy as np
from animai.integracoes.momentum import MomentumClient

def test_real_worker_reports_and_matches_fk(sample, tmp_path, worker_settings):
    worker = MomentumClient(worker_settings)
    report = worker.execute("probe", sample.actor_path / "character.json",
                            tmp_path / "probe", {"wall_seconds": 60})
    assert report["status"] == "ready"
    assert "solve" in report["operations"]
    result = worker.execute("fk", sample.analytic_actor_path / "character.json",
                            tmp_path / "fk", {"wall_seconds": 60})
    assert np.allclose(result["positions_m"], sample.analytic_expected_positions,
                       atol=0.0001, rtol=0)
```

- [ ] Rodar `uv run pytest tests/integration/test_momentum.py -v`; sem configuração, o gate deve falhar explicitamente. `worker_settings` lê o arquivo local indicado por `ANIMAI_TEST_SETTINGS`; não inventa um interpretador instalado.
- [ ] Preparar ambiente isolado usando distribuição conda-forge/Pixi do núcleo Momentum. Resolver e fixar versão/build/hash; conferir os símbolos necessários no binário. Se o pacote disponível não expuser `solver2`, registrar a incompatibilidade e usar uma revisão de fonte identificada, com build isolado; não assumir que binário e documentação de `main` são equivalentes.

```python
command = [settings["python"], str(settings["worker"]),
           "--operation", operation, "--manifest", str(manifest_path),
           "--output", str(output_dir)]
completed = subprocess.run(command, shell=False, capture_output=True,
                           text=True, timeout=budget["wall_seconds"])
```

- [ ] Implementar conversão completa e testar pose→parâmetros→pose, juntas fora da cadeia ativa, dedos e escala. Comparar também rotações ao esperado analítico com limite de 0,1 grau, fora do worker. Canais que o backend não representa continuam guardados; se alterarem a FK de uma cadeia ativa, recusá-la com `UNSUPPORTED_KINEMATICS`. Não recolocar escala depois de resolver uma geometria diferente.
- [ ] Rodar microcaso de cinco poses com alvo alcançável e canal protegido animado, usando a API de sequência real. Publicar recibo com versões, perdas e medidas. Somente habilitar o backend se a prova de preservação passar.
- [ ] Registrar checkpoint e decisão: aprovar Momentum para o recorte testado ou nomear requisito que falhou. São permitidas uma correção focal e nova execução do mesmo caso; persistindo limitação estrutural, propor o adaptador PyRoki/jaxls para esse requisito, antes de continuar M2. Não experimentar bibliotecas aleatórias nem reduzir o gate.

`solver2` tem máscara de parâmetros compartilhada entre frames. Isso não
implementa sozinho máscara arbitrária por tempo. A resolução em M2 trabalha
por janela e conjunto ativo; contexto, recomposição e validação final são
obrigatórios. Funções de erro ponderadas também não equivalem a restrições
rígidas. [API de sequência](https://facebookresearch.github.io/momentum/python_api_doc/solver2.html).

## M2 — Máscaras, limites e composição sem destruir a base

Arquivos: criar `src/animai/edicao/schema.py`, `edicao/mascaras.py`,
`edicao/compilador.py`, `edicao/servico.py` no mesmo pacote;
`tests/unit/test_mascaras.py`, `tests/unit/test_compilador.py` e
`docs/desenvolvimento/modulos/edicao.md`.

Interfaces: `compile_edit` e `compose_candidate` de INTERFACES; compilador
produz recipe versionada, máscara por canal, intervalos de contexto e plano
de execução. `apply_patch_request(studio: Studio, request: dict) -> dict`
fica em edicao/servico.py. Consome RevisionStore e WorkerClient; retorno usa
o envelope comum. Promoção só é habilitada após o verificador M3.

- [ ] Criar teste de composição com proposta maliciosa que altera todos os canais.

```python
import numpy as np
from animai.edicao.mascaras import compose_candidate

def test_forbidden_values_are_copied_from_base(sample):
    base = sample.arrays
    proposed = {key: value + 0.25 for key, value in base.items()}
    allowed = {key: np.zeros(value.shape[:2], dtype=bool)
               for key, value in base.items()}
    allowed["rotation_xyzw"][12:42, 3] = True
    out = compose_candidate(base, proposed, allowed)
    for key in base:
        assert np.array_equal(out[key][~allowed[key]], base[key][~allowed[key]])
```

- [ ] Rodar `uv run pytest tests/unit/test_mascaras.py tests/unit/test_compilador.py -v`; confirmar falha.
- [ ] Implementar máscara por canal TRS, sem expandir implicitamente janela, dedos ou ancestrais. Proibir margem fora da janela autorizada, âncora desconhecida, alvo contraditório e uso de escala para alcançar posição. Composição copia arrays da base e substitui apenas células autorizadas.

```python
out = {key: values.copy() for key, values in base.items()}
for key, mask in allowed.items():
    out[key][mask] = proposed[key][mask]
return out
```

- [ ] Compilar janela ativa e contexto imutável para Momentum. Se máscaras de operações diferirem, particionar por intervalos constantes e validar fronteiras conjuntamente. Não prometer fixação de parâmetros por frame que o backend não oferece; rejeitar recorte não representável. Usar base como inicialização e restrições ponderadas como propostas, nunca como prova final.
- [ ] Adicionar teste para membro protegido animado, rotação local intacta com pai alterado e janela adjacente. Rodar unitários; registrar checkpoint sem anunciar ainda o caso visual resolvido.

## M3 — Verificação independente, contato e primeiro patch completo

Arquivos: criar `src/animai/inspecao/cinematica.py`, `inspecao/metricas.py`,
`edicao/contatos.py`, `edicao/continuidade.py` no pacote;
`tests/unit/test_metricas.py`, `tests/integration/test_patch.py`;
completar serviço, catálogo e `docs/desenvolvimento/modulos/inspecao.md`.

Interfaces: `evaluate` de INTERFACES; `forward_kinematics(character: dict,
arrays: dict) -> dict` em cinemática devolve TRS mundial com IDs. Verificador
usa dados canônicos, não resíduos fornecidos pelo solver. `motion.inspect`
ganha checks de esqueleto e relatório com cobertura explícita.

- [ ] Criar teste do fluxo real, com variante cinemática de `guard_request`.

```python
def test_patch_preserves_grip_and_can_be_undone(integrated, sample):
    studio, actor, motion, base = integrated
    result = studio.call("motion.patch", {
        "mode": "apply", "motion_id": motion, "base_revision_id": base,
        "expected_head": base, "request_id": "guard-kinematic",
        "edit": sample.guard_request(surface=False),
    })
    assert result["status"] == "ready"
    assert result["quality"]["technical"] == "passed"
    assert result["quality"]["destination"] == "not_evaluated"
    assert not result["violations"]
    undo = studio.call("motion.patch", {
        "mode": "select_revision", "motion_id": motion,
        "revision_id": base, "expected_head": result["revision_id"],
        "request_id": "undo-guard",
    })
    assert undo["revision_id"] == base
```

- [ ] Rodar `uv run pytest tests/unit/test_metricas.py tests/integration/test_patch.py -v`; confirmar falha.
- [ ] Implementar preservação exata dos canais externos, erro de posição e distância angular entre quatérnios, limites por perfil e transformação relativa mão–arma. Cada comparação usa referencial explícito. Independência do verificador é comprovada pela cadeia analítica e por proposta propositalmente errada.

```python
relative = np.linalg.inv(object_world) @ anchor_world
rotation_error = 2 * np.arccos(np.clip(abs(np.dot(q_base, q_new)), 0, 1))
# q_base e q_new são unitários; rotation_error está em radianos.
```

- [ ] Medir velocidades/acelerações em segundos e fronteiras do trecho. Para a fixture, limitar derivada da correção a 150 graus/s e 1500 graus/s²; não confundir isso com velocidade absoluta do gesto. Guardar limites por perfil, medir defeitos preexistentes e impedir regressão protegida. Sem suavização fora da janela.
- [ ] Implementar laço de no máximo dois candidatos e três correções dentro do orçamento da receita. Após recompor, avaliar todos os checks obrigatórios; só então RevisionStore.put com CAS. Testar alvo inalcançável, orçamento esgotado e conflito após resolução: todos preservam o head anterior e retornam resíduos/diagnóstico, sem aprovação parcial.
- [ ] Rodar integração real e gate parcial E2; registrar checkpoint e evidência cinemática, explicitamente sem validação de pele.

## M4 — Retarget com orientação e preservação de detalhes

Arquivos: criar `src/animai/edicao/retarget.py`,
`src/animai/personagens/mapeamento.py`,
`tests/integration/test_retarget.py`, `docs/uso/adaptar-movimento.md`;
completar `movimentos/fontes.py` e schema de fonte.

Interfaces: `retarget(source_actor: dict, target_actor: dict, motion: dict,
mapping: dict, target_base: dict, worker: WorkerClient) -> dict` retorna
arrays candidatos, perdas e constraints convertidas. Fonte de `motion.build`
inclui `mapping_id` e `target_base_revision_id` quando precisa preservar dedos.

- [ ] Escrever teste com o segundo personagem de nomes/proporções diferentes, raiz distinta da pelve e dedos ausentes na fonte.

```python
def test_retarget_preserves_missing_fingers(retarget_case):
    out = retarget_case.run()
    assert out["quality"]["technical"] == "passed"
    assert out["data"]["preserved_missing_channels"] == retarget_case.finger_ids
    assert out["data"]["max_grip_error_m"] <= 0.005
    assert out["data"]["root_applied_once"] is True
```

- [ ] Criar `retarget_case` em `tests/support/retarget.py`, usando os dois pacotes de A2, com `run()`, `finger_ids` e base do destino; expor em conftest. Rodar `uv run pytest tests/integration/test_retarget.py -v`; confirmar falha.
- [ ] Converter bases de repouso e orientação, mapear cadeias por IDs confirmados, aplicar escala declarada à trajetória e resolver alvos no destino. Twist sem informação usa prior explícito do perfil e aparece em `losses`; ausência de dedos exige base do destino ou receita de mão, nunca zeros silenciosos.

```python
for joint_id in missing_source_channels:
    target_index = target_joint_ids.index(joint_id)
    candidate["rotation_xyzw"][:, target_index] = target_base["rotation_xyzw"][:, target_index]
```

- [ ] Testar twists, unidades e repouso divergentes, mapeamento ambíguo, socket ausente e root motion aplicado duas vezes. Resolver e verificar no destino com M3; não promover resultado apenas porque a posição das juntas parece correta.
- [ ] Rodar testes, documentar perdas/compatibilidade e registrar checkpoint.

## M5 — Tempo, mãos e operações reutilizáveis

Arquivos: criar `src/animai/movimentos/tempo.py`,
`src/animai/edicao/operacoes.py`, `src/animai/movimentos/receitas.py`,
`tests/unit/test_tempo.py`, `tests/integration/test_operacoes.py`,
`docs/uso/editar-trecho.md`.

Interfaces: `retime(motion: dict, knots: list[tuple[float,float]]) -> dict`
em tempo remapeia arrays e metadados pelo mesmo mapa monotônico;
`expand_recipe(recipe: dict, profile: dict) -> list[dict]` produz operações
tipadas. `finger_pose`, `mirror`, `root_motion` e `transition` usam o mesmo
compilador/máscara de M2 e verificador M3, sem atalhos.

- [ ] Escrever teste que retarda uma ação e seus eventos/contatos igualmente.

```python
from animai.movimentos.tempo import retime

def test_retime_moves_all_metadata_together(timed_motion):
    out = retime(timed_motion, [(0.0, 0.0), (2.0, 4.0)])
    assert out["events"][0]["time_s"] == 1.0
    assert out["contacts"][0]["start_s"] == 0.8
    assert out["contacts"][0]["end_s"] == 1.6
    assert out["duration_s"] == 4.0
```

- [ ] Criar fixture `timed_motion` derivada de A2: evento em 0,5 s, contato em `[0,4;0,8)` e duração 2 s. Rodar `uv run pytest tests/unit/test_tempo.py -v`; confirmar falha.
- [ ] Implementar mapa piecewise linear monotônico, Slerp para rotações, amostragem explícita e remapeamento de eventos, contatos e curvas. Rejeitar mapa não monotônico, evento sem política e mudança de tempo com preservação absoluta incompatível. Metadados contínuos e discretos mantêm políticas próprias.

Neste primeiro recorte, retime exige autorização para o clipe inteiro e todos
os canais temporais. Preservação por índice de frame ou janela parcial é
incompatível e retorna `UNSUPPORTED_TIME_EDIT`. A taxa original é mantida;
a duração final deve coincidir com sua grade de amostras, senão retornar
`TIME_GRID_MISMATCH`. Recalcular N e reamostrar a fonte, sem passar arrays de
N diferente pela máscara de composição M2. O critério é equivalência ao
movimento original no tempo inversamente mapeado, não igualdade de arrays.
Referências animadas externas exigem um contexto temporal explicitamente
compatível; não retimar objetos do cenário sem autorização.

```python
new_event = {**event, "time_s": float(np.interp(event["time_s"], old_times, new_times))}
```

- [ ] Implementar cada operação em um ciclo de teste próprio: dedos por perfil sem mover punho; espelhamento por matriz/reflexão e mapa de lados; root motion com escolha explícita in-place; transição com margens autorizadas e continuidade. Testar espelhar duas vezes, mãos animadas preservadas, loop sem frame extra e drift de apoio após transição.
- [ ] Rodar `uv run --locked python -m animai.gates --stage E2 --report artifacts/E2.json`. Gate inclui Momentum real, todas as operações habilitadas e falhas negativas. Registrar checkpoint e relatório E2; nenhuma alegação de aparência final antes de E3.
