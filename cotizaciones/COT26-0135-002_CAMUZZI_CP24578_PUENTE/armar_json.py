"""Arma cotizacion.json y oferta.json del puente de medición (CP 24578 ítem 3) desde cotizacion_auto.json (precotizar.py):
las filas del plano conservan la descripción, la especificación y la cantidad del cliente; las fuentes de precio, las filas
agregadas (b, c…), la MO, los servicios, el plazo y los textos se fijan acá, cada uno con su fuente. Correrlo de nuevo no
deshace nada: todo lo revisado está escrito en este archivo (revisión completa del 30-10-2026, ver bitacora.md).
Correr: python cotizaciones/COT26-0135-002_CAMUZZI_CP24578_PUENTE/armar_json.py"""
import json
import math
import sys
from pathlib import Path

C = Path(__file__).resolve().parent
sys.path.insert(0, str(C.parent / "COT26-0135-001_CAMUZZI_CP24578_SKIDREG"))
import camuzzi_comun  # noqa: E402

auto = json.load(open(C / "cotizacion_auto.json", encoding="utf-8"))
base = json.load(open(C / "cotizacion.json", encoding="utf-8"))
plano = {i["pos"]: i for i in auto["items"] if i["grupo"] == "material" and not i["pos"][-1].isalpha() or i["pos"] == "A"}

HOY = "2026-11-05"
RENARD = "fuentes_originales/renar_lista_2025-12.xlsx"
TAVAL40 = "fuentes_originales/ofertas_texto/TAVAL/40- INARTECO FILTROS LIC 9333/4.Armado de la Oferta Comercial/LM costo Filtros rev.1.xlsx.txt"
MEGATAP = "fuentes_originales/ofertas_texto/TAVAL/60 - Inarteco - ERPs tipo 2da etapa - Litoral Gas/5.Proveedores 3ros/Megatap PRESUPUESTO ITT SA 27143.pdf.txt"
QUESADA = "fuentes_originales/ofertas_texto/TAVAL/58 - Inarteco - ERPs tipo 1ra etapa - Litoral Gas/5.Proveedores 3ros/Cotizacion JQ-020-2026.pdf.txt"
LISTADO = "cotizaciones/COT26-0135-003_CAMUZZI_CP24578_SEPARADOR/pedido/CP24527_mail_2026-10-14/789-2- LISTADO DE MARCAS Y PROVEEDORES CAMUZZI.txt"
TC_OCT = 1541.43  # BNA oficial venta, promedio de oct-2026 (conocimiento/costos/dolar_mensual.csv)


def F(tipo, precio, prov, origen, fecha, coincide="similar", dif="", **extra):
    f = {"tipo": tipo, "precio": precio, "proveedor": prov, "origen": origen, "fecha": fecha, "coincide": coincide}
    if dif:
        f["diferencia"] = dif
    f.update(extra)
    return f


def SIN(motivo, fecha=HOY):
    """Sin referencia válida: no se adivina (P4 ter, Matías 28-10-2026). Va a la lista para Compras."""
    return F("est", 0, "SIN PRECIO: pedir cotización", "—", fecha, "sin_ref", motivo)


items = []


def P(pos, fuentes, ident=None, **extra):
    """Fila del plano: descripción, especificación, cantidad y unidad del cliente (cotizacion_auto.json ← transcripción)."""
    a = plano[pos]
    it = {"id": ident or a["id"], "pos": pos, "grupo": "material", "descripcion": a["descripcion"], "cantidad": a["cantidad"],
          "unidad": a["unidad"], "especificacion": a.get("especificacion", ""), "fuentes": fuentes}
    it.update(extra)
    items.append(it)


def X(ident, pos, grupo, desc, cant, unidad, esp, fuentes, **extra):
    """Fila agregada por ITT (b, c… del plano, MO o servicio)."""
    it = {"id": ident, "pos": pos, "grupo": grupo, "descripcion": desc, "cantidad": cant, "unidad": unidad, "especificacion": esp, "fuentes": fuentes}
    it.update(extra)
    items.append(it)


MARCA_ESF = "comprar marca del listado SCE-IN-501-0015 (Esferomatic, Worcester, Valvtronic, Pentair, Indave, Wenlen, Spirax Sarco hasta 4\" S150, Beta, Valmec)"

# ---------------------------------------------------------------- 1. Filtro FM-06: costeado por componentes (revisión 30-10-2026)
# Modelo: planilla de costo TAVAL/40 (filtros FM de Inarteco, 15-01-2026): cuerpo, tapa, internos, instrumentos + MO por pulgada
# (16 USD/pulg) + horas de montaje. El FM-6 #150 simple módulo de Camuzzi lleva cuerpo de 12" y toberas de 6" (oferta ITT OE 260-23,
# CAMUZZI/19) y tapa de cierre rápido (OE 260-23; CAMUZZI/23: "Con tapa de cierre rápido"). El plano tipo SCE-RE-112-0004 no está en
# el repositorio: los largos del cuerpo y de la pollera son estimados y se confirman con él.
P("1", [F("est", 0, "Costeado por componentes en las filas 1b a 1k y en la MO del filtro (MOF, ARMF)", "—", HOY, "sin_ref",
          "el precio del filtro es la suma de sus componentes: ver filas 1b–1k, MOF y ARMF")],
  sin_precio_motivo="Filtro fabricado por ITT: costeado por componentes en las filas 1b a 1k (materiales) y MOF / ARMF (mano de obra); RX, PH y pintura en sus rubros")
X("M01B", "1b", "material", "Cuerpo y pollera del filtro FM-06: caño 12\" sch 40 sin costura A53/A106/API 5L B", 1.5, "m",
  "Estimado ITT: cuerpo ≈ 1,1 m + pollera ≈ 0,4 m (confirmar con el plano tipo SCE-RE-112-0004)",
  [F("lista", 177.72, "Renard (cód. 1200) · Tubo s/costura 323,8 x 10,31 mm A53/A106/API 5L B", f"{RENARD} · código 1200", "2025-12-26", "igual",
     "largo de compra 10,50 a 11,80 m: pedir corte o tramo a Compras")])
X("M01C", "1c", "material", "Fondo del filtro FM-06: casquete semielíptico 12\" Std ASTM A234 WPB", 1, "un", "Plano tipo SCE-RE-112-0004",
  [F("lista", 69.76, "Renard (cód. 3438) · Casquete Semieliptico 12\" Std ASTM A234 WPB · ABW-00012", f"{RENARD} · código 3438", "2025-12-26", "igual",
     codigo="ABW-00012")])
