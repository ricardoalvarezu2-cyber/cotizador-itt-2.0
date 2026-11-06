"""Planilla Excel de la cotización (rediseño del 05-11-2026, pedido de Matías: "muchas hojas, información desordenada,
difícil de entender y seguir").

Seis hojas, en el orden en que se leen:
  1. Planilla ITT            la que lee la dirección (planilla_itt.py; distribución de la planilla base de ITT)
  2. Resumen                 de arriba hacia abajo: resultado, costo y precio por rubro, costo por familia y por rubro de
                             MO, parámetros (celdas amarillas), ajuste por inflación, peso y notas
  3. Materiales              una lista por familia (válvulas, accesorios, caños…), cada renglón con lo que pide el cliente,
                             el precio y de dónde sale, y los datos de la pieza pedida y del antecedente
  4. MO y servicios          una lista por rubro (MO de terceros, MO ITT, pintura, END, transporte…), mismas columnas
  5. Antecedentes y desvíos  desvíos declarados, antecedentes usados y precios alternativos que no se usaron
  6. Índices                 tabla de índices del ajuste por inflación

Las celdas que importan tienen nombre (PrecioUnitario, TotalOferta, Cantidad, Flete, FactorMateriales…): las fórmulas se
leen solas ("=PrecioUnitario*Cantidad+Flete") y los programas que leen la planilla (armar_cotizacion.leer_planilla,
generar_oferta.leer_precios) buscan por nombre, no por dirección de celda.

Materiales y MO y servicios tienen las mismas columnas de la A a la R (ver COLS); el Resumen suma la columna J
(subtotal a hoy) según la columna L (clase: Material, Válvula Taval, MO, Servicio). Los renglones de subtotal no tienen
clase, así que no se cuentan dos veces.

La página arma la misma planilla (web/src/documentos.js, planilla). Si se cambia algo acá, cambiarlo allá.
"""
import csv
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from openpyxl import Workbook  # noqa: E402
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side  # noqa: E402
from openpyxl.utils import get_column_letter  # noqa: E402
from openpyxl.workbook.defined_name import DefinedName  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
USD = "#,##0.00"
AZUL, VERDE, VIOLETA, GRIS_T = "1D5F86", "2C7A4B", "6B4E9B", "5D6B75"
AMARILLO, TOTAL, CLARO = "FBEFD6", "E8EDF0", "F4F7F9"
EQ_COLOR = {"Igual": "DDF1E4", "Similar": "FBEFD6", "No encontrado": "F8E1DE"}
TIPO_COLOR = {"cot": "DDF1E4", "lista": "DCEBF4", "stock": "DCEBF4", "ant": "FBEFD6", "est": "F8E1DE"}
EQUIV = {"igual": "Igual", "similar": "Similar", "sin_ref": "No encontrado"}

# Columnas fijas de Materiales y de MO y servicios: (letra, encabezado, ancho, grupo). Los grupos dan el color del encabezado.
COLS = [("A", "Pos", 6, "pedido"), ("B", "Descripción", 46, "pedido"), ("C", "Cant. / {s}", 9, "pedido"), ("D", "Unidad", 7, "pedido"),
        ("E", "Equivalencia", 12, "precio"), ("F", "USD unit. a la fecha del precio", 13, "precio"), ("G", "Fecha del precio", 11, "precio"),
        ("H", "Factor de inflación", 10, "precio"), ("I", "USD unit. a hoy", 12, "precio"), ("J", "Subtotal a hoy USD", 13, "precio"),
        ("K", "Subtotal sin ajuste USD", 13, "precio"), ("L", "Clase", 12, "precio"),
        ("M", "Tipo de origen", 12, "origen"), ("N", "Proveedor o criterio", 40, "origen"), ("O", "Código del catálogo", 12, "origen"),
        ("P", "Descripción del antecedente", 40, "origen"), ("Q", "Diferencia con lo pedido", 40, "origen"), ("R", "Documento de origen", 30, "origen")]
COLOR_GRUPO = {"pedido": VERDE, "precio": AZUL, "origen": VIOLETA, "datos_ped": VERDE, "datos_ant": VIOLETA, "extra": GRIS_T}

# Nombres de las celdas del Resumen (lo leen planilla_itt.py, armar_cotizacion.leer_planilla y generar_oferta.leer_precios)
NOMBRES_RESULTADO = ("PrecioUnitario", "TotalOferta", "Cantidad", "Flete", "IncluirFlete", "CostoUnitario")


