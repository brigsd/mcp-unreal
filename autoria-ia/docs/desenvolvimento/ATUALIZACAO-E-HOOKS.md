> Cópia histórica desde 19/09/2026. O AnimAI agora tem raiz própria.
> Fonte atual: [docs/desenvolvimento/ATUALIZACAO-E-HOOKS.md](../../../../AnimAI/docs/desenvolvimento/ATUALIZACAO-E-HOOKS.md).
> O conteúdo abaixo foi preservado para consulta e não governa trabalho novo.

# AnimAI — atualização documental e hooks

Versão 1, de 19/09/2026. Apoia o [contrato macro](CONTRATO-MACRO.md) e o
[plano documental](../../planos/DOCUMENTACAO-E-SKILLS.md). Objetivo: detectar
perda de validade e encaminhar a revisão certa, sem alegar atualização automática
do conhecimento só porque uma rotina foi executada.

## O que existe e o que será implementado

Nesta revisão existem contrato, índices e instruções em
[AGENTS.md](../../AGENTS.md): gatilhos documentais para agentes que carreguem
essas instruções. Não são scripts executáveis nem garantia de leitura em
qualquer cliente. Não há job agendado, monitoramento web, hook Git ou CI AnimAI
instalado. Nenhum hook da Unreal foi modificado.

A0 implementará o verificador local; A1 o integrará aos gates. O4 validará
empacotamento e integração do comando no ambiente de desenvolvimento escolhido.
Hooks de cliente/Git são adaptadores opcionais e explícitos; o gate reproduzível
é obrigatório e não depende de instalar um hook em cada máquina.

## Gatilhos e consequências

| Gatilho | Ação exigida | Limite |
| --- | --- | --- |
| Entrada em trabalho de desenvolvimento AnimAI. | Ler índice e estado da revisão dos documentos pertinentes. | Não carregar todo o histórico nem pesquisar o mercado em cada sessão. |
| Pergunta macro, inclusive paráfrases. | Ler contrato macro e fazer auditoria atual das capacidades/alternativas relevantes. | Mesmo evidência dentro do prazo não dispensa verificar novidades para responder “hoje”. |
| Mudança de API, schema, capability, exemplo, plano ou skill. | Identificar docs dependentes, atualizar referências e repetir testes afetados no mesmo checkpoint. | Alterar uma data ou reformatar um arquivo não comprova revisão. |
| Mudança de lock, adaptador, licença, formato, hardware-alvo ou requisito. | Invalidar recibos e decisões dependentes; reavaliar compatibilidade e custo. | Não atualizar pacotes/modelos automaticamente. |
| Defeito observado ou alternativa nova conhecida que contradiz decisão. | Registrar evidência, marcar decisão afetada para revisão e encaminhar a análise. | Erro não prova impossibilidade global nem autoriza reconstruir tudo. |
| Prazo de revisão vencido. | Marcar evidência temporal como pendente na próxima execução do verificador. | Não há processo que acorde sozinho; não bloqueia uso de assets/capacidades válidos. |
| Conclusão de tarefa, etapa ou distribuição. | Rodar gates, verificar vínculos, exemplos, versões e pendências do escopo. | Não declarar entrega validada quando a documentação requerida está divergente. |

## Política de validade

Separar o estado editorial (`planned`, `draft`, `validated`, `historical`) da
validade da evidência (`current`, `stale`, `unverified`, `historical`). Uma
proposta pode estar bem escrita e ainda não ter prova de implementação.

Referências sobre mercado, manutenção de dependências, disponibilidade,
preço/licença e compatibilidade externa têm prazo inicial de revisão de
30 dias após conferência real, ou antes se houver mudança relevante conhecida.
Esse prazo é política do AnimAI, não garantia de que nada mudou no intervalo.
Exigências verificadas contra versão fixa não se tornam falsas por idade;
o prazo reabre sua adequação atual, preservando a evidência histórica.

Contratos estáveis e exemplos versionados são invalidados por mudança de suas
fontes/requisitos, sem pesquisa mensal arbitrária. A pergunta explícita sobre
as melhores opções sempre exige conferência externa atual das alegações
temporais. Fontes inacessíveis ficam não verificadas; acesso HTTP bem-sucedido
não comprova que o conteúdo ainda sustenta a decisão.

O manifesto documental planejado ganha `freshness` por documento: `kind`
(`stable`, `external`, `mixed`, `historical`), `reviewed_at`, `review_after`,
`source_fingerprints` (mapa caminho relativo → SHA-256 dos bytes),
`evidence_refs` e `reason`. Horários são ISO 8601 UTC; campos sem comprovação
ficam nulos. Documentos mistos usam a política temporal para afirmações externas
e fingerprints para dependências locais. O verificador calcula o estado;
um campo escrito manualmente como “current” não sobrepõe a prova.

