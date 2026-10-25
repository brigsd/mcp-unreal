> Cópia histórica desde 19/09/2026. O AnimAI agora tem raiz própria.
> Fonte atual: [docs/desenvolvimento/historico/ESTUDO.md](../../../AnimAI/docs/desenvolvimento/historico/ESTUDO.md).
> O conteúdo abaixo foi preservado para consulta e não governa trabalho novo.

# Autoria IA de animações — estudo de 17/09/2026

Nota de 19/09/2026: o [contrato do conjunto modular](../CONTRATO.md) passa
a governar a arquitetura. Este estudo conserva os detalhes e fundamentos
da proposta de 17/09; suas escolhas técnicas não são decisão final vigente.
Em particular, a seleção de Mink/MuJoCo com refinamento temporal próprio
foi reaberta em favor de avaliar primeiro a integração com Momentum, tendo
PyRoki/jaxls como alternativa delimitada. Nenhum backend foi homologado.

Revisão de 17/09/2026. Substitui a recomendação anterior centrada na Unreal.
Arquitetura escolhida nesta análise; executores ainda não implementados nem
homologados. Auditoria de código e alternativas: [EVIDENCIAS.md](EVIDENCIAS.md).

## 1. Decisão

Construir uma oficina externa de animação, controlável por dados e executável
sem interface. Seu núcleo mantém personagens, movimentos, intenções,
restrições, versões e avaliações. A Unreal será um destino e um avaliador de
integração; fechar o editor não deve impedir criar ou corrigir animações.

O conjunto escolhido é Python/NumPy/SciPy para autoria e dados; Mink/MuJoCo
para cinemática e restrições; Blender em processo separado para intercâmbio,
malha deformada e imagens; Kimodo oficial como fornecedor de movimento
neural; e um adaptador Unreal para importar, amostrar e conferir o resultado.
Geradores são dispensáveis para editar uma animação já existente.

Nosso desenvolvimento concentra-se no compilador de intenção em operações,
contrato de personagem, retarget, correções temporais, inspeção e execução
incremental. Não proponho treinar um modelo fundacional, construir outro
editor manual ou instalar uma coleção de modelos concorrentes.

O requisito de produto é conseguir pedir “mantenha a empunhadura, afaste a
mão do rosto nesse trecho e preserve a recuperação do golpe”, receber uma
versão comparável e corrigir novamente sem reconstruir o trabalho.

### O que já podemos decidir e o que precisa de teste

Documentação e código permitem fechar a arquitetura e excluir candidatos
agora. Não precisamos instalar todos para descobrir se oferecem keyframes,
se omitem dedos ou se exigem um editor aberto.

Precisamos de testes curtos dos componentes escolhidos durante a construção.
Eles verificam conversões, preservação, colisões, persistência e integração.
Código disponível não comprova que nosso adaptador está correto, que o solver
converge naquele personagem ou que o movimento parece bom. A seção 11 define
essas provas. Não haverá benchmark aberto de todos os modelos nem bloqueio
de toda a oficina por um gerador.

## 2. Conjunto de ferramentas

| Componente | Responsabilidade escolhida | Limite explícito |
| --- | --- | --- |
| Python + NumPy/SciPy | Receitas, composição, rotações, tempo, catálogo, versões, correção temporal e relatórios. | Interpolação matemática não produz atuação convincente sozinha. |
| Mink + MuJoCo + DAQP | Resolver alvos corporais, preservar graus de liberdade e evitar colisões de aproximações geométricas. | IK local; não garante solução global, anatomia ou dinâmica física. |
| Blender headless | Importar fontes, avaliar malha/armature, exportar GLB/FBX e renderizar inspeções. | Não reproduz automaticamente deformadores e lógica exclusivos da Unreal. |
| Kimodo oficial, SOMA-RP v1.1 | Gerar bases condicionadas por texto e controles cinemáticos. | Esqueleto próprio, dependências neurais e detalhes incompletos; requer retarget e correção. |
| Adaptador Unreal | Registrar personagem, escrever AnimSequence e conferir reprodução no jogo. | Exige instalação/projeto de editor; escrita será serializada. |
| Biblioteca local curada | Bases, poses de mãos, contatos e receitas de ações reutilizáveis. | Cada item registra origem, direitos de uso e compatibilidade. |

