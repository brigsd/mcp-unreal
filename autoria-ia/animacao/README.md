> Cópia histórica desde 19/09/2026. O AnimAI agora tem raiz própria.
> Fonte atual: [docs/desenvolvimento/animacao/README.md](../../../AnimAI/docs/desenvolvimento/animacao/README.md).
> O conteúdo abaixo foi preservado para consulta e não governa trabalho novo.

# AnimAI — Animação

Oficina externa proposta para uma IA criar, editar, adaptar e revisar
animações por operações semânticas, sem dirigir manualmente um editor.
O núcleo independe de Unreal e Jogo01; a Unreal é destino de publicação e
conferência final.

Estado em 19/09/2026: arquitetura contratada, conjunto não implementado.
Não existem novos comandos ou skills instalados por esta pasta.

Comece pelo [índice AnimAI](../README.md), que separa uso e desenvolvimento.
Para desenvolver, o [contrato do conjunto modular](../CONTRATO.md) governa
as fronteiras entre núcleo, módulos e integrações, as operações para a IA,
a preservação do trabalho e os critérios de primeira entrega. Animação é
o primeiro domínio; Mecanifica continua independente e Jogo01 é consumidor.

O [plano de implementação](../planos/README.md), de 19/09/2026, detalha
seis etapas: base/revisões, edição, inspeção/intercâmbio, MCP/operação,
Unreal e geração opcional. Inclui interfaces compartilhadas, testes e
critérios de saída. Execução ainda não iniciada.

O [estudo de 17/09/2026](ESTUDO.md) detalha a proposta anterior de execução.
Sua seleção de Mink/MuJoCo com refinamento temporal próprio foi reaberta:
Momentum é o candidato prioritário de integração, com PyRoki/jaxls como
alternativa delimitada. Nenhum desses backends foi homologado nesta oficina.
Blender continua previsto para intercâmbio e inspeção, Kimodo para geração
opcional e Unreal para publicação. Editar um clipe não exige geração neural.

O [dossiê de 17/09/2026](EVIDENCIAS.md) conserva fontes, revisões auditadas
e riscos daquela rodada; não é inventário atualizado de todos os candidatos.
Em divergência, o contrato prevalece. Control Rig/Sequencer são opcionais.

As ferramentas MCP existentes mantêm sua organização. Perfis de personagem,
bibliotecas e receitas específicas pertencem ao workspace consumidor.

Não usar este estudo como autorização para instalar modelos, alterar assets,
migrar scripts ou substituir os contratos atuais dos projetos.
