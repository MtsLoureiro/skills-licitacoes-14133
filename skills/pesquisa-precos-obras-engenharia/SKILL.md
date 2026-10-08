---
name: pesquisa-precos-obras-engenharia
description: "Use ao orçar obra ou serviço de engenharia com SINAPI/SICRO: custo direto, BDI, curva ABC, planilha orçamentária e justificativa. Aciona com 'orçamento de obra', 'SINAPI', 'SICRO', 'BDI', 'planilha orçamentária', 'curva ABC'."
---

# Orçamento de obras e serviços de engenharia (SINAPI / SICRO / BDI)

Monta o **valor estimado** de obra ou serviço de engenharia sob a Lei 14.133/2021 (art. 23, § 2º): baixa a tabela **SINAPI** do mês, busca composições, calcula **custo direto + BDI**, gera
planilha orçamentária (.csv/.xlsx), **curva ABC**, memória de cálculo e minuta de justificativa. Complementa `pesquisa-precos-pncp` (bens e serviços em geral; **aquela skill exclui obras**).
Esta skill **apoia o orçamentista**: quantitativos, escolha das composições, BDI e a assinatura (ART/RRT) são da equipe técnica. Não substitui projeto nem parecer jurídico.

## Parâmetros do órgão (preencha uma vez)
| Campo | Seu valor |
|---|---|
| Ente/esfera e se há **recursos da União** | |
| Norma de orçamento de obras (IN SEGES/ME 91/2022? decreto local?) | |
| UF/localidade da obra | |
| Regime de encargos (desonerado / não desonerado) e base legal | |
| Regime de execução (art. 46) e critério de aceitabilidade do edital | |
| Responsável técnico (ART/RRT) | |

## Requisitos
Python 3.8+ e `requests` (`pip install requests`; só para o download). `openpyxl` opcional (gera `.xlsx`). Sem chave. Cache e SQLite em `~/.cache/pesquisa-precos-obras` (variável `OBRAS_CACHE`).
Scripts em `scripts/` (todos com `--help`). Sem rede o cálculo funciona sobre uma base já baixada ou sobre `--arquivo` local.

## Fluxo (siga a ordem)
1. **Baixar e preparar a tabela** (um ZIP por mês, todas as UFs; ~16 MB; importa em SQLite em ~10 s):
   ```bash
   python3 scripts/sinapi_baixar.py                    # mais recente publicada (caminha para trás do mês corrente)
   python3 scripts/sinapi_baixar.py --mes 2026-08
   python3 scripts/sinapi_baixar.py --arquivo SINAPI-2026-08-formato-xlsx.zip --mes 2026-08   # se já baixou à mão
   ```
2. **Achar composições/insumos** e conferir a estrutura:
   ```bash
   python3 scripts/sinapi_buscar.py comp "contrapiso espessura 5" --uf DF --regime nao-desonerado
   python3 scripts/sinapi_buscar.py comp --codigo 87690 --uf DF --analitico      # insumos, coeficientes e conferência da soma
   python3 scripts/sinapi_buscar.py insumo "cimento portland" --uf DF
   ```
   `%AS > 0` = parte do preço atribuída de SP; **custo 0 = sem preço na UF** (não use).
3. **BDI** (fórmula do TCU; CONFERIR faixas no Ac. 2622/2013-Plenário): `python3 scripts/bdi.py --ac 4 --s 0.8 --r 1 --g 0.8 --df 1.2 --l 7 --pis 0.65 --cofins 3 --iss 3 [--faixa MIN,MAX]`.
   O **regime do BDI (CPRB) tem de casar** com o regime do SINAPI usado.
4. **Orçamento** a partir da planilha de quantitativos (modelo em `references/modelos.md`):
   ```bash
   python3 scripts/orcamento.py quantitativos.csv --uf DF --regime nao-desonerado --bdi 24.5 --titulo "Reforma ..." --out obra/orc
   ```
   Linhas fora do SINAPI (`PROPRIA`, `COTACAO`, `SICRO`, `MANUAL`) exigem `custo_unitario` e `referencia`; `bdi` por linha permite BDI reduzido para materiais/equipamentos (justificar).
   Código inexistente ou sem preço **interrompe** (não inventa valor).
