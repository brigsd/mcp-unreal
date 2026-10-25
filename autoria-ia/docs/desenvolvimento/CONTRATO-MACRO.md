> Cópia histórica desde 19/09/2026. O AnimAI agora tem raiz própria.
> Fonte atual: [docs/desenvolvimento/CONTRATO-MACRO.md](../../../../AnimAI/docs/desenvolvimento/CONTRATO-MACRO.md).
> O conteúdo abaixo foi preservado para consulta e não governa trabalho novo.

# AnimAI — contrato de avaliação macro

Versão 1, de 19/09/2026. Define o entendimento da pergunta; não certifica que
as escolhas atuais sejam as melhores. Complementa o
[contrato técnico](../../CONTRATO.md), sem alterar suas garantias.

## Quando ler

Quando o usuário perguntar “Temos as melhores ferramentas/abordagens aqui?”,
“o que falta investigar?”, “há algo mais avançado?” ou pedir uma avaliação
equivalente do AnimAI, aplicar este contrato. É uma tarefa de desenvolvimento
e avaliação estratégica, mesmo sem pedido de alteração de código.

## O que a pergunta significa

Considerando o que existe hoje e o que podemos adaptar ou construir, o AnimAI
tem a melhor combinação viável para uma IA produzir animações com qualidade,
controle, praticidade e retorno verificável?

Avaliar obrigatoriamente:

1. **Resultado completo:** preparar personagem, obter movimento, adaptar,
   editar, inspecionar, corrigir, reverter e publicar.
2. **Controle efetivo:** ajustes locais de corpo, mãos, dedos, contatos e tempo,
   preservando o que já foi aprovado; não depender apenas de novos prompts.
3. **Praticidade para a IA:** operações semânticas em lote, execução automatizada,
   retorno estruturado e pouca coordenação manual entre ferramentas.
4. **Solidez:** revisões recuperáveis, validação independente, diagnóstico,
   testes de regressão e falhas que não destruam trabalho aprovado.
5. **Iteração útil:** comparar antes/depois, localizar o problema e corrigir só
   o necessário, sem regenerar tudo nem recarregar modelos sem necessidade.
6. **Alternativas atuais:** pesquisar além das ferramentas já conhecidas e da
   Unreal; considerar bibliotecas, técnicas, projetos e combinações externas.
7. **Adaptação e criação própria:** integrar ou reaproveitar componentes com
   licença e origem preservadas; construir lacunas quando isso trouxer ganho
   concreto, incluindo custo de desenvolvimento e manutenção.
8. **Viabilidade real:** hardware, memória, latência, sistema operacional,
   dependências, licenças de código/pesos/assets, redistribuição e custo.
   Priorizar base gratuita/local; vantagem paga não vira requisito implícito.
9. **Coerência do conjunto:** compatibilidade de dados, limites entre módulos,
   portabilidade/headless, observabilidade e custo de trocar componentes.
10. **Cobertura e incerteza:** dizer o que foi investigado, o que falta e quais
    limitações são documentadas, observadas em teste ou apenas inferidas.

## Como decidir

O contrato técnico continua sendo o piso: qualidade e preservações obrigatórias
não podem ser trocadas por novidade, velocidade ou facilidade de instalação.
Entre alternativas que atendem esse piso, priorizar controle, qualidade e
iteração da IA; então avaliar custo operacional, dependências e manutenção.

Comparar a arquitetura atual com alternativas relevantes e a opção de
combinar/adaptar/construir. Uma recomendação precisa nomear capacidade,
limitação resolvida, ganho, custo, risco e impacto de migração. Não declarar
vantagem só por popularidade, demonstração bonita, nome recente ou quantidade
de tools. Uma abordagem própria pode ser melhor, mas precisa da mesma prova.

Consultar fontes primárias atuais quando a pergunta tratar do melhor disponível
hoje. Registrar data, versões e cobertura; evidência antiga não vira atual por
releitura deste plano. Se a pesquisa não for possível, declarar a limitação
e entregar avaliação provisória, sem atestar superioridade atual.

Usar documentação e código para eliminar opções inadequadas. Propor teste
somente para incerteza que possa mudar uma decisão: hipótese, fixture,
critério de aprovação, orçamento e consequência do resultado. A avaliação
não autoriza instalações, downloads pesados ou benchmarks automaticamente.

## Retorno obrigatório à pergunta

Entregar primeiro um resumo direto, com estes cinco itens:

1. **Veredito datado:** o conjunto é adequado, tem lacunas ou há evidência
   insuficiente; delimitar para qual objetivo e condições.
2. **Manter:** escolhas sustentadas e por quê.
3. **Substituir, complementar ou construir:** ações priorizadas pelo ganho no
   fluxo completo, com custo e risco; “nenhuma” exige justificativa.
4. **Lacunas e prova mínima:** pontos não investigados e testes decisivos que
   ainda faltam, sem transformar a avaliação em pesquisa infinita.
5. **Evidências e impacto documental:** fontes/versões, data da análise e quais
   decisões, planos, docs ou skills precisam ser atualizados.

“Melhor” é uma recomendação fundamentada no recorte e na evidência, não uma
garantia de conhecer todas as soluções do mundo. O plano existente é objeto
da avaliação; estar de acordo com ele não demonstra que ele seja a melhor
escolha. Pergunta de análise não autoriza implementar nem publicar mudanças.

## Manutenção deste entendimento

Aplicar os [gatilhos de atualização](ATUALIZACAO-E-HOOKS.md). A skill futura
`animai-desenvolver` deve encaminhar essa intenção para este contrato, inclusive
quando a frase variar. Quem apenas usa o AnimAI não precisa abrir uma auditoria
de arquitetura a cada edição de animação.
