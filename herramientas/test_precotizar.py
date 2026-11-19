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
# auditoría 30-10-2026: antes se esperaba "igual" con la de Ingeniería en Fluidos (USD 533), pero esa es trim 8 (13Cr, no
# AISI 316) y el plano pide internos AISI 316: la regla de material (el texto del plano, no el atributo) la descarta bien
igual("retención 2\" #600 A-216 / AISI 316: la WCB trim 13Cr no sirve", (auto["7"]["fuentes"][0]["coincide"], auto["7"]["fuentes"][0]["precio"]), ("sin_ref", 0))
igual("codo 45° 2\" sch80 BW: igual", auto["15"]["fuentes"][0]["coincide"], "igual")
# 30-10-2026: la junta de Duralitte no dice el material y el plano pide A-234 WPB → no es similar (compatibilidades revisadas)
igual("junta monolítica: SIN PRECIO (la de Duralitte no dice el material; regla del 30-10-2026)", auto["13"]["fuentes"][0]["precio"], 0)
igual("unión doble extensible sin precio", auto["21"]["fuentes"][0]["precio"], 0)
igual("caño 1900 mm se compra por metro", (auto["14"]["unidad"], auto["14"]["cantidad"]), ("m", 1.9))
igual("cupla BW es forjado (no se empareja con un codo)", "codo" in auto["23"]["fuentes"][0].get("diferencia", ""), False)
# tee 2" #2000 NPT: la única de la misma serie es el estimado del cepo; una #3000 ya no es referencia (Matías, 29-10-2026)
igual("similar solo de la misma serie (tee 2\" #2000)", (auto["8"]["fuentes"][0]["codigo"], auto["8"]["fuentes"][0]["coincide"]), ("AFO-00917", "igual"))
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

# pintura de una virola cargada en kg: es una pieza (π·D·L), no "kg piezas" (Camuzzi 003, 30-10-2026: daba 38.852 m²)
sup = dict(precotizar.superficie_pintura([{"descripcion": 'Chapa para virola Ø55" (DI 1.280 mm) × 3,2 m × 2 1/4" (6.287 kg + 10% recortes)', "diametro": '55"', "cantidad": "6916", "unidad": "kg", "extremos": "BW", "serie_sch": ""}], 0))
igual("virola en kg: π·D·L de una pieza", round(sup["envolvente"], 1), round(3.14159265 * 55 * 0.0254 * 3.2, 1))

# peso escrito en la descripción o la especificación (ficha_rubros.peso_equipo): coma decimal y punto de miles con el
# lector único (AESA COT26-0010-001, 18-11-2026: "0,60 kg" se leía 60 kg y el filtro daba 697 kg en lugar de ≈ 102)
import ficha_rubros  # noqa: E402
for txt, esperado in (("Tornillo (0,60 kg c/u)", 0.6), ("Brida ciega 3,69 kg", 3.69), ("Cabezal (417 kg)", 417.0),
                      ("Virola 1.250 kg", 1250.0), ("Disco de refuerzo (24,4 kg c/u)", 24.4), ("Tapa 1.250,5 kg", 1250.5),
                      ("Disco (24,4 kg c/u) · rango 0-160 kg/cm2g", 24.4)):
    it = {"pos": "1", "grupo": "material", "descripcion": "Pieza", "especificacion": txt, "cantidad": 2, "unidad": "un"}
    igual(f"peso en el texto: {txt}", ficha_rubros.peso_equipo({"items": [it]})["kg"], round(2 * esperado, 1), 1e-9)

