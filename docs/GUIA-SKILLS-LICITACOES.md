# Guia das skills de licitações, contratos e pesquisa de preços (Lei 14.133/2021)

> Versão de 07/10/2026. Pacote com **3 skills** para Claude Code (ou qualquer agente que leia arquivos `SKILL.md`).
> Foram escritas para **qualquer órgão público brasileiro**: nada é específico de uma unidade. Cada skill traz um bloco "Parâmetros do órgão" que quem usa preenche.
> **Aviso:** são ferramentas de apoio. Não substituem parecer jurídico, a decisão do agente responsável nem a conferência do texto oficial. Onde a skill escreve **CONFERIR**, a informação não foi confirmada na fonte primária e deve ser checada antes de entrar em processo.

---

## 1. O que tem no pacote

| Skill | Para que serve | Tipo |
|---|---|---|
| `licitacoes-contratos-br` | Conhecimento: como planejar, licitar, contratar e gerir contratos | Só leitura (sem código) |
| `pesquisa-precos-pncp` | Pesquisa de preços de **bens e serviços** com preços homologados de outros órgãos (PNCP / Compras.gov.br) | Scripts Python |
| `pesquisa-precos-obras-engenharia` | Orçamento de **obras e serviços de engenharia** com SINAPI, BDI e curva ABC | Scripts Python |

As três se complementam: a primeira dá o contexto legal e os checklists; a segunda e a terceira fazem a pesquisa de preço (a segunda exclui obras, a terceira cobre só obras).

---

## 2. O que cada skill faz

### 2.1 `licitacoes-contratos-br` — guia de licitações e contratos

Aciona com: *licitação, contrato, termo aditivo, ETP, TR, dispensa, inexigibilidade, SRP*.

Estrutura (o agente abre só o arquivo de que precisa):

| Tema | Arquivo | Conteúdo |
|---|---|---|
| Ciclo e governança | `references/01_ciclo_e_governanca.md` | Fases da contratação, agentes, linhas de defesa, PNCP |
| Planejamento | `references/02_planejamento_etp_tr_riscos.md` | PCA, DFD, ETP, mapa de riscos, TR, orçamento estimado |
| Modalidades e critérios | `references/03_modalidades_e_criterios.md` | Pregão, concorrência, concurso, leilão, diálogo competitivo; critérios de julgamento (art. 33) |
| Contratação direta | `references/04_contratacao_direta.md` | Dispensa (art. 75), inexigibilidade (art. 74), processo de contratação direta (art. 72) |
| SRP e atas | `references/05_srp_e_atas.md` | Registro de preços, adesão ("carona"), gestão de ata |
| Contratos e aditivos | `references/06_contratos_e_aditivos.md` | Cláusulas, garantias, vigência, prorrogação, reajuste/repactuação/reequilíbrio, aditivos 25%/50% |
| Gestão e fiscalização | `references/07_gestao_e_fiscalizacao.md` | Gestor, fiscal, recebimento provisório/definitivo, liquidação |
| Sanções e recursos | `references/08_sancoes_recursos_extincao.md` | Infrações, sanções, rescisão, recursos |
| Jurisprudência TCU | `references/09_jurisprudencia_tcu.md` | Orientações do TCU (números de acórdão só quando confirmados; o resto marcado CONFERIR) |
| Transição 8.666 → 14.133 | `references/10_mapeamento_8666_para_14133.md` | Tabela de correspondência artigo a artigo |
| Lições e armadilhas | `references/11_licoes_aprendidas_e_armadilhas.md` | Erros recorrentes em processos e documentos |
| Glossário | `references/12_glossario_e_siglas.md` | Termos e siglas |
| **Valores atualizados** | `references/13_valores_atualizados.md` | Tetos de dispensa, contrato verbal, grande vulto etc., conforme o decreto vigente (**muda todo 1º de janeiro**) |
| Checklists | `checklists/01…07` | Fase preparatória, edital e minutas, contratação direta, aditivo de acréscimo/supressão, aditivo de prorrogação, adesão a ata, fiscalização e recebimento |

Exemplos de uso: "monte o checklist de aditivo de prorrogação", "essa compra cabe em dispensa por valor?", "qual o rito da adesão a ata?", "o que mudou da 8.666 para a 14.133 em reajuste?".

