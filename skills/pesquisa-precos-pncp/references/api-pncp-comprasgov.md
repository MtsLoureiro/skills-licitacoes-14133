# APIs públicas usadas (sem chave) — testadas com chamadas reais em 07/10/2026

Tudo abaixo foi chamado de verdade antes de entrar aqui. Se algo mudar, o `swagger` de cada API é a fonte:
`https://dadosabertos.compras.gov.br/v3/api-docs` e `https://pncp.gov.br/api/consulta/v3/api-docs`.

**Regras gerais**
- Header `User-Agent` de navegador **em todas** as chamadas. A busca textual do PNCP derruba a conexão em silêncio sem ele (parece "site fora do ar").
- **Rate limit**: rajada com muitas threads gera **HTTP 429**. Use ≤ 3 chamadas simultâneas, pausa de ~0,25 s e espere/repita no 429 (os scripts já fazem).
- A API do Compras.gov **ignora filtros de texto** do catálogo (`nomePdm`, `descricaoItem`): devolve tudo ou nada. Filtre localmente (`catalogo.py`).
- Datas: Compras.gov usa `AAAA-MM-DD`; a API de consulta do PNCP usa `AAAAMMDD`.

## A. Dados Abertos Compras.gov.br — `https://dadosabertos.compras.gov.br`

### A1. Preços praticados (a rota principal da skill)

```
GET /modulo-pesquisa-preco/1_consultarMaterial      (CATMAT)
GET /modulo-pesquisa-preco/3_consultarServico       (CATSER)
```
Parâmetros de `1_consultarMaterial`: `tipo` (**obrigatório**: `codigoItemCatalogo` ou `codigoPdm`), `codigo` (**obrigatório**),
`pagina`, `tamanhoPagina` (10 a 500), `codigoUasg`, `estado` (UF), `codigoMunicipio`, `dataResultado`, `codigoClasse`, `poder`, `esfera`
(F/E/M), `idCompra`, `dataCompraInicio`, `dataCompraFim` (`AAAA-MM-DD`).
`3_consultarServico`: `codigoItemCatalogo` **obrigatório** (sem `tipo`/`codigo`) e os mesmos filtros de data/local.
Há variantes `…Detalhe` (2 e 4) e `…_CSV` (1.1 a 4.1).

Resposta: `{resultado:[...], totalRegistros, totalPaginas, paginasRestantes}`. Campos úteis de cada item:
`idCompra`, `idItemCompra`, `numeroItemCompra`, `dataCompra`, `dataResultado`, `forma` (SISPP = preço/pregão; SISRP = registro de preços),
`modalidade` (código), `criterioJulgamento`, `precoUnitario` (**preço unitário homologado**), `quantidade`, `percentualMaiorDesconto`,
`niFornecedor`, `nomeFornecedor`, `marca`, `siglaUnidadeFornecimento`, `nomeUnidadeFornecimento`, `capacidadeUnidadeFornecimento`,
`siglaUnidadeMedida`, `codigoUasg`, `nomeUasg`, `nomeOrgao`, `estado`, `municipio`, `esfera`, `poder`, `objetoCompra`, `descricaoDetalhadaItem`, `codigoPdm`.

Pegadinhas:
- O filtro `dataCompraInicio/Fim` funciona no servidor, mas **confira também no cliente**: sem ele a API devolve histórico longo (uma consulta de papel A4 devolveu 95 linhas; só 23 estavam em 12 meses).
- `estado=DF` pode devolver 0 mesmo havendo mercado: UF é a do **órgão comprador**, e a amostra pode ser pequena. Teste sem filtro de UF.
- `capacidadeUnidadeFornecimento` > 1 indica **embalagem** (ex.: EMB com 50): o preço pode ser por embalagem ou por unidade. Veja `qualidade-dados.md`.
- Resposta sem link PNCP: a linha só traz `idCompra`. Use A3 para obter o número de controle.

### A2. Catálogo (para achar CATMAT/CATSER)
```
GET /modulo-material/3_consultarPdmMaterial      pagina, tamanhoPagina(10-500)  -> ~20 mil PDM (padrão descritivo)
GET /modulo-material/4_consultarItemMaterial     codigoPdm | codigoClasse | codigoGrupo | codigoItem ...  -> itens CATMAT (campo descricaoItem, statusItem)
GET /modulo-material/2_consultarClasseMaterial   /1_consultarGrupoMaterial
GET /modulo-servico/6_consultarItemServico       tamanhoPagina, codigoClasse... -> ~3 mil serviços (nomeServico, codigoServico)
```
Os endpoints de serviço `3_consultarItemServico` etc. **não existem** (404): o de itens é o `6_`.
`tamanhoPagina` acima de 500 dá erro 400 ("deve ser no máximo 500"); abaixo de 10 também.

