"""Arma todos los entregables de una cotización a partir de su cotizacion.json.

Uso: python herramientas/armar_cotizacion.py cotizaciones/<carpeta>

Entrada (en la carpeta):
  cotizacion.json                      datos de la cotización: ítems con todas sus fuentes de precio,
                                       parámetros, textos del informe (ver cotizaciones/_plantilla/)
  pedido/lista_materiales_plano.csv    tabla de materiales del plano, renglón por renglón
  oferta.json                          (opcional) textos de la oferta técnica y económica

Salida:
  computo.csv            cómputo con la fuente de base de cada ítem (lo usa verificar_computo.py)
  controles_tablas.md    kilos y m², plazos de material por rubro y marcas del cliente (controles_tablas.py)
  <codigo>_<...>.xlsx    planilla con fórmulas: parámetros, ajuste por inflación, detalle, índices, desvíos, antecedentes
  informe.html           informe interactivo (plantillas/informe_cotizacion.html)
  compras/               lista de materiales y servicios para Compras (si cotizacion.json tiene "compras")
  oferta/                ofertas técnica y económica en Word y PDF (si hay oferta.json)

Controles (procedimiento P7 y P9): recalcula el precio en Python y lo compara con la planilla recalculada
con LibreOffice; corre verificar_computo.py. Si algo no coincide, termina con error.
"""
import base64
import csv
import hashlib
import html
import json
import re
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

RAIZ = Path(__file__).resolve().parent.parent
INDICES = RAIZ / "conocimiento" / "costos" / "indices_ajuste.csv"
PLANTILLA_INFORME = RAIZ / "plantillas" / "informe_cotizacion.html"
TIPOS = {"cot": "cotización", "lista": "lista", "stock": "stock", "ant": "antecedente", "est": "estimado"}
MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]


def sin_html(t):
    return html.unescape(re.sub(r"<[^>]+>", "", str(t)))


def leer_indices():
    return [(r["mes"][:7], float(r["indice_local_usd"]), float(r["cpi_eeuu"]))
            for r in csv.DictReader(open(INDICES, encoding="utf-8"))]


def fecha(t):
    p = [int(x) for x in str(t).split("-")]
    return date(p[0], p[1] if len(p) > 1 else 7, p[2] if len(p) > 2 else 1)  # solo año: mitad de año


# ---------------------------------------------------------------- cálculo (espejo de la planilla y el informe)
def factor(item, idx, fref, aplicar):
    if not aplicar:
        return 1.0
    col = 1 if item["grupo"] != "material" else 2
    mes = max(min(item["fuentes"][0]["fecha"][:7], fref), idx[0][0])

    def en(m):
        v = idx[0]
        for r in idx:
            if r[0] <= m:
                v = r
        return v[col]
    return en(fref) / en(mes)


def calcular(cfg, idx):
    p = cfg["parametros"]
    fref = p["fecha_referencia"][:7]
    sub = {"material": 0.0, "mo": 0.0, "servicio": 0.0}
    for it in cfg["items"]:
        sub[it["grupo"]] += it["cantidad"] * it["fuentes"][0]["precio"] * factor(it, idx, fref, p["AJ"])
    cont = sub["material"] * p["CONT"] / 100
    costo = sub["material"] + cont + sub["mo"] + sub["servicio"]
    precio = round((sub["material"] + cont) * p["FM"] + (sub["mo"] + sub["servicio"]) * p["FMO"], 2)
    flete = (p["TR_ARS"] / p["TC"] + p["TR_EMB"]) * p["TR_F"] if p["TRANS"] else 0
    return {"costo": costo, "precio_unitario": precio, "total": round(precio * p["N"] + flete, 2)}


# ---------------------------------------------------------------- cómputo
def escribir_computo(cfg, carpeta):
    with open(carpeta / "computo.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "pos", "descripcion", "cant_por_puente", "unidad", "precio_unit_usd", "subtotal_usd",
                    "tipo_origen", "proveedor_o_criterio", "carpeta_origen", "fecha_precio", "coincidencia", "diferencia"])
        for it in cfg["items"]:
            s = it["fuentes"][0]
            w.writerow([it["id"], it["pos"], it["descripcion"], f"{it['cantidad']:g}", it["unidad"], f"{s['precio']:g}",
                        f"{it['cantidad'] * s['precio']:.2f}", TIPOS[s["tipo"]], s["proveedor"], s["origen"], s["fecha"],
                        s.get("coincide", ""), s.get("diferencia", "")])