### 2.2 `pesquisa-precos-pncp` — pesquisa de preços (bens e serviços)

Aciona com: *pesquisa de preços, preço estimado, mapa de preços, CATMAT*.

Faz, nesta ordem:
1. **Acha o código de catálogo** (CATMAT para material, CATSER para serviço) — `scripts/catalogo.py`.
2. **Coleta preços unitários homologados** de contratações similares de outros órgãos, com fornecedor, órgão, UF, quantidade, unidade e **link do PNCP** de cada preço — `scripts/buscar_precos.py` (por código de catálogo ou por texto livre).
3. **Saneia e calcula** com critério de corte escrito (IQR, MAD, faixa da mediana ou nenhum), média/mediana/menor preço, desvio e coeficiente de variação; avisa quando há menos de 3 preços ou muitos alertas de qualidade — `scripts/calcular_precos.py` (roda **offline** sobre o arquivo coletado).
4. **Gera os documentos**: mapa comparativo (`.csv` e `.xlsx`), memória de cálculo e minuta de justificativa da pesquisa — `scripts/gerar_mapa.py`.

Base normativa: Lei 14.133 art. 23 e, na União, IN SEGES/ME nº 65/2021 (parâmetros, ordem de prioridade, janela de até 1 ano, mínimo de 3 preços, saneamento). Fora da União a IN serve de **referência**; a skill manda conferir a norma local.
Também documenta alertas de qualidade dos dados (unidade divergente, preço de lote, SRP, item cancelado) e casos-limite (item único, inexigibilidade, serviço contínuo, TIC).
**Fora do escopo:** obras e engenharia (use a skill 2.3).

### 2.3 `pesquisa-precos-obras-engenharia` — orçamento de obras e engenharia

Aciona com: *orçamento de obra, SINAPI, SICRO, BDI, planilha orçamentária, curva ABC*.

1. **Baixa a tabela SINAPI** da Caixa (mês mais recente publicado; se o mês atual não saiu, volta sozinha até achar) e guarda em banco SQLite local — `scripts/sinapi_baixar.py`.
2. **Busca composições e insumos** por código ou texto, por UF, desonerado ou não, com o detalhamento analítico — `scripts/sinapi_buscar.py`.
3. **Monta o orçamento** a partir de uma planilha de quantitativos: custo direto → BDI → preço global, com memória de cálculo, justificativa e planilha `.xlsx` — `scripts/orcamento.py`.
4. **Calcula o BDI** pela fórmula consolidada do TCU — `scripts/bdi.py`.
5. **Curva ABC** do orçamento — `scripts/curva_abc.py`.

Referências: norma do orçamento de obras (Lei 14.133 art. 23 §§ 2º a 6º, art. 24; Decreto 7.983/2013; IN SEGES/ME 91/2022), fonte e formato do SINAPI, SICRO e outras fontes, BDI e encargos, aceitabilidade de preços/regimes de execução/sobrepreço, modelos de documento.
**Limites:** SICRO (DNIT) e tabelas estaduais **não têm download automatizável** — a skill aceita entrada manual (`fonte=SICRO` na planilha). PNCP e Compras.gov.br **não trazem preço unitário de serviço de obra** (só valor global, útil como teste de sanidade).

---

## 3. Como instalar

### 3.1 Estrutura final esperada

