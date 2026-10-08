"""Utilitários comuns: sessão HTTP com User-Agent de navegador, retry e cache em disco.

Só stdlib + requests. APIs públicas, sem chave.
"""
import json
import os
import sys
import time
from pathlib import Path

import requests

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
)
DADOS_ABERTOS = "https://dadosabertos.compras.gov.br"
PNCP = "https://pncp.gov.br"

_sess = None


def sessao():
    global _sess
    if _sess is None:
        _sess = requests.Session()
        _sess.headers.update({"User-Agent": UA, "Accept": "application/json"})
    return _sess


def get_json(url, params=None, tentativas=6, timeout=40, pausa=0.25):
    """GET com retry (timeout/5xx/429). Retorna (status, json|None).

    4xx (exceto 429) não é repetido: devolve o status para o chamador decidir.
    Algumas rotas do PNCP respondem 200 com corpo vazio quando não há dados.
    """
    ultimo = None
    for i in range(tentativas):
        try:
            r = sessao().get(url, params=params, timeout=timeout)
            if r.status_code == 429 or r.status_code >= 500:
                ultimo = f"HTTP {r.status_code}"
                espera = float(r.headers.get("Retry-After") or 0) if r.status_code == 429 else 0
                time.sleep(max(espera, 4 * (i + 1) if r.status_code == 429 else 1.5 * (i + 1)))
                continue
            time.sleep(pausa)
            if r.status_code == 200 and r.text.strip():
                try:
                    return 200, r.json()
                except ValueError:
                    return 200, None
            return r.status_code, None
        except requests.RequestException as e:
            ultimo = type(e).__name__
            time.sleep(1.5 * (i + 1))
    print(f"[aviso] falha em {url}: {ultimo}", file=sys.stderr)
    return 0, None


def paginar_dados_abertos(caminho, params, tam=500, max_paginas=40, verbose=True):
    """Percorre as páginas de um endpoint Dados Abertos (resposta {resultado,totalPaginas}).

    tamanhoPagina: mínimo 10, máximo 500 (testado em 10/2026).
    """
    todos = []
    pagina = 1
    while pagina <= max_paginas:
        p = dict(params, pagina=pagina, tamanhoPagina=tam)
        st, j = get_json(DADOS_ABERTOS + caminho, p, timeout=90)
        if st != 200 or not j:
            if verbose and st not in (200, 404):
                print(f"[aviso] {caminho} página {pagina}: status {st}", file=sys.stderr)
            break
        todos.extend(j.get("resultado", []))
        total = j.get("totalPaginas") or 1
        if pagina >= total:
            break
        pagina += 1
    return todos


def cache_dir():
    d = Path(os.environ.get("PNCP_CACHE", "")) if os.environ.get("PNCP_CACHE") else Path.home() / ".cache" / "pesquisa-precos-pncp"
    d.mkdir(parents=True, exist_ok=True)
    return d


def cache_ler(nome, validade_dias=30):
    f = cache_dir() / nome
    if f.exists() and (time.time() - f.stat().st_mtime) < validade_dias * 86400:
        return json.loads(f.read_text(encoding="utf-8"))
    return None


def cache_gravar(nome, obj):
    (cache_dir() / nome).write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")


def link_pncp(numero_controle):
    """'{cnpj}-1-{seq6}/{ano}' -> URL da página pública da contratação no PNCP."""
    try:
        cnpj, _, resto = numero_controle.split("-", 2)
        seq, ano = resto.split("/")
        return f"{PNCP}/app/editais/{cnpj}/{ano}/{int(seq)}"
    except (ValueError, AttributeError):
        return ""