X("M01D", "1d", "material", "Tapa de cierre rápido 12\" #150 soldada, para el filtro FM-06 (Futura / Gora / Peco / EKA, listado SCE-IN-501-0015)", 1, "un",
  "Tapa soldada, no roscada (listado SCE-IN-501-0015, tapas de cierre rápido para filtros)",
  [F("cot", 2480.0, "Megatap presupuesto 2026-143 (19-05-2026): tapa de cierre rápido horizontal MTV 12\" S/150 (serie 150), ASTM A105N, ASME VIII Div 1, con 2 o-rings de repuesto",
     MEGATAP, "2026-05-19", "similar",
     "marca Megatap (no está en el listado de Camuzzi: comprar Futura, Gora, Peco o EKA) y apertura horizontal (el FM es vertical); la asignación 6\" 1.085 / 8\" 1.630 / 12\" 2.480 sale del orden del texto (conocimiento/comercial/plazos_proveedores.csv): verificar en el PDF",
     validez_hasta="2026-06-03"),
   F("ant", 3424.0, "Futura cot. S00198 (planilla, OTR-03021): tapa de cierre rápido 8\" #300", "Z:\\VENTAS\\OFERTAS Y LICITACIONES (catálogo de materiales, OTR-03021)", "2025-12-10", "descartada",
     "no es referencia (otra medida y otra serie); muestra que Futura, del listado, puede cotizar más que Megatap")])
X("M01E", "1e", "material", "Elemento filtrante para filtro FM-06 (Gora / Metpor / Filtron / De Nichilo / Panden / SP, listado SCE-IN-501-0015)", 1, "un",
  "Según plano tipo SCE-RE-112-0004 y ET SCE-RE-512-0004",
  [F("ant", 75.0, "Planilla TAVAL/40: elemento filtrante G4 Metpor (hoja del filtro FM8, pos 10)", TAVAL40, "2026-01-15", "similar",
     "elemento del FM8 (cuerpo 16\", mayor que el del FM-6): pedir a Gora / Metpor el del FM-6")])
X("M01F", "1f", "material", "Toberas del filtro FM-06: brida WN 6\" #150 RF sch 40 ASTM A105 (Futura / Francovigh)", 2, "un", "Entrada y salida del filtro",
  [F("lista", 58.91, "Renard (cód. 11297) · BRI-01313", f"{RENARD} · código 11297", "2025-12-26", "igual", "marca: comprar Futura o Francovigh (listado)",
     codigo="BRI-01313")])
X("M01G", "1g", "material", "Toberas del filtro FM-06: caño 6\" sch 40 sin costura A53/A106/API 5L B (sale del sobrante de la media tira de la pos 15)", 0.3, "m",
  "2 toberas de ≈ 150 mm",
  [F("cot", 49.48, "Grupo Provemet cot. 288974 ítem 1 · CAN-01510", "fuentes_originales/listas_vendedor/2026-10-30/provemet_cotizacion_288974_canos_2026-10-29.pdf · ítem 1", "2026-10-29", "igual", "TUBO S/C ASTM A53/A106/API5L B 6'' SCH 40 Ø 168,3 X 7,11 mm; Provemet cot. 288974 (29-10-2026), precio neto con bonificación 4% (vale comprando toda la cotización), validez 15 días", codigo="CAN-01510"), F("lista", 60.51, "Renard (cód. 1173) · CAN-01510", f"{RENARD} · código 1173", "2025-12-26", "igual", codigo="CAN-01510")])
X("M01H", "1h", "material", "Instrumentos del filtro FM-06: manómetro diferencial con aguja de arrastre (Wika), manifold 3 vías (ABAC / Casucci / Fittinox), conectores doble virola y tubing inox",
  1, "gl", "Listado SCE-IN-501-0015: manómetros diferenciales Wika con aguja de arrastre; manifold para manómetro diferencial ABAC / Casucci / Fittinox",
  [F("ant", 950.0, "Planilla TAVAL/40, filtro FM3 S150 (pos 21 manómetro diferencial 500, 28 manifold 3 vías ABAC 170, 22/29/30 conectores 30+30+112, 31/32 tubing 42+66)",
     TAVAL40, "2026-01-15", "similar", "FM3 de Inarteco (manómetro Weisz): Camuzzi pide Wika con aguja de arrastre; pedir cotización")])
X("M01J", "1j", "material", "Manómetro de presión estática Ø 100, conexión 1/2\" NPT, AISI 316, para el filtro FM-06 (dibujado en el plano), montado con manifold de tres vías",
  1, "gl", "Características de la ET §5.7 (clase 1, glicerina, IP65, certificado de calibración) y §5.8; marcas Weisz / Wika / ABAC / Casucci / Capino",
  [F("ant", 115.0 + 170.0, "Manómetro Ø 100 1/2\" NPT AISI 316 (INS-02698, planilla Sacde/15 LM-TANQUE GLICOL, 115) + manifold de 3 vías AISI 304/316 ABAC M1-C-T (planilla TAVAL/40, filtro FM3 S150 pos 28, 170)",
     "fuentes_originales/ofertas_texto/Sacde/15- PTG-SCH - SE-PTG-032 - TK Y BOMBA DE GLICOL/4.Armado de la Oferta Comercial/LM-TANQUE GLICOL.xlsx.txt; " + TAVAL40, "2026-01-15", "similar",
     "marca no dicha en la planilla: comprar Weisz / Wika / ABAC / Casucci / Capino; confirmar clase 1, IP65 y certificado de calibración; manifold AISI 304/316 (superior al A-105 zincado)")])
X("M01I", "1i", "material", "Internos, refuerzos tipo poncho, purga (esférica 1/2\" + tapón), medias cuplas, asas y chapa de identificación del filtro FM-06", 1, "gl",
  "Plano tipo SCE-RE-112-0004",
  [F("ant", 127.5, "Planilla TAVAL/40, filtro FM3 S150: pos 6, 7, 11, 12, 13, 15, 16, 18, 19, 20, 24, 25 y 26 (los refuerzos tipo poncho van aparte en la fila 1k)",
     TAVAL40, "2026-01-15", "similar", "lista del FM3 (cuerpo 6\", tapa bridada): confirmar con el plano tipo SCE-RE-112-0004")])