Mink separa objetivos ponderados de restrições de igualdade no
[código de resolução IK](https://github.com/kevinzakka/mink/blob/ab45779fea46933832dee1c240f94103633347a1/src/mink/solve_ik.py).
MuJoCo permite executar etapas de cinemática sem avançar uma simulação
física. Usá-lo aqui não exige treinamento de políticas nem adicionar um robô
ao jogo. [Funcionamento do MuJoCo](https://mujoco.readthedocs.io/en/stable/overview.html).

Blender fica em processo próprio. O Python da Unreal não carregará PyTorch,
Mink ou dependências do Blender. O formato persistido também não dependerá
de objetos Python específicos desses programas.

## 3. Arquitetura e fluxo

```text
Pedido da IA + personagem + fonte + restrições
                    |
          compilador de receita
                    |
       movimentos e versões próprios
          /         |          \
 biblioteca      Kimodo      operações diretas
          \         |          /
        retarget + correção no personagem final
                    |
     métricas + malha + imagens A/B + diagnóstico
                    |
       patch localizado sobre uma revisão
                    |
      publicação Unreal / GLB / FBX
```

Uma API interna única sustenta CLI com entrada/saída JSON e uma fachada MCP
fina. A fachada oferece operações de autoria; as MCP tools atuais da Unreal
continuam organizadas como estão. Não haverá implementações divergentes por
porta de acesso.

Cada tarefa registra dependências. Alterar um alvo invalida apenas resolução
do trecho, avaliações afetadas e imagens. Não invalida o embedding textual,
não baixa o modelo novamente e não refaz importações ainda válidas.

O consumidor fornece seu perfil. Caminhos `/Game/Weapons`, nomes de Quinn,
sockets de cutelo e convenções particulares do Jogo01 não entram no núcleo.
Jogo01 será um consumidor e caso de integração. Um personagem sintético
assimétrico comprovará que o módulo funciona sem ele.

## 4. Fonte de verdade e preservação

### Pacote de personagem e cena

O pacote contém hierarquia completa, identidades estáveis dos ossos,
transformações de repouso, malha, pesos, âncoras semânticas e perfil cinemático.
O perfil relaciona mão, palma, dedos, cotovelo, planta do pé e cabeça ao rig
real. Registra limites, articulações derivadas, twist bones e capacidades
que só o destino consegue avaliar.

A cena contém piso e objetos relevantes, escala, posições e contatos. Uma
arma recebe âncoras de empunhadura. Mão–arma é uma relação persistida, não
uma coleção de coordenadas que a IA precisa repetir a cada tentativa.

O registro extrai dados disponíveis e propõe mapeamentos com confiança.
Ambiguidades e limites anatômicos ausentes exigem calibração explícita, uma
vez por perfil. Não inventar limites pelo nome do osso nem prometer zero
configuração para qualquer criatura. O primeiro domínio é humanoide com
esqueleto e skin existentes; animais, faces e rigging de malha estática não
são capacidades implícitas dessa primeira entrega.

Perfis conhecidos são reutilizados por assinatura de hierarquia/repouso;
nomes semelhantes não bastam. O registro produz poses diagnósticas automáticas
de flexão, palma e apoio para conferir os eixos. A IA recebe apenas as
ambiguidades restantes, não uma ficha inteira para preencher manualmente.
Revisar malha ou rig invalida as calibrações afetadas, não todo o catálogo.

### Movimento neutro

Adotar manifesto JSON versionado e arrays numéricos carregados sem pickle.
O contrato usa metros, segundos, base destra, Y vertical, frente +Z e
quaternions XYZW normalizados. Adaptadores convertem ordens e convenções
explicitamente. FPS é racional `n/d`. Um clipe com N amostras tem tempos
`t[i] = i*d/n`, de zero a `(N-1)*d/n`; a última amostra é incluída, não um
frame extra de duração. Pose estática é tipo próprio. A publicação adapta
amostras/intervalos às APIs do destino sem alterar a duração.

Janelas de patch usam índices `[início, fim)`, com margens de transição
incluídas na autorização. Eventos/contatos são expressos em segundos;
retiming aplica o mesmo mapa temporal monotônico a movimento e metadados.
Loop registra período e política da amostra de fechamento explicitamente.

Guardar transformações locais completas por osso, trajetória da raiz, curvas
e eventos. Repouso e pose animada são campos distintos. Matrizes de bind e
pesos pertencem ao personagem; não são reestimados a cada geração. A base
geométrica é convertida por matrizes, sem inversão arbitrária de componentes
de quaternion. Transformações não representáveis, como certos casos de shear,
precisam de diagnóstico, não de descarte silencioso.

Preservar o esqueleto do personagem. SOMA-30, SMPL-22 e G1 são representações
de fornecedores, não nosso formato universal. O solver pode trabalhar num
subconjunto, mas o resultado recompõe todos os canais intocados. GLB serve
ao intercâmbio e à prévia; não substitui receita, contatos ou evidências.

### Revisões e camadas

Revisões imutáveis apontam para fonte, operações ordenadas, parâmetros,
restrições e resultado materializado. Patches exigem revisão-base; conflito
concorrente é recusado. Undo seleciona uma revisão anterior. A composição
parte das fontes e camadas persistidas, evitando acumular arredondamentos de
exports sucessivos. Preservar a amostra original significa preservar seu
movimento ao longo do tempo, não congelar o membro no primeiro frame.

“Preservar mão” deve especificar: rotações locais dos dedos, palma no mundo
ou transformação relativa à arma. São contratos diferentes. Uma pose local
intacta pode mover-se no mundo quando o ombro se move.

Uma revisão pode estar tecnicamente válida, visualmente revisada ou aprovada
para uso. Alterações invalidam aprovações dependentes. Código zero do processo,
sozinho, não aprova um movimento. Inferência neural guarda também o resultado
concreto: mesma seed não garante identidade entre hardwares.

## 5. Criação, retarget e edição

### Fonte e intenção

O planejador reutiliza uma base compatível quando existir, usa operações
diretas para ajustes localizados e chama Kimodo para ações novas ou transições
corporais mais ricas. A decisão é registrada e pode ser fixada na receita.
Uma correção de cotovelo não passa pelo encoder ou pelo gerador.

O catálogo indexa ação, fase, duração, apoios, mão dominante, objetos,
esqueleto e permissões. Receitas de ação descrevem preparação, execução e
recuperação com marcos temporais. Alcance, guarda, empunhadura, golpe, giro
e agachamento são vocabulário útil: parâmetros e restrições explícitos,
sem supor compreensão perfeita desses nomes pelo modelo.

Para geração selecionamos a API oficial Kimodo com pós-processamento
explicitamente habilitado e encoder com cache injetado. A CLI não conecta
esse cache automaticamente. Reaproveitar MotionCorrection antes do retarget
para corrigir o movimento nativo, mantendo as correções finais no personagem.
O código confirma expansão de 30 para 77 juntas a partir de mãos relaxadas;
portanto dedos e empunhaduras continuam sob responsabilidade da oficina.
[API e limites auditados](EVIDENCIAS.md#kimodo-oficial).

Regeneração neural produz uma proposta separada para a janela autorizada,
com poses de fronteira e contexto. Copiar somente os canais permitidos e
resolver as bordas. Não reenviar uma animação inteira esperando que o modelo
preserve tudo por instrução textual. Fixar frames isolados também não garante
continuidade de velocidade; isso será medido.

### Retarget para o personagem final

Converter coordenadas; relacionar cadeias e bases de repouso; transferir
orientação e trajetória com escala declarada; resolver alvos no destino.
A calibração estabelece frame da palma, flexão e distribuição de twist.
Posições de juntas não determinam unicamente torção: quando a fonte não
contém orientação suficiente, usar prior explícito e registrar a perda.

Dados ausentes na fonte vêm da base aprovada ou de receita específica.
Dedos não são zerados ao importar movimento corporal. Raiz de locomoção e
pelve são distintas. In-place, remoção de deslocamento e mudança de escala
são operações explícitas. O retarget também converte restrições do destino
para o fornecedor quando a geração precisa ser condicionada por elas.

### Resolução geométrica

Gerar automaticamente uma articulação cinemática MuJoCo a partir do perfil,
com correspondência rastreável aos ossos. Não trocar o esqueleto de deformação.
Usar Mink para alvos de posição/orientação, relações e limites. Canais
protegidos recebem a amostra-base em cada frame e não participam da mudança.

O primeiro backend resolve hierarquias rígidas: raiz livre, rotações locais
e offsets constantes, com escala de unidade incorporada na calibração.
Translação animada não-raiz, escala animada/não uniforme e ossos derivados
exigem representação explícita e paridade de cinemática direta com o pacote.
Sem essa paridade, o canal permanece armazenado, mas a cadeia dependente
não é habilitada para IK. Não basta recolocar um canal depois se ele altera
a geometria que o solver usou. Regras de twist derivado são aplicadas antes
da avaliação final e também testadas contra a referência.

O [congelamento de graus de liberdade](https://github.com/kevinzakka/mink/blob/ab45779fea46933832dee1c240f94103633347a1/src/mink/tasks/dof_freezing_task.py)
será imposto como igualdade; alvos relativos usam
[RelativeFrameTask](https://github.com/kevinzakka/mink/blob/ab45779fea46933832dee1c240f94103633347a1/src/mink/tasks/relative_frame_task.py).
Empunhaduras obrigatórias entram em `constraints`, não apenas em `tasks` com
peso alto. Relações parciais usam apenas as linhas do Jacobiano exigidas;
zerar um peso não remove uma linha de igualdade. Alvos estilísticos ficam
nos objetivos ponderados. O compilador detecta duplicações/conflitos e não
transforma uma falha de igualdade em preferência silenciosamente.
Cada solução tem limite de passo, iteração e tempo, e validação da pose real.
Igualdade no problema linearizado não prova erro zero na cinemática não
linear: iterar e medir é parte do executor.

Desenvolveremos máscaras por região/tempo, compilador de perfis, prioridades,
continuidade temporal e diagnóstico. Ombros exigem limites por direção;
o [ConfigurationLimit](https://github.com/kevinzakka/mink/blob/ab45779fea46933832dee1c240f94103633347a1/src/mink/limits/configuration_limit.py)
usa aproximação de primeira ordem para ball joints. Acrescentar limites de
swing/twist por perfil e verificar depois de integrar. Não tratar esse solver
como solução anatômica pronta para qualquer rig.

Iniciar da fonte e dos frames vizinhos, preservar postura como objetivo e
corrigir uma janela limitada, com margens de transição autorizadas. Refinar
a trajetória de correções com NumPy/SciPy; reprojetar contatos e revalidar.
Não aplicar suavização final que volte a soltar o pé. A estrutura esparsa de
[SciPy least_squares](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.least_squares.html)
serve ao refinamento local; ela não implementa igualdade geral. Travamentos
permanecem fora das variáveis ou na projeção cinemática.

A última projeção é seguida de validação conjunta de contatos, preservações,
velocidade e aceleração do clipe. Medir em segundos, inclusive nas duas
fronteiras da janela, com limites por fase/perfil. O passo interno do IK não
é a velocidade entre frames. Descontinuidades já presentes na fonte são
registradas; editar não pode introduzir novas nos canais protegidos. Uma
janela incapaz de satisfazer tudo é rejeitada, sem suavização oculta fora dela.

Restrições obrigatórias não são relaxadas silenciosamente. Estilo pode ceder
conforme prioridades. Em falha, retornar resíduos e envolvidos, com alternativas
permitidas. Falha de convergência local não demonstra impossibilidade global.
Tampouco aceitaremos stretch de ossos para esconder um alvo inalcançável.

### Contatos, colisão e deformação

O grafo distingue apoio, empunhadura, toque e regiões proibidas, com intervalos
e tolerâncias. Apoio detectado é hipótese registrada: saltos e chutes não
podem ser corrigidos prendendo todos os pés ao piso.

A [evitação de colisão do Mink](https://github.com/kevinzakka/mink/blob/ab45779fea46933832dee1c240f94103633347a1/src/mink/limits/collision_avoidance_limit.py)
usa pares de geometrias configurados. Cápsulas orientam a resolução, mas não
comprovam ausência de interpenetração da pele. A inspeção secundária usa a
malha deformada nos trechos relevantes e distingue contato permitido de
interseção proibida. Amostrar também entre frames em regiões de movimento
rápido; verificar só keyframes não garante colisão contínua ausente.

Se a pele do cotovelo continuar ruim com cinemática correta, apontar pesos ou
corretivos como causa candidata. Não reponderar a malha ou trocar o rig como
consequência automática de editar uma animação.

## 6. Operações e retorno para a IA

Contratos propostos, ainda não comandos disponíveis:

| Operação | Entrada e retorno |
| --- | --- |
| `autoria.describe` | Capacidades reais, ambientes, perfis e limites, sem carregar modelos. |
| `actor.register` | Fonte → pacote de personagem, mapa e diagnóstico de calibração. |
| `motion.build` | Intenção/receita/fonte → candidatos, métricas e prévias versionados. |
| `motion.patch` | Revisão + trecho + operações + preservações → edição localizada, diff e avaliação. |
| `motion.inspect` | Revisão e foco → medidas, frames relevantes, imagens e A/B sincronizado. |
| `motion.publish` | Revisão validada + destino → export e relatório de ida e volta. |
| `job.control` | Estado, cancelamento, retomada e liberação de recursos. |

Patches combinam operações tipadas: alvo de membro, pose dos dedos, contato,
trajetória, tempo, espelhamento, transição, composição por região e root motion.
Operações declaram efeitos e dependências. O serviço executa o lote; a IA
não precisa dirigir centenas de chamadas de baixo nível.

Exemplo: revisão 7, mão esquerda, intervalo 0,6–1,2 s, distância mínima de
4 cm da superfície do rosto, preservar empunhadura direita e frames externos,
permitir compensação da clavícula esquerda. A revisão 8 devolve o que mudou,
o que permaneceu e o que ainda falha. A distância refere-se à superfície ou
âncora declarada, não à origem arbitrária de um osso.

Retorno curto: revisão, estado, duração, violações obrigatórias e artefatos.
Cada problema contém tipo, intervalo, partes, medida, tolerância, confiança e
operações corretivas possíveis. Logs completos ficam acessíveis por referência.
O diagnóstico precisa orientar a próxima edição, não apenas anunciar falha.

## 7. Inspeção e iteração sem manipulação manual

Gerar automaticamente frente, perfil, três quartos, detalhe de mãos e câmera
da ação. A/B usa mesmos frames, câmera, malha e iluminação. Mostrar apoios,
trajetória e piores erros. Detalhes não podem esconder equilíbrio corporal.

Blender avalia e renderiza em background por receita, produzindo imagens,
folha de contato e vídeo curto. GLB pode alimentar visor leve com seleção de
frame; a IA consegue solicitar outra vista, medir e corrigir sem clicar.
Versão de Blender e opções de avaliação/exportação são fixadas por ambiente.
Uma sessão de render pode processar um lote; não iniciar um programa para
cada frame.

Distinguir esqueleto, aproximação externa e resultado do motor. Corretivos
exclusivos da Unreal exigem evidência no alvo; a prévia externa não a substitui.
Solicitar essa conferência nas fronteiras relevantes, não em todo ajuste.

A crítica visual escolhe região e intenção; operações mensuráveis executam a
correção. Aprovação numérica não significa atuação convincente. A IA pode
iterar automaticamente dentro de limites de candidatos, tentativas, tempo e
magnitude. Sem melhoria, retornar diagnóstico em vez de prompts aleatórios
ilimitados. Alterações fora da região autorizada exigem ampliar a receita,
não ampliar silenciosamente a liberdade do solver.

Orçamento inicial: até dois candidatos e três correções geométricas por
candidato; timeout por etapa. Só promover quando cumprir as restrições
obrigatórias e melhorar o critério declarado sem regressão protegida. Caso
contrário, manter a revisão-base. Aumentar orçamento é decisão explícita,
não uma escalada automática para outro modelo ou outra GPU.

Metas de usabilidade, ainda não medidas: correção regional de clipe até
4 s/30 fps em até 5 s com processos iniciados; folha de inspeção simples em
até 15 s nas mesmas condições. Inicialização, geração neural e publicação
são medidas separadamente. São metas para orientar implementação, não
benchmarks já obtidos ou garantias do hardware.

## 8. Processos, recursos e recuperação

Coordenador e solver rodam no Windows em ambiente Python separado. Blender
é worker externo; Kimodo fica em Linux/WSL isolado. Unreal usa o Python do
editor. Manifestos e arrays cruzam essas fronteiras, não objetos específicos
de cada ambiente. O núcleo funciona sem Torch, WSL, Blender ou Unreal
carregados para operações puramente numéricas.

A instalação futura automatiza versões, pré-requisitos e verificação de
artefatos. Pacotes externos e modelos ficam fora do Git. Consultar o catálogo
não dispara downloads. Dependências ficam travadas por ambiente; código de
modelos executa apenas de versões previamente confiadas, sem execução remota
arbitrária de um checkpoint. Nenhum asset privado é enviado a serviços externos
por padrão.

Inventário somente leitura desta rodada: RTX 5070 com 12.227 MiB reportados,
RTX 2080 Ti com 11.264 MiB, cerca de 31,8 GiB de RAM e Unreal 5.8 instalada.
Não é benchmark. UUIDs e caminhos pertencem à configuração local, fora de
receitas portáveis.

Escolha inicial: geração na 5070; encoder textual na CPU em cache miss, com
residência limitada; 2080 Ti disponível para render opcional. Evita depender
de quantização para a primeira integração. O teste do fornecedor verifica
compatibilidade CUDA/PyTorch com essa GPU e uso real de memória. Memória livre,
não só total, decide se a carga pode iniciar. Com RAM insuficiente, a tarefa
aguarda/libera cargas próprias e explica o motivo; não entra em paginação
ilimitada nem encerra aplicativos do usuário.

O worker textual materializa os embeddings e encerra sua residência antes
de iniciar etapas pesadas de geração/render/publicação. Requisições do mesmo
lote compartilham essa passagem. Ao terminar a geração, o modelo também pode
ser descarregado; editar e inspecionar continuam usando o clipe salvo. Esse
escalonamento é obrigatório com pouca RAM, não um ajuste manual por sessão.

Reaproveitar o [cache textual existente](https://github.com/nv-tlabs/kimodo/blob/1aece8c124d73d255ceff5086d983b844c9f4e94/kimodo/demo/embedding_cache.py)
por encoder injetado na API e fortalecer sua chave: texto normalizado, pesos,
adaptadores, tokenizer, revisões, configuração e precisão. Embeddings
incompatíveis não são reutilizados. Fontes neurais geradas ficam persistidas
para reedição offline. Desligar o computador perde processos, não esse acervo.

Usar reserva exclusiva por GPU estável, fila, limites de CPU e política de
uso configurável. Sem fallback silencioso de duas cargas para a mesma placa.
Pausar/liberar vale só para processos iniciados pela oficina.

Diário de jobs em SQLite; artefatos endereçados por hash. Estados: aguardando,
executando, validando, pronta, falhou e cancelada. A saída só vira revisão
utilizável após escrita completa e validação. Reinício reaproveita etapas
concluídas; cancelamento registra o último resultado íntegro. Atualizações
são atômicas na fronteira de arquivos, não uma promessa de transação entre
três programas. Escritas no destino têm diário próprio e reconciliação.

## 9. Integração Unreal sem torná-la centro da autoria

Na entrada, extrair esqueleto, repouso, pesos, malha e animações necessárias,
por revisão do personagem. Usar um adaptador editor C++ pequeno para dados de
malha sem exposição suficiente em Python, em vez de reconstruir pesos via
FBX. Preservar LOD e perfil de skin usados. FBX é alternativa de aquisição
quando já existir, sempre com validação. A extração fica isolada no adaptador.

Manifesto adicional preserva sockets, virtual bones, curvas, notifies,
retarget settings, Control Rig, ABP e pós-processamento. GLB não representa
toda essa semântica. Corretivos assados e corretivos avaliados pelo destino
são alternativas explícitas, para evitar aplicação dupla.

Separar três grupos: dados transportados (curvas/eventos/root motion),
referências mantidas no destino (Skeleton, sockets, ABP, Control Rig) e
recursos não reproduzíveis externamente (deformadores específicos). Não
recriar esses recursos a partir de nomes. Ao editar clipe existente, criar
cópia candidata e modificar campos permitidos; para fonte nova, reconstruir
explicitamente os metadados suportados. Retiming remapeia curvas, notifies
e contatos com o mesmo mapa do movimento. Metadado sem política definida
bloqueia a promoção, em vez de desaparecer. Conferir tudo após recarregar.

Na saída, escolher `AnimationDataController` para escrever transformações
locais no Skeleton existente. Esse caminho já aparece no script de guarda
do Jogo01. A API não faz retarget: recebe o resultado já adaptado. Verificar
retornos de cada operação, amostras e duração; publicar em assets candidatos.
FBX permanece formato de intercâmbio, sem round-trip obrigatório por edição.

Tarefas de assets usam `UnrealEditor-Cmd` com Python commandlet, unattended e
sem render quando compatível. A captura final de superfície/aparência usa
sessão automatizada com render habilitado. O código instalado mostra que a
captura CPU de pele pode exigir objeto de render; não prometer que NullRHI
avalia toda a deformação final. Control Rig/Sequencer têm dependências de
contexto específicas e serão opcionais.
[Modos de execução documentados pela Epic](https://dev.epicgames.com/documentation/unreal-engine/scripting-the-unreal-editor-using-python).

O perfil consumidor inclui cenário de validação persistido: mapa/fixture,
personagem, objetos e vínculos, ABP/slot, estado inicial, acionamentos, passo
temporal fixo, aquecimento e câmeras. O adaptador recria esse cenário e gera
capturas por receita. Há um cenário padrão de AnimSequence isolado; validar
gameplay exige o cenário correspondente, calibrado uma vez e reutilizado.
Sem ele, retornar “sem validação no contexto de jogo”, nunca aprovação geral.

Após salvar, recarregar e amostrar o asset em processo independente. Comparar
pose, tempo e raiz com a revisão enviada e verificar o contexto de uso pedido.
Slot, blend, extração de root motion e ABP podem alterar o resultado. A fila
de escrita é exclusiva por projeto, inclusive entre commandlet e editor já
aberto; não rodar dois escritores sobre os mesmos assets. Quando a publicação
usar o editor aberto, respeitar estado sujo e não sobrescrever alterações.

Área de candidatos é configurável. Promoção exige gates do destino; não
sobrescreve fonte, Skeleton, ABP ou montagem aprovada por efeito implícito.
O jogo recebe animações convencionais. Levar gerador neural ao executável é
outra arquitetura, com orçamento e distribuição próprios.

## 10. Reaproveitamento e decisões de exclusão

Reaproveitar matemática, Mink/MuJoCo, I/O/render Blender, geração Kimodo e seu
MotionCorrection/cache. Desenvolver contratos, máscaras, contatos, retarget,
histórico, diagnósticos, orçamento de iteração e publicação. Patches de
fornecedores ficam pequenos e ligados a revisões auditadas.

CondMDI inspira máscaras de observação e preenchimento temporal; MotionFix,
edição relativa; MotionLab, o contrato movimento + condição → movimento.
Nenhum entra como dependência neural adicional. Suas interfaces e representações
não eliminam a necessidade de preservação e adaptação próprias. A auditoria
também encontrou questões de manutenção e de licença que impedem presumir
incorporação irrestrita. [Decisões por candidato](EVIDENCIAS.md).

`kimodo.cpp` já quantiza o encoder textual na revisão auditada, corrigindo a
avaliação anterior; ainda faltam controles gerais e quantização do denoiser.
Não substitui a API escolhida. MotionBricks/ARDY em tempo real, SkinTokens e
políticas físicas ficam fora do caminho crítico desta oficina, por escopo.
ARDY possui controles; nosso experimento anterior não provou incapacidade do
modelo.

Motius é referência de organização, não dependência do núcleo. Seu pacote
base agrega bibliotecas neurais, a exportação de personagem passa por SMPL-22,
e não foi encontrada licença geral na raiz da revisão inspecionada. Usar
fontes originais com autorização verificável. PyMotion é referência útil de
operações de movimento, mas não oferece o solver de edição necessário; ozz
é útil para runtime e IK reduzido, sem justificar outro núcleo C++ agora.

Não extrair código proprietário da Unreal para o núcleo externo. Componentes
MIT/Apache conservam atribuição; Blender permanece processo externo sob seus
termos. Código, modelos, dados e assets têm registros de licença separados.
Falta de uma proibição no README não autoriza redistribuição.

## 11. Provas delimitadas de implementação

| Prova | Caso pequeno | Falhas que deve detectar |
| --- | --- | --- |
| Coordenadas | Esqueleto assimétrico, rotação de 90°, raiz deslocada e dedos diferentes; comparar FK do pacote e MuJoCo. | Eixos/lados, quaternion, escala, duração e geometria do solver errados. |
| Patch | Mover mão por 20 frames preservando dedos animados, empunhadura obrigatória e janela externa; medir fronteiras após projeção; depois alvo incompatível. | Máscara violada, membro congelado no tempo, salto temporal e sucesso falso. |
| Contatos | Pé apoiado, salto permitido e mão perto do rosto, com amostras intermediárias. | Deslizamento, contato indevido e penetração entre keyframes. |
| Recuperação | Cancelar, reiniciar e repetir a mesma entrada. | Resultado parcial aprovado, download/inferência repetidos e vazamento de recursos. |
| Unreal | Gravar clipe curto com evento, recarregar noutro processo, comparar e recriar o cenário de captura. | Asset divergente, perda de raiz/metadados, evento fora de tempo e validação manual não reproduzível. |
| Kimodo | Clipe curto com keyframes/alvo; repetir texto com cache e conferir pós-processamento. | Ambiente, formato, condicionamento e cache incompatíveis. |

Começar com dados sintéticos, sem geração pesada. O ensaio neural não bloqueia
a edição de clipes existentes. Repetir apenas ao mudar dependências relevantes;
falha gera correção específica, sem reiniciar a seleção de todos os candidatos.

Limites iniciais propostos para humano em escala normal: alvos obrigatórios
com erro até 5 mm/1 grau; canais locais protegidos até 0,1 mm/0,1 grau após
serialização; frames externos iguais à base dentro da tolerância de round-trip.
São critérios de engenharia a registrar por perfil, não resultados medidos.
Falha vira revisão parcial/reprovada. A tolerância de alvo não é permissão
para a pele atravessar o rosto; contato de superfície tem critério próprio.

Métricas temporais usam segundos e taxa de amostragem explícita. Piso vem da
cena, não do menor ponto do pé no próprio clipe, que poderia esconder
penetração. Verificar amostras raw e comprimidas no destino. Qualidade
artística continua separada das tolerâncias numéricas.

## 12. Organização e sequência de construção

```text
autoria-ia/animacao/
  README.md, ESTUDO.md, EVIDENCIAS.md
  core/          # contratos, receitas, versões, planejamento de jobs
  motion/        # retarget, camadas, tempo, contatos, correção
  adapters/      # mink, blender, kimodo, unreal e formatos
  interfaces/    # CLI e fachada MCP sobre os mesmos serviços
  inspection/    # medidas, frames, imagens e diagnósticos
  skills/        # procedimentos de criação, edição e publicação
  tests/         # contratos sintéticos e integrações delimitadas
```

Essa árvore é futura. Perfis e bibliotecas pertencem ao workspace consumidor.
O módulo nasce aqui, mas pode virar pacote/repositório próprio sem levar a
Unreal para o núcleo.

Primeira entrega: registrar personagem, abrir movimento conhecido, editar
um trecho com contatos/preservações, receber inspeção, desfazer e exportar.
Depois ligar publicação Unreal e comprovar ida e volta. Então conectar Kimodo
à mesma entrada de fontes. Expandir receitas após o laço estar operacional.

Skills ensinam escolhas e interpretação de evidências; schemas vêm do catálogo.
Entradas de descoberta por cliente apontam para orientação canônica, sem cópias
divergentes ou suposição de descoberta automática de pasta aninhada. A
orientação de uso fica separada do dossiê de desenvolvimento.

O diferencial buscado é edição localizada com memória do trabalho e retorno
acionável: corrigir sem destruir decisões anteriores e saber o próximo ajuste.
É uma direção concreta de produto, não uma alegação de ineditismo científico
ou garantia de qualidade universal. Nesta rodada foram alterados documentos;
nenhum modelo, runtime ou asset foi instalado, executado ou modificado.
