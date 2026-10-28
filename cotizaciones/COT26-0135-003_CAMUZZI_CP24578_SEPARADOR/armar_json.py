"""Separador vertical coalescente (CP 24578 ítem 1, 2 un): el concurso no trae plano ni especificación del separador, solo
condiciones de proceso. Diseño preliminar de ITT (ver bitacora.md §Dimensionamiento) y cómputo por componentes.
Escribe pedido/lista_materiales_plano.csv (cómputo de diseño, no es un plano del cliente) y cotizacion.json.
Correr: python cotizaciones/COT26-0135-003_CAMUZZI_CP24578_SEPARADOR/armar_json.py"""
import csv
import json
import math
import sys
from pathlib import Path

C = Path(__file__).resolve().parent
sys.path.insert(0, str(C.parent / "COT26-0135-001_CAMUZZI_CP24578_SKIDREG"))
import camuzzi_comun  # noqa: E402

BIT = "cotizaciones/COT26-0135-003_CAMUZZI_CP24578_SEPARADOR/bitacora.md"
# ---- dimensionamiento preliminar (bitacora.md) ----
N_ELEM = 37            # hacen falta ≈ 34 (3.660 m3/h reales a 25 bar ÷ 108 m3/h por elemento, Sacde/12); en arreglo triangular de 180 mm el anillo completo es 1+6+12+18 = 37 (revisión 28-10-2026)
D_EXT = 1.346          # m (53"): centros hasta 0,54 m de radio + 70 mm de medio elemento + 30 mm de huelgo → DI 1,28 m (con 44" no entraban: revisión 28-10-2026)
T_CUERPO = 41.3        # mm (1 5/8"): ASME VIII Div.1 a 77 bar (70 + 10%), SA-516-70 (S 138 MPa, E 1): 36,7 + 3,2 de corrosión = 39,9 mm
L_CUERPO = 3.2         # m: cámara inferior de separación 1,3 m + placa + cámara de coalescencia (914 mm + 200 mm a la salida + 0,8 m)
kg_cuerpo = round(math.pi * D_EXT * L_CUERPO * T_CUERPO / 1000 * 7850)
kg_placa = round(math.pi * (D_EXT - 0.07) ** 2 / 4 * T_CUERPO / 1000 * 7850)


def fuente(tipo, precio, prov, origen, fecha, coincide="similar", dif=""):
    f = {"tipo": tipo, "precio": round(precio, 2), "proveedor": prov, "origen": origen, "fecha": fecha, "coincide": coincide}
    if dif:
        f["diferencia"] = dif
    return f


