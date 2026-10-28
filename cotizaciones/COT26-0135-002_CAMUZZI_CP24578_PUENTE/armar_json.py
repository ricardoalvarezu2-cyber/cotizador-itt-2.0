"""Arma cotizacion.json del puente de medición (CP 24578 ítem 3) desde cotizacion_auto.json (precotizar.py) + correcciones
revisadas a mano, cada una con su fuente. Correr: python cotizaciones/COT26-0135-002_CAMUZZI_CP24578_PUENTE/armar_json.py"""
import json
import sys
from pathlib import Path

C = Path(__file__).resolve().parent
sys.path.insert(0, str(C.parent / "COT26-0135-001_CAMUZZI_CP24578_SKIDREG"))
import camuzzi_comun  # noqa: E402

auto = json.load(open(C / "cotizacion_auto.json", encoding="utf-8"))
base = json.load(open(C / "cotizacion.json", encoding="utf-8"))
items = {i["pos"]: i for i in auto["items"]}
BIT = "cotizaciones/COT26-0135-002_CAMUZZI_CP24578_PUENTE/bitacora.md"


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


poner("1", [fuente("est", 9000.0, "Estimado: filtro FM-6 #150 simple módulo fabricado por ITT (venta del FM-6 #300 en CAMUZZI/23 13.543 ÷ 1,35 = 10.032 de costo; el #150 lleva menos espesor y bridas más livianas)",
                   "fuentes_originales/ofertas_texto/CAMUZZI/23.Filtro FM y skid salto de regulacion de presion/4.Armado de la Oferta Comercial/Concurso 17584 Vuelta 2.xlsx.txt", "2025-03-06", "similar",
                   "costo armado del filtro completo (materiales, tapa, elemento, MO, RX, PH); control: FM3 S150 de TAVAL/40 costó 5.575 y el FM8 S600 14.375 (01-2026)"),
            fuente("ant", 5574.88, "Planilla TAVAL/40: costo del filtro FM3 S150 (materiales 1.639 + MO 3.855 + repuestos y seguro)", "fuentes_originales/ofertas_texto/TAVAL/40- INARTECO FILTROS LIC 9333/4.Armado de la Oferta Comercial/LM costo Filtros rev.1.xlsx.txt", "2026-01-15", "similar", "FM3 (menor)")])
poner("2", [fuente("est", 90.0, "Estimado: 2 bridas WN 4\" #150 (Renard 35,65 c/u) + 0,3 m de caño 4\" sch 40 (Renard 26,95/m)", "fuentes_originales/renar_lista_2025-12.xlsx", "2025-12-26", "similar", "largo definitivo según la turbina que provee Camuzzi")])
poner("3", [fuente("lista", 740.0, "Taval (Lista 30 × 0.52) · VAL-04474 (BF61501R0104VP)", "fuentes_originales/taval_lista30_2025-09.xlsx", "2025-09-01", "similar", "antifuego API 6D según SCE-IN-501-0008 a confirmar con Taval")], taval=True)
items["4"]["taval"] = True
poner("7", items["7"]["fuentes"], descripcion="Te normal 6\" STD A-234 WPB BW (el plano dice A-105: desvío a declarar)")
poner("8", items["8"]["fuentes"], descripcion="Te normal 4\" STD A-234 WPB BW (el plano dice A-105: desvío a declarar)")
poner("11", SIN("termovaina 3/4\" NPT AISI 316: la base solo tiene termovainas bridadas 1 1/2\"-2\" (otra pieza)"))
poner("13", [fuente("cot", round(200 * 17.4 / 13.4 * 1.10, 2), "Grupo Provemet cot. 236623: UPN 120 a USD 17,40/m (1,30 USD/kg +10% recortes) × 200 kg estimados (3.530 × 800 mm, soportes y orejas)",
                    "fuentes_originales/listas_vendedor/2026-10-28/provemet_cotizacion_236623_perfiles_2025-07-01.pdf", "2025-07-01", "similar", "kilos estimados del plano")],
     especificacion="Skid 3.530 × 800 mm, soportes de cañería (4) y oreja de PAT (200 kg estimados)")
