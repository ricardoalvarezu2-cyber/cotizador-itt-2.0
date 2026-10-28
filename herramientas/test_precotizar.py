"""Test de la precotización automática con la CAPEX como caso de control (cotizacion armada a mano y revisada).

  python herramientas/test_precotizar.py

Si cambia el catálogo, algún precio puede cambiar; lo que no debe cambiar es la lógica: soldaduras de los extremos,
tipo de pieza reconocido, igual/similar y piezas sin precio.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import precotizar  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
CAPEX = RAIZ / "cotizaciones" / "COT26-1003-001_CAPEX_OQ8209"
fallas = []


def igual(nombre, obtenido, esperado, tol=None):
    ok = abs(obtenido - esperado) <= tol if tol is not None else obtenido == esperado
    if not ok:
        fallas.append(f"{nombre}: dio {obtenido!r}, se esperaba {esperado!r}")


precotizar.main(CAPEX)
auto = {i["pos"]: i for i in json.load(open(CAPEX / "cotizacion_auto.json", encoding="utf-8"))["items"]}
s = auto["MO"]
igual("soldadura: pulgadas equivalentes (4 a tope 2\" sch80 + reducción 2½\" + 2 cuplas)", s["cantidad"], 13.37, 0.02)
igual("soldadura: tarifa de las planillas 2026 (16 USD/pulg)", s["fuentes"][0]["precio"], 16.0)
igual("retención 2\" #600 WCB NPT: igual (Ingeniería en Fluidos 533)", (auto["7"]["fuentes"][0]["coincide"], auto["7"]["fuentes"][0]["precio"]), ("igual", 533.0))
igual("codo 45° 2\" sch80 BW: igual", auto["15"]["fuentes"][0]["coincide"], "igual")
igual("junta monolítica: Duralitte 280 (renglón separado de una cotización con varios productos, 28-10-2026)", auto["13"]["fuentes"][0]["precio"], 280.0)
igual("unión doble extensible sin precio", auto["21"]["fuentes"][0]["precio"], 0)
igual("caño 1900 mm se compra por metro", (auto["14"]["unidad"], auto["14"]["cantidad"]), ("m", 1.9))
igual("cupla BW es forjado (no se empareja con un codo)", "codo" in auto["23"]["fuentes"][0].get("diferencia", ""), False)
igual("precio real antes que estimado del cepo (tee 2\")", auto["8"]["fuentes"][0]["tipo"] != "est", True)
if fallas:
    print(f"FALLAN {len(fallas)}:")
    for f in fallas:
        print("  -", f)
    sys.exit(1)
print("Precotización: todos los casos de control OK")
