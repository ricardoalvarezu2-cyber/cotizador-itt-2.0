"""Hoja "Planilla ITT" de la planilla de cotización: la distribución de la planilla base de ITT que lee la dirección
(encabezado del pedido, cuadro de rentabilidad, plazo y entrega, alcance SI/NO, material principal y END, y un bloque
por rubro con descripción, descripción ampliada, cantidad, unidad, USD/un y subtotal). Pedido de Matías, 03-11-2026;
modelo en fuentes_originales/planillas_modelo/Planilla_base_para_cotizaciones.xlsx.

Los números no se cargan a mano: cada renglón toma su precio ajustado y su subtotal de las hojas Materiales y
"MO y servicios" y el cuadro de rentabilidad sale de la hoja Cotización, así que el total es el mismo de siempre.
La página arma la misma hoja (web/src/documentos.js, planillaItt)."""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from indice_proyectos import norm  # noqa: E402

# bloques en el orden de la planilla base (los dos "Otros" no están en la base: se agregan para no perder renglones)
BLOQUES = ["Recipiente", "Piping", "Skid", "Plataforma / escaleras", "Válvulas manuales", "Instrumental", "Instalación eléctrica",
           "Aislación", "Tracing eléctrico", "Otros materiales", "Mano de obra de 3ros", "Mano de obra ITT", "Granallado y pintura",
           "Ensayos no destructivos", "Embalaje", "Transporte a destino final", "Seguro de Caución", "Otros servicios"]
INSTRUMENTOS = (r"^(sensor|transmisor|presion regulada|temperatura|switch|interruptor|manometro|termometro|termovaina|indicador|"
                r"toma multiport|regulador y filtro|tubing|conector)|\bdoble virola\b|\binstrumento")
RECIPIENTES = r"filtro|separador|recipiente|tanque|calentador|trampa|coalesc|depurador|scrubber|slug"


def es_recipiente(cfg):
    e = cfg.get("equipo") or {}
    return bool(re.search(RECIPIENTES, norm(f"{e.get('tipo', '')} {e.get('singular', '')}")))


def bloques(cfg):
    """{id del ítem: bloque}; las compras extra de una posición ("14b: completar la barra") van con su posición."""
    out, por_pos = {}, {}
    for it in cfg["items"]:
        out[id(it)] = bloque_de(it, cfg)
        por_pos.setdefault(str(it.get("pos", "")), out[id(it)])
    for it in cfg["items"]:
        m = re.match(r"^(\d+)[a-z]$", str(it.get("pos", "")))
        if m and m.group(1) in por_pos and re.search(r"completar|sobrante|compra minima|tira|barra", norm(it.get("descripcion", ""))):
            out[id(it)] = por_pos[m.group(1)]
    return out


def bloque_de(it, cfg):
    """Bloque de la planilla base para un renglón de la cotización."""
    import atributos_plano
    import ficha_rubros
    d = norm(f"{it.get('descripcion', '')}")
    if it["grupo"] == "material":
        if re.search(r"aislac", d):
            return "Aislación"
        if re.search(r"tracing|traceado", d):
            return "Tracing eléctrico"
        if re.search(r"\bcable|bandeja portacable|conduit|prensacable|caja de paso|luminaria|instalacion electrica", d):
            return "Instalación eléctrica"
        if re.search(r"escalera|plataforma|baranda|rejilla|guarda ?hombre|pasarela", d):
            return "Plataforma / escaleras"
        if re.search(INSTRUMENTOS, d):
            return "Instrumental"
        if re.match(r"valv", d):
            return "Válvulas manuales"
        g = atributos_plano.grupo_de(it)
        if g == 0:
            return "Válvulas manuales"
        if g in (1, 2, 6):
            return "Piping"
        if g == 5:
            return "Instrumental"
        if g == 3:
            return "Skid"
        if es_recipiente(cfg) and g in (4, 7) and not re.search(r"\bskid\b|soporte|pollera|patas", d):
            return "Recipiente"
        if g == 4 or re.search(r"\bskid\b|soporte|estructura|bastidor|pollera|patas", d):
            return "Skid"
        return "Otros materiales"
    t = norm(f"{it.get('descripcion', '')} {it['fuentes'][0].get('proveedor', '')}")
    if re.search(r"caucion|seguro", t):
        return "Seguro de Caución"
    if re.search(r"embalaje", t):
        return "Embalaje"
    if re.search(r"galvaniz", t):
        return "Granallado y pintura"
    if re.search(r"rolado|cilindrado|plegado", t):
        return "Mano de obra de 3ros"
    if re.search(r"prueba de fugas|horas de planta", t):
        return "Mano de obra ITT"
    r = ficha_rubros.rubro_de(it)
    if r == "procedimientos" and re.search(r"radiograf|penetrant|\brx\b|\blp\b|ultrason", t):
        return "Ensayos no destructivos"
    if r in ("horas", "ph") or (it["grupo"] == "mo" and re.search(r"propi|\bitt\b", t)):
        return "Mano de obra ITT"
    if r == "pintura":
        return "Granallado y pintura"
    if r == "end":
        return "Ensayos no destructivos"
    if r == "transporte":
        return "Transporte a destino final"
    if r in ("mo_piping", "mo_estructura") or it["grupo"] == "mo":
        return "Mano de obra de 3ros"
    return "Otros servicios"


