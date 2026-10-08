#!/usr/bin/env python3
"""Calculadora de BDI (Benefícios e Despesas Indiretas) pela fórmula consolidada do TCU.

    BDI = [ (1 + AC + S + R + G) x (1 + DF) x (1 + L) / (1 - I) ] - 1

  AC administração central · S seguro · R risco · G garantia · DF despesas financeiras · L lucro
  I = soma das alíquotas sobre o preço de venda: PIS + COFINS + ISS (+ CPRB, só no regime desonerado)

Todos os parâmetros em PERCENTUAL (ex.: --ac 3.8). Esta é a forma de fórmula usada pela jurisprudência do TCU
(Acórdão 2622/2013-Plenário, que também fixou faixas referenciais por tipo de obra). CONFERIR no inteiro teor do acórdão
antes de citar; o script NÃO traz as faixas porque não pôde confirmá-las: passe a faixa do SEU tipo de obra em --faixa MIN,MAX
para receber o aviso de enquadramento. A taxa adequada é a do caso concreto (TCU, Acórdão 1666/2017-Plenário, ementa):
alíquotas reais de ISS do município, PIS/COFINS pelo regime da empresa, CPRB só se o orçamento for desonerado.

Exemplos:
  bdi.py --ac 4 --s 0.8 --r 1 --g 0.8 --df 1.2 --l 7 --pis 0.65 --cofins 3 --iss 3 --out-json bdi.json
  bdi.py --ac 4 --s 0.8 --r 1 --g 0.8 --df 1.2 --l 7 --pis 0.65 --cofins 3 --iss 3 --cprb 4.5 --faixa 20,26
"""
import argparse
import json
import sys


def calcular_bdi(ac=0.0, s=0.0, r=0.0, g=0.0, df=0.0, l=0.0, pis=0.0, cofins=0.0, iss=0.0, cprb=0.0):
    """Entradas em %, saída em % (ex.: 24.5). Levanta ValueError se I >= 100%."""
    i = (pis + cofins + iss + cprb) / 100.0
    if i >= 1:
        raise ValueError("soma dos tributos sobre o preço >= 100%")
    bdi = ((1 + (ac + s + r + g) / 100.0) * (1 + df / 100.0) * (1 + l / 100.0) / (1 - i)) - 1
    return bdi * 100.0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for k, h in (("ac", "administração central"), ("s", "seguro"), ("r", "risco"), ("g", "garantia"), ("df", "despesas financeiras"),
                 ("l", "lucro"), ("pis", "PIS"), ("cofins", "COFINS"), ("iss", "ISS (alíquota real do município e base de cálculo)"),
                 ("cprb", "CPRB (somente orçamento desonerado)")):
        ap.add_argument("--" + k, type=float, default=0.0, help=h + " em %%")
    ap.add_argument("--faixa", help="MIN,MAX (%%) do tipo de obra, para aviso de enquadramento (você confere a faixa na fonte)")
    ap.add_argument("--out-json")
    a = ap.parse_args()
    par = {k: getattr(a, k) for k in ("ac", "s", "r", "g", "df", "l", "pis", "cofins", "iss", "cprb")}
    try:
        bdi = calcular_bdi(**par)
    except ValueError as e:
        sys.exit(f"erro: {e}")
    print(f"BDI = {bdi:.2f}%   (I = {a.pis + a.cofins + a.iss + a.cprb:.2f}%)")
    if a.cprb:
        print("Atenção: CPRB incluída => use SINAPI DESONERADO nos custos diretos (mesmo regime).")
    elif a.pis or a.cofins or a.iss:
        print("Sem CPRB => use SINAPI NÃO DESONERADO nos custos diretos (mesmo regime).")
    if a.faixa:
        lo, hi = (float(x) for x in a.faixa.split(","))
        print("Dentro da faixa informada." if lo <= bdi <= hi else f"FORA da faixa informada ({lo:g}%–{hi:g}%): justifique no processo (TCU: avaliar caso concreto).")
    if a.out_json:
        json.dump({"parametros_pct": par, "bdi_pct": bdi}, open(a.out_json, "w"), indent=1)


if __name__ == "__main__":
    main()
