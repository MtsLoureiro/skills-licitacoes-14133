# SICRO, tabelas estaduais, PNCP/Compras.gov e demais fontes para obras

## 1. SICRO (DNIT) — infraestrutura de transportes

- **Quando usar:** serviços e obras de **infraestrutura de transportes** (rodovias, ferrovias, hidrovias, portos...), art. 23 § 2º, I, da Lei 14.133 e art. 4º do Decreto 7.983/2013. Para edificações e saneamento, o SINAPI.
- **Quem mantém:** DNIT. Custos por **região** do país (Sul, Sudeste, Centro-Oeste, Norte, Nordeste; tabelas por estado), atualização **trimestral** na prática (informação de busca; **CONFERIR** a periodicidade atual).
- **Onde (testado em 07/10/2026):** página `https://www.gov.br/dnit/pt-br/assuntos/planejamento-e-pesquisa/custos-referenciais/sistemas-de-custos/sicro` responde 200, mas os **arquivos não aparecem no HTML estático** (a navegação por região/ano é carregada dinamicamente em subpáginas), e os endereços de subpágina que testei devolveram 404 (a árvore de URLs do gov.br muda). Também há informativos (`.../sicro/informativos/informativo-sicro-no-NN-AAAA.pdf`).
  **Conclusão honesta: não consegui um download automatizável e estável do SICRO.** Baixe pelo navegador (relatórios sintéticos/analíticos por estado e mês, em xlsx) e use no orçamento por **entrada manual**: `fonte=SICRO` com `custo_unitario` e `referencia` "SICRO <UF/região> <mês> <regime>".
- **Particularidades do SICRO** (CONFERIR no manual do DNIT): composições com equipamentos (custo produtivo e improdutivo), **BDI próprio do DNIT** (o TCU discute faixas diferentes para obras rodoviárias), **administração local e canteiro** fora do BDI nas versões atuais (alinhado à determinação do Ac. 2622/2013), ISS, **DMT** (distância média de transporte) como parâmetro do orçamento.
- O script não tem leitor SICRO. Para trazer valores: planilha de quantitativos com `fonte=SICRO` (ou `MANUAL`), o `orcamento.py` calcula BDI, totais, ABC e memória igualmente.

## 2. Tabelas de referência estaduais e municipais

- **Quando:** Estado/DF/Município **sem recursos da União** pode adotar sistema de custos do próprio ente (art. 23 § 3º). Com recursos federais, vale o § 2º (SINAPI/SICRO), salvo regra do concedente.
- Exemplos de tabelas públicas (verifique a edição vigente no site do órgão; **CONFERIR**): secretarias de obras/infraestrutura estaduais, DERs (departamentos de estradas de rodagem) — por exemplo o DER-RO publica tabela referencial de preços regionais de obras rodoviárias em PDF, com edições periódicas.
- Cuidados: data-base, desoneração, BDI embutido ou não, **código/descrição não coincidem com o SINAPI**, formato PDF (extrair manualmente). Use `fonte=MANUAL` e `referencia`.
- A tabela precisa ser **formalmente adotada** pelo ente e citada no processo.

## 3. Preços de obras no Compras.gov / PNCP — o que existe de verdade

| Fonte | O que dá | Serve para orçamento de obra? |
|---|---|---|
| **Compras.gov (Dados Abertos), pesquisa de preço CATSER** | Há códigos CATSER genéricos de obra (ex.: `1619 OBRAS CIVIS DE CONSTRUCAO PREDIAIS DE EDIFICIOS`, `1414 ... PAVIMENTACAO POLIEDRICA`, `1392 ... PAVIMENTACAO DE CONCRETO`, consulta ao catálogo em 07/10/2026) | **Só como indicador global**: o "preço unitário" desses códigos é o valor da obra inteira (unidade UN), não é comparável |
| **PNCP, itens e resultados** | Obras licitadas por preço global/lote aparecem com valor global homologado; a busca textual acha editais de obra (ex.: "execução de obras de reforma") | **Contratações similares** (art. 23 § 2º, III): útil como **verificação de razoabilidade global** (R$/m² de obra parecida) e para **composições próprias de materiais/equipamentos**, nunca como base de custo unitário de serviço |
| Painel de Preços | Preços de bens e serviços em geral | Não cobre composição de obra |
| Banco de notas fiscais eletrônicas (art. 23 § 2º, IV) | Notas fiscais | Depende de **regulamento**; **CONFERIR** se está operacional para seu órgão |

Para materiais e equipamentos **avulsos** (ex.: um grupo gerador, uma bomba), a ferramenta correta é a skill irmã **`pesquisa-precos-pncp`** (CATMAT + preços homologados), e o resultado entra no orçamento como `fonte=COTACAO`/`PROPRIA` com a referência do mapa de preços.
Obras e serviços de engenharia ficam **fora** do escopo daquela skill; os **equipamentos fornecidos** (bens) podem ser pesquisados lá.

## 4. Quando usar cotação de mercado em engenharia

Só quando **não há** composição no SINAPI/SICRO (ou tabela do ente) para o serviço ou insumo, ou quando a cotação local demonstrar vantagem (Decreto 7.983/2013, arts. 6º e 8º, texto a CONFERIR):
1. Tente primeiro a **composição analítica própria** montada com **insumos do SINAPI** (coeficientes de produtividade com fonte).
2. Se for insumo ausente: ≥ 3 cotações formais (sugestão; **CONFERIR** a regra do seu ente), mesma especificação, mesma data, justificativa da escolha dos fornecedores.
3. Registre no campo `referencia` e anexe os documentos. O `orcamento.py` alerta toda linha não-SINAPI sem referência.

## 5. Composições próprias

- Estrutura: serviço, unidade, **insumos (mão de obra, materiais, equipamentos)**, **coeficientes** (consumo/produtividade, com fonte: manual técnico, TCPO/outra publicação, medição em campo), **preços unitários** de cada insumo com data-base e fonte, encargos aplicados à mão de obra no mesmo regime do restante do orçamento, perdas.
- Precisa de responsável técnico (ART/RRT). Compare com serviço similar do SINAPI (ordem de grandeza).
- O script trata a composição própria já calculada como `custo_unitario` (custo direto, sem BDI). Anexe a planilha analítica no processo.
