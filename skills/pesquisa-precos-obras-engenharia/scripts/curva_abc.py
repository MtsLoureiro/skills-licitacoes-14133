#!/usr/bin/env python3
"""Curva ABC de um orçamento (ordem decrescente de valor, % acumulado, classes A/B/C).

Os cortes 80% / 95% são CONVENÇÃO usual de engenharia de custos, não norma: ajuste com --corte-a e --corte-b e registre no processo.
(O art. 17 do Decreto 7.983/2013 usa "itens que somem 80% do valor" como amostra mínima de verificação em repasses: é outro uso.)

Entrada: CSV do orcamento.py (colunas item;descricao;total) ou qualquer CSV com --col-valor e --col-desc.
Uso:  curva_abc.py pesquisa/obra.orcamento.csv --out pesquisa/obra
"""
import argparse
import csv
import sys


def curva_abc(itens, corte_a=80.0, corte_b=95.0):
    """itens: lista de dicts com 'valor'. Devolve lista ordenada com pct, acumulado e classe."""
    tot = sum(i["valor"] for i in itens)
    if not tot:
        return []
    ordenados = sorted(itens, key=lambda x: x["valor"], reverse=True)
    acum, out = 0.0, []
    for i in ordenados:
        antes = acum
        acum += i["valor"]
        pct = i["valor"] / tot * 100 if tot else 0
        ac_pct = acum / tot * 100 if tot else 0
        # classe pelo acumulado ANTES do item: o item que cruza o corte ainda pertence à classe corrente
        classe = "A" if antes / tot * 100 < corte_a else ("B" if antes / tot * 100 < corte_b else "C")
        out.append(dict(i, pct=pct, acumulado=ac_pct, classe=classe))
    return out


def ler_valores(caminho, col_valor, col_desc):
    with open(caminho, encoding="utf-8-sig", newline="") as f:
        amostra = f.read(2048)
        f.seek(0)
        delim = ";" if amostra.count(";") >= amostra.count(",") else ","
        rd = csv.DictReader(f, delimiter=delim)
        itens = []
        for r in rd:
            v = r.get(col_valor, "").replace("R$", "").strip()
            if "," in v:
                v = v.replace(".", "").replace(",", ".")
            try:
                itens.append({"item": r.get("item", ""), "descricao": r.get(col_desc, ""), "valor": float(v)})
            except ValueError:
                continue
    return itens


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("entrada")
    ap.add_argument("--col-valor", default="total")
    ap.add_argument("--col-desc", default="descricao")
    ap.add_argument("--corte-a", type=float, default=80.0)
    ap.add_argument("--corte-b", type=float, default=95.0)
    ap.add_argument("--out", help="prefixo; grava <prefixo>.abc.csv")
    a = ap.parse_args()
    abc = curva_abc(ler_valores(a.entrada, a.col_valor, a.col_desc), a.corte_a, a.corte_b)
    if not abc:
        sys.exit("nenhum item lido")
    cont = {c: sum(1 for x in abc if x["classe"] == c) for c in "ABC"}
    print(f"{len(abc)} itens · A={cont['A']} · B={cont['B']} · C={cont['C']} (cortes {a.corte_a:g}% / {a.corte_b:g}%, convenção)")
    for x in abc[:15]:
        print(f"  {x['classe']}  {x['pct']:6.2f}%  acum {x['acumulado']:6.2f}%  R$ {x['valor']:>14,.2f}  {x['item']} {x['descricao'][:60]}")
    if a.out:
        with open(a.out + ".abc.csv", "w", encoding="utf-8-sig", newline="") as f:
            w = csv.writer(f, delimiter=";")
            w.writerow(["classe", "item", "descricao", "valor", "pct", "acumulado_pct"])
            for x in abc:
                w.writerow([x["classe"], x["item"], x["descricao"], round(x["valor"], 2), round(x["pct"], 4), round(x["acumulado"], 4)])
        print(f"Gravado: {a.out}.abc.csv", file=sys.stderr)


if __name__ == "__main__":
    main()
