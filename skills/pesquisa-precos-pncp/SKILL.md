---
name: pesquisa-precos-pncp
description: "Use ao fazer pesquisa de preços de contratação pública com preços homologados do PNCP/Compras.gov.br (CATMAT/CATSER, mediana, mapa). Aciona com 'pesquisa de preços', 'preço estimado', 'mapa de preços', 'CATMAT'."
---

# Pesquisa de preços com contratações similares (PNCP / Compras.gov.br)

Monta a pesquisa de preços de bens e serviços em geral a partir de **preços unitários homologados** por outros órgãos, com a fonte de cada preço
(número de controle e link do PNCP), estatística com critério de corte explícito, mapa comparativo, memória de cálculo e minuta de justificativa.

**Base:** Lei 14.133/2021, art. 23 (todos os entes) e, na União, IN SEGES/ME nº 65/2021 (CONFERIR vigência; ver `references/norma-comentada.md`).
Fora da União a IN 65 serve de **referência**: confira a norma do seu ente. **Obras e engenharia** (SINAPI/SICRO) estão **fora do escopo desta skill**: use `pesquisa-precos-obras-engenharia`.
Esta skill apoia a pesquisa; **a decisão, o critério e a assinatura são do agente responsável**. Não envia cotação a ninguém.

## Parâmetros do órgão (preencha uma vez e use no processo)

| Campo | Seu valor |
|---|---|
| Órgão/ente e esfera (federal/estadual/municipal) | |
| Norma de pesquisa de preços aplicável (IN 65? decreto local?) | |
| Janela de preços (padrão 365 dias) | |
| Mínimo de preços (padrão 3) | |
| Método preferido (mediana/média/menor) e critério de corte | |
| Responsável(is) pela pesquisa | |

## Requisitos
Python 3.8+ e `requests` (`pip install requests`). `openpyxl` é opcional (gera `.xlsx`). Sem chave de API. Cache em `~/.cache/pesquisa-precos-pncp` (mude com `PNCP_CACHE`).
Scripts em `scripts/`; todos têm `--help`.

## Fluxo (siga a ordem)

1. **Descrever o objeto** com especificação suficiente para comparar (marca só se justificada, unidade, capacidade, gramatura...).
2. **Achar o código de catálogo** (CATMAT = material, CATSER = serviço):
   ```bash
   python3 scripts/catalogo.py pdm "papel impressao formatado"         # PDM = padrão descritivo
   python3 scripts/catalogo.py itens --pdm 19746 --filtro "297 210 75 sulfite branco"
   python3 scripts/catalogo.py servico "microfilmagem"                 # CATSER
   ```
   A API ignora filtro de texto; o script baixa o catálogo uma vez e busca localmente. Escolha o(s) código(s) que representam exatamente o seu objeto.
3. **Coletar preços homologados** (janela de 1 ano por padrão):
   ```bash
   python3 scripts/buscar_precos.py --catmat 461819 461821 --dias 365 --out pesquisa/papel
   python3 scripts/buscar_precos.py --catser 15083 --uf DF --out pesquisa/servico
   python3 scripts/buscar_precos.py --texto "notebook 16gb" --palavras "notebook,16gb" --excluir-palavras "fonte,bateria,lote" --max-compras 30 --out pesquisa/nb  # sem código de catálogo
   ```
   Gera `.json` (guarde no processo) e `.csv`. Mostra a **unidade predominante** e quantos registros têm link PNCP. A coleta de links é lenta (≈ 1 chamada por compra; respeita o limite da API).
4. **Revisar o bruto** (abra o `.csv`): unidades, quantidades, extremos, alertas. Leia `references/qualidade-dados.md`.
5. **Calcular** com critério explícito (funciona offline sobre o arquivo):
   ```bash
   python3 scripts/calcular_precos.py pesquisa/papel.json --metodo mediana --outliers iqr --k 1.5 \
       --qtd-min 10 --excluir-alerta difere --out pesquisa/papel
   ```
   Critérios de corte: `iqr`, `mad`, `faixa-mediana`, `nenhum`. Avisa se há < 3 preços, CV alto ou muitos alertas. Detalhes em `references/saneamento-e-casos-limite.md`.
6. **Gerar os documentos**:
   ```bash
   python3 scripts/gerar_mapa.py pesquisa/papel.calculo.json --titulo "Papel A4 75 g, resma 500 fls" --out pesquisa/papel
   ```
   Saem `.mapa.csv`, `.mapa.xlsx`, `.memoria.md` e `.justificativa.md` (minuta com [CAMPOS] a preencher). Estrutura em `references/modelos.md`.
7. **Conferir por amostragem**: abra 3 a 5 links do mapa no PNCP e confira item, preço e fornecedor.
8. **Complementar** com outros parâmetros do art. 5º da IN 65 quando necessário (pesquisa direta ≥ 3 fornecedores, mídia com data/hora, notas fiscais) e **justificar** se usar só um.

## Regras que não podem ser esquecidas
- Prioridade (IN 65, art. 5º § 1º): painel/banco de preços (I) e contratações similares (II); outro parâmetro exige justificativa.
- **3 ou mais preços** válidos; menos só com justificativa e aprovação (art. 6º § 5º).
- Critério de corte de valores inexequíveis/inconsistentes/excessivamente elevados **escrito no processo** (art. 6º § 3º). Não há percentual fixo na norma.
- Janela: resultados de **até 1 ano** antes da pesquisa (art. 23 § 1º, II); mais antigo só com justificativa e atualização por índice.
- Mesma **unidade** na série; preço de lote/grupo não é unitário; SRP é preço de ata (registre).
- Guarde o `.json` bruto, o `.calculo.json` e o mapa: permitem refazer a conta.

## Armadilhas das APIs (resumo; completo em `references/api-pncp-comprasgov.md`)
- `User-Agent` de navegador sempre. Muitas chamadas simultâneas → **429**; os scripts usam poucas threads e repetem.
- Filtros de texto do catálogo são ignorados pelo servidor; `tamanhoPagina` entre 10 e 500 (50 em `/contratacoes/publicacao`).
- Compras.gov (rota A) pode atrasar em relação ao PNCP; para vencedor/situação atual use `/api/pncp/v1/.../itens/{n}/resultados`.
- Compra sem número de controle PNCP = fonte difícil de comprovar (alerta).

## Quando abrir o quê
| Preciso de | Abrir |
|---|---|
| Artigos, prazos, exceções, outros entes, jurisprudência | `references/norma-comentada.md` |
| Endpoints, parâmetros, limites, links do PNCP | `references/api-pncp-comprasgov.md` |
| Como descartar preços, item único, inexigibilidade, serviço, TIC, engenharia | `references/saneamento-e-casos-limite.md` |
| Alertas de dados (unidade, lote, SRP, cancelado) | `references/qualidade-dados.md` |
| Estrutura do mapa e da justificativa, variações de texto | `references/modelos.md` |

## Testes
`python3 tests/test_calculo.py` roda offline (fixture com dados fictícios `tests/fixture_precos.json`).

## O que ficou como CONFERIR
Vigência atual da IN 65/2021 e eventual norma substituta; norma local do seu ente; IN que substituiu a IN 5/2017 (mão de obra exclusiva); valores atualizados dos limites de dispensa;
códigos de modalidade fora de 3–7; leitura integral dos acórdãos citados antes de usá-los.
