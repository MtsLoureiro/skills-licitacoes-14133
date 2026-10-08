# BDI e encargos sociais

## 1. Encargos sociais (já estão dentro das composições do SINAPI)

- O SINAPI aplica **encargos sociais sobre a mão de obra** dentro de cada composição, por UF e por regime. Cabeçalho da planilha (exemplo real, 08/2026, DF, não desonerado): **horista 110,08%** e **mensalista 69,94%**; desonerado: horista 94,63%, mensalista 57,45% (SP, não desonerado: 115,01% / 71,18%).
- Você **não soma encargos de novo** no orçamento: o custo da composição já os contém. O que escolhe é o **regime**:
  - **Não desonerado**: encargos incluem a contribuição previdenciária patronal sobre a folha.
  - **Desonerado**: a folha é desonerada e, para as atividades abrangidas, a contribuição incide sobre a receita (**CPRB**), que entra no **BDI** como tributo. **O regime tem que ser o mesmo nos custos e no BDI.**
  - **Sem encargos**: base para quem monta composição própria aplicando seus próprios encargos (raro).
- A legislação da desoneração da folha/CPRB teve mudanças sucessivas (prorrogações, retorno gradual). **CONFERIR** a lei vigente e se o seu objeto/CNAE está abrangido antes de escolher "desonerado". O edital deve dizer qual regime serve de base e como o licitante comprova o seu.

## 2. BDI — o que é e como compor

**BDI** = Benefícios e Despesas Indiretas: percentual aplicado sobre o **custo direto** (Decreto 7.983/2013, art. 2º, V) para chegar ao preço (art. 2º, VI). Deve evidenciar, no mínimo (art. 9º): **administração central** (rateio), **tributos sobre o preço**, **seguro, risco e garantia**, **lucro**.

Fórmula consolidada usada pelo TCU (a mesma de `bdi.py`):

```
BDI = [ (1 + AC + S + R + G) × (1 + DF) × (1 + L) / (1 − I) ] − 1
AC administração central · S seguro · R risco · G garantia · DF despesas financeiras · L lucro
I   = PIS + COFINS + ISS (+ CPRB se orçamento desonerado)       (sobre o preço de venda)
```
`python3 scripts/bdi.py --ac 4 --s 0.8 --r 1 --g 0.8 --df 1.2 --l 7 --pis 0.65 --cofins 3 --iss 3` → 23,65% (exemplo **didático**, parâmetros inventados para ilustrar, não referência de mercado).

**CONFERIR** a fórmula e as **faixas referenciais por tipo de obra** no inteiro teor do **Acórdão 2622/2013-Plenário** (citado pelo Ac. 1799/2014-Plenário como o que fixou faixas aceitáveis de BDI por tipo de obra). Não reproduzo números de faixa porque não os confirmei em fonte primária.
`bdi.py --faixa MIN,MAX` aceita a faixa que **você** conferiu e avisa se o resultado cai fora.

### Cuidados exigidos pelo TCU (determinações do Ac. 2622/2013, reproduzidas no Ac. 1799/2014, itens 9.3.2.x — **CONFERIR** o inteiro teor)

| Ponto | Regra de prática |
|---|---|
| **Administração local, canteiro, mobilização/desmobilização** | **Fora do BDI**: discriminar na planilha de custos diretos (identificáveis, medíveis, pagos por medição). Medição **proporcional à execução financeira**, não valor mensal fixo (evita pagar por atraso/prorrogação) |
| **ISS** | Alíquota **compatível com a legislação do município** onde se presta o serviço, aplicada sobre a **base de cálculo** prevista na lei municipal; entre o piso de 2% (ADCT art. 88) e o teto de 5% (LC 116/2003, art. 8º, II) |
| **PIS/COFINS** | Se a empresa é do regime **não cumulativo**, o edital deve exigir demonstrativo de que os percentuais do BDI correspondem à média efetivamente recolhida (descontados os créditos) |
| **Simples Nacional** | Licitante optante apresenta ISS/PIS/COFINS discriminados compatíveis com o Anexo IV da LC 123/2006 e encargos **sem** as contribuições de que está dispensada (Sesi, Senai, Sebrae etc.) |
| **Aditivos** | Para serviços **novos** em aditivos, exigir no edital a incidência da taxa de BDI do **orçamento-base** quando a do contratado for injustificadamente elevada, para manter o desconto ofertado (art. 14 do Decreto 7.983) |
| **Não fixar teto de BDI de forma cega** | Ac. 1666/2017-Plenário (ementa): "não é recomendável estabelecer limites máximos para o BDI"; avaliar no caso concreto, pelas alíquotas aplicáveis |

### BDI diferenciado (materiais e equipamentos)

- **Súmula TCU 253** e **Decreto 7.983, art. 9º, § 1º**: quando o parcelamento do objeto é **tecnicamente/economicamente inviável**, e há itens de **fornecimento de materiais/equipamentos de natureza específica** (empresas com especialidades próprias) com **percentual significativo** do preço global, esses itens devem ter **BDI reduzido**.
- **Art. 9º, § 2º**: exceção — fornecimento em que o contratado não é mero intermediário, ou equipamentos/sistemas não padronizados, com projeto/fabricação/logística próprios: o BDI pode ser calculado e justificado pela complexidade.
- Na planilha: coluna `bdi` por linha (`orcamento.py`) com justificativa; o script alerta toda linha com BDI diferente do global. Não existe "percentual reduzido padrão": o TCU não fixa na súmula; **calcule** (sem administração central duplicada, sem lucro cheio, etc.) e fundamente.

## 3. Arredondamento

Preço unitário e totais com 2 casas. Escolha **arredondar** ou **truncar** e diga no edital (`--arredondamento`). A diferença se acumula em planilhas grandes, e o licitante recalcula do mesmo modo. A regra do seu órgão pode impor um (CONFERIR).
