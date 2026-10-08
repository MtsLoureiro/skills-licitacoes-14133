# Base normativa da pesquisa de preços (comentada)

> Texto de referência. Os dispositivos abaixo foram conferidos no texto das normas em 07/10/2026
> (legislação federal e portal de compras do governo federal). Onde está **CONFERIR**,
> não houve confirmação da vigência atual: abra a norma oficial antes de citar no processo.

## 1. Lei nº 14.133/2021, art. 23 (vale para todos os entes)

- **Caput**: o valor estimado deve ser compatível com os valores de mercado, considerados os preços de
  **bancos de dados públicos** e as quantidades a contratar, com atenção à economia de escala e às
  peculiaridades do local de execução.
- **§ 1º** (bens e serviços em geral): valor estimado definido com base no **melhor preço aferido** por meio
  dos parâmetros abaixo, "adotados de forma combinada ou não":
  - **I** composição de custos unitários menores ou iguais à **mediana** do item no painel de preços ou no
    banco de preços em saúde disponíveis no PNCP;
  - **II** **contratações similares** da Administração Pública, em execução ou concluídas no **período de 1 (um) ano**
    anterior à data da pesquisa, inclusive por registro de preços, com índice de atualização de preços;
  - **III** pesquisa publicada em mídia especializada, tabela de referência aprovada pelo Poder Executivo federal e sítios
    especializados ou de domínio amplo, **com data e hora de acesso**;
  - **IV** pesquisa direta com **no mínimo 3 fornecedores**, com solicitação formal de cotação e justificativa da escolha,
    sem orçamentos com mais de **6 meses** de antecedência da divulgação do edital;
  - **V** pesquisa na base nacional de notas fiscais eletrônicas, na forma de regulamento.
- **§ 2º** (obras e serviços de engenharia): ordem própria, com **SICRO** (transportes) e **SINAPI** (demais), mais BDI e encargos
  sociais. **Fora do escopo desta skill**; ver `saneamento-e-casos-limite.md`.
- **§ 3º**: Estados, DF e Municípios, sem recursos da União, podem usar outros sistemas de custos adotados pelo respectivo ente.
- **§ 4º**: contratação direta (dispensa/inexigibilidade) sem possibilidade de estimar pelos §§ 1º a 3º: o contratado comprova
  que o preço é compatível com o praticado em contratações semelhantes, por **notas fiscais** de até 1 ano ou outro meio idôneo.

## 2. IN SEGES/ME nº 65, de 7/7/2021 (órgãos federais)

Regulamenta a pesquisa de preços para **bens e serviços em geral** na Administração federal direta, autárquica e fundacional.
Não se aplica a obras e serviços de engenharia (art. 1º, § 1º).

| Artigo | Conteúdo útil |
|---|---|
| Art. 1º, § 2º | Estados/DF/Municípios que executem **recursos da União** (transferências voluntárias) devem seguir a IN |
| Art. 1º, § 3º | Também se aplica à vantagem econômica de **adesão a ata de registro de preços** |
| Art. 2º | Define **preço estimado** (método matemático sobre série de preços, **desconsiderando inexequíveis, inconsistentes e excessivamente elevados**) e **sobrepreço** |
| Art. 3º | **Conteúdo mínimo do documento**: objeto; responsáveis; fontes consultadas; **série de preços**; **método estatístico**; justificativas (inclusive dos valores desconsiderados); **memória de cálculo** e documentos; justificativa dos fornecedores escolhidos (pesquisa direta) |
| Art. 4º | Observar, quando possível, condições comerciais: prazos e locais de entrega, quantidade, pagamento, frete, garantia, marca/modelo, economia de escala e local |
| Art. 5º | **Parâmetros** (I a V, espelham o art. 23 § 1º, com prazos: mídia/sítios até **6 meses** antes do edital; fornecedores até 6 meses; notas fiscais até 1 ano). **§ 1º: priorizar os incisos I e II**; usar outro só com **justificativa nos autos** |
| Art. 5º § 2º | Pesquisa com fornecedores: prazo de resposta compatível, propostas formais com dados mínimos (descrição, valor unitário/total, CNPJ/CPF, contatos, data, responsável), informar as características da contratação e **registrar quem foi consultado e não respondeu** |
| Art. 6º | **Métodos**: **média, mediana ou menor** valor, sobre **3 ou mais preços**, desconsiderados inexequíveis, inconsistentes e excessivamente elevados. § 1º: outros métodos, justificados e aprovados. § 2º: pode somar/subtrair percentual. § 3º: **critérios para descartar valores devem ser fundamentados e descritos no processo**. § 4º: análise crítica, sobretudo com grande variação. § 5º: **menos de 3 preços** só excepcionalmente, com justificativa e aprovação da autoridade. § 6º: se baseado **só** no inciso I do art. 5º, o valor **não pode superar a mediana** do item |
| Art. 7º | Contratação **direta**: aplica-se o art. 5º; sem como estimar, justificativa por notas fiscais de objetos idênticos da futura contratada (até 1 ano), ou semelhantes; § 3º veda inexigibilidade se a justificativa de preços mostrar possibilidade de competição; § 4º/5º dispensa por valor (art. 75, I e II) pode estimar junto com a cotação formal |
| Art. 8º | **TIC**: preços dos Catálogos de Soluções de TIC com Condições Padronizadas valem como preço estimado, salvo se a pesquisa der menos |
| Art. 9º | **Mão de obra com dedicação exclusiva**: aplica-se a IN nº 5/2017 "ou outra que venha a substituí-la" (**CONFERIR** qual norma está em vigor; há atos recentes da SEGES/MGI sobre custos mínimos nesses contratos) |