EST = lambda precio, criterio, dif="": fuente("est", precio, "Estimado: " + criterio, BIT, "2026-10-28", "sin_ref", dif)
S12 = "fuentes_originales/ofertas_texto/Sacde/12-2970-SE-PTG-008 - FILTRO COALESCENTE - Pedido de precios/4.Armado de la Oferta Comercial/LM costos Filtro Coalecedor FC 301 y 302 #600 PC0-C.xlsx.txt"
C30 = "fuentes_originales/ofertas_texto/CAMUZZI/30 - Separador Polvo y Líquido (2 unid) - Lic 22737/5.Proveedores 3ros/"
L30 = "fuentes_originales/taval_lista30_2025-09.xlsx"
# pos, descripción, Ø, serie/sch, material, extremos, cantidad, unidad, fuentes
M = [
    ("1", f"Chapa para virola Ø53\" × {L_CUERPO:g} m × 1 5/8\" ({kg_cuerpo} kg + 10% recortes)", '53"', "e = 1 5/8\"", "SA-516 Gr. 70", "BW", round(kg_cuerpo * 1.1), "kg",
     [fuente("ant", 1.80, "Planilla Sacde/12 coalescedor FC-301/302: chapa SA-516-70 1 1/2\" a 1,80 USD/kg", S12, "2025-12-18", "similar", "espesor 1 1/2\" (acá 1 5/8\")")]),
    ("2", "Cabezal semielíptico 2:1 Ø53\" × 1 3/4\" (fondo inferior)", '53"', "e = 1 3/4\"", "SA-516 Gr. 70", "BW", 1, "un",
     [fuente("ant", 3000 * (53 / 36) ** 2 * 1.75 / 1.5, "Planilla Sacde/12: cabezal 36\" × 1 1/2\" SA-516-70 a 3.000, escalado por superficie (53/36)² y espesor (1 3/4 ÷ 1 1/2)", S12, "2025-12-18", "similar", "Ø36\" (escalado × 2,53)")]),
    ("3", "Tapa de cierre rápido Ø53\" #600 (70 bar) con pescante, A105N, o-rings de repuesto", '53"', "600", "A105N", "BW", 1, "un",
     [fuente("cot", 14963 * (53 / 28) ** 1.5, "Megatap (CAMUZZI/30): tapa 28\" #600 70 kg/cm2 a 14.963 c/u, escalada × (53/28)^1,5", C30 + "Megatap PPTO ITT SA 27133.pdf.txt", "2026-05-06", "similar", "Ø28\" horizontal; pedir cotización 53\" vertical"),
      fuente("ant", 24288.6 * (53 / 36) ** 1.5, "Planilla Sacde/12: tapa Futura 36\" #600 con pescante 24.288,60, escalada × (53/36)^1,5", S12, "2025-12-18", "similar", "Ø36\"")]),
    ("4", f"Placa portaelementos Ø1,26 m × 1 5/8\" con {N_ELEM} agujeros mecanizados ({kg_placa} kg)", "", "e = 1 5/8\"", "SA-516 Gr. 70", "—", 1, "un",
     [fuente("ant", kg_placa * 1.8, f"{kg_placa} kg × 1,80 USD/kg (chapa SA-516-70, planilla Sacde/12)", S12, "2025-12-18", "similar", "solo la chapa: el corte y el mecanizado de los agujeros, a cotizar")]),
    ("5", "Elemento coalescente 0,3 µm, 140 × 914 mm (5 1/2\" × 36\")", "", "", "fibra de vidrio", "—", N_ELEM, "un",
     [fuente("ant", 854, "Planilla Sacde/12 FC-301/302: elemento filtrante coalescedor (16 u a 854)", S12, "2025-12-18", "similar", "elemento de otro tamaño (no informado); pedir el 0,3 µm 140 × 914 a Gora / Pall")]),
    ("6", "Brida WN RF entrada y salida 10\" #600 sch 80", '10"', "600 x 80", "ASTM A-105", "RF/BW", 2, "un",
     [fuente("cot", 338.45, "Provemet · BRI-01227", "conocimiento/precios/catalogo_materiales.csv", "2025-07-29", "igual")]),
    ("7", "Caño 10\" sch 80 (toberas de entrada y salida)", '10"', "80", "ASTM A-106 Gr. B", "BW", 0.8, "m",
     [fuente("lista", 204.43, "Renard (cód. 1193) · CAN-01420 (273 × 15,09 mm)", "fuentes_originales/renar_lista_2025-12.xlsx", "2025-12-26", "igual")]),
    ("8", "Brida WN RF 6\" #600 sch 80 (boca de inspección a 90° de la entrada)", '6"', "600 x 80", "ASTM A-105", "RF/BW", 1, "un",
     [fuente("cot", 226.14, "Renard · BRI-01320", "conocimiento/precios/catalogo_materiales.csv", "2025-07-11", "igual")]),
    ("9", "Brida ciega RF 6\" #600 (boca de inspección)", '6"', "600", "ASTM A-105", "RF", 1, "un", [fuente("cot", 226.14 * 1.1, "Renard: brida WN 6\" #600 sch 80 a 226,14 (BRI-01320) + 10% (ciega más pesada)", "conocimiento/precios/catalogo_materiales.csv", "2025-07-11", "similar", "precio de la WN de la misma medida y serie")]),
    ("10", "Caño 6\" sch 80 (boca de inspección)", '6"', "80", "ASTM A-106 Gr. B", "BW", 0.3, "m",
     [fuente("ant", 90.70, "Renard · CAN-01512 (planilla de costo ITT)", "conocimiento/precios/catalogo_materiales.csv", "2026-06-26", "igual")]),
    ("11", "Brida WN RF 2\" #600 sch 160 (purgas y stand-pipes de las 2 cámaras)", '2"', "600 x 160", "ASTM A-105", "RF/BW", 6, "un",
     [fuente("cot", 25.60, "Oil Metal · BRI-01255", "conocimiento/precios/catalogo_materiales.csv", "2025-07-03", "igual")]),
    ("12", "Caño 2\" sch 160 (conexiones y stand-pipes)", '2"', "160", "ASTM A-106 Gr. B", "BW", 4, "m",
     [fuente("ant", 24.67, "CAN-01454 (planilla de costo ITT)", "conocimiento/precios/catalogo_materiales.csv", "2026-06-26", "igual")]),
    ("13", "Brida WN RF 1\" #600 sch 160 (visores y manómetros)", '1"', "600 x 160", "ASTM A-105", "RF/BW", 7, "un",
     [fuente("cot", 25.00, "Oil Metal · BRI-01201", "conocimiento/precios/catalogo_materiales.csv", "2025-07-03", "igual")]),
    ("14", "Válvula esférica 2\" #600 PT RF (bloqueos de purgas y stand-pipes)", '2"', "600", "A216 WCB", "RF", 6, "un",
     [fuente("lista", 220, "Taval (Lista 30 × 0.52) · VAL-04447", L30, "2025-09-01", "igual")]),
    ("15", "Válvula esférica 1/2\" NPT API 608 (visores y manómetros)", '1/2"', "2000", "A105", "NPT", 8, "un",
     [fuente("lista", 36.06, "Taval (Lista 30 × 0.52) · VAL-04865", L30, "2025-09-01", "similar", "#2000 NPT")]),
    ("16", "Purga automática de líquidos (controlador de nivel + válvula), una por cámara", "", "600", "", "—", 2, "un", [{"tipo": "est", "precio": 0, "proveedor": "SIN PRECIO: pedir cotización", "origen": "—", "fecha": "2026-10-28", "coincide": "sin_ref", "diferencia": "purga automática #600: no hay precio ni pieza parecida"}]),
    ("17", "Switch de nivel alto sobre stand-pipe, Ex-d, una por cámara", "", "", "", "—", 2, "un", [{"tipo": "est", "precio": 0, "proveedor": "SIN PRECIO: pedir cotización", "origen": "—", "fecha": "2026-10-28", "coincide": "sin_ref", "diferencia": "switch de nivel Ex-d para 70 bar: no hay precio ni pieza parecida"}]),
    ("18", "Visor de nivel óptico reflex 500 mm, 70 bar, una por cámara", "", "", "", "—", 2, "un",
     [fuente("cot", 685, "Riva Hnos: indicador de nivel reflex 500 mm, 70 bar", C30 + "Riva Hnos - Cotización de indicadores de nivel.msg.txt", "2026-02-12", "igual")]),
    ("19", "Manómetro de presión diferencial con aguja de arrastre y contacto seco", "", "", "", "—", 1, "un", [fuente("ant", 500, "Weisz: manómetro diferencial 0-2 bar (planilla TAVAL/40)", "fuentes_originales/ofertas_texto/TAVAL/40- INARTECO FILTROS LIC 9333/4.Armado de la Oferta Comercial/LM costo Filtros rev.1.xlsx.txt", "2026-01-15", "similar", "sin aguja de arrastre ni contacto seco: pedir cotización")]),
    ("20", "Manómetro de presión estática Ø100 con glicerina + manifold de 3 vías", "", "", "", "—", 1, "un",
     [fuente("ant", 290, "Weisz 120 (INS-02702) + manifold ABAC 3 vías 170 (planilla TAVAL/40)", "fuentes_originales/ofertas_texto/TAVAL/40- INARTECO FILTROS LIC 9333/4.Armado de la Oferta Comercial/LM costo Filtros rev.1.xlsx.txt", "2026-01-15", "similar", "Weisz o similar; manifold ABAC")]),
    ("21", "Internos: deflector de entrada, rompe-vórtice, soportes y fijaciones de elementos", "", "", "SA-516 / AISI 316", "—", 1, "gl", [{"tipo": "est", "precio": 0, "proveedor": "SIN PRECIO: pedir cotización", "origen": "—", "fecha": "2026-10-28", "coincide": "sin_ref", "diferencia": "internos del separador: dependen del diseño; no hay pieza parecida"}]),
    ("22", "Juntas espiraladas y espárragos de las conexiones internas (6\", 2\" y 1\" #600)", "", "600", "AISI 316 / B7", "—", 1, "gl", [fuente("ant", 350, "Juntas MS Juntas (cot. 48.445/48.729: 2,30 a 5,82) y espárragos de planillas 2026 (2,50 a 10): 1 junta 6\" + 6 de 2\" + 7 de 1\" #600 con 12, 48 y 28 espárragos", "fuentes_originales/ofertas_texto/TAVAL/72- Lic 64675 - SKID CONCENTRADOR - UTE NARAMBUE/5.Proveedores 3ros/COTIZACION_N§_048729.pdf.txt", "2026-07-06", "similar", "precios de piezas parecidas por renglón")]),
    ("23", "Skid y plataforma de acceso con escalera y baranda (1.300 kg estimados)", "", "", "ASTM A-36", "—", 1300, "kg",
     [fuente("cot", 17.4 / 13.4 * 1.10, "Grupo Provemet cot. 236623: UPN 120 a 17,40/m (1,30 USD/kg +10% recortes) como precio por kg de perfiles", "fuentes_originales/listas_vendedor/2026-10-28/provemet_cotizacion_236623_perfiles_2025-07-01.pdf", "2025-07-01", "similar", "kilos estimados; rejilla y escalera a cotizar")]),
    ("24", "Pollera / patas de apoyo (450 kg)", "", "e = 1\"", "ASTM A-36", "—", 450, "kg",
     [fuente("ant", 1.2744, "Chapa negra A36 (precios de acero por kg, J. Elejondo) +10% recortes", "conocimiento/precios/acero_por_kg.csv", "2026-02-10", "similar", "chapa 1/2\" de la lista (acá 1\")")]),
]
with open(C / "pedido" / "lista_materiales_plano.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["pos", "descripcion", "diametro", "serie_sch", "material", "extremos", "modelo_fabricante", "cantidad", "unidad", "extremos_campo"])
    for pos, desc, d, s, mat, ext, q, u, _ in M:
        w.writerow([pos, desc, d, s, mat, ext, "diseño preliminar ITT (sin plano del cliente)", q, u, 0])
items = [{"id": f"M{int(p):02d}", "pos": p, "grupo": "material", "descripcion": desc, "especificacion": f"{d} {s} {mat}".strip(), "cantidad": q, "unidad": u, "fuentes": f}
         for p, desc, d, s, mat, ext, q, u, f in M]
ROL = C30 + "Sandri rolado de chapa esp 1.docx.txt"
items += [
    {"id": "S01", "pos": "ROL", "grupo": "servicio", "descripcion": f"Rolado y punteado de la virola ({kg_cuerpo} kg)", "especificacion": "Sandri: 2 virolas 26\" × 2,5 m × 1\" A516 (≈ 1.033 kg c/u) a ARS 2.550.000 + IVA c/u = 1,74 USD/kg (BNA 03-2026 1.416,29)",
     "cantidad": kg_cuerpo, "unidad": "kg", "fuentes": [fuente("cot", 2550000 / 1416.29 / 1033, "Juan y Víctor Sandri S.A.: cilindrado y punteado ARS 2.550.000 + IVA por virola de 1.033 kg", ROL, "2026-03-25", "similar", "Ø26\" × 1\" (acá 53\" × 1 5/8\")"),
                                                         fuente("ant", 3.7, "Rolado 3,70 USD/kg (tarifas.csv, AESA/44)", "conocimiento/costos/tarifas.csv", "2025-09-30", "similar")]},
    {"id": "S02", "pos": "MO", "grupo": "mo", "descripcion": "Fabricación del separador y del skid por tercero (armado, soldadura, internos, montaje sobre skid)", "especificacion": "Ledesma 28\" #600 + skid 13.000 (CAMUZZI/30) × 2,2 por tamaño (53\" vertical de 1 5/8\", plataforma)",
     "cantidad": 1, "unidad": "gl", "fuentes": [fuente("cot", 13000 * 2.2, "Edgardo Ledesma: separador de polvo y líquido 28\" #600 + skid, USD 13.000 (no incluye plegado de cunas, PH ni END), × 2,2 por tamaño", C30 + "E Ledesma - Cotización de Separador de polvo y líquido 28_ #600.pdf.txt", "2026-05-10", "similar", "28\" horizontal; pedir cotización con el diseño")]},
    {"id": "S03", "pos": "RX", "grupo": "servicio", "descripcion": "Radiografía 100% de costuras y toberas + tintas penetrantes", "especificacion": "≈ 12 m de costura en 1 5/8\" + toberas", "cantidad": 1, "unidad": "gl",
     "fuentes": [fuente("ant", 60 * 8 + 20 * 6.5 + 2 * 408, "Tarifas DB NDT (tarifas.csv): 60 placas grandes × 8 + 20 chicas × 6,50 + 2 servicios × 408", "conocimiento/costos/tarifas.csv", "2026-08-31", "similar", "placas estimadas por metro de costura; confirmar con el mapa de soldaduras")]},
    {"id": "S04", "pos": "PH", "grupo": "servicio", "descripcion": "Prueba hidráulica (1,5 × presión de diseño) con registro", "especificacion": "", "cantidad": 16, "unidad": "h", "fuentes": [fuente("ant", 13, "Prueba hidráulica por hora de planta (END-00215, MO ITT)", "conocimiento/precios/catalogo_servicios.csv", "2026-03-10", "similar", "16 h para un recipiente de ≈ 5 m³ (llenado, 6 h de prueba, vaciado y secado)")]},
    {"id": "S05", "pos": "PIN", "grupo": "servicio", "descripcion": "Granallado y pintura (≈ 38 m²)", "especificacion": "cuerpo 13,5 m² + fondo 2 + skid y plataforma ≈ 22", "cantidad": 38, "unidad": "m2",
     "fuentes": [fuente("ant", 50, "Granallado y pintura piping (incluye materiales), criterio ITT · PIN-00569", "conocimiento/precios/catalogo_servicios.csv", "2026-10-10", "similar", "esquema SCE-PC-511-0003 a confirmar")]},
    {"id": "S06", "pos": "HH", "grupo": "mo", "descripcion": "Ingeniería: memoria de cálculo ASME VIII Div.1, planos y documentación", "especificacion": "150 h (Sacde/12 coalescedor: 250 h)", "cantidad": 150, "unidad": "h",
     "fuentes": [fuente("est", 15, "Horas propias ITT (15 USD/h); 150 h por criterio, contra 250 h del coalescedor Sacde/12", "conocimiento/costos/horas_por_equipo.csv", "2025-12-18", "similar", "estimado")]},
    {"id": "S07", "pos": "CAL", "grupo": "mo", "descripcion": "Calidad, inspecciones y data book", "especificacion": "120 h", "cantidad": 120, "unidad": "h",
     "fuentes": [fuente("est", 15, "Horas propias ITT (15 USD/h); criterio", "conocimiento/costos/horas_por_equipo.csv", "2025-12-18", "similar", "estimado")]},
    {"id": "S08", "pos": "ARM", "grupo": "mo", "descripcion": "Montaje propio: instrumentos, purgas, stand-pipes, movimientos y PH", "especificacion": "160 h", "cantidad": 160, "unidad": "h",
     "fuentes": [fuente("est", 16, "Horas propias ITT (16 USD/h en recipientes); criterio", "conocimiento/costos/horas_por_equipo.csv", "2025-12-18", "similar", "estimado")]},
]
base = json.load(open(C.parent / "_plantilla" / "cotizacion.json", encoding="utf-8"))
base.update({"codigo": "COT26-0135-003", "fecha": "2026-10-28", "cliente": {"nombre": "CAMUZZI GAS PAMPEANA S.A. / CAMUZZI GAS DEL SUR S.A.", "codigo_itt": "0135", "comprador": "Gerencia de Abastecimiento Obras y Almacenes (Juan Filas)"},
             "titulo": "Camuzzi · Concurso de precios N° 24578 ítem 1 — 2 separadores verticales coalescentes (diseño preliminar ITT)",
             "titulo_pagina": "Cotización Camuzzi CP 24578 · Separador coalescente", "archivo_planilla": "CAMUZZI_CP24578_SEPARADOR_COALESCENTE",
             "subtitulo_planilla": f"2 separadores verticales coalescentes Ø53\" #600, {N_ELEM} elementos · diseño preliminar ITT · USD sin IVA",
             "meta": ["Concurso de precios N° 24578 · ítem 1", "Sin plano ni especificación del separador: diseño preliminar ITT", "Comprador: Camuzzi (portal de compras)", "Preparó: Matías Russo · 28-10-2026"],
             "equipo": {"singular": "separador", "plural": "separadores", "tipo": "filtro", "diametro_pulg": 53}, "items": items})
base["parametros"].update({"N": 2, "fecha_referencia": "2026-10-28", "rx_pct": 0, "ph_horas": 0, "TRANS": 1, "TC": 1541.43, "TR_ARS": 1400000, "TR_EMB": 300, "TR_F": 1.0})
base["plazo"] = {"dias": 165, "texto": "desde OC · entregado en Transporte Cruz del Sur (Tapiales)",
                 "tareas": [["Memoria de cálculo y planos para aprobación de Camuzzi", 0, 25, ""], ["Tapas de cierre rápido 53\" #600 (Megatap 90/110 días desde anticipo y datos de diseño)", 25, 135, "crit"],
                            ["Chapa, rolado, bridas y elementos", 25, 70, ""], ["Soldadura del cuello de la tapa, RX y PH", 135, 150, "tal"], ["Instrumentos, pintura, inspección y despacho", 150, 165, "tal"]],
                 "nota": "Fija el plazo la tapa de cierre rápido (90/110 días desde anticipo y certificación de los datos de diseño, que salen de la memoria de cálculo)."}
base["flete"] = {"etiqueta": "Flete a Transporte Cruz del Sur (Tapiales)", "referencia_html": "<b>Estimado:</b> camión con hidrogrúa para los 2 separadores (≈ 30 km): ARS 1.400.000 + USD 300 de embalaje.",
                 "criterio_html": "La planilla del concurso pone el flete a cargo del proveedor hasta Transporte Cruz del Sur."}
base["pedido"] = {"eyebrow": "Concurso de precios N° 24578 · ítem 1", "datos_html": [["Cliente", "Camuzzi Gas Pampeana S.A. / Camuzzi Gas del Sur S.A. (código ITT 0135)"],
                  ["Ítem", "1 · Separador vertical coalescente sobre skid con plataforma · <b>2 un</b>"], ["Condiciones", "Pe máx 70 bar · Pe mín 25 bar · Qmáx 100.000 Sm3/h · filtrado 0,3 µm · cartuchos 140 × 914 mm"],
                  ["Documentos", "Solo la descripción de la planilla: el esquema y la especificación que menciona NO vinieron en el pedido"],
                  ["Entrega pedida", "Transporte Cruz del Sur, Mercado Central nave D3, Tapiales"]],
                  "requisitos_html": ["Entrada y salida a 180°, preferentemente 10\" #600", "Purga automática; switch de nivel alto Ex-d sobre stand-pipe en ambas cámaras; visor de nivel en ambas cámaras",
                                      "Manómetro diferencial con aguja de arrastre y contacto seco; manómetro estático", "Boca de inspección 6\" #600 a 90° de la entrada",
                                      "Salida a 200 mm del límite superior de los cartuchos; 40 mm entre elementos", "Un juego de elementos por equipo",
                                      "<b>Con la oferta:</b> memoria de cálculo (cantidad de elementos, diámetros, espesores) y esquema con dimensiones generales"]}
base["nota_mo_html"] = (f"Diseño preliminar: {N_ELEM} elementos, cuerpo Ø53\" × {L_CUERPO:g} m × 1 5/8\" SA-516-70 ({kg_cuerpo} kg), fondo 2:1, tapa de cierre rápido superior, 2 cámaras. "
                        "Fabricación por tercero (Ledesma, escalado de su presupuesto del separador 28\" #600 de CAMUZZI/30); ITT pone ingeniería, calidad, montaje de instrumentos, RX, PH y pintura.")
base["desvios"] = [{"tag": "Todo", "titulo": "Diseño preliminar sin especificación", "texto": "La especificación y el esquema que cita la planilla no vinieron. La cantidad de elementos y el diámetro salen de un dimensionamiento preliminar: hay que hacer la memoria de cálculo antes de presentar."}]
base["antecedentes"] = [
    {"carpeta_html": "<b>CAMUZZI/30</b> · Concurso 22737", "fecha": "14-05-2026", "que": "2 separadores horizontales de polvo y líquido 28\" #600, 11 elementos 140 × 914", "precio": "venta 93.033 c/u", "tomado_html": "Tapa Megatap, MO Ledesma, rolado Sandri, elementos Gora, visores Riva"},
    {"carpeta_html": "<b>Sacde/12</b> · Filtro coalescente FC-301/302", "fecha": "18-12-2025", "que": "Coalescedor 36\" #600, 16 elementos, planilla de costo", "precio": "costo con planilla", "tomado_html": "Caudal por elemento, chapa por kg, cabezal y tapa Futura"}]
base["pendientes"] = [{"titulo": "Ingeniería", "items": ["<b>CRÍTICO para presentar:</b> el concurso exige entregar con la cotización la memoria de cálculo y el esquema con dimensiones generales; sin eso la oferta incumple el ítem 1", "Memoria de cálculo ASME VIII (espesores) y dimensionamiento con el fabricante de elementos (Gora / Pall): caudal por elemento a 25 bar", "Esquema con dimensiones generales (lo pide el concurso con la oferta)"]},
                      {"titulo": "Proveedores", "items": ["Tapa de cierre rápido 53\" #600 vertical (Megatap / Futura)", "Elementos coalescentes 0,3 µm 140 × 914", "Purgas automáticas, switches de nivel Ex-d, manómetro diferencial con contacto", "Fabricación (Ledesma) con el diseño"]},
                      {"titulo": "Camuzzi", "items": ["Pedir la especificación técnica y el esquema del separador que menciona la planilla (no vinieron)"]}]
base["planilla_notas"] = ["Plazo: 165 días desde OC (tapa de cierre rápido 90/110 días desde la memoria de cálculo; el cuerpo y el skid se fabrican mientras tanto).", "Precio preliminar: diseño sin especificación del cliente, ±30%."]
base["pie"] = "Fuentes: base de conocimiento del repositorio cotizador-itt. Precios en USD sin IVA. Borrador sin revisar; diseño preliminar."
base["compras"] = {"fecha_respuesta": "2026-11-06", "material_en_planta_dias": 110, "lugar_entrega": "Planta ITT S.A., Av. 12 de Octubre 4004, Quilmes Oeste, Bs. As.",
                   "requisitos_generales": ["Cotizar en USD sin IVA, con plazo y validez.", "Certificados 3.1 de chapas, bridas y caños.", "Las cantidades son por separador × 2."],
                   "notas": {"3": "Vertical, 53\" #600, 77 bar de diseño", "5": "Coalescente 0,3 µm; indicar caudal por elemento a 25 bar"}, "proveedores": {"3": "Megatap / Futura", "5": "Gora", "18": "Riva Hnos"},
                   "cantidad_compra": {}, "servicios": [{"servicio": "Rolado de virola Ø53\" × 1 5/8\"", "proveedores": "Sandri", "referencia": "1,74 USD/kg (03-2026)", "nota": ""},
                                                        {"servicio": "Fabricación del separador y skid", "proveedores": "Ledesma", "referencia": "13.000 el 28\" (05-2026)", "nota": "con el diseño"}]}
json.dump(base, open(C / "cotizacion.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
camuzzi_comun.oferta(C, "COT26-0135-003", "Separador coalescente", 1, "separador vertical coalescente sobre skid con plataforma de acceso (filtrado 0,3 µm, Pe 25-70 bar, Qmáx 100.000 Sm3/h)", "2", 165,
                     ["Concurso de precios N° 24578: planilla de cotización (ítem 1), cláusulas particulares y condiciones generales"],
                     f"Separador vertical coalescente de dos cámaras, cuerpo Ø53\" en SA-516-70 de 1 5/8\", diseño ASME VIII Div.1 a 70 bar, conexiones 10\" #600 a 180°, {N_ELEM} elementos coalescentes 0,3 µm de 140 × 914 mm, tapa de cierre rápido, boca de inspección 6\" #600, purga automática, switch de nivel Ex-d y visor en cada cámara, manómetros diferencial y estático, sobre skid con plataforma de acceso.",
                     ["Diseño preliminar: la especificación y el esquema del separador citados en la planilla no se recibieron. Se entregará la memoria de cálculo y el esquema con dimensiones generales.",
                      "Un juego de elementos instalado por equipo."],
                     ["Memoria de cálculo y planos para aprobación.", "Suministro de materiales, elementos e instrumentos.", "Fabricación, RX, PH, pintura y montaje sobre skid con plataforma.", "Data book.", "Embalaje y flete hasta Transporte Cruz del Sur (Tapiales)."])
print(len(items), "ítems · cuerpo", kg_cuerpo, "kg · placa", kg_placa, "kg")
