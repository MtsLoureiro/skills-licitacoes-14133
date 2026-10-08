# SINAPI: de onde baixar, como é a planilha, armadilhas (testado com o arquivo real de 08/2026)

SINAPI = Sistema Nacional de Pesquisa de Custos e Índices da Construção Civil. Preços de insumos pesquisados pelo IBGE; composições e
metodologia mantidas pela Caixa. Para orçamento de obras (exceto infraestrutura de transportes) é a referência do art. 23 § 2º, I, da Lei 14.133.

## 1. Onde obter

| Item | Fato testado em 07/10/2026 |
|---|---|
| Página oficial | `https://www.caixa.gov.br/sinapi` (Caixa → Poder Público → Modernização e Gestão → SINAPI). A lista de downloads é montada por **JavaScript**: não dá para "raspar" os links; use o padrão de URL abaixo |
| **URL do ZIP mensal** | `https://www.caixa.gov.br/Downloads/sinapi-relatorios-mensais/SINAPI-AAAA-MM-formato-xlsx.zip` (também existe `...-formato-pdf.zip`). **UM zip por mês com TODAS as UFs** (~16 MB) |
| Mês publicado | 08/2026: ZIP válido de 15,8 MB (relatório emitido em 11/09/2026). 09/2026 e 10/2026: **não publicados** em 07/10/2026. A tabela de um mês sai, em geral, no mês seguinte |
| Mês inexistente | A Caixa responde com **laço de redirecionamento 302** (curl) ou **HTTP 200 com HTML** (outros casos). **Nunca confie no status**: valide os 2 primeiros bytes `PK` e o tamanho. `sinapi_baixar.py` já faz isso e caminha para trás até achar o mês |
| Cookies/UA | Sem `User-Agent` de navegador e cookie (`security=true`) o servidor entra em laço de 302. `requests.Session` com UA de navegador resolve |
| **Formato antigo por UF** | `.../sinapi-a-partir-jul-2009-df/SINAPI_ref_Insumos_Composicoes_DF_AAAAMM_Desonerado.zip` → **404** (formato morto; não use) |
| Nomes dentro do ZIP | 4 xlsx: `SINAPI_Referência_AAAA_MM.xlsx` (a principal, 13,5 MB), `SINAPI_familias_e_coeficientes`, `SINAPI_mao_de_obra`, `SINAPI_Manutenções`. Os nomes têm acento em UTF-8 sem flag: `unzip` do sistema os estraga; `zipfile` do Python lê (o script extrai com nome ASCII) |
| Outros arquivos úteis na página | Metodologia (`Livro_SINAPI_Metodologias_Conceitos.pdf`, `Livro_SINAPI_Calculos_Parametros.pdf`), notas/encargos (`Notas_SINAPI.pdf`), fichas de especificação técnica de insumos |
| Fallback manual | Baixe pelo navegador e rode `sinapi_baixar.py --arquivo <zip|xlsx> --mes AAAA-MM` |

## 2. Estrutura da planilha "Referência" (10 abas)

| Aba | Conteúdo | Layout |
|---|---|---|
| Menu, Busca | Navegação; busca por fórmulas modernas do Excel (FILTRO/LAMBDA): **não serve para script** | — |
| **ISD** | Insumos, **sem desoneração** (encargos sociais com INSS patronal) | Cabeçalho até a linha 10; **1 coluna de preço por UF** a partir da col. F; col. E = origem do preço (C coletado, CR coeficiente de representatividade, AS atribuído de SP) |
| **ICD** | Insumos, **com desoneração** | idem |
| **ISE** | Insumos, **sem encargos sociais** | idem |
| **CSD / CCD / CSE** | **Composições** (custo unitário) sem desoneração / com desoneração / sem encargos | **Pares de colunas por UF**: `Custo (R$)` e `%AS`, a partir da col. E; col. A grupo, B código, C descrição, D unidade |
| **Analítico** | Estrutura das composições: composição → itens (INSUMO ou COMPOSICAO), **coeficiente**, situação | Linha-cabeçalho da composição (sem tipo de item) seguida das linhas de itens |
| Analítico com Custo | Planilha interativa (você digita UF e código, ela calcula por fórmula) | **Não use**: os valores são fórmulas de Excel |

