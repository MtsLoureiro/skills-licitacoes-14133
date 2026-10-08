# Regimes, critério de aceitabilidade, sobrepreço, jogo de planilha, curva ABC

## 1. Regime de execução e o que ele muda no orçamento (Lei 14.133, art. 46)

| Regime | Como remunera | Orçamento / cuidado |
|---|---|---|
| **Preço unitário** (art. 46, I) | Paga-se por **unidade medida** de cada serviço executado | Planilha com quantitativos **estimados**; risco de quantidade é do contratante. Critério de aceitabilidade **por item** e global |
| **Preço global** (II) | Preço certo e total; pagamento por **etapas** do cronograma físico-financeiro | Quantitativos precisam estar corretos (projeto executivo completo). Aceitabilidade **global e por etapa** (Decreto 7.983, art. 13, parágrafo único). Licitante pode ter custos unitários diferentes do sistema se global e etapas ficarem ≤ referência (art. 13, I) |
| **Empreitada integral** (III) | Empreendimento completo, "chave na mão" | Idem global; contratado responde até a entrada em operação |
| **Tarefa** (IV) | Mão de obra para pequenos trabalhos, com ou sem material | Orçamento simples; teto de valor local (CONFERIR regra do ente) |
| **Contratação integrada** (V) | Contratado faz projeto básico + executivo + execução | Edital tem **anteprojeto**; orçamento **sintético/paramétrico** com os cuidados do art. 23 § 5º (remuneração de risco; paramétrica só nas frações pouco detalhadas) |
| **Semi-integrada** (VI) | Contratado faz projeto executivo + execução | Projeto básico da Administração; orçamento detalhado do básico |
| **Fornecimento e serviço associado** (VII) | Fornecimento + operação/manutenção por tempo determinado | Fora do foco de orçamento SINAPI |

**Art. 46, § 1º**: é **vedado** realizar obras e serviços de engenharia **sem projeto executivo** (salvo art. 18, § 3º). Quantitativo sem projeto é a principal causa de sobrepreço/aditivo.

## 2. Critério de aceitabilidade de preços

- Parâmetro de **preços máximos, unitários e global**, fixado pela Administração e **publicado no edital** (Decreto 7.983, art. 2º, IX e art. 11). Lei 14.133, art. 59, § 3º: exequibilidade e sobrepreço consideram **preço global, quantitativos e preços unitários relevantes**, conforme o critério do edital.
- Prática de redação: *"Serão desclassificadas as propostas com preço global superior ao orçamento estimado, ou com preço unitário superior ao máximo da planilha para os itens [da curva ABC classe A / de maior relevância], ou ... (inexequível: art. 59 § 4º)."* Defina **quais itens** têm teto unitário (em geral os da classe A da curva ABC e os de maior risco) e se há tolerância. Texto exato: CONFERIR com a assessoria jurídica e a norma do ente.
- **Inexequibilidade**: obras/engenharia, proposta **< 75% do valor orçado** (art. 59, § 4º). **Garantia adicional** se **< 85%** do orçado (art. 59, § 5º). Diligência para demonstrar exequibilidade (art. 59, § 2º).

## 3. Sobrepreço, superfaturamento, jogo de planilha

- **Sobrepreço** (art. 6º, LVI): preço orçado ou contratado **expressivamente superior** aos preços referenciais de mercado — de **um só item** (preços unitários) ou do **valor global** (por tarefa, global ou integral).
- **Superfaturamento** (art. 6º, LVII): dano ao patrimônio da Administração, caracterizado, entre outras situações, por: **(a)** medição de quantidades superiores às executadas ou fornecidas; **(b)** deficiência na execução de obras/serviços de engenharia que diminua qualidade, vida útil ou segurança; **(c)** **alterações no orçamento** de obras/serviços de engenharia que causem desequilíbrio econômico-financeiro **em favor do contratado**; **(d)** outras alterações financeiras que gerem recebimentos antecipados, distorção do cronograma físico-financeiro, prorrogação injustificada com custos adicionais ou reajuste irregular. A expressão "jogo de planilha" **não aparece** no texto da lei: a hipótese (c) é a que a alcança na prática.
- **Jogo de planilha** (conceito): licitante apresenta **preços unitários elevados** em serviços com tendência de **aumento de quantitativo** e **preços baixos** nos que tendem a **diminuir**, mantendo o global competitivo; depois dos aditivos, o contrato fica caro. Defesa: orçamento com **quantitativos corretos**, **tetos unitários** nos itens relevantes, e a regra do **art. 14 do Decreto 7.983** (a diferença percentual entre o valor global do contrato e o preço global de referência **não pode ser reduzida em favor do contratado** por aditivos; preços de aditivos com orçamento específico, art. 15) e a do **desconto global preservado nos aditivos** (Ac. 991/2022-Plenário trata de superfaturamento por **perda do desconto** — leia o acórdão).
- **Limites de aditivo**: 25% (50% reforma de edifício/equipamento), art. 125 da Lei 14.133.
- Ferramentas desta skill: `curva_abc.py` (itens relevantes), BDI por linha (alertas) e memória com pontos de atenção. A análise de jogo de planilha em contrato em execução é outra tarefa (comparar proposta × orçamento × aditivos item a item): fora do escopo dos scripts.

## 4. Curva ABC

Ordena os itens do orçamento por valor, acumula o percentual e classifica. **Cortes 80% / 95% são convenção da engenharia de custos, não norma** (`--corte-a`, `--corte-b`). Usos:
1. Escolher os itens com **teto unitário** no edital e priorizar a **conferência** de preços/composições (poucos itens concentram a maior parte do valor).
2. Direcionar pesquisa de cotação e composições próprias.
3. Amostra de verificação em transferências: o Decreto 7.983, art. 17, I, usa "no mínimo 10% dos itens que somem ao menos 80% do valor" (**CONFERIR** redação vigente) — outro uso, mesma lógica.
Rodar a ABC por **insumos** (agregando o consumo de cada insumo em todas as composições) exige o analítico completo; esta skill faz a ABC **de serviços**.

## 5. Quando usar contratações similares do PNCP em engenharia

- Posição **III** na ordem do § 2º do art. 23. Em obra, serve como **sanidade global** (R$/m² de obra comparável, com data e região) e para **itens avulsos** (equipamentos/bens). Não substitui SINAPI/SICRO para serviços com composição (ver `sicro-e-outras-fontes.md`).
- Preço global de obra de outro órgão carrega projeto, local, BDI e riscos diferentes: ajuste/explique a diferença.

## 6. Orçamento sigiloso (art. 24)

Pode ser sigiloso se justificado; **quantitativos e informações para elaborar propostas continuam públicos**; não vale para controle interno/externo; no **maior desconto**, o preço estimado/máximo consta do edital. O sigilo não dispensa orçamento detalhado e fundamentado (ele fica no processo).

## 7. Composições próprias e cotações no controle

O controle (TCU/CGU/TCE) pede: composição analítica com **fonte dos coeficientes e dos preços**, data-base, ART do orçamentista, justificativa de não usar SINAPI/SICRO, e que a composição própria use **insumos do SINAPI** quando existirem (Decreto 7.983, art. 5º, parágrafo único, trata de sistemas novos incorporando insumos do SINAPI/SICRO). Itens "verba" (vb) sem decomposição são alvo clássico: evite.
