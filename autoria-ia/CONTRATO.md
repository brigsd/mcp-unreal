> Cópia histórica desde 19/09/2026. O AnimAI agora tem raiz própria.
> Fonte atual: [docs/desenvolvimento/CONTRATO.md](../../AnimAI/docs/desenvolvimento/CONTRATO.md).
> O conteúdo abaixo foi preservado para consulta e não governa trabalho novo.

# AnimAI — contrato do conjunto modular

Versão 1.2, de 19/09/2026. Mantém nome e trilhas da versão 1.1; acrescenta o
contrato de avaliação macro e a política de atualização documental, sem
alterar as garantias técnicas da versão 1.
Os requisitos abaixo governam o desenvolvimento futuro; não descrevem
ferramentas já disponíveis. Esta entrega é documental, sem instalação,
implementação, migração de assets ou mudança das MCP tools existentes.

## 1. Objetivo e fronteiras

AnimAI é o nome deste conjunto modular de autoria de animação por IA.
“Usar AnimAI” significa operar esse conjunto; “desenvolver AnimAI” significa
evoluir sua implementação. Não é outro nome para o Jogo01, Mecanifica ou para
todo o MCP_Unreal. O diretório atual `autoria-ia/` permanece por compatibilidade
dos links; essa localização não cria dependência do repositório hospedeiro.

Oferecer à IA operações práticas para criar, inspecionar, corrigir e publicar
conteúdo, preservando decisões aprovadas e permitindo iteração por partes.
A medida de utilidade é concluir esse ciclo com retorno verificável e pouca
coordenação manual, não a quantidade de bibliotecas ou tools reunidas.

Animação de personagens é o primeiro domínio. Começa com humanoides que já
tenham esqueleto e skin, movimentos existentes e ajustes localizados. Geração
neural é uma fonte opcional. Rigging de malha estática, atuação facial,
criaturas arbitrárias e animação neural dentro do jogo ficam fora da primeira
entrega. Novos domínios exigem recorte próprio, sem ampliar este escopo por
analogia.

Mecanifica permanece independente e responsável por seus objetos mecânicos.
Jogo01 é consumidor, com seus assets e perfis. Unreal é destino e avaliador
de integração. Nenhum dos três define caminhos, personagens ou convenções
obrigatórias do núcleo desta oficina.

## 2. Arquitetura e organização

Uma API de serviços sustenta MCP e CLI, com a mesma validação e os mesmos
resultados. O núcleo mantém contratos, receitas, revisões, catálogo de
capacidades e tarefas. Integrações traduzem esses contratos para bibliotecas,
processos e destinos. Dados persistidos não dependem de objetos internos de
um fornecedor. Não haverá uma segunda implementação das regras dentro do MCP.

O domínio de animação se organiza em cinco módulos por responsabilidade:

| Módulo | Responsabilidade e resultado |
| --- | --- |
| Personagens | Registrar esqueleto, malha, pesos, âncoras e limites; devolver perfil calibrado ou ambiguidades explícitas. |
| Movimentos | Importar, compor e receber geração opcional; manter fontes, tempo, receitas e revisões. |
| Edição | Ajustar poses, dedos, trajetórias e contatos por trecho; adaptar movimentos ao personagem de destino. |
| Inspeção | Medir preservações, contatos e continuidade; produzir comparação visual e diagnóstico acionável. |
| Publicação | Converter e entregar uma revisão a formatos ou motores; conferir dados e registrar o resultado no destino. |

Cada módulo terá documentação de desenvolvimento que explique finalidade,
operações, entradas, saídas, limites e dependências; schemas versionados;
testes de contrato; e orientação de uso por tarefa. Skills ensinam o fluxo e
a interpretação dos resultados. Validação, limites e preservações precisam
existir no código, sem depender de a IA lembrar uma instrução.

As integrações ficam identificadas por fornecedor dentro de adaptadores.
Trocar o resolvedor não muda o significado de “preservar empunhadura”.
Descoberta não carrega modelos nem instala dependências. O pacote deve poder
sair deste repositório sem levar o editor Unreal ou o Jogo01 para seu núcleo.