def otros(at, cols, familia=False):
    """Datos de la pieza que no tienen columna propia en su familia (auditoría 05-11-2026: ningún dato se pierde)."""
    import atributos_plano
    claves = [k for _, k in atributos_plano.COLS] + atributos_plano.OTROS
    out = ([f"familia: {at['familia']}"] if familia and at.get("familia") else []) + \
        [f"{atributos_plano.NOMBRES.get(k, k)}: {at[k]}" for k in claves if k not in cols and at.get(k)]
    return "; ".join(out)


def _fill(c):
    return PatternFill("solid", fgColor=c)


def _nombrar(wb, nombre, hoja, celda):
    col = "".join(ch for ch in celda if ch.isalpha())
    fila = "".join(ch for ch in celda if ch.isdigit())
    wb.defined_names[nombre] = DefinedName(nombre, attr_text=f"'{hoja}'!${col}${fila}")


def escribir(cfg, carpeta, idx_rows, ruta=None):
    """Arma el libro completo y lo guarda en la carpeta (o en ruta, si se da: lo usa web/probar_planilla.js). Devuelve la ruta."""
    import armar_cotizacion as ac
    import atributos_plano
    import ficha_rubros
    import planilla_itt
    p, eq = cfg["parametros"], cfg["equipo"]
    atributos_plano.atributos_items(carpeta, cfg)
    CAT = {r["codigo"]: r for r in csv.DictReader(open(RAIZ / "conocimiento" / "precios" / "catalogo_materiales.csv", encoding="utf-8"))}
    fus = RAIZ / "conocimiento" / "precios" / "catalogo_codigos_fusionados.csv"
    if fus.exists():  # códigos fusionados al cambiar una regla del catálogo (05-11-2026)
        CAT.update({x["codigo_viejo"]: CAT[x["codigo_vigente"]] for x in csv.DictReader(open(fus, encoding="utf-8")) if x["codigo_vigente"] in CAT})
    mat = [i for i in cfg["items"] if i["grupo"] == "material"]
    srv = [i for i in cfg["items"] if i["grupo"] != "material"]
    try:
        cfg["_oferta"] = json.load(open(carpeta / "oferta.json", encoding="utf-8"))
    except (OSError, ValueError):
        cfg["_oferta"] = {}
    lista_itt = "ITT" in cfg["_oferta"].get("titulo_materiales", "")
    bloque = planilla_itt.bloques(cfg)

    B = Border(bottom=Side(style="thin", color="C9D3D9"))
    BOLD, GRIS = Font(bold=True), Font(italic=True, color=GRIS_T, size=9)
    wb = Workbook()
    rs = wb.active
    rs.title = "Resumen"

    def barra(ws, r, texto, ultima, color=AZUL):
        """Título de sección: barra de color a lo ancho."""
        for j in range(1, ultima + 1):
            ws.cell(r, j).fill = _fill(color)
        c = ws.cell(r, 1, texto)
        c.font = Font(bold=True, color="FFFFFF", size=11)
        ws.row_dimensions[r].height = 18

    def encabezado(ws, r, columnas):
        """columnas: [(texto, grupo)]; fila de encabezados con el color del grupo."""
        for j, (t, g) in enumerate(columnas, 1):
            x = ws.cell(r, j, t)
            x.font = Font(bold=True, color="FFFFFF", size=9)
            x.fill = _fill(COLOR_GRUPO[g])
            x.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
        ws.row_dimensions[r].height = 30

    # ------------------------------------------------------------ Índices (se arma primero: las demás hojas lo usan)
    x = wb.create_sheet("Índices")
    x["A1"] = "ÍNDICES DEL AJUSTE POR INFLACIÓN"; x["A1"].font = Font(bold=True, size=13)
    x["A2"] = ("Factor de un precio = índice del mes de hoy / índice del mes del precio. Materiales: CPI de EE.UU. (los precios ya "
               "están en dólares). MO y servicios: costo local en dólares = IPC INDEC / dólar BNA vendedor (promedio mensual).")
    x["A2"].font = GRIS
    hdr = ["Mes", "IPC Argentina (oct-24=100)", "Dólar BNA vendedor", "Costo local en USD (IPC/dólar, oct-24=100)", "CPI EE.UU. (oct-24=100)",
           "Origen IPC", "Origen dólar", "Origen CPI"]
    encabezado(x, 4, [(t, "precio") for t in hdr])
    for j, w in enumerate([11, 13, 12, 16, 12, 40, 40, 40], 1):
        x.column_dimensions[get_column_letter(j)].width = w
    for i, r in enumerate(idx_rows, 5):
        y, m, _ = map(int, r["mes"].split("-"))
        for j, v in enumerate([date(y, m, 1), float(r["ipc_argentina"]), float(r["dolar_bna"]), float(r["indice_local_usd"]),
                               float(r["cpi_eeuu"]), r["origen_ipc"], r["origen_dolar"], r["origen_cpi"]], 1):
            c = x.cell(i, j, v); c.border = B
            c.number_format = {1: "mm-yyyy", 2: "#,##0.0##", 3: "#,##0.00", 4: "#,##0.0##", 5: "#,##0.0##"}.get(j, "General")
            if j >= 6 and str(v).startswith("dato"):
                c.font = Font(color=VERDE)
            if j >= 6 and ("ESTIMADO" in str(v) or "APROXIMADO" in str(v)):
                c.font = Font(color="A3392F")
    ni = 4 + len(idx_rows)
    x.cell(ni + 2, 1, "Generado con herramientas/indices_inflacion.py. Verde: dato publicado. Rojo: estimado o aproximado. El resto, interpolado."
           + (f" Índices congelados el {ac.a_vista(cfg['indices_congelados']['fecha'])}." if cfg.get("indices_congelados") else "")).font = GRIS
    x.freeze_panes = "B5"
    wb.defined_names["Indices"] = DefinedName("Indices", attr_text=f"'Índices'!$A$5:$E${ni}")

    # ------------------------------------------------------------ Materiales y MO y servicios
    filas = {}  # id(ítem) → (hoja, fila)

    def lista(nombre, secciones, es_srv):
        """secciones: [(título, ítems, columnas de datos de la familia)]. Devuelve [(título, celda del subtotal)]."""
        w = wb.create_sheet(nombre)
        n_fijas = len(COLS)
        w.cell(1, 1, f"{nombre.upper()} · por {eq['singular']} · USD sin IVA").font = Font(bold=True, size=13)
        w.cell(2, 1, "Verde: lo que pide el cliente · Azul: precio (amarillo = se puede cambiar; «a hoy» = con el ajuste por inflación "
                     "del Resumen) · Violeta: de dónde sale el precio" + ("" if es_srv else " · a la derecha, los datos de la pieza pedida y del antecedente")
                ).font = GRIS
        for letra, _, ancho, _ in COLS:
            w.column_dimensions[letra].width = ancho
        col_ind = 4 if es_srv else 5  # columna de Índices: costo local USD (MO y servicios) o CPI EE.UU. (materiales)
        r, subt, n_max = 4, [], n_fijas
        for titulo, its, cols in secciones:
            extra = [] if es_srv else (["ID", "Faltan datos del pedido"] + [f"Pedido: {atributos_plano.ETIQUETAS[k]}" for k in cols] + ["Pedido: otros datos"]
                                       + [f"Antecedente: {atributos_plano.ETIQUETAS[k]}" for k in cols] + ["Antecedente: otros datos"])
            grupos_extra = [] if es_srv else (["extra", "extra"] + ["datos_ped"] * (len(cols) + 1) + ["datos_ant"] * (len(cols) + 1))
            if es_srv:
                extra, grupos_extra = ["ID", "Especificación"], ["extra", "extra"]
            n_max = max(n_max, n_fijas + len(extra))
            barra(w, r, titulo.upper(), n_fijas + len(extra))
            r += 1
            desc = "Descripción" if es_srv else ("Descripción (lista de ITT)" if lista_itt else "Descripción (texto del cliente)")
            encabezado(w, r, [(desc if letra == "B" else t.format(s=eq["singular"]), g) for letra, t, _, g in COLS]
                       + list(zip(extra, grupos_extra)))
            r += 1
            r0 = r
            for it in its:
                s = it["fuentes"][0]
                eqv = "No encontrado" if not s["precio"] or s.get("coincide") == "sin_ref" else EQUIV.get(s.get("coincide"), "")
                if es_srv:
                    clase, cod, desc_ant = ("MO" if it["grupo"] == "mo" else "Servicio"), "", ""
                else:
                    clase = "Válvula Taval" if ac.es_taval(it) else "Material"
                    ped, ant = atributos_plano.fila_datos(it, CAT)
                    cod, desc_ant = ant[0], ant[1]
                f = r
                vals = [it["pos"], it["descripcion"], it["cantidad"], it["unidad"], eqv, s["precio"], ac.fecha(s["fecha"]),
                        f"=IF(AplicarAjuste=1,VLOOKUP(FechaHoy,Indices,{col_ind},1)/VLOOKUP(MAX(G{f},'Índices'!$A$5),Indices,{col_ind},1),1)",
                        f"=F{f}*H{f}", f"=C{f}*I{f}", f"=C{f}*F{f}", clase, ac.TIPOS[s["tipo"]], s["proveedor"], cod, desc_ant,
                        s.get("diferencia", ""), s.get("origen", "")]
                if es_srv:
                    vals += [it["id"], str(it.get("especificacion", ""))]
                else:
                    at, ra = it.get("atributos") or {}, CAT.get(cod, {})
                    vals += ([it["id"], ", ".join(atributos_plano.NOMBRES.get(k, k) for k in it.get("faltan_datos", []))]
                             + [at.get(k, "") for k in cols] + [otros(at, cols, True)]
                             + [ra.get(k, "") for k in cols] + [otros(ra, cols) if ra else ""])
                for j, v in enumerate(vals, 1):
                    c = w.cell(r, j, v); c.border = B
                    c.alignment = Alignment(vertical="top", wrap_text=j in (2, 14, 16, 17))
                w.cell(r, 3).number_format = "#,##0" if float(it["cantidad"]).is_integer() else ac.FMT_TECNICO
                w.cell(r, 3).fill = w.cell(r, 6).fill = _fill(AMARILLO)
                for j in (6, 9, 10, 11):
                    w.cell(r, j).number_format = USD
                w.cell(r, 7).number_format = "dd-mm-yyyy"
                w.cell(r, 8).number_format = "#,##0.0000"
                w.cell(r, 5).fill = _fill(EQ_COLOR.get(eqv, "FFFFFF"))
                w.cell(r, 13).fill = _fill(TIPO_COLOR[s["tipo"]])
                if not es_srv and vals[n_fijas + 1]:
                    w.cell(r, n_fijas + 2).fill = _fill("F8E1DE")
                filas[id(it)] = (nombre, r)
                r += 1
            w.cell(r, 2, f"Subtotal {titulo.split(' (')[0].lower()}").font = BOLD
            for j in range(1, n_fijas + 1):
                w.cell(r, j).fill = _fill(TOTAL)
            for letra in ("J", "K"):
                c = w[f"{letra}{r}"]; c.value = f"=SUM({letra}{r0}:{letra}{r - 1})"; c.font = BOLD; c.number_format = USD
            subt.append((titulo.split(" (")[0], f"'{nombre}'!$J${r}"))
            r += 2
        # total de la hoja (por clase: lo mismo que suma el Resumen)
        barra(w, r, f"TOTAL {nombre.upper()} por {eq['singular']}", n_fijas)
        for letra in ("J", "K"):
            c = w[f"{letra}{r}"]; c.value = f'=SUMIF($L$5:$L${r - 1},"?*",{letra}$5:{letra}${r - 1})'
            c.font = Font(bold=True, color="FFFFFF"); c.number_format = USD
        r += 1
        alt = [(it, a) for it in (x for _, its, _ in secciones for x in its) for a in it["fuentes"][1:]]
        if alt:
            r += 1
            barra(w, r, "OTROS PRECIOS ENCONTRADOS (referencia: no entran en el cálculo)", 8, GRIS_T)
            r += 1
            encabezado(w, r, [(t, "extra") for t in ("Pos", "Descripción", "USD unit.", "Fecha", "Tipo de origen", "Proveedor", "Documento de origen", "Equivalencia")])
            r += 1
            for it, a in alt:
                vals = [it["pos"], it["descripcion"], a["precio"], ac.fecha(a["fecha"]), ac.TIPOS[a["tipo"]], a["proveedor"], a.get("origen", ""),
                        EQUIV.get(a.get("coincide"), "")]
                for j, v in enumerate(vals, 1):
                    c = w.cell(r, j, v); c.border = B; c.font = Font(color=GRIS_T)
                w.cell(r, 3).number_format = USD; w.cell(r, 4).number_format = "dd-mm-yyyy"
                r += 1
        if es_srv and cfg.get("nota_mo_html"):
            w.cell(r + 1, 2, ac.sin_html(cfg["nota_mo_html"])).font = GRIS
        for j in range(n_fijas + 1, n_max + 1):
            w.column_dimensions[get_column_letter(j)].width = 30 if es_srv else 13
        w.column_dimensions[get_column_letter(n_fijas + 1)].width = 7
        if not es_srv:
            w.column_dimensions[get_column_letter(n_fijas + 2)].width = 22
        w.freeze_panes = "C4"
        w.sheet_view.zoomScale = 90
        return subt

    sec_mat = []
    for g, (nombre, _, cols) in enumerate(atributos_plano.GRUPOS):
        its = [it for it in mat if atributos_plano.grupo_de(it) == g]
        if its:
            sec_mat.append((nombre, its, cols))
    sec_srv = []
    for nombre in planilla_itt.BLOQUES:
        its = [it for it in srv if bloque[id(it)] == nombre]
        if its:
            sec_srv.append((nombre, its, []))
    subt_mat = lista("Materiales", sec_mat, False)
    subt_srv = lista("MO y servicios", sec_srv, True)

    # ------------------------------------------------------------ Resumen
    for col, w in zip("ABCDEF", (52, 16, 12, 16, 16, 44)):
        rs.column_dimensions[col].width = w
    rs["A1"] = f"{cfg['codigo']} {cfg['revision']} · {cfg['titulo']}"; rs["A1"].font = Font(bold=True, size=14)
    rs["A2"] = f"{cfg['subtitulo_planilla']} · {cfg['estado']} {ac.a_vista(cfg['fecha'])}"; rs["A2"].font = Font(italic=True, color=GRIS_T)
    if cfg["estado"] in ("borrador", ""):
        rs["A3"] = "BORRADOR, SIN REVISAR: no enviar al cliente"; rs["A3"].font = Font(bold=True, color="A3392F")
    rs["A4"] = "Hojas: Planilla ITT (para la dirección) · Resumen · Materiales · MO y servicios · Antecedentes y desvíos · Índices"
    rs["A4"].font = GRIS
    S = eq["singular"]
    r = 6
    # 1. resultado
    barra(rs, r, "1. RESULTADO", 6); r += 1
    res = [("PrecioUnitario", f"PRECIO UNITARIO POR {S.upper()}", "=ROUND(PrecioCalculado,2)", USD, "Redondeado a 2 decimales; es el que va a la oferta"),
           (None, f"Cantidad de {eq['plural']}", "=Cantidad", "0", ""),
           (None, "Flete y embalaje (por envío)", "=Flete", USD, "0 si no se incluye (entrega EXW)"),
           ("TotalOferta", "TOTAL DE LA OFERTA SIN IVA", "=PrecioUnitario*Cantidad+Flete", USD, "Precio unitario × cantidad + flete"),
           (None, f"Costo por {S}", "=CostoUnitario", USD, "Sección 2"),
           (None, "Margen sobre el precio", "=IFERROR(1-CostoUnitario/PrecioCalculado,0)", "0.0%", ""),
           (None, "Precio de venta por kg (USD/kg)", "=IF(PesoEquipo>0,PrecioUnitario/PesoEquipo,0)", USD, "Con el peso de la sección 4")]
    for nombre, t, f, z, nota in res:
        rs.cell(r, 1, t); c = rs.cell(r, 2, f); c.number_format = z
        rs.cell(r, 3, nota).font = GRIS
        if nombre:
            _nombrar(wb, nombre, "Resumen", f"B{r}")
            for j in (1, 2):
                rs.cell(r, j).font = Font(bold=True, size=12, color=AZUL)
                rs.cell(r, j).fill = _fill(TOTAL)
        r += 1
    r += 1
    # 2. costo y precio por rubro
    barra(rs, r, f"2. COSTO Y PRECIO POR RUBRO (por {S})", 6); r += 1
    encabezado(rs, r, [(t, "precio") for t in ("Rubro", f"Costo / {S}", "Factor", f"Precio / {S}", f"Total × {eq['plural']}", "De dónde sale")]); r += 1
    M, MS = "Materiales!", "'MO y servicios'!"
    rubros = [("CostoMateriales", "Materiales (sin válvulas Taval)", f'=SUMIF({M}$L:$L,"Material",{M}$J:$J)', "=FactorMateriales", "Hoja Materiales, clase Material (con ajuste por inflación)"),
              ("CostoContingencia", "Contingencia de materiales", None, "=FactorMateriales", "Materiales × contingencia"),
              ("CostoTaval", "Válvulas Taval (con su contingencia)", f'=SUMIF({M}$L:$L,"Válvula Taval",{M}$J:$J)*(1+Contingencia)', "=FactorTaval", "Hoja Materiales, clase Válvula Taval; factor propio"),
              ("CostoMO", "Mano de obra", f'=SUMIF({MS}$L:$L,"MO",{MS}$J:$J)', "=FactorMO", "Hoja MO y servicios, clase MO"),
              ("CostoServicios", "Servicios e insumos", f'=SUMIF({MS}$L:$L,"Servicio",{MS}$J:$J)', "=FactorMO", "Hoja MO y servicios, clase Servicio")]
    r1 = r
    for nombre, t, f, fa, de in rubros:
        rs.cell(r, 1, t)
        rs.cell(r, 2, f or "=CostoMateriales*Contingencia").number_format = USD
        rs.cell(r, 3, fa).number_format = "#,##0.00"
        rs.cell(r, 4, f"=B{r}*C{r}").number_format = USD
        rs.cell(r, 5, f"=D{r}*Cantidad").number_format = USD
        rs.cell(r, 6, de).font = GRIS
        _nombrar(wb, nombre, "Resumen", f"B{r}")
        for j in range(1, 6):
            rs.cell(r, j).border = B
        r += 1
    rs.cell(r, 1, f"Total por {S}")
    rs.cell(r, 2, f"=SUM(B{r1}:B{r - 1})"); rs.cell(r, 3, f"=IFERROR(D{r}/B{r},0)"); rs.cell(r, 4, f"=SUM(D{r1}:D{r - 1})"); rs.cell(r, 5, f"=SUM(E{r1}:E{r - 1})")
    rs.cell(r, 6, "Factor = factor promedio").font = GRIS
    _nombrar(wb, "CostoUnitario", "Resumen", f"B{r}"); _nombrar(wb, "PrecioCalculado", "Resumen", f"D{r}")
    for j in range(1, 6):
        c = rs.cell(r, j); c.fill = _fill(TOTAL); c.font = BOLD; c.number_format = "#,##0.00" if j == 3 else USD
    r += 1
    rs.cell(r, 1, "Flete y embalaje (por envío)")
    rs.cell(r, 3, "=FactorFlete").number_format = "#,##0.00"
    rs.cell(r, 5, "=IF(IncluirFlete=1,(FleteARS/TipoCambio+EmbalajeUSD)*FactorFlete,0)").number_format = USD
    rs.cell(r, 6, "Parámetros de flete (sección 4)").font = GRIS
    _nombrar(wb, "Flete", "Resumen", f"E{r}")
    r += 1
    rs.cell(r, 1, "Total de la oferta sin redondear")
    rs.cell(r, 5, f"=E{r - 2}+E{r - 1}").number_format = USD
    rs.cell(r, 6, "El de la oferta usa el unitario redondeado (sección 1)").font = GRIS
    r += 1
    rs.cell(r, 1, f"Costo por {S} sin ajuste por inflación")
    rs.cell(r, 2, f'=(SUMIF({M}$L:$L,"?*",{M}$K:$K))*(1+Contingencia)+SUMIF({MS}$L:$L,"?*",{MS}$K:$K)').number_format = USD
    r += 1
    rs.cell(r, 1, "Ajuste por inflación incluido en el costo")
    rs.cell(r, 2, f"=CostoUnitario-B{r - 1}").number_format = USD
    rs.cell(r, 3, f"=IFERROR(B{r}/B{r - 1},0)").number_format = "+0.0%"
    r += 2
    # 3. costo por familia y por rubro de MO
    barra(rs, r, f"3. DÓNDE ESTÁ EL COSTO (por {S}, a hoy, sin contingencia)", 6); r += 1
    encabezado(rs, r, [(t, "precio") for t in ("Familia de materiales / rubro de MO y servicios", "Costo", "% del costo", "", "", "")]); r += 1
    r1 = r
    for grupo, sub in (("Materiales", subt_mat), ("MO y servicios", subt_srv)):
        rs.cell(r, 1, grupo).font = BOLD; r += 1
        for t, ref in sub:
            rs.cell(r, 1, f"   {t}"); rs.cell(r, 2, f"={ref}").number_format = USD
            rs.cell(r, 3, f"=IFERROR(B{r}/SUM($B${r1}:$B$__FIN__),0)").number_format = "0.0%"
            r += 1
    fin = r - 1
    for k in range(r1, r):
        c = rs.cell(k, 3)
        if isinstance(c.value, str):
            c.value = c.value.replace("__FIN__", str(fin))
    rs.cell(r, 1, "Total (sin contingencia)"); rs.cell(r, 2, f"=SUM(B{r1}:B{fin})").number_format = USD
    rs.cell(r, 1).font = rs.cell(r, 2).font = BOLD
    r += 2
    # 4. parámetros
    barra(rs, r, "4. PARÁMETROS (las celdas amarillas se pueden cambiar)", 6); r += 1
    pe = ficha_rubros.peso_equipo(cfg)
    params = [("Cantidad", f"Cantidad de {eq['plural']}", p["N"], "0", ""),
              ("FactorMateriales", "Factor de materiales (y su contingencia)", p["FM"], "#,##0.00", "Propuesta 1,35; lo define la dirección"),
              ("FactorMO", "Factor de mano de obra y servicios", p["FMO"], "#,##0.00", "1,35; 1,40 solo para MO vendida sola"),
              ("FactorTaval", "Factor de válvulas Taval", p.get("FTV", 1.0), "#,##0.00", "Empresa del grupo: por defecto 1"),
              ("Contingencia", "Contingencia de materiales", p["CONT"] / 100, "0%", ""),
              ("AplicarAjuste", "Aplicar ajuste por inflación (1 = sí, 0 = no)", p["AJ"], "0", "Lleva cada precio de su fecha a la de referencia"),
              ("FechaHoy", "Fecha de referencia de los precios", ac.fecha(p["fecha_referencia"]), "dd-mm-yyyy", ""),
              ("IncluirFlete", "Incluir flete (1 = sí, 0 = no)", p["TRANS"], "0", "Sin flete: entrega EXW planta Quilmes Oeste"),
              ("TipoCambio", "Tipo de cambio ARS/USD (BNA)", p["TC"], "#,##0", "Para pasar el flete a dólares"),
              ("FleteARS", "Flete ARS por envío", p["TR_ARS"], "#,##0", ""),
              ("EmbalajeUSD", "Embalaje USD por envío (estimado)", p["TR_EMB"], USD, ""),
              ("FactorFlete", "Factor de flete", p["TR_F"], "#,##0.00", ""),
              ("PesoEquipo", f"Peso aproximado por {S} (kg)", pe["kg"], "#,##0", "De la ficha de rubros; se puede corregir")]
    for nombre, t, v, z, nota in params:
        rs.cell(r, 1, t); c = rs.cell(r, 2, v); c.fill = _fill(AMARILLO); c.number_format = z; c.border = B
        rs.cell(r, 3, nota).font = GRIS
        _nombrar(wb, nombre, "Resumen", f"B{r}")
        r += 1
    r += 1
    # 5. ajuste por inflación y peso
    barra(rs, r, "5. AJUSTE POR INFLACIÓN Y PESO", 6); r += 1
    for t, f, z in (("Variación 12 meses, materiales (CPI EE.UU.)", "=VLOOKUP(FechaHoy,Indices,5,1)/VLOOKUP(EDATE(FechaHoy,-12),Indices,5,1)-1", "0.0%"),
                    ("Variación 12 meses, MO y servicios (costo local en USD)", "=VLOOKUP(FechaHoy,Indices,4,1)/VLOOKUP(EDATE(FechaHoy,-12),Indices,4,1)-1", "0.0%"),
                    ("Costo por kg (USD/kg)", "=IF(PesoEquipo>0,CostoUnitario/PesoEquipo,0)", USD),
                    ("Precio de venta por kg (USD/kg)", "=IF(PesoEquipo>0,PrecioUnitario/PesoEquipo,0)", USD)):
        rs.cell(r, 1, t); rs.cell(r, 2, f).number_format = z; r += 1
    for t in ("Factor de cada renglón = índice del mes de referencia / índice del mes del precio (hoja Índices).",
              ("Peso sin estos renglones (no suman): pos " + ", ".join(pe["sin_peso"]) + ". Corregir el peso a mano si hace falta.") if pe["sin_peso"] else
              "Peso: piping con tabla, estructura, renglones por kg y piezas con su peso; sin compras extra, repuestos ni instrumentos."):
        rs.cell(r, 1, t).font = GRIS; r += 1
    if cfg.get("planilla_notas"):
        r += 1
        barra(rs, r, "6. NOTAS", 6); r += 1
        for t in cfg["planilla_notas"]:
            rs.merge_cells(start_row=r, start_column=1, end_row=r, end_column=6)
            c = rs.cell(r, 1, ac.sin_html(t)); c.alignment = Alignment(wrap_text=True, vertical="top")
            rs.row_dimensions[r].height = 15 * (1 + len(t) // 130)
            r += 1
    rs.freeze_panes = "A5"

    # ------------------------------------------------------------ Antecedentes y desvíos
    d = wb.create_sheet("Antecedentes y desvíos")
    for j, w in enumerate([30, 12, 50, 14, 70], 1):
        d.column_dimensions[get_column_letter(j)].width = w
    d["A1"] = "ANTECEDENTES Y DESVÍOS"; d["A1"].font = Font(bold=True, size=13)
    r = 3
    barra(d, r, "DESVÍOS Y ACLARACIONES (van a la oferta)", 5); r += 1
    encabezado(d, r, [(t, "origen") for t in ("Pos", "", "Desvío", "Detalle", "")]); r += 1
    for dv in cfg.get("desvios", []) or [{"tag": "", "titulo": "Sin desvíos declarados", "texto": ""}]:
        for j, v in ((1, dv["tag"]), (3, dv["titulo"]), (4, dv["texto"])):  # pos en A:B, desvío en C, detalle en D:E
            c = d.cell(r, j, ac.sin_html(v)); c.alignment = Alignment(wrap_text=True, vertical="top")
        for j in range(1, 6):
            d.cell(r, j).border = B
        d.merge_cells(start_row=r, start_column=1, end_row=r, end_column=2)
        d.merge_cells(start_row=r, start_column=4, end_row=r, end_column=5)
        r += 1
    r += 1
    barra(d, r, "ANTECEDENTES USADOS", 5); r += 1
    encabezado(d, r, [(t, "origen") for t in ("Carpeta / oferta", "Fecha", "Qué es", "Precio c/u USD", "Qué se tomó")]); r += 1
    for an in cfg.get("antecedentes", []) or [{"carpeta_html": "Sin antecedentes cargados", "fecha": "", "que": "", "precio": "", "tomado_html": ""}]:
        for j, v in enumerate([an["carpeta_html"], ac.a_vista(an["fecha"]), an["que"], an["precio"], an["tomado_html"]], 1):
            c = d.cell(r, j); c.alignment = Alignment(wrap_text=True, vertical="top"); c.border = B
            ac.celda_excel(c, ac.sin_html(v), "precio" if j == 4 else "", documento=True)
        r += 1

    # ------------------------------------------------------------ Planilla ITT (primera hoja) y orden final
    planilla_itt.escribir(wb, cfg, filas, CAT, ac.fecha)
    cfg.pop("_oferta", None)
    orden = ["Planilla ITT", "Resumen", "Materiales", "MO y servicios", "Antecedentes y desvíos", "Índices"]
    wb._sheets = [wb[n] for n in orden]
    wb.active = 0
    ruta = Path(ruta) if ruta else carpeta / f"{cfg['codigo']}_{cfg['archivo_planilla']}.xlsx"
    wb.save(ruta)
    return ruta


def leer_valores(ruta, nombres=NOMBRES_RESULTADO):
    """Recalcula la planilla con LibreOffice y devuelve {nombre: valor} de las celdas con nombre."""
    import subprocess
    import tempfile
    from openpyxl import load_workbook
    from candado import perfil_soffice
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["soffice", perfil_soffice(), "--headless", "--convert-to", "xlsx", "--outdir", tmp, str(ruta)], check=True, capture_output=True)
        wb = load_workbook(Path(tmp) / Path(ruta).name, data_only=True)
        out = {}
        for n in nombres:
            hoja, celda = next(iter(wb.defined_names[n].destinations))
            out[n] = wb[hoja][celda.replace("$", "")].value
        return out
