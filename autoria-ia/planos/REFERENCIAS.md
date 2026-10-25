> Cópia histórica desde 19/09/2026. O AnimAI agora tem raiz própria.
> Fonte atual: [docs/desenvolvimento/decisoes/BASE-TECNICA.md](../../../AnimAI/docs/desenvolvimento/decisoes/BASE-TECNICA.md).
> O conteúdo abaixo foi preservado para consulta e não governa trabalho novo.

# Referências técnicas do plano

Consulta focal em 19/09/2026. Este registro verifica fronteiras necessárias
ao planejamento, sem nova rodada ampla de candidatos e sem instalar ou executar
dependências. Os testes dos planos ainda precisam comprovar a integração local.

## Momentum

A documentação de `solver2` expõe resolução de sequências e termos temporais;
`set_enabled_parameters` aplica a mesma máscara a todos os frames. Por isso o
plano exige recortes, recomposição e validação, sem prometer travamento temporal
arbitrário fornecido pela biblioteca. Termos de custo de colisão não são prova
de cumprimento de uma obrigação. [API solver2](https://facebookresearch.github.io/momentum/python_api_doc/solver2.html).

O README atual separa núcleo NumPy/nativo e complementos Torch, recomenda
Conda/Pixi e classifica o caminho PyPI como experimental. A escolha é worker
isolado com binário, versão e símbolos conferidos; não uma dependência pesada
importada pela descoberta. A compatibilidade anunciada não é homologação
na máquina do usuário. [Instalação oficial](https://github.com/facebookresearch/momentum#installation).

A revisão anteriormente auditada foi
`6487aa6795a13a222424d7e5087672e0a34f08a3`. Seu teste `test_sequence_ik.py` usa
a interface diferenciável/Torch; não é prova direta do worker NumPy `solver2`
escolhido agora. O plano cria prova própria da fronteira usada.
[Teste nessa revisão](https://github.com/facebookresearch/momentum/blob/6487aa6795a13a222424d7e5087672e0a34f08a3/pymomentum/test/test_sequence_ik.py).

## SDK MCP

A documentação oficial consultada identifica v2 como linha estável, com
`MCPServer` em `mcp.server` e `Client` em `mcp`. O plano usa esse SDK como
dependência opcional e transporta os mesmos serviços por stdio. Não copiar
exemplos antigos de FastMCP v1 para uma instalação não fixada.
[Entrada oficial](https://py.sdk.modelcontextprotocol.io/),
[primeiros passos](https://py.sdk.modelcontextprotocol.io/get-started/first-steps/),
[testes](https://py.sdk.modelcontextprotocol.io/get-started/testing/).

## Blender, Unreal e Kimodo

Os detalhes previamente auditados de avaliação de malha, formatos e Unreal
permanecem no [dossiê de 17/09](../animacao/EVIDENCIAS.md). A página do manual
Blender não pôde ser relida pela ferramenta web nesta rodada; flags e APIs
serão conferidas no `--help`/versão do executável escolhido em B1 antes de
homologar o worker. Não instalar uma versão diferente automaticamente.

Leitura local nesta rodada confirmou Unreal 5.8.2, changelist 56702186, no
arquivo `C:\Program Files\Epic Games\UE_5.8\Engine\Build\Build.version`.
O script existente `C:\Users\micro\Desktop\Jogo01\Tools\preparar_previas_guarda.py`
usa `set_frame_rate`, `add_bone_curve` e `set_bone_track_keys`. Isso sustenta
uma rota de escrita, mas não comprova fidelidade de exportação, sequência
longa, metadados ou contexto de jogo. E5 testa esses pontos separadamente.

Kimodo permanece integração opcional pelo repositório oficial. Cache textual,
pós-processamento, representação SOMA e limitações de dedos precisam entrar
no manifesto do adaptador. O acesso a código não decide os direitos de pesos
e fontes. [Repositório oficial](https://github.com/nv-tlabs/kimodo) e
[auditoria anterior](../animacao/EVIDENCIAS.md#kimodo-oficial).

## Regra de atualização

Este registro é uma consulta focal, não uma certificação macro de “melhores
ferramentas”. Para essa pergunta, seguir o
[contrato macro](../docs/desenvolvimento/CONTRATO-MACRO.md) e os
[gatilhos de atualização](../docs/desenvolvimento/ATUALIZACAO-E-HOOKS.md).
Esta revisão documental não renova a data das pesquisas acima.

Na instalação de cada adaptador, registrar pacote/build ou commit exato,
licenças e hash, ambiente resolvido e resultado dos testes locais. Atualização
de dependência invalida o recibo afetado e executa novamente seus gates.
Uma mudança em `main` não atualiza automaticamente a oficina do usuário.