### A3. Ligar `idCompra` ao PNCP
```
GET /modulo-contratacoes/1.1_consultarContratacoes_PNCP_14133_Id?tipo=idCompra&codigo=<idCompra>
```
Devolve `numeroControlePNCP` (`{cnpj}-1-{sequencial6}/{ano}`), `orgaoEntidadeCnpj`, `anoCompraPncp`, `sequencialCompraPncp`, modalidade, objeto.
**Link público**: `https://pncp.gov.br/app/editais/{cnpj}/{ano}/{sequencial}` (sequencial sem zeros à esquerda). Compra anterior à Lei 14.133 ou fora do PNCP pode voltar vazia → marcar "sem link".
Outros: `1_consultarContratacoes_PNCP_14133` (por UASG/CNPJ/modalidade/data), `2_consultarItensContratacoes_PNCP_14133` (itens; filtros `codItemCatalogo`, `codigoPdm`, `temResultado`),
`3_consultarResultadoItensContratacoes_PNCP_14133` (resultados; filtros de valor unitário homologado).
Atraso: esses módulos de contratações **atrasam em relação ao PNCP** (horas a dias). Para situação atual e vencedor, use a B.

## B. PNCP — `https://pncp.gov.br`

### B1. Busca textual (descobrir compras por objeto)
```
GET /api/search/?q=<texto>&tipos_documento=edital&status=todos&pagina=1&tam_pagina=50&ordenacao=-data
```
Resposta `{items:[...], total}`. Campos: `numero_controle_pncp`, `orgao_cnpj`, `orgao_nome`, `unidade_codigo`, `esfera_nome`, `uf`, `municipio_nome`,
`modalidade_licitacao_nome`, `situacao_nome`, `tem_resultado`, `data_publicacao_pncp`, `valor_global`, `description` (objeto), `item_url`.
`tipos_documento=item` retornou vazio; a busca é por **edital/ata**, não por item. Filtrar por `orgaos=` direto funciona mal: busque pelo texto e filtre no resultado.
Exige User-Agent de navegador.

### B2. Itens e resultados de uma compra (tempo real)
```
GET /api/pncp/v1/orgaos/{cnpj}/compras/{ano}/{sequencial}/itens?pagina=1&tamanhoPagina=500
GET /api/pncp/v1/orgaos/{cnpj}/compras/{ano}/{sequencial}/itens/{numeroItem}/resultados
GET /api/consulta/v1/orgaos/{cnpj}/compras/{ano}/{sequencial}          (cabeçalho: valorTotalEstimado, valorTotalHomologado, linkSistemaOrigem)
```
Item: `numeroItem`, `descricao`, `unidadeMedida` (às vezes com sufixo de quantidade, ex. "Embalagem 1.0 KG"), `quantidade`, `valorUnitarioEstimado`, `valorTotal`,
`situacaoCompraItemNome` (Homologado, Fracassado, Cancelado...), `temResultado`, `criterioJulgamentoNome`.
Resultado: `valorUnitarioHomologado`, `quantidadeHomologada`, `valorTotalHomologado`, `niFornecedor`, `nomeRazaoSocialFornecedor`, `porteFornecedorNome` (ME/EPP...),
`percentualDesconto`, `dataResultado`, `dataCancelamento`, `situacaoCompraItemResultadoNome`.
A lista de itens é um **array direto** (sem envelope); pare a paginação quando vier vazia ou com menos de `tamanhoPagina`.

### B3. Listas por período (`/api/consulta/v1`)
```
GET /api/consulta/v1/contratacoes/publicacao  dataInicial, dataFinal, codigoModalidadeContratacao (obrigatórios), uf, cnpj, pagina (obrig.), tamanhoPagina (10-50)
GET /api/consulta/v1/atas                      dataInicial, dataFinal (obrig.), cnpj, pagina, tamanhoPagina (10-500)
GET /api/consulta/v1/contratos                 dataInicial, dataFinal (obrig.), cnpjOrgao, pagina, tamanhoPagina (10-500)
```
Resposta com envelope `{data:[...], totalRegistros, totalPaginas}`. Úteis para varrer atas/contratos de um período, mas **não filtram por objeto**: para preço de um item, prefira A1.
`/api/consulta/v1/contratacoes/publicacao` limita a 50 por página (o `tamanhoPagina` 500 de outros endpoints não vale aqui).

### B4. Modalidades (`codigoModalidade` do Compras.gov / `codigoModalidadeContratacao` do PNCP)
Compras.gov: 3 Concorrência eletrônica · 4 Concorrência presencial · 5 Pregão eletrônico · 6 Dispensa · 7 Inexigibilidade (demais códigos: CONFERIR no swagger).
Atenção: o PNCP usa **outra numeração** em `modalidadeIdPncp` (ex.: pregão eletrônico = 6 no PNCP, 5 no Compras.gov). Não misture.
