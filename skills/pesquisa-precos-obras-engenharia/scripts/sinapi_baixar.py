#!/usr/bin/env python3
"""Baixa e prepara a tabela SINAPI de um mês (cache local em SQLite).

A Caixa publica UM ZIP por mês com TODAS as UFs e os 3 regimes (não desonerado, desonerado, sem encargos):
  https://www.caixa.gov.br/Downloads/sinapi-relatorios-mensais/SINAPI-AAAA-MM-formato-xlsx.zip
(formato antigo por UF, "sinapi-a-partir-jul-2009-<uf>/SINAPI_ref_Insumos_Composicoes_<UF>_AAAAMM_*.zip", devolve 404: não use.)

Uso:
  sinapi_baixar.py                         # mês mais recente publicado (caminha para trás a partir do mês corrente)
  sinapi_baixar.py --mes 2026-08           # mês específico
  sinapi_baixar.py --arquivo SINAPI-2026-08-formato-xlsx.zip --mes 2026-08   # arquivo que você já baixou (fallback manual)
  sinapi_baixar.py --listar                # meses já preparados no cache

O download exige User-Agent de navegador; a Caixa devolve HTML com status 200 para mês inexistente (por isso validamos o
conteúdo ZIP, não o status). O mês corrente costuma ainda NÃO estar publicado; a tabela sai em geral no mês seguinte.
Cache: ~/.cache/pesquisa-precos-obras (mude com a variável OBRAS_CACHE).
"""
import argparse

import _sinapi as S


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mes", help="AAAA-MM")
    ap.add_argument("--arquivo", help="ZIP ou XLSX 'Referência' já baixado (exige --mes se o nome não tiver AAAA-MM)")
    ap.add_argument("--listar", action="store_true")
    ap.add_argument("--refazer", action="store_true", help="apaga o SQLite do mês e importa de novo")
    a = ap.parse_args()
    if a.listar:
        for f in sorted(S.cache_dir().glob("sinapi-*.sqlite")):
            con = S.abrir(f)
            m = dict(con.execute("select chave, valor from meta").fetchall())
            print(f"{f.name}  mês-ref {m.get('mes_referencia')}  emissão {m.get('data_emissao')}  {f.stat().st_size/1e6:.0f} MB")
        return
    if a.refazer and a.mes:
        p = S.cache_dir() / f"sinapi-{a.mes}.sqlite"
        if p.exists():
            p.unlink()
    db, tag = S.garantir_base(a.mes, a.arquivo)
    con = S.abrir(db)
    m = dict(con.execute("select chave, valor from meta").fetchall())
    nc = con.execute("select count(*) from composicao_def where regime='nao-desonerado'").fetchone()[0]
    ni = con.execute("select count(*) from insumo_def where regime='nao-desonerado'").fetchone()[0]
    print(f"Pronto: SINAPI {tag} (referência {m.get('mes_referencia')}, emissão {m.get('data_emissao')}) — {nc} composições, {ni} insumos")
    print(f"Base: {db}")


if __name__ == "__main__":
    main()
