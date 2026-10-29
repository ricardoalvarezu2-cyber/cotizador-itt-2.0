"""Arma cotizacion.json del skid de regulación (CP 24578 ítem 2) desde cotizacion_auto.json (precotizar.py) + correcciones
revisadas a mano, cada una con su fuente. Correr: python cotizaciones/COT26-0135-001_CAMUZZI_CP24578_SKIDREG/armar_json.py"""
import json
from pathlib import Path

C = Path(__file__).resolve().parent
auto = json.load(open(C / "cotizacion_auto.json", encoding="utf-8"))
base = json.load(open(C / "cotizacion.json", encoding="utf-8"))
items = {i["pos"]: i for i in auto["items"]}
TORMENE = "fuentes_originales/ofertas_texto/ALONZO RED/2 - ERP B° Pilara/5.Proveedores 3ros/OFERTA TA7785A-ITT-REG TA956-NATURGY.pdf.txt"


def fuente(tipo, precio, prov, origen, fecha, coincide="similar", dif=""):
    f = {"tipo": tipo, "precio": precio, "proveedor": prov, "origen": origen, "fecha": fecha, "coincide": coincide}
    if dif:
        f["diferencia"] = dif
    return f


def poner(pos, fuentes, **extra):
    items[pos]["fuentes"] = fuentes
    items[pos].update(extra)


def SIN(motivo):
    """Sin referencia ni pieza parecida: no se adivina (P4 ter, decisión de Matías 28-10-2026)."""
    return [{"tipo": "est", "precio": 0, "proveedor": "SIN PRECIO: pedir cotización", "origen": "—", "fecha": "2026-10-28", "coincide": "sin_ref", "diferencia": motivo}]


poner("1", [fuente("cot", 9545.0, "Tormene Americana · oferta TA7785A pos. 1 (TA956-FC+SSV monitor)", TORMENE, "2026-06-16", "similar",
                   "DN3\" #300 (pedido #150), con bloqueo OPSO e indicador de posición; condiciones P1 25/7 bar, P2 1,5 bar, Q 8.000 Sm3/h (acá 15-10 / 4 bar, 6.000 Sm3/h). Pedir cotización para #150 y estas condiciones")])
poner("2", [fuente("cot", 6073.0, "Tormene Americana · oferta TA7785A pos. 2 (TA956-DFO activo silenciado)", TORMENE, "2026-06-16", "similar",
                   "DN3\" #300 (pedido #150); silenciador interno. Pedir cotización para #150 y estas condiciones"),
            fuente("ant", 4060.0, "Planilla Sacde/15 (VAL-03275: válvula reguladora 3\" RF set 0,03 kg/cm2)", "fuentes_originales/ofertas_texto/Sacde/15- PTG-SCH - SE-PTG-032 - TK Y BOMBA DE GLICOL", "2026-02-20", "similar", "otra aplicación (baja presión)")])
# Esféricas: marca del listado de Camuzzi (Matías, 29-10-2026); el precio Taval de la misma especificación queda como referencia
for i in items.values():
    i.pop("taval", None)  # Taval no está en el listado SCE-IN-501-0015: nada lleva el factor de válvulas Taval
for p in ("3", "4"):
    f = items[p]["fuentes"][0]
    f["coincide"], f["diferencia"] = "similar", "precio de referencia Taval (misma especificación): comprar marca del listado SCE-IN-501-0015 (Esferomatic, Worcester, Valvtronic, Pentair, Indave, Wenlen, Beta, Valmec)"
