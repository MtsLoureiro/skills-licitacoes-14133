"""SINAPI: download do ZIP mensal da Caixa, leitura das planilhas XLSX e banco SQLite local.

Só stdlib (+ requests para o download). Não usa openpyxl para LER: a planilha "Referência" tem ~13 MB
compactados / ~100 MB de XML e o openpyxl não termina em tempo útil. Aqui lemos o XML em fluxo.

Estrutura real (conferida com a tabela 08/2026):
  abas ISD/ICD/ISE = INSUMOS (sem desoneração / com desoneração / sem encargos), um preço por UF por coluna
  abas CSD/CCD/CSE = COMPOSIÇÕES, pares de colunas (Custo R$, %AS) por UF
  aba  Analítico   = estrutura das composições (itens e coeficientes)
ARMADILHA: na aba de composições a coluna do código é uma FÓRMULA HYPERLINK(...MATCH(<código>,...)) cujo
valor em cache é 0. O código verdadeiro está no texto da fórmula, não no valor.
"""
import os
import re
import sqlite3
import sys
import zipfile
from datetime import date
from pathlib import Path
from xml.etree import ElementTree as ET

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
RNS = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
UF_RE = re.compile(r"^[A-Z]{2}$")
UFS = set("AC AL AM AP BA CE DF ES GO MA MG MS MT PA PB PE PI PR RJ RN RO RR RS SC SE SP TO".split())
URL_MENSAL = "https://www.caixa.gov.br/Downloads/sinapi-relatorios-mensais/SINAPI-{ano}-{mes:02d}-formato-xlsx.zip"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/128.0.0.0 Safari/537.36")
REGIMES = {"nao-desonerado": ("ISD", "CSD"), "desonerado": ("ICD", "CCD"), "sem-encargos": ("ISE", "CSE")}


def cache_dir():
    d = Path(os.environ["OBRAS_CACHE"]) if os.environ.get("OBRAS_CACHE") else Path.home() / ".cache" / "pesquisa-precos-obras"
    d.mkdir(parents=True, exist_ok=True)
    return d


# ----------------------------------------------------------------------------- leitura de XLSX em fluxo
def _col(ref):
    return re.sub(r"\d", "", ref)


class Xlsx:
    """Leitor mínimo e rápido de .xlsx (aba por nome). Devolve linhas como dict {coluna: valor}.

    Células com fórmula devolvem também a fórmula em row['_f'][coluna].
    Aceita strings compartilhadas e inlineStr (usado nos arquivos de teste).
    """

    def __init__(self, caminho):
        self.z = zipfile.ZipFile(caminho)
        self.ss = self._shared_strings()
        self.abas = self._abas()

    def _shared_strings(self):
        if "xl/sharedStrings.xml" not in self.z.namelist():
            return []
        out = []
        for _, el in ET.iterparse(self.z.open("xl/sharedStrings.xml")):
            if el.tag == NS + "si":
                out.append("".join(t.text or "" for t in el.iter(NS + "t")))
                el.clear()
        return out

    def _abas(self):
        wb = ET.fromstring(self.z.read("xl/workbook.xml"))
        rels = ET.fromstring(self.z.read("xl/_rels/workbook.xml.rels"))
        alvo = {r.get("Id"): r.get("Target") for r in rels}
        out = {}
        for s in wb.iter(NS + "sheet"):
            t = alvo[s.get(RNS + "id")]
            out[s.get("name")] = t.lstrip("/") if t.startswith("/") else "xl/" + t
        return out

    def linhas(self, aba, max_linhas=None):
        n = 0
        for _, el in ET.iterparse(self.z.open(self.abas[aba])):
            if el.tag != NS + "row":
                continue
            r, f = {}, {}
            for c in el.findall(NS + "c"):
                col = _col(c.get("r"))
                t = c.get("t")
                v = c.find(NS + "v")
                fe = c.find(NS + "f")
                if fe is not None and fe.text:
                    f[col] = fe.text
                if t == "inlineStr":
                    is_ = c.find(NS + "is")
                    r[col] = "".join(x.text or "" for x in is_.iter(NS + "t")) if is_ is not None else ""
                elif v is None or v.text is None:
                    continue
                elif t == "s":
                    r[col] = self.ss[int(v.text)]
                elif t in ("str", "b", "e"):
                    r[col] = v.text
                else:
                    try:
                        r[col] = float(v.text)
                    except ValueError:
                        r[col] = v.text
            r["_n"] = int(el.get("r"))
            r["_f"] = f
            yield r
            el.clear()
            n += 1
            if max_linhas and n >= max_linhas:
                return