X("M01K", "1k", "material", "Refuerzos tipo poncho 12\" x 6\" STD ASTM A-234 WPB para las toberas del filtro FM-06 (Cintolo / Curvo Sold)", 2, "un", "Plano tipo SCE-RE-112-0004 (no está en el repositorio)",
  [SIN("sin precio de refuerzo 12\" x 6\": la planilla TAVAL/40 pone 150 estimado para el de 6\" x 3\" (auditoría 30-10-2026): pedir a Cintolo")])

# ---------------------------------------------------------------- 2 a 16 y A
P("2", [F("est", round(2 * 23.42 + 0.3 * 34.34, 2), "Estimado: 2 bridas WN 4\" #150 (Provemet cot. 288979 ítem 5, 23,42 c/u, 29-10-2026) + 0,3 m de caño 4\" sch 40 sin costura A53/A106/API 5L B (Renard cód. 1160, 34,34/m)",
          RENARD, "2025-12-26", "similar", "largo entre caras 300 mm del plano; definitivo según la turbina que provee Camuzzi")],
  especificacion="Plano: 4\" · 150 · S/ Esp. CAMUZZI · Nota ITT: carretel bridado entre las bridas pos 5 (2 bridas WN 4\" + caño, 2 soldaduras en la MO); 300 mm entre caras en el plano")
P("3", [F("lista", 740.0, "Taval (Lista 30 × 0.52) · VAL-04474 (BF61501R0104VP)", "fuentes_originales/taval_lista30_2025-09.xlsx", "2025-09-01", "similar",
          "precio de referencia Taval PT flotante a palanca: el plano dibuja la válvula 3 con volante (caja reductora), que no está en el precio; " + MARCA_ESF + "; certificados según SCE-IN-501-0008 y SCE-RE-308-0001")])
P("4", [F("lista", 300.0, "Taval (Lista 30 × 0.52) · VAL-04465", "fuentes_originales/taval_lista30_2025-09.xlsx", "2025-09-01", "similar",
          "precio de referencia Taval (misma especificación): " + MARCA_ESF + "; certificados según SCE-IN-501-0008 y SCE-RE-308-0001")])
P("5", [F("cot", 23.42, "Grupo Provemet cot. 288979 ítem 5 · BRI-01295", "fuentes_originales/listas_vendedor/2026-10-30/provemet_cotizacion_288979_bridas_2026-10-29.pdf · ítem 5", "2026-10-29", "igual", "Brida Welding Neck Sch 40 Raised Face Serie 150 ASTM A 105 ANSI B16.5 4\"; cotizada para 4 un, validez 15 días; marca: comprar Futura o Francovigh (listado)", codigo="BRI-01295"), F("lista", 35.65, "Renard (cód. 11295) · BRI-01295", f"{RENARD} · código 11295", "2025-12-26", "igual", "marca: comprar Futura o Francovigh (listado)", codigo="BRI-01295")])
X("M5B", "5b", "material", "Junta espiralada 4\" #150 AISI 316/grafito con anillo ext. zincado (válvulas y carretel)", 6, "un",
  "Nota del plano: juntas y espárragos según diámetro de brida (SCE-IN-301-0001/2)",
  [F("ant", 15.0, "Planilla Techint/12 (JUN-02778)", "fuentes_originales/ofertas_texto/TECHINT/12. Proyecto LOS TOLDOS - Skid de Sand Jetting Desarenado", "2025-12-23", "igual")])
X("M5C", "5c", "material", "Espárrago 5/8\" × 3 1/2\" A193 B7 con 2 tuercas 2H zincado (8 por junta de 4\")", 48, "un",
  "ET §5.8: espárragos ASTM A193 B7 y tuercas A194 2H zincados; marcas Petrobul / Talleres Versailles / Fornis",
  [F("est", 10.0, "Bules o Versailles (planilla TAVAL/43, hoja 3\" x 442u ítem 9) · JUN-04173", "fuentes_originales/ofertas_texto/TAVAL/43- YPF- CM PUENTES DE PRODUCCION/4.Armado de la Oferta Comercial/TAVAL- LM - Puentes de Producción YPF.xlsx.txt · línea 147",
     "2026-02-19", "similar", "largo 110 mm (pedido 3 1/2\" ≈ 89 mm, más largo: sirve); la planilla pone USD 10 también al de 7/8\" x 230 mm: parece valor global, pedir cotización",
     codigo="JUN-04173")])
P("6", [F("lista", 58.91, "Renard (cód. 11297) · BRI-01313", f"{RENARD} · código 11297", "2025-12-26", "igual", "marca: comprar Futura o Francovigh (listado)", codigo="BRI-01313")])
X("M6B", "6b", "material", "Junta espiralada 6\" #150 AISI 316/grafito (entrada del filtro, filtro–válvula 3 y salida de la válvula 3)", 3, "un",
  "Nota del plano: juntas y espárragos según diámetro de brida (SCE-IN-301-0001/2)",
  [SIN("sin junta 6\" #150 cotizada (la de MS Juntas es 8\" #300; la 6\" #150 del catálogo es del cepo): pedir cotización a MS Juntas / Klinger")])
X("M6C", "6c", "material", "Espárrago 3/4\" × 4\" A193 B7 con 2 tuercas 2H zincado (8 por junta de 6\")", 24, "un",
  "ET §5.8: espárragos ASTM A193 B7 y tuercas A194 2H zincados; marcas Petrobul / Talleres Versailles / Fornis",
  [F("est", 10.0, "Planilla Techint/12 (JUN-02733: 3/4\" L 120 mm con 2 tuercas)", "fuentes_originales/ofertas_texto/TECHINT/12. Proyecto LOS TOLDOS - Skid de Sand Jetting Desarenado",
     "2025-12-23", "similar", "L 120 mm · estimado: la planilla Techint/12 tiene columnas ambiguas (tercera auditoría 30-10-2026)")])
P("7", [F("lista", 104.61, "Renard (cód. 3468) · ABW-00418", f"{RENARD} · código 3468", "2025-12-26", "similar",
          "material: A234 WPB (pedido A105): consulta al cliente C4; Compras pide la del plano", codigo="ABW-00418")])
P("8", [F("lista", 50.63, "Renard (cód. 3466) · ABW-00406", f"{RENARD} · código 3466", "2025-12-26", "similar",
          "material: A234 WPB (pedido A105): consulta al cliente C4; Compras pide la del plano", codigo="ABW-00406")])