# ---------------------------------------------------------------- planilla
def escribir_planilla(cfg, carpeta, idx_rows):
    H = Font(bold=True, color="FFFFFF"); HF = PatternFill("solid", fgColor="1D5F86")
    INP = PatternFill("solid", fgColor="FBEFD6"); TOT = PatternFill("solid", fgColor="E8EDF0")
    B = Border(bottom=Side(style="thin", color="C9D3D9")); USD = "#,##0.00"; GRIS = Font(italic=True, color="5D6B75")
    TF = {"cot": "DDF1E4", "lista": "DCEBF4", "stock": "DCEBF4", "ant": "FBEFD6", "est": "F8E1DE"}
    p, eq = cfg["parametros"], cfg["equipo"]
    mat = [i for i in cfg["items"] if i["grupo"] == "material"]
    srv = [i for i in cfg["items"] if i["grupo"] != "material"]
    nm, ns, ni = len(mat) + 1, len(srv) + 1, len(idx_rows) + 1
    RNG = f"Índices!$A$2:$E${ni}"

    def head(ws, cols, widths):
        for i, (c, wd) in enumerate(zip(cols, widths), 1):
            x = ws.cell(1, i, c); x.font = H; x.fill = HF; x.alignment = Alignment(wrap_text=True, vertical="center")
            ws.column_dimensions[chr(64 + i)].width = wd
        ws.freeze_panes = "A2"

    wb = Workbook(); ws = wb.active; ws.title = "Cotización"
    ws["A1"] = f"{cfg['codigo']} {cfg['revision']} · {cfg['titulo']}"; ws["A1"].font = Font(bold=True, size=14)
    ws["A2"] = f"{cfg['subtitulo_planilla']} · {cfg['estado']} {cfg['fecha']}"; ws["A2"].font = GRIS
    ws["A4"] = "PARÁMETROS (celdas amarillas editables)"; ws["A4"].font = Font(bold=True)
    params = [(f"Cantidad de {eq['plural']}", p["N"], "0"), ("Factor de materiales (materiales y contingencia)", p["FM"], "0.00"),
              ("Factor de mano de obra y servicios", p["FMO"], "0.00"), ("Contingencia materiales", p["CONT"] / 100, "0%"),
              ("Incluir flete (1 = sí, 0 = no)", p["TRANS"], "0"), ("Tipo de cambio ARS/USD (cargar BNA del día)", p["TC"], "#,##0"),
              ("Flete ARS por envío", p["TR_ARS"], "#,##0"), ("Embalaje USD por envío (estimado)", p["TR_EMB"], USD), ("Factor flete", p["TR_F"], "0.00")]
    for r, (n, v, f) in enumerate(params, 5):
        ws.cell(r, 1, n); c = ws.cell(r, 2, v); c.fill = INP; c.number_format = f
    # ajuste por inflación
    ws["G5"] = "AJUSTE POR INFLACIÓN (desde la fecha de cada precio hasta hoy)"; ws["G5"].font = Font(bold=True)
    for r, (n, v, f) in enumerate([("Aplicar ajuste (1 = sí, 0 = no)", p["AJ"], "0"),
                                   ("Fecha de hoy (referencia)", fecha(p["fecha_referencia"]), "dd/mm/yyyy")], 6):
        ws.cell(r, 7, n); c = ws.cell(r, 8, v); c.fill = INP; c.number_format = f
    ws["G8"] = "Variación 12 meses — materiales (CPI EE.UU.)"; ws["H8"] = f"=VLOOKUP(H7,{RNG},5,1)/VLOOKUP(EDATE(H7,-12),{RNG},5,1)-1"
    ws["G9"] = "Variación 12 meses — MO y servicios (costo local en USD)"; ws["H9"] = f"=VLOOKUP(H7,{RNG},4,1)/VLOOKUP(EDATE(H7,-12),{RNG},4,1)-1"
    ws["H8"].number_format = ws["H9"].number_format = "0.0%"
    for r, t in enumerate(["Factor de cada fila = índice del mes de hoy / índice del mes del precio (hoja Índices).",
                           "Materiales: CPI de EE.UU. (los precios ya están en dólares).",
                           "MO y servicios: costo local en dólares = IPC INDEC / dólar BNA vendedor.",
                           "Fuentes y meses interpolados o estimados: hoja Índices (conocimiento/costos/indices_ajuste.csv)."], 10):
        ws.cell(r, 7, t).font = Font(italic=True, color="5D6B75", size=9)
    ws.column_dimensions["G"].width = 58; ws.column_dimensions["H"].width = 13
    # resumen
    ws["A16"] = "RESUMEN"; ws["A16"].font = Font(bold=True)
    for j, t in enumerate(["Rubro", f"Costo / {eq['singular']}", "Factor", f"Precio / {eq['singular']}", "Total"], 1):
        c = ws.cell(17, j, t); c.font = H; c.fill = HF
    S = "'MO y servicios'"
    filas = [("Materiales (con ajuste por inflación)", f"=SUM(Materiales!P2:P{nm})", "=$B$6"),
             ("Contingencia", "=B18*$B$8", "=$B$6"),
             ("Mano de obra", f'=SUMIF({S}!B2:B{ns},"MO",{S}!P2:P{ns})', "=$B$7"),
             ("Servicios e insumos", f'=SUMIF({S}!B2:B{ns},"Servicio",{S}!P2:P{ns})', "=$B$7")]
    for r, (n, f, fa) in enumerate(filas, 18):
        ws.cell(r, 1, n); ws.cell(r, 2, f).number_format = USD; ws.cell(r, 3, fa).number_format = "0.00"
        ws.cell(r, 4, f"=B{r}*C{r}").number_format = USD; ws.cell(r, 5, f"=D{r}*$B$5").number_format = USD
    ws["A22"] = "Flete + embalaje (por envío)"; ws["C22"] = "=$B$13"; ws["E22"] = "=IF($B$9=1,($B$11/$B$10+$B$12)*$B$13,0)"
    ws["C22"].number_format = "0.00"; ws["E22"].number_format = USD
    ws["A23"] = "TOTAL SIN IVA"; ws["B23"] = "=SUM(B18:B21)"; ws["C23"] = "=D23/B23"; ws["D23"] = "=SUM(D18:D21)"; ws["E23"] = "=SUM(E18:E22)"
    ws["A24"] = "IVA 21%"; ws["E24"] = "=E23*0.21"; ws["A25"] = "TOTAL CON IVA"; ws["E25"] = "=E23+E24"
    ws["A26"] = "Margen sobre precio"; ws["D26"] = "=1-B23/D23"; ws["D26"].number_format = "0.0%"
    for r in range(23, 26):
        for c in range(1, 6):
            x = ws.cell(r, c); x.fill = TOT; x.font = Font(bold=True)
            if c in (2, 4, 5):
                x.number_format = USD
    ws["C23"].number_format = "0.00"
    ws["A27"] = "PRECIO UNITARIO DE VENTA (redondeado, va a la oferta)"; ws["D27"] = "=ROUND(D23,2)"
    ws["A28"] = "TOTAL DE LA OFERTA SIN IVA (unitario redondeado × cantidad + flete)"; ws["E28"] = "=D27*B5+E22"
    for c in ("A27", "D27", "A28", "E28"):
        ws[c].font = Font(bold=True, color="1D5F86")
    ws["D27"].number_format = ws["E28"].number_format = USD
    ws["A29"] = f"Costo / {eq['singular']} SIN ajuste por inflación"; ws["B29"] = f"=SUM(Materiales!G2:G{nm})*(1+B8)+SUM({S}!G2:G{ns})"
    ws["A30"] = "Ajuste por inflación incluido en el costo"; ws["B30"] = "=B23-B29"; ws["C30"] = "=B30/B29"
    ws["B29"].number_format = ws["B30"].number_format = USD; ws["C30"].number_format = "+0.0%"
    for k, t in enumerate(cfg.get("planilla_notas", []), 32):
        ws.cell(k, 1, t)
    ws.column_dimensions["A"].width = 52
    for c in "BCDE":
        ws.column_dimensions[c].width = 16

    def detalle(nombre, items, es_srv):
        w = wb.create_sheet(nombre)
        head(w, ["Pos", "Grupo" if es_srv else "ID", "Descripción", f"Cant. / {eq['singular']}", "Unidad",
                 "USD unit. (a la fecha del precio)", "Subtotal USD (sin ajuste)", "Tipo de origen", "Proveedor o criterio",
                 "Carpeta de origen", "Fecha del precio", "ID", "Meses hasta hoy",
                 "Factor inflación (" + ("costo local USD" if es_srv else "CPI EE.UU.") + ")", "USD unit. ajustado", "Subtotal USD ajustado",
                 "Coincidencia con el plano", "Diferencia con lo pedido"],
             [6, 10, 44, 10, 8, 13, 13, 13, 48, 26, 12, 6, 9, 10, 12, 13, 13, 50])
        col = 4 if es_srv else 5
        for i, it in enumerate(items, 2):
            s = it["fuentes"][0]
            g = ("MO" if it["grupo"] == "mo" else "Servicio") if es_srv else it["id"]
            vals = [it["pos"], g, it["descripcion"], it["cantidad"], it["unidad"], s["precio"], f"=D{i}*F{i}", TIPOS[s["tipo"]],
                    s["proveedor"], s["origen"], fecha(s["fecha"]), it["id"], f"=MAX(0,(Cotización!$H$7-K{i})/30.4375)",
                    f"=IF(Cotización!$H$6=1,VLOOKUP(Cotización!$H$7,{RNG},{col},1)/VLOOKUP(MAX(K{i},Índices!$A$2),{RNG},{col},1),1)",
                    f"=F{i}*N{i}", f"=D{i}*O{i}", {"igual": "Igual", "similar": "Similar", "sin_ref": "Sin referencia"}.get(s.get("coincide"), ""),
                    s.get("diferencia", "")]
            for j, v in enumerate(vals, 1):
                c = w.cell(i, j, v); c.border = B
                if j in (4, 6):
                    c.fill = INP
                if j in (6, 7, 15, 16):
                    c.number_format = USD
                c.number_format = {11: "dd/mm/yyyy", 13: "0.0", 14: "0.000"}.get(j, c.number_format)
            w.cell(i, 8).fill = PatternFill("solid", fgColor=TF[s["tipo"]])
            w.cell(i, 17).fill = PatternFill("solid", fgColor={"igual": "DDF1E4", "similar": "FBEFD6", "sin_ref": "F8E1DE"}.get(s.get("coincide"), "FFFFFF"))
            w.cell(i, 18).alignment = Alignment(wrap_text=True, vertical="top")
        n = len(items) + 2
        w.cell(n, 3, f"Subtotal por {eq['singular']}").font = Font(bold=True)
        for col_, letra in ((7, "G"), (16, "P")):
            c = w.cell(n, col_, f"=SUM({letra}2:{letra}{n - 1})"); c.font = Font(bold=True); c.number_format = USD
        for j in range(1, 19):
            w.cell(n, j).fill = TOT
        w.auto_filter.ref = f"A1:R{n - 1}"
        k = n + 2
        for it in items:
            for a in it["fuentes"][1:]:
                w.cell(k, 3, f"Alternativa pos {it['pos']}: USD {a['precio']:g} · {a['proveedor']} · {a['origen']} · {a['fecha']} ({TIPOS[a['tipo']]})").font = GRIS
                k += 1
        return w

    detalle("Materiales", mat, False)
    w = detalle("MO y servicios", srv, True)
    if cfg.get("nota_mo_html"):
        w.cell(w.max_row + 2, 3, sin_html(cfg["nota_mo_html"])).font = GRIS
    # índices
    x = wb.create_sheet("Índices")
    head(x, ["Mes", "IPC Argentina (oct-24=100)", "Dólar BNA vendedor", "Costo local en USD (IPC/dólar, oct-24=100)",
             "CPI EE.UU. (oct-24=100)", "Origen IPC", "Origen dólar", "Origen CPI"], [11, 13, 12, 16, 12, 40, 40, 40])
    for i, r in enumerate(idx_rows, 2):
        y, m, _ = map(int, r["mes"].split("-"))
        for j, v in enumerate([date(y, m, 1), float(r["ipc_argentina"]), float(r["dolar_bna"]), float(r["indice_local_usd"]),
                               float(r["cpi_eeuu"]), r["origen_ipc"], r["origen_dolar"], r["origen_cpi"]], 1):
            c = x.cell(i, j, v); c.border = B
            c.number_format = {1: "mm/yyyy", 2: "0.00", 3: "#,##0.00", 4: "0.00", 5: "0.00"}.get(j, "General")
            if j >= 6 and str(v).startswith("dato"):
                c.font = Font(color="2C7A4B")
            if j >= 6 and ("ESTIMADO" in str(v) or "APROXIMADO" in str(v)):
                c.font = Font(color="A3392F")
    x.cell(ni + 2, 1, "Generado con herramientas/indices_inflacion.py. Verde: dato publicado. Rojo: estimado o aproximado. El resto, interpolado.").font = GRIS
    # desvíos y antecedentes
    d = wb.create_sheet("Desvíos"); head(d, ["Pos", "Desvío", "Detalle"], [16, 50, 80])
    for i, dv in enumerate(cfg.get("desvios", []), 2):
        for j, v in enumerate([dv["tag"], dv["titulo"], dv["texto"]], 1):
            c = d.cell(i, j, sin_html(v)); c.alignment = Alignment(wrap_text=True, vertical="top"); c.border = B
    a = wb.create_sheet("Antecedentes"); head(a, ["Carpeta / oferta", "Fecha", "Qué es", "Precio c/u USD", "Qué se tomó"], [34, 12, 52, 14, 60])
    for i, an in enumerate(cfg.get("antecedentes", []), 2):
        for j, v in enumerate([an["carpeta_html"], an["fecha"], an["que"], an["precio"], an["tomado_html"]], 1):
            c = a.cell(i, j, sin_html(v)); c.alignment = Alignment(wrap_text=True, vertical="top"); c.border = B
    ruta = carpeta / f"{cfg['codigo']}_{cfg['archivo_planilla']}.xlsx"
    wb.save(ruta)
    return ruta


