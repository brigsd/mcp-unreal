> Cópia histórica desde 19/09/2026. O AnimAI agora tem raiz própria.
> Fonte atual: [docs/desenvolvimento/historico/EVIDENCIAS.md](../../../AnimAI/docs/desenvolvimento/historico/EVIDENCIAS.md).
> O conteúdo abaixo foi preservado para consulta e não governa trabalho novo.

# Evidências e decisões técnicas

Consulta em 17/09/2026. Complementa o [estudo daquela data](ESTUDO.md).
Nota de 19/09/2026: decisões vigentes são regidas pelo
[contrato do conjunto modular](../CONTRATO.md). Este dossiê conserva a
auditoria anterior e não cobre toda a pesquisa posterior; a seleção de
backend foi reaberta. Fontes datadas não comprovam homologação local.

A rodada examinou documentação, assinaturas e implementações. Não instalou
pacotes, carregou pesos, executou modelos ou abriu editores. Recomendações
são inferências de engenharia; desempenho anunciado não é medição local.

## Revisões examinadas

| Fonte | Revisão |
| --- | --- |
| MCP_Unreal | `7e3b09bbf6d2984c155233f9d3de5fcf523d2d42`, antes dos documentos desta tarefa |
| Unreal instalada | 5.8.2, changelist 56702186, conforme `Engine/Build/Build.version` |
| Mink | `ab45779fea46933832dee1c240f94103633347a1` |
| Kimodo oficial | `1aece8c124d73d255ceff5086d983b844c9f4e94` |
| ARDY oficial | `693f74d13b3d04a0a22ce127ee79c929dd89756b` |
| kimodo.cpp | `5679ff19ba0a522c0b0516e9a9d402fe1af2c027` |
| Motius | árvore `6d259de4672ff33c43a44d948fe8182f2c6eafb2` |
| PyMotion | `483abfefbc138e63c606cae5a87693bddaf1700e` |
| ozz-animation | `744eb9d99f606eda849acb0b1204f7a3dc20bca1` |

As demais páginas são as consultadas nesta data; não se presume imutabilidade
de `main`. Fixar revisões/licenças antes de incorporar código. Revisão de
pesquisa não significa versão homologada de runtime.

## Diagnóstico local

MCP_Unreal contém skills e hooks; APIs vêm de plugins Unreal. O catálogo
salvo no Jogo01 lista 72 operações de `SequencerControlRigTools`, sem provar
disponibilidade ao vivo.

O [script de guarda](C:/Users/micro/Desktop/Jogo01/Tools/preparar_previas_guarda.py)
preserva dedos, resolve mão/cotovelo e escreve trilhas via AnimSequence.
Entretanto, contém caminhos/coordenadas específicos, gera poses estáticas
e recusa nomes de propostas existentes. É evidência de operações úteis,
não um editor temporal reutilizável.

O [verificador](C:/Users/micro/Desktop/Jogo01/Tools/verificar_guarda_cutelo.py)
mantém critérios de lâmina horizontal, enquanto o
[estudo posterior](C:/Users/micro/Desktop/Jogo01/Docs/ESTUDO_GUARDA_CONTROL_RIG.md)
usa inclinações. Restrições artísticas precisam pertencer à receita, separadas
dos invariantes técnicos. Jogo01 e Mecanifica não foram alterados.

## Kimodo oficial

