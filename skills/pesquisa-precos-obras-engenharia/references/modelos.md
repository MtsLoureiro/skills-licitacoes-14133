# Modelos e roteiro de uso

## 1. Planilha de quantitativos (entrada do `orcamento.py`)

Modelo CSV (`;` ou `,`; UTF-8). **Os códigos abaixo são só de exemplo da tabela 08/2026; confirme os seus com `sinapi_buscar.py`** (descrição e custo saem na tela).

```csv
item;etapa;fonte;codigo;descricao;unidade;quantidade;custo_unitario;bdi;referencia
1.1;Alvenaria;SINAPI;101159;;;85;;;
1.2;Pisos;SINAPI;87690;;;120;;;
1.3;Pintura;SINAPI;88489;;;340;;;
2.1;Equipamentos;COTACAO;;Bomba centrífuga 5 cv;UN;2;4200,00;12;3 cotações anexas (processo fls. __), mapa de preços em anexo
3.1;Esquadrias;PROPRIA;;Porta especial 90x210;UN;6;980,00;;composição analítica em anexo, insumos SINAPI 08/2026
```
Colunas: `item` · `etapa` · `fonte` (SINAPI padrão; SICRO, PROPRIA, COTACAO, MANUAL) · `codigo` · `descricao`/`unidade` (obrigatórias fora do SINAPI) · `quantidade` · `custo_unitario` (SEM BDI; obrigatório fora do SINAPI, sobrescreve o SINAPI com alerta) · `bdi` (% da linha; vazio = global) · `referencia` · `tipo_sinapi` (`comp`/`insumo`, só em caso de código duplicado).
Aceita também `.xlsx` simples (1ª aba, 1ª linha = cabeçalho).

## 2. Roteiro (do zero ao orçamento)

1. **Projeto** (básico/executivo conforme o regime) e **quantitativos** por serviço, com memória de quantitativos (responsável técnico).
2. **Tabela SINAPI**: `python3 scripts/sinapi_baixar.py` (mês mais recente) — anote o mês de referência.
3. **Achar as composições**: `python3 scripts/sinapi_buscar.py comp "contrapiso espessura 5" --uf DF`; confira descrição, unidade, `%AS`. `--codigo N --analitico` mostra os insumos e confere a soma.
4. **Regime**: decida desonerado ou não e **use o mesmo no BDI** (`bdi-encargos.md`).
5. **BDI**: `python3 scripts/bdi.py --ac ... --iss ... ` (ISS do município; PIS/COFINS do regime; CPRB só se desonerado); confronte com a faixa do TCU para o tipo de obra (conferida por você).
6. **Orçamento**: `python3 scripts/orcamento.py quantitativos.csv --uf DF --regime nao-desonerado --bdi 24.5 --out obra/orc --titulo "Reforma ..."`. Saem planilha (.csv/.xlsx), curva ABC, memória e minuta de justificativa.
7. **Itens fora do SINAPI**: composição própria/cotação com documentos (ver `sicro-e-outras-fontes.md`); infraestrutura de transportes: SICRO manual.
8. **Edital**: critério de aceitabilidade (global, por etapa e unitário nos itens da classe A), regime, data-base, regime de desoneração, BDI discriminado.
9. **Guarde** `quantitativos.csv`, `.orcamento.json`, `.memoria.md` e a base SINAPI usada (mês).

## 3. Estrutura da Planilha Orçamentária (`.orcamento.xlsx`)

| Aba | Conteúdo |
|---|---|
| Orçamento | Item · Etapa · Fonte · Código · Descrição · Un. · Quant. · Custo unit. · BDI% · Preço unit. · Total · Alertas; total geral com fórmulas `ROUND` (recalculam no Excel) |
| Resumo | Data-base, UF, regime, encargos (horista/mensalista), BDI, custo direto, preço global, nº de itens SINAPI × outras fontes |

Anexos que o controle espera: **composição do BDI**, **cronograma físico-financeiro**, **memória de quantitativos**, **composições analíticas** (SINAPI e próprias), **ART/RRT**, cotações, curva ABC.

## 4. Minutas geradas

- `.memoria.md`: parâmetros, resultado, curva ABC, pontos de atenção, checklist antes de assinar.
- `.justificativa.md`: fundamento (art. 23 § 2º; IN 91/2022 se federal), base de custos e data-base, BDI, resultado, critério de aceitabilidade, observações. Campos [ENTRE COLCHETES] são seus.