def leer_planilla(ruta):
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["soffice", "--headless", "--convert-to", "xlsx", "--outdir", tmp, str(ruta)], check=True, capture_output=True)
        ws = load_workbook(Path(tmp) / ruta.name, data_only=True)["Cotización"]
        return {"costo": ws["B23"].value, "precio_unitario": ws["D27"].value, "total": ws["E28"].value}


# ---------------------------------------------------------------- informe
def escribir_informe(cfg, carpeta, idx, adjuntos):
    p, eq, e = cfg["parametros"], cfg["equipo"], html.escape
    fref = p["fecha_referencia"][:7]
    y, m = map(int, fref.split("-"))
    fref_txt = f"{MESES[m - 1]}-{y}"

    def var12(col):
        d = {r[0]: r[col] for r in idx}
        prev = f"{y - 1}-{m:02d}"
        return (d[fref] / d[prev] - 1) * 100 if prev in d else None

    def js(it):
        o = {"id": it["id"], "pos": it["pos"], "d": it["descripcion"], "sp": it["especificacion"], "cant": it["cantidad"], "un": it["unidad"],
             "src": [{"tipo": s["tipo"], "precio": s["precio"], "who": s["proveedor"], "from": s["origen"], "fecha": s["fecha"],
                     "co": s.get("coincide", ""), "dif": s.get("diferencia", "")} for s in it["fuentes"]]}
        if it["grupo"] != "material":
            o["grp"] = "mo" if it["grupo"] == "mo" else "serv"
        return o
    mat = [js(i) for i in cfg["items"] if i["grupo"] == "material"]
    srv = [js(i) for i in cfg["items"] if i["grupo"] != "material"]
    huella = hashlib.sha1(json.dumps(cfg["items"], sort_keys=True).encode()).hexdigest()[:8]
    estado = {"borrador": "Borrador · sin revisar · no enviar", "revisado": "Revisado · falta aprobación · no enviar",
              "aprobado": "Aprobado", "enviado": "Enviado"}.get(cfg["estado"], cfg["estado"])
    header = (f'<header class="cab">\n  <div style="display:flex;flex-direction:column;gap:8px;min-width:0">\n'
              f'    <span class="eyebrow">ITT S.A. · Informe de cotización · {e(cfg["codigo"])} {e(cfg["revision"])}</span>\n'
              f'    <h1>{e(cfg["titulo"])}</h1>\n    <div class="meta">' + "".join(f"<span>{e(x)}</span>" for x in cfg["meta"]) +
              f'</div>\n  </div>\n  <span class="estado">{e(estado)}</span>\n</header>')
    hist = ""
    if cfg.get("historial_html"):
        hist = ('<div class="aviso">\n  <h3>Historial de correcciones</h3>\n  <ul class="small">\n' +
                "\n".join(f"    <li>{x}</li>" for x in cfg["historial_html"]) + "\n  </ul>\n</div>")
    ped = cfg["pedido"]
    pedido = (f'<section>\n  <div class="sec-head"><h2>Pedido</h2><span class="eyebrow">{e(ped["eyebrow"])}</span></div>\n  <div class="dos">\n'
              '    <div class="bloque">\n      <dl class="kv">\n' + "\n".join(f"        <dt>{k}</dt><dd>{v}</dd>" for k, v in ped["datos_html"]) +
              '\n      </dl>\n    </div>\n    <div class="bloque">\n      <h3>Requisitos técnicos del pedido</h3>\n      <ul class="lista small">\n' +
              "\n".join(f"        <li>{x}</li>" for x in ped["requisitos_html"]) + "\n      </ul>\n    </div>\n  </div>\n</section>")
    pct = lambda v: f"{v:.1f}%".replace(".", ",")
    vm, vl = var12(2), var12(1)
    ajuste = (f'<section>\n  <div class="sec-head"><h2>Ajuste por inflación</h2><span class="eyebrow">desde la fecha de cada precio hasta {fref_txt}</span></div>\n'
              '  <div class="bloque small">\n    <p>Cada precio se lleva a hoy con un índice mensual, según el mes de su fecha: '
              f'<b>factor = índice de {fref_txt} / índice del mes del precio</b>. Los precios estimados o editados hoy no se ajustan. '
              'Los índices están en <span class="mono">conocimiento/costos/indices_ajuste.csv</span> (hoja Índices de la planilla).</p>\n    <ul class="lista">\n'
              f'      <li><b>Materiales:</b> CPI de EE.UU., porque los precios ya están en dólares. Últimos 12 meses: {pct(vm)}.</li>\n'
              f'      <li><b>Mano de obra y servicios:</b> costo local medido en dólares = IPC del INDEC ÷ dólar BNA vendedor. Últimos 12 meses: <b>{pct(vl)}</b>. '
              'Puede subir o bajar según cuánto suba el dólar frente a la inflación; por eso se usa un índice mensual y no una tasa fija.</li>\n'
              '      <li>Hay meses interpolados entre datos publicados y el último mes puede estar estimado (ver la hoja Índices).</li>\n    </ul>\n  </div>\n</section>')
    desv = "\n".join(f'    <div class="desvio"><span class="tag">{d["tag"]}</span><b>{d["titulo"]}</b><span class="small muted">{d["texto"]}</span></div>'
                     for d in cfg.get("desvios", []))
    ante = "\n".join(f'      <tr><td>{a["carpeta_html"]}</td><td class="mono">{e(a["fecha"])}</td><td>{a["que"]}</td><td class="n">{a["precio"]}</td><td>{a["tomado_html"]}</td></tr>'
                     for a in cfg.get("antecedentes", []))
    pend = "\n".join(f'    <div class="bloque"><h3>{e(b["titulo"])}</h3><ol class="lista small">\n' + "\n".join(f"      <li>{x}</li>" for x in b["items"]) + "\n    </ol></div>"
                     for b in cfg.get("pendientes", []))
    dias = cfg["plazo"]["dias"]
    ticks = "".join(f"<span>{round(dias * k / 4)}</span>" for k in range(5))
    params = {k: v for k, v in p.items() if k != "fecha_referencia"}
    rep = {"TITULO_PAGINA": e(cfg["titulo_pagina"]), "HEADER": header, "HISTORIAL": hist, "PEDIDO": pedido, "AJUSTE": ajuste,
           "EQ": e(eq["singular"]), "EQS": e(eq["plural"]), "N": str(p["N"]), "PLAZO_DIAS": str(dias), "PLAZO_TEXTO": e(cfg["plazo"]["texto"]),
           "PLAZO_NOTA": cfg["plazo"]["nota"], "TAREAS_JSON": json.dumps(cfg["plazo"]["tareas"], ensure_ascii=False), "TICKS": ticks,
           "FREF": fref, "FREF_TXT": fref_txt, "FLETE_ETIQUETA": e(cfg["flete"]["etiqueta"]), "FLETE_REF": cfg["flete"]["referencia_html"],
           "FLETE_CRITERIO": cfg["flete"]["criterio_html"], "N_POS": str(len({i["pos"] for i in cfg["items"] if i["grupo"] == "material" and i["pos"].isdigit()})),
           "NOTA_MO": cfg.get("nota_mo_html", ""), "DESVIOS": desv, "ANTECEDENTES": ante, "PENDIENTES": pend, "PIE": cfg.get("pie", ""),
           "IDX_JSON": json.dumps([list(r) for r in idx]), "PARAMS_JSON": json.dumps(params), "MAT_JSON": json.dumps(mat, ensure_ascii=False),
           "SERV_JSON": json.dumps(srv, ensure_ascii=False), "XLSX_PRES": f"{cfg['codigo']}_{cfg['archivo_planilla']}.xlsx",
           "XLSX_COMPRAS": f"{cfg['codigo']}_pedido_materiales_compras.xlsx", "XLSX_JSON": json.dumps(adjuntos), "KEY": f"{cfg['codigo'].lower()}:{huella}", "CODIGO": cfg["codigo"]}
    t = PLANTILLA_INFORME.read_text(encoding="utf-8")
    for k, v in rep.items():
        t = t.replace("{{" + k + "}}", v)
    faltan = re.findall(r"\{\{[A-Z_]+\}\}", t)
    if faltan:
        sys.exit(f"Quedaron marcadores sin completar en el informe: {faltan}")
    (carpeta / "informe.html").write_text(t, encoding="utf-8")


