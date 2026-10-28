"""Cotizaciones que alimentan la base (catálogo de materiales e índice de antecedentes).

- cotizaciones/COT*/cotizacion.json: las armadas en el repositorio con el cotizador.
- cotizaciones_web/<id>/cotizacion.json: las de la página que se pidieron incorporar (botón "Incorporar a la base", que
  deja `cot.base`) o que están aprobadas o enviadas. Las copia `web/respaldo_base.py` (pedido "incorporar_base" o tarea
  semanal). Si el mismo código está en el repositorio, vale la del repositorio.
"""
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def incorporable(c):
    return bool(c.get("base")) or c.get("estado") in ("aprobado", "enviado")


def cotizaciones():
    """Lista de (ruta de cotizacion.json, dict)."""
    out, codigos = [], set()
    for f in sorted((RAIZ / "cotizaciones").glob("COT*/cotizacion.json")):
        c = json.load(open(f, encoding="utf-8"))
        out.append((f, c))
        codigos.add(c.get("codigo"))
    for f in sorted((RAIZ / "cotizaciones_web").glob("*/cotizacion.json")):
        c = json.load(open(f, encoding="utf-8"))
        if incorporable(c) and c.get("codigo") not in codigos and c.get("items"):
            out.append((f, c))
            codigos.add(c.get("codigo"))
    return out
