> Cópia histórica desde 19/09/2026. O AnimAI agora tem raiz própria.
> Fonte atual: [docs/desenvolvimento/planos/DOCUMENTACAO-E-SKILLS.md](../../../AnimAI/docs/desenvolvimento/planos/DOCUMENTACAO-E-SKILLS.md).
> O conteúdo abaixo foi preservado para consulta e não governa trabalho novo.

# AnimAI — plano de documentação e skills

Revisão de 19/09/2026. Complementa o [contrato v1.2](../CONTRATO.md) e integra
o [plano mestre](README.md). Define entregas futuras; as entradas de uso e
desenvolvimento já existem como orientação documental, mas skills, validadores
e pacote executável ainda não foram implementados.

O [contrato macro](../docs/desenvolvimento/CONTRATO-MACRO.md) fixa a intenção
de “temos as melhores ferramentas/abordagens?”. O
[protocolo de atualização](../docs/desenvolvimento/ATUALIZACAO-E-HOOKS.md)
define gatilhos, validade da evidência e os hooks a implementar. AGENTS já
encaminha a leitura; verificadores automáticos ainda não existem.

## 1. Decisão

AnimAI é a identidade pública do conjunto. Haverá duas trilhas documentais e
duas skills: `animai-usar` e `animai-desenvolver`. Ambas serão curtas e carregarão
referências por necessidade. Não haverá uma skill monolítica que obrigue a IA
operadora a absorver arquitetura, planos e todo o histórico de pesquisa.

O reconhecimento nasce dos pontos de entrada, dos metadados das skills e da
descoberta do serviço. Não depende desta conversa nem de memória global.
O nome não altera a independência de Jogo01, Mecanifica ou Unreal.

## 2. Estrutura final planejada

Caminhos abaixo são relativos ao futuro pacote `autoria-ia/oficina/`.
Todos os arquivos citados nesta árvore são planejados, não entregas prontas.

```text
README.md                         identidade, estado e duas entradas
AGENTS.md                         roteador curto para agentes neste pacote
docs/
  manifesto.json                  fontes, público, versões, vínculos e testes
  uso/
    README.md                     início por tarefa e pré-requisitos reais
    referencia/                   contratos públicos gerados dos schemas
    exemplos/                     pedidos completos, fixtures e retorno esperado
    primeiro-ciclo.md              importar → editar → comparar → reverter/exportar
    editar-trecho.md               preservações, contatos e iteração delimitada
    inspecionar.md                 evidência numérica, visual e no destino
    configurar-e-recuperar.md      recursos, jobs, cache e retomada
    conectar-mcp.md                instalação/conexão autorizada pelo usuário
    gotchas.md                    sintomas e correções comprovadas
  desenvolvimento/
    README.md                     início por tipo de mudança
    CONTRATO.md                    fonte única das garantias do conjunto
    CONTRATO-MACRO.md              critérios da avaliação do conjunto e decisões
    ATUALIZACAO-E-HOOKS.md          gatilhos, validade de evidência e enforcement
    arquitetura.md                responsabilidades, dependências e fluxo de dados
    interfaces.md                 contratos compartilhados e formatos
    ambiente.md                   setup reproduzível, locks e workers isolados
    testes.md                     fixtures, gates e leitura das evidências
    contribuicao.md                ciclo de mudança e checklist de entrega
    distribuicao.md                versões, compatibilidade, docs e bundles de skills
    modulos/                      contratos por módulo e adaptador
    decisoes/                     decisões duráveis, alternativas e consequências
    planos/                       etapas, progresso e relatórios de execução
    historico/                    estudos datados, sem autoridade operacional
skills/
  animai-usar/SKILL.md
  animai-desenvolver/SKILL.md
scripts/
  doc_freshness.py                 verificador local, sem rede, ligado aos gates
tests/
  docs/                           links, exemplos, fontes e disponibilidade
  skills/                         cenários, rubrica e evidências em contexto novo
```

Guias específicos de retarget, Unreal e Kimodo continuam nas etapas que os
introduzem. Não criar páginas vazias para aparentar cobertura. Criar cada
documento quando houver conteúdo útil; o manifesto registra o restante como
planejado. Índice de uso aponta apenas a guias existentes e rotula limitações.

## 3. Fonte única e migração

Hoje, contrato e planos vivem fora de `oficina/`; permanecem válidos nesses
caminhos durante esta revisão. Em A0, migrar sua autoridade uma única vez para
`oficina/docs/desenvolvimento/`, junto dos índices operacionais para `docs/uso/`.
O contrato vai para `CONTRATO.md`; INTERFACES vai para `interfaces.md`; o plano
mestre e as seis etapas vão para `planos/`; REFERENCIAS vai para
`decisoes/BASE-TECNICA.md`; este documento vai para
`planos/DOCUMENTACAO-E-SKILLS.md`. Estudos datados vão para `historico/` quando
necessários à portabilidade. Corrigir links internos no mesmo checkpoint.