```
~/.claude/skills/
├── licitacoes-contratos-br/          (contém SKILL.md)
├── pesquisa-precos-pncp/             (contém SKILL.md, scripts/, references/, tests/)
└── pesquisa-precos-obras-engenharia/ (contém SKILL.md, scripts/, references/, tests/)
```
No Windows: `%USERPROFILE%\.claude\skills\`. Para instalar só num projeto: `<pasta-do-projeto>/.claude/skills/`.

### 3.2 Instalação manual (mais simples)

1. Descompacte o zip numa pasta qualquer.
2. Copie as 3 pastas de skill (não o `LEIAME.md` nem este guia) para `~/.claude/skills/`.
3. Instale as bibliotecas Python (seção 4): `pip install requests openpyxl`.
4. Abra uma sessão **nova** do Claude Code (skills são lidas na abertura) e peça algo como "faça a pesquisa de preços de papel A4".

### 3.3 Instalação por prompt (cole no Claude Code ou em outro agente com acesso a arquivos e terminal)

> Instale as skills do pacote que está em `<CAMINHO-DO-ZIP-OU-PASTA>`. Passos: (1) se for .zip, extraia para uma pasta temporária nova e vazia; (2) copie as pastas `licitacoes-contratos-br`, `pesquisa-precos-pncp` e `pesquisa-precos-obras-engenharia` para `~/.claude/skills/` sem sobrescrever nada que já exista com outro conteúdo (se existir pasta de mesmo nome, mostre a diferença e pergunte); (3) rode `pip install requests openpyxl`; (4) rode os testes offline: `python3 pesquisa-precos-pncp/tests/test_calculo.py` e `python3 pesquisa-precos-obras-engenharia/tests/test_obras.py` dentro de `~/.claude/skills/`; (5) confirme que cada pasta tem `SKILL.md` com `name:` e `description:` no início; (6) me diga o que foi instalado, o resultado dos testes e se faltou algo. Não apague nada, não use `sudo`.

### 3.4 Instalação por um agente lendo este documento

Entregue este arquivo ao agente com a instrução: *"Leia o GUIA-SKILLS-LICITACOES.md e instale as skills conforme a seção 3, depois execute a seção 5 (verificação) e relate."* O agente deve seguir 3.1 a 3.3 e a seção 5. Para agentes que **não** são o Claude Code:

| Agente | Onde colocar |
|---|---|
| Claude Code | `~/.claude/skills/<skill>/` |
| Antigravity (`agy`) | `<projeto>/.agents/skills/<skill>/` (ou a pasta de skills globais do agente) |
| Outros (Codex, Cursor, etc.) | Copie as pastas para onde o agente lê skills ou aponte no arquivo de instruções do projeto (`AGENTS.md`) para `SKILL.md` de cada uma; as `references/` e `scripts/` ficam ao lado e são abertos sob demanda |

### 3.5 Preencher uma vez
Ao usar pela primeira vez, preencha o bloco **"Parâmetros do órgão"** das skills (esfera federal/estadual/municipal, norma local de pesquisa de preços, janela de preços, mínimo de preços, método e responsáveis). Sem isso a skill aplica os padrões federais.

---

## 4. O que as skills precisam para funcionar (integrações e dependências)

### 4.1 Resumo

| Item | `licitacoes-contratos-br` | `pesquisa-precos-pncp` | `pesquisa-precos-obras-engenharia` |
|---|:---:|:---:|:---:|
| Python 3.8 ou superior | — | **sim** | **sim** |
| Biblioteca `requests` | — | **sim** (coleta) | **sim** (só o download SINAPI) |
| Biblioteca `openpyxl` | — | opcional (gera `.xlsx`) | opcional (gera `.xlsx`; a leitura do SINAPI usa parser próprio) |
| Internet | — | **sim** para coletar; o cálculo roda offline | **sim** para baixar o SINAPI; depois usa cópia local |
| Chave de API / login / credencial | **nenhum** | **nenhum** | **nenhum** |

**Nenhuma skill exige chave, senha, token ou conta.** Todas as APIs e downloads usados são públicos.

### 4.2 Bibliotecas Python
```
pip install requests openpyxl
```
Python testado em 3.14 e escrito para 3.8+. Fora isso só biblioteca padrão. `openpyxl` é opcional: sem ela as skills geram `.csv` e `.md`, mas não `.xlsx`.

### 4.3 Serviços públicos acessados pela internet

| Serviço | Endereço base | Usado por | Para quê | Observações |
|---|---|---|---|---|
| PNCP — API de consulta | `https://pncp.gov.br` (`/api/consulta/v1`, `/api/pncp/v1`, `/api/search`) | pesquisa-precos-pncp | Contratações, itens, resultados/vencedores, número de controle e link de cada preço | Sem chave. **Enviar `User-Agent` de navegador** (os scripts já enviam), senão o WAF bloqueia. Muitas chamadas simultâneas → erro **429** (os scripts limitam as threads e repetem). Os links `pncp.gov.br/app/...` abrem no navegador, não por `curl` |
| Dados Abertos Compras.gov.br | `https://dadosabertos.compras.gov.br` | pesquisa-precos-pncp | Catálogo CATMAT/CATSER e módulo "Pesquisa de Preço" (preço unitário homologado item a item) | Sem chave. Os filtros de texto do catálogo são **ignorados pelo servidor** — o script baixa o catálogo e busca localmente. Pode atrasar em relação ao PNCP |
| Caixa — SINAPI | `https://www.caixa.gov.br/Downloads/sinapi-relatorios-mensais/SINAPI-AAAA-MM-formato-xlsx.zip` (página `https://www.caixa.gov.br/sinapi`) | pesquisa-precos-obras-engenharia | Tabela mensal de preços e composições, todas as UFs (~16 MB por mês) | Sem login. O mês corrente costuma não estar publicado: o script volta até achar. Mês inexistente pode devolver HTML ou loop de redirecionamento em vez de erro (o script valida que o arquivo é um zip). Se a Caixa mudar a URL, o download quebra — ver `references/sinapi-fonte-e-formato.md` |
| Planalto (legislação) | `planalto.gov.br` | todas (apenas para conferência humana) | Texto oficial de leis e decretos | Não é acessado pelos scripts |

