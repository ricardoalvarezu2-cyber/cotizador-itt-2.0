"""Marcas aprobadas por el cliente para cada renglón (columna "Marcas aprobadas" de la lista para Compras).

Regla (Matías, 06-11-2026): cada renglón de la lista para Compras lleva las marcas que el listado del cliente acepta
para ese tipo de producto, con sus observaciones; si el listado no trae ese producto, se dice. Los listados están en
conocimiento/comercial/listados_marcas.csv (uno por cliente, con la revisión): cada fila es un subgrupo del listado con
un patrón (regex sobre la descripción normalizada, sin acentos y en minúsculas) y se toma la primera que coincide por
orden. Lo cargado a mano en compras.marcas[pos] de la cotización manda sobre esto.
La página hace lo mismo con la misma tabla (datos.json "listados_marcas", web/src/documentos.js).

Uso: python herramientas/marcas_cliente.py "<cliente>" "<descripción>"
"""
import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from indice_proyectos import norm  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
CSV = RAIZ / "conocimiento" / "comercial" / "listados_marcas.csv"
SIN = "El listado {listado} no trae marcas para este producto"


def tabla():
    return sorted(csv.DictReader(open(CSV, encoding="utf-8")), key=lambda r: (r["cliente"], int(r["orden"])))


def listado(cliente, filas=None):
    """Filas del listado del cliente (por patron_cliente sobre el nombre), o [] si no tiene listado cargado."""
    c = norm(cliente)
    return [r for r in (filas or tabla()) if re.search(r["patron_cliente"], c)]


def marcas(cliente, descripcion, filas=None):
    """Texto para la columna: 'marcas (observaciones)', o el aviso de que el listado no lo trae; '' si el cliente no tiene listado."""
    ls = listado(cliente, filas)
    if not ls:
        return ""
    d = norm(descripcion)
    for r in ls:
        if re.search(r["patron"], d):
            if not r["marcas"]:  # subgrupo que el listado no tiene (switch, conector): se dice
                break
            return r["marcas"] + (f" ({r['observaciones']})" if r["observaciones"] else "")
    return SIN.format(listado=ls[0]["listado"].split(" (")[0])


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    print(marcas(sys.argv[1], sys.argv[2]) or "(el cliente no tiene listado de marcas cargado)")