poner("A", [fuente("ant", 1448.33, "ABB · Transmisor de temperatura (INS-02714, planilla TAVAL/72)", "fuentes_originales/ofertas_texto/TAVAL/72- Lic 64675 - SKID CONCENTRADOR - UTE NARAMBUE", "2026-08-14", "similar", "con sensor; para correctora de caudal")])
b = items["15b"]
b["cantidad"], b["descripcion"], b["especificacion"] = 5, "Completar media tira de 6 m de la pos 15 (sobrante a stock)", "1 tramo de 6 m para 1 m (con 12 m el sobrante era 92%)"
for k, h, crit in (("HH", 20, "único equipo con documentación para aprobación de Camuzzi (planos, mapa de soldaduras, procedimientos); se comparte con el ítem 2"),
                   ("CAL", 40, "inspecciones de Camuzzi por etapa, data book y certificados")):
    for i in auto["items"]:
        if i["pos"] == k:
            i["cantidad"] = h
            i["especificacion"] = f"{h} h · criterio: {crit} (el antecedente de puentes en serie daba {i['fuentes'][0]['diferencia'][:60]}…)"
ext = [("5b", "Junta espiralada 4\" #150 AISI 316/grafito con anillo ext. zincado (válvulas y carretel)", 6,
        fuente("ant", 15.0, "Planilla Techint/12 (JUN-02778)", "fuentes_originales/ofertas_texto/TECHINT/12. Proyecto LOS TOLDOS - Skid de Sand Jetting Desarenado", "2025-12-23", "igual")),
       ("5c", "Espárrago 5/8\" × 3 1/2\" A193 B7 con 2 tuercas 2H zincado (8 por junta de 4\")", 48,
        fuente("ant", 2.6, "Planilla Sacde/15 (JUN-04177: 5/8 x 90 B7M bicromatizado)", "fuentes_originales/ofertas_texto/Sacde/15- PTG-SCH - SE-PTG-032 - TK Y BOMBA DE GLICOL", "2026-02-20", "similar", "B7M bicromatizado; confirmar tuercas")),
       ("6b", "Junta espiralada 6\" #150 AISI 316/grafito (entrada del filtro, filtro–válvula 3 y salida de la válvula 3)", 3,
        fuente("cot", 5.82, "MS Juntas cot. 48.729 (8\" #300)", "fuentes_originales/ofertas_texto/TAVAL/72- Lic 64675 - SKID CONCENTRADOR - UTE NARAMBUE/5.Proveedores 3ros/COTIZACION_N§_048729.pdf.txt", "2026-07-06", "similar", "8\" #300 (pedido 6\" #150)")),
       ("6c", "Espárrago 3/4\" × 4\" A193 B7 con 2 tuercas 2H zincado (8 por junta de 6\")", 24,
        fuente("ant", 10.0, "Planilla Techint/12 (JUN-02733: 3/4\" L 120 mm con 2 tuercas)", "fuentes_originales/ofertas_texto/TECHINT/12. Proyecto LOS TOLDOS - Skid de Sand Jetting Desarenado", "2025-12-23", "similar", "L 120 mm"))]
lista = []
for it in auto["items"]:
    lista.append(it)
    for pos, desc, q, f in ext:
        if pos[:-1] == it["pos"]:
            lista.append({"id": "M" + pos.upper(), "pos": pos, "grupo": "material", "descripcion": desc, "especificacion": "Nota del plano: juntas y espárragos según diámetro de brida (SCE-IN-301-0001/2)",
                          "cantidad": q, "unidad": "un", "fuentes": [f]})
lista.append({"id": "S05", "pos": "EST", "grupo": "mo", "descripcion": "Fabricación del skid y soportes (200 kg estimados)", "especificacion": "kg × tarifa por kg de estructura de skid", "cantidad": 200, "unidad": "kg",
              "fuentes": [fuente("ant", 3.0, "Fabricación de estructura de skid por kg (tercero Ledesma): tarifas.csv", "YPF/28 Lic 69343 planilla PC0 (850 kg × 3 = 2.550)", "2026-10-10", "similar", "kilos estimados")]})
