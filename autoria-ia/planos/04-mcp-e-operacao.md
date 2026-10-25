> Cópia histórica desde 19/09/2026. O AnimAI agora tem raiz própria.
> Fonte atual: [docs/desenvolvimento/planos/04-mcp-e-operacao.md](../../../AnimAI/docs/desenvolvimento/planos/04-mcp-e-operacao.md).
> O conteúdo abaixo foi preservado para consulta e não governa trabalho novo.

# E4 — MCP e operação confiável Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Operar a oficina pela IA com tarefas persistentes, cancelamento, recuperação e retorno enxuto, sem coordenar manualmente programas e placas.

**Architecture:** O mesmo serviço de E1–E3 atende MCP e CLI. Jobs persistidos separam pedidos curtos de processamento longo; workers têm reservas explícitas de recursos. Transporte inicial stdio, sem serviço exposto na rede.

**Tech Stack:** Python, SQLite, subprocessos, SDK MCP Python 2 como extra, pytest/AnyIO e manifests locais de recursos.

**Spec:** [Contrato](../CONTRATO.md), [interfaces](INTERFACES.md) e [mestre](README.md).

## Global Constraints

Valem as [restrições globais](README.md#global-constraints). “Descoberta não
carrega modelos nem instala dependências.” “Revisões são imutáveis.” E3
concluída é pré-condição. A oficina só cancela processos que ela iniciou.

---

## O1 — Diário de jobs, idempotência e retomada

Arquivos: criar `src/animai/core/tarefas.py`, `core/executor.py`,
`core/cache.py` no pacote; `tests/unit/test_jobs.py`,
`tests/integration/test_recuperacao.py`, `tests/support/fault_worker.py`,
`docs/desenvolvimento/modulos/tarefas.md`; modificar API, serviços e clientes de workers.

Interfaces: JobStore de INTERFACES, com construtor `JobStore(workspace: Path)`;
`JobExecutor(store: JobStore, services: Services).run_once() -> dict` em
executor processa uma etapa pronta. `cache_key(inputs: dict, versions: dict,
settings: dict) -> str` em cache. JobStore.status retorna estado, etapa,
progresso, tentativa, último artefato íntegro e `result` quando concluído.

- [ ] Escrever teste de interrupção entre resolução e render, garantindo que retomada não execute de novo a etapa íntegra.

```python
def test_resume_reuses_verified_steps(recovery_case):
    job_id = recovery_case.submit_guard()
    recovery_case.run_until("solve-complete")
    recovery_case.interrupt_own_worker()
    recovery_case.restart_coordinator()
    result = recovery_case.resume_and_finish(job_id)
    assert result["status"] == "ready"
    assert recovery_case.executions("solve") == 1
    assert recovery_case.executions("render") == 1
    assert recovery_case.partial_revision_was_published is False
```

- [ ] Implementar `recovery_case` em `tests/support/recuperacao.py`, com os métodos acima, subprocesso controlado e contadores persistidos; o worker de falhas é somente fixture, nunca tool pública. Rodar `uv run pytest tests/unit/test_jobs.py tests/integration/test_recuperacao.py -v`; confirmar falha.
- [ ] Persistir pedido validado antes de iniciar worker. Gravar estados e etapas com hashes; após reinício, `running` sem processo próprio vivo vira recuperação necessária. Revalidar arquivos/hash e `expected_head` antes de reusar resultados ou promover. Não repetir efeitos externos sem reconciliar o recibo.

```python
cached = cache.lookup(stage_key)
if cached is not None and artifacts.verify(cached):
    return cached
result = worker.execute(operation, manifest_path, output_dir, budget)
artifacts.verify_or_raise(result)
cache.record(stage_key, result)
return result
```

- [ ] Implementar cancelamento cooperativo com deadline e término apenas do grupo de processos pertencente ao job. Conferir PID e instante de criação para evitar matar PID reutilizado. Cancelamento observado antes do commit impede promoção; depois de commit, devolver estado já concluído e referência íntegra, sem fingir rollback.
- [ ] API normal passa a enfileirar operações pesadas e retorna `queued/job_id`; `job.control` consulta ou retoma. Testes de serviço podem usar `settings.execution_mode='inline'`, executando as mesmas etapas e verificações. Atualizar fixtures existentes para esse modo, sem criar um segundo executor simplificado.
- [ ] Testar idempotência após queda, lease vencido, erro permanente, timeout, cancelamento antes/depois do commit e alteração de dependência invalidando só o cache afetado. Registrar checkpoint e recibo de recuperação.

## O2 — Recursos previsíveis e ambientes isolados

Arquivos: criar `src/animai/core/recursos.py`, `core/processos.py`,
`core/configuracao.py` no pacote; `config/recursos.example.json`,
`tests/unit/test_recursos.py`, `tests/integration/test_processos.py`,
`docs/uso/configurar-e-recuperar.md`.

Interfaces: `ResourcePool(inventory: dict, policy: dict)` com
`acquire(job_id: str, requirements: dict) -> dict` e
`release(job_id: str) -> dict`; aquisição não disponível retorna `queued`
com motivo, não outra placa. Inventário usa UUID estável e orçamento de
RAM/VRAM/threads; configuração da máquina fica fora de receitas portáveis.

- [ ] Escrever teste para a falha que motivou este trabalho: duas cargas não podem cair silenciosamente na mesma placa.

```python
from animai.core.recursos import ResourcePool

def test_busy_gpu_does_not_trigger_silent_fallback():
    inventory = {"gpus": [{"uuid": "GPU-A", "free_mb": 12000},
                           {"uuid": "GPU-B", "free_mb": 11000}], "ram_free_mb": 24000}
    pool = ResourcePool(inventory, {"gpu_fallback": False, "max_workers": 2,
                                    "allowed_gpu_uuids": ["GPU-A", "GPU-B"]})
    req = {"gpu_uuid": "GPU-A", "vram_mb": 6000, "ram_mb": 4000}
    first = pool.acquire("one", req)
    second = pool.acquire("two", req)
    assert first["state"] == "acquired"
    assert second["state"] == "queued"
    assert "gpu_uuid" not in second or second["gpu_uuid"] != "GPU-B"
```

- [ ] Rodar `uv run pytest tests/unit/test_recursos.py tests/integration/test_processos.py -v`; confirmar falha.
- [ ] Implementar reserva exclusiva por identidade, headroom configurável e conferência de memória livre antes da carga. Default: um worker pesado por vez e no máximo quatro threads CPU, limitado também ao hardware disponível. O pool coordena RAM global mesmo com GPUs diferentes. Não prometer reserva contra outros aplicativos; se memória mudar, aguardar/recusar com diagnóstico.

```python
if requested_uuid not in policy["allowed_gpu_uuids"]:
    raise DomainError("RESOURCE_NOT_ALLOWED", "GPU fora da política", {}, False)
if requested_uuid in leases or free_mb < required_mb + safety_margin_mb:
    return {"state": "queued", "reason": "insufficient_or_reserved_resource"}
```

- [ ] Associar processos ao job e inicializar helper em background sem janela visível no Windows. Configurar WSL só para worker que o exija; traduzir caminhos explicitamente. Não alterar serviços, drivers, distribuição Linux ou variáveis globais para atender uma tarefa.
- [ ] Testar pausa/liberação de cargas próprias, processo alheio protegido, memória reduzida, GPU removida e mudança da ordem dos índices CUDA. Registrar política efetiva e limites; documentar um comando de diagnóstico, sem pedir ao usuário repetir ajustes por sessão.
- [ ] Rodar suíte de recuperação novamente; registrar checkpoint.

## O3 — Sete tools, schemas e artefatos pelo MCP

Arquivos: criar `src/animai/interfaces/mcp_server.py`,
`src/animai/interfaces/artefatos.py`, `tests/integration/test_mcp.py`,
`tests/integration/test_mcp_stdio.py`, `docs/uso/conectar-mcp.md`;
modificar `pyproject.toml` com extra MCP e atualizar lock.

Interfaces: `create_server(studio: Studio) -> MCPServer`; uma tool por
operação de INTERFACES, com modelo tipado de entrada e `Response` de saída.
Para uniformidade, MCP recebe `{"request": <payload>}`; o adaptador remove
somente esse envelope. CLI e API continuam recebendo o payload diretamente.
Resources `animai://artifacts/{hash}` servem somente artefatos registrados.

- [ ] Escrever teste de equivalência da descoberta e teste negativo de schema.

```python
import pytest
from mcp import Client
from animai.interfaces.mcp_server import create_server

@pytest.mark.anyio
async def test_mcp_uses_the_same_response(studio):
    expected = studio.call("animai.describe", {})
    async with Client(create_server(studio), raise_exceptions=True) as client:
        result = await client.call_tool("animai.describe", {"request": {}})
    assert result.structured_content["data"] == expected["data"]
    assert result.structured_content["status"] == "ready"
```

- [ ] Fixar SDK `mcp>=2,<3` no extra e versão exata no lock. Configurar fixture AnyIO `asyncio`; rodar `uv run --extra mcp pytest tests/integration/test_mcp.py -v` e confirmar falha. Usar APIs verificadas da versão travada, sem importar FastMCP v1.
- [ ] Implementar wrappers pequenos, de tipos compartilhados. `DescribeRequest` é modelo vazio com `module` opcional em `core/catalogo.py`; modelos das outras operações pertencem a seus módulos.

```python
@server.tool(name="animai.describe")
def describe(request: DescribeRequest) -> Response:
    return Response.model_validate(studio.call(
        "animai.describe", request.model_dump(exclude_none=True)))
```

- [ ] Expor respostas estruturadas, resumo textual curto e recursos/imagens por referência controlada. Erros de operação devem também ser sinalizados no resultado MCP; não retornar somente texto com aparência de sucesso. Rotular read-only apenas quando verdadeiro: inspeção que grava artefatos não é leitura pura.
- [ ] Testar handshake e sete tools em subprocesso stdio; stdout não pode conter logs. Repetir ciclo E3 pelo cliente MCP e comparar IDs, violações e hashes com API/CLI, ignorando tempos/IDs de execução quando legítimo. Injetar payload extra, URI alheia e capability ausente; nenhum deve iniciar processo.
- [ ] Registrar checkpoint e exemplo de configuração gerado com caminhos absolutos da instalação. Não instalar automaticamente em contas/clientes nem abrir endpoint HTTP.

## O4 — Empacotamento, documentação e skills portáveis

Arquivos: criar `docs/uso/gotchas.md`,
`docs/desenvolvimento/distribuicao.md`, `tests/acceptance/test_instalacao_limpa.py`,
`tests/acceptance/test_ciclo_mcp.py`, `tests/docs/test_bundles_skills.py`,
`scripts/build_skills.py`; atualizar os dois índices, `docs/manifesto.json`,
`skills/animai-usar/SKILL.md`, `skills/animai-desenvolver/SKILL.md` e cenários
em `tests/skills/`. Completar documentos de cada módulo.

Interfaces: instalação do pacote fornece `animai` e `animai-mcp` como
entrypoints, apontando para CLI e servidor existentes. Manifests de schemas
e capacidades derivam dos modelos; skill referencia essa fonte, sem copiar
listas divergentes. As duas skills nasceram em A0 e evoluem por capacidade;
esta tarefa valida sua distribuição e o ciclo completo, não adia sua criação
para o fim. Seguir [documentação e skills](DOCUMENTACAO-E-SKILLS.md).
Na execução, ler as skills de criação/validação antes de alterar SKILL.md.

- [ ] Criar teste de instalação em ambiente temporário sem Unreal, Blender, Momentum ou Torch; catálogo deve funcionar e dizer o que falta.

```python
def test_minimal_install_does_not_require_workers(clean_install):
    out = clean_install.call("animai.describe", {})
    assert out["status"] == "ready"
    assert clean_install.imported_heavy_modules == []
    assert clean_install.network_requests_during_discovery == 0
```

- [ ] Definir `clean_install` em `tests/support/instalacao.py`, com ambiente criado da wheel/lock, captura de imports e bloqueio de rede durante descoberta. Rodar o teste e confirmar falha antes do empacotamento.
- [ ] Implementar build/entrypoints e inclusão dos schemas; manter modelos, ambientes e assets privados fora da wheel. Documentar selecionar fonte, editar, examinar retorno, corrigir, reverter e publicar. Atualizar arquitetura, ambiente, testes e módulos na trilha de desenvolvimento. Gotchas registra configuração que falhou, erro observável e correção comprovada, sem “dicas” não testadas.

```toml
[project.scripts]
animai = "animai.interfaces.cli:main"
animai-mcp = "animai.interfaces.mcp_server:main"
```

- [ ] Antes do build das skills, escrever testes negativos de link fora do checkout, hash divergente, fonte ausente e versão incompatível. Implementar `scripts/build_skills.py`: gerar bundles separados, referências necessárias, links relocáveis e manifesto de origem/hashes. Não duplicar manualmente documentação nem incluir planos de desenvolvimento no bundle de uso.
- [ ] Validar estrutura de cada skill e abrir todas as referências obrigatórias do bundle em diretório temporário sem acesso ao checkout. Rodar `uv run --locked pytest tests/docs/ -v`; conferir exemplos contra schemas/capacidades e documentar versão compatível. Não instalar em cliente como efeito do build.
- [ ] Validar comando de freshness e gatilhos macro no checkout relocável e bundle de desenvolvimento. Documentar conexão do gate à CI real do repositório escolhido e aos hooks opcionais do cliente, testando detecção de documento dependente desatualizado. Não criar workflow aninhado inoperante nem substituir hooks existentes; integrações não autorizadas ficam explicitamente não instaladas.
- [ ] Repetir baseline/pós-skill com contexto novo para cada papel: uso do ciclo real; desenvolvimento de adaptador; capacidade ausente; diagnóstico sem implementação autorizada; não ativação para Mecanifica; operação fora do checkout. Registrar evidências e corrigir orientação apenas onde necessário, testando cada skill alterada separadamente.
- [ ] Demonstrar uma sessão começando por `animai-usar` e documentação de uso, sem abrir dossiês de desenvolvimento nem dirigir editores. O ciclo deve permitir segunda correção sobre revisão anterior; medir chamadas, tempo de carga, tempo de edição e render separadamente. Conferir também que `animai-desenvolver` encontra contrato e testes sem depender do histórico desta conversa.
- [ ] Rodar `uv run --locked --extra mcp python -m animai.gates --stage E4 --report artifacts/E4.json`. Registrar checkpoint e evidências. Só então oferecer instalação no cliente escolhido pelo usuário.

## Saída de E4

A IA opera o ciclo completo pela API/MCP com recuperação e limites reais.
Docs e skills das duas trilhas correspondem à versão entregue, passam pelos
cenários em contexto novo e são relocáveis, sem dependência do checkout.
A revisão técnica não substitui a opinião do usuário sobre atuação. E5 usa
esse mesmo ciclo para publicar no motor; não cria outra oficina dentro dele.
