# Qualidade dos dados do PNCP / Compras.gov — o que olhar antes de aceitar um preço

Os dados são preenchidos pelos próprios órgãos: o erro de digitação e a unidade errada são comuns. Cada alerta abaixo aparece (quando detectável)
na coluna `alertas` gerada por `buscar_precos.py`. Alerta **não** significa descartar; significa **olhar** e decidir com critério registrado.

| # | Problema | Como aparece | O que fazer |
|---|---|---|---|
| 1 | **Preço unitário × global (de lote/grupo)** | Descrição começa com "LOTE"/"GRUPO"; preço 0; preço muito maior que o resto | Rota B: preço do item de lote pode ser o valor global. Exclua, ou use só itens com `valorUnitarioHomologado` coerente com `valorTotalHomologado / quantidadeHomologada` |
| 2 | **Unidade de medida divergente** | Mesmo CATMAT com `EMB` (500), `FL` (folha), `UN`; preços de R$ 0,05 a R$ 96 mil na mesma série | O script marca quem difere da unidade predominante. Converta (preço por embalagem ÷ capacidade) ou exclua. Nunca misture resma e folha |
| 3 | **Capacidade da embalagem** | `capacidadeUnidadeFornecimento` > 1 (ex.: 500) | A série homogênea (todos EMB/500) é comparável; um EMB/100 no meio não é |
| 4 | **Unidade com quantidade embutida** | Rota B: `unidadeMedida` = "Embalagem 1.0 KG"; ou "GRAMA 0,00" | Limpar o sufixo numérico (`\s+0[,.]00\s*$`) e ler a quantidade da embalagem na descrição |
| 5 | **Quantidade 0 ou 1** | Quantidade irrelevante | Pode ser item simbólico, lance ou item de teste. Use `--qtd-min` para ficar com volumes comparáveis |
| 6 | **Escala de quantidade** | Compra de 5 unidades × compra de 38.000 | Preço de grande volume tende a ser menor (art. 23 caput: economia de escala). Compare faixas parecidas ao que você vai comprar |
| 7 | **Desconto em vez de preço** | Critério "maior desconto"; `percentualMaiorDesconto` > 0 | O unitário pode ser a referência (tabela) e não o pago. Exclua ou calcule o valor final |
| 8 | **Registro de preços (SRP)** | `forma = SISRP` | É preço de ata (promessa), não compra efetivada. A lei aceita SRP como contratação similar (art. 23 § 1º II), mas registre isso |
| 9 | **Item cancelado, fracassado, deserto, anulado** | Rota B: `situacaoCompraItemNome` ≠ Homologado; resultado com `dataCancelamento` | Só use itens **homologados/adjudicados** com resultado vigente. A rota A só traz resultados, mas confira |
| 10 | **Resultado "Informado" sem homologar** | `situacaoCompraItemResultadoNome` = Informado | Ainda não consolidado; o preço pode mudar. Prefira homologados quando houver amostra suficiente |
| 11 | **Pregão parcialmente homologado** | Alguns itens com resultado, outros não | Normal. Trate item a item |
| 12 | **`temResultado` nulo** | Item homologado com `temResultado = null` | Considere vencedor se há CNPJ do fornecedor **e** situação "homologado/adjudicado" |
| 13 | **Defasagem entre sistemas** | Dados Abertos "Em andamento" com itens já homologados no PNCP | Para situação atual, consulte o PNCP em tempo real (B2) |
| 14 | **Sem número de controle PNCP** | `link_pncp` vazio | Compra de regime anterior ou fora do PNCP. Fonte difícil de comprovar: exclua ou anexe outro comprovante |
| 15 | **Duplicatas** | Mesmo item aparece 2× (itens agrupados, republicação) | `calcular_precos.py` remove duplicata exata (compra+item+fornecedor+preço). Duplicata "quase igual" (mesmo órgão e fornecedor, preços ligeiramente diferentes) exige olho |
| 16 | **Um órgão domina a amostra** | Muitos registros do mesmo órgão/fornecedor | Considere um preço por órgão (mediana por órgão) para não pesar uma compra única N vezes |
| 17 | **Especificação mais ampla que o seu objeto** | Descrição do CATMAT genérica | Leia `descricao`/`descricaoDetalhadaItem`; use `--palavras` para fixar o que importa (marca, gramatura, capacidade) |
| 18 | **Data** | `dataResultado` vazia, ou resultado antigo | A janela de 1 ano vale pela data do resultado. Sem data, não dá para comprovar a janela |
| 19 | **Frete, prazo, local, garantia** | Não estão no preço unitário | Art. 4º da IN 65: observar condições comerciais; registre diferenças relevantes na análise crítica |
| 20 | **Preço de ME/EPP, benefício, margem de preferência** | `porteFornecedorNome`, margem de preferência | Pode afetar o preço; observe se o seu certame terá o mesmo benefício |

## Regras práticas

1. **Olhe a distribuição** antes de tirar média: ordene o mapa, veja os extremos, leia a descrição de cada extremo.
2. **Uma unidade só** na série final. Se não der para converter com segurança, exclua e diga no processo.
3. **Valide por amostragem**: abra no PNCP (link do mapa) 3 a 5 registros e confira preço, item e fornecedor. A skill foi validada assim (5 de 5 coincidiram entre
   Compras.gov e PNCP em 07/10/2026), mas isso não dispensa a sua conferência no seu objeto.
4. **Guarde o arquivo bruto** (`.json` de `buscar_precos.py`) junto ao processo: ele prova de onde veio cada número e com que filtros.
5. **Preço que parece ótimo demais** (muito abaixo da mediana) pode ser erro de unidade ou proposta inexequível; **preço altíssimo** pode ser lote ou erro de vírgula. Em ambos os casos o critério de corte deve estar escrito.
