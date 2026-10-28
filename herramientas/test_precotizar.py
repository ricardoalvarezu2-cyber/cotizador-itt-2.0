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
# lectores (segunda tanda de controles, 28-10-2026)
from catalogo_materiales import atributos, expandir, familia_de  # noqa: E402
from indice_proyectos import norm  # noqa: E402


def at(t):
    t = expandir(norm(t))
    return atributos(t, familia_de(t))


igual("sch_de lee XS, XXS y STD x XS", [precotizar.sch_de(v) for v in ("XS", "XXS", "STD x XS", "#300 x sch 80")], ["XS", "XXS", "STD", "80"])
igual("fecha AAAA-MM → último día real del mes", precotizar.fin_de_mes("2026-02"), "2026-02-28")
igual("retención rotulada como esférica en la planilla Sacde", at("TAVAL | VALVULA ESFERICA | Ø 12 - Ret | RF | 600#").get("tipo"), "retencion")
igual("válvula wafer con Ø en columna suelta", at("VALVULA WAFER | 3 | 150# | A216 | RETENCION WAFER").get("diametro"), '3"')
igual("codo 90 10 BW XS: Ø 10 y XS (no sch 80)", (at("CODO 90º 10 BW XS A234").get("diametro"), at("CODO 90º 10 BW XS A234").get("schedule")), ('10"', "XS"))
igual('espesor 5/8" = 15,88 mm', at('caño sin costura 12" esp. 5/8" API 5L X52').get("espesor_mm"), "15.88")
igual("espárrago con largo en mm", at("esparrago 7/8 x 145 mm B7").get("medida"), "7/8 x 5 3/4")
igual("espárrago 1.25x207: Ø 1 1/4", at("esparrago c/2 tuercas 1.25x207 B7").get("diametro"), '1.25"')
igual('tuerca 1 7/8"', at('tuerca 2H 1 7/8"').get("diametro"), '1.875"')
igual("anillo BX 153 es junta ring joint", (at("Anillo octogonal RTJ-10K BX 153").get("tipo"), at("Anillo octogonal RTJ-10K BX 153").get("medida")), ("ring joint", "BX153"))
igual("ESP SWI es junta espiralada", at('ESP SW AC 316LFG Ø12" 300').get("tipo"), "junta espiralada")
igual("WNRF se lee WN", at('brida WNRF 3" #300 sch 40 A105').get("tipo"), "wn")
igual("tapa de cierre rápido con Ø y serie", (at('Tapa de cierre rapido 16" #900').get("tipo"), at('Tapa de cierre rapido 16" #900').get("serie")), ("tapa de cierre rapido", "900"))
igual("scrapper = scraper", at("detector de paso de scrapper").get("tipo"), "detector de scraper")
fila = {"diametro": '12"', "serie_sch": "300", "descripcion": "retención"}
igual("válvula de otra serie: no es similar", bool(precotizar.rechazo((0, 0, 0, 0, 0, 0, ["serie: 600 (pedido 300)"], {}), fila, "VAL")), True)
igual("válvula sin Ø: no es similar", bool(precotizar.rechazo((0, 0, 0, 0, 0, 0, ['diametro: sin dato (pedido 12")'], {}), fila, "VAL")), True)
igual('brida 16" con una de 10": no (más de 1,25× desde 8")', bool(precotizar.rechazo((0, 0, 0, 0, 0, 0, ['diametro: 10" (pedido 16")'], {}), {**fila, "diametro": '16"'}, "BRI")), True)
igual('sockolet 12"x3/4": se escala por la salida', precotizar.ajuste_similar((0, 0, 0, 0, 0, 0, ['diametro: 0.75" (pedido 12")'], {}), {"diametro": '12"x3/4"', "descripcion": "Sockolet"}, "AFO")[0], 1.0)

if fallas:
    print(f"FALLAN {len(fallas)}:")
    for f in fallas:
        print("  -", f)
    sys.exit(1)
print("Precotización: todos los casos de control OK")
