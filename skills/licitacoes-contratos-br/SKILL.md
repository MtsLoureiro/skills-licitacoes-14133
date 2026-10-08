---
name: licitacoes-contratos-br
description: "Use ao planejar, instruir ou gerir contratações públicas sob a Lei 14.133/2021: ETP, TR, edital, dispensa/inexigibilidade, SRP, contratos, aditivos (25%/50%), fiscalização e sanções. Aciona com 'licitação', 'contrato', 'termo aditivo', 'ETP', 'TR', 'dispensa', 'inexigibilidade', 'SRP'."
---

# Guia Operacional de Licitações e Contratos Administrativos (Lei nº 14.133/2021)

Esta skill consolida o conhecimento normativo, jurisprudencial e operacional para planejar, instruir, licitar, contratar, aditar e fiscalizar contratações públicas no Brasil sob o regime da Lei Geral de Licitações e Contratos Administrativos (Lei nº 14.133/2021).

O conteúdo foi estruturado para ser reutilizável por qualquer órgão ou entidade da Administração Pública direta, autárquica e fundacional de qualquer esfera federativa (Federal, Estadual, Distrital ou Municipal).

---

## Parâmetros do Órgão (Preencher para Reuso)

Antes de iniciar a instrução processual ou redação de minutas, configure as variáveis do órgão:

| Parâmetro | Valor no Órgão / Entidade |
|---|---|
| Nome do Órgão / Entidade | `[Nome Completo do Órgão / Entidade]` |
| Órgão Superior / Vinculação | `[Ministério / Secretaria de Estado ou Município]` |
| CNPJ do Órgão | `[00.000.000/0000-00]` |
| Código da Unidade Gestora / UASG no PNCP | `[Código da Unidade Compradora no PNCP / Compras.gov.br]` |
| Esfera Federativa | `[Federal / Estadual / Distrital / Municipal]` |
| Órgão de Controle Externo Competente | `[Tribunal de Contas da União (TCU) / TCE / TCM]` |
| Sistema Oficial de Compras Eletrônicas | `[Compras.gov.br / Sistema Próprio / Outro Portal]` |

---

## Mapa do Ciclo de Contratação e Índice "Quando Abrir o Quê"

Para executar cada etapa com o máximo de precisão técnica, consulte os arquivos de referência (`references/`) e listas de checagem (`checklists/`):

| Etapa do Ciclo | O que você precisa fazer | Arquivo de Referência | Checklist Operacional |
|---|---|---|---|
| **01. Governança & Agentes** | Compreender o fluxo geral, papéis (agente de contratação, comissão, gestor, fiscais) e segregação de funções. | `references/01_ciclo_e_governanca.md` | — |
| **02. Fase Preparatória** | Elaborar DFD, alinhamento ao PCA, ETP (13 incisos), Matriz de Riscos, Termo de Referência ou Projeto Básico. | `references/02_planejamento_etp_tr_riscos.md` | `checklists/01_checklist_fase_preparatoria.md` |
| **03. Pesquisa de Preços** | Metodologia estatística, busca de contratações similares no PNCP, saneamento de outliers e mapa comparativo. | *(Skill irmã: `pesquisa-precos-pncp`)* | — |
| **04. Modalidade & Disputa** | Escolher entre Pregão (art. 29), Concorrência, Concurso, Leilão ou Diálogo Competitivo e fixar critério de julgamento (art. 33) e modo de disputa (art. 56). | `references/03_modalidades_e_criterios.md` | `checklists/02_checklist_edital_e_minutas.md` |
| **05. Contratação Direta** | Instruir processo de Inexigibilidade (art. 74) ou Dispensa (art. 75), com justificativa de preço e rito do art. 72. *(CONFERIR teto anual)*. | `references/04_contratacao_direta.md` | `checklists/03_checklist_contratacao_direta.md` |
| **06. Sistema de Registro de Preços** | Conduzir IRP, gerenciar ata, processar adesão de órgão não participante ("carona" - limites 50%/2x) e renegociar preços. | `references/05_srp_e_atas.md` | `checklists/06_checklist_adesao_ata_carona.md` |
| **07. Contratos & Aditivos** | Redigir cláusulas (art. 92), garantias, prorrogações (até 10 anos), aditivos de 25%/50% (cálculo isolado), reajuste e repactuação. | `references/06_contratos_e_aditivos.md` | `checklists/04_checklist_termo_aditivo_acrescimo_supressao.md`<br>`checklists/05_checklist_termo_aditivo_prorrogacao_vigencia.md` |
| **08. Gestão & Fiscalização** | Fiscalização técnica/administrativa (DEMO, encargos, conta vinculada), IMR, atesto, recebimento provisório/definitivo e ordem cronológica. | `references/07_gestao_e_fiscalizacao.md` | `checklists/07_checklist_fiscalizacao_e_recebimento.md` |
| **09. Sanções & Extinção** | Conduzir rescisão unilateral/consensual, processo sancionador (art. 158), impedimento/inidoneidade e recursos (arts. 165-168). | `references/08_sancoes_recursos_extincao.md` | — |
| **10. Jurisprudência TCU** | Consultar acórdãos balizadores (cálculo isolado de aditivos, BDI, ETP, vedação ao jogo de planilha, pesquisa de preços). | `references/09_jurisprudencia_tcu.md` | — |
| **11. Transição 8.666 → 14.133** | Mapeamento comparativo artigo a artigo e substituição de comandos em minutas e contratos legados. | `references/10_mapeamento_8666_para_14133.md` | — |
| **12. Lições & Armadilhas** | Evitar erros recorrentes (extenso vs numeral, prazos de execução vs vigência, empenho de reforço vs reclassificação). | `references/11_licoes_aprendidas_e_armadilhas.md` | — |
| **13. Glossário & Siglas** | Dicionário de termos técnicos e relação completa de siglas utilizadas nas contratações públicas. | `references/12_glossario_e_siglas.md` | — |
| **14. Valores Atualizados** | Tetos de dispensa, contrato verbal, grande vulto etc. (Decreto vigente; muda todo 1º de janeiro). | `references/13_valores_atualizados.md` | — |

---

## Princípios Operacionais Inegociáveis

1. **Vedação ao Jogo de Planilha (art. 128)**: Em qualquer aditamento contratual, a vantagem percentual (desconto global) obtida na licitação original em favor da Administração deve ser preservada. É expressamente proibido suprimir itens com grande desconto e acrescer itens com preços elevados.
2. **Regra do Cálculo Isolado de Aditivos (Decisão TCU 215/1999-Plenário c/c art. 125)**: Acréscimos e supressões contratuais devem ser calculados isoladamente em valores absolutos sobre o valor inicial atualizado do contrato. É nula a compensação mútua de quantitativos para burlar os limites de 25% (ou 50% em reformas).
3. **Publicidade Obrigatória no PNCP (art. 94 e art. 174)**: A divulgação no Portal Nacional de Contratações Públicas é requisito essencial de validade e eficácia jurídica de editais, contratos, aditivos e atos de contratação direta.
4. **Veracidade Orçamentária**: Nunca declarar disponibilidade orçamentária que não esteja concretamente suportada por dotação ativa e empenho prévio emitido ou expressamente condicionado nos autos.
5. **Adoção de Modelos Padronizados**: Utilizar preferencialmente as minutas padronizadas da Advocacia-Geral da União (AGU) ou do órgão central competente (art. 19, IV), justificando expressamente nos autos eventuais alterações de cláusulas obrigatórias.
