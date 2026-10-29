"""Cotizaciones que alimentan la base (catálogo de materiales e índice de antecedentes): la biblioteca.

Solo entran las que el usuario incorporó con el botón "Pasar al repositorio y a la biblioteca" de la página (decisión de
Matías, 29-10-2026): `web/incorporar_base.py` deja cada una en biblioteca_cotizaciones/<id>/cotizacion.json. Si se
vuelve a incorporar la misma cotización, la última versión reemplaza a la anterior (misma carpeta). Las cotizaciones del
repositorio (cotizaciones/COT*) y el respaldo semanal de la página (cotizaciones_web/) no entran solas.
"""
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
BIBLIOTECA = RAIZ / "biblioteca_cotizaciones"


def cotizaciones():
    """Lista de (ruta de cotizacion.json, dict), una por código (si hubiera dos carpetas con el mismo código, la más nueva)."""
    por_codigo = {}
    for f in sorted(BIBLIOTECA.glob("*/cotizacion.json")):
        c = json.load(open(f, encoding="utf-8"))
        if not c.get("items"):
            continue
        meta = f.parent / "incorporacion.json"
        fecha = json.load(open(meta, encoding="utf-8")).get("incorporada", "") if meta.exists() else ""
        k = c.get("codigo") or f.parent.name
        if k not in por_codigo or fecha >= por_codigo[k][0]:
            por_codigo[k] = (fecha, f, c)
    return [(f, c) for _, f, c in sorted(por_codigo.values(), key=lambda x: str(x[1]))]
