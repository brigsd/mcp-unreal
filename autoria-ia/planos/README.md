> Cópia histórica desde 19/09/2026. O AnimAI agora tem raiz própria.
> Fonte atual: [docs/desenvolvimento/planos/README.md](../../../AnimAI/docs/desenvolvimento/planos/README.md).
> O conteúdo abaixo foi preservado para consulta e não governa trabalho novo.

# AnimAI — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Entregar o AnimAI, conjunto modular para editar e verificar animações por trecho, preservar trabalho aprovado e publicar assets convencionais, com documentação e skills distintas para uso e desenvolvimento.

**Architecture:** Serviços independentes do motor, acessíveis pela mesma API através de CLI e MCP. Bibliotecas ficam atrás de adaptadores substituíveis; tarefas e revisões são persistidas. A primeira entrega útil não depende de geração neural nem do Jogo01.

**Tech Stack:** Python 3.11, NumPy, Pydantic 2, SQLite, pytest e uv no núcleo; Momentum em worker isolado; Blender para intercâmbio e inspeção; SDK MCP Python 2 em extra separado. Unreal e Kimodo entram nas etapas finais. Versões exatas e hashes serão fixados ao produzir os ambientes, sem assumir que a versão mais recente esteja homologada.

**Spec:** [Contrato do conjunto modular, v1.2](../CONTRATO.md), [contrato macro](../docs/desenvolvimento/CONTRATO-MACRO.md) e [documentação e skills](DOCUMENTACAO-E-SKILLS.md).

## Global Constraints

- “Animação de personagens é o primeiro domínio.”
- “Mecanifica permanece independente e responsável por seus objetos mecânicos.”
- “Jogo01 é consumidor, com seus assets e perfis.”
- “Revisões são imutáveis.”
- “Preservações e tolerâncias são fixadas antes da execução, com unidade e referencial, e conferidas no resultado.”
- “Só promover uma candidata quando cumprir os critérios obrigatórios do pedido.”
- “Descoberta não carrega modelos nem instala dependências.”
- “O jogo recebe assets convencionais.”
- “Uso e desenvolvimento têm documentação e skills próprias, mantidas com cada capacidade.”
- “Cumprir este plano não comprova superioridade da arquitetura escolhida.”
- “A leitura deste documento não autoriza instalações, publicação remota ou implementação automática.”

---

## Estado e leitura

Plano criado em 19/09/2026; execução ainda não iniciada. Os seis planos abaixo
formam entregas dependentes, com tarefas pequenas, testes de regressão e um
critério de saída próprio. Os blocos de código são especificações para a futura
implementação; os comandos ainda não existem neste repositório.

Revisado em 19/09/2026 para o nome AnimAI e as duas trilhas de documentação e
skills. São seis etapas e 23 tarefas, incluindo A0 para estabelecer essa base.
Inclui contrato macro e [gatilhos de atualização](../docs/desenvolvimento/ATUALIZACAO-E-HOOKS.md):
instruções documentais presentes; verificador em A0, gates em A1 e distribuição
em O4. Nenhum hook automático AnimAI está instalado nesta revisão.
O [índice do conjunto](../README.md) é a entrada por papel; este plano é para
quem desenvolve, não leitura obrigatória de quem apenas usa.

Leia o contrato, as [interfaces compartilhadas](INTERFACES.md) e somente o
plano da etapa em execução. O [registro técnico](REFERENCIAS.md) explica as
escolhas de integração e limitações que não podem ser esquecidas. O estudo de
17/09 continua sendo referência histórica, sem substituir estes documentos.

O código nascerá em `C:\Users\micro\Desktop\MCP_Unreal\autoria-ia\oficina`.
Essa pasta será um pacote autocontido; não será necessário transferir hooks,
skills Unreal ou assets de jogo quando o pacote ganhar repositório próprio.
Não criar um repositório remoto nesta implementação por efeito implícito.

O diretório histórico `autoria-ia/` não muda nesta revisão. Os nomes futuros
do pacote Python, CLI e servidor são `animai`, `animai` e `animai-mcp`;
a descoberta será `animai.describe`. Como ainda não há implementação, não
criar aliases de execução para os antigos nomes propostos.

## Etapas e progresso