# Pos 9 y 14: se cotiza lo que dice el plano (te ASTM A-105, cupla ASTM A-106); el precio es de la pieza similar y Compras pide la del plano
poner("10", [fuente("lista", 283.84, "Renard (cód. 3533) · ABW-00423", "fuentes_originales/renar_lista_2025-12.xlsx", "2025-12-26", "igual")])
poner("15", [fuente("ant", 170.0, "Manifold ABAC de 3 vías M1-C-T AISI 304/316 (OTR-02980, planilla TAVAL/40)", "fuentes_originales/ofertas_texto/TAVAL/40- INARTECO FILTROS LIC 9333/4.Armado de la Oferta Comercial/LM costo Filtros rev.1.xlsx.txt", "2026-01-15", "similar", "manifold de 3 vías; pedir cotización de la toma multiport a ABAC")])
poner("16", SIN("válvula de alivio roscada 1/2\" tipo S-71: no hay precio ni pieza parecida (solo PSV de 1 1/2\" x 2\")"))
poner("18", SIN("termovaina 3/4\" NPT AISI 316: la base solo tiene termovainas bridadas 1 1/2\"-2\" (otra pieza)"))
poner("20", [fuente("cot", round(330 * 17.4 / 13.4 * 1.10, 2), "Grupo Provemet cot. 236623: UPN 120 a USD 17,40/m (13,40 kg/m) = 1,30 USD/kg +10% recortes, × 330 kg estimados (medidos del plano: 3.700 × 1.630 mm, perimetral, 4 travesaños, soportes y cáncamos)",
                   "fuentes_originales/listas_vendedor/2026-10-28/provemet_cotizacion_236623_perfiles_2025-07-01.pdf", "2025-07-01", "similar", "kilos estimados del plano; confirmar con el típico SCE-RE-110-0006")],
     especificacion="Skid 3.700 × 1.630 mm, UPN 120 perimetral y travesaños, soportes de cañería, 4 cáncamos y oreja de PAT (330 kg estimados)")
poner("19", [fuente("ant", 230.0, "Bloqueo y purga ABAC 80 (VAL-03162, planilla TAVAL/55) + manómetro Ø100 glicerina 150 (INS-02671, Weisz o similar, TAVAL/43)", "fuentes_originales/ofertas_texto/TAVAL/43- YPF- CM PUENTES DE PRODUCCION", "2026-04-22", "similar",
                    "manómetro según SCE-PR-506-1000 (AISI 316, certificado de calibración): confirmar (revisión independiente: faltaba el manómetro)")])
poner("A", [fuente("ant", 856.63, "ABB · Transmisor de presión (INS-02708, planilla TAVAL/72)", "fuentes_originales/ofertas_texto/TAVAL/72- Lic 64675 - SKID CONCENTRADOR - UTE NARAMBUE", "2026-08-14", "similar", "rango a definir 0-25 bar; sin válvula de bloqueo y purga (va en pos 19)")])
poner("B", [fuente("ant", 1448.33, "ABB · Transmisor de temperatura (INS-02714, planilla TAVAL/72)", "fuentes_originales/ofertas_texto/TAVAL/72- Lic 64675 - SKID CONCENTRADOR - UTE NARAMBUE", "2026-08-14", "similar", "con sensor; rango 0-100 °C a confirmar")])
poner("C", SIN("switch de posición de la monitora: confirmar si viene con la reguladora (Tormene ofrece indicador de posición)"))
# compra extra de caño: media tira (6 m), no 12 m: con 1-2 m usados una tira de 12 m deja más del 80% de sobrante; consultar recortes a Compras
for p, usado in (("21", 1.8), ("22", 2.0), ("23", 2.25), ("24", 1.0)):
    b = items[p + "b"]
    b["cantidad"] = round(6 - usado, 3)
    b["descripcion"] = f"Completar media tira de 6 m de la pos {p} (compra mínima; sobrante a stock)"
    b["especificacion"] = f"1 tramo de 6 m para {usado:g} m (con tira de 12 m el sobrante superaba 80%)"