ETQ = {"diametro": "Ø", "diametro2": "Ø2", "serie": "serie", "schedule": "sch", "espesor_mm": "esp. mm", "material": "", "extremos": "",
       "cara": "", "norma": "", "marca": "marca", "modelo": "modelo", "rango": "rango", "trim": "trim", "paso": "paso", "costura": "",
       "revestimiento": "", "largo_mm": "largo mm", "medida": "", "designacion": "", "conexion": "conexión"}


def ampliada(it):
    """Descripción ampliada: los datos de la pieza (materiales) o la especificación (MO y servicios)."""
    at = it.get("atributos") or {}
    if it["grupo"] == "material" and at:
        return " · ".join(([at["tipo"]] if at.get("tipo") else []) + [f"{ETQ[k]} {at[k]}".strip() for k in ETQ if at.get(k)])
    return str(it.get("especificacion", ""))


def material_principal(cfg, b):
    """Material del renglón más caro de cada tipo de pieza (caños, accesorios, bridas, válvulas)."""
    import atributos_plano
    out = []
    for nombre, cond in (("Caños", lambda it: atributos_plano.grupo_de(it) == 2), ("Accesorios", lambda it: (it.get("atributos") or {}).get("familia") in ("ABW", "AFO")),
                         ("Bridas", lambda it: (it.get("atributos") or {}).get("familia") == "BRI"), ("Válvulas", lambda it: b[id(it)] == "Válvulas manuales"),
                         ("Recipiente", lambda it: b[id(it)] == "Recipiente")):
        its = sorted([it for it in cfg["items"] if it["grupo"] == "material" and cond(it) and (it.get("atributos") or {}).get("material")],
                     key=lambda it: -it["cantidad"] * it["fuentes"][0]["precio"])
        if its:
            out.append(f"{nombre} {its[0]['atributos']['material']}")
    return ", ".join(out)


