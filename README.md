# Skills de licitações, contratos e pesquisa de preços (Lei 14.133/2021)

Três skills para o **Claude Code** (e outros agentes que leiam `SKILL.md`), feitas para **qualquer órgão público brasileiro**:

| Skill | O que faz |
|---|---|
| [`licitacoes-contratos-br`](skills/licitacoes-contratos-br) | Guia de planejamento, modalidades, contratação direta, SRP/atas, contratos e aditivos, fiscalização, sanções, mapa 8.666 → 14.133, tabela de **valores atualizados** (Decreto 12.807/2025) e 7 checklists |
| [`pesquisa-precos-pncp`](skills/pesquisa-precos-pncp) | Pesquisa de preços de **bens e serviços** com preços homologados do PNCP e do Compras.gov.br (IN SEGES/ME 65/2021): coleta, saneamento, mediana, mapa `.xlsx`, memória de cálculo e justificativa |
| [`pesquisa-precos-obras-engenharia`](skills/pesquisa-precos-obras-engenharia) | Orçamento de **obras e engenharia**: baixa o SINAPI da Caixa, monta custo direto + BDI (fórmula do TCU), curva ABC e planilha orçamentária |

Sem chave de API, sem login: tudo usa serviços públicos. Detalhes, dependências e limites no [guia completo](docs/GUIA-SKILLS-LICITACOES.md).

> **Aviso:** ferramenta de apoio. Não substitui parecer jurídico nem a decisão do agente responsável. Itens marcados **CONFERIR** nas skills não foram confirmados em fonte oficial: cheque antes de citar em processo. Os valores monetários da lei mudam todo 1º de janeiro.

## Instalar (3 caminhos)

**Passo a passo ilustrado (PDF):** [`docs/passo-a-passo-instalacao.pdf`](docs/passo-a-passo-instalacao.pdf)

### A) Por prompt, direto no chat do Claude Code
Abra o Claude Code (`claude`) e cole:

```text
Instale as skills do repositório https://github.com/MtsLoureiro/skills-licitacoes-14133 :
1) clone para uma pasta temporária nova (git clone --depth 1);
2) copie as 3 pastas de skills/ para ~/.claude/skills/ sem sobrescrever nada que já exista com conteúdo diferente (se houver, mostre a diferença e pergunte);
3) rode pip install requests openpyxl;
4) rode os testes offline: python3 tests/test_calculo.py dentro de pesquisa-precos-pncp e python3 tests/test_obras.py dentro de pesquisa-precos-obras-engenharia;
5) diga o que foi instalado e o resultado dos testes. Não use sudo e não apague nada.
```
Depois **abra uma sessão nova** do Claude Code (as skills são lidas na abertura).

### B) Por terminal, copiando as pastas
```bash
git clone --depth 1 https://github.com/MtsLoureiro/skills-licitacoes-14133.git
mkdir -p ~/.claude/skills
cp -R skills-licitacoes-14133/skills/* ~/.claude/skills/
pip install requests openpyxl
```
Windows (PowerShell): `Copy-Item -Recurse skills-licitacoes-14133\skills\* $env:USERPROFILE\.claude\skills\`

### C) Sem git: baixar o ZIP
Botão verde **Code → Download ZIP**, extraia e copie o conteúdo da pasta `skills/` para `~/.claude/skills/`.

## Testar
```bash
cd ~/.claude/skills/pesquisa-precos-pncp && python3 tests/test_calculo.py
cd ~/.claude/skills/pesquisa-precos-obras-engenharia && python3 tests/test_obras.py
```
Depois, no Claude Code: *"Faça a pesquisa de preços de papel A4 75 g, resma de 500 folhas."*

## Licença
[MIT](LICENSE). Os dados consultados (PNCP, Compras.gov.br, SINAPI/Caixa) pertencem às respectivas fontes públicas.