# juntas y espárragos (nota del plano: según diámetro de brida y SCE-IN-301-0001/2); solo juntas internas, no las de conexión a planta
ext = [
    ("5b", "Junta espiralada 3\" #150 AISI 316/grafito con anillo ext. zincado (juntas de las válvulas, nota del plano)", 12, "un",
     fuente("ant", 6.0, "Planilla Techint/12 (JUN-01698)", "fuentes_originales/ofertas_texto/TECHINT/12. Proyecto LOS TOLDOS - Skid de Sand Jetting Desarenado", "2025-12-23", "igual")),
    ("5c", "Espárrago 5/8\" × 3 1/2\" A193 B7 con 2 tuercas 2H zincado (4 por junta de 3\")", 48, "un",
     fuente("ant", 2.6, "Planilla Sacde/15 (JUN-04177: 5/8 x 90 B7M bicromatizado)", "fuentes_originales/ofertas_texto/Sacde/15- PTG-SCH - SE-PTG-032 - TK Y BOMBA DE GLICOL", "2026-02-20", "similar", "B7M bicromatizado; confirmar si trae tuercas")),
    ("6b", "Junta espiralada 6\" #150 AISI 316/grafito con anillo ext. zincado", 4, "un",
     fuente("cot", 5.82, "MS Juntas cot. 48.729 (8\" #300)", "fuentes_originales/ofertas_texto/TAVAL/72- Lic 64675 - SKID CONCENTRADOR - UTE NARAMBUE/5.Proveedores 3ros/COTIZACION_N§_048729.pdf.txt", "2026-07-06", "similar", "8\" #300 (pedido 6\" #150)")),
    ("6c", "Espárrago 3/4\" × 4\" A193 B7 con 2 tuercas 2H zincado (8 por junta de 6\")", 32, "un",
     fuente("ant", 10.0, "Planilla Techint/12 (JUN-02733: 3/4\" L 120 mm con 2 tuercas zincado)", "fuentes_originales/ofertas_texto/TECHINT/12. Proyecto LOS TOLDOS - Skid de Sand Jetting Desarenado", "2025-12-23", "similar", "L 120 mm")),
    ("7b", "Junta espiralada 8\" #150 AISI 316/grafito (brida ciega)", 1, "un",
     fuente("cot", 5.82, "MS Juntas cot. 48.729 (8\" #300)", "fuentes_originales/ofertas_texto/TAVAL/72- Lic 64675 - SKID CONCENTRADOR - UTE NARAMBUE/5.Proveedores 3ros/COTIZACION_N§_048729.pdf.txt", "2026-07-06", "similar", "#300 (pedido #150)")),
    ("7c", "Espárrago 3/4\" × 4 1/4\" A193 B7 con 2 tuercas 2H zincado (8 por la brida ciega 8\")", 8, "un",
     fuente("ant", 10.0, "Planilla Techint/12 (JUN-02733)", "fuentes_originales/ofertas_texto/TECHINT/12. Proyecto LOS TOLDOS - Skid de Sand Jetting Desarenado", "2025-12-23", "similar", "L 120 mm")),
]
lista = []
for it in auto["items"]:
    lista.append(it)
    for pos, desc, q, u, f in ext:
        if pos[:-1] == it["pos"] and it["pos"] in ("5", "6", "7") and not any(x["pos"] == pos for x in lista):
            for pos2, desc2, q2, u2, f2 in [e for e in ext if e[0][:-1] == it["pos"]]:
                lista.append({"id": "M" + pos2.upper(), "pos": pos2, "grupo": "material", "descripcion": desc2, "especificacion": "Nota del plano: juntas y espárragos según diámetro de brida (SCE-IN-301-0001/2)",
                              "cantidad": q2, "unidad": u2, "fuentes": [f2]})
            break
lista.append({"id": "S05", "pos": "EST", "grupo": "mo", "descripcion": "Fabricación del skid y soportes (330 kg estimados)", "especificacion": "kg × tarifa por kg de estructura de skid",
              "cantidad": 330, "unidad": "kg", "fuentes": [fuente("ant", 3.0, "Fabricación de estructura de skid por kg (tercero Ledesma): tarifas.csv", "YPF/28 Lic 69343 planilla PC0 (850 kg × 3 = 2.550)", "2026-10-10", "similar", "kilos estimados")]})
