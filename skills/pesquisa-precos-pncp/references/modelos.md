# Modelos: Mapa de Preços e Justificativa da Pesquisa de Preços

`gerar_mapa.py` produz os dois já preenchidos com os números. Aqui está a **estrutura**, para quem quiser montar à mão ou adaptar ao modelo do seu órgão.
Preencha os campos [ENTRE COLCHETES]. Estrutura baseada no conteúdo mínimo do art. 3º da IN SEGES/ME 65/2021 (CONFERIR se o seu ente tem modelo próprio).

---

## A. Mapa de Preços (anexo)

**Objeto:** [descrição, CATMAT/CATSER] · **Unidade de fornecimento:** [ex.: resma 500 folhas] · **Data da pesquisa:** [dd/mm/aaaa]

| Nº | Data do resultado | Preço unit. (R$) | Unid. | Qtd. | Fornecedor | Órgão / UF | Modalidade | Nº controle PNCP | Link |
|---|---|---|---|---|---|---|---|---|---|
| 1 | | | | | | | | | |
| … | | | | | | | | | |

| Estatística | Valor (R$) |
|---|---|
| Nº de preços válidos | |
| Média | |
| Mediana | |
| Menor | |
| Maior | |
| Desvio-padrão / CV | |
| **Preço estimado ([método])** | |

**Preços desconsiderados:** tabela à parte, com o motivo de cada um (aba "Excluídos" no `.xlsx`).
**Quantidade total estimada na contratação:** [Q] → **valor total estimado:** Q × preço estimado.

---

## B. Memória de cálculo
Gerada em `.memoria.md`. Conteúdo: parâmetros; funil dos dados (entrada → filtros → duplicatas → corte → válidos); tabela antes/depois do corte; resultado;
pontos de atenção; lista dos registros descartados e motivo. É o que o controle pede para **refazer a conta**.

---

## C. Justificativa da Pesquisa de Preços (texto)

> **1. Objeto.** [descrição].
> **2. Base normativa.** Art. 23 da Lei nº 14.133/2021; [IN SEGES/ME nº 65/2021 / norma do ente].
> **3. Parâmetros e fontes.** Contratações similares da Administração Pública (art. 23, § 1º, II), preços homologados extraídos do PNCP e do Compras.gov.br em [período], com
> link/número de controle de cada preço no Mapa. [Outros parâmetros: ___. Se só um parâmetro: justificativa ___ (IN 65, art. 5º § 1º).]
> **4. Série e saneamento.** [N] registros coletados; filtros: [unidade, especificação, quantidade, região]; duplicatas removidas: [n]; critério de corte: [critério e parâmetros
> — art. 6º § 3º]; [n] preços válidos.
> **5. Método.** [média/mediana/menor] (art. 6º), por [motivo]. Resultado: R$ [valor] por [unidade].
> **6. Análise crítica.** Dispersão (CV = [x%]); diferenças de condições comerciais (prazo, local, quantidade, garantia — art. 4º); alertas de qualidade de dados e como foram tratados.
> **7. Conclusão.** O valor estimado é compatível com o mercado (art. 23, caput).
> [Local], [data]. [Responsável(is) — art. 3º, II]

### Variações de texto

**Quando houver menos de 3 preços (exceção, art. 6º § 5º):**
> A estimativa foi obtida com [n] preços porque [motivo: objeto de baixa demanda / especificação singular / ...]. Foram realizadas as seguintes tentativas de ampliar a amostra: [janela, região,
> CATMAT vizinhos, pesquisa direta com fornecedores consultados: ___]. Submete-se a justificativa à autoridade competente para aprovação.

**Quando usar apenas um parâmetro (art. 5º § 1º):**
> Utilizou-se unicamente o parâmetro [__] porque [os parâmetros prioritários (incisos I e II) não retornaram preços comparáveis / a especificação não é encontrada em contratações públicas / ...].

**Quando a série tem mistura de modalidades ou SRP:**
> Foram consideradas contratações em pregão eletrônico, dispensa e registro de preços; os preços de ata são considerados por constituírem preço ofertado e homologado em certame competitivo (art. 23 § 1º, II, admite registro de preços).

**Uso de fator de atualização:**
> Os preços foram atualizados por [índice oficial] do mês da homologação ao mês da pesquisa, fator [x,xxxx], conforme IN 65, art. 5º, II e § 3º.