# ---------------------------------------------------------------- principal
def main(carpeta):
    carpeta = Path(carpeta)
    cfg = json.load(open(carpeta / "cotizacion.json", encoding="utf-8"))
    faltan = [it["id"] for it in cfg["items"] if it["fuentes"][0].get("coincide") not in ("igual", "similar", "sin_ref")
              or (it["fuentes"][0].get("coincide") == "similar" and not it["fuentes"][0].get("diferencia"))]
    if faltan:
        sys.exit(f"ERROR: falta indicar si el precio de base es de una pieza igual o similar a la del plano (y en qué difiere): {faltan}")
    idx_rows = list(csv.DictReader(open(INDICES, encoding="utf-8")))
    idx = leer_indices()
    escribir_computo(cfg, carpeta)
    ruta = escribir_planilla(cfg, carpeta, idx_rows)
    sys.path.insert(0, str(RAIZ / "herramientas"))
    adjuntos = {ruta.name: base64.b64encode(ruta.read_bytes()).decode()}
    if cfg.get("compras"):
        import lista_compras
        rc = lista_compras.main(carpeta)
        adjuntos[rc.name] = base64.b64encode(rc.read_bytes()).decode()
    escribir_informe(cfg, carpeta, idx, adjuntos)  # el informe lleva los dos Excel embebidos para descargarlos
    py, xl = calcular(cfg, idx), leer_planilla(ruta)
    print(f"Python : costo {py['costo']:,.2f} · precio unitario {py['precio_unitario']:,.2f} · total {py['total']:,.2f}")
    print(f"Planilla: costo {xl['costo']:,.2f} · precio unitario {xl['precio_unitario']:,.2f} · total {xl['total']:,.2f}")
    if any(abs(py[k] - xl[k]) > 0.011 for k in py):
        sys.exit("ERROR: el cálculo en Python y la planilla no coinciden. Revisar antes de seguir.")
    import verificar_computo
    if verificar_computo.main(carpeta) != 0:
        sys.exit("ERROR: verificar_computo.py encontró errores.")
    import controles_tablas
    controles_tablas.main(carpeta)  # kilos y m², plazos de material y marcas del cliente → controles_tablas.md
    if (carpeta / "oferta.json").exists():
        import generar_oferta
        generar_oferta.main(carpeta)
    import indice_proyectos
    indice_proyectos.main()  # la cotización queda en el índice de antecedentes
    print(f"\nListo: {carpeta}/computo.csv, {ruta.name}, informe.html" + (", oferta/" if (carpeta / "oferta.json").exists() else ""))
    print(f"Estado: {cfg['estado']}. Recordar: revisión independiente y aprobación antes de enviar (procedimiento P9).")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