def codigo_da_formula(formula):
    """HYPERLINK(...MATCH(104658,Analítico!$B:$B,0)...,104658) -> 104658."""
    m = re.search(r"MATCH\(\s*(\d+)\s*,", formula or "")
    return int(m.group(1)) if m else None


def num(v):
    if v is None or v == "":
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def mapa_ufs(linhas_cab, pares):
    """Acha, entre as linhas do cabeçalho, a que traz as siglas de UF e devolve {UF: coluna}.

    Na aba de composições cada UF ocupa 2 colunas (custo e %AS); a coluna da sigla é a do custo.
    """
    melhor = {}
    for r in linhas_cab:
        achados = {v: c for c, v in r.items() if c not in ("_n", "_f") and isinstance(v, str) and v in UFS}
        if len(achados) > len(melhor):
            melhor = achados
    return melhor


def col_prox(col):
    """'E' -> 'F'; 'Z' -> 'AA'."""
    n = 0
    for ch in col:
        n = n * 26 + ord(ch) - 64
    n += 1
    s = ""
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


# ----------------------------------------------------------------------------- banco SQLite
SCHEMA = """
CREATE TABLE meta(chave TEXT PRIMARY KEY, valor TEXT);
CREATE TABLE insumo_def(regime TEXT, codigo INTEGER, classificacao TEXT, descricao TEXT, unidade TEXT, origem TEXT, PRIMARY KEY(regime, codigo));
CREATE TABLE insumo(regime TEXT, codigo INTEGER, uf TEXT, preco REAL);
CREATE TABLE composicao_def(regime TEXT, codigo INTEGER, grupo TEXT, descricao TEXT, unidade TEXT, PRIMARY KEY(regime, codigo));
CREATE TABLE composicao(regime TEXT, codigo INTEGER, uf TEXT, custo REAL, pct_as REAL);
CREATE TABLE estrutura(comp INTEGER, tipo TEXT, item INTEGER, descricao TEXT, unidade TEXT, coef REAL, situacao TEXT);
CREATE TABLE comp_cab(codigo INTEGER PRIMARY KEY, grupo TEXT, descricao TEXT, unidade TEXT, situacao TEXT);
CREATE TABLE encargos(regime TEXT, uf TEXT, horista REAL, mensalista REAL);
CREATE INDEX i_ins ON insumo(regime, codigo, uf);
CREATE INDEX i_com ON composicao(regime, codigo, uf);
CREATE INDEX i_est ON estrutura(comp);
"""


def _cabecalho(x, aba):
    cab = list(x.linhas(aba, max_linhas=10))
    return cab


def _meta_mes(cab, meta):
    for r in cab:
        if str(r.get("A", "")).startswith("Mês de Referência"):
            meta["_mes"] = r.get("B")
        if str(r.get("A", "")).startswith("Data de emissão"):
            meta["_emissao"] = r.get("B")


def _ler_insumos(x, aba, regime, con, meta):
    cab = _cabecalho(x, aba)
    ufs = mapa_ufs(cab, 1)
    if not ufs:
        print(f"[aviso] aba {aba}: UFs não encontradas", file=sys.stderr)
        return 0
    hdr = next((r["_n"] for r in cab if any(isinstance(v, str) and v.startswith("Código") for k, v in r.items() if k == "B")), 10)
    for r in cab:
        for rot, chave in (("Horista", "horista"), ("Mensalista", "mensalista")):
            if rot in r.values():
                for uf, c in ufs.items():
                    v = num(r.get(c))
                    if v is not None:
                        meta.setdefault((regime, uf), {})[chave] = v
    _meta_mes(cab, meta)
    n = 0
    lote, defs = [], []
    for r in x.linhas(aba):
        if r["_n"] <= hdr:
            continue
        cod = num(r.get("B"))
        if cod is None:
            continue
        for uf, c in ufs.items():
            p = num(r.get(c))
            if p is not None:
                lote.append((regime, int(cod), uf, p))
        defs.append((regime, int(cod), r.get("A"), r.get("C"), r.get("D"), r.get("E")))
        if len(lote) > 20000:
            con.executemany("INSERT INTO insumo VALUES(?,?,?,?)", lote)
            n += len(lote)
            lote = []
    con.executemany("INSERT INTO insumo VALUES(?,?,?,?)", lote)
    con.executemany("INSERT OR REPLACE INTO insumo_def VALUES(?,?,?,?,?,?)", defs)
    return n + len(lote)


