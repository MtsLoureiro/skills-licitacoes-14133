#!/usr/bin/env python3
"""Estatística da pesquisa de preços -- funciona OFFLINE sobre o arquivo de buscar_precos.py.

Entrada: .json (lista de registros) ou .csv (separador ; ou , -- precisa da coluna do preço).
Saída: resumo no terminal e (com --out) <prefixo>.calculo.json, lido por gerar_mapa.py.

Etapas, todas registradas no resultado (nada some em silêncio):
  1. filtros objetivos (quantidade, UF, palavras, texto de alerta a excluir)
  2. remoção de duplicatas exatas (mesma compra+item+fornecedor+preço)
  3. atualização por fator (opcional, --fator; ver references/norma-comentada.md sobre índice)
  4. corte de valores inconsistentes/inexequíveis/excessivamente elevados, com critério
     EXPLÍCITO e configurável (--outliers): nenhum | iqr | mad | faixa-mediana
  5. estatísticas (n, média, mediana, menor, maior, desvio, coef. de variação)
  6. preço estimado pelo método escolhido (--metodo media|mediana|menor) e checagem do
     mínimo de preços (IN SEGES/ME 65/2021, art. 6º: 3 ou mais)

A IN 65/2021 NÃO fixa percentual de corte: o critério é escolha fundamentada de quem faz a
pesquisa (art. 6º §3º). Este script apenas aplica e documenta o critério que você escolher.
"""
import argparse
import csv
import json
import statistics as st
import sys


def ler_entrada(caminho, campo):
    if caminho.lower().endswith(".json"):
        with open(caminho, encoding="utf-8") as f:
            dados = json.load(f)
    else:
        with open(caminho, encoding="utf-8-sig", newline="") as f:
            amostra = f.read(4096)
            f.seek(0)
            delim = ";" if amostra.count(";") >= amostra.count(",") else ","
            dados = list(csv.DictReader(f, delimiter=delim))
    out = []
    for i, r in enumerate(dados, 1):
        r = dict(r)
        v = r.get(campo)
        if isinstance(v, str):
            v = v.replace("R$", "").strip()
            if "," in v:  # formato brasileiro 1.234,56
                v = v.replace(".", "").replace(",", ".")
            try:
                v = float(v)
            except ValueError:
                v = None
        r[campo] = v
        r.setdefault("_linha", i)
        if isinstance(r.get("alertas"), str):
            r["alertas"] = [x for x in r["alertas"].split(" | ") if x]
        out.append(r)
    return out


