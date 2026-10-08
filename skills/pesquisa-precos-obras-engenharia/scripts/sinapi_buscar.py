#!/usr/bin/env python3
"""Busca composições e insumos do SINAPI por código ou texto, para uma UF e um regime.

Exemplos:
  sinapi_buscar.py comp "contrapiso espessura 5" --uf DF --regime nao-desonerado
  sinapi_buscar.py comp --codigo 87298 --uf DF --analitico      # estrutura (insumos x coeficiente x preço) e conferência da soma
  sinapi_buscar.py insumo "cimento portland" --uf DF
  sinapi_buscar.py meses                                          # bases já preparadas

Regime (OBRIGATÓRIO escolher conscientemente): nao-desonerado | desonerado | sem-encargos. A escolha tem de combinar com o regime
tributário da folha usado no BDI (CPRB): ver references/bdi-encargos.md. Padrão aqui: nao-desonerado.
Texto: todas as palavras precisam aparecer (sem acento / maiúscula). %AS > 0 = parte do preço foi atribuída a partir de SP.
"""
import argparse
import json
import sys

import _sinapi as S


def abrir_base(a):
    db, tag = S.garantir_base(a.mes, a.arquivo, verbose=False)
    return S.abrir(db), tag


def achar_comp(con, regime, uf, codigo=None, termos=None, limite=30):
    if codigo:
        rows = con.execute("""select d.codigo,d.grupo,d.descricao,d.unidade,c.custo,c.pct_as from composicao_def d
            join composicao c on c.regime=d.regime and c.codigo=d.codigo where d.regime=? and c.uf=? and d.codigo=?""", (regime, uf, codigo)).fetchall()
        return rows
    todos = con.execute("""select d.codigo,d.grupo,d.descricao,d.unidade,c.custo,c.pct_as from composicao_def d
        join composicao c on c.regime=d.regime and c.codigo=d.codigo where d.regime=? and c.uf=?""", (regime, uf)).fetchall()
    out = [r for r in todos if all(t in S.normaliza(r["descricao"] + " " + (r["grupo"] or "")) for t in termos)]
    return out[:limite]


def achar_ins(con, regime, uf, codigo=None, termos=None, limite=30):
    sql = """select d.codigo,d.classificacao,d.descricao,d.unidade,d.origem,i.preco from insumo_def d
        join insumo i on i.regime=d.regime and i.codigo=d.codigo where d.regime=? and i.uf=?"""
    if codigo:
        return con.execute(sql + " and d.codigo=?", (regime, uf, codigo)).fetchall()
    todos = con.execute(sql, (regime, uf)).fetchall()
    return [r for r in todos if all(t in S.normaliza(r["descricao"]) for t in termos)][:limite]


def analitico(con, regime, uf, codigo):
    """Itens da composição com preço/custo unitário na UF e conferência: soma(coef x preço) ≈ custo da composição."""
    itens = con.execute("select tipo,item,descricao,unidade,coef,situacao from estrutura where comp=?", (codigo,)).fetchall()
    linhas, soma = [], 0.0
    for it in itens:
        if it["tipo"] == "INSUMO":
            r = con.execute("select preco, 0.0 as pct from insumo where regime=? and codigo=? and uf=?", (regime, it["item"], uf)).fetchone()
        else:
            r = con.execute("select custo as preco, pct_as as pct from composicao where regime=? and codigo=? and uf=?", (regime, it["item"], uf)).fetchone()
        pu = r["preco"] if r else None
        parcial = (pu or 0) * (it["coef"] or 0)
        soma += parcial
        linhas.append({"tipo": it["tipo"], "codigo": it["item"], "descricao": it["descricao"], "unidade": it["unidade"],
                       "coef": it["coef"], "preco_unit": pu, "parcial": parcial, "situacao": it["situacao"]})
    return linhas, soma


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("tipo", choices=["comp", "insumo", "meses"])
    ap.add_argument("texto", nargs="?", default="")
    ap.add_argument("--codigo", type=int)
    ap.add_argument("--uf", default="DF")
    ap.add_argument("--regime", choices=list(S.REGIMES), default="nao-desonerado")
    ap.add_argument("--mes", help="AAAA-MM (padrão: mais recente disponível)")
    ap.add_argument("--arquivo", help="ZIP/XLSX local (fallback manual)")
    ap.add_argument("--analitico", action="store_true", help="(comp) mostra a estrutura e confere a soma")
    ap.add_argument("--limite", type=int, default=25)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    if a.tipo == "meses":
        for f in sorted(S.cache_dir().glob("sinapi-*.sqlite")):
            print(f.name)
        return
    a.uf = a.uf.upper()
    con, tag = abrir_base(a)
    termos = S.normaliza(a.texto).split()
    if not a.codigo and not termos:
        sys.exit("Informe um texto ou --codigo")
    ref = dict(con.execute("select chave, valor from meta").fetchall())
    cab = f"SINAPI {tag} (ref. {ref.get('mes_referencia')}) · {a.uf} · {a.regime}"
    if a.tipo == "comp":
        rs = achar_comp(con, a.regime, a.uf, a.codigo, termos, a.limite)
        if a.json:
            print(json.dumps([dict(r) for r in rs], ensure_ascii=False, indent=1))
            return
        print(cab + f" — {len(rs)} composição(ões)")
        for r in rs:
            alerta = f"  [%AS={r['pct_as']:.1%}: parte do preço atribuída de SP]" if r["pct_as"] and r["pct_as"] > 0 else ""
            print(f"  {r['codigo']:>7}  {r['unidade']:<4} R$ {r['custo']:>11,.2f}  {r['descricao']}{alerta}")
        if a.analitico and a.codigo and rs:
            linhas, soma = analitico(con, a.regime, a.uf, a.codigo)
            print(f"\nEstrutura da composição {a.codigo}:")
            for l in linhas:
                pu = "sem preço na UF" if l["preco_unit"] is None else f"{l['preco_unit']:,.4f}"
                print(f"  {l['tipo']:<10} {l['codigo']:>7}  coef {l['coef']:<9.5g} {l['unidade']:<4} pu {pu:>16}  parcial {l['parcial']:>10,.4f}  {l['descricao'][:70]}")
            custo = rs[0]["custo"]
            dif = abs(soma - custo)
            print(f"\nSoma(coef x preço) = {soma:,.4f}  |  custo publicado = {custo:,.4f}  |  diferença = {dif:,.4f}"
                  + ("  OK" if dif <= max(0.02, custo * 0.002) else "  ATENÇÃO: diferença acima de 0,2% (item sem preço na UF / preço atribuído de SP / arredondamento)"))
    else:
        rs = achar_ins(con, a.regime, a.uf, a.codigo, termos, a.limite)
        if a.json:
            print(json.dumps([dict(r) for r in rs], ensure_ascii=False, indent=1))
            return
        print(cab + f" — {len(rs)} insumo(s)")
        for r in rs:
            print(f"  {r['codigo']:>7}  {r['unidade']:<4} R$ {r['preco']:>11,.2f}  origem {r['origem'] or '-':<3} {r['descricao']}")


if __name__ == "__main__":
    main()
