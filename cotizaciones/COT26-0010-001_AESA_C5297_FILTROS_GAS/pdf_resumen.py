"""Arma resumen_diseno.html con el plano, los pesos y la lista de materiales del filtro FCC-707/708 (COT26-0010-001).

Uso: python dimensionamiento.py && python pdf_resumen.py   (después se imprime a PDF con Chromium: ver bitacora.md)
Lee arreglo_general.svg, la sección 4 de dimensionamiento.md y pedido/lista_materiales_plano.csv. No calcula nada.
"""
import csv
import html
import re
from pathlib import Path

A = Path(__file__).resolve().parent
md = (A / "dimensionamiento.md").read_text(encoding="utf-8")
svg = (A / "arreglo_general.svg").read_text(encoding="utf-8")
svg = re.sub(r'width="1180" height="900"', 'width="100%" height="184mm"', svg, count=1)   # entra en una hoja A4 apaisada
sec4 = md.split("## 4. Peso (por filtro)")[1].split("## 5.")[0]
tablas = [[[c.strip() for c in f.strip().strip("|").split("|")] for f in bloque.strip().splitlines() if not set(f) <= set("|- ")]
          for bloque in re.findall(r"((?:^\|.*\n)+)", sec4, flags=re.M)]
e = html.escape
neg = lambda s: re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", e(s))


def tabla(filas, clases=""):
    cab, cuerpo = filas[0], filas[1:]
    return (f'<table class="{clases}"><thead><tr>' + "".join(f"<th>{e(c)}</th>" for c in cab) + "</tr></thead><tbody>"
            + "".join("<tr>" + "".join(f"<td>{neg(c)}</td>" for c in f) + "</tr>" for f in cuerpo) + "</tbody></table>")


def num(x):
    try:
        v = float(x)
    except ValueError:
        return x
    return (f"{v:,.2f}".replace(",", "§").replace(".", ",").replace("§", ".")).replace(",00", "") if v != int(v) else f"{int(v)}"


lista = list(csv.DictReader(open(A / "pedido" / "lista_materiales_plano.csv", encoding="utf-8")))
filas = [["Pos", "Descripción (texto del cliente)", "Ø", "Serie / Sch", "Material (texto del cliente)", "Cant.", "Un.", "Detalle de ITT"]]
for r in lista:
    sch = " / ".join(x for x in (r["serie_sch"], ("Sch " + r["schedule"]) if r["schedule"] and "Sch" not in r["serie_sch"] else "") if x)
    filas.append([r["pos"], r["descripcion"], r["diametro"], sch, r["material"], num(r["cantidad"]) + (" (*)" if r["cantidad_origen"] else ""), r["unidad"], r["nota"]])
pie = "COT26-0010-001 · AESA C5297 PC-02 LANor · FCC-707/708 · BORRADOR, SIN REVISAR · predimensionamiento de ITT para cotizar, no es documento de fabricación"
doc = f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><title>FCC-707/708 diseño preliminar</title><style>
@page {{ size: A4 landscape; margin: 10mm 10mm 12mm 10mm; }}
body {{ font-family: Arial, Helvetica, sans-serif; font-size: 9.5pt; color: #111; margin: 0; }}
h1 {{ font-size: 14pt; margin: 0 0 2mm; }} h2 {{ font-size: 11pt; margin: 3mm 0 1.5mm; }}
.aviso {{ color: #a00; font-size: 9pt; margin: 0 0 3mm; }} .pag {{ page-break-after: always; }}
table {{ border-collapse: collapse; width: 100%; }} th, td {{ border: 0.4pt solid #888; padding: 0.7mm 1.4mm; vertical-align: top; text-align: left; }}
th {{ background: #e8e8e8; }} thead {{ display: table-header-group; }} tr {{ page-break-inside: avoid; }}
.pesos td:nth-child(3), .pesos th:nth-child(3), .tot td:nth-child(2), .tot th:nth-child(2) {{ text-align: right; white-space: nowrap; }}
.pesos {{ width: 72%; font-size: 8.6pt; }} .tot {{ width: 45%; }} .lista {{ font-size: 7.4pt; }} .lista td:nth-child(8) {{ width: 46%; }} .lista td:nth-child(1), .lista td:nth-child(6) {{ white-space: nowrap; }}
.nota {{ font-size: 8.5pt; color: #333; margin-top: 2mm; }}
</style></head><body>
<div class="pag">{svg}</div>
<div class="pag"><h1>FCC-707/708 · Filtro de gas de emergencia · Pesos (por filtro)</h1><p class="aviso">{pie}</p>
{tabla(tablas[0], "pesos")}<h2>Resumen</h2>{tabla(tablas[1], "tot")}
<p class="nota">Origen: tabla = tablas de pesos de bridas, caños y accesorios (bridas ±15 %, accesorios ±10–15 %); calculado = volumen × 7,85; estimado = pieza sin definir.
Son 2 filtros: el pedido completo pesa el doble. Detalle y cálculo en dimensionamiento.md.</p></div>
<div><h1>FCC-707/708 · Lista de materiales (por filtro; el pedido son 2 filtros)</h1><p class="aviso">{pie}</p>
{tabla(filas, "lista")}
<p class="nota">(*) El cliente no indica cantidad: calculada por ITT según la hoja de datos 5297-02-0600-IG-EM-HD-001 E0. Descripción y material: texto de la hoja de datos y de la requisición del cliente;
lo que define ITT está en la última columna. Sin definir: válvulas de drenaje y venteo, tapón del drenaje y junta de la tapa (falta la clase de cañerías CA11) y el elemento filtrante (a confirmar con el fabricante).</p></div>
</body></html>"""
(A / "resumen_diseno.html").write_text(doc, encoding="utf-8")
print("resumen_diseno.html:", len(lista), "renglones;", len(tablas[0]) - 1, "filas de peso")