O manifesto mapeia `receipt_paths` (ID → caminho relativo de recibo local).
Cada recibo contém `id`, `reviewed_at`, `document_ids` e `source_fingerprints`.
Para pesquisa externa, contém também `sources` com URL primária, data de acesso,
versão/revisão quando disponível e afirmação que a fonte sustenta. Não criar
recibos vazios para satisfazer o formato; os dados precisam corresponder ao
trabalho efetivamente feito. Em A0, definir o schema e validar campos/links.

Uma decisão registra questão, opção vigente, alternativas consideradas, ação
(manter/substituir/complementar/construir), fontes/versões, limitações, provas,
impacto nos consumidores e motivo/data de reabertura. A nova revisão preserva
a anterior como histórico. Registros de pesquisa não certificados por esta
rodada mantêm suas datas e cobertura originais.

## Contrato do verificador planejado

Arquivo futuro: `oficina/scripts/doc_freshness.py`; testes em
`oficina/tests/docs/test_freshness.py`, sem rede nem dependências pesadas.
Interface pura para testes:

```python
def evaluate_freshness(document: dict, now: str,
                       observed_fingerprints: dict[str, str]) -> dict:
    ...
```

Resultado: `state` e `reasons` (códigos). Precedência: histórico explicitamente
classificado retorna `historical`; prova ausente/incompleta retorna
`unverified`; fingerprint divergente ou prazo vencido retorna `stale`;
caso restante retorna `current`. Um documento estável requer ao menos um
fingerprint de fonte local ou referência de evidência verificável; externo
requer revisão, evidência e prazo até 30 dias depois. Documento misto exige
ambas as provas. Revisão futura, prazo inválido, evidência ausente ou fonte
apagada nunca aprovam. Comparar prazo com `now >= review_after`.

A CLI resolve `evidence_refs` pelos `receipt_paths` e acrescenta ao `document`
o campo transitório `evidence_receipts`, lista dos recibos validados; a função
pura não lê arquivos. Ela confere vínculo do ID, documento, data e fontes com
o estado revisado. Referência não resolvida ou recibo divergente resulta em
`unverified`. Códigos mínimos: `MISSING_EVIDENCE`, `INVALID_REVIEW_TIME`,
`SOURCE_MISSING`, `SOURCE_CHANGED` e `REVIEW_EXPIRED`. Fingerprint diferente
do observado retorna `SOURCE_CHANGED`, mesmo que o texto documental não mudou.

CLI planejada (ainda inexistente):

```text
python scripts/doc_freshness.py --manifest docs/manifesto.json --scope all --mode report
python scripts/doc_freshness.py --manifest docs/manifesto.json --scope changed --mode gate
```

`report` resume IDs, estado e motivo, sem alterar datas ou documentos; pendência
válida retorna 0, erro de configuração retorna 2. `gate` retorna 1 para
pendência obrigatória no escopo e 2 para configuração inválida. Não baixa nada.
`changed` compara o checkpoint-base explicitamente fornecido por `--base <ref>`
com a árvore de trabalho, incluindo alterações staged/unstaged e novos arquivos
do pacote, e resolve dependentes transitivos pelo manifesto. Sem base válida
ou fora do Git, verificar `all`; jamais assumir lista vazia. Os testes passam
`now` à função pura; a CLI de produção usa o relógio real em UTC.

O gate de alteração bloqueia documentos operacionais afetados que contradizem
schemas/capacidades/fontes e evidências usadas para aprovar a decisão alterada.
Páginas planejadas ou históricas não são exigidas como provas de capacidades
entregues. Pesquisa vencida de módulo não afetado vira aviso e permanece visível;
não paralisa correção nem uso comum. Uma pendência de pesquisa bloqueia o selo
de decisão atual, não a execução inteira do AnimAI.

## Provas que os hooks precisam passar

E1/A0 deve testar prazo exato, passagem de dia, revisão futura, fonte apagada,
mudança local sem mudança do texto, arquivo novo não rastreado e dependência
transitiva. Atualizar só `reviewed_at` sem recibo novo de evidência não renova
a certificação: a comprovação deve vincular data, fontes e revisão avaliada.
A checagem estrutural dessa comprovação não substitui julgar sua veracidade.

Os cenários de `animai-desenvolver` incluem a pergunta macro literal e uma
paráfrase, com evidência vencida e pesquisa indisponível. A IA deve identificar
a intenção, declarar limites e propor decisões concretas; não responder
“é o melhor porque segue nosso plano”. Uma edição comum de animação não deve
disparar pesquisa ou desenvolvimento de ferramentas.

Em A1, os gates acumulados chamam esse verificador. Em O4, validar que o comando
funciona no checkout relocável e que o bundle de desenvolvimento inclui este
protocolo. Configuração de CI/hook real depende do repositório/cliente escolhido;
não criar um workflow aninhado que a hospedagem não executaria nem substituir
hooks preexistentes. Falta de integração deve constar como não implementada.
