#!/usr/bin/env python3
"""Coleta preços unitários HOMOLOGADOS de contratações similares (PNCP / Compras.gov.br).

Duas rotas:

 A) Por código de catálogo (recomendada) -- Dados Abertos "Pesquisa de Preço":
      buscar_precos.py --catmat 461848 --dias 365 --out saida/papel
      buscar_precos.py --catser 15083  --uf DF
    Devolve item a item o preço unitário homologado, fornecedor, órgão, UF, quantidade
    e unidade de fornecimento. Depois liga cada compra ao número de controle do PNCP
    (link público) pela rota 1.1_consultarContratacoes_PNCP_14133_Id.

 B) Por texto livre -- busca do PNCP (/api/search) + itens + resultados:
      buscar_precos.py --texto "notebook 16gb ssd" --palavras "notebook,16gb" --max-compras 30
    Use quando o objeto não tem CATMAT/CATSER claro. Mais lenta (1 chamada por compra).

Saída: arquivo .json (completo) e .csv (planilha) com o prefixo de --out; resumo no stderr.
Cada registro traz `alertas` (ver references/qualidade-dados.md). Nada é descartado aqui:
o saneamento é feito em calcular_precos.py, com critério explícito.
"""
import argparse
import csv
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta

from _pncp import (DADOS_ABERTOS, PNCP, cache_gravar, cache_ler, get_json,
                   link_pncp, paginar_dados_abertos)

MODALIDADES = {  # código Compras.gov "modalidade"/codigoModalidade (Lei 14.133)
    3: "Concorrência eletrônica", 4: "Concorrência presencial", 5: "Pregão eletrônico",
    6: "Dispensa", 7: "Inexigibilidade",
}
CAMPOS = [
    "fonte", "data_resultado", "preco_unitario", "unidade_fornecimento", "capacidade_unidade",
    "unidade_medida", "quantidade", "fornecedor", "cnpj_fornecedor", "marca", "orgao", "uasg",
    "uf", "municipio", "esfera", "modalidade", "forma", "numero_item", "descricao",
    "id_compra", "numero_controle_pncp", "link_pncp", "alertas",
]