| Etapa | Entrega observável | Depende de | Situação |
| --- | --- | --- | --- |
| [E1 — Base e revisões](01-base-e-revisoes.md) | Estabelecer docs/skills por papel; registrar personagem/movimento, guardar revisões e consultar capacidades pela CLI. | Contrato aprovado. | Não iniciada. |
| [E2 — Edição com Momentum](02-edicao-e-momentum.md) | Editar um trecho sem alterar canais protegidos; medir contatos e continuidade; rejeitar conflito e desfazer. | E1. | Não iniciada. |
| [E3 — Inspeção e primeira entrega](03-inspecao-e-intercambio.md) | Inspecionar pele e antes/depois automaticamente, exportar e conferir a ida e volta. | E2; B1 pode começar após E1. | Não iniciada. |
| [E4 — MCP e operação confiável](04-mcp-e-operacao.md) | Executar o ciclo pela IA, com progresso, fila, cancelamento e retomada após interrupção. | E3. | Não iniciada. |
| [E5 — Unreal](05-publicacao-unreal.md) | Extrair um personagem e publicar/reabrir uma animação candidata na Unreal, com metadados preservados. | E4. | Não iniciada. |
| [E6 — Kimodo opcional](06-geracao-kimodo.md) | Gerar uma base, adaptá-la e reeditá-la sem recarregar o modelo. | E5. | Não iniciada. |

O primeiro momento de validação visual pelo usuário é o fim de E3. O primeiro
ciclo completo via MCP é E4. E5 entrega integração no motor; E6 amplia as fontes
de movimento. Não chamar E2 de solução para pele deformada nem E3 de animação
validada em gameplay.

Os checkboxes dentro de cada tarefa são a fonte de progresso fino. Esta tabela
resume a etapa, sem manter uma segunda lista de tarefas. Ao concluir uma etapa,
registrar em `oficina/docs/desenvolvimento/planos/relatorios/E<N>.md` após a
migração de A0: revisão do código, ambientes,
comandos executados, resultado, evidências, limitações e próximo passo. A pasta
de relatórios só será criada quando houver resultados reais.

## Abordagem escolhida

Construir primeiro um caminho vertical estreito: personagem registrado,
movimento conhecido, correção localizada, inspeção e revisão reversível.
Não começar por um catálogo amplo de geradores ou uma interface gráfica.
A prova de instalação e fidelidade do Momentum acontece em E2/M1, antes de
investir no editor temporal completo. Se houver falha, o teste identifica
instalação, representação ou resolução; não reabre uma busca genérica.

A biblioteca é consumida por adaptador. PyRoki/jaxls só recebe um recorte de
integração se a prova mostrar uma limitação concreta que ele possa resolver.
Não implementar dois backends completos preventivamente. Não escrever um
resolvedor temporal próprio para contornar uma configuração incorreta.

O formato persistido é próprio, mas o pacote não reinventa skinning, render,
transporte MCP ou rotinas numéricas já disponíveis. A verificação independente
dos resultados pertence à oficina; ela não aceita a palavra do gerador ou do
resolvedor como prova de preservação.

## Localização dos arquivos futuros

Todos os caminhos das tarefas são relativos a
`C:\Users\micro\Desktop\MCP_Unreal\autoria-ia\oficina`, exceto quando indicado.
São caminhos planejados, não links para implementação existente.

| Caminho futuro | Responsabilidade |
| --- | --- |
| `pyproject.toml`, `uv.lock` | Pacote leve, dependências e comandos da oficina. |
| `src/animai/api.py`, `interfaces/` | API única, CLI e fachada MCP. |
| `src/animai/core/` | Schemas comuns, catálogo, revisões, artefatos, tarefas e política de recursos. |
| `src/animai/personagens/` | Pacote, calibração e capacidades por personagem. |
| `src/animai/movimentos/` | Fontes, tempo, curvas, eventos e revisões de movimentos. |
| `src/animai/edicao/` | Máscaras, alvos, contatos, retarget e preservação. |
| `src/animai/inspecao/` | Medidas, comparações e relatórios. |
| `src/animai/publicacao/` | Preparação, diário e verificação de exportação. |
| `src/animai/integracoes/` | Clientes isolados de Momentum, Blender, Unreal e Kimodo. |
| `workers/` | Executores de cada fornecedor, fora do processo do núcleo. |
| `ambientes/` | Manifestos e locks por worker; nenhum ambiente binário no Git. |
| `tests/unit/`, `tests/integration/`, `tests/acceptance/` | Regras puras, fronteiras reais e ciclo de uso. |
| `tests/support/`, `tests/fixtures/` | Dados próprios, pequenos e reproduzíveis. |
| `README.md`, `AGENTS.md` | Identidade AnimAI, estado e roteamento por papel, sem obrigar leitura de todo o histórico. |
| `docs/uso/` | Fluxos operacionais, retorno, exemplos, diagnóstico e recuperação para quem usa. |
| `docs/desenvolvimento/` | Arquitetura, contratos, módulos, decisões, testes, planos e evolução. |
| `skills/animai-usar/`, `skills/animai-desenvolver/` | Duas skills com gatilhos, referências e testes próprios. |
| `docs/manifesto.json`, `tests/docs/`, `tests/skills/` | Vínculos de fontes e versões, validação documental e cenários por papel. |