## 3. Superfície de trabalho para a IA

O catálogo público oferece poucas operações orientadas a tarefas. Estes
nomes são contratos propostos, ainda não comandos executáveis:

| Operação | Contrato resumido |
| --- | --- |
| `animai.describe` | Informar capacidades realmente disponíveis, versões, dependências e limites sem inicializar cargas pesadas. |
| `actor.register` | Produzir um pacote de personagem reutilizável e o diagnóstico de sua calibração. |
| `motion.build` | Criar candidatos a partir de fonte, receita ou gerador permitido, com origem e evidências. |
| `motion.patch` | Executar um lote de alterações sobre uma revisão-base, limitado por região, tempo e preservações. |
| `motion.inspect` | Medir e mostrar uma revisão, compará-la à base e indicar problemas por parte e intervalo. |
| `motion.publish` | Entregar uma revisão a um destino explícito, sem sobrescrever o trabalho aprovado por efeito implícito. |
| `job.control` | Consultar progresso, cancelar e retomar etapas recuperáveis; liberar apenas recursos da própria oficina. |

A IA expressa intenção através de parâmetros e relações estruturados. Não
precisa emitir uma chamada por osso ou por frame, escolher GPU a cada ajuste
ou controlar manualmente editores. Operações avançadas continuam acessíveis
por schema, sem expor cada função de fornecedor como uma nova MCP tool.

## 4. Dados e preservação

O pacote de personagem preserva hierarquia completa, identidades estáveis,
repouso, bind, pesos e mapeamento semântico. Convenções geométricas, unidades,
tempo e políticas de conversão são explícitas e versionadas. O movimento
guarda canais locais, raiz, curvas, eventos e contatos. Uma representação
reduzida de um modelo não substitui o esqueleto completo do consumidor.

Toda edição informa revisão-base, janela temporal, canais autorizados,
margens de transição e restrições. Preservar dedos locais, palma no mundo e
mão relativa à arma são relações diferentes. O executor não deduz uma delas
silenciosamente. Retiming aplica o mesmo mapa temporal ao movimento e aos
metadados afetados; dados não representáveis produzem diagnóstico de perda.

Revisões são imutáveis. Uma alteração produz candidata, sem modificar a base;
reverter significa voltar a uma revisão íntegra. Conflitos de revisão são
recusados. Preservações e tolerâncias são fixadas antes da execução, com
unidade e referencial, e conferidas no resultado. Pesos altos em uma função
de otimização não comprovam cumprimento de uma restrição obrigatória.

Só promover uma candidata quando cumprir os critérios obrigatórios do pedido.
Falhas podem manter artefatos para diagnóstico, mas não substituem a base nem
recebem aprovação. Relaxar restrições, ampliar a janela ou alterar skin/rig
exige autorização adicional. Falha de um resolvedor não prova impossibilidade
global da pose.

## 5. Retorno, inspeção e iteração

Toda resposta informa estado e capacidades ou resultado pertinente à operação.
Operações de autoria acrescentam identificação da tarefa, revisão-base quando
aplicável, candidata quando houver, resumo das alterações, evidências e
próximos ajustes possíveis. Violações identificam tipo, partes, intervalo,
medida, limite e nível de evidência. Logs e artefatos maiores são referenciados,
sem ocupar todo o contexto da IA.

Comparações A/B usam os mesmos instantes, câmeras e condições de avaliação.
A inspeção combina enquadramento corporal e detalhe das regiões alteradas,
métricas e malha deformada quando necessária. Colisões em aproximações
geométricas não comprovam ausência de interpenetração da pele. Amostragem
finita informa sua cobertura, sem alegar prova contínua universal.

Validade técnica, revisão visual e aprovação no contexto de jogo são estados
distintos. Saída zero de um processo não equivale a aprovação. Quando um
deformador ou comportamento só puder ser avaliado na Unreal, essa pendência
permanece explícita até a conferência no destino.