Migrar também CONTRATO-MACRO e ATUALIZACAO-E-HOOKS da trilha atual para a mesma
trilha em `oficina/`, sem duplicá-los. O AGENTS da oficina deve manter os
gatilhos do AGENTS atual, ajustando caminhos e estado. Não perder a distinção
entre instruções textuais, scripts implementados e integrações instaladas.

Os caminhos antigos tornam-se páginas de encaminhamento, sem segunda cópia
normativa. O índice de animação mantém apenas estado e links, não outro plano.
Validar a árvore copiada para local temporário sem acesso ao repositório
hospedeiro. AGENTS e skills do plugin Unreal existente não são substituídos.

Código/schema é fonte dos campos, enumerações e assinaturas; o catálogo informa
disponibilidade na instalação. Contrato define o significado e as garantias;
decisões registram por quê; plano registra o que falta. Docs explicam o uso,
sem manter manualmente uma segunda definição de API. Contradição entre essas
fontes bloqueia a entrega e exige correção, não escolha silenciosa de uma delas.

O manifesto terá `schema_version`, `release` e `documents`. Cada documento
registra `id`, `path`, `audience` (`uso` ou `desenvolvimento`), `kind`, `status`
(`planned`, `draft`, `validated`, `historical`), `source_refs`, `capability_refs`,
`test_refs`, `verified_revision` e `verified_at`. Campos de comprovação ficam
nulos quando não houve validação; páginas planejadas não precisam existir.
Uma referência compartilhada tem um dono, não cópias editáveis por papel.

A extensão `freshness`, seus recibos e sua regra de cálculo são definidos
somente no protocolo de atualização. O manifesto referencia essa fonte, sem
manter outra política de prazo. Datas de escrita e pesquisas não são sinônimos.

## 4. Contrato das skills

| Skill | Quando carregar | Entrega e fronteira |
| --- | --- | --- |
| `animai-usar` | Pedido para usar AnimAI em personagem, pose, clipe, retarget, inspeção ou publicação. | Consultar disponibilidade, preparar pedido, iterar dentro do orçamento, devolver revisão e evidências; não modificar o núcleo. |
| `animai-desenvolver` | Pedido para avaliar ferramentas/abordagens, implementar, depurar, testar ou ampliar o próprio AnimAI. | Na avaliação, aplicar o contrato macro e emitir decisão fundamentada; na mudança autorizada, localizar contrato/etapa, testar e atualizar docs. Não implementar por efeito de uma pergunta nem alterar assets de consumidores por conveniência. |

Frontmatter inclui nome e descrição de gatilhos com “AnimAI”; descrições
diferenciam usar o produto de desenvolver o produto. Corpo inclui escopo,
pré-requisitos, sequência curta, interpretação do retorno, falhas e referências.
Detalhes pertencem aos docs. Não criar uma skill por osso, tool ou fornecedor.
Só separar novas skills se testes demonstrarem uma fronteira útil.

“Melhore esta animação no AnimAI” é uso. “Melhore o resolvedor do AnimAI” é
desenvolvimento. Pedido misto produz recortes explícitos, sem transformar erro
de operação em autorização implícita de implementação. Pedido exclusivamente
de objeto mecânico do Mecanifica não deve ativar essas skills por afinidade 3D.

“Temos as melhores ferramentas/abordagens aqui?” encaminha ao contrato macro
quando o contexto é AnimAI, mesmo sem palavra exata ou pedido de código.
Reconhecer essa intenção faz parte dos testes da skill de desenvolvimento;
o corpo referencia a lista de critérios, sem copiá-la e criar divergência.

Em A0, a skill de desenvolvimento atende o trabalho de construção. A skill de
uso deve reconhecer o conjunto ainda indisponível e encaminhar corretamente,
sem ensinar comandos futuros como executáveis. A partir de A1, seus guias
e exemplos crescem conforme as capacidades reais; transporte MCP só em E4.
Na execução, ler as skills de criação e validação do ambiente antes de editar
SKILL.md. Cada skill é testada separadamente antes de ser distribuída.

### Transferência entre papéis

Quando uma operação revelar falha do AnimAI, a IA usuária devolve um registro
com versão, operação e payload sanitizado, IDs de pedido/job/revisão, resultado
esperado/observado, violações, evidências por referência e reprodução mínima.
Tokens, assets privados e logs brutos desnecessários não entram no registro.
A revisão aprovada permanece intacta. Corrigir o produto depende do escopo
autorizado; a IA desenvolvedora começa por esse registro, não por recontar toda
a sessão de uso.

### Distribuição sem referências quebradas

