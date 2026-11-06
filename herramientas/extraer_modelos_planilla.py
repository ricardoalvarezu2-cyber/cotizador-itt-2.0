"""Extrae la lista de componentes de las planillas "OFERTA ..." de ITT (formato viejo 2017–2020: hojas Pres., Mat.,
M.O., Repuestos) a un CSV con columnas fijas. Lo usó la carga de los modelos de separador coalescente (06-11-2026).

Uso: python herramientas/extraer_modelos_planilla.py CARPETA_CON_PLANILLAS SALIDA.csv

Criterios (ver conocimiento/tecnico/separadores_coalescentes_LEEME.md):
- La hoja Mat. trae arriba un bloque de plantilla heredado de otra oferta (tags PSV21103, LV21103, proveedores
  CONVER/FUTURA/ESFEROMATIC) sin cantidad. El bloque real empieza en la fila con el título del equipo
  ("SEPARADOR COALESCENTE 24\"", "SEPARADOR COLAESCENTE VERTICAL DE Ø22” ...") debajo de la fila 20. Si no hay
  título, se lee toda la hoja.
- Solo se toman renglones con cantidad > 0 (una fila con cantidad vacía no suma en la planilla).
- Repuestos se lee desde el primer encabezado: también trae arriba el bloque de plantilla, pero sin cantidad (no entra).
- Algunas celdas están bajo otro encabezado (42" 32 mm, fila 137: el Sch 80 de un codo está en "Esp."): se copian
  tal cual; el renglón original queda en la última columna.
- Los precios son los de la planilla (USD, sin IVA, de 2017–2020): sirven como referencia de proporciones, no
  como precio vigente. No se cargan al catálogo de materiales.
"""
import csv
import datetime
import re
import sys
from pathlib import Path

import openpyxl
import xlrd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from numeros import fecha_iso  # noqa: E402

COLUMNAS = ["archivo", "fecha_planilla", "hoja", "fila", "pos", "item", "cantidad", "descripcion", "material",
            "diametro", "largo_mm", "schedule", "serie", "espesor_mm", "ancho_mm", "tipo", "comentario", "proveedor",
            "plazo", "notas", "precio_unitario_usd", "precio_total_usd", "renglon_original"]

# encabezado de la planilla -> columna del CSV
MAPA = {
    "Pos.": "pos", "Item": "item", "Cant.": "cantidad", "Descripción": "descripcion", "Material": "material",
    "Øn": "diametro", "Øn(\")": "diametro", "Ø": "diametro", "Ø(\")": "diametro", "Øe(\")": "diametro", "Øe(mm)": "diametro",
    "Largo": "largo_mm", "Largo (mm)": "largo_mm", "Sch": "schedule", "Sch.": "schedule", "Serie": "serie", "SERIE": "serie",
    "ESP (mm)": "espesor_mm", "Esp.": "espesor_mm", "Esp (mm)": "espesor_mm", "ANCHO": "ancho_mm", "ANCHO (mm)": "ancho_mm", "Tipo": "tipo",
    "Comentarios": "comentario", "Observasiones": "comentario", "Proveedor": "proveedor", "Plazo de entrega": "plazo",
}


def limpio(v, datemode=None):
    if v is None:
        return ""
    if isinstance(v, datetime.datetime):
        return v.date().isoformat()
    if isinstance(v, float):
        return ("%d" % v) if v == int(v) else ("%.4f" % v).rstrip("0").rstrip(".")
    return re.sub(r"\s+", " ", str(v)).strip()


def hojas(ruta):
    if ruta.suffix.lower() == ".xls":
        wb = xlrd.open_workbook(str(ruta))
        for s in wb.sheets():
            filas = []
            for r in range(s.nrows):
                fila = []
                for c in range(s.ncols):
                    v = s.cell_value(r, c)
                    if s.cell_type(r, c) == xlrd.XL_CELL_DATE:
                        v = datetime.datetime(*xlrd.xldate_as_tuple(v, wb.datemode))
                    fila.append(v)
                filas.append(fila)
            yield s.name.strip(), filas
    else:
        wb = openpyxl.load_workbook(ruta, data_only=True)
        for ws in wb:
            yield ws.title.strip(), [[c.value for c in row] for row in ws.iter_rows()]


