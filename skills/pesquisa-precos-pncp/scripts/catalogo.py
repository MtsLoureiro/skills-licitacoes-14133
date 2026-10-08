#!/usr/bin/env python3
"""Acha o código CATMAT (material) ou CATSER (serviço) de um objeto.

Por que local: os filtros de texto da API de catálogo (nomePdm, descricaoItem) são
IGNORADOS pelo servidor (testado em 10/2026) -- devolvem tudo ou nada. Então o script
baixa a lista do catálogo uma vez (PDM ~20 mil registros, ~20 s; serviços ~3 mil),
guarda em cache (30 dias) e busca por palavras no seu computador.

Subcomandos:
  pdm      "papel sulfite a4"        -> PDMs (padrão descritivo de material) que casam
  itens    --pdm 19746 [--filtro "297 x 210 75 g"]  -> itens CATMAT do PDM, filtrados
  servico  "limpeza conservacao"     -> serviços CATSER que casam

Saída: tabela legível (padrão) ou --json.
"""
import argparse
import json
import sys
import unicodedata

from _pncp import cache_gravar, cache_ler, paginar_dados_abertos


def norm(s):
    s = unicodedata.normalize("NFD", str(s or "").lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def casa(texto, termos):
    t = norm(texto)
    return all(p in t for p in termos)


def carregar_pdm(forcar=False):
    dados = None if forcar else cache_ler("pdm.json")
    if dados is None:
        print("Baixando catálogo de PDM (uma vez, ~20 s)...", file=sys.stderr)
        dados = paginar_dados_abertos("/modulo-material/3_consultarPdmMaterial", {}, max_paginas=60)
        if dados:
            cache_gravar("pdm.json", dados)
    return dados


def carregar_servicos(forcar=False):
    dados = None if forcar else cache_ler("servicos.json")
    if dados is None:
        print("Baixando catálogo de serviços (uma vez)...", file=sys.stderr)
        dados = paginar_dados_abertos("/modulo-servico/6_consultarItemServico", {}, max_paginas=20)
        if dados:
            cache_gravar("servicos.json", dados)
    return dados


def cmd_pdm(a):
    termos = norm(a.termo).split()
    res = [x for x in carregar_pdm(a.atualizar) if casa(x["nomePdm"], termos) or casa(x.get("nomeClasse", ""), termos)]
    if not a.inativos:
        res = [x for x in res if x.get("statusPdm")]
    res = res[: a.limite]
    if a.json:
        print(json.dumps(res, ensure_ascii=False, indent=1))
        return
    print(f"{len(res)} PDM(s). Use o código em: catalogo.py itens --pdm <código>")
    for x in res:
        print(f"  PDM {x['codigoPdm']:>6}  {x['nomePdm']}  [{x.get('nomeClasse','')}]")


def cmd_itens(a):
    itens = paginar_dados_abertos("/modulo-material/4_consultarItemMaterial", {"codigoPdm": a.pdm})
    termos = norm(a.filtro).split() if a.filtro else []
    res = [x for x in itens if x.get("statusItem") and casa(x["descricaoItem"], termos)]
    if a.json:
        print(json.dumps(res, ensure_ascii=False, indent=1))
        return
    print(f"{len(res)} item(ns) CATMAT ativos de {len(itens)} no PDM {a.pdm}. Use o código em: buscar_precos.py --catmat <código>")
    for x in res[: a.limite]:
        print(f"  CATMAT {x['codigoItem']:>7}  {x['descricaoItem'].strip()}")


def cmd_servico(a):
    termos = norm(a.termo).split()
    res = [x for x in carregar_servicos(a.atualizar) if x.get("statusServico") and casa(x["nomeServico"], termos)]
    res = res[: a.limite]
    if a.json:
        print(json.dumps(res, ensure_ascii=False, indent=1))
        return
    print(f"{len(res)} serviço(s). Use o código em: buscar_precos.py --catser <código>")
    for x in res:
        print(f"  CATSER {x['codigoServico']:>6}  {x['nomeServico']}  [{x.get('nomeClasse','')}]")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for nome, fn, arg in (("pdm", cmd_pdm, "termo"), ("servico", cmd_servico, "termo"), ("itens", cmd_itens, None)):
        p = sub.add_parser(nome)
        if arg:
            p.add_argument(arg, help="palavras (todas precisam aparecer; sem acento/maiúscula)")
        else:
            p.add_argument("--pdm", type=int, required=True, help="código do PDM")
            p.add_argument("--filtro", default="", help="palavras para filtrar a descrição do item")
        p.add_argument("--limite", type=int, default=40)
        p.add_argument("--json", action="store_true")
        p.add_argument("--atualizar", action="store_true", help="rebaixa o catálogo em cache")
        if nome == "pdm":
            p.add_argument("--inativos", action="store_true", help="inclui PDM desativado")
        p.set_defaults(fn=fn)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