### 4.4 Armazenamento local (cache)

| Skill | Pasta padrão | Variável para mudar | Conteúdo |
|---|---|---|---|
| pesquisa-precos-pncp | `~/.cache/pesquisa-precos-pncp` | `PNCP_CACHE` | Respostas da API e catálogo |
| pesquisa-precos-obras-engenharia | `~/.cache/pesquisa-precos-obras` | `OBRAS_CACHE` | Zip do SINAPI e banco SQLite (cerca de 115 MB por mês importado) |

Pode apagar o cache a qualquer momento; ele é refeito na próxima coleta.

### 4.5 Ferramentas do agente (opcionais)

Os scripts **não dependem de nenhuma ferramenta extra do agente**. Para **conferir norma e jurisprudência** antes de citar em processo, use as fontes oficiais:

| Fonte | Para quê |
|---|---|
| Planalto (`planalto.gov.br/ccivil_03`) | Texto oficial de leis e decretos (ex.: Lei 14.133 e o decreto anual de valores) |
| Portal de jurisprudência do TCU (`pesquisa.apps.tcu.gov.br`) | Número, ementa e inteiro teor de acórdãos e súmulas |
| PNCP (`pncp.gov.br`) | Divulgação oficial da atualização anual de valores (art. 182) |
| Busca web ou leitura de página do próprio agente (se tiver) | Abrir essas páginas e trazer o trecho para a conversa; sem isso, abra o link no navegador e cole o trecho para o agente |

**Regra das skills:** número de acórdão ou artigo que não foi confirmado numa fonte oficial fica marcado CONFERIR e não deve ser citado em processo.

### 4.6 Rede corporativa (proxy)
Em órgãos com proxy, o `pip install` e os scripts precisam sair pelo proxy. Configure `HTTPS_PROXY`/`HTTP_PROXY` no terminal antes de rodar (`requests` respeita essas variáveis). Erro **407**, timeout ou erro de certificado SSL costuma ser proxy ou inspeção de TLS: ajuste a rede/TI em vez de repetir o comando. Se a TI bloquear `caixa.gov.br` ou `pncp.gov.br`, baixe o SINAPI manualmente e use a importação de arquivo local: `python3 scripts/sinapi_baixar.py --arquivo <zip baixado> --mes AAAA-MM` (ver `references/sinapi-fonte-e-formato.md`).

---

## 5. Verificação depois de instalar (5 minutos)

