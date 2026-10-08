"""Testes offline (sem rede) das ferramentas de orçamento de obras. Rodar: python3 tests/test_obras.py"""
import argparse
import csv
import os
import subprocess
import sys
import tempfile
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SC = os.path.join(RAIZ, "scripts")
sys.path.insert(0, SC)
sys.path.insert(0, os.path.join(RAIZ, "tests"))
import _sinapi as S  # noqa: E402
import bdi as B  # noqa: E402
import curva_abc as C  # noqa: E402
import make_fixture  # noqa: E402
import orcamento as O  # noqa: E402
import sinapi_buscar as SB  # noqa: E402


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.xlsx = make_fixture.criar(os.path.join(cls.tmp.name, "fix.xlsx"))
        cls.db = os.path.join(cls.tmp.name, "fix.sqlite")
        S.importar(cls.xlsx, cls.db, verbose=False)
        cls.con = S.abrir(cls.db)

    @classmethod
    def tearDownClass(cls):
        cls.con.close()
        cls.tmp.cleanup()


class Leitura(Base):
    def test_codigo_vem_da_formula_e_nao_do_valor_em_cache(self):
        x = S.Xlsx(self.xlsx)
        linha = [r for r in x.linhas("CSD") if r["_n"] == 11][0]
        self.assertEqual(linha["B"], 0)  # valor em cache é 0 (a armadilha)
        self.assertEqual(S.codigo_da_formula(linha["_f"]["B"]), 90001)

    def test_importacao(self):
        codigos = {r[0] for r in self.con.execute("select codigo from composicao_def where regime='nao-desonerado'")}
        self.assertEqual(codigos, {90001, 90002, 90003})
        r = self.con.execute("select custo, pct_as from composicao where codigo=90001 and uf='SP'").fetchone()
        self.assertEqual((r["custo"], r["pct_as"]), (120.0, 0.05))
        self.assertEqual(self.con.execute("select preco from insumo where codigo=1002 and uf='DF'").fetchone()[0], 100.0)
        self.assertIsNone(self.con.execute("select preco from insumo where codigo=1002 and uf='SP'").fetchone())  # em branco em SP
        m = dict(self.con.execute("select chave, valor from meta").fetchall())
        self.assertEqual(m["mes_referencia"], "01/2030")
        e = self.con.execute("select horista, mensalista from encargos where uf='DF'").fetchone()
        self.assertEqual((e[0], e[1]), (1.1, 0.7))

    def test_analitico_confere_com_custo(self):
        linhas, soma = SB.analitico(self.con, "nao-desonerado", "DF", 90001)
        self.assertEqual(len(linhas), 2)
        self.assertAlmostEqual(soma, 100.0)  # 50 x 1,00 + 0,5 x 100,00 = custo publicado