A árvore, fontes únicas, migração dos documentos atuais e entregas por etapa
estão no [plano de documentação e skills](DOCUMENTACAO-E-SKILLS.md).

## Regra de execução de cada tarefa

Cada tarefa contém um teste inicial e um recorte de implementação. Executar
teste vermelho, implementação, teste verde e revisão do diff. Quando um bloco
exigir várias mudanças, separá-lo em ciclos de uma função/comportamento por vez;
os blocos não são estimativas de duração total. Não pular testes negativos.

Antes de alterar código, conferir instruções locais e `git status`; preservar
mudanças preexistentes e usar worktree isolado para implementação quando
adequado. Não alterar `.claude-plugin/plugin.json`, `hooks/` ou `skills/unreal-mcp/`
para instalar a nova oficina. Instalação futura em cliente é ação separada.

Rodar os testes específicos da tarefa e os gates acumulados. Integrações ausentes
podem ser excluídas da suíte rápida, mas nunca contadas como aprovadas no gate
da etapa que depende delas. Registrar falha, cancelamento e teste não executado
de forma diferente. Sem evidência, a etapa continua aberta.

Cada tarefa deve atualizar o guia de uso afetado, seu contrato de desenvolvimento
e referências da skill pertinente. Exemplo, schema e capability precisam
concordar. E1/A0 estabelece os validadores; E4/O4 verifica também a distribuição
e uso em contexto novo. Documentação desatualizada mantém a tarefa aberta.

Mudança de fonte, dependência, requisito ou evidência reabre somente os
documentos/decisões afetados. A0 implementa o verificador de validade documental
e A1 o chama pelos gates. Pesquisa vencida alheia ao recorte gera aviso, sem
bloquear operações válidas; não pode sustentar nova certificação de escolha
atual. A pergunta macro dispara pesquisa atual, não execução automática.

Ao final de cada tarefa, preparar um checkpoint local com apenas seus arquivos;
commits dependem da política de execução autorizada, sem `git add .`, push ou
publicação automática. Os planos desta rodada não fazem nenhum commit.

## Gates acumulados e cobertura

| Exigência do contrato | Implementação e prova |
| --- | --- |
| Identidade AnimAI, docs/skills por papel e leitura progressiva. | E1/A0, manutenção em cada tarefa e E4/O4; cenários em contexto novo. |
| Entendimento macro e detecção de evidência/documentação desatualizada. | E1/A0 (cenários e verificador), E1/A1 (gates), E4/O4 (distribuição). |
| Independência de motor, MCP fino e capacidades verdadeiras. | E1/A1, E4/O3. |
| Dados completos, identidades, coordenadas e calibração. | E1/A2–A3, E2/M1, E3/B1, E5/U1. |
| Revisões imutáveis, conflitos, retorno e reversão. | E1/A4, E2/M2–M3. |
| Edição por trecho, contatos, continuidade e operações de tempo. | E2/M2–M5, E3/B2. |
| Inspeção numérica, visual e contexto separados. | E3/B2–B3, E5/U3. |
| Dependências, licenças e isolamento. | E1/A1, E2/M1, E4/O1, E6/G1. |
| Cancelamento, retomada, cache e limites. | E4/O1–O2, E6/G2. |
| Exportação segura, metadados e leitura após escrita. | E3/B3, E5/U2–U3. |
| Geração opcional e ausência de carga neural no jogo. | E6/G1–G3; E1–E5 independem dela. |

O detalhe de uma descoberta pode ajustar uma implementação, mas não enfraquecer
um gate. Alterar escopo, tolerâncias aprovadas ou fronteiras exige registrar a
decisão e obter aprovação. Tempo gasto e métricas de desempenho serão medidos
por etapa; não há promessa de prazo ou benchmark nesta documentação.

## Próximo passo autorizado por este planejamento

Entregar e revisar estes planos. Quando o usuário autorizar implementar,
começar por E1/A0 e depois A1. Recomendo execução por tarefas com revisão entre entregas;
subagentes podem trabalhar em arquivos independentes depois dos contratos
comuns, sem concorrência sobre schemas, catálogo ou workspace de publicação.
Execução sequencial na mesma tarefa também é válida e usa os mesmos gates.