```bash
# 1) Testes que rodam sem internet
cd ~/.claude/skills/pesquisa-precos-pncp && python3 tests/test_calculo.py          # esperado: OK (7 testes)
cd ~/.claude/skills/pesquisa-precos-obras-engenharia && python3 tests/test_obras.py # esperado: OK (15 testes)

# 2) Ajuda dos scripts
python3 scripts/orcamento.py --help

# 3) Teste real de pesquisa de preços (usa a internet)
cd ~/.claude/skills/pesquisa-precos-pncp
python3 scripts/buscar_precos.py --catmat 461819 --dias 120 --max-compras 40 --out /tmp/teste
python3 scripts/calcular_precos.py /tmp/teste.json --out /tmp/teste
python3 scripts/gerar_mapa.py /tmp/teste.calculo.json --out /tmp/teste
# esperado: dezenas de preços com link PNCP, mediana calculada, arquivos .mapa.xlsx/.memoria.md/.justificativa.md

# 4) Teste real de orçamento de obra (baixa ~16 MB)
cd ~/.claude/skills/pesquisa-precos-obras-engenharia
python3 scripts/sinapi_baixar.py
python3 scripts/sinapi_buscar.py comp --codigo 87690 --uf DF
printf 'item;fonte;codigo;quantidade\n1;SINAPI;87690;120\n' > /tmp/q.csv
python3 scripts/orcamento.py /tmp/q.csv --uf DF --bdi 23.65 --out /tmp/orc
# esperado: custo da composição 87690 em DF, preço com BDI e arquivos de orçamento
```
No Windows, troque `python3` por `python` e `/tmp` por uma pasta sua. Se o passo 3 ou 4 falhar por rede, veja a seção 4.6.

Na sessão do agente, teste se a skill é reconhecida perguntando: "Quais skills de licitação você tem?" — ele deve citar as três.

---

## 6. Como pedir ao agente (exemplos)

- "Faça a pesquisa de preços de papel A4 75 g, resma de 500 folhas, últimos 12 meses, e gere o mapa e a justificativa."
- "Ache o CATSER de serviço de limpeza e pesquise os preços no DF."
- "Monte o orçamento desta planilha de quantitativos com SINAPI do DF, não desonerado, BDI de 23,65%, e gere a curva ABC."
- "Calcule o BDI com AC 3,8%, S 0,8%, R 0,5%, G 0,5%, DF 1,2%, L 7%, ISS 3%, PIS 0,65%, COFINS 3%."
- "Qual o teto da dispensa por valor para obras neste ano? Cite o decreto."
- "Monte o checklist do termo aditivo de prorrogação de vigência."

---

## 7. Limites e cuidados (leia antes de usar em processo)

1. **Valores monetários da lei mudam todo 1º de janeiro** (art. 182). A tabela da skill vale para 2026 (Decreto 12.807/2025). Em 2027 em diante a atualização pode sair por **portaria do MGI** (Ministério da Gestão), não só por decreto — confira antes de usar.
2. **Vigência de normas** marcadas CONFERIR: IN SEGES/ME 65/2021 (pesquisa de preços), Decreto 7.983/2013 e IN SEGES/ME 91/2022 (orçamento de obras), desoneração da folha (CPRB), norma local do seu ente federativo.
3. **Acórdãos do TCU** aparecem só com número e tese confirmados; os demais estão como orientação com CONFERIR. Leia o inteiro teor antes de citar em processo.
4. **Estados e municípios:** a base é a Lei 14.133 (nacional), mas decretos, INs e valores citados são federais — aplique a norma do seu ente.
5. **Qualidade dos dados do PNCP:** preço unitário vs. global, unidade de medida divergente, lote, desconto e item cancelado podem distorcer. Os scripts alertam; **abra 3 a 5 links do mapa e confira** antes de assinar.
6. **Coleta lenta:** a rota por texto livre faz ~1 chamada por compra (200 compras ≈ 2 a 3 minutos).
7. **Comunicação externa:** as skills redigem, mas **não enviam** cotação a fornecedor nem ofício a autoridade. Isso fica com o responsável.
8. **Dados do órgão:** nunca coloque senha, token, dado pessoal ou documento sigiloso nos arquivos das skills.

## 8. Atualização e manutenção

- Valores (seção 13 de `licitacoes-contratos-br`): atualizar a cada 1º de janeiro.
- SINAPI: o próprio script baixa o mês mais recente; rode `sinapi_baixar.py` no início de cada orçamento.
- Se uma API mudar (PNCP, Compras.gov.br ou Caixa), a falha costuma aparecer como erro 404, HTML no lugar de JSON/zip ou resposta vazia. Consulte `references/api-pncp-comprasgov.md` e `references/sinapi-fonte-e-formato.md`, que registram como cada endpoint se comportou em 07/10/2026.
- Rode os testes offline (seção 5) depois de qualquer alteração nos scripts.