P("9", [F("lista", 49.6, "Renard (cód. 3065) · ABW-00236", f"{RENARD} · código 3065", "2025-12-26", "similar", "material: A234 WPB (S/ Esp. CAMUZZI en el plano)", codigo="ABW-00236")])
P("10", [F("lista", 26.2, "Renard (cód. 3400) · ABW-00111", f"{RENARD} · código 3400", "2025-12-26", "igual", "radio largo (el plano no dice el radio)", codigo="ABW-00111")])
P("11", [SIN("termovaina 3/4\" NPT AISI 316: la base solo tiene termovainas bridadas 1 1/2\"-2\" o en conjunto con transmisor (otra pieza)")])
X("M11B", "11b", "material", "Cupla 3/4\" NPT S3000 ASTM A105 soldada sobre el caño 4\" para cada termovaina (no figura en la tabla del plano)", 2, "un",
  "Agregado por ITT: conexión de cada termovaina al caño (marcas CH / Thorsa / Forja Atlas)",
  [F("lista", 3.51, "Renard (cód. 5293) · Cupla 3/4\" NPT S3000 ASTM A105 · AFO-00721", f"{RENARD} · código 5293", "2025-12-26", "igual", codigo="AFO-00721")])
P("12", [F("ant", 65.2 + 2.71, "Esférica 1/2\" NPT S3000 A-105 (VAL-03526, 65,20, planilla Tecpetrol/9; precio de referencia Taval, comprar marca del listado) + cupla 1/2\" S3000 A-105 (AFO-00714, Renard 2,71) con tapón",
           "fuentes_originales/ofertas_texto/TECPETROL/9. CM SKID MANIFOLD PAD S-600/ESTRUCTURA DE COSTOS- LM de Manifold S600 CM - PC0-C", "2026-01-26", "similar",
           "material S/ Fabricante en el plano; marca del listado de Camuzzi")])
P("13", [F("cot", round(200 * 17.4 / 13.4 * 1.10, 2), "Grupo Provemet cot. 236623: UPN 120 a USD 17,40/m (1,30 USD/kg +10% recortes) × 200 kg estimados (3.530 × 800 mm, soportes, orejas de PAT y cáncamos de izaje)",
           "fuentes_originales/listas_vendedor/2026-10-28/provemet_cotizacion_236623_perfiles_2025-07-01.pdf", "2025-07-01", "similar", "kilos estimados del plano (típicos SCE-RE-110-0006 no disponibles)")],
  especificacion="Skid 3.530 × 800 mm, soportes de cañería (4), oreja de PAT y cáncamos de izaje (ET §5.1) · 200 kg estimados")
P("14", [F("lista", 34.34, "Renard (cód. 1160) · CAN-01495", f"{RENARD} · código 1160", "2025-12-26", "similar",
           "Tubo s/costura 114,3 x 6,02 mm A53/A106/API 5L B (sin costura, triple certificación: cumple A53 Gr B); largo 10,50 a 12,50 m", codigo="CAN-01495")])
X("M14B", "14b", "material", "Completar barra de 12 m de la pos 14 (compra mínima; sobrante, no va en el equipo)", 4.0, "m", "1 barra de 12 m para 8 m",
  [F("lista", 34.34, "Renard (cód. 1160) · CAN-01495", f"{RENARD} · código 1160", "2025-12-26", "similar", "misma pieza que la pos 14", codigo="CAN-01495")])
P("15", [F("cot", 49.48, "Grupo Provemet cot. 288974 ítem 1 · CAN-01510", "fuentes_originales/listas_vendedor/2026-10-30/provemet_cotizacion_288974_canos_2026-10-29.pdf · ítem 1", "2026-10-29", "similar", "TUBO S/C ASTM A53/A106/API5L B 6'' SCH 40 Ø 168,3 X 7,11 mm (cumple A53 Gr B); Provemet cot. 288974 (29-10-2026), precio neto con bonificación 4% (vale comprando toda la cotización), validez 15 días", codigo="CAN-01510"), F("lista", 60.51, "Renard (cód. 1173) · CAN-01510", f"{RENARD} · código 1173", "2025-12-26", "similar",
           "Tubo s/costura 168,3 x 7,11 mm A53/A106/API 5L B (cumple A53 Gr B)", codigo="CAN-01510")])
X("M15B", "15b", "material", "Completar media tira de 6 m de la pos 15 (sobrante a stock)", 4.7, "m",
  "1 tramo de 6 m: 1 m pos 15 + 0,3 m toberas del filtro (fila 1g) + 4,7 m de sobrante",
  [F("cot", 49.48, "Grupo Provemet cot. 288974 ítem 1 · CAN-01510", "fuentes_originales/listas_vendedor/2026-10-30/provemet_cotizacion_288974_canos_2026-10-29.pdf · ítem 1", "2026-10-29", "similar", "misma pieza que la pos 15", codigo="CAN-01510"), F("lista", 60.51, "Renard (cód. 1173) · CAN-01510", f"{RENARD} · código 1173", "2025-12-26", "similar", "misma pieza que la pos 15", codigo="CAN-01510")])
P("16", [SIN("la referencia era una válvula A105 y el plano pide A-106 (otra clase de material): sin referencia compatible (consulta al cliente C3)", "2026-10-30")])
P("A", [F("ant", 3470.06, "Rosemount · transmisor de temperatura (INS-02716, planilla PAMPA ENERGIA/5, proveedor Induquip)",
          "fuentes_originales/ofertas_texto/PAMPA ENERGIA/5 - Doc5757155642 - Construc 10 Puentes y 2 Colectores - RDA/4.Armado de la Oferta Comercial/Cot Skid Manifolds Colectores RDA Rev2.xlsx.txt · línea 177",
          "2026-06-26", "similar",
          "transmisor Rosemount (marca del listado); el plano pide 0-100 °C / 4-20 mA 3/4\" para correctora: si alcanza una sonda o la provee Camuzzi, baja (consulta C2). La referencia anterior (ABB) no está en el listado SCE-IN-501-0015",
          codigo="INS-02716")])

