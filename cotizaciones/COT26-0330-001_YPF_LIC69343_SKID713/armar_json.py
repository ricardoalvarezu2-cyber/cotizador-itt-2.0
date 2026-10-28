"""Arma cotizacion.json de los dos skids YPF desde cotizacion_auto.json (catálogo) y la planilla PC0 del pedido."""
import json, sys, csv
sys.path.insert(0, "/tmp/claude-0/-home-user-cotizador-itt/82ad64dc-b6db-5ba7-866e-adf8ec6ac548/scratchpad/ypf")
import pc0
R = "/home/user/cotizador-itt/"
ORIGEN = "fuentes_originales/pedidos_web/pmvrzbrh616ftx/Cotización Lic 69343 Skid concentradores VCD26217 PC0.xlsx.md"
FPC0 = "2026-10-10"  # recepción del pedido (hoja Resumen); la planilla PC0 no fecha cada precio
acero = {r["forma"] + r["medida"]: r for r in csv.DictReader(open(R + "conocimiento/precios/acero_por_kg.csv", encoding="utf-8"))}
H = pc0.hojas()

def fpc0(p, hoja, nota=""):
    v = pc0.precios(H[hoja])[p]
    prov = v["prov"].strip() or "sin proveedor en la planilla"
    return {"tipo": "est", "precio": round(v["precio"], 4), "proveedor": f"Planilla PC0 de este pedido · {prov}", "origen": f"{ORIGEN} · hoja {hoja}",
            "fecha": FPC0, "coincide": "igual",
            "diferencia": ("precio de la planilla PC0 sin fecha ni documento del proveedor: confirmar con Compras" + (f" · {nota}" if nota else ""))}

def serv(id_, pos, grupo, desc, esp, cant, un, fuente):
    return {"id": id_, "pos": pos, "grupo": grupo, "descripcion": desc, "especificacion": esp, "cantidad": cant, "unidad": un, "fuentes": [fuente]}

def est(precio, prov, dif, origen=ORIGEN, fecha=FPC0, coincide="similar"):
    return {"tipo": "est", "precio": precio, "proveedor": prov, "origen": origen, "fecha": fecha, "coincide": coincide, "diferencia": dif}

