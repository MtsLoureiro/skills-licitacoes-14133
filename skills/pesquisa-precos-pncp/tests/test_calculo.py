"""Testes offline do cálculo. Rodar: python3 tests/test_calculo.py  (sem rede)."""
import json
import os
import statistics
import subprocess
import sys
import tempfile
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "scripts"))
import calcular_precos as cp  # noqa: E402

FIXTURE = os.path.join(RAIZ, "tests", "fixture_precos.json")
BOM = [22.90, 23.50, 24.10, 24.80, 25.00, 25.40, 25.90, 26.30, 26.80, 27.20]


def args(**kw):
    import argparse
    base = dict(campo="preco_unitario", metodo="mediana", outliers="iqr", k=1.5, z=3.5, faixa_inf=0.5, faixa_sup=1.5,
                fator=1.0, min_precos=3, cv_alerta=0.25, qtd_min=None, qtd_max=None, uf=None, palavras=None, excluir_alerta=None)
    base.update(kw)
    return argparse.Namespace(**base)


class Calculo(unittest.TestCase):
    def regs(self):
        return cp.ler_entrada(FIXTURE, "preco_unitario")

    def test_iqr_remove_extremos_e_duplicata(self):
        r = cp.processar(self.regs(), args())
        self.assertEqual(r["entrada_total"], 13)
        self.assertEqual(r["apos_filtros_e_duplicatas"], 12)          # 1 duplicata exata
        self.assertEqual(r["estatisticas_finais"]["n"], 10)             # 2.35 e 89.90 cortados
        self.assertAlmostEqual(r["preco_estimado"], statistics.median(BOM), places=6)
        motivos = " ".join(x["_excluido"] for x in r["excluidos"])
        self.assertIn("duplicata exata", motivos)
        self.assertIn("inexequível", motivos)
        self.assertIn("excessivamente elevado", motivos)

    def test_metodos(self):
        self.assertAlmostEqual(cp.processar(self.regs(), args(metodo="media"))["preco_estimado"], statistics.fmean(BOM), places=6)
        self.assertAlmostEqual(cp.processar(self.regs(), args(metodo="menor"))["preco_estimado"], 22.90, places=6)

    def test_sem_corte_mantem_tudo(self):
        r = cp.processar(self.regs(), args(outliers="nenhum"))
        self.assertEqual(r["estatisticas_finais"]["n"], 12)
        self.assertTrue(any("variação" in a for a in r["avisos"]))      # CV alto avisa

    def test_faixa_mediana_e_mad(self):
        self.assertEqual(cp.processar(self.regs(), args(outliers="faixa-mediana"))["estatisticas_finais"]["n"], 10)
        self.assertEqual(cp.processar(self.regs(), args(outliers="mad"))["estatisticas_finais"]["n"], 10)

    def test_minimo_de_precos(self):
        r = cp.processar(self.regs(), args(qtd_min=1100))               # sobram poucos
        self.assertLess(r["estatisticas_finais"]["n"], 3)
        self.assertTrue(any("mínimo" in a for a in r["avisos"]))

    def test_fator_e_filtro_uf(self):
        r = cp.processar(self.regs(), args(fator=1.1, uf=["DF"]))
        self.assertTrue(all(m["uf"] == "DF" for m in r["mantidos"]))
        self.assertAlmostEqual(min(m["_valor"] for m in r["mantidos"]), 22.90 * 1.1, places=6)

    def test_cli_e_mapa(self):
        with tempfile.TemporaryDirectory() as d:
            pref = os.path.join(d, "x")
            sc = os.path.join(RAIZ, "scripts")
            p = subprocess.run([sys.executable, os.path.join(sc, "calcular_precos.py"), FIXTURE, "--out", pref], capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stderr)
            p = subprocess.run([sys.executable, os.path.join(sc, "gerar_mapa.py"), pref + ".calculo.json", "--out", pref, "--titulo", "Papel A4 (teste)"], capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stderr)
            for ext in ("mapa.csv", "memoria.md", "justificativa.md"):
                self.assertTrue(os.path.getsize(f"{pref}.{ext}") > 100, ext)
            self.assertIn("https://pncp.gov.br/app/editais/", open(pref + ".mapa.csv", encoding="utf-8-sig").read())


if __name__ == "__main__":
    unittest.main(verbosity=2)