# ---------------------------------------------------------------- MO y servicios
# Soldaduras del puente, junta por junta del dibujo SCE-ME-315-039 (revisión 30-10-2026): 21 a tope + 5 cuplas
JUNTAS = ("A tope 6\" (6): brida 6 de entrada–caño 15, caño 15–te 7, te 7–caño (≈ 290 mm hacia la válvula 3), caño–brida 6 (válvula 3), te 7–reducción 9 (lado 6\"), reducción 9 (antes del filtro)–brida 6 · "
          "A tope 4\" (16): reducción 9 (sobre te 7)–brida 5 · bypass: brida 5–caño 911, caño–codo 10, codo–caño 3.961, caño–codo 10, codo–te 8, te 8–caño 1.213, caño–codo 10, te 8–brida 5 de salida · "
          "línea: codo 10–brida 5 (válvula 4), brida 5–caño 452, caño 452–brida 5, brida 5–caño 1.100, caño 1.100–reducción 9 · carretel 2: 2 (brida–caño) · "
          "Cuplas (×1,75): pos 12 (1 × 1/2\"), pos 16 (2 × 1/2\"), cuplas 11b (2 × 3/4\") · pulgadas: 6 × 6 + 16 × 4 + 3 × 0,5 × 1,75 + 2 × 0,75 × 1,75 = 105,25 (auditoría 30-10-2026: tramo de caño entre la te 7 y la brida de la válvula 3)")
X("S01", "MO", "mo", "Soldaduras del puente: 22 a tope + 5 cuplas (junta por junta)", 105.25, "pulg", JUNTAS,
  [F("ant", 16.0, "Mano de obra soldadura piping (criterio de las planillas de costo 2026): precio por pulgada de las planillas de ITT 2025-2026 (16 a 16,5)",
     "planillas 2026 (TAVAL/43 puentes YPF 19-02-2026; TAVAL/40 Inarteco; Sacde 12 a 15; Tecpetrol 9: 16,5)", "2026-02-28", "igual"),
   F("cot", 12.0, "J. C. Quesada presupuesto JQ-020-2026: precio por pulgada soldada (ERP tipo Litoral Gas; incluye consumibles y calificación de soldadores ASME IX; sin END, PH ni pintura)",
     QUESADA, "2026-05-06", "igual", validez_hasta="2026-06-05")])
X("MOF", "MOF", "mo", "Soldaduras del filtro FM-06 (cuerpo 12\", toberas 6\", cuplas y pollera)", 70.75, "pulg",
  "Cuerpo–casquete 12\" sch 40 (12 × 1,083 = 13) + cuerpo–tapa 13 + 2 toberas 6\" injertadas (2 × 6 × 1,5 = 18) + 2 bridas–toberas 6\" (12) + purga 1/2\" (0,875) + 2 cuplas 1/4\" del manómetro diferencial (0,875) + pollera–casquete (13, filete); mismo criterio que la hoja Mano de Obra de la planilla TAVAL/40",
  [F("ant", 16.0, "Mano de obra soldadura por pulgada (planilla TAVAL/40, hoja Mano de Obra de ITT: precio por pulgada 16 en los filtros FM)", TAVAL40, "2026-01-15", "igual")])
X("S05", "EST", "mo", "Fabricación del skid y soportes (200 kg estimados)", 200, "kg", "kg × tarifa por kg de estructura de skid",
  [F("cot", 4.5, "J. C. Quesada presupuesto JQ-020-2026: precio por kg de skid (ERP tipo Litoral Gas)", QUESADA, "2026-05-06", "similar", "kilos estimados del plano",
     validez_hasta="2026-06-05"),
   F("ant", 3.0, "Fabricación de estructura de skid por kg (Ledesma, YPF/28 PC0: precio con fecha supuesta)", "YPF/28 Lic 69343 planilla PC0", "2026-10-10", "similar", "descartada como base: fecha supuesta (error 3 de la PC0)")])
M2 = {"piping": 6.21, "filtro": 1.94, "skid": 6.65}
X("S02", "PIN", "servicio", "Granallado y pintura (m² calculados: piping, filtro y skid)", round(sum(M2.values()) * 1.2, 2), "m2",
  "Piping 6,21 m² (ficha_rubros: caños, bridas, accesorios y válvulas) + filtro 1,94 m² (caño 12\" 1,5 m × 1,018 m²/m + casquete, tapa y toberas) + skid 6,65 m² (≈ 14,9 m de UPN 120 × 0,446 m²/m); esquema según SCE-PC-511-0003 (no leído)",
  [F("ant", 37.98, "Pintor (sin nombre) · PIN-00579 (precio confirmado por Matías)", "conocimiento/precios/precios_usuario.csv", "2026-10-30", "similar", "Granallado y pintura de piping y skid, incluye materiales: USD 37,98/m² confirmado por Matías Russo el 30-10-2026 (precio firme, PIN-00579); la planilla de origen (YPF Lic 66944 colectores) lo aplica sobre los m² + 20 % de overspray, por eso la cantidad va × 1,2; esquema SCE-PC-511-0003 a confirmar (× 1,2 sobre 14,8 m²)", codigo="PIN-00579"),
   F("ant", 50.0, "criterio ITT: granallado y pintura de skids, incluye materiales · PIN-00494", "fuentes_originales/ofertas_texto/PAMPA ENERGIA/7- Licitacion contrato Marco Skid PAD Rincon de Aranda",
     "2026-08-14", "similar", "esquema SCE-PC-511-0003 sin leer: confirmar espesores y productos (Sherwin Williams / Hempel)", codigo="PIN-00494")])
X("S03", "PH", "servicio", "Pruebas hidráulicas de resistencia y hermeticidad del puente (horas de planta)", 18, "h",
  "ET §5.4: prefabricados del puente sin válvulas ni equipos, 1,5 × presión máxima de la serie ANSI 150, durante 6 h, con las bridas de las válvulas cegadas; armado, llenado, desarme y secado: 1 día × 2 personas × 9 h = 18 h (planilla TAVAL/40, hoja Soldadura + HH, «PH con armado y desarme»). La PH del filtro FM-06 va en ARMF (18 h, como en la planilla TAVAL/40)",
  [F("ant", 13.0, "MO ITT · END-00215", "Z:\\VENTAS\\OFERTAS Y LICITACIONES\\TAVAL\\49 - A&A Fluid Control - Manifolds Tecpetrol - Salar El Tolillar\\4.Armado de la Oferta Comercial",
     "2026-03-10", "igual", codigo="END-00215")])