def escribir(wb, cfg, mat, srv, CAT, fecha):
    """Agrega la hoja "Planilla ITT" como primera hoja del libro (las demás quedan atrás)."""
    import atributos_plano
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    p, eq = cfg["parametros"], cfg["equipo"]
    of = cfg.get("_oferta") or {}
    ws = wb.create_sheet("Planilla ITT", 0)
    T, M = Side(style="thin"), Side(style="medium")
    BT, BM = Border(left=T, right=T, top=T, bottom=T), Border(left=M, right=M, top=M, bottom=M)
    DUR, GRIS, GRIS2, AMA, NAR = (PatternFill("solid", fgColor=c) for c in ("FCD5B4", "BFBFBF", "D9D9D9", "FFFF00", "FFC000"))
    F = lambda **k: Font(name="Arial Narrow", **k)
    CONT = "_-* #,##0.00_-;\\-* #,##0.00_-;_-* \"-\"??_-;_-@_-"
    for col, w in zip("ABCDEFGHIJ", (43.5, 61.2, 13.7, 9, 16.8, 17.3, 13, 30, 16, 14)):
        ws.column_dimensions[col].width = w
    b = bloques(cfg)
    # ---- encabezado (filas 1–10)
    datos = dict(cfg.get("pedido", {}).get("datos_html", []) or [])
    cli = (cfg.get("cliente") or {}).get("nombre", "")
    enc = [("CLIENTE", cli), ("PEDIDO DE PRECIOS", (of.get("cliente") or {}).get("referencia") or cfg.get("pedido", {}).get("eyebrow", "")),
           ("REFERENCIA", (of.get("cliente") or {}).get("proyecto") or cfg.get("titulo", "")),
           ("PRESUPUESTO", f"{cfg['codigo']} {cfg.get('revision', '')} · {(of.get('oferta') or {}).get('numero', '')}".strip(" ·")),
           ("ÍTEM", (of.get("item") or {}).get("item", "")), ("NOMBRE", (of.get("item") or {}).get("descripcion") or cfg.get("titulo", "")),
           ("CANTIDAD", f"{p['N']} {eq['plural'] if p['N'] != 1 else eq['singular']}"),
           ("FECHA RECEPCION PED COTIZACION", cfg.get("fecha_recepcion", "")), ("FECHA DE VENCIMIENTO DE COTIZACION", cfg.get("fecha_vencimiento", "")),
           ("PLANO / ER", cfg.get("plano") or datos.get("Documento") or datos.get("Documentos", ""))]
    import re as _re
    for r, (k, v) in enumerate(enc, 1):
        a = ws.cell(r, 1, k); a.font = Font(name="Arial", size=10); a.alignment = Alignment(horizontal="center", vertical="center"); a.border = BT
        v = _re.sub(r"<[^>]+>", "", str(v or ""))
        if _re.match(r"^\d{4}-\d{2}-\d{2}$", v):
            v = fecha(v)
        c = ws.cell(r, 2, v); c.font = Font(name="Arial", size=12, bold=True); c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        if hasattr(v, "year"):
            c.number_format = "dd-mm-yyyy"
        ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=8)
        for j in range(2, 9):
            ws.cell(r, j).border = BT
        ws.row_dimensions[r].height = 22.5
    # ---- bloques (se escriben primero para conocer sus subtotales); empiezan debajo del alcance
    fila_mat = {id(it): i for i, it in enumerate(mat, 2)}
    fila_srv = {id(it): i for i, it in enumerate(srv, 2)}
    activos = [n for n in BLOQUES if any(b[id(it)] == n for it in cfg["items"])]
    n_res = 5 + (0 if p.get("FM") == p.get("FMO") else 1) + (1 if p.get("TRANS") else 0)
    r_tot = 15 + n_res
    r_plazo = r_tot + 5
    r_alc = r_plazo + 4
    r = r_alc + 1 + len(BLOQUES) + 5
    sub = {}
    EQV = {"igual": "Igual", "similar": "Similar", "sin_ref": "No encontrado"}
    for nombre in activos:
        its = [it for it in mat + srv if b[id(it)] == nombre]
        c = ws.cell(r, 1, nombre); c.font = Font(name="Arial", size=12, bold=True); c.fill = GRIS
        ws.cell(r, 2, "SI").font = Font(name="Arial", size=10)
        r += 1
        for j, t in enumerate(["Descripción", "Descripción ampliada", "Cantidad", "Unid", "USD/un", "Subt USD", "Posición", "Proveedor / antecedente",
                               "Equivalencia", "Fecha del precio"], 1):
            x = ws.cell(r, j, t); x.font = Font(name="Arial", size=10); x.fill = GRIS2 if j <= 7 else PatternFill("solid", fgColor="E8E1F3")
            x.alignment = Alignment(horizontal="center"); x.border = BT
        r += 1
        r0 = r
        for it in its:
            s = it["fuentes"][0]
            hoja, i = ("Materiales", fila_mat[id(it)]) if it["grupo"] == "material" else ("'MO y servicios'", fila_srv[id(it)])
            ped, ant = atributos_plano.fila_datos(it, CAT) if it["grupo"] == "material" else ([], ["", ""])
            eqv = "No encontrado" if not s["precio"] or s.get("coincide") == "sin_ref" else EQV.get(s.get("coincide"), "")
            vals = [it["descripcion"], ampliada(it), it["cantidad"], it["unidad"], f"={hoja}!O{i}", f"={hoja}!P{i}", it.get("pos", ""),
                    (ant[0] + " · " if ant[0] else "") + str(s.get("proveedor", "")), eqv, fecha(s["fecha"]) if s.get("fecha") else ""]
            for j, v in enumerate(vals, 1):
                x = ws.cell(r, j, v); x.border = BT; x.font = Font(name="Calibri", size=11)
                x.alignment = Alignment(wrap_text=j in (1, 2, 8), vertical="center", horizontal="center" if j in (3, 4, 7, 9, 10) else None)
            ws.cell(r, 5).number_format = ws.cell(r, 6).number_format = CONT
            ws.cell(r, 3).number_format = "#,##0" if float(it["cantidad"]).is_integer() else "#,##0.00##"
            ws.cell(r, 10).number_format = "dd-mm-yyyy"
            ws.cell(r, 9).fill = PatternFill("solid", fgColor={"Igual": "DDF1E4", "Similar": "FBEFD6"}.get(eqv, "F8E1DE"))
            r += 1
        x = ws.cell(r, 6, f"=SUM(F{r0}:F{r - 1})"); x.fill = AMA; x.font = Font(name="Calibri", size=11, bold=True); x.number_format = CONT; x.border = BT
        sub[nombre] = f"F{r}"
        r += 3
    ref = lambda n: sub.get(n, "0")
    # ---- cuadro de rentabilidad (filas 12 en adelante)
    for col, (t1, t2) in enumerate([("Detalle", ""), ("Cantidad", "Unidad"), ("Costo Unitario", "U$S"), ("Factor de Rentabilidad", ""),
                                    ("Precio de Venta Unitario", "U$S"), ("Precio de Venta unitario", "U$S"), ("Margen de ganancia", "%"),
                                    ("Precio de venta total", "U$S")], 1):
        for rr, t in ((12, t1), (13, t2)):
            x = ws.cell(rr, col, t); x.fill = DUR; x.border = BT
            x.font = F(size=16 if col == 1 else 11, bold=col == 1); x.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.merge_cells("A12:A13"); ws.row_dimensions[12].height = 42
    C = "'Cotización'!"
    resto = f"({C}B21+{C}B22-{ref('Mano de obra de 3ros')}-{ref('Seguro de Caución')}-{ref('Transporte a destino final')})"
    if p.get("FM") == p.get("FMO"):
        filas = [("Materiales, MO y SVC", f"={C}B5", f"={C}B18+{C}B19+{resto}", f"={C}B6")]
    else:
        filas = [("Materiales (con contingencia)", f"={C}B5", f"={C}B18+{C}B19", f"={C}B6"), ("MO ITT y servicios", f"={C}B5", f"={resto}", f"={C}B7")]
    filas += [("Válvulas Taval", f"={C}B5", f"={C}B20", f"={C}B14"), ("Mano de obra de terceros", f"={C}B5", f"={ref('Mano de obra de 3ros')}", f"={C}B7"),
              ("Seguro de caución", f"={C}B5", f"={ref('Seguro de Caución')}", f"={C}B7"), ("Transporte", f"={C}B5", f"={ref('Transporte a destino final')}", f"={C}B7")]
    if p.get("TRANS"):
        filas.append(("Flete y embalaje (por envío)", 1, f"={C}E23", 1))
    for k, (n, cant, costo, fac) in enumerate(filas, 15):
        vals = [n, cant, costo, fac, f"=C{k}*D{k}", f"=E{k}", f"=IFERROR((E{k}-C{k})/E{k},0)", f"=F{k}*B{k}"]
        for j, v in enumerate(vals, 1):
            x = ws.cell(k, j, v); x.border = BT; x.font = F(size=11)
            x.number_format = {2: "0", 3: "#,##0.00", 4: "0.00", 5: CONT, 6: CONT, 7: "0.0%", 8: "#,##0.00"}.get(j, "General")
            x.alignment = Alignment(horizontal="right" if j == 1 else "center" if j in (2, 4) else "right")
        ws.cell(k, 4).fill = AMA
    k_ult = 14 + len(filas)
    unit = [k for k in range(15, k_ult + 1) if not (p.get("TRANS") and k == k_ult)]
    r_tot = k_ult + 1
    ws.cell(r_tot, 2, "Total").font = F(size=11, bold=True)
    ws.cell(r_tot, 3, "=" + "+".join(f"C{k}" for k in unit)).number_format = "#,##0.00"
    ws.cell(r_tot, 6, "=" + "+".join(f"F{k}" for k in unit)).number_format = CONT
    ws.cell(r_tot, 8, f"=SUM(H15:H{k_ult})").number_format = "#,##0.00"
    for j in range(1, 9):
        ws.cell(r_tot, j).border = BT
    for j in (3, 6, 8):
        ws.cell(r_tot, j).font = F(size=11, bold=True); ws.cell(r_tot, j).fill = AMA if j != 3 else PatternFill("solid", fgColor="DDEBF7")
    ws.cell(r_tot + 1, 7, f"=IFERROR((F{r_tot}-C{r_tot})/F{r_tot},0)").number_format = "0.0%"
    rt = r_tot + 2
    ws.merge_cells(start_row=rt, start_column=6, end_row=rt, end_column=7)
    x = ws.cell(rt, 6, "Total U$D"); x.font = F(size=18, bold=True); x.fill = AMA; x.alignment = Alignment(horizontal="center"); x.border = BM
    x = ws.cell(rt, 8, f"={C}E28"); x.font = F(size=18, bold=True); x.fill = AMA; x.number_format = "#,##0.00"; x.alignment = Alignment(horizontal="center"); x.border = BM
    ws.cell(rt + 1, 6, "Precio unitario de la oferta (redondeado):").font = F(size=10, italic=True)
    x = ws.cell(rt + 1, 8, f"={C}D27"); x.number_format = "#,##0.00"; x.font = F(size=10, italic=True)
    # ---- plazo y entrega
    rp = rt + 3
    pz = cfg.get("plazo") or {}
    entrega = (cfg.get("flete") or {}).get("etiqueta") if p.get("TRANS") else "EXW, ITT SA, Av. 12 de Octubre 4004, Quilmes Oeste, AMBA."
    for rr, t in ((rp, f"Plazo de entrega : {pz.get('dias', '')} días {pz.get('texto', '')}".strip()), (rp + 1, f"Entrega: {entrega}")):
        ws.merge_cells(start_row=rr, start_column=1, end_row=rr, end_column=8)
        x = ws.cell(rr, 1, t); x.font = F(size=14, bold=True); x.fill = DUR; x.alignment = Alignment(horizontal="left", vertical="center")
        ws.row_dimensions[rr].height = 22.5
    # ---- alcance SI/NO
    ra = rp + 4
    x = ws.cell(ra, 1, "MATERIA PRIMA Y MATERIALES"); x.font = Font(name="Arial", size=12, bold=True); x.fill = GRIS
    for k, n in enumerate(BLOQUES, ra + 1):
        si = n in activos
        ws.cell(k, 1, n).font = Font(name="Arial", size=12); ws.cell(k, 1).alignment = Alignment(horizontal="center")
        x = ws.cell(k, 2, "SI" if si else "NO"); x.font = Font(name="Arial", size=10)
        if si:
            for j in (2, 3, 4):
                ws.cell(k, j).fill = DUR
            ws.cell(k, 3, f"={ref(n)}").number_format = CONT
        if n == "Mano de obra ITT":
            ws.cell(k, 5, "Ingeniería - Calidad - Movimientos internos, PH, armado final").font = Font(name="Arial", size=9)
    rm = ra + len(BLOQUES) + 2
    end = "; ".join(it["descripcion"] for it in srv if b[id(it)] == "Ensayos no destructivos")
    for rr, (k, v) in enumerate((("Material principal:", material_principal(cfg, b)), ("END", end or "Sin ensayos no destructivos")), rm):
        ws.cell(rr, 1, k).font = Font(name="Calibri", size=14)
        x = ws.cell(rr, 2, v); x.font = Font(name="Calibri", size=14, color="FF0000")
    ws.page_setup.orientation = "landscape"; ws.page_setup.fitToWidth = 1; ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    return ws
