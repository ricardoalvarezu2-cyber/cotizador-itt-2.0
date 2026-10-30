"""Listas de precios que carga Ventas (fuentes_originales/listas_vendedor/<fecha de carga>/) → conocimiento/precios/listas_vendedor.csv

Uso: python herramientas/listas_vendedor.py   (lo corre actualizar_base.py antes de los catálogos)

Cada renglón conserva la fecha del documento (no la de carga): con eso el catálogo decide cuál precio es el más nuevo y
ajusta por inflación. Formatos conocidos:
  renard_lista_AAAA-MM-DD.xlsx       hojas "Table N": Código | Producto | Precio (usd/Un) | Unidad
  cintolo_lista_*_AAAA-MM-DD.xlsx    ARTIC. | DESCRIPCION | ESPESOR | NORMA | CALIDAD | PRECIO USD
  provemet_cotizacion_*_AAAA-MM-DD.pdf   cotización Provemet (perfiles, caños, bridas): # | descripción | [kg/m] | cant | unid | precio | … | neto
Un archivo de otro formato se avisa y no se carga (pedir que lo lea la IA y lo pase a conocimiento/precios/listas_nuevas.csv).
"""
import csv
import re
import subprocess
import sys
from pathlib import Path

from openpyxl import load_workbook

RAIZ = Path(__file__).resolve().parent.parent
ORIGEN = RAIZ / "fuentes_originales" / "listas_vendedor"
SALIDA = RAIZ / "conocimiento" / "precios" / "listas_vendedor.csv"
CAMPOS = ["fecha", "proveedor", "codigo", "descripcion", "precio", "moneda", "unidad", "iva", "tipo_precio", "archivo_origen", "fecha_carga", "nota"]


def fecha_de(nombre):
    m = re.search(r"(\d{4}-\d{2}-\d{2})", nombre)
    if not m:
        sys.exit(f"{nombre}: el nombre tiene que llevar la fecha del documento (AAAA-MM-DD)")
    return m.group(1)


def renard(ruta, base):
    wb = load_workbook(ruta, data_only=True)
    for ws in wb.worksheets:
        categoria = ""
        for r in ws.iter_rows(values_only=True):
            v = [x for x in r if x is not None]
            if not v:
                continue
            if isinstance(v[0], str) and "RENARD" in v[0].upper():
                categoria = v[0].split("\n")[0].strip()
                continue
            if isinstance(v[0], (int, float)) and len(v) >= 3 and isinstance(v[2], (int, float)) and v[2] > 0:
                yield {**base, "codigo": int(v[0]), "descripcion": f"{v[1]} ({categoria})" if categoria else str(v[1]),
                       "precio": round(float(v[2]), 2), "unidad": (v[3] if len(v) > 3 else "un") or "un"}


def cintolo(ruta, base):
    ws = load_workbook(ruta, data_only=True).worksheets[0]
    for r in ws.iter_rows(values_only=True):
        if r and isinstance(r[0], (int, float)) and isinstance(r[-1], (int, float)) and r[-1] > 0:
            art, desc, esp, norma, calidad, precio = (list(r) + [None] * 6)[:6]
            yield {**base, "codigo": int(art), "descripcion": " ".join(str(x) for x in (desc, esp, norma, calidad) if x),
                   "precio": round(float(precio), 2), "unidad": "un"}


def provemet(ruta, base):
    """Cotización de Grupo Provemet (perfiles, caños, bridas): # | descripción (1 o 2 renglones) | [kg/m] | cant | unid | precio |
    [bonif.] | neto | unid | total. Se toma el precio neto; un ítem en 0 («Lamentamos no cotizar») no se carga."""
    texto = subprocess.run(["pdftotext", "-layout", str(ruta), "-"], capture_output=True, text=True, check=True).stdout
    renglones = texto.splitlines()
    item = re.compile(r"^\s*(\d+)\s+(.*?)\s*(?:(\d+\.\d+)\s+)?(\d+\.\d+)\s+(Mt|U)\s+([\d.]+)\s+(?:[\d.]+\s+)?([\d.]+)\s+(Mt|U)\s+[\d.]+")
    for i, linea in enumerate(renglones):
        m = item.match(linea)
        if not m:
            continue
        desc, kgm, unid, neto = m.group(2).strip(), m.group(3), m.group(5), float(m.group(7))
        if not desc:  # el texto quedó en el renglón de arriba (ítem con entregas partidas)
            desc = re.split(r"\s{2,}", renglones[i - 1].strip())[0]
        if neto <= 0:
            continue
        sig = renglones[i + 1].strip() if i + 1 < len(renglones) else ""
        if desc.startswith("PERFIL "):  # el segundo renglón es el largo (12000 mm)
            desc = f"{desc} ({kgm} kg/m, barra de 12 m)"
        else:
            if sig and not item.match(renglones[i + 1]):
                desc = f"{desc} {re.split(r'\s{2,}', sig)[0]}"
            if kgm:
                desc = f"{desc} ({kgm} kg/m)"
        yield {**base, "codigo": "", "descripcion": desc, "precio": round(neto, 2), "unidad": "metro" if unid == "Mt" else "un"}


FORMATOS = [(r"^renard_lista", renard, "Tubos Renard", "lista", "sin IVA (lista Renard en USD)"),
            (r"^cintolo_lista", cintolo, "Cintolo Hnos.", "lista", "no dice: se toma sin IVA"),
            (r"^provemet_cotizacion", provemet, "Grupo Provemet", "cotización", "sin IVA (lo dice: «los precios no incluyen IVA»)")]


def main():
    filas, avisos = [], []
    for carpeta in sorted(p for p in ORIGEN.glob("*") if p.is_dir()):
        for ruta in sorted(carpeta.iterdir()):
            if ruta.name.lower() == "readme.md":
                continue
            fmt = next((f for f in FORMATOS if re.match(f[0], ruta.name)), None)
            if not fmt:
                avisos.append(f"{ruta.relative_to(RAIZ)}: formato desconocido, no se cargó")
                continue
            _, lector, prov, tipo, iva = fmt
            base = {"fecha": fecha_de(ruta.name), "proveedor": prov, "moneda": "USD", "iva": iva, "tipo_precio": tipo,
                    "archivo_origen": str(ruta.relative_to(RAIZ)), "fecha_carga": carpeta.name, "nota": f"cargada por Ventas el {carpeta.name}"}
            n0 = len(filas)
            filas += list(lector(ruta, base))
            print(f"{ruta.name}: {len(filas) - n0} precios")
    with open(SALIDA, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS)
        w.writeheader()
        w.writerows(filas)
    for a in avisos:
        print("AVISO:", a)
    print(f"{SALIDA.relative_to(RAIZ)}: {len(filas)} precios")


if __name__ == "__main__":
    main()
