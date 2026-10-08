# Saneamento da série de preços e casos-limite

## 1. Saneamento: como decidir o que sai da série

A IN SEGES/ME 65/2021 manda desconsiderar valores **inexequíveis, inconsistentes e excessivamente elevados** (arts. 2º, I, e 6º) e exige que o critério seja
**fundamentado e descrito no processo** (art. 6º, § 3º). Ela **não fixa percentual**. Escolha um critério, escreva por quê, aplique igual a todos.

| Critério (`--outliers`) | Regra | Quando usar | Cuidado |
|---|---|---|---|
| `iqr` (padrão) | Fora de [Q1 − k·IQR ; Q3 + k·IQR]; k = 1,5 (usual) ou 3 (só extremos) | Amostra ≥ 8 preços, distribuição razoável | Exige ≥ 4 preços; com poucos dados pode cortar demais |
| `mad` | Escore z modificado > 3,5 (desvio absoluto mediano) | Amostra com muita cauda; robusto | Se mais da metade dos preços for igual, MAD = 0 (não aplica) |
| `faixa-mediana` | Entre 50% e 150% da mediana (ajustável) | Critério simples de explicar a controle externo; amostra pequena | Percentuais são escolha sua: justifique |
| `nenhum` | Sem corte | Poucos preços, todos conferidos um a um | Dispersão alta vira alerta (CV > 25%) |

Sequência recomendada:
1. **Filtros objetivos primeiro** (unidade, especificação, quantidade comparável, região, janela de 1 ano, só homologado). Isto é saneamento de **comparabilidade**, não estatístico.
2. **Duplicatas**.
3. **Corte estatístico** com critério escrito.
4. **Leia os cortados**: um "excessivamente elevado" que é um produto melhor (outra especificação) é problema de filtro, não de outlier.
5. **Método**: `mediana` (padrão da skill; menos sensível), `media` ou `menor` (art. 6º). O **menor** preço isolado é o mais arriscado (pode ser inexequível ou erro).
6. **Mínimo de 3 preços** válidos. Abaixo disso, só com justificativa nos autos e aprovação da autoridade (art. 6º § 5º).
7. **Coeficiente de variação**: acima de ~25% pare e investigue (a skill avisa). Não é norma; é sinal prático.
8. **Atualização**: preço com meses de idade, aplicar índice oficial (`--fator`) e registrar o índice.

Se baseado **somente** no parâmetro I (painel/banco de preços), o valor não pode superar a **mediana** do item (IN 65, art. 6º § 6º): use `--metodo mediana`.

## 2. Casos-limite

### 2.1 Item sem concorrência / poucos preços no PNCP
- Amplie a **janela** só até o que a norma permite (1 ano; fora disso só com justificativa e índice de atualização — IN 65, art. 5º § 3º trata de orçamento fora do prazo).
- Amplie **geograficamente** (todo o Brasil) e **por CATMAT** vizinhos (mesmo PDM, característica adicional diferente), documentando a similaridade.
- Combine **parâmetros** (art. 5º): pesquisa com fornecedores (≥ 3), mídia especializada com data/hora de acesso, notas fiscais.
- Se ainda assim < 3, aplique o art. 6º § 5º: justificativa + aprovação. Descreva as tentativas.

### 2.2 Inexigibilidade e dispensa
- Aplica-se o art. 5º também (IN 65, art. 7º). Se não houver como estimar, **notas fiscais** da futura contratada para outros clientes (até 1 ano) ou outro meio idôneo (Lei 14.133, art. 23 § 4º).
- Se a justificativa de preços mostrar que **há competição**, a inexigibilidade fica vedada (IN 65, art. 7º § 3º).
- Dispensa por valor (art. 75, I e II da Lei 14.133): a pesquisa pode ser feita junto com a seleção da proposta, por solicitação formal de cotações (IN 65, art. 7º § 4º e 5º). **CONFERIR** o valor atualizado do limite (decreto de atualização anual).
- Fornecedor exclusivo: o preço de tabela do fabricante não basta; compare com notas fiscais a outros clientes.

### 2.3 Serviço continuado e mão de obra com dedicação exclusiva
- Serviço continuado **sem** mão de obra exclusiva (manutenção, licenças, locação): a série do PNCP funciona, mas compare **unidade** (mensal, por posto, por m²) e escopo; o CATSER ajuda, o objeto raramente é idêntico.
- **Mão de obra com dedicação exclusiva**: a estimativa vem de **planilha de custos e formação de preços** (convenção coletiva, encargos, insumos), não de média de contratos. A IN 65, art. 9º, remete à IN SEGES nº 5/2017 "ou outra que a substitua" (**CONFERIR** a norma atual). Esta skill não calcula planilha de custos.
- Prorrogação e repactuação seguem outras regras (índices e convenção); fora do escopo.

### 2.4 Obras e serviços de engenharia (fora do escopo, mas cite)
- A IN 65 **não se aplica** (art. 1º § 1º). A Lei 14.133, art. 23 § 2º, manda usar **SICRO** (transportes) ou **SINAPI** (demais) com BDI e encargos, depois mídia especializada, contratações similares e notas fiscais.
- Use as tabelas oficiais atualizadas e documente a **data-base**. Contratação integrada/semi-integrada: art. 23 § 5º. Para detalhes e regulamento (decreto), **CONFERIR**; esta skill não gera orçamento de engenharia.

### 2.5 TIC
- IN 65, art. 8º: preços dos **Catálogos de Soluções de TIC com Condições Padronizadas** da secretaria de governo digital servem como preço estimado, salvo se a pesquisa der menos. **CONFERIR** a vigência dos catálogos e normas de TIC.
- Software/licença: cuide da métrica (usuário, núcleo, subscrição) e do prazo (12/36 meses); preços de períodos diferentes não são comparáveis.

### 2.6 Itens de saúde (medicamentos e correlatos)
- O art. 23 § 1º, I cita o **banco de preços em saúde**. Medicamentos têm também teto regulatório (CMED, **CONFERIR**). Use o catálogo de medicamentos e a unidade de fornecimento correta (comprimido × cartela × caixa).

### 2.7 Pesquisa direta com fornecedores
- Mínimo 3, justificativa da escolha, formal, com dados mínimos (IN 65, art. 5º § 2º). Registre os que **não responderam**. O envio de cotação a terceiros em nome do órgão é ato externo: faça com autorização do responsável. Esta skill não envia nada.

### 2.8 Adesão a ata (carona)
- A IN 65, art. 1º § 3º, manda usar a pesquisa para aferir a **vantagem econômica** da adesão. Compare o preço da ata com a mediana da série de outras contratações.

### 2.9 Preço de referência sigiloso
- Orçamento sigiloso (art. 24 da Lei 14.133) muda a divulgação, não a necessidade de pesquisar. Mantenha o mapa interno ao processo. **CONFERIR** o regime vigente.

### 2.10 Objetos heterogêneos (kits, soluções)
- Decomponha em itens com código de catálogo e some, ou use contratações de objeto equivalente; evite comparar "solução completa" com item solto.

### 2.11 Marca, modelo e especificação rara
- Justifique a escolha se a especificação restringir (art. 41 da Lei 14.133 trata de indicação de marca — **CONFERIR**). A série deve refletir a especificação que você pretende exigir, não uma mais ampla.