A iteração automática respeita orçamento de tempo, tentativas e recursos
definido na tarefa. Pode corrigir e reavaliar dentro do escopo autorizado.
Ao esgotar o orçamento ou não melhorar, encerra com diagnóstico e mantém a
base. Não amplia permissões nem inicia tentativas ilimitadas.

## 6. Reaproveitamento e dependências

A preferência é consumir uma biblioteca por adaptador. Extrair código
pontual é aceitável quando reduz dependências ou resolve uma incompatibilidade
real, com testes e origem preservados. Uma versão modificada inteira exige
justificativa e plano de manutenção. Não copiar repositórios completos apenas
para aparentar integração.

Cada componente incorporado registra origem, revisão, licença, alterações,
dependências, capacidades usadas e testes. Licenças de código, pesos, dados e
assets são verificadas separadamente; acesso público ou download gratuito não
basta para autorizar redistribuição ou uso comercial. Custo e necessidade de
conta/serviço são declarados antes de habilitar uma integração. A meta é uma
base local sem serviço pago obrigatório.

Momentum é o candidato prioritário para a integração de processamento de
personagem e sequência; PyRoki/jaxls é alternativa delimitada, não obrigação
de manter dois conjuntos completos. Mink/MuJoCo permanece como referência e
alternativa localizada. A seleção antiga de Mink com refinamento temporal
próprio deixa de ser decisão fechada: não construir esse refinamento do zero
antes de conferir a capacidade necessária no candidato prioritário.

Blender permanece previsto como processo externo de intercâmbio e inspeção;
Kimodo, como fonte generativa opcional; Unreal, como adaptador de publicação e
validação. Esses papéis não significam integrações já homologadas. Cada
adaptador precisa passar pelas provas do contrato antes de aparecer como
disponível. Incompatibilidade deve nomear o requisito que falhou, sem iniciar
uma pesquisa indefinida nem degradar as garantias silenciosamente.

## 7. Execução e recuperação

Serviços de autoria são executáveis sem operação manual de interface. Tarefas
que dependam de contexto de editor ou render declaram isso e automatizam o
contexto necessário. Dependências pesadas ficam em processos/ambientes
isolados; uma correção geométrica não exige carregar um gerador textual.

Configuração local registra recursos por identidade estável, orçamento de
CPU/RAM/GPU e política de concorrência. A oficina não transfere cargas para
outra GPU silenciosamente, não encerra aplicativos do usuário e não envia
assets privados a serviços externos por padrão.

Tarefas e artefatos concluídos são persistidos. Cache considera entradas,
versões e configuração; alterações invalidam somente etapas dependentes.
Reinício retoma a partir de resultados íntegros, sem prometer retomar o meio
de uma inferência que não suporta checkpoint. Cancelamento não promove saída
incompleta. Escritas no destino são serializadas e reconciliadas para evitar
duplicação em uma nova tentativa.

## 8. Publicação e custo no jogo

Publicar recebe destino e revisão explícitos, escreve uma candidata e
confere o resultado após leitura. Substituir assets aprovados é ação separada
e autorizada. Metadados não suportados não desaparecem silenciosamente.
Validação externa não certifica blend, física ou lógica de animação do jogo.

O jogo recebe assets convencionais. O conjunto de autoria, seus modelos e
resolvedores não entram automaticamente no executável. Integrar geração em
tempo de jogo requer outro contrato de runtime, desempenho e distribuição.

## 9. Critério de primeira entrega

A primeira entrega precisa registrar um personagem, abrir um movimento,
editar um trecho, preservar regiões e contatos declarados, produzir revisão
comparável, reverter e exportar. Deve funcionar sem gerador neural e sem
Jogo01. Uma fixture sintética assimétrica verifica conversões e preservações;
um personagem com malha verifica a inspeção de deformação. A integração Unreal
é a etapa seguinte; a fonte Kimodo entra depois pelo mesmo contrato de fontes.

O caso de aceitação é afastar a mão esquerda do rosto entre 0,6 e 1,2 s,
mantendo a empunhadura direita e o restante aprovado. A receita fixa distância
à superfície, canais permitidos, transições e tolerâncias. O resultado deve
mostrar antes/depois e medidas; um pedido conflitante deve falhar mantendo
a base. Cancelamento, recuperação, conflito de revisão e perdas de exportação
também precisam de testes, não apenas o caso de sucesso.