def para_data(s):
    try:
        return datetime.strptime((s or "")[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


def alertas_registro(r):
    a = []
    if (r.get("preco_unitario") or 0) <= 0:
        a.append("preço zero/negativo")
    if not r.get("unidade_fornecimento") and not r.get("unidade_medida"):
        a.append("sem unidade de medida informada")
    if (r.get("quantidade") or 0) in (0, 1) and r.get("fonte") == "comprasgov":
        a.append("quantidade 0/1: pode ser lance/estimativa, não volume real")
    if str(r.get("descricao", "")).strip().lower().startswith(("lote", "grupo")):
        a.append("item de lote/grupo: o valor pode ser global do lote, não unitário do item")
    if r.get("desconto_percentual"):
        a.append(f"critério por desconto ({r['desconto_percentual']}%): preço unitário pode não refletir o valor final")
    if r.get("forma") == "SISRP":
        a.append("registro de preços (SRP): preço de ata, não necessariamente contratado")
    if not r.get("numero_controle_pncp"):
        a.append("sem número de controle PNCP: compra fora do PNCP/regime anterior; fonte difícil de comprovar")
    return a


def chave_unidade(r):
    return ((r.get("unidade_fornecimento") or r.get("unidade_medida") or "?").upper(), r.get("capacidade_unidade") or 0)


def marcar_unidade_divergente(regs):
    """Alerta nos registros cuja unidade/embalagem difere da predominante (risco de comparar maçã com pera)."""
    from collections import Counter
    if not regs:
        return
    cont = Counter(chave_unidade(r) for r in regs)
    (un, cap), n = cont.most_common(1)[0]
    print(f"Unidade predominante: {un}" + (f" com {cap:g} unid." if cap else "") + f" ({n} de {len(regs)}). Outras: "
          + (", ".join(f"{k[0]}/{k[1]:g}×{v}" for k, v in cont.items() if k != (un, cap)) or "nenhuma"), file=sys.stderr)
    for r in regs:
        if chave_unidade(r) != (un, cap) and "?" not in chave_unidade(r)[0]:
            r["alertas"].append(f"unidade/embalagem ({chave_unidade(r)[0]}, cap. {chave_unidade(r)[1]:g}) difere da predominante ({un}, cap. {cap:g}): "
                                "preço pode não ser comparável; converter ou excluir (--excluir-alerta difere)")


def normalizar_comprasgov(x, tipo):
    r = {
        "fonte": "comprasgov",
        "id_compra": str(x.get("idCompra") or ""),
        "id_item_compra": x.get("idItemCompra"),
        "numero_item": x.get("numeroItemCompra"),
        "codigo_catalogo": x.get("codigoItemCatalogo"),
        "tipo_catalogo": tipo,
        "descricao": (x.get("descricaoItem") or "").strip(),
        "descricao_detalhada": (x.get("descricaoDetalhadaItem") or "").strip(),
        "preco_unitario": x.get("precoUnitario"),
        "quantidade": x.get("quantidade"),
        "unidade_fornecimento": x.get("siglaUnidadeFornecimento") or x.get("nomeUnidadeFornecimento"),
        "capacidade_unidade": x.get("capacidadeUnidadeFornecimento"),
        "unidade_medida": x.get("siglaUnidadeMedida") or x.get("nomeUnidadeMedida"),
        "fornecedor": x.get("nomeFornecedor"),
        "cnpj_fornecedor": x.get("niFornecedor"),
        "marca": x.get("marca"),
        "orgao": x.get("nomeOrgao"),
        "uasg": x.get("codigoUasg"),
        "uf": x.get("estado"),
        "municipio": x.get("municipio"),
        "esfera": x.get("esfera"),
        "poder": x.get("poder"),
        "modalidade": MODALIDADES.get(x.get("modalidade"), f"código {x.get('modalidade')} (CONFERIR)"),
        "forma": x.get("forma"),
        "criterio_julgamento": x.get("criterioJulgamento"),
        "desconto_percentual": x.get("percentualMaiorDesconto") or 0,
        "data_compra": x.get("dataCompra"),
        "data_resultado": x.get("dataResultado"),
        "objeto_compra": (x.get("objetoCompra") or "").strip(),
        "numero_controle_pncp": "",
        "link_pncp": "",
    }
    return r


def enriquecer_pncp(registros, workers=3):
    """Liga idCompra -> numeroControlePNCP (cache em disco por idCompra)."""
    ids = sorted({r["id_compra"] for r in registros if r["id_compra"]})
    cache = cache_ler("idcompra_pncp.json", validade_dias=365) or {}
    faltam = [i for i in ids if i not in cache]

    def um(i):
        st, j = get_json(DADOS_ABERTOS + "/modulo-contratacoes/1.1_consultarContratacoes_PNCP_14133_Id",
                         {"tipo": "idCompra", "codigo": i})
        if st == 200 and j and j.get("resultado"):
            return i, j["resultado"][0].get("numeroControlePNCP") or ""
        return i, ("" if st in (200, 404) else None)  # None = erro de rede: não gravar no cache

    if faltam:
        print(f"Ligando {len(faltam)} compra(s) ao PNCP...", file=sys.stderr)
        with ThreadPoolExecutor(workers) as ex:
            for k, (i, nc) in enumerate(ex.map(um, faltam), 1):
                if nc is not None:
                    cache[i] = nc
                if k % 50 == 0:
                    print(f"  {k}/{len(faltam)}", file=sys.stderr)
                    cache_gravar("idcompra_pncp.json", cache)
        cache_gravar("idcompra_pncp.json", cache)
    for r in registros:
        nc = cache.get(r["id_compra"], "")
        r["numero_controle_pncp"] = nc
        r["link_pncp"] = link_pncp(nc) if nc else ""


def rota_catalogo(a):
    inicio = (date.today() - timedelta(days=a.dias)).isoformat()
    fim = date.today().isoformat()
    filtros = {"dataCompraInicio": inicio, "dataCompraFim": fim}
    if a.uf:
        filtros["estado"] = a.uf.upper()
    if a.esfera:
        filtros["esfera"] = a.esfera.upper()
    if a.catmat:
        brutos = []
        for cod in a.catmat:
            brutos += [(x, "CATMAT") for x in paginar_dados_abertos(
                "/modulo-pesquisa-preco/1_consultarMaterial",
                dict(filtros, tipo="codigoItemCatalogo", codigo=cod))]
    else:
        brutos = []
        for cod in a.catser:
            brutos += [(x, "CATSER") for x in paginar_dados_abertos(
                "/modulo-pesquisa-preco/3_consultarServico", dict(filtros, codigoItemCatalogo=cod))]
    return [normalizar_comprasgov(x, t) for x, t in brutos]


def rota_texto(a):
    """Busca textual no PNCP -> itens da compra que casam com as palavras -> resultados."""
    palavras = [p.strip().lower() for p in (a.palavras or a.texto).replace(",", " ").split() if p.strip()]
    achadas, pagina = [], 1
    while len(achadas) < a.max_compras and pagina <= 10:
        st, j = get_json(PNCP + "/api/search/", {
            "q": a.texto, "tipos_documento": "edital", "status": "todos",
            "pagina": pagina, "tam_pagina": 50, "ordenacao": "-data"})
        if st != 200 or not j or not j.get("items"):
            break
        achadas += [i for i in j["items"] if i.get("numero_controle_pncp") and i.get("tem_resultado")]
        pagina += 1
    vistos, compras = set(), []
    for i in achadas:  # deduplica por número de controle
        if i["numero_controle_pncp"] not in vistos:
            vistos.add(i["numero_controle_pncp"])
            compras.append(i)
    compras = compras[: a.max_compras]
    limite = date.today() - timedelta(days=a.dias)

    def uma(c):
        nc = c["numero_controle_pncp"]
        cnpj, _, resto = nc.split("-", 2)
        seq, ano = resto.split("/")
        base = f"{PNCP}/api/pncp/v1/orgaos/{cnpj}/compras/{ano}/{int(seq)}/itens"
        st, itens = get_json(base, {"pagina": 1, "tamanhoPagina": 500})
        out = []
        for it in itens or []:
            desc = (it.get("descricao") or "").lower()
            if not it.get("temResultado") or not all(p in desc for p in palavras):
                continue
            st, res = get_json(f"{base}/{it['numeroItem']}/resultados")
            for rs in res or []:
                if rs.get("situacaoCompraItemResultadoNome", "").lower().startswith("cancel") or rs.get("dataCancelamento"):
                    continue
                d = para_data(rs.get("dataResultado"))
                if d and d < limite:
                    continue
                out.append({
                    "fonte": "pncp", "id_compra": "", "numero_item": it["numeroItem"],
                    "descricao": (it.get("descricao") or "").strip(),
                    "preco_unitario": rs.get("valorUnitarioHomologado"),
                    "quantidade": rs.get("quantidadeHomologada"),
                    "unidade_fornecimento": it.get("unidadeMedida"), "capacidade_unidade": None,
                    "unidade_medida": None,
                    "fornecedor": rs.get("nomeRazaoSocialFornecedor"), "cnpj_fornecedor": rs.get("niFornecedor"),
                    "marca": None, "orgao": c.get("orgao_nome"), "uasg": c.get("unidade_codigo"),
                    "uf": c.get("uf"), "municipio": c.get("municipio_nome"),
                    "esfera": c.get("esfera_id"), "poder": c.get("poder_id"),
                    "modalidade": c.get("modalidade_licitacao_nome"), "forma": None,
                    "desconto_percentual": rs.get("percentualDesconto") or 0,
                    "data_compra": (c.get("data_publicacao_pncp") or "")[:10],
                    "data_resultado": rs.get("dataResultado"),
                    "objeto_compra": c.get("description"), "numero_controle_pncp": nc,
                    "link_pncp": link_pncp(nc),
                    "situacao_item": it.get("situacaoCompraItemNome"),
                })
        return out

    regs = []
    with ThreadPoolExecutor(6) as ex:
        for out in ex.map(uma, compras):
            regs += out
    return regs


def filtrar(regs, a):
    limite = date.today() - timedelta(days=a.dias)
    ok = []
    for r in regs:
        d = para_data(r.get("data_resultado")) or para_data(r.get("data_compra"))
        if d and d < limite:
            continue  # a API pode devolver registros mais antigos que a janela
        if a.uf and (r.get("uf") or "").upper() != a.uf.upper():
            continue
        if a.palavras and r["fonte"] == "comprasgov":  # na rota B o filtro já foi aplicado item a item
            txt = (r["descricao"] + " " + r.get("descricao_detalhada", "")).lower()
            if not all(p.strip().lower() in txt for p in a.palavras.split(",") if p.strip()):
                continue
        if a.excluir_palavras:
            txt = (r["descricao"] + " " + r.get("descricao_detalhada", "")).lower()
            if any(p.strip().lower() in txt for p in a.excluir_palavras.split(",") if p.strip()):
                continue
        ok.append(r)
    return ok


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--catmat", type=int, nargs="+", help="código(s) CATMAT (material) -- achar com catalogo.py")
    g.add_argument("--catser", type=int, nargs="+", help="código(s) CATSER (serviço)")
    g.add_argument("--texto", help="busca textual livre no PNCP (rota B)")
    ap.add_argument("--dias", type=int, default=365, help="janela de busca em dias (padrão 365 = art. 23 §1º II Lei 14.133)")
    ap.add_argument("--uf", help="filtrar por UF (ex.: DF); sem filtro = Brasil todo")
    ap.add_argument("--esfera", help="F federal, E estadual, M municipal (rota A)")
    ap.add_argument("--palavras", help="palavras que a descrição deve conter (vírgula); ex.: '75 g,a4'")
    ap.add_argument("--excluir-palavras", help="descarta item cuja descrição contenha alguma (vírgula); ex.: 'fonte,bateria,locação'")
    ap.add_argument("--max-compras", type=int, default=30, help="rota B: máximo de compras a abrir")
    ap.add_argument("--sem-link", action="store_true", help="rota A: não buscar número de controle PNCP (mais rápido)")
    ap.add_argument("--out", help="prefixo dos arquivos de saída (gera .json e .csv)")
    a = ap.parse_args()

    regs = rota_texto(a) if a.texto else rota_catalogo(a)
    n_bruto = len(regs)
    regs = filtrar(regs, a)
    if regs and regs[0]["fonte"] == "comprasgov" and not a.sem_link:
        enriquecer_pncp(regs)
    for r in regs:
        r["alertas"] = alertas_registro(r)
    marcar_unidade_divergente(regs)

    print(f"{n_bruto} registro(s) brutos; {len(regs)} após filtros (janela {a.dias} dias"
          + (f", UF {a.uf}" if a.uf else "") + ").", file=sys.stderr)
    com_link = sum(1 for r in regs if r["link_pncp"])
    print(f"{com_link} com link PNCP; {sum(1 for r in regs if r['alertas'])} com algum alerta.", file=sys.stderr)

    if a.out:
        with open(a.out + ".json", "w", encoding="utf-8") as f:
            json.dump(regs, f, ensure_ascii=False, indent=1)
        with open(a.out + ".csv", "w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=CAMPOS, extrasaction="ignore", delimiter=";")
            w.writeheader()
            for r in regs:
                w.writerow(dict(r, alertas=" | ".join(r["alertas"])))
        print(f"Gravado: {a.out}.json e {a.out}.csv", file=sys.stderr)
    else:
        json.dump(regs, sys.stdout, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