PLACAS = 6 * 4 + 16 * 3 + 2 * 6 + 2 * 4  # puente 6" (4 placas) y 4" (3); filtro 12" (6) y bridas–toberas 6" (4): factores_soldadura.csv
VISITAS = math.ceil(PLACAS / 45)
ARS_RX = VISITAS * 850000 + PLACAS * 15000
X("S04", "RX", "servicio", "Radiografía 100% de las soldaduras a tope (puente y filtro)", 1, "gl",
  f"ET §5.3.1 · {PLACAS} placas (puente: 6 juntas 6\" × 4 + 16 juntas 4\" × 3; filtro: 2 juntas 12\" × 6 + 2 bridas–toberas 6\" × 4) → {VISITAS} visitas de hasta 45 placas; placas originales y digitalizadas para el data book",
  [F("cot", round(ARS_RX / TC_OCT, 2), f"Proveedor de RX (sin nombre), precio confirmado por Matías el 30-10-2026: {VISITAS} visitas × ARS 850.000 + {PLACAS} placas × ARS 15.000 = ARS {ARS_RX:,}".replace(",", ".").replace("(sin nombre). precio", "(sin nombre), precio")
     + " sin IVA, a BNA oct-2026 (1.541,43)", "conocimiento/precios/precios_usuario.csv", HOY, "igual"),
   F("ant", 1571.5, "Servicio de radiografía DB NDT (2026-08; PAMPA ENERGIA/5 y /7, hoja ENOD)", "PAMPA ENERGIA/5 y /7, hoja ENOD (Lista DB NDT)", "2026-08-31", "similar", "71 placas del cómputo anterior")])
X("S04L", "LP", "servicio", "Líquidos penetrantes en uniones que no se radiografían (cuplas, toberas injertadas, filetes)", 10, "junta",
  "ET §5.3.1 · puente: 5 cuplas (pos 12, 16 y 11b); filtro: 2 toberas, 3 cuplas (purga y manómetro diferencial)",
  [F("ant", 30.0, "Líquidos penetrantes por soldadura 1\", 3/4\", 1/2\" (END terceros) · END-00209",
     "fuentes_originales/ofertas_texto/Sacde/18- PREFABRICADO PIPING - Plantas Compresoras TGS/7.Propuesta Comercial (envío al Cliente)/Sacde - Cotización piping x pulgada+END y mtr2 Rev4 Direccion.xlsx.txt",
     "2026-04-20", "similar", "tarifa por junta de otro proveedor; las toberas son mayores que 1\"", codigo="END-00209")])
X("S06", "PF", "servicio", "Prueba de fugas con aire seco a 5,5 bar con el equipo terminado y pintado (ET §5.4.3)", 8, "h",
  "Estimado ITT: 2 personas × 4 h con solución jabonosa y espejo; aire seco del compresor de planta (la ET admite aire seco o nitrógeno)",
  [F("est", 13.0, "Horas de planta para movimientos internos y PH (tarifa) · FAB-00351", "fuentes_originales/ofertas_texto/TECPETROL/13- TRAMPAS TSR TSL de 16- 12 - 8 pGSD Evento 12681",
     "2026-06-26", "similar", "horas estimadas por criterio (sin antecedente de prueba de fugas)", codigo="FAB-00351")])
HORAS = auto_h = {i["pos"]: i for i in auto["items"] if i["pos"] in ("HH", "CAL", "ARM")}
for ident, pos, h, crit in (("S12H", "HH", 29, "20 h del puente (único equipo con planos, mapa de soldaduras, listado de documentos, cronograma y procedimientos para aprobación de Camuzzi, ET §3.1) + 9 h del filtro (planilla TAVAL/40, FM3 S150)"),
                            ("S13C", "CAL", 49, "40 h del puente (inspecciones de Camuzzi por etapa, data book en pdf, CD y papel, ET §6–7) + 9 h del filtro (planilla TAVAL/40, FM3 S150)")):
    a = HORAS[pos]
    X(ident, pos, "mo", a["descripcion"].replace("(estimadas del antecedente)", "(estimadas por criterio)"), h, "h", f"{h} h · criterio: {crit}",
      [dict(a["fuentes"][0], diferencia=f"horas por criterio; el antecedente de puentes en serie (TAVAL/43) da {a['cantidad']} h por unidad")])
a = HORAS["ARM"]
X("S13A", "ARM", "mo", a["descripcion"], a["cantidad"], a["unidad"], a["especificacion"], a["fuentes"])
X("ARMF", "ARMF", "mo", "Horas de montaje del filtro FM-06 (corte y presentación, PH, pintura y armado final)", 45, "h",
  "Planilla TAVAL/40, hoja Soldadura + HH, filtro FM3 150: corte y presentación 18 h + PH con armado y desarme 18 h + armado final 9 h",
  [F("est", 13.0, "Horas propias ITT (tarifa de la planilla TAVAL/40)", TAVAL40, "2026-01-15", "similar", "horas del FM3 S150 (menor) aplicadas al FM-06")])

base["items"] = items
base["parametros"].update({"TRANS": 1, "TC": TC_OCT, "TR_ARS": 700000, "TR_EMB": 150, "TR_F": 1.0, "ph_horas": 18, "fecha_referencia": "2026-10-31"})  # último mes con índices (05-11-2026)
PLAZO = 150
base["plazo"] = {"dias": PLAZO, "texto": "desde OC · entregado en Transporte Cruz del Sur (Tapiales)",
                 "tareas": [["Ingeniería, documentación y aprobación de Camuzzi (datos de diseño de la tapa)", 0, 20, ""],
                            ["Tapa de cierre rápido 12\" #150 de marca del listado (referencia Futura FV16: 90 días desde OC)", 15, 105, "crit"],
                            ["Esféricas de marca del listado, elemento filtrante, instrumentos, bridas, accesorios y caño", 0, 45, ""],
                            ["Soldadura de la tapa, RX, PH y secado del filtro", 105, 115, "tal"],
                            ["Montaje final, pintura y prueba de fugas", 115, 122, "tal"],
                            ["Inspección de Camuzzi, data book y despacho", 122, 130, "tal"]],
                 "nota": "Fija el plazo la tapa de cierre rápido del filtro (Futura cotizó 90 días la FV16 #600 en TAVAL/40; Megatap 60 días, fuera del listado). El prefabricado del puente se hace mientras llega la tapa. La turbina la provee Camuzzi: se entrega con carretel."}
base["flete"] = {"etiqueta": "Flete a Transporte Cruz del Sur (Tapiales)",
                 "referencia_html": "<b>Estimado, sin cotización:</b> un camión con hidrogrúa Quilmes → Mercado Central nave D3 (≈ 30 km), ARS 700.000 + USD 150 de embalaje. Si se adjudican los ítems 2 y 3, un solo flete. Pedir precio a Compras.",
                 "criterio_html": "La planilla del concurso pone el flete a cargo del proveedor hasta Transporte Cruz del Sur."}