# Otros lectores de kg y mm del texto con el lector único (auditoría del 19-11-2026, después del arreglo de peso_equipo):
# con el código viejo, "152,4 mm" daba 0,004 m, "1.250 kg c/u" 1,25 kg, "1.250,5 kg c/u" 250,5 kg, "1.5 kg" 15 kg,
# "kg/cm2" se tomaba como peso, "USD 26.4" daba 264 y los tags PIT/TIT/FIT/FQIT no se reconocían como instrumentos.
import controles_tablas as ct  # noqa: E402
import lista_compras  # noqa: E402
import verificar_computo  # noqa: E402
import catalogo_materiales  # noqa: E402
igual('largo_m "Niple 1/2\" x 152,4 mm"', precotizar.largo_m('Niple 1/2" x 152,4 mm'), 0.1524, 1e-9)
igual('largo_m "L 3.200 mm"', precotizar.largo_m("Virola L 3.200 mm"), 3.2, 1e-9)
igual('largo_virola "DI 1.280,5 mm × L 3.200 mm"', precotizar.largo_virola("Virola DI 1.280,5 mm × L 3.200 mm"), 3.2, 1e-9)
igual('kg_de "1.250 kg c/u"', precotizar.kg_de({"descripcion": "Chapa 1.250 kg c/u", "diametro": ""})[0], 1250.0, 1e-9)
igual('kg_de "1.250,5 kg c/u"', precotizar.kg_de({"descripcion": "Chapa 1.250,5 kg c/u", "diametro": ""})[0], 1250.5, 1e-9)
igual('kg_de "590 kg c/u"', precotizar.kg_de({"descripcion": "Tapa 590 kg c/u", "diametro": ""})[0], 590.0, 1e-9)
igual('verificar_computo.largo_plano_m "152,4 mm"', verificar_computo.largo_plano_m('Niple 1/2" x 152,4 mm'), 0.1524, 1e-9)
igual("verificar_computo.error_largo con largo decimal", verificar_computo.error_largo({"pos": "7", "cantidad": "2"}, 0.1524, 0.3048, 0.3),
      "Pos 7: el plano pide 2 × 152,4 mm = 0,305 m y el cómputo tiene 0,300 m")
igual('verificar_computo.num de computo.csv "33.258" (formato interno)', verificar_computo.num("33.258"), 33.258, 1e-9)
canos = ct.leer(ct.TEC / "canos_peso_superficie.csv")
f12 = next(r for r in canos if r["dn_pulg"] == "0.5" and r["schedule"] == "80")
kg_n, _, _ = ct.peso_item({"descripcion": 'Niple 1/2" x 152,4 mm', "especificacion": "", "unidad": "un"},
                          {"diametro": "0.5", "schedule": "80", "material": "A106"}, "NIP", canos, [], [], [])
igual("controles_tablas.peso_item niple 152,4 mm", kg_n, float(f12["kg_m_carbono"]) * 0.1524, 1e-9)
for desc, esperado in (("Skid 1.5 kg", 1.5), ("Skid 1.250 kg", 1250.0), ("Skid 2,75 kg", 2.75)):
    kg_l, _ = lista_compras.kg_por_unidad({"descripcion": desc + " a 10 kg/cm2", "diametro": "", "serie_sch": "", "material": "", "extremos": ""},
                                         {"unidad": "un", "cantidad": 1, "especificacion": ""})
    igual(f"lista_compras.kg_por_unidad {desc}", kg_l, esperado, 1e-9)
kg_l, _ = lista_compras.kg_por_unidad({"descripcion": "Regulador 10 kg/cm2", "diametro": "", "serie_sch": "", "material": "", "extremos": ""},
                                     {"unidad": "un", "cantidad": 1, "especificacion": ""})
igual("lista_compras.kg_por_unidad: kg/cm2 no es peso", kg_l, None)
for txt, esperado in (("USD 26.4", 26.4), ("USD 26.04", 26.04), ("USD 1.250,50", 1250.5)):
    sep = catalogo_materiales.separar_renglon(f'Válvula esférica 2" {txt}; Brida ciega 2" USD 40')
    igual(f"catalogo_materiales.separar_renglon {txt}", sep and sep[0][1], esperado, 1e-9)
for tag in ("PIT-101", "TIT-201", "FIT-301", "FQIT-401", "PI-1", "TW-2", "LIT-5", "PDIT-6"):
    it = {"pos": "9", "grupo": "material", "descripcion": f"{tag} 1/2\" NPT", "especificacion": "(2,5 kg)", "cantidad": 1, "unidad": "un"}
    igual(f"instrumento {tag}: no se pesa", ficha_rubros.peso_equipo({"items": [it]})["kg"], 0.0, 1e-9)
it = {"pos": "2", "grupo": "material", "descripcion": 'Caño 3" Sch 80 sin costura (tramos del medidor FE-1800A)', "especificacion": "(10 kg)",
      "cantidad": 1, "unidad": "un"}
igual("caño que nombra el FE del medidor: se pesa", ficha_rubros.peso_equipo({"items": [it]})["kg"], 10.0, 1e-9)

if fallas:
    print(f"FALLAN {len(fallas)}:")
    for f in fallas:
        print("  -", f)
    sys.exit(1)
print("Precotización: todos los casos de control OK")