def fecha_de(filas):
    """Fecha del presupuesto: celda a la derecha de "FECHA" en las primeras filas de la hoja Pres."""
    for f in filas[:8]:
        for j, v in enumerate(f):
            if limpio(v) == "FECHA":
                for w in f[j + 1:]:
                    if w not in (None, ""):
                        if isinstance(w, float):  # serial de Excel
                            w = datetime.datetime(1899, 12, 30) + datetime.timedelta(days=w)
                        return fecha_iso(w) or ""
    return ""


def numero(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def extraer(ruta, base):
    salida = []
    contenido = list(hojas(ruta))
    fecha = next((fecha_de(f) for n, f in contenido if n == "Pres."), "")
    for nombre, filas in contenido:
        if nombre not in ("Mat.", "Repuestos"):
            continue
        ini = 0
        if nombre == "Mat.":
            for i, f in enumerate(filas):
                a = limpio(f[0]) if f else ""
                if i > 20 and re.search(r"(?i)separador|colaescente|coalescente", a) and sum(1 for x in f if limpio(x)) <= 2:
                    ini = i
                    break
        enc = None
        for i in range(ini, len(filas)):
            f = [limpio(x) for x in filas[i]]
            if "Cant." in f:
                enc = [x.strip() for x in f]
                continue
            if enc is None:
                continue
            if any("Total Costo Materiales" in x for x in f):
                break
            d, precios, original, notas = {}, [], [], []
            for j in range(min(len(enc), len(f))):
                if not f[j] or f[j] == "0":
                    continue
                original.append(f"{enc[j] or '?'}={f[j]}")
                if not enc[j] and numero(f[j]) is None:
                    notas.append(f[j])  # celda sin encabezado con texto: nota al margen (cotización, fecha, "Estimado"...);
                    # los números sueltos (incidencia %, $/m sin encabezado) quedan solo en renglon_original
                col = MAPA.get(enc[j])
                if col and col not in d:
                    d[col] = f[j]
                if enc[j] in ("Pr.($)", "Pr.T.($)"):
                    precios.append((enc[j], f[j]))
            cant = numero(d.get("cantidad"))
            if not cant or cant <= 0:
                continue
            # precio: con Pr.T.($) el Pr.($) es unitario; con dos Pr.($) el primero es unitario y el segundo total;
            # con uno solo es el total del renglón (caños y chapas: $/m o $/kg × medida).
            unit = total = ""
            if any(k == "Pr.T.($)" for k, _ in precios):
                unit = next((v for k, v in precios if k == "Pr.($)"), "")
                total = next(v for k, v in precios if k == "Pr.T.($)")
            elif len(precios) >= 2:
                unit, total = precios[0][1], precios[-1][1]
            elif precios:
                total = precios[0][1]
                if numero(total) is not None:
                    unit = limpio(numero(total) / cant)
            fila = {c: d.get(c, "") for c in COLUMNAS}
            fila.update({"archivo": str(ruta.relative_to(base)), "fecha_planilla": fecha, "hoja": nombre, "fila": i + 1,
                         "precio_unitario_usd": unit, "precio_total_usd": total, "notas": " · ".join(notas), "renglon_original": " | ".join(original)})
            salida.append(fila)
    return salida


def main():
    base, sal = Path(sys.argv[1]), Path(sys.argv[2])
    filas = []
    for ruta in sorted(p for p in base.rglob("*") if p.suffix.lower() in (".xls", ".xlsx")):
        filas += extraer(ruta, base)
    with open(sal, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNAS)
        w.writeheader()
        w.writerows(filas)
    print(f"{sal}: {len(filas)} renglones de {len({f['archivo'] for f in filas})} planillas")


if __name__ == "__main__":
    main()
