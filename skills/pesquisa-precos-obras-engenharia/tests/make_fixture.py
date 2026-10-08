"""Gera um XLSX minúsculo com a MESMA estrutura da planilha 'Referência' do SINAPI (dados FICTÍCIOS).

Reproduz as armadilhas reais: código da composição como FÓRMULA HYPERLINK(...MATCH(cod,...)) com valor em cache 0,
UFs em linhas de cabeçalho (insumos: 1 coluna por UF; composições: pares Custo/%AS), aba Analítico com a estrutura.
"""
import zipfile
from xml.sax.saxutils import escape


def _cell(col, row, v):
    if v is None:
        return ""
    ref = f"{col}{row}"
    if isinstance(v, tuple):  # (valor_em_cache, formula)
        return f'<c r="{ref}"><f>{escape(v[1])}</f><v>{v[0]}</v></c>'
    if isinstance(v, (int, float)):
        return f'<c r="{ref}"><v>{v}</v></c>'
    return f'<c r="{ref}" t="inlineStr"><is><t>{escape(str(v))}</t></is></c>'


def _sheet(rows):
    xml = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>']
    for n in sorted(rows):
        xml.append(f'<row r="{n}">' + "".join(_cell(c, n, v) for c, v in rows[n].items()) + "</row>")
    xml.append("</sheetData></worksheet>")
    return "".join(xml)


def hyperlink(cod):
    return (0, f'HYPERLINK("#"&CELL("address",OFFSET(Analítico!$B$1,MATCH({cod},Analítico!$B:$B,0)-1,3)),{cod})')


def abas():
    isd = {
        1: {"A": "SINAPI - FIXTURE FICTICIA"}, 2: {"A": "RELATÓRIO DE PREÇOS DE INSUMOS - ENCARGOS SOCIAIS SEM DESONERAÇÃO"},
        3: {"A": "Mês de Referência:", "B": "01/2030"}, 4: {"A": "Data de emissão:", "B": "01/02/2030", "E": "(SEM DESONERAÇÃO)", "F": "DF", "G": "SP"},
        6: {"E": "Horista", "F": 1.1, "G": 1.2}, 7: {"E": "Mensalista", "F": 0.7, "G": 0.8},
        10: {"A": "Classificação", "B": "Código do\nInsumo", "C": "Descrição do Insumo", "D": "Unidade", "E": "Origem de\nPreço", "F": "DF", "G": "SP"},
        11: {"A": "MATERIAL", "B": 1001, "C": "CIMENTO FICTICIO", "D": "KG", "E": "C", "F": 1.0, "G": 1.2},
        12: {"A": "MATERIAL", "B": 1002, "C": "AREIA FICTICIA", "D": "M3", "E": "CR", "F": 100.0},  # sem preço em SP
    }
    csd = {
        1: {"A": "SINAPI - FIXTURE FICTICIA"}, 2: {"A": "RELATÓRIO DE CUSTOS DE COMPOSIÇÕES - ENCARGOS SOCIAIS SEM DESONERAÇÃO"},
        3: {"A": "Mês de Referência:", "B": "01/2030"}, 4: {"A": "Data de emissão:", "B": "01/02/2030", "D": "(SEM DESONERAÇÃO)", "E": "DF", "G": "SP"},
        6: {"D": "Horista", "E": 1.1, "G": 1.2}, 7: {"D": "Mensalista", "E": 0.7, "G": 0.8},
        9: {"E": "DF", "G": "SP"},
        10: {"A": "Grupo", "B": "Código da\nComposição", "C": "Descrição", "D": "Unidade", "E": "Custo (R$)", "F": "%AS", "G": "Custo (R$)", "H": "%AS"},
        11: {"A": "TESTE", "B": hyperlink(90001), "C": "ARGAMASSA FICTICIA", "D": "M3", "E": 100.0, "F": 0, "G": 120.0, "H": 0.05},
        12: {"A": "TESTE", "B": hyperlink(90002), "C": "SERVICO FICTICIO SEM PRECO NO DF", "D": "M2", "E": 0, "F": 0, "G": 50.0, "H": 0},
        13: {"A": "TESTE", "B": hyperlink(90003), "C": "PAREDE FICTICIA", "D": "M2", "E": 40.0, "F": 0.02, "G": 45.0, "H": 0},
    }
    ana = {
        10: {"A": "Grupo", "B": "Código da\nComposição", "C": "Tipo Item", "D": "Código do Item", "E": "Descrição", "F": "Unidade", "G": "Coeficiente", "H": "Situação"},
        11: {"A": "TESTE", "B": 90001, "E": "ARGAMASSA FICTICIA", "F": "M3", "H": "COM PREÇO"},
        12: {"A": "TESTE", "B": 90001, "C": "INSUMO", "D": 1001, "E": "CIMENTO FICTICIO", "F": "KG", "G": 50.0, "H": "COM PREÇO"},
        13: {"A": "TESTE", "B": 90001, "C": "INSUMO", "D": 1002, "E": "AREIA FICTICIA", "F": "M3", "G": 0.5, "H": "COM PREÇO"},
    }
    return {"ISD": isd, "CSD": csd, "Analítico": ana}


def criar(caminho):
    a = abas()
    nomes = list(a)
    with zipfile.ZipFile(caminho, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="xml" ContentType="application/xml"/></Types>')
        sheets = "".join(f'<sheet name="{n}" sheetId="{i}" r:id="rId{i}"/>' for i, n in enumerate(nomes, 1))
        z.writestr("xl/workbook.xml", f'<?xml version="1.0"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>{sheets}</sheets></workbook>')
        rels = "".join(f'<Relationship Id="rId{i}" Target="worksheets/sheet{i}.xml" Type="x"/>' for i in range(1, len(nomes) + 1))
        z.writestr("xl/_rels/workbook.xml.rels", f'<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">{rels}</Relationships>')
        for i, n in enumerate(nomes, 1):
            z.writestr(f"xl/worksheets/sheet{i}.xml", _sheet(a[n]))
    return caminho


if __name__ == "__main__":
    import sys
    print(criar(sys.argv[1] if len(sys.argv) > 1 else "fixture_sinapi.xlsx"))
