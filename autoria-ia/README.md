> Cópia histórica desde 19/09/2026. O AnimAI agora tem raiz própria.
> Fonte atual: [README.md](../../AnimAI/README.md).
> O conteúdo abaixo foi preservado para consulta e não governa trabalho novo.

# AnimAI

AnimAI é o conjunto modular de autoria de animação por IA: criar, adaptar,
editar, inspecionar e publicar animações com controle por trecho, preservações
verificáveis e revisões recuperáveis. É externo ao motor; Unreal é uma
integração, Jogo01 é consumidor e Mecanifica continua independente.

Estado em 19/09/2026: contrato e plano definidos; implementação não iniciada.
Não há CLI, servidor ou skills AnimAI instalados por estes documentos.
O caminho `autoria-ia/` foi mantido para preservar links existentes.

## Escolha a entrada

| Intenção | Leitura inicial | Skill prevista |
| --- | --- | --- |
| Usar AnimAI para trabalhar em uma animação/personagem. | [Uso](docs/uso/README.md) | `animai-usar` |
| Desenvolver, corrigir ou ampliar o próprio AnimAI. | [Desenvolvimento](docs/desenvolvimento/README.md) | `animai-desenvolver` |
| Avaliar se temos as melhores ferramentas e abordagens. | [Contrato macro](docs/desenvolvimento/CONTRATO-MACRO.md) | `animai-desenvolver` |

“AnimAI” identifica este conjunto, não todo o plugin MCP_Unreal. Uma IA em
contexto novo precisa ter acesso a esta entrada ou às skills instaladas para
reconhecê-lo. O reconhecimento por nome será verificado na implementação.

## Fontes atuais

As [instruções para agentes](AGENTS.md) encaminham essas intenções. O
[protocolo de atualização](docs/desenvolvimento/ATUALIZACAO-E-HOOKS.md)
separa gatilhos documentais existentes de verificadores automáticos planejados.

O [contrato](CONTRATO.md) define garantias e fronteiras. O
[plano de implementação](planos/README.md) define sequência e progresso;
o [plano de documentação e skills](planos/DOCUMENTACAO-E-SKILLS.md) define
as duas trilhas, sua manutenção e testes. O
[estado do domínio de animação](animacao/README.md) encaminha aos estudos
históricos, sem transformá-los em instruções de uso.