5. **Curva ABC**: já sai do `orcamento.py`; avulsa: `python3 scripts/curva_abc.py obra/orc.orcamento.csv --corte-a 80 --corte-b 95` (cortes = convenção).
6. **Revisar** `.memoria.md` (pontos de atenção) e completar `.justificativa.md`. Definir no edital o **critério de aceitabilidade** (global, por etapa, unitário nos itens da classe A).
7. **Guardar** quantitativos, `.orcamento.json`, memória e o mês do SINAPI usado.

## Regras que não podem ser esquecidas
- Ordem do art. 23 § 2º: **SINAPI/SICRO (≤ mediana, já é o valor publicado)** → mídia/tabela/sítios → contratações similares → notas fiscais. Fora do primeiro, **justifique**.
- **Projeto executivo** antes da licitação (art. 46 § 1º); sem ele o orçamento nasce errado.
- **Administração local, canteiro, mobilização** discriminados na planilha, não escondidos no BDI (determinação do TCU; CONFERIR inteiro teor).
- **ISS** pela alíquota do município; **PIS/COFINS** pelo regime; **CPRB** só no orçamento desonerado.
- Inexequível < 75% do orçado; garantia adicional se < 85% (art. 59 §§ 4º e 5º). Aditivos: 25% / 50% reforma (art. 125).
- Orçamento pode ser sigiloso (art. 24), mas **quantitativos** são públicos.
- **Infraestrutura de transportes → SICRO** (sem download automatizável estável; use entrada manual).

## Limites honestos
- **SICRO**: página do DNIT responde, mas os arquivos não estão no HTML estático; sem leitor automático. Entrada manual (`fonte=SICRO`).
- **Tabelas estaduais/municipais**: PDFs/planilhas heterogêneas; entrada manual com referência.
- **PNCP/Compras.gov** não trazem preço unitário de serviço de obra; servem de sanidade global e para bens/equipamentos (use `pesquisa-precos-pncp`).
- A Caixa muda URLs e o mês corrente quase nunca está publicado; o script valida o conteúdo do ZIP e volta no tempo.

## Quando abrir o quê
| Preciso de | Abrir |
|---|---|
| Artigos da Lei 14.133, Decreto 7.983, IN SEGES/ME 91/2022, quem segue o quê, jurisprudência confirmada | `references/norma-orcamento-obras.md` |
| URL real do SINAPI, formato das abas, armadilhas (código em fórmula, preço 0, %AS, regime) | `references/sinapi-fonte-e-formato.md` |
| SICRO, tabelas estaduais, PNCP/Compras.gov em obras, composições próprias, cotação | `references/sicro-e-outras-fontes.md` |
| BDI (fórmula, componentes, diferenciado), encargos, desoneração, arredondamento | `references/bdi-encargos.md` |
| Regimes de execução, aceitabilidade, sobrepreço, jogo de planilha, curva ABC, sigilo | `references/aceitabilidade-regimes-sobrepreco.md` |
| Modelo de quantitativos, roteiro e anexos esperados | `references/modelos.md` |

## Testes
`python3 tests/test_obras.py` (15 testes offline; gera um XLSX fictício com a mesma estrutura do SINAPI, inclusive o código em fórmula).

## O que ficou como CONFERIR
Vigência atual do Decreto 7.983/2013 e da IN SEGES/ME 91/2022 (nenhuma revogação encontrada até 07/10/2026); faixas e fórmula de BDI do Ac. 2622/2013-Plenário; legislação vigente da desoneração/CPRB;
texto dos arts. 6º e 8º do Decreto 7.983 (citados via Manual do TCU); valores de análise paramétrica do art. 17; periodicidade e URLs do SICRO; norma do seu ente (decreto local, concedente).