Selecionado como fornecedor generativo, não editor autoritativo. Usar
SOMA-RP v1.1, API com encoder injetado e pós-processamento habilitado.
A [assinatura real](https://github.com/nv-tlabs/kimodo/blob/1aece8c124d73d255ceff5086d983b844c9f4e94/kimodo/model/kimodo_model.py)
recebe `prompts`, `constraint_lst` e `post_processing`; o último é desabilitado
por padrão na API. Não copiar exemplos sem conferir a assinatura.

| Limitação concreta | Fonte primária | Tratamento escolhido |
| --- | --- | --- |
| SOMA77 não significa dedos gerados: a expansão começa com mãos relaxadas e sobrescreve 30 juntas. | [`to_SOMASkeleton77`](https://github.com/nv-tlabs/kimodo/blob/1aece8c124d73d255ceff5086d983b844c9f4e94/kimodo/skeleton/definitions.py) | Preservar/editar dedos no destino. |
| Condicionamento full-body não fixa por si só todas as rotações. | [`FullBodyConstraintSet`](https://github.com/nv-tlabs/kimodo/blob/1aece8c124d73d255ceff5086d983b844c9f4e94/kimodo/constraints.py) | Ativar corretor e medir após retarget. |
| Correção geométrica é uma etapa distinta da geração. | [`CorrectMotion`](https://github.com/nv-tlabs/kimodo/blob/1aece8c124d73d255ceff5086d983b844c9f4e94/MotionCorrection/src/cpp/AnimProcessing/Utility.cpp) | Registrar antes/depois, sem atribuir toda fidelidade ao modelo. |
| A leitura estática das máscaras de correção reconhece mãos/pés nomeados, mas não `end-effector` genérico. | [`_build_constraint_masks_dict`](https://github.com/nv-tlabs/kimodo/blob/1aece8c124d73d255ceff5086d983b844c9f4e94/kimodo/postprocess.py) | Usar tipos específicos; verificar equivalência em teste focal. Não é bug reproduzido nesta rodada. |
| Inicializa uma sequência nova; não oferece nossa transação de edição preservada sobre clipe-base. | [`_generate`/`__call__`](https://github.com/nv-tlabs/kimodo/blob/1aece8c124d73d255ceff5086d983b844c9f4e94/kimodo/model/kimodo_model.py) | Gerar proposta isolada e incorporar apenas janela/canais autorizados. |
| Condicionamento público por contatos dos pés não está implementado; não há compreensão geral de objetos. | [Constraints](https://github.com/nv-tlabs/kimodo/blob/1aece8c124d73d255ceff5086d983b844c9f4e94/docs/source/key_concepts/constraints.md), [model card](https://huggingface.co/nvidia/Kimodo-SOMA-RP-v1.1) | Converter contatos em alvos e resolver no destino. |
| Até dez segundos por prompt; recomenda menos de vinte frames restringidos por tipo, exceto trajetória densa da raiz. | [Limitações](https://github.com/nv-tlabs/kimodo/blob/1aece8c124d73d255ceff5086d983b844c9f4e94/docs/source/key_concepts/limitations.md) | Segmentar com fronteiras verificadas, sem travar densamente tudo. |
| Conversão de formatos não recebe rig genérico de destino. | [`convert_motion_files`](https://github.com/nv-tlabs/kimodo/blob/1aece8c124d73d255ceff5086d983b844c9f4e94/kimodo/exports/motion_convert_lib.py) | Retarget próprio com perfis. |
| NPZ/BVH diferem em repouso/unidade; SOMA77 expande quatro contatos para seis. | [BVH](https://github.com/nv-tlabs/kimodo/blob/1aece8c124d73d255ceff5086d983b844c9f4e94/kimodo/exports/bvh.py), [definições](https://github.com/nv-tlabs/kimodo/blob/1aece8c124d73d255ceff5086d983b844c9f4e94/kimodo/skeleton/definitions.py) | Validar shape, unidade e referência explicitamente. |

O [CachedTextEncoder](https://github.com/nv-tlabs/kimodo/blob/1aece8c124d73d255ceff5086d983b844c9f4e94/kimodo/demo/embedding_cache.py)
já guarda embeddings. Sua chave usa modelo, classe do encoder e texto;
fortalecer com revisões/configuração. A
[injeção em load_model](https://github.com/nv-tlabs/kimodo/blob/1aece8c124d73d255ceff5086d983b844c9f4e94/kimodo/model/load_model.py)
permite reutilizar isso sem interface gráfica. O encoder continua sendo
LLM2Vec/Llama 3, não qualquer embedding de outro LLM.

[MotionCorrection](https://github.com/nv-tlabs/kimodo/blob/1aece8c124d73d255ceff5086d983b844c9f4e94/MotionCorrection/python/motion_correction/motion_postprocess.py)
atua sem inferência textual. Seu [build](https://github.com/nv-tlabs/kimodo/blob/1aece8c124d73d255ceff5086d983b844c9f4e94/MotionCorrection/CMakeLists.txt)
usa C++, Eigen e pybind11. A fonte declara Apache-2.0; manter no worker
Kimodo, sem impor essa compilação ao núcleo. Pesos SOMA e encoder conservam
termos próprios. SMPL-X não foi selecionado.

## Mink e cinemática

[`solve_ik`](https://github.com/kevinzakka/mink/blob/ab45779fea46933832dee1c240f94103633347a1/src/mink/solve_ik.py)
retorna velocidade e pode falhar no QP. Integrar e reavaliar; escolher
`safety_break=True` para não continuar fora dos limites. O passo interno de
convergência não altera timestamps do clipe.

[DofFreezingTask](https://github.com/kevinzakka/mink/blob/ab45779fea46933832dee1c240f94103633347a1/src/mink/tasks/dof_freezing_task.py)
como tarefa comum é preferência; em `constraints`, trava aqueles graus de
liberdade. Inicializar cada frame com seus próprios canais-base preserva a
animação bloqueada, em vez de paralisá-la no tempo.

O mesmo caminho aceita tarefas com erro/Jacobiano, incluindo
[RelativeFrameTask](https://github.com/kevinzakka/mink/blob/ab45779fea46933832dee1c240f94103633347a1/src/mink/tasks/relative_frame_task.py).
Nas igualdades, o montador usa Jacobiano e ganho, não os pesos do objetivo:
selecionar explicitamente os componentes de uma relação parcial. A oficina
precisa distinguir empunhadura obrigatória de preferência estilística.

[ConfigurationLimit](https://github.com/kevinzakka/mink/blob/ab45779fea46933832dee1c240f94103633347a1/src/mink/limits/configuration_limit.py)
lineariza ball joints, podendo exceder o limite em passos grandes. Limites
de velocidade e verificação final são necessários. Anatomia por perfil e
continuidade temporal são desenvolvimento próprio. Mink não é autor de atuação
nem solver global de trajetórias.

O [pacote](https://github.com/kevinzakka/mink/blob/ab45779fea46933832dee1c240f94103633347a1/pyproject.toml)
declara MuJoCo e `qpsolvers[daqp]`, com configuração de builds Windows.
Isso sustenta a escolha CPU Windows; não substitui o teste de instalação.
Mink/MuJoCo: Apache-2.0; [DAQP](https://github.com/darnstrom/daqp/blob/master/LICENSE): MIT.

## Headless e Unreal

O worker Blender usa background, estado inicial limpo, job explícito e
saída não zero em erro Python, conforme a
[linha de comando](https://docs.blender.org/manual/en/4.5/advanced/command_line/arguments.html).
Headless não garante render sem GPU; selecionar Cycles CPU quando solicitado.

A avaliação usa frame da cena, depsgraph avaliado e `to_mesh`, liberando dados
temporários. O [bake oficial](https://github.com/blender/blender/blob/blender-v4.5-release/scripts/modules/bpy_extras/anim_utils.py)
avança frames e converte a transformação visual. Bake preserva o resultado
amostrado, não a lógica editável; fazê-lo em cópia de publicação. O
[exportador FBX](https://github.com/blender/blender/blob/blender-v4.5-release/scripts/addons_core/io_scene_fbx/__init__.py)
expõe leaf bones, actions e simplificação; opções ficam fixadas no adaptador.

A [especificação glTF](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html)
representa skin/animação, mas não semântica de sockets/ABP. Consumidores podem
limitar conjuntos de pesos. O manifesto preserva identidade e avisos de perda.

Leitura do código instalado confirmou:

| Fonte local | Evidência e consequência |
| --- | --- |
| [AnimDataController.cpp](<C:/Program Files/Epic Games/UE_5.8/Engine/Source/Developer/AnimationDataController/Private/AnimDataController.cpp:1358>) | Arrays de posição/rotação/escala coerentes e trilha existente são exigidos; retornos falsos precisam de tratamento. `AddBoneCurve` é a operação atual. |
| [SkeletalMesh.h](<C:/Program Files/Epic Games/UE_5.8/Engine/Source/Runtime/Engine/Classes/Engine/SkeletalMesh.h:538>) | `GetMeshDescription`, `GetRefSkeleton` e atributos de skin permitem extração. LOD gerado pode não ter MeshDescription; registrar LOD-fonte e sockets efetivos. |
| [ControlRigSequencerEditorLibrary.cpp](<C:/Program Files/Epic Games/UE_5.8/Engine/Plugins/Animation/ControlRig/Source/ControlRigEditor/Private/ControlRigSequencerEditorLibrary.cpp:1167>) | Uma exportação exige Sequencer aberto; outras rotas possuem contexto alternativo. Não generalizar compatibilidade headless a toda API. |
| [SkinnedMeshComponent.cpp](<C:/Program Files/Epic Games/UE_5.8/Engine/Source/Runtime/Engine/Private/Components/SkinnedMeshComponent.cpp:4965>) | `GetCPUSkinnedVertices` depende de MeshObject/estado de render. NullRHI não garante deformação final completa. |

Os links locais dependem desta instalação. A
[Epic](https://dev.epicgames.com/documentation/unreal-engine/scripting-the-unreal-editor-using-python)
separa commandlet de editor completo e restringe Python ao contexto de editor.
Não executamos o publicador nem NullRHI nesta análise.

## Alternativas de geração e edição

| Candidato | Decisão | Fundamento concreto |
| --- | --- | --- |
| CondMDI | Referência de máscaras/inbetweening; não adicionar checkpoint. | O [script](https://github.com/setarehc/diffusion-motion-inbetweening/blob/main/sample/conditional_synthesis.py) exige HumanML/raiz absoluta, usa 20 fps/196 frames e separa condicionamento de reposição explícita. Não é editor do nosso skeleton. |
| MotionFix/TMED | Inspiração para edição relativa; excluir como editor central. | O [inpainting](https://github.com/atnikos/motionfix/blob/main/src/model/tmed_denoiser.py) repete máscara corporal no tempo. Janela arbitrária com preservação rigorosa requer adaptação. |
| MotionLab | Inspiração para movimento + condição → movimento; excluir dependência direta. | O [README](https://github.com/Diouo/MotionLab/blob/main/README.md) recomenda versão anterior para reprodução e retreino após correções; o [laço](https://github.com/Diouo/MotionLab/blob/main/rfmotion/models/modeltype/rfmotion.py) não oferece nossa transação preservada. |
| kimodo.cpp | Adiar substituição do original. | O [README auditado](https://github.com/localai-org/kimodo.cpp/blob/5679ff19ba0a522c0b0516e9a9d402fe1af2c027/README.md) lista constraints gerais, SOMA77 e quantização do denoiser ausentes. O encoder já tem quantização: a conclusão anterior genérica estava desatualizada. |
| ARDY | Reservar para eventual geração interativa em execução. | A [API](https://github.com/nv-tlabs/ardy/blob/693f74d13b3d04a0a22ce127ee79c929dd89756b/ardy/model/ardy_model.py) tem histórico, máscaras e embeddings. Não é um gerador sem controle. |
| motion-bricks.cpp | Fora da primeira oficina de autoria. | A [interface](https://github.com/localai-org/motion-bricks.cpp) usa G1 e replanejamento. O benchmark SONIC não mede todo o pipeline de animação. |
| skin-tokens.cpp | Preparação de personagens, não edição de movimentos. | O [modo skin](https://github.com/localai-org/skin-tokens.cpp) aceita esqueleto existente; pesos de deformação não são criação de atuação. |

Licenças também afetam incorporação.
[CondMDI](https://github.com/setarehc/diffusion-motion-inbetweening/blob/main/LICENSE)
declara MIT para código; pesos não ficaram suficientemente esclarecidos nas
fontes consultadas. MotionFix tem [LICENSE MIT](https://github.com/atnikos/motionfix/blob/main/LICENSE),
mas [README](https://github.com/atnikos/motionfix#license) diz pesquisa não
comercial: esclarecer a divergência antes de copiar. MotionLab não apresentou
licença geral explícita na árvore consultada. São pendências de autorização
de reutilização, não proibição de estudar as abordagens.

Datasets permanecem separados: [AMASS](https://amass.is.tue.mpg.de/license.html)
tem restrições próprias; os textos/metadados de
[MotionFix](https://motionfix.is.tue.mpg.de/license.html) não comprovam
relicenciamento de movimentos de terceiros. Nosso editor não exige baixar
esses datasets para editar clipes do usuário.

## Infraestrutura e exclusões adicionais

[Motius](https://github.com/ZeyuLing/Motius) é referência de organização. Seu
[pyproject](https://github.com/ZeyuLing/Motius/blob/main/pyproject.toml) instala
Torch, Diffusers, Transformers, PEFT e outros na base. A
[exportação](https://github.com/ZeyuLing/Motius/blob/main/docs/motion/fbx.md)
passa por SMPL-22, corpo licenciado e backend FBX. Isso não atende nosso núcleo
leve nem preservação universal. Na árvore completa `6d259de...`, faltava
licença geral na raiz e a metadata GitHub estava vazia; licenças de subpastas
não autorizam automaticamente o pacote inteiro.

Nas [métricas](https://github.com/ZeyuLing/Motius/blob/main/docs/evaluation/physical_metrics.md),
estimar piso pelo mínimo dos pés torna penetração quase degenerada. Nossa
avaliação usa a cena e não minimiza velocidade corporal como sinônimo de
qualidade.

[PyMotion](https://github.com/UPC-ViRVIG/pymotion) oferece FK, rotações e BVH;
o módulo IK consta como trabalho futuro. Pode fornecer operações pontuais MIT,
não substitui Mink. Sua convenção WXYZ deve ser convertida explicitamente.

[ozz-animation](https://github.com/guillaumeblanc/ozz-animation) atende playback
e runtime C++. O [IK de dois ossos](https://github.com/guillaumeblanc/ozz-animation/blob/744eb9d99f606eda849acb0b1204f7a3dc20bca1/include/ozz/animation/runtime/ik_two_bone_job.h)
documenta flip com alinhamento de alvo/pole. Não justifica introduzir outro
runtime para resolver autoria com contatos.

[Pink](https://github.com/stephane-caron/pink) é outra solução diferencial,
com Pinocchio/QP. Mink foi escolhido pela composição de tarefas relativas,
igualdades e geometria de colisão na base MuJoCo, não por benchmark de
velocidade que não fizemos.

[Cascadeur](https://cascadeur.com/plans) fica fora da base gratuita: o Free
consultado limita exportação a CASC e uso não comercial.
[Mixamo](https://helpx.adobe.com/creative-cloud/faq/mixamo-faq.html) e
[Game Animation Sample](https://dev.epicgames.com/documentation/unreal-engine/game-animation-sample-project-in-unreal-engine)
podem alimentar o catálogo sob seus termos. Não são serviços obrigatórios
nem garantem cobertura de todas as ações de combate.

## Limite das conclusões

Não há medição nova de qualidade, velocidade ou memória dos executores.
A composição foi escolhida por capacidades, interfaces, restrições e custo
de integração identificáveis. As provas curtas verificam a implementação
dessas fronteiras; não reabrem indefinidamente a seleção de ferramentas.