lista.append({"id": "S06", "pos": "PF", "grupo": "servicio", "descripcion": "Prueba de fugas con nitrógeno a 5,5 bar con el equipo terminado (especificación §5.4.3)", "especificacion": "N2 + horas de planta",
              "cantidad": 1, "unidad": "gl", "fuentes": SIN("prueba de fugas con N2 a 5,5 bar: no hay tarifa ni antecedente")})
base["items"] = [items.get(i["pos"], i) if i["grupo"] == "material" else i for i in lista]
base["parametros"].update({"TRANS": 1, "TC": 1541.43, "TR_ARS": 700000, "TR_EMB": 150, "TR_F": 1.0})
base["plazo"] = {"dias": 105, "texto": "desde OC · entregado en Transporte Cruz del Sur (Tapiales)",
                 "tareas": [["Ingeniería y documentación para aprobación de Camuzzi", 0, 20, ""], ["Filtro FM-6: tapa, elemento y materiales", 0, 45, "crit"],
                            ["Esféricas Taval, bridas, accesorios y caño", 0, 30, ""], ["Fabricación del filtro y prefabricado del puente, RX 100% y PH", 45, 70, "tal"],
                            ["Montaje, pintura y prueba de fugas", 70, 80, "tal"], ["Inspección Camuzzi, data book y despacho", 80, 90, "tal"]],
                 "nota": "Fija el plazo el filtro FM-6 (tapa de cierre rápido y elemento). La turbina la provee Camuzzi: se entrega con carretel provisorio."}
base["flete"] = {"etiqueta": "Flete a Transporte Cruz del Sur (Tapiales)",
                 "referencia_html": "<b>Estimado:</b> un camión con hidrogrúa Quilmes → Mercado Central nave D3 (≈ 30 km), ARS 700.000 + USD 150 de embalaje. Si se despacha junto con el ítem 2, un solo flete.",
                 "criterio_html": "La planilla del concurso pone el flete a cargo del proveedor hasta Transporte Cruz del Sur."}
base["pedido"] = {"eyebrow": "Concurso de precios N° 24578 · Cláusulas particulares del 01-10-2026 · especificación del 19-10-2026",
                  "datos_html": [["Cliente", "Camuzzi Gas Pampeana S.A. / Camuzzi Gas del Sur S.A. (código ITT 0135)"], ["Ítem", "3 · Skid puente de medición · <b>1 un</b>"],
                                 ["Documentos", "Plano SCE-ME-315-039 · Especificación SCE-ME-515-0030 (ERP Parque Industrial Tres Arroyos)"],
                                 ["Condiciones de proceso", "Pe 15-10 bar · Qmáx 6.000 Sm3/h"], ["Entrega pedida", "Transporte Cruz del Sur, Mercado Central nave D3, Tapiales (flete a cargo del proveedor)"],
                                 ["Condiciones", "Pago 30 días f.p.f., dólar BNA divisa del día de factura · validez 30 días"]],
                  "requisitos_html": ["Turbina de medición provista por Camuzzi: ITT provee un carretel con sus dimensiones", "Filtro FM según SCE-RE-112-0004 y SCE-RE-512-0004", "RX 100%, PH (NAG-124), prueba de fugas a 5,5 bar",
                                      "Protección anticorrosiva SCE-PC-511-0003", "Esféricas según SCE-IN-501-0008 / SCE-RE-308-0001", "Documentación para aprobación y data book; inspección de Camuzzi"]}
base["nota_mo_html"] = ("Soldadura propia por pulgada (16 USD/pulg-eq) contada de la columna de extremos; caños medidos del dibujo. El filtro FM-6 va como un ítem completo (fabricado por ITT, con su MO). "
                        "Ingeniería 20 h y calidad 40 h por criterio (el antecedente de puentes en serie no sirve para un equipo único con aprobación de Camuzzi). Incluye RX 100%, PH, pintura y skid (200 kg estimados).")
base["desvios"] = [{"tag": "Pos 7-8", "titulo": "Tes en A-234 WPB", "texto": "El plano dice A-105 para tes STD a tope: se cotiza A-234 WPB."},
                   {"tag": "Pos 2", "titulo": "Carretel provisorio", "texto": "Largo según la turbina que provee Camuzzi (300 mm en el plano): confirmar marca y modelo."}]