def _ler_composicoes(x, aba, regime, con, meta):
    cab = _cabecalho(x, aba)
    ufs = mapa_ufs(cab, 2)
    if not ufs:
        print(f"[aviso] aba {aba}: UFs não encontradas", file=sys.stderr)
        return 0
    hdr = next((r["_n"] for r in cab if any(isinstance(v, str) and v.startswith("Grupo") for v in r.values())), 10)
    for r in cab:
        for rot, chave in (("Horista", "horista"), ("Mensalista", "mensalista")):
            if rot in r.values():
                for uf, c in ufs.items():
                    v = num(r.get(c))
                    if v is not None:
                        meta.setdefault((regime, uf), {})[chave] = v
    _meta_mes(cab, meta)
    n = 0
    lote, defs = [], []
    sem_codigo = 0
    for r in x.linhas(aba):
        if r["_n"] <= hdr:
            continue
        cod = codigo_da_formula(r["_f"].get("B")) or (int(num(r.get("B"))) if num(r.get("B")) else None)
        if not cod:
            sem_codigo += 1
            continue
        for uf, c in ufs.items():
            custo = num(r.get(c))
            if custo is not None:
                lote.append((regime, cod, uf, custo, num(r.get(col_prox(c))) or 0.0))
        defs.append((regime, cod, r.get("A"), r.get("C"), r.get("D")))
        if len(lote) > 20000:
            con.executemany("INSERT INTO composicao VALUES(?,?,?,?,?)", lote)
            n += len(lote)
            lote = []
    con.executemany("INSERT INTO composicao VALUES(?,?,?,?,?)", lote)
    con.executemany("INSERT OR REPLACE INTO composicao_def VALUES(?,?,?,?,?)", defs)
    if sem_codigo:
        print(f"[aviso] aba {aba}: {sem_codigo} linhas sem código", file=sys.stderr)
    return n + len(lote)


def _ler_analitico(x, con):
    cab_n = 10
    atual = None
    lote, cabs = [], []
    for r in x.linhas("Analítico"):
        if r["_n"] <= cab_n:
            continue
        cod = num(r.get("B"))
        if cod is None:
            continue
        tipo = r.get("C")
        if tipo in ("INSUMO", "COMPOSICAO"):
            lote.append((int(cod), tipo, int(num(r.get("D"))) if num(r.get("D")) is not None else None,
                         r.get("E"), r.get("F"), num(r.get("G")), r.get("H")))
        else:
            cabs.append((int(cod), r.get("A"), r.get("E"), r.get("F"), r.get("H")))
    con.executemany("INSERT INTO estrutura VALUES(?,?,?,?,?,?,?)", lote)
    con.executemany("INSERT OR REPLACE INTO comp_cab VALUES(?,?,?,?,?)", cabs)
    return len(lote), len(cabs)


def importar(xlsx_referencia, destino, verbose=True):
    """Converte o XLSX 'Referência' em SQLite (todas as UFs e os 3 regimes). Demora ~1-3 min uma vez."""
    x = Xlsx(xlsx_referencia)
    tmp = str(destino) + ".tmp"
    if os.path.exists(tmp):
        os.remove(tmp)
    con = sqlite3.connect(tmp)
    con.executescript(SCHEMA)
    meta = {}
    for regime, (aba_i, aba_c) in REGIMES.items():
        if aba_i in x.abas:
            n = _ler_insumos(x, aba_i, regime, con, meta)
            if verbose:
                print(f"  {aba_i}: {n} preços de insumo", file=sys.stderr)
        if aba_c in x.abas:
            n = _ler_composicoes(x, aba_c, regime, con, meta)
            if verbose:
                print(f"  {aba_c}: {n} custos de composição", file=sys.stderr)
    if "Analítico" in x.abas:
        ni, nc = _ler_analitico(x, con)
        if verbose:
            print(f"  Analítico: {ni} itens em {nc} composições", file=sys.stderr)
    for k, v in meta.items():
        if isinstance(k, tuple):
            con.execute("INSERT INTO encargos VALUES(?,?,?,?)", (k[0], k[1], v.get("horista"), v.get("mensalista")))
    con.execute("INSERT INTO meta VALUES('mes_referencia',?)", (str(meta.get("_mes") or ""),))
    con.execute("INSERT INTO meta VALUES('data_emissao',?)", (str(meta.get("_emissao") or ""),))
    con.commit()
    con.close()
    os.replace(tmp, destino)
    return destino