base["pedido"] = {"eyebrow": "Concurso de precios N° 24578 · Cláusulas particulares del 01-10-2026 · especificación del 19-10-2026",
                  "datos_html": [["Cliente", "Camuzzi Gas Pampeana S.A. / Camuzzi Gas del Sur S.A. (código ITT 0135)"], ["Ítem", "3 · Skid puente de medición · <b>1 un</b>"],
                                 ["Documentos", "Plano SCE-ME-315-039 · Especificación SCE-ME-515-0030 (ERP Parque Industrial Tres Arroyos) · matriz de requisitos en pedido/requisitos.csv"],
                                 ["Condiciones de proceso", "Pe 15-10 bar · Pr 4 bar · Qmáx 6.000 Sm3/h · Qmín 1.000 Sm3/h"],
                                 ["Entrega pedida", "Transporte Cruz del Sur, Mercado Central nave D3, Tapiales (flete a cargo del proveedor)"],
                                 ["Condiciones", "Pago 30 días f.p.f., dólar BNA divisa vendedor del día de factura · validez 30 días · multas por mora CGP art. 16"]],
                  "requisitos_html": ["Turbina de medición provista por Camuzzi: ITT provee un carretel con sus dimensiones", "Filtro FM según SCE-RE-112-0004 y SCE-RE-512-0004 (costeado por componentes)",
                                      "RX 100% (LP donde no se puede radiografiar), PH 1,5 × serie ANSI durante 6 h (NAG-124), prueba de fugas a 5,5 bar",
                                      "Protección anticorrosiva SCE-PC-511-0003", "Esféricas según SCE-IN-501-0008 / SCE-RE-308-0001", "Marcas del listado SCE-IN-501-0015",
                                      "Documentación para aprobación, data book (pdf, CD y papel) e inspección de Camuzzi por etapas"]}
base["nota_mo_html"] = ("Soldadura por pulgada (16 USD/pulg-eq) contada junta por junta del dibujo: puente 105,25 pulg (22 a tope + 5 cuplas) y filtro FM-06 70,75 pulg. "
                        "El filtro se costea por componentes (planilla TAVAL/40 como modelo). RX con la tarifa confirmada por Matías (30-10-2026), LP, PH (puente y filtro), "
                        "pintura de piping, filtro y skid, prueba de fugas, skid por kg (Quesada) y horas de ingeniería, calidad y montaje.")
base["desvios"] = [{"tag": "Pos 3", "titulo": "Esférica 6\" con reductor", "texto": "El plano la dibuja con volante: el precio de referencia es a palanca; Compras la pide con caja reductora."},
                   {"tag": "Pos 2", "titulo": "Carretel provisorio", "texto": "Largo entre caras 300 mm del plano; se ajusta a la turbina que provee Camuzzi."},
                   {"tag": "Consultas", "titulo": "5 consultas al cliente abiertas", "texto": "Manómetros adicionales de la ET §5.7, sensor A, material A-106 de la pos 16, tes A-105 y cantidades dibujadas de las pos 11, 12 y 16 (consultas_cliente.md)."}]
base["antecedentes"] = [
    {"carpeta_html": "<b>TAVAL/40</b> · Inarteco Lic 9333", "fecha": "15-01-2026", "que": "Filtros FM3 S150 / FM8 S600 con planilla de costo", "precio": "costo FM3 5.575",
     "tomado_html": "Modelo de costeo del filtro FM-06 por componentes"},
    {"carpeta_html": "<b>CAMUZZI/19</b> · OE 260-23", "fecha": "03-07-2023", "que": "Filtro FM6 S150 simple módulo, cuerpo 12\", tapa de cierre rápido (venta)", "precio": "37.200 (cepo)",
     "tomado_html": "Configuración del FM-6 (cuerpo 12\", toberas 6\")"},
    {"carpeta_html": "<b>TAVAL/58</b> · Quesada JQ-020-2026", "fecha": "06-05-2026", "que": "MO de ERP tipo Litoral Gas: 12 USD/pulgada y 4,50 USD/kg de skid", "precio": "—",
     "tomado_html": "Fabricación del skid por kg"}]
base["pendientes"] = [{"titulo": "Compras", "items": ["Tapa de cierre rápido 12\" #150 de marca del listado (Futura / Gora / Peco / EKA)", "Elemento filtrante FM-6, manómetro diferencial Wika y manifold",
                                                      "Esféricas 6\" y 4\" #150 de marca del listado con certificados SCE-IN-501-0008", "Bridas, accesorios y caños (Renard 12-2025 vencida)",
                                                      "Termovainas, junta 6\" #150, espárragos B7/2H, cupla A-106", "UPN del skid; MO del skid (Quesada) y flete a Tapiales"]},
                      {"titulo": "Camuzzi (consultas_cliente.md)", "items": ["C1 manómetros adicionales de la ET §5.7", "C2 sensor A de temperatura", "C3 cupla A-106 de la pos 16", "C4 tes A-105 (pos 7 y 8)", "C5 cantidades de las pos 11, 12 y 16 en el dibujo"]},
                      {"titulo": "ITT", "items": ["Descargar de la web de Camuzzi SCE-RE-112-0004, SCE-RE-512-0004, SCE-PC-511-0003, SCE-RE-110-0006 y SCE-IN-301-0005",
                                                  "Confirmar si los WPS/PQR y soldadores calificados vigentes sirven (ET §3.1.3)"]}]
base["planilla_notas"] = [f"Plazo: {PLAZO} días desde OC (tapa de cierre rápido del filtro ≈ 105 días + taller 25 días = 130, más margen).",
                          "Condiciones del concurso: pago 30 días f.p.f., USD al BNA divisa vendedor del día de factura, validez 30 días, entregado en Transporte Cruz del Sur (Tapiales)."]
