> Cópia histórica desde 19/09/2026. O AnimAI agora tem raiz própria.
> Fonte atual: [docs/desenvolvimento/README.md](../../../../AnimAI/docs/desenvolvimento/README.md).
> O conteúdo abaixo foi preservado para consulta e não governa trabalho novo.

# AnimAI — desenvolvimento

Entrada para a IA que implementa, corrige e evolui o AnimAI. Estado atual:
planejamento, sem pacote executável nem skills instaladas. Operar animações
com capacidades já disponíveis pertence à trilha de [uso](../uso/README.md).

## Leitura necessária

Para a pergunta “Temos as melhores ferramentas/abordagens aqui?” ou equivalente,
comece pelo [contrato macro](CONTRATO-MACRO.md): dez critérios, decisões
esperadas e limites da auditoria. Não é preciso ler todos os planos para
entender a intenção. A avaliação deve usar as evidências pertinentes e atuais.

1. [Contrato v1.2](../../CONTRATO.md): identidade, escopo, garantias e fronteiras.
2. [Plano mestre](../../planos/README.md): estado, dependências e etapa atual.
3. [Interfaces](../../planos/INTERFACES.md): tipos e comportamentos compartilhados
   quando a mudança tocar API, dados, serviços ou testes.
4. [Documentação e skills](../../planos/DOCUMENTACAO-E-SKILLS.md): estrutura,
   fontes únicas, responsabilidades e critérios de entrega.
5. Somente o plano da etapa e os contratos dos módulos afetados.

Aplicar os [gatilhos de atualização](ATUALIZACAO-E-HOOKS.md) às fontes e
decisões afetadas. As instruções já estão no AGENTS desta pasta; scripts de
verificação e integração aos gates continuam como entregas de E1, não como
automações já instaladas.

O [registro técnico](../../planos/REFERENCIAS.md) fundamenta decisões de
integração. Os [estudos anteriores](../../animacao/README.md) são leitura
seletiva para uma questão histórica, nunca pré-requisito universal.

## Entrega e limites

A skill prevista `animai-desenvolver` orientará diagnóstico, implementação,
testes, atualização das referências e migrações. Cada mudança precisa manter
guia de uso e contrato técnico compatíveis, sem transformar planos em
capacidades anunciadas. Mudanças nas garantias exigem decisão explícita.

O primeiro trabalho de implementação será E1/A0: estrutura documental e
skills por papel, seguida do núcleo leve em A1. A existência deste plano
não autoriza iniciar implementação, instalar integrações ou alterar projetos
consumidores. Retorno ao [índice AnimAI](../../README.md).