def numero(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def estatisticas(valores):
    if not valores:
        return {"n": 0}
    n = len(valores)
    media = st.fmean(valores)
    dp = st.stdev(valores) if n > 1 else 0.0
    return {
        "n": n, "media": media, "mediana": st.median(valores), "menor": min(valores),
        "maior": max(valores), "desvio_padrao": dp,
        "coef_variacao": (dp / media) if media else None,
    }


def limites_outlier(valores, criterio, k, z, inf, sup):
    """Devolve (limite_inferior, limite_superior, descricao) -- None = sem limite."""
    if criterio == "nenhum" or len(valores) < 4:
        return None, None, "nenhum corte aplicado" + (" (menos de 4 preços: corte estatístico não se aplica)" if criterio != "nenhum" else "")
    if criterio == "iqr":
        q1, _, q3 = st.quantiles(valores, n=4, method="inclusive")
        iqr = q3 - q1
        return q1 - k * iqr, q3 + k * iqr, f"IQR de Tukey: fora de [Q1 - {k}·IQR ; Q3 + {k}·IQR] (Q1={q1:.4f}, Q3={q3:.4f})"
    if criterio == "mad":
        med = st.median(valores)
        mad = st.median([abs(v - med) for v in valores])
        if mad == 0:
            return None, None, "MAD = 0 (mais da metade dos preços iguais): corte por MAD não aplicável"
        d = z * mad / 0.6745
        return med - d, med + d, f"MAD (escore z modificado > {z}): mediana={med:.4f}, MAD={mad:.4f}"
    if criterio == "faixa-mediana":
        med = st.median(valores)
        return med * inf, med * sup, f"faixa em torno da mediana: [{inf:g}×mediana ; {sup:g}×mediana], mediana={med:.4f}"
    raise SystemExit(f"critério desconhecido: {criterio}")


def processar(regs, a):
    campo = a.campo
    log = []  # decisões: {linha, motivo}
    ativos = []
    for r in regs:
        v = numero(r.get(campo))
        if v is None or v <= 0:
            r["_excluido"] = "preço ausente ou não positivo"
        else:
            r[campo] = v
            ativos_ok = True
            q = numero(r.get("quantidade"))
            if a.qtd_min is not None and (q is None or q < a.qtd_min):
                r["_excluido"], ativos_ok = f"quantidade < {a.qtd_min:g}", False
            elif a.qtd_max is not None and (q is None or q > a.qtd_max):
                r["_excluido"], ativos_ok = f"quantidade > {a.qtd_max:g}", False
            elif a.uf and (r.get("uf") or "").upper() not in [u.upper() for u in a.uf]:
                r["_excluido"], ativos_ok = "UF fora do filtro", False
            elif a.palavras and not all(p.lower() in (str(r.get("descricao", "")) + " " + str(r.get("descricao_detalhada", ""))).lower() for p in a.palavras):
                r["_excluido"], ativos_ok = "descrição não contém as palavras exigidas", False
            elif a.excluir_alerta and any(t.lower() in al.lower() for t in a.excluir_alerta for al in r.get("alertas", [])):
                r["_excluido"], ativos_ok = "alerta de qualidade excluído por filtro", False
            if ativos_ok:
                ativos.append(r)
    # duplicatas exatas
    vistos, unicos = set(), []
    for r in ativos:
        chave = (r.get("id_compra") or r.get("numero_controle_pncp"), r.get("numero_item"), r.get("cnpj_fornecedor"), r[campo])
        if chave in vistos and chave[0]:
            r["_excluido"] = "duplicata exata"
        else:
            vistos.add(chave)
            unicos.append(r)
    # fator de atualização
    for r in unicos:
        r["_valor"] = r[campo] * a.fator
    valores = [r["_valor"] for r in unicos]
    antes = estatisticas(valores)
    lo, hi, desc = limites_outlier(valores, a.outliers, a.k, a.z, a.faixa_inf, a.faixa_sup)
    mantidos = []
    for r in unicos:
        v = r["_valor"]
        if lo is not None and v < lo:
            r["_excluido"] = f"abaixo do limite inferior ({lo:.4f}): possível preço inexequível/inconsistente"
        elif hi is not None and v > hi:
            r["_excluido"] = f"acima do limite superior ({hi:.4f}): possível preço excessivamente elevado"
        else:
            mantidos.append(r)
    valores_ok = [r["_valor"] for r in mantidos]
    depois = estatisticas(valores_ok)
    estimado = None
    if valores_ok:
        estimado = {"media": depois["media"], "mediana": depois["mediana"], "menor": depois["menor"]}[a.metodo]
    avisos = []
    if len(valores_ok) < a.min_precos:
        avisos.append(f"Apenas {len(valores_ok)} preço(s) válido(s): mínimo é {a.min_precos} (IN SEGES/ME 65/2021, art. 6º, caput). "
                      "Só é admitido com justificativa nos autos e aprovação da autoridade competente (art. 6º §5º).")
    if depois.get("coef_variacao") and depois["coef_variacao"] > a.cv_alerta:
        avisos.append(f"Coeficiente de variação {depois['coef_variacao']:.0%} acima de {a.cv_alerta:.0%}: grande dispersão; "
                      "a IN 65/2021 (art. 6º §4º) exige análise crítica. Verifique unidade/embalagem/especificação antes de aceitar a média.")
    if a.metodo == "media" and depois.get("n", 0) >= 3 and depois["media"] > depois["mediana"] * 1.15:
        avisos.append("Média mais de 15% acima da mediana: cauda alta; considere a mediana ou revise o corte.")
    n_alerta = sum(1 for r in mantidos if [x for x in r.get("alertas", []) if not x.startswith("registro de preços")])
    if n_alerta:
        avisos.append(f"{n_alerta} dos {len(mantidos)} preços mantidos têm alertas de qualidade de dados além de SRP (ver coluna 'alertas'); revise antes de assinar.")
    return {
        "parametros": {
            "campo_preco": campo, "metodo": a.metodo, "outliers": a.outliers, "k_iqr": a.k, "z_mad": a.z,
            "faixa_inf": a.faixa_inf, "faixa_sup": a.faixa_sup, "fator_atualizacao": a.fator,
            "min_precos": a.min_precos, "qtd_min": a.qtd_min, "qtd_max": a.qtd_max, "uf": a.uf,
            "palavras": a.palavras, "excluir_alerta": a.excluir_alerta,
        },
        "criterio_corte": desc, "limite_inferior": lo, "limite_superior": hi,
        "entrada_total": len(regs), "apos_filtros_e_duplicatas": len(unicos),
        "estatisticas_antes_do_corte": antes, "estatisticas_finais": depois,
        "preco_estimado": estimado, "avisos": avisos,
        "mantidos": [limpar(r) for r in mantidos],
        "excluidos": [limpar(r) for r in regs if r.get("_excluido")],
    }


def limpar(r):
    return {k: v for k, v in r.items() if not k.startswith("_") or k in ("_excluido", "_valor", "_linha")}


def mostrar(res):
    f, a0 = res["estatisticas_finais"], res["estatisticas_antes_do_corte"]
    p = res["parametros"]
    print(f"Entrada: {res['entrada_total']} | após filtros/duplicatas: {res['apos_filtros_e_duplicatas']} | válidos: {f.get('n', 0)}")
    print(f"Corte: {res['criterio_corte']}")
    if a0.get("n"):
        print(f"Antes do corte : n={a0['n']} média={a0['media']:.4f} mediana={a0['mediana']:.4f} menor={a0['menor']:.4f} maior={a0['maior']:.4f}")
    if f.get("n"):
        cv = f["coef_variacao"]
        print(f"Depois do corte: n={f['n']} média={f['media']:.4f} mediana={f['mediana']:.4f} menor={f['menor']:.4f} "
              f"maior={f['maior']:.4f} dp={f['desvio_padrao']:.4f} CV={cv:.1%}" if cv is not None else "")
        print(f"PREÇO ESTIMADO ({p['metodo']}): R$ {res['preco_estimado']:.4f}")
    for av in res["avisos"]:
        print("ATENÇÃO:", av)
    if res["excluidos"]:
        print(f"Excluídos ({len(res['excluidos'])}):")
        for r in res["excluidos"][:15]:
            print(f"  linha {r.get('_linha')}: {r.get('_excluido')}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("entrada", help="arquivo .json/.csv gerado por buscar_precos.py (ou seu)")
    ap.add_argument("--campo", default="preco_unitario", help="coluna do preço (padrão preco_unitario)")
    ap.add_argument("--metodo", choices=["media", "mediana", "menor"], default="mediana",
                    help="método do preço estimado (IN 65/2021 art. 6º). Padrão: mediana, menos sensível a extremos")
    ap.add_argument("--outliers", choices=["nenhum", "iqr", "mad", "faixa-mediana"], default="iqr",
                    help="critério de corte (padrão iqr). Registre a justificativa no processo")
    ap.add_argument("--k", type=float, default=1.5, help="iqr: multiplicador (1.5 padrão; 3.0 = só extremos)")
    ap.add_argument("--z", type=float, default=3.5, help="mad: limite do escore z modificado")
    ap.add_argument("--faixa-inf", type=float, default=0.5, help="faixa-mediana: fração inferior da mediana")
    ap.add_argument("--faixa-sup", type=float, default=1.5, help="faixa-mediana: fração superior da mediana")
    ap.add_argument("--fator", type=float, default=1.0, help="fator de atualização monetária aplicado a todos os preços (1.0 = nenhum)")
    ap.add_argument("--min-precos", type=int, default=3, help="mínimo de preços válidos (padrão 3, IN 65 art. 6º)")
    ap.add_argument("--cv-alerta", type=float, default=0.25, help="avisar se coef. de variação passar disso (padrão 0.25)")
    ap.add_argument("--qtd-min", type=float, help="descarta registros com quantidade menor")
    ap.add_argument("--qtd-max", type=float, help="descarta registros com quantidade maior")
    ap.add_argument("--uf", nargs="+", help="mantém só estas UFs")
    ap.add_argument("--palavras", nargs="+", help="a descrição deve conter todas")
    ap.add_argument("--excluir-alerta", nargs="+", help="descarta registros cujo alerta contenha o texto (ex.: embalagem 'sem número')")
    ap.add_argument("--out", help="prefixo do arquivo de saída (<prefixo>.calculo.json)")
    a = ap.parse_args()

    res = processar(ler_entrada(a.entrada, a.campo), a)
    mostrar(res)
    if a.out:
        with open(a.out + ".calculo.json", "w", encoding="utf-8") as f:
            json.dump(res, f, ensure_ascii=False, indent=1)
        print(f"Gravado: {a.out}.calculo.json", file=sys.stderr)
    return 0 if res["preco_estimado"] is not None else 2


if __name__ == "__main__":
    sys.exit(main())