lista.append({"id": "S06", "pos": "PF", "grupo": "servicio", "descripcion": "Prueba de fugas con nitrógeno a 5,5 bar con el equipo terminado (especificación §5.4.3)", "especificacion": "N2 + horas de planta",
              "cantidad": 1, "unidad": "gl", "fuentes": SIN("prueba de fugas con N2 a 5,5 bar: no hay tarifa ni antecedente")})
for it in lista:  # pintura: sumar el skid (≈ 25 m de UPN 120 ≈ 10,7 m²), que precotizar no cuenta cuando el skid va por unidad
    if it["pos"] == "PIN":
        it["cantidad"] = round(it["cantidad"] + 10.7, 3)
        it["especificacion"] += " + skid ≈ 10,7 m² (25 m de UPN 120)"
base["items"] = [items.get(i["pos"], i) if i["grupo"] == "material" and i["pos"] in items else i for i in lista]
PED = "cotizaciones/COT26-0135-001_CAMUZZI_CP24578_SKIDREG/pedido/"
base["parametros"].update({"TRANS": 1, "TC": 1541.43, "TR_ARS": 700000, "TR_EMB": 150, "TR_F": 1.0})
base["plazo"] = {"dias": 120, "texto": "desde OC · entregado en Transporte Cruz del Sur (Tapiales)",
                 "tareas": [["Ingeniería: planos, procedimientos y calificaciones para aprobación de Camuzzi", 0, 20, ""],
                            ["Reguladoras y monitoras Tormene (45/60 días de OC y anticipo)", 0, 60, "crit"],
                            ["Esféricas, bridas, accesorios y caño", 0, 30, ""],
                            ["Prefabricado, soldadura, RX 100% y PH (sin válvulas)", 30, 60, "tal"],
                            ["Montaje de reguladoras, conexionado de pilotos, pintura y prueba de fugas", 60, 80, "tal"],
                            ["Inspección Camuzzi, data book y despacho", 80, 95, "tal"]],
                 "nota": "Fija el plazo la entrega de las reguladoras (Tormene: 45/60 días). La inspección de Camuzzi tiene que avisarse con 5 días hábiles."}
base["flete"] = {"etiqueta": "Flete a Transporte Cruz del Sur (Tapiales)",
                 "referencia_html": "<b>Estimado:</b> un camión con hidrogrúa Quilmes → Mercado Central nave D3 (≈ 30 km), ARS 700.000 + USD 150 de embalaje. No hay cotización de flete local en la base: pedir a Compras.",
                 "criterio_html": "La planilla del concurso dice \"Flete a cargo del proveedor hasta Transporte Cruz del Sur, Mercado Central nave D3\": el flete va incluido en el precio."}
base["pedido"] = {"eyebrow": "Concurso de precios N° 24578 · Cláusulas particulares del 01-10-2026 · especificación del 19-10-2026",
                  "datos_html": [["Cliente", "Camuzzi Gas Pampeana S.A. / Camuzzi Gas del Sur S.A. (código ITT 0135)"],
                                 ["Ítem", "2 · Skid de regulación / medición · <b>1 un</b>"],
                                 ["Documentos", "Plano SCE-RE-315-0048 rev 0 · Especificación SCE-RE-515-0032 (ERP Parque Industrial Tres Arroyos)"],
                                 ["Condiciones de proceso", "Pe 15-10 bar · Pr 4 bar · Qmáx 6.000 Sm3/h · Qmín 1.000 Sm3/h"],
                                 ["Entrega pedida", "Transporte Cruz del Sur, Mercado Central nave D3, Tapiales (flete a cargo del proveedor)"],
                                 ["Condiciones", "Pago 30 días f.p.f. por transferencia, dólar BNA divisa vendedor del día de factura · validez 30 días · multas automáticas por demora"]],
                  "requisitos_html": ["RX 100% de las soldaduras a tope (filetes y media V con tintas penetrantes)", "PH de los prefabricados sin válvulas: 1,5 × presión máxima de la serie, 6 h (NAG-124); secado y prueba de fugas con aire o N2 a 5,5 bar",
                                      "Protección anticorrosiva SCE-PC-511-0003", "Esféricas según SCE-IN-501-0008 y ensayo SCE-RE-308-0001, con certificados firmados", "Marcas del listado SCE-IN-501-0015",
                                      "Documentación para aprobación (planos, mapa de soldaduras, procedimientos, calificaciones) y data book", "Inspección de Camuzzi en etapas (aviso 5 días hábiles)", "DDJJ de ética firmada con la oferta"]}