for carp, hoja, kg, m2_pip, m2_skid, instr, rep in [
        ("COT26-0330-001_YPF_LIC69343_SKID713", "1000623713", 2100, 50, 50,
         [("TI-011A/B/C/D", "Termómetro (la planilla lo rotula «Manómetro»: rótulos cruzados)", 4, 120, "Weisz"),
          ("TW-011A/B/C/D", "Termovaina bridada", 4, 150, "Abac"),
          ("PI-011A/B/C/D", "Manómetro (la planilla lo rotula «Termómetro 0-200 °C, cuadrante 4\"»)", 4, 100, "Weisz"),
          ("VBP", "Válvula de bloqueo y purga", 2, 150, "Weisz")], 353.62),
        ("COT26-0330-002_YPF_LIC69343_SKID708", "1000623708", 850, 22, 21,
         [("TI-014A/B/C", "Termómetro bimetálico dial 5\" cuerpo y vástago AISI 316", 3, 150, "sin proveedor"),
          ("TW-014A/B/C", "Vaina (termopozo) bridada 1 1/2\" 300 LB RF barstock AISI 316", 3, 100, "sin proveedor"),
          ("PI-014A/B/C", "Manómetro dial 4\" inox c/glicerina, conexión 1/2\" NPT inferior", 3, 120, "sin proveedor")], 0)]:
    c = json.load(open(R + f"cotizaciones/{carp}/cotizacion.json", encoding="utf-8"))
    a = json.load(open(R + f"cotizaciones/{carp}/cotizacion_auto.json", encoding="utf-8"))
    items = []
    for it in a["items"]:
        if it["grupo"] != "material":
            continue
        p = it["pos"].rstrip("b")
        f0 = it["fuentes"][0]
        if it["pos"].endswith("b"):
            if f0["coincide"] == "igual":
                items.append(it)
            continue
        alt = fpc0(p, hoja)
        if f0["coincide"] == "igual" and f0["precio"]:
            it["fuentes"] = [f0, alt]
        else:
            it["fuentes"] = [alt] + ([{**f0, "coincide": "similar" if f0["precio"] else "sin_ref"}] if f0["precio"] else [])
        items.append(it)
    # estructura del skid (perfilería por kg, cantidad de la planilla PC0)
    ang = next(v for k, v in acero.items() if v["forma"] == "hierro ángulo")
    items.append(serv("M90", "EST", "material", "Estructura del skid: perfilería", f"{kg} kg según planilla PC0 (no hay plano de estructura)", kg, "kg",
                      {"tipo": "cot", "precio": float(ang["usd_kg_con_recortes"]), "proveedor": "Precios de acero (J. Elejondo) · hierro ángulo", "origen": ang["fuente"],
                       "fecha": ang["fecha"], "coincide": "similar", "diferencia": f"kg de la planilla PC0 ({kg} kg) a precio de ángulo {ang['medida']}; la PC0 usa USD 2/kg; perfiles exactos sin plano"}))
    for k, (tag, d, q, pu, prov) in enumerate(instr, 1):
        items.append(serv(f"M9{k}", "INS", "material", f"{tag}: {d}", "Instrumental según planilla PC0", q, "un",
                          est(pu, f"Planilla PC0 · {prov}", "precio de la planilla PC0 sin documento del proveedor; el alcance de la PC0 dice «Instrumental: NO» pero lo cotiza: confirmar con el cliente", coincide="igual")))
    if rep:
        items.append(serv("M98", "REP", "material", "Repuestos PEM y 2 años (10% de bulonería y juntas)", "Listas de la planilla PC0 (2 × USD 176,81)", 1, "gl",
                          est(rep, "Planilla PC0", "la hoja Resumen de la PC0 suma USD 3.520,04 por repuestos, pero sus listas dan USD 353,62: se toman las listas; confirmar el alcance")))
    else:
        items.append(serv("M98", "REP", "material", "Repuestos PEM y 2 años (10% de bulonería y juntas)", "Sin definir", 1, "gl",
                          {"tipo": "est", "precio": 0, "proveedor": "SIN PRECIO: definir la lista", "origen": ORIGEN, "fecha": FPC0, "coincide": "sin_ref",
                           "diferencia": "la lista de repuestos de esta hoja en la PC0 es la del otro skid (espárragos 7/8\" y juntas 8\" que este skid no tiene); la hoja Resumen suma USD 2.305,40: armar la lista con los espárragos 1 1/4\" y 1 1/8\" y las juntas 12\" y 16\""}))
    # MO y servicios
    for it in a["items"]:
        if it["grupo"] == "material":
            continue
        if it["pos"] == "PIN":
            a_m2 = it["cantidad"]
            it["cantidad"] = m2_pip
            it["especificacion"] = f"{m2_pip} m² de piping con overspray 20% (planilla PC0); el cálculo de caños y niples da {a_m2:.2f} m²"
            it["fuentes"][0]["diferencia"] = "m² de la planilla PC0 (incluye accesorios, bridas y válvulas); esquema Pampa RAL 7039 a confirmar"
        if it["pos"] == "MO":
            it["fuentes"].append(est(28000 if hoja == "1000623713" else 13250, "Planilla PC0 · Ledesma (tercero): piping y skid", "otro alcance: la PC0 terceriza soldadura y armado (más USD 6.000 / 3.000 de montaje, dimensional y desmontaje)"))
        items.append(it)
    items.append(serv("S20", "MOE", "mo", "Fabricación de la estructura del skid (tercero)", f"{kg} kg × USD 3/kg (Ledesma, planilla PC0 hoja 1000623708: 850 kg × 3 = 2.550)", kg, "kg",
                      est(3.0, "Planilla PC0 · Ledesma (tercero): estructura por kg", "precio por kg de la PC0 (cálculo al margen de la MO de Ledesma), sin presupuesto del taller: confirmar", origen=ORIGEN + " · hoja 1000623708", coincide="igual")))
    items[-1]["fuentes"].append({"tipo": "ant", "precio": 5.10, "proveedor": "Costo propio de planta: 61,16 USD/hh / 12 kg/h", "origen": "conocimiento/costos/tarifas.csv · costo_mo_planta_2024-10",
                                 "fecha": "2024-10-31", "coincide": "similar", "diferencia": "costo propio con cepo (oct-2024), alternativa"})
    items.append(serv("S21", "PINE", "servicio", "Granallado y pintura de la estructura", f"{m2_skid} m² con overspray 20% (planilla PC0)", m2_skid, "m2",
                      est(50.0, "Criterio ITT USD 50/m² con materiales (como el piping)", "m² de la planilla PC0; esquema Pampa a confirmar")))
    items.append(serv("S22", "CAU", "servicio", "Seguro de caución", "Planilla PC0", 1, "gl",
                      est(459.2, "Planilla PC0", "monto de la planilla PC0 sin póliza: confirmar con Administración", coincide="igual")))
    c["items"] = items
    c["equipo"]["tipo"] = "skid"
    c["parametros"].update({"TRANS": 0, "ph_horas": 0})
    json.dump(c, open(R + f"cotizaciones/{carp}/cotizacion.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(carp, len(items), "ítems")

# ---- datos generales (segunda pasada)
for carp, hoja, art, plano, N, items_pv in [("COT26-0330-001_YPF_LIC69343_SKID713", "1000623713", "1000623713", "VCD21223PPL020015D0", 3, "2, 5 y 7"),
                                            ("COT26-0330-002_YPF_LIC69343_SKID708", "1000623708", "1000623708", "VCD21223PPL020019D0", 6, "1, 3, 4, 6, 8 y 9")]:
    p = R + f"cotizaciones/{carp}/cotizacion.json"
    c = json.load(open(p, encoding="utf-8"))
    c["plazo"] = {"dias": 120, "texto": "desde la aprobación de la documentación · EXW Quilmes Oeste",
                  "tareas": [["Documentación e ingeniería", 0, 20, "tal"], ["Válvulas Taval (120 d sin stock)", 0, 120, "crit"],
                             ["Accesorios y bridas 8\"–16\"", 20, 80, "crit"], ["Taller: armado, soldadura, RX, PH y pintura", 80, 115, "tal"], ["Dossier y despacho", 115, 120, "tal"]],
                  "nota": "La planilla PC0 ofrece 90/120 días desde la aprobación de documentación; las válvulas Taval son 7 días con stock y 120 sin stock. Con stock de válvulas el plazo baja a unos 90 días."}
    c["flete"] = {"etiqueta": "Flete a Rincón de Aranda (Neuquén)", "referencia_html": "Planilla PC0: USD 2.800 por camión a Neuquén (hoja del skid) y USD 3.000 por camión completo (hoja Resumen); sin cotización del transportista.",
                  "criterio_html": "Se cotiza EXW Quilmes Oeste. La PC0 mezcla EXW (hojas de cada skid) con entrega en Rincón de Aranda (hoja Resumen): confirmar con Ventas."}
    c["historial_html"] = [f"28-10-2026 · Rev 0 · recotización automática de la planilla PC0 (pedido {'pmvrzbrh616ftx'} desde la página)"]
    c["pedido"] = {"eyebrow": "Lic 69343 (la PC0 dice 69434) · recibido 10-10-2026 · vence 27-10-2026",
                   "datos_html": [["Cliente", "YPF S.A. (código ITT 0330) · Bloque LAN"], ["Ítem", f"SKID CONCEN.YPF PL.{plano} · SAP {art} · <b>{N} un</b> (ítems {items_pv} del pie de venta)"],
                                  ["Documento", f"Plano conjunto de cañerías {art} (no adjunto: la tabla se tomó de la planilla PC0)"], ["Entrega pedida", "Rincón de Aranda, locación de Pampa Energía (según la hoja Resumen)"],
                                  ["Fechas", "Recepción 10-10-2026 · vencimiento 27-10-2026 · necesidad según el pie de venta (06-2027 a 12-2027)"]],
                   "requisitos_html": ["ASME B31.3 · radiografía 100% (LP donde no se pueda RX)", "Presión de diseño 52 kg/cm² · prueba hidráulica 78 kg/cm² · -29 / 38 °C",
                                       "Revestimiento: esquema Pampa RAL 7039", "Tubo ASTM A106 Gr.B, accesorios A234 WPB, bridas A105, válvulas Taval"]}
    c["nota_mo_html"] = "Soldadura propia de planta, junta por junta desde los extremos (el caño va por metro: cada extremo BW de accesorio o brida es una junta). La planilla PC0 terceriza soldadura y armado en Ledesma; ese valor queda como alternativa. Sin el plano no se pudo ver qué extremos quedan para campo: se supone todo en taller."
    c["desvios"] = [{"tag": "Válvulas retención", "titulo": "Trim no indicado en plano", "texto": "Se ofrece trim 8 (a confirmar), como en la PC0."},
                    {"tag": "Válvulas NPT", "titulo": "Material no indicado", "texto": "Cuerpo A105 (clase CE22 acero al carbono); globos API 602 A105 trim 5."}]
    c["antecedentes"] = [{"carpeta_html": "<b>TAVAL/72</b> · Lic 64675 skid concentrador UTE Narambue", "fecha": "08-07-2026", "que": "Skid manifold concentrador SCC-010 3×8\" + 1×12\" #300 C22", "precio": "—", "tomado_html": "referencia de alcance (no se tomaron precios)"},
                         {"carpeta_html": "<b>TAVAL/78</b> · LIC66577 skid concentrador L. Camp", "fecha": "19-08-2026", "que": "Manifold concentrador 4\"x10\" + salida 4\" a 12\"", "precio": "—", "tomado_html": "referencia de alcance (no se tomaron precios)"}]
    c["pendientes"] = [{"titulo": "Proveedores", "items": ["Cotizar accesorios y bridas 8\"–16\" (tees, tees de reducción, bridas WN XS/SCH 60): hoy son precios de la PC0 sin documento", "Confirmar con Taval precio y stock de las válvulas"]},
                       {"titulo": "Cliente / Ventas", "items": ["Cliente, comprador y N confirmados", "EXW o entregado en Rincón de Aranda", "Instrumental: la PC0 dice «NO» en el alcance pero lo cotiza", "Plano de cañerías (para soldaduras de campo y estructura)"]}]
    c["planilla_notas"] = ["Plazo: 120 días desde la aprobación de documentación (válvulas Taval sin stock).", "Borrador sin revisar: recotización automática de la planilla PC0. EXW Quilmes Oeste, USD sin IVA."]
    c["compras"] = {"fecha_respuesta": "2026-11-04", "material_en_planta_dias": 80, "lugar_entrega": "Planta ITT S.A., Av. 12 de Octubre 4004, Quilmes Oeste, Bs. As.",
                    "requisitos_generales": ["Cotizar en USD sin IVA, con plazo de entrega y validez de la oferta.", "Certificados de material (colada / 3.1).", "Indicar cualquier diferencia con lo pedido (serie, material, extremos, modelo)."],
                    "notas": {}, "proveedores": {}, "cantidad_compra": {}, "servicios": [{"servicio": "Radiografía 100% y LP", "proveedores": "NDT Antonelli", "referencia": "tarifas 03-11-2025", "nota": ""}]}
    json.dump(c, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