Cabeçalho (linhas 3 a 9): mês de referência, data de emissão, regime, localidade (nome da capital de cada UF), e **encargos sociais horista e mensalista por UF**
(ex.: DF, não desonerado, 08/2026: horista 110,08%, mensalista 69,94%). 27 UFs. Valores numéricos com ponto decimal no XML.

## 3. Armadilhas (todas encontradas na prática)

1. **Código da composição é fórmula.** Nas abas CSD/CCD/CSE a coluna B é `HYPERLINK("#"&CELL("address",OFFSET(Analítico!$B$1,MATCH(104658,Analítico!$B:$B,0)-1,3)),104658)` com **valor em cache 0**.
   Leitor que pega só o valor enxerga todas as composições como "0". O código está dentro da fórmula (`MATCH(<código>,`). Os insumos (ISD/ICD/ISE) têm código numérico normal.
2. **openpyxl não serve para ler.** As abas de composição têm ~23 MB de XML cada; `load_workbook(read_only=True)` não terminou em 115 s. Leitura em fluxo (`zipfile` + `iterparse`) importa as 3 abas de insumos, as 3 de composições e o Analítico em ~9 s (script `_sinapi.py`).
3. **Preço zero ≠ preço baixo.** Composição ou insumo sem pesquisa na UF aparece como **0** (composição) ou em **branco** (insumo). Ex.: 08/2026, DF: a composição 104644 (pintura látex acrílica econômica, aplicação mecânica) tem custo 0,00. O orçamento **recusa** linha sem preço e pede custo informado com fonte.
4. **%AS (porcentagem atribuída de São Paulo).** Quando a UF não tem preço de algum insumo da composição, o SINAPI usa o de SP e informa o percentual do custo que veio de lá. `%AS > 0` = custo parcialmente emprestado: registre/justifique. Exemplo real: alvenaria 103322 no DF com %AS 0,5% (insumo "pino de aço" sem preço no DF).
5. **Soma analítica ≠ custo publicado por pouco.** Recalcular `Σ coeficiente × preço` com os preços da UF reproduz o custo com diferença de centavos (arredondamento); diferença maior sinaliza item sem preço/AS. `sinapi_buscar.py comp --codigo N --analitico` faz a conferência.
6. **Regime importa.** Mesma composição tem custo diferente em desonerado (sem INSS patronal sobre a folha; a contribuição passa a incidir como CPRB sobre a receita, no BDI) e não desonerado. Misturar (custo desonerado com BDI sem CPRB ou o contrário) distorce o preço. Regras da desoneração da folha mudaram por lei; **CONFERIR** a legislação vigente para o seu objeto (ver `bdi-encargos.md`).
7. **Código de insumo e de composição são espaços diferentes.** O mesmo número pode existir nos dois; o orçamento avisa e usa a composição, a menos que a coluna `tipo_sinapi` diga `insumo`.
8. **Descrição muda com a revisão** (sufixo `AF_MM/AAAA` na descrição indica a revisão da composição). Cite sempre código + data-base.
9. **Data-base.** O preço vale para o mês de referência; o edital deve dizer a data-base e o critério de reajuste. Uso de tabela desatualizada deve ser justificado (CONFERIR prazo exigido pelo seu órgão ou concedente).
10. **Mediana.** O SINAPI publica **preços medianos** pesquisados. Usar o valor publicado atende "menor ou igual à mediana" do art. 23 § 2º, I (a mediana já é o valor da tabela).
11. **Composições não encontradas.** Se o serviço não existe no SINAPI (ou é de infraestrutura de transportes), use SICRO ou a ordem do § 2º (mídia, similares, notas fiscais) e **justifique**; `orcamento.py` aceita `fonte=PROPRIA|COTACAO|SICRO|MANUAL` com `custo_unitario` e `referencia`.

## 4. Como o skill usa os dados

`sinapi_baixar.py` → baixa/valida o ZIP, extrai a "Referência", importa tudo para **SQLite** (`~/.cache/pesquisa-precos-obras/sinapi-AAAA-MM.sqlite`, ~100 MB, todas as UFs e 3 regimes).
`sinapi_buscar.py` consulta por código ou texto. `orcamento.py` monta a planilha. Mês seguinte: rode `sinapi_baixar.py` de novo (ele detecta o mês novo).