base["nota_mo_html"] = ("Soldadura propia por pulgada (16 USD/pulg-eq): juntas contadas de la columna de extremos (bridas WN, tees, reducciones y casquetes; los caños no tienen largo en el plano y se midieron del dibujo). "
                        "Montaje, ingeniería y calidad estimados del antecedente de skid más parecido. Incluye RX 100% (DB NDT 08-2026), PH, pintura, conexionado de pilotos y fabricación del skid (330 kg estimados). "
                        "Las juntas y espárragos van según la nota del plano (solo uniones internas; las de conexión a la planta no).")
base["desvios"] = [                   {"tag": "Pos 1-2", "titulo": "Reguladoras de referencia en #300", "texto": "El precio es de Tormene TA956 #300 (ERP Pilará, 06-2026). Pedir cotización #150 a marcas del listado SCE-IN-501-0015."}]
base["antecedentes"] = [
    {"carpeta_html": "<b>CAMUZZI/23</b> · Concurso 17584, ítem 5 (OC 4500150421)", "fecha": "06-03-2025", "que": "Skid de regulación / medición SCE-RE-315-0047 (ERP Ascensión), ganado", "precio": "venta 24.454", "tomado_html": "Alcance y control del orden de magnitud (no hay planilla de costo)"},
    {"carpeta_html": "<b>ALONZO RED/2</b> · ERP B° Pilará (Naturgy)", "fecha": "16-06-2026", "que": "Reguladoras Tormene TA956 3\" monitor + activo", "precio": "9.545 / 6.073", "tomado_html": "Precio de las pos 1 y 2"},
    {"carpeta_html": "<b>TAVAL/69</b> · YPF UTE LACH", "fecha": "19-07-2026", "que": "2 skids de regulación y medición SCC 113 A/B, MO Ledesma 200295", "precio": "17.200 (2 skids)", "tomado_html": "Control de la MO de fabricación (alternativa de tercero ≈ 8.600 por skid)"}]
base["pendientes"] = [
    {"titulo": "Proveedores", "items": ["Reguladoras y monitoras 3\" #150 para Pe 15-10 / Pr 4 bar, 6.000 Sm3/h, con switch de posición (Tormene, Fiorentini u otra del listado SCE-IN-501-0015)",
                                        "Toma multiport ABAC, alivio S-71, termovainas, transmisores (marca del listado)", "Flete local a Tapiales"]},
    {"titulo": "Camuzzi", "items": ["Confirmar si los sensores A, B y C los provee Camuzzi (\"sensores a instalar\")", "Largo de los caños (el plano no da cantidades)",
                                    "Típico SCE-RE-110-0006 (skid) y listado SCE-IN-501-0015 (se descargan de la web de Camuzzi)"]}]
base["planilla_notas"] = ["Plazo: 120 días desde OC (reguladoras 60 días + taller + inspección + margen por aprobaciones); se puede acortar si las reguladoras están en stock.",
                          "Condiciones del concurso: pago 30 días f.p.f., USD al BNA divisa vendedor del día de factura, validez 30 días, entregado en Transporte Cruz del Sur (Tapiales)."]