Fontes das skills permanecem nos dois diretórios previstos. O build de E4
gera bundles autocontidos com SKILL.md e apenas as referências necessárias,
reescrevendo links locais e incluindo manifesto de origem, revisão e hashes.
São artefatos gerados, nunca uma segunda fonte editável de documentação.
O bundle de uso não inclui dossiês e planos de desenvolvimento; o de
desenvolvimento inclui os contratos e instruções exigidos por seus fluxos.
Todo link transitivo obrigatório entra no bundle ou é removido do recorte
opcional explicitamente; link necessário não pode apontar para a máquina
do autor. Validar os bundles fora do checkout antes de oferecer instalação.

Versão do bundle e compatibilidade do serviço são declaradas. Referências de
API são geradas dos schemas da mesma versão; incompatibilidade resulta em
diagnóstico de atualização, sem chamadas inventadas. Instalar no cliente é
ação separada e explícita, não efeito colateral do build.

## 5. Entregas por etapa

| Etapa | Documentação e skills que devem acompanhar a capacidade |
| --- | --- |
| E1/A0 | Identidade, roteadores, contratos macro/atualização, manifesto, verificador local e duas skills testadas com o estado real. |
| E1/A1–A4 | Descoberta, registro, formatos e revisões; exemplos executáveis de CLI; docs e skill de uso deixam claro o que ainda falta. |
| E2 | Edição, retarget e tempo; preservações e falhas; contrato Momentum; regressões e atualização de referências das skills. |
| E3 | Inspeção, exportação e primeiro ciclo; evidência visual e limites; sessão de uso sem depender de docs de desenvolvimento. |
| E4 | Operação MCP, recuperação e recursos; bundles portáveis; cenários por papel em contexto novo e instalação limpa. |
| E5 | Publicação Unreal e validação no jogo; distinção entre resultado externo e contexto do motor. |
| E6 | Fonte gerativa opcional, requisitos/licenças, recursos e fallback declarado; nenhum requisito neural para fluxos anteriores. |

O responsável por cada tarefa mantém docs e referências afetadas no mesmo
checkpoint. Mudança em gatilhos/fluxo de skill exige repetir seus cenários;
mudança de assinatura exige regenerar referências e executar exemplos.
Manter notas de migração para consumidores em mudança incompatível.

## 6. Verificação e critérios de saída

Testes documentais automatizados conferem links e âncoras, manifesto, campos
obrigatórios, exemplos completos contra schemas, versão e disponibilidade.
Casos negativos: link quebrado; operação planejada vendida como disponível;
campo removido ainda em exemplo; bundle que depende de arquivo externo;
versão incompatível. A suíte deve detectar cada defeito deliberadamente.
Conteúdo histórico fica separado e rotulado, fora de exemplos operacionais.

Para cada skill, estabelecer baseline com a documentação sem skill e depois
repetir os mesmos pedidos com a skill em contextos independentes. Registrar
modelo/configuração, fontes oferecidas, ações, resultado e avaliação humana
das evidências. Não considerar contagem de palavras ou presença do nome uma
prova de comportamento. Orientação adicional responde a falhas observadas;
instruções redundantes não se justificam apenas porque cabem no arquivo.

| Cenário | Resultado necessário |
| --- | --- |
| “Use AnimAI para corrigir esta mão e preservar a outra.” | Reconhece o conjunto, entra por uso, consulta capacidades e não lê todo o histórico nem altera código. |
| Mesmo pedido quando a capacidade não existe. | Informa indisponibilidade sem instalar, inventar tool ou declarar resultado fictício. |
| “Adicione suporte a um novo adaptador no AnimAI.” | Entra por desenvolvimento, encontra contratos e testes pertinentes sem exigir docs de todos os módulos. |
| “Temos as melhores ferramentas/abordagens aqui?” e paráfrase no contexto AnimAI. | Lê contrato macro, avalia fluxo completo e alternativas, explicita cobertura e entrega decisões; não defende o plano por circularidade. |
| Pergunta macro com evidência vencida e pesquisa indisponível. | Declara avaliação provisória e lacunas; não renova datas nem inventa pesquisa ou confirmação. |
| “Crie uma peça no Mecanifica.” | Não confunde os produtos nem impõe AnimAI ao pedido. |
| “A edição falhou; quero diagnóstico.” | Produz registro reproduzível e preserva base; não implementa uma correção sem escopo. |
| Skill instalada fora do checkout. | Reconhece AnimAI, abre todas as referências necessárias e respeita a versão disponível. |

Em A0, testar roteamento e indisponibilidade, não operações ainda inexistentes.
Em E3/E4, repetir com o ciclo real em fixture descartável e comparar revisões,
preservações e artefatos. O roteiro nunca autoriza mutações em assets reais.
Sem ferramenta adequada para contextos independentes, registrar o teste como
não executado e não certificar a skill como validada. Baseline e pós-skill
precisam de evidência, não transcrições simuladas pelo autor.

Gate concluído exige: fontes únicas, links íntegros, exemplos correspondentes
às capacidades, nenhum campo obrigatório sem prova e cenários pertinentes
aprovados. Documentação e skills desatualizadas mantêm a tarefa aberta mesmo
que os testes numéricos estejam verdes.