**Vigência (verificação de 07/10/2026):** a IN 65/2021 continua listada entre as instruções normativas vigentes no portal de compras do governo federal
e sem marca de revogação nas fontes consultadas; **não encontrei norma que a tenha substituído**. Mesmo assim **CONFERIR** no
portal oficial (gov.br/compras → Legislação → Instruções Normativas) e no DOU, porque a busca não prova ausência de alteração.

## 3. O que a norma NÃO diz (decisões que são suas e precisam constar do processo)

- **Não há percentual fixo** para descartar preço "fora da curva". Práticas antigas de "mercado" com percentual fixo de corte não estão na IN 65 (não cite como regra legal sem localizar o dispositivo); o que vale é o critério
  **fundamentado e descrito** (art. 6º § 3º). Por isso `calcular_precos.py` pede um critério explícito (IQR, MAD, faixa da mediana) e o grava na memória de cálculo.
- **Não impõe** média, mediana ou menor: você escolhe e justifica. Mediana é a escolha mais defensável quando há dispersão.
- **"Ano anterior à data da pesquisa"** conta da data da pesquisa; use a **data do resultado** (homologação/adjudicação) do item, não a de publicação do edital.
- **Índice de atualização**: a norma manda observá-lo, mas não escolhe o índice. Se o preço tem alguns meses, aplique um índice oficial (IPCA, IPCA-E ou o setorial do contrato)
  e registre qual e por quê (`--fator`).

## 4. Outros entes (Estado, DF, Município, empresas estatais)

- A **Lei 14.133 vale para todos**. A **IN 65 é federal**: fora da União ela serve como **referência metodológica**, a menos que o seu ente
  a tenha adotado por decreto/regulamento próprio ou que haja recurso federal (art. 1º § 2º).
- **Conferir a norma local**: decreto ou portaria estadual/municipal de pesquisa de preços costuma existir e pode mudar parâmetros, prazos ou o mínimo de preços.
- **Estatais** seguem a Lei 13.303/2016 e o regulamento interno (CONFERIR); a lógica de mercado é a mesma.
- **Art. 23 § 3º** da Lei 14.133 permite a Estados, DF e Municípios, sem recurso da União, usar outros sistemas de custos do próprio ente.

## 5. Jurisprudência de apoio (ementas em 07/10/2026; **leia o acórdão inteiro antes de citar**)

| Acórdão | Tema (pela ementa) |
|---|---|
| 2816/2014 – Plenário | Necessidade de aperfeiçoar a metodologia de pesquisas de preços que embasam a orçamentação |
| 1231/2018 – Plenário | Cotação restrita a potenciais fornecedores; sobrepreço; anulação do pregão |
| 1544/2023 – Plenário | Falhas na definição do orçamento estimativo; superestimativa do preço de referência |

Ideia que se repete na jurisprudência (confirmar no inteiro teor): **cotação só com fornecedores é frágil**; preços de contratações públicas homologadas são a base
mais robusta. Isso reforça a prioridade dos incisos I e II do art. 5º da IN.