base["pie"] = "Fuentes: base de conocimiento del repositorio cotizador-itt. Precios en USD sin IVA. Borrador sin revisar."
base["historial_html"] = []
base["compras"] = {"fecha_respuesta": "2026-11-04", "material_en_planta_dias": 60, "lugar_entrega": "Planta ITT S.A., Av. 12 de Octubre 4004, Quilmes Oeste, Bs. As.",
                   "requisitos_generales": ["Cotizar en USD sin IVA, con plazo de entrega y validez de la oferta.", "Certificados de material 3.1; válvulas esféricas con certificados de fabricación y prueba según SCE-IN-501-0008 / SCE-RE-308-0001.",
                                            "Marcas del listado SCE-IN-501-0015 de Camuzzi.", "Indicar cualquier diferencia con lo pedido."],
                   "notas": {"1": "Monitora pilotada NC, obturador guiado, 3\" #150 RF, Pe 15-10 bar, Pr 4 bar, Q 6.000 Sm3/h, con switch de posición", "2": "Reguladora pilotada a diafragma NA, 3\" #150 RF, mismas condiciones"},
                   "proveedores": {"1": "Tormene Americana", "2": "Tormene Americana", "3": "Esferomatic / Worcester / Valvtronic (listado Camuzzi)", "4": "Esferomatic / Worcester / Valvtronic (listado Camuzzi)", "5": "Renard / Provemet", "15": "ABAC"},
                   "cantidad_compra": {"21": "media tira de 6 m", "22": "media tira de 6 m", "23": "media tira de 6 m", "24": "media tira de 6 m"},
                   "servicios": [{"servicio": "Radiografía 100% y tintas penetrantes", "proveedores": "DB NDT / Antonelli", "referencia": "DB NDT 08-2026", "nota": ""},
                                 {"servicio": "Flete a Tapiales con hidrogrúa", "proveedores": "a definir", "referencia": "sin referencia", "nota": ""}]}
json.dump(base, open(C / "cotizacion.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
import camuzzi_comun  # noqa: E402
camuzzi_comun.oferta(C, "COT26-0135-001", "Skid de regulacion", 2, "skid de regulación / medición según plano SCE-RE-315-0048 y especificación SCE-RE-515-0032", "1", 120,
                     ["Concurso de precios N° 24578: planilla de cotización, cláusulas particulares (01-10-2026) y condiciones generales", "Plano mecánico SCE-RE-315-0048 rev 0", "Especificación técnica SCE-RE-515-0032 (19-10-2026)"],
                     "Salto de regulación de presión sobre skid: 2 ramas 3\" #150 con monitora y reguladora pilotadas, colector de entrada 6\" y de salida 8\". Pe 15-10 bar, Pr 4 bar, Q 1.000-6.000 Sm3/h. RX 100%, PH según NAG-124, prueba de fugas a 5,5 bar, protección anticorrosiva SCE-PC-511-0003.",
                     [
                      "Largos de caño: el plano no los indica; se tomaron del dibujo.", "Sensores A, B y C: incluidos (marca del listado SCE-IN-501-0015); si los provee Camuzzi, se descuentan.",
                      "Reguladoras y monitoras: marca y modelo a confirmar dentro del listado de Camuzzi."],
                     ["Ingeniería de fabricación y documentación para aprobación (planos, mapa de soldaduras, procedimientos y calificaciones).", "Suministro de todos los materiales del plano, juntas y espárragos internos.",
                      "Prefabricado, armado y soldadura en taller; montaje de reguladoras y conexionado de pilotos en tubing inoxidable.", "Radiografía 100% y tintas penetrantes; prueba hidráulica de los prefabricados y prueba de fugas.",
                      "Protección anticorrosiva según SCE-PC-511-0003.", "Data book y certificados.", "Embalaje y flete hasta Transporte Cruz del Sur (Tapiales)."])
print(len(base["items"]), "ítems")
