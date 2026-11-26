"""Insertar filas en una hoja de un libro openpyxl corriendo TODAS las referencias de fórmulas del libro.

openpyxl.insert_rows mueve las celdas pero no toca las fórmulas, las celdas combinadas ni las alturas de fila
(skill cotizar-skids-equipos, punto 1: "desplazar a mano todas las referencias"). Esta función lo hace:
- fórmulas de la misma hoja (referencias sin prefijo) y de otras hojas que apuntan a ella ('Hoja'!A1, Hoja!A1:B2);
- rangos A1:B5 (cada extremo), con o sin $; no toca texto entre comillas ni nombres de función (LOG10( );
- celdas combinadas, alturas de fila, formato condicional y nombres definidos de esa hoja.
Uso: from excel_filas import insertar_filas; insertar_filas(wb, "Cotización", 71, 5)  # 5 filas nuevas antes de la 71.
Prueba: herramientas/test_excel_filas.py.
"""
import re
from openpyxl.worksheet.cell_range import CellRange

_REF = re.compile(
    r"(?P<pre>(?:'[^']+'|[A-Za-z_À-ÿ][\wÀ-ÿ\.]*)!)?"
    r"(?<![A-Za-z0-9_À-ÿ\.\$])(?P<c1>\$?[A-Z]{1,3})(?P<r1>\$?\d+)(?![\d(A-Za-z_])"
    r"(?::(?P<c2>\$?[A-Z]{1,3})(?P<r2>\$?\d+)(?![\d(A-Za-z_]))?")


def _nombre(pre):
    return pre[:-1].strip("'") if pre else None


def correr_formula(f, hoja_formula, hoja_objetivo, desde, n):
    """Devuelve la fórmula f (escrita en hoja_formula) con las filas >= desde de hoja_objetivo corridas n."""
    if not isinstance(f, str) or not f.startswith("="):
        return f

    def fila(r):
        absol = r.startswith("$")
        num = int(r.lstrip("$"))
        if num >= desde:
            num += n
        return ("$" if absol else "") + str(num)

    def rep(m):
        hoja = _nombre(m.group("pre")) or hoja_formula
        if hoja != hoja_objetivo:
            return m.group(0)
        s = (m.group("pre") or "") + m.group("c1") + fila(m.group("r1"))
        if m.group("c2"):
            s += ":" + m.group("c2") + fila(m.group("r2"))
        return s

    partes = re.split(r'("[^"]*")', f)  # no tocar textos entre comillas dobles
    return "".join(p if p.startswith('"') else _REF.sub(rep, p) for p in partes)


def insertar_filas(wb, hoja, desde, n):
    ws = wb[hoja]
    alturas = {r: d.height for r, d in ws.row_dimensions.items() if d.height is not None}
    combinadas = [CellRange(str(m)) for m in ws.merged_cells.ranges]
    for m in combinadas:
        ws.unmerge_cells(str(m))
    ws.insert_rows(desde, n)
    for m in combinadas:
        if m.min_row >= desde:
            m.shift(row_shift=n)
        elif m.max_row >= desde:
            m.expand(down=n)
        ws.merge_cells(str(m))
    for r, h in sorted(alturas.items(), reverse=True):
        if r >= desde:
            ws.row_dimensions[r + n].height = h
            ws.row_dimensions[r].height = None
    for w in wb.worksheets:
        for fila in w.iter_rows():
            for c in fila:
                if isinstance(c.value, str) and c.value.startswith("="):
                    c.value = correr_formula(c.value, w.title, hoja, desde, n)
    for nombre, d in list(wb.defined_names.items()):
        d.attr_text = correr_formula("=" + d.attr_text, None, hoja, desde, n)[1:]
    return ws