base["pie"] = "Fuentes: base de conocimiento del repositorio cotizador-itt. Precios en USD sin IVA. Borrador sin revisar."
base["compras"] = {"fecha_respuesta": "2026-11-04", "material_en_planta_dias": 45, "lugar_entrega": "Planta ITT S.A., Av. 12 de Octubre 4004, Quilmes Oeste, Bs. As.",
                   "requisitos_generales": ["Cotizar en USD sin IVA, con plazo de entrega y validez de la oferta.", "Certificados 3.1; esféricas con certificados según SCE-IN-501-0008 / SCE-RE-308-0001.",
                                            "Solo marcas del listado SCE-IN-501-0015 de Camuzzi (rev. 1, 10-02-2026)."],
                   "notas": {"1": "Filtro FM-06 #150 simple módulo fabricado por ITT: ver filas 1b a 1k",
                             "1d": "Tapa de cierre rápido 12\" #150 vertical soldada: Futura, Gora, Peco o EKA (referencia Megatap 2026-143: 2.480, fuera del listado)",
                             "1e": "Elemento filtrante para FM-06 según SCE-RE-112-0004: Gora / Metpor / Filtron / De Nichilo / Panden / SP",
                             "1h": "Manómetro diferencial Wika con aguja de arrastre; manifold ABAC / Casucci / Fittinox",
                             "11": "Termovaina 3/4\" NPT AISI 316 (Wika / ABAC / Casucci / Capino / Weisz)",
                             "16": "Cupla de acero ASTM A-106 1/2\" NPT soldable con esférica 1/2\" S3000 (consulta C3 al cliente)",
                             "3": "Esférica 6\" #150 PT con caja reductora y volante (como en el plano), marca del listado",
                             "1k": "Refuerzos tipo poncho 12\" x 6\" STD A-234 WPB (Cintolo)",
                             "A": "Sensor / transmisor de temperatura 0-100 °C 4-20 mA 3/4\" para correctora (Rosemount, Yokogawa, Siemens, Aplisens, Smar…; consulta C2)"},
                   "proveedores": {"1d": "Futura Hnos. / Gora / EKA Técnica", "1e": "Gora / Metpor", "3": "Esferomatic / Worcester / Valvtronic (listado Camuzzi)",
                                   "4": "Esferomatic / Worcester / Valvtronic (listado Camuzzi)", "5": "Futura / Francovigh", "6": "Futura / Francovigh", "5b": "Klinger / Teadit / Flexseal / Miyashiro / Garlock", "7": "Cintolo (Curvo Sold) / TDW", "8": "Cintolo (Curvo Sold) / TDW", "9": "Cintolo (Curvo Sold) / TDW", "10": "Cintolo (Curvo Sold) / TDW", "1c": "Cintolo (Curvo Sold) / TDW", "1k": "Cintolo (Curvo Sold) / TDW", "1j": "Weisz / Wika + ABAC / Casucci", "11b": "CH / Thorsa / Forja Atlas",
                                   "5c": "Petrobul / Talleres Versailles / Fornis", "6c": "Petrobul / Talleres Versailles / Fornis", "6b": "Klinger / Teadit / Flexseal / Miyashiro"},
                   "cantidad_compra": {"15": "media tira de 6 m (incluye 0,3 m para las toberas del filtro)", "1b": "tramo de 1,5 m de 12\" sch 40"},
                   "servicios": [{"servicio": "Reconfirmar MO del skid por kg (J. C. Quesada JQ-020-2026 vencida)", "proveedores": "Quesada / Ledesma", "referencia": "4,50 USD/kg (06-05-2026)", "nota": ""},
                                 {"servicio": "Flete Quilmes → Transporte Cruz del Sur, Tapiales (camión con hidrogrúa)", "proveedores": "a definir", "referencia": "estimado ARS 700.000", "nota": "un solo flete si se adjudican los ítems 2 y 3"}]}
base["justificaciones"] = {}  # ningún freno se levanta con texto: se levantan con las respuestas de Compras y de Camuzzi
json.dump(base, open(C / "cotizacion.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

camuzzi_comun.oferta(C, "COT26-0135-002", "Puente de medicion", 3, "skid puente de medición según plano SCE-ME-315-039 y especificación SCE-ME-515-0030", "1", PLAZO,
                     ["Concurso de precios N° 24578: planilla de cotización, cláusulas particulares y condiciones generales", "Plano mecánico SCE-ME-315-039", "Especificación técnica SCE-ME-515-0030 (19-10-2026)"],
                     "Puente de medición volumétrico con bypass sobre skid: filtro FM-06 #150 simple módulo con tapa de cierre rápido, línea de medición 4\" con carretel de turbina, bypass 4\", válvulas esféricas paso total. RX 100% y líquidos penetrantes, PH según NAG-124, prueba de fugas, protección anticorrosiva SCE-PC-511-0003.",
                     ["Turbina de medición: la provee Camuzzi; se entrega un carretel con las dimensiones de la turbina (300 mm entre caras según plano).",
                      "Largos de caño tomados del dibujo (el plano no los indica): 8 m de 4\" y 1 m de 6\". Se marcan con (*).",
                      "Materiales, válvulas, instrumentos, juntas y espárragos de marcas del listado SCE-IN-501-0015 de Camuzzi.",
                      "Cupla 3/4\" NPT para cada termovaina (pos 11), necesaria para su montaje, incluida aunque no figura en la tabla del plano.",
                      "Sensor de temperatura A incluido (transmisor 4-20 mA); si lo provee Camuzzi con la correctora, se descuenta.",
                      "Con la oferta se presentan la DDJJ de ética, el Anexo I y los Anexos II y III (Compre Argentino), y la especificación y el plano firmados."],
                     ["Ingeniería de fabricación, cronograma, listado de documentos y documentación para aprobación (ET §3).", "Fabricación del filtro FM-06 según el plano tipo de Camuzzi, con su manómetro diferencial y su manómetro de presión estática.",
                      "Suministro de materiales del plano, juntas y espárragos internos.", "Prefabricado, armado y soldadura en taller; RX 100% y líquidos penetrantes; PH y prueba de fugas.",
                      "Protección anticorrosiva SCE-PC-511-0003.", "Data book (pdf, CD y copia en papel) y certificados.", "Embalaje y flete hasta Transporte Cruz del Sur (Tapiales)."])
ro = C / "oferta.json"
o = json.load(open(ro, encoding="utf-8"))
o["exclusiones"]["items"] += ["Turbina de medición (la provee Camuzzi, ET §4).", "Manómetros de presión estática adicionales al del filtro FM-06 (ET §5.7): la tabla del plano no los lista; se cotizan si Camuzzi lo confirma."]
o["garantia"] = ("Garantía general de 2 años desde la entrega o 1 año desde la instalación, lo que ocurra primero (especificación de Camuzzi, §9), con responsabilidad por vicios ocultos de "
                 "fabricación, más las garantías particulares de materiales e instrumentos.")
json.dump(o, open(ro, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(base["items"]), "ítems")