class Orcamento(Base):
    def args(self, **kw):
        d = dict(regime="nao-desonerado", uf="DF", bdi=25.0, arredondamento="arredondar")
        d.update(kw)
        return argparse.Namespace(**d)

    def test_calculo_com_bdi(self):
        itens, erros = O.montar([{"fonte": "SINAPI", "codigo": "90001", "quantidade": "10"}], self.con, self.args())
        self.assertEqual(erros, [])
        i = itens[0]
        self.assertEqual((i["custo"], i["preco_unitario"], i["total"]), (100.0, 125.0, 1250.0))

    def test_sem_preco_e_codigo_inexistente_viram_erro(self):
        itens, erros = O.montar([{"fonte": "SINAPI", "codigo": "90002", "quantidade": "1"},
                                 {"fonte": "SINAPI", "codigo": "55555", "quantidade": "1"}], self.con, self.args())
        self.assertEqual(itens, [])
        self.assertEqual(len(erros), 2)
        self.assertIn("SEM PREÇO", erros[0])
        self.assertIn("não invento", erros[1])

    def test_pct_as_gera_alerta_e_bdi_diferenciado(self):
        itens, _ = O.montar([{"fonte": "SINAPI", "codigo": "90003", "quantidade": "2", "bdi": "10"}], self.con, self.args())
        alertas = " ".join(itens[0]["alertas"])
        self.assertIn("%AS", alertas)
        self.assertIn("BDI diferenciado", alertas)
        self.assertEqual(itens[0]["preco_unitario"], 44.0)  # 40 x 1,10

    def test_fonte_propria_exige_custo_e_pede_referencia(self):
        _, erros = O.montar([{"fonte": "PROPRIA", "descricao": "x", "unidade": "UN", "quantidade": "1"}], self.con, self.args())
        self.assertTrue(erros)
        itens, erros = O.montar([{"fonte": "COTACAO", "descricao": "Bomba", "unidade": "UN", "quantidade": "1", "custo_unitario": "1000"}],
                                self.con, self.args())
        self.assertEqual(erros, [])
        self.assertTrue(any("cotação" in a for a in itens[0]["alertas"]))

    def test_truncar_x_arredondar(self):
        self.assertEqual(O.arred(1.239, "arredondar"), 1.24)
        self.assertEqual(O.arred(1.239, "truncar"), 1.23)

    def test_cli_ponta_a_ponta_com_arquivo_local(self):
        q = os.path.join(self.tmp.name, "q.csv")
        with open(q, "w", encoding="utf-8") as f:
            f.write("item;fonte;codigo;quantidade\n1;SINAPI;90001;10\n2;SINAPI;90003;100\n")
        env = dict(os.environ, OBRAS_CACHE=os.path.join(self.tmp.name, "cache"))
        pref = os.path.join(self.tmp.name, "saida", "orc")
        p = subprocess.run([sys.executable, os.path.join(SC, "orcamento.py"), q, "--uf", "DF", "--bdi", "25", "--arquivo", self.xlsx,
                            "--mes", "2030-01", "--out", pref], capture_output=True, text=True, env=env)
        self.assertEqual(p.returncode, 0, p.stderr)
        for ext in ("orcamento.csv", "abc.csv", "memoria.md", "justificativa.md", "orcamento.json"):
            self.assertGreater(os.path.getsize(f"{pref}.{ext}"), 50, ext)
        with open(f"{pref}.orcamento.csv", encoding="utf-8-sig") as f:
            linhas = list(csv.DictReader(f, delimiter=";"))
        self.assertEqual(sum(float(l["total"]) for l in linhas), 1250.0 + 5000.0)  # 10x125 + 100x(40x1,25=50)
        self.assertIn("SINAPI 2030-01", p.stdout)


class Bdi(unittest.TestCase):
    def test_sem_nada_e_zero(self):
        self.assertAlmostEqual(B.calcular_bdi(), 0.0)

    def test_so_tributos(self):
        self.assertAlmostEqual(B.calcular_bdi(iss=10), 100 * (1 / 0.9 - 1))

    def test_formula_completa(self):
        v = B.calcular_bdi(ac=4, s=0.8, r=1, g=0.8, df=1.2, l=7, pis=0.65, cofins=3, iss=3)
        esperado = ((1.066) * 1.012 * 1.07 / (1 - 0.0665) - 1) * 100
        self.assertAlmostEqual(v, esperado, places=6)

    def test_tributos_impossiveis(self):
        with self.assertRaises(ValueError):
            B.calcular_bdi(iss=100)


class Abc(unittest.TestCase):
    def test_classes(self):
        r = C.curva_abc([{"valor": v} for v in (700, 150, 100, 50)])
        self.assertEqual([x["classe"] for x in r], ["A", "A", "B", "C"])  # acumulado antes do item: 0, 70, 85, 95 (cortes 80/95)
        self.assertAlmostEqual(r[-1]["acumulado"], 100.0)

    def test_vazio(self):
        self.assertEqual(C.curva_abc([{"valor": 0}]), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