base["antecedentes"] = [
    {"carpeta_html": "<b>CAMUZZI/23</b> · Concurso 17584", "fecha": "06-03-2025", "que": "Filtro FM-6 #300 simple módulo (venta)", "precio": "13.543", "tomado_html": "Costo estimado del filtro FM-6"},
    {"carpeta_html": "<b>TAVAL/40</b> · Inarteco Lic 9333", "fecha": "15-01-2026", "que": "Filtros FM3 S150 / FM8 S600 con planilla de costo", "precio": "costo 5.575 / 14.375", "tomado_html": "Control del costo del filtro"}]
base["pendientes"] = [{"titulo": "Proveedores", "items": ["Tapa y elemento del filtro FM-6 #150 (cotizar el filtro completo)", "Termovainas y transmisor de temperatura (marca del listado)", "Flete local a Tapiales"]},
                      {"titulo": "Camuzzi", "items": ["Marca y modelo de la turbina (largo del carretel)", "Si el sensor A lo provee Camuzzi", "Largos de caño (el plano no da cantidades)"]}]
base["planilla_notas"] = ["Plazo: 105 días desde OC (filtro FM-6 45 días + taller + inspección + margen por aprobaciones).",
                          "Condiciones del concurso: pago 30 días f.p.f., USD al BNA divisa vendedor del día de factura, validez 30 días, entregado en Transporte Cruz del Sur (Tapiales)."]
base["pie"] = "Fuentes: base de conocimiento del repositorio cotizador-itt. Precios en USD sin IVA. Borrador sin revisar."
base["compras"] = {"fecha_respuesta": "2026-11-04", "material_en_planta_dias": 45, "lugar_entrega": "Planta ITT S.A., Av. 12 de Octubre 4004, Quilmes Oeste, Bs. As.",
                   "requisitos_generales": ["Cotizar en USD sin IVA, con plazo de entrega y validez de la oferta.", "Certificados 3.1; esféricas con certificados según SCE-IN-501-0008 / SCE-RE-308-0001.", "Marcas del listado SCE-IN-501-0015."],
                   "notas": {"1": "Tapa de cierre rápido y elemento filtrante para FM-6 #150 (plano tipo SCE-RE-112-0004)"},
                   "proveedores": {"3": "Taval", "4": "Taval", "5": "Renard / Provemet"}, "cantidad_compra": {"15": "media tira de 6 m"},
                   "servicios": [{"servicio": "Radiografía 100% y tintas penetrantes", "proveedores": "DB NDT / Antonelli", "referencia": "DB NDT 08-2026", "nota": ""}]}
json.dump(base, open(C / "cotizacion.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
camuzzi_comun.oferta(C, "COT26-0135-002", "Puente de medicion", 3, "skid puente de medición según plano SCE-ME-315-039 y especificación SCE-ME-515-0030", "1", 105,
                     ["Concurso de precios N° 24578: planilla de cotización, cláusulas particulares y condiciones generales", "Plano mecánico SCE-ME-315-039", "Especificación técnica SCE-ME-515-0030 (19-10-2026)"],
                     "Puente de medición volumétrico con bypass sobre skid: filtro FM-6 #150 simple módulo, línea de medición 4\" con carretel provisorio de turbina, bypass 4\", válvulas esféricas paso total. RX 100%, PH según NAG-124, prueba de fugas, protección anticorrosiva SCE-PC-511-0003.",
                     ["Turbina de medición: la provee Camuzzi; se entrega un carretel provisorio con sus dimensiones.", "Tes (pos 7 y 8): se ofrecen A-234 WPB a tope (el plano dice A-105).",
                      "Largos de caño tomados del dibujo (el plano no los indica).", "Sensor A incluido; si lo provee Camuzzi, se descuenta."],
                     ["Ingeniería de fabricación y documentación para aprobación.", "Fabricación del filtro FM-6 según el plano tipo de Camuzzi.", "Suministro de materiales del plano, juntas y espárragos internos.",
                      "Prefabricado, armado y soldadura en taller; RX 100% y tintas; PH y prueba de fugas.", "Protección anticorrosiva SCE-PC-511-0003.", "Data book y certificados.", "Embalaje y flete hasta Transporte Cruz del Sur (Tapiales)."])
print(len(base["items"]), "ítems")