Essas provas são curtas e direcionadas às fronteiras usadas. Não exigem
testar todos os modelos do mercado. Desempenho e qualidade só serão declarados
com evidência da implementação; documentação não equivale a benchmark.

## 10. Autoridade documental

O [índice AnimAI](README.md) encaminha a leitura para
[uso](docs/uso/README.md) ou [desenvolvimento](docs/desenvolvimento/README.md).
Nome, propósito e estado devem estar acessíveis nesses pontos de entrada e
nos metadados das skills. Reconhecimento depende de a IA ter acesso ao
repositório ou às skills instaladas; o nome não cria memória global.

Este contrato governa as fronteiras, garantias e critérios de incorporação do
conjunto. A [entrada de animação](animacao/README.md) informa o estado desse
domínio. O [estudo de 17/09](animacao/ESTUDO.md) e seu
[dossiê](animacao/EVIDENCIAS.md) permanecem como fundamentos e evidências
datadas; suas escolhas de backend e detalhes propostos não prevalecem sobre
este contrato nem constituem APIs já aprovadas ou implementadas.

Schemas e planos de implementação devem detalhar este contrato sem alterar
seu significado. Mudanças incompatíveis exigem revisão explícita do contrato,
impacto nos consumidores e migração definida. A leitura deste documento não
autoriza instalações, publicação remota ou implementação automática.

## 11. Documentação e skills como parte da entrega

Haverá duas trilhas explícitas, com leitura progressiva:

- **Uso:** operar capacidades existentes, preparar entradas, interpretar
  retorno, inspecionar, corrigir, reverter e publicar. Não exige ler código,
  planos, debates de arquitetura ou histórico de pesquisa.
- **Desenvolvimento:** evoluir núcleo, módulos, adaptadores, contratos,
  testes e distribuição. Inclui arquitetura, decisões, ambiente, gates,
  planejamento e evidências; não transforma uma operação de uso em licença
  para modificar o produto.

As skills planejadas são `animai-usar` e `animai-desenvolver`. Cada uma terá
gatilhos, escopo e referências próprios; ambas identificam o nome AnimAI.
São orientações de trabalho, não substitutos de validação em código nem
catálogos duplicados. O catálogo executável informa disponibilidade; contratos
e schemas definem significado. Uma divergência gera diagnóstico, não improviso.

Docs e skills começam em E1 e evoluem com cada capacidade. Uma tarefa só fica
concluída quando suas referências, exemplos e orientações correspondem ao
estado entregue. Guias de uso não anunciam planos como ferramentas prontas.
Mudança incompatível exige versão, migração e atualização das duas trilhas.

Skills precisam de validação estrutural, referências íntegras na instalação e
testes de orientação em contexto novo, com e sem a skill. Falta de capacidade
deve produzir diagnóstico e transferência para desenvolvimento, não alteração
automática do núcleo. O recorte e os critérios estão no
[plano de documentação e skills](planos/DOCUMENTACAO-E-SKILLS.md).

## 12. Avaliação macro e validade das decisões

Perguntas sobre “as melhores ferramentas/abordagens” no AnimAI têm o sentido
definido pelo [contrato macro](docs/desenvolvimento/CONTRATO-MACRO.md): avaliar
o fluxo completo, alternativas atuais e possibilidades de adaptação/criação,
priorizando controle, qualidade, solidez e iteração prática para a IA.
Cumprir este plano não comprova superioridade da arquitetura escolhida.

Fontes, versões, cobertura e incertezas acompanham decisões. Os
[gatilhos de atualização](docs/desenvolvimento/ATUALIZACAO-E-HOOKS.md)
definem quando revisar evidências e documentos dependentes. Detectar uma data
vencida não atualiza conhecimento; passar um teste de links não certifica uma
escolha técnica. A pergunta de análise exige um veredito fundamentado, sem
autorizar por si só substituições, instalações ou publicação de alterações.