# ----------------------------------------------------------------------------- download
def zip_valido(b):
    return b[:2] == b"PK"


def baixar_zip(ano, mes, destino, session=None, verbose=True):
    """Baixa o ZIP mensal. Valida por magic bytes 'PK' (a Caixa devolve HTML 200 quando o mês não existe)."""
    import requests
    s = session or requests.Session()
    s.headers.update({"User-Agent": UA})
    url = URL_MENSAL.format(ano=ano, mes=mes)
    try:
        r = s.get(url, timeout=180, allow_redirects=True)
    except requests.TooManyRedirects:
        return None  # mês não publicado: a Caixa entra em laço de redirecionamento (302 -> página de downloads)
    except requests.RequestException as e:
        raise RuntimeError(f"falha de rede em {url}: {type(e).__name__}") from e
    if r.status_code != 200 or not zip_valido(r.content[:4]) or len(r.content) < 1_000_000:
        return None
    with open(destino, "wb") as f:
        f.write(r.content)
    return url


def extrair_referencia(zip_path, pasta):
    """Extrai SÓ o xlsx 'Referência' com nome ASCII (nomes do ZIP vêm em UTF-8 sem flag)."""
    z = zipfile.ZipFile(zip_path)
    alvo = None
    for i in z.infolist():
        if re.search(r"Refer.{1,4}ncia", i.filename, re.I):
            alvo = i
            break
    if alvo is None:
        raise RuntimeError("ZIP sem planilha 'Referência'; conteúdo: " + ", ".join(i.filename for i in z.infolist()))
    saida = Path(pasta) / "SINAPI_Referencia.xlsx"
    with open(saida, "wb") as f:
        f.write(z.read(alvo))
    return saida


def garantir_base(ano_mes=None, arquivo=None, meses_atras=8, verbose=True):
    """Devolve o caminho do SQLite do mês pedido, baixando/importando se preciso.

    ano_mes 'AAAA-MM'; sem ele, caminha do mês corrente para trás até achar ZIP válido.
    arquivo: ZIP ou XLSX local (fallback manual) -- o mês vem do próprio conteúdo/nome ('AAAA-MM' obrigatório em ano_mes).
    """
    cd = cache_dir()
    if arquivo:
        if not ano_mes:
            m = re.search(r"(20\d\d)[_-](\d\d)", os.path.basename(arquivo))
            if not m:
                raise SystemExit("--arquivo exige --mes AAAA-MM (não consegui deduzir do nome)")
            ano_mes = f"{m.group(1)}-{m.group(2)}"
        db = cd / f"sinapi-{ano_mes}.sqlite"
        if not db.exists():
            ref = arquivo
            if arquivo.lower().endswith(".zip"):
                ref = extrair_referencia(arquivo, cd)
            importar(ref, db, verbose)
        return db, ano_mes
    candidatos = []
    if ano_mes:
        candidatos = [tuple(map(int, ano_mes.split("-")))]
    else:
        hoje = date.today()
        a, m = hoje.year, hoje.month
        for _ in range(meses_atras):
            candidatos.append((a, m))
            m -= 1
            if m == 0:
                a, m = a - 1, 12
    for a, m in candidatos:
        tag = f"{a}-{m:02d}"
        db = cd / f"sinapi-{tag}.sqlite"
        if db.exists():
            return db, tag
        zp = cd / f"SINAPI-{tag}.zip"
        if not zp.exists():
            if verbose:
                print(f"Baixando SINAPI {tag} (~16 MB)...", file=sys.stderr)
            if baixar_zip(a, m, zp) is None:
                if verbose:
                    print(f"  {tag}: não publicado/indisponível", file=sys.stderr)
                if zp.exists():
                    zp.unlink()
                continue
        if verbose:
            print(f"Importando {tag} para SQLite (uma vez, 1-3 min)...", file=sys.stderr)
        ref = extrair_referencia(zp, cd)
        importar(ref, db, verbose)
        try:
            ref.unlink()
        except OSError:
            pass
        return db, tag
    raise SystemExit("Nenhum mês do SINAPI pôde ser baixado. Baixe manualmente em "
                     "https://www.caixa.gov.br/sinapi (relatórios mensais, formato xlsx) e use --arquivo <zip|xlsx> --mes AAAA-MM.")


def abrir(db):
    con = sqlite3.connect(db)
    con.row_factory = sqlite3.Row
    return con


def normaliza(s):
    import unicodedata
    s = unicodedata.normalize("NFD", str(s or "").lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")
