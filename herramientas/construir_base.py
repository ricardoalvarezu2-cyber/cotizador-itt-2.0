"""Arma la base de conocimiento (conocimiento/*.csv) a partir de las fuentes vigentes de ITT.

Uso: python herramientas/construir_base.py [carpeta_fuentes]   (por defecto: fuentes_originales/)

Cada tabla generada lleva el nombre de la fuente de la que sale (ver conocimiento/fuentes.md).
Volver a correrlo cuando se actualice una fuente: los CSV se regeneran completos.
"""
import csv
import re
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

import openpyxl

sys.path.insert(0, str(Path(__file__).resolve().parent))
from numeros import fecha_iso, numero as _numero  # noqa: E402
import xlrd

RAIZ = Path(__file__).resolve().parent.parent
ORIGEN = Path(sys.argv[1]) if len(sys.argv) > 1 else RAIZ / "fuentes_originales"
DESTINO = RAIZ / "conocimiento"

F_FACTORES = "factores_soldadura_rev02-2026.xlsx"
F_ELEMENTOS = "cotizacion_elementos_equipos_2026-03.xlsx"
F_RENAR = "renar_lista_2025-12.xlsx"
F_STOCK = "stock_valorizado_2024-11.xlsx"
F_CODIFICADOR = "codificador_taval_2023-07.xlsx"
F_REGISTRO = "registro_presupuestos_2022-05.xlsx"
F_REMITOS = "remitos_valorizados_2022-2023.xls"
F_SEGUIMIENTO = "seguimiento_presupuestos_proyectos_2026-08.xlsx"
F_COSTO_PLANTA = "costo_mo_planta_2024-10.xlsx"

# Familia de producto (códigos de codificacion/familias_producto.csv) según palabras de la descripción
FAMILIAS = [("CALENT", "C"), ("SEPARADOR", "SEP"), ("SCRUB", "SC"), ("FILTRO", "F"), ("MANIFOLD", "M"),
            ("COLECTOR", "CO"), ("ACOMETIDA", "CO"), ("PUENTE", "P"), ("TRAMO", "P"), ("SATELITE", "P"),
            ("SKID", "SK"), ("TANQUE", "T"), ("ACUMULADOR", "T"), ("TRAMPA", "TS"), ("DESGA", "DES"),
            ("VALVULA", "V"), ("MAZO", "OT"), ("MOJON", "OT")]


def familia(descripcion: str) -> str:
    d = sin_acentos(descripcion.upper())
    return next((cod for clave, cod in FAMILIAS if clave in d), "OT")


# ---------------------------------------------------------------- utilidades

def escribir(ruta: str, columnas: list, filas: list):
    archivo = DESTINO / ruta
    archivo.parent.mkdir(parents=True, exist_ok=True)
    with archivo.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(columnas)
        for fila in filas:
            w.writerow(["" if v is None else v for v in fila])
    print(f"  {ruta}: {len(filas)} filas")


def texto(v) -> str:
    return " ".join(str(v).split()) if v is not None else ""


def sin_acentos(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def numero(v):
    """Lector único de números: herramientas/numeros.py (4,413.92 · 4.413,92 · 28.500 · 1.096.71 · 0,904)."""
    return _numero(v)


def fecha(v) -> str:
    if isinstance(v, datetime):
        return v.date().isoformat()
    return texto(v)


def pulgadas(v):
    """'11/2' -> 1.5, '3 1/2' -> 3.5, '1/8' -> 0.125, 6 -> 6.0"""
    if isinstance(v, (int, float)):
        return float(v)
    s = texto(v).replace('"', "")
    m = re.fullmatch(r"(\d+)\s+(\d+)/(\d+)", s) or re.fullmatch(r"(\d)(1)/(2)", s)
    if m:
        return int(m.group(1)) + int(m.group(2)) / int(m.group(3))
    m = re.fullmatch(r"(\d+)/(\d+)", s)
    if m:
        return int(m.group(1)) / int(m.group(2))
    return numero(s)


# ---------------------------------------------------------------- técnico

def factores_soldadura():
    """Regla única: factor = espesor / espesor STD del mismo DN (mínimo 1). Hasta 10" coincide con la
    tabla de ITT; desde 12" la tabla original mezclaba criterios y se conserva en factor_original_itt."""
    ws = openpyxl.load_workbook(ORIGEN / F_FACTORES, data_only=True)["Tabla Principal"]
    filas, esparragos = [], []
    series = [(14, 150), (16, 300), (18, 600), (20, 900), (22, 1500)]  # columna de medida; la de cantidad es la siguiente
    for r in range(10, 178):
        dn = pulgadas(ws.cell(r, 3).value)
        if not dn:
            continue
        sch = texto(ws.cell(r, 5).value)
        clase = texto(ws.cell(r, 6).value).replace("SDT", "STD")
        od, espesor = numero(ws.cell(r, 4).value), numero(ws.cell(r, 7).value)
        if dn == 0.375 and espesor in (4.78, 7.47):  # filas de 1/2" cargadas como 3/8" en el escaneo original
            dn, od = 0.5, 21.3
        filas.append([dn, od, sch if sch != "-" else "", clase if clase not in ("-", "0") else "", espesor,
                      round(numero(ws.cell(r, 8).value) or 0, 4), round(numero(ws.cell(r, 10).value) or 0, 1),
                      numero(ws.cell(r, 11).value) or 0, numero(ws.cell(r, 12).value) or 0])
        for col, serie in series:
            medida, cant = texto(ws.cell(r, col).value), numero(ws.cell(r, col + 1).value)
            if medida and medida != "-" and cant:
                esparragos.append((dn, serie, medida, int(cant)))
    espesor_std = {}
    for f in filas:
        if f[3] == "STD" or (f[2] == "40" and f[0] not in espesor_std):
            espesor_std[f[0]] = f[4] if f[3] == "STD" else espesor_std.get(f[0], f[4])
    salida = []
    for dn, od, sch, clase, espesor, original, desarrollo, chicas, grandes in sorted(filas, key=lambda f: (f[0], f[4])):
        factor = round(max(1.0, espesor / espesor_std[dn]), 4)
        salida.append([dn, od, sch, clase, espesor, factor, round(dn * factor, 4), original, desarrollo,
                       chicas, grandes])
    escribir("tecnico/factores_soldadura.csv",
             ["dn_pulg", "diam_ext_mm", "schedule", "clase", "espesor_mm", "factor_espesor",
              "diam_equivalente_pulg", "factor_original_itt", "desarrollo_mm", "placas_rx_chicas",
              "placas_rx_grandes"], salida)
    escribir("tecnico/esparragos_por_brida.csv", ["dn_pulg", "serie", "medida_esparrago", "cantidad"],
             sorted(set(esparragos)))
    acc = []
    for r in range(178, 190):
        nombre, nota, f = texto(ws.cell(r, 3).value), texto(ws.cell(r, 5).value), numero(ws.cell(r, 8).value)
        if nombre and f:
            acc.append([nombre, f, nota])
    escribir("tecnico/factores_accesorios.csv", ["accesorio", "factor", "criterio"], acc)


def perfiles():
    """Masa y superficie por metro. En los perfiles W la masa está en otra columna:
    se toma la que coincide con el kg/m indicado en la designación (ej. 'W(I) 460 x 52,0')."""
    ws = openpyxl.load_workbook(ORIGEN / F_FACTORES, data_only=True)["Tabla de Perfiles "]
    filas, familia = [], ""
    for r in range(12, ws.max_row + 1):
        if texto(ws.cell(r, 2).value):
            familia = texto(ws.cell(r, 2).value).replace("Perfiles ", "")
        nombre = texto(ws.cell(r, 4).value)
        if not nombre or nombre in ("0", "Designación del Perfil", "mm x kg/m") or not re.search(r"\d", nombre):
            continue
        kg_m, sup = numero(ws.cell(r, 13).value), numero(ws.cell(r, 21).value)
        m = re.search(r"x\s*([\d,.]+)", nombre)
        if m:  # perfiles W: la designación trae el kg/m
            esperado = numero(m.group(1))
            candidatos = [numero(ws.cell(r, c).value) for c in range(5, 21)]
            kg_m = next((c for c in candidatos if c and abs(c - esperado) <= 1.5), esperado)
        if not kg_m:
            continue
        tipo = familia or re.match(r"[A-Z]+", nombre).group(0)
        filas.append([tipo, nombre, round(kg_m, 2), round(sup, 3) if sup else ""])
    escribir("tecnico/perfiles.csv", ["familia", "designacion", "kg_por_m", "m2_por_m"], filas)


# ---------------------------------------------------------------- codificación

def codificacion():
    wb = openpyxl.load_workbook(ORIGEN / F_CODIFICADOR, data_only=True, read_only=True)
    hojas = {
        "VALVULA": ("valvula_tipos", 1, ["codigo", "descripcion", "abreviatura"]),
        "DIAMETRO": ("diametros", 0, ["codigo", "pulgadas"]),
        "SERIE": ("series", 0, ["codigo", "serie"]),
        "EXTREMOS": ("extremos", 0, ["codigo", "descripcion", "abreviatura"]),
        "MATERIAL": ("materiales", 0, ["codigo", "descripcion", "abreviatura"]),
        "MANDO": ("mandos", 0, ["codigo", "descripcion", "abreviatura"]),
        "COMPONENTES": ("componentes", 0, ["codigo", "descripcion", "abreviatura"]),
        "FILT-MESH": ("filtros_mesh", 0, ["codigo", "descripcion", "abreviatura"]),
    }
    for hoja, (nombre, desde, cols) in hojas.items():
        filas = []
        for row in wb[hoja].iter_rows(min_row=2, values_only=True):
            valores = [texto(v) for v in row[desde:desde + len(cols)]]
            if valores[0] and valores[1] and valores[1].upper() != "SELECCIONE":
                filas.append(valores)
        escribir(f"codificacion/{nombre}.csv", cols, filas)
    clientes = []
    for row in wb["CLIENTES"].iter_rows(min_row=2, values_only=True):
        if row[1] and row[2]:
            clientes.append([texto(row[1]), texto(row[2]), texto(row[0]), texto(row[3])])
    escribir("comercial/clientes.csv", ["codigo", "razon_social", "estado", "calificacion"], clientes)


# ---------------------------------------------------------------- precios

COLUMNAS_ELEMENTOS = {
    "dimension": ("DIMEN", "DIAMETRO"),
    "tipo": ("TIPO", "SECC"),
    "schedule": ("SCH",),
    "serie": ("SERIE",),
    "material": ("MATERIAL",),
    "norma": ("NORMA",),
    "unidad": ("UNIDAD", "METROS"),
    "precio_usd": ("COSTO", "U$D"),
    "proveedor": ("PROVEEDOR",),
    "fecha": ("FECHA",),
    "plazo_entrega": ("PLAZO",),
    "en_stock": ("STOCK",),
    "cotizacion_proveedor": ("COTIZACI",),
    "oferta_valida": ("OFERTA",),
    "observacion": ("OBS", "ORIGEN"),
}


def precios_elementos():
    wb = openpyxl.load_workbook(ORIGEN / F_ELEMENTOS, data_only=True)
    filas = []
    for ws in wb.worksheets:
        enc = None
        for r in range(1, 8):
            if any("DESCRIP" in texto(ws.cell(r, c).value).upper() for c in range(1, 22)):
                enc = r
                break
        if not enc:
            continue
        cols, desc = {}, []
        for c in range(1, 22):
            t = sin_acentos(texto(ws.cell(enc, c).value).upper())
            if not t:
                continue
            if "DESCRIP" in t:
                desc.append(c)
                continue
            for campo, claves in COLUMNAS_ELEMENTOS.items():
                if campo not in cols and any(k in t for k in claves):
                    cols[campo] = c
                    break
        if "precio_usd" not in cols:
            continue
        enc_precio = sin_acentos(texto(ws.cell(enc, cols["precio_usd"]).value).upper())
        ultima = ""
        for r in range(enc + 1, ws.max_row + 1):
            d = texto(ws.cell(r, desc[0]).value)
            ultima = d or ultima
            precio = numero(ws.cell(r, cols["precio_usd"]).value)
            if not precio:
                continue
            detalle = texto(ws.cell(r, desc[1]).value) if len(desc) > 1 else ""
            valor = {k: ws.cell(r, c).value for k, c in cols.items()}
            item, dim = ultima, texto(valor.get("dimension"))
            # moneda: "$16.114,07 + IVA" en una hoja cuyo encabezado dice solo "COSTO" son pesos (auditoría 27/10/2026)
            crudo = texto(ws.cell(r, cols["precio_usd"]).value)
            en_usd = re.search(r"U\$|USD|U\$S|DOLAR", crudo.upper()) or re.search(r"U\$|USD|DOLAR", enc_precio)
            moneda = "USD" if en_usd or not re.search(r"\$", crudo) else "ARS"
            # fecha: la de su columna; si no es válida, la primera dd/mm/aa de la fila (columnas corridas); nunca por defecto
            # "Cintolo cot 11/02/26" en la columna proveedor manda: es la fecha de la cotización
            f_iso = fecha_iso(valor.get("proveedor")) or fecha_iso(valor.get("fecha"))
            if not f_iso:
                f_iso = next((fecha_iso(c.value) for c in ws[r] if fecha_iso(c.value)), "")
            obs = texto(valor.get("observacion"))
            if not f_iso and texto(valor.get("fecha")):
                obs = "; ".join(x for x in [obs, f"fecha ilegible en el origen: '{texto(valor.get('fecha'))}'"] if x)
            if detalle:
                # Hojas con dos columnas DESCRIPCION (bombas, caja porta orificio, anillo de purga, válvulas): la primera
                # y la dimensión son un modelo copiado de otra hoja; lo cotizado es la segunda.
                item, detalle, dim = detalle, f"col. A de la hoja (no es lo cotizado): {ultima} {dim}".strip(), ""
            filas.append([
                ws.title.strip(), item, detalle, dim, texto(valor.get("tipo")),
                texto(valor.get("schedule")), texto(valor.get("serie")), texto(valor.get("material")),
                texto(valor.get("norma")), texto(valor.get("unidad")), round(precio, 4), moneda,
                texto(valor.get("proveedor")), f_iso, texto(valor.get("plazo_entrega")),
                texto(valor.get("en_stock")), texto(valor.get("cotizacion_proveedor")),
                texto(valor.get("oferta_valida")), obs,
            ])
    escribir("precios/precios_componentes.csv",
             ["rubro", "descripcion", "detalle", "dimension", "tipo", "schedule", "serie", "material", "norma",
              "unidad", "precio", "moneda", "proveedor", "fecha", "plazo_entrega", "en_stock", "cotizacion_proveedor",
              "oferta_valida", "observacion"], filas)


def lista_renar():
    ws = openpyxl.load_workbook(ORIGEN / F_RENAR, data_only=True)["Table 1"]
    filas, categoria = [], ""
    for row in ws.iter_rows(values_only=True):
        valores = [v for v in row if v not in (None, "")]
        if len(valores) == 1 and isinstance(valores[0], str):
            categoria = texto(valores[0])
            continue
        if not row or not isinstance(row[0], (int, float)) or not row[1]:
            continue
        resto = [texto(v) for v in row[2:] if v not in (None, "")]
        precio = next((numero(v) for v in resto if re.fullmatch(r"[\d.]+,\d{2}", v)), None)
        unidad = next((v for v in resto if re.fullmatch(r"[A-Za-zñ. ]+", v)), "")
        if precio:
            filas.append([int(row[0]), texto(row[1]), categoria, precio, unidad])
    escribir("precios/lista_renar_2025-12.csv", ["codigo", "producto", "categoria", "precio_usd", "unidad"], filas)


def stock():
    ws = openpyxl.load_workbook(ORIGEN / F_STOCK, data_only=True)["General"]
    filas = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or not row[2]:
            continue
        ultima = row[9] if isinstance(row[9], datetime) else None
        filas.append([texto(row[2]), texto(row[3]), texto(row[1]), texto(row[0]), texto(row[4]),
                      numero(row[5]), numero(row[7]), numero(row[8]) if ultima else "",
                      ultima.date().isoformat() if ultima else "", texto(row[10]).upper()])
    escribir("precios/stock_2024-11.csv",
             ["codigo", "descripcion", "grupo", "deposito", "unidad", "cantidad", "precio_maestro_usd",
              "precio_ultima_compra", "fecha_ultima_compra", "moneda"], filas)


# ---------------------------------------------------------------- comercial

def registro_cotizaciones():
    wb = openpyxl.load_workbook(ORIGEN / F_REGISTRO, data_only=True)
    ws = wb["Planilla Principal "]
    familias = {}
    for r in range(3, 26):  # tabla de códigos PyS en G:H
        cod, desc = texto(ws.cell(r, 7).value), texto(ws.cell(r, 8).value)
        if cod and desc and len(cod) <= 4:
            familias[cod] = desc
    escribir("codificacion/familias_producto.csv", ["codigo", "familia"], sorted(familias.items()))
    enc = 27
    cols = {texto(ws.cell(enc, c).value): c for c in range(1, 30) if ws.cell(enc, c).value}

    def v(r, nombre):
        clave = next(k for k in cols if k.startswith(nombre))
        return ws.cell(r, cols[clave]).value

    resultado = {"1": "ganada", "0.5": "activa", "L1": "perdida_precio", "L2": "perdida_tecnica",
                 "L3": "perdida_plazo", "L4": "perdida_otros", "C": "cancelada"}
    filas = []
    for r in range(enc + 1, ws.max_row + 1):
        cliente = texto(v(r, "RAZON SOCIAL"))
        if not cliente or not texto(v(r, "DESCRIPCION DEL MATERIAL")):
            continue
        sit = texto(v(r, "SIT"))
        filas.append([texto(v(r, "NUMERO Presupuesto")), fecha(v(r, "Fecha de Recepción")),
                      fecha(v(r, "Fecha de Emisión")), cliente, texto(v(r, "REF. DE CLIENTE")),
                      texto(v(r, "DESCRIPCION DEL MATERIAL")), texto(v(r, "PyS")),
                      numero(v(r, "Precio U")), numero(v(r, "Precio Total")), sit, resultado.get(sit, ""),
                      texto(v(r, "Número de OC")), numero(v(r, "Monto de la OC en US$"))])
    escribir("comercial/registro_cotizaciones_2020-2022.csv",
             ["numero", "fecha_recepcion", "fecha_emision", "cliente", "referencia_cliente", "descripcion",
              "familia", "precio_unitario_usd", "precio_total_usd", "situacion", "resultado", "orden_compra",
              "monto_oc_usd"], filas)


def ventas_equipos():
    hoja = xlrd.open_workbook(ORIGEN / F_REMITOS).sheets()[0]
    filas, cliente, fch, oc = [], "", "", ""
    for r in range(hoja.nrows):
        crudo = hoja.row_values(r)
        vals = [texto(x) for x in crudo if texto(x)]
        if not vals:
            continue
        if len(vals) == 2 and re.fullmatch(r"\d{4}", vals[0]):
            cliente = vals[1]
        elif vals[0] == "Fecha:":
            fch = xlrd.xldate_as_datetime(float(vals[1]), 0).date().isoformat()
        elif vals[0] == "Ord.Cpra.:":
            oc = vals[1]
        else:
            nums = [x for x in crudo if isinstance(x, float)]
            if len(vals) >= 5 and len(nums) >= 2 and vals[0] not in ("Cód.Artículo", "Desde Fecha:", "Total:"):
                filas.append([fch, cliente, oc, vals[0], vals[1], nums[-3] if len(nums) >= 3 else 1,
                              nums[-2], nums[-1]])
    escribir("comercial/ventas_2022-2023.csv",
             ["fecha", "cliente", "orden_compra", "codigo_articulo", "descripcion", "cantidad",
              "precio_unitario_usd", "importe_usd"], filas)


def plazos_proyectos():
    """Plazo comprometido vs. real por proyecto. Fecha de OC: hoja de proyectos o, si falta, histórico de
    ventas (por OP). Entrega real: lista de entregados del Resumen o fecha programada ya cumplida."""
    wb = openpyxl.load_workbook(ORIGEN / F_SEGUIMIENTO, data_only=True)
    dia = lambda v: v.date() if isinstance(v, datetime) else None
    historico = {}
    ws = wb["Historico de ventas"]
    for r in range(4, ws.max_row + 1):
        op = texto(ws.cell(r, 11).value)
        if op.isdigit() and op not in historico:
            historico[op] = (dia(ws.cell(r, 13).value), texto(ws.cell(r, 8).value))
    entregas = {}
    ws = wb["Resumen"]
    for r in range(11, 60):
        m = re.match(r"\s*(\d{4})", texto(ws.cell(r, 2).value))
        f = dia(ws.cell(r, 3).value)
        if m and f:
            entregas.setdefault(m.group(1), []).append(f)
    filas, vistos = [], set()
    ws = wb["Proyectos en general x fecha "]
    for r in range(5, ws.max_row + 1):
        op, desc = texto(ws.cell(r, 2).value), texto(ws.cell(r, 14).value)
        if not op.isdigit() or not desc or (op, desc) in vistos:
            continue
        vistos.add((op, desc))
        oc_hist, proyecto = historico.get(op, (None, ""))
        oc = dia(ws.cell(r, 4).value) or oc_hist
        comprometida = dia(ws.cell(r, 15).value)
        programada = ws.cell(r, 16).value
        estado = "anulado" if "ANULAD" in texto(programada).upper() else ""
        real = min(entregas[op]) if op in entregas else (dia(programada) if isinstance(programada, datetime) else None)
        nota = ""
        if real and comprometida and (comprometida - real).days > 300:  # "entregado" casi un año antes: error de carga
            nota, real = "fecha real con año mal cargado en la fuente; se descarta", None
        if real and not estado:
            estado = "entregado"
        dias = lambda a, b: (b - a).days if a and b else ""
        filas.append([op, proyecto, texto(ws.cell(r, 7).value), desc, familia(desc), numero(ws.cell(r, 8).value),
                      numero(ws.cell(r, 9).value), oc.isoformat() if oc else "",
                      comprometida.isoformat() if comprometida else "", real.isoformat() if real else "",
                      dias(oc, comprometida), dias(oc, real), dias(comprometida, real), estado, nota])
    escribir("comercial/plazos_proyectos.csv",
             ["op", "proyecto", "cliente", "descripcion", "familia", "cantidad", "monto_oc_usd", "fecha_oc",
              "entrega_comprometida", "entrega_real", "plazo_comprometido_dias", "plazo_real_dias",
              "atraso_dias", "estado", "nota"], filas)


def costo_planta():
    """Costo de mano de obra propia por centro de costo (oct-2024): sueldos, prorrateo de improductivos,
    indirectos y costo hora. Base: 200 horas por mes."""
    wb = openpyxl.load_workbook(ORIGEN / F_COSTO_PLANTA, data_only=True)
    ws = wb["Reparto"]
    filas = []
    for r in range(3, 12):
        centro = texto(ws.cell(r, 1).value)
        if not centro:
            continue
        valores = [numero(ws.cell(r, c).value) for c in (2, 4, 6, 7, 8, 11, 13)]
        filas.append([centro] + [round(v, 2) if v is not None else "" for v in valores])
    escribir("costos/costo_hora_planta.csv",
             ["centro_costo", "personas", "sueldos_mes_usd", "costo_con_prorrateo_usd", "indirectos_usd",
              "costo_mo_mes_usd", "costo_hora_centro_usd", "costo_hora_persona_usd"], filas)
    sueldos = []
    for row in wb["Sueldos"].iter_rows(min_row=2, values_only=True):
        if row[0] and row[4]:
            sueldos.append([texto(row[0]), fecha(row[1]), texto(row[4]), texto(row[8]), numero(row[5]),
                            round(numero(row[6]) or 0, 2), numero(row[11])])
    escribir("costos/sueldos_2024-10.csv",
             ["empresa", "fecha", "cuenta", "centro_costo", "importe_ars", "importe_usd", "tipo_cambio"], sueldos)


def plazos_historicos():
    """Histórico de ventas 2019-2024: plazo pedido en la OC y entregas reales por proyecto."""
    ws = openpyxl.load_workbook(ORIGEN / F_SEGUIMIENTO, data_only=True)["Historico de ventas"]
    dia = lambda v: v.date() if isinstance(v, datetime) else None
    proyectos, actual = [], None
    for r in range(4, ws.max_row + 1):
        if texto(ws.cell(r, 9).value):
            actual = {"proyecto": texto(ws.cell(r, 8).value), "cliente": texto(ws.cell(r, 2).value),
                      "desc": texto(ws.cell(r, 9).value), "op": texto(ws.cell(r, 11).value),
                      "cant": numero(ws.cell(r, 12).value), "oc": dia(ws.cell(r, 13).value),
                      "entrega_oc": dia(ws.cell(r, 16).value), "reales": []}
            proyectos.append(actual)
        if actual and dia(ws.cell(r, 20).value):
            actual["reales"].append(dia(ws.cell(r, 20).value))
    filas = []
    for p in proyectos:
        if not (p["oc"] or p["entrega_oc"]):
            continue
        ultima = max(p["reales"]) if p["reales"] else None
        dias = lambda a, b: (b - a).days if a and b and (b - a).days >= 0 else ""
        filas.append([p["proyecto"], p["op"], p["cliente"], p["desc"], familia(p["desc"]), p["cant"],
                      p["oc"].isoformat() if p["oc"] else "", p["entrega_oc"].isoformat() if p["entrega_oc"] else "",
                      ultima.isoformat() if ultima else "", dias(p["oc"], p["entrega_oc"]), dias(p["oc"], ultima)])
    escribir("comercial/plazos_historicos_2019-2024.csv",
             ["proyecto", "op", "cliente", "descripcion", "familia", "cantidad", "fecha_oc", "entrega_segun_oc",
              "ultima_entrega_real", "plazo_pedido_dias", "plazo_real_dias"], filas)


def cotizaciones_recientes():
    """Seguimiento de cotizaciones 2024-2026."""
    ws = openpyxl.load_workbook(ORIGEN / F_SEGUIMIENTO, data_only=True)["Cotizaciones ITTSA"]
    filas = []
    for r in range(5, ws.max_row + 1):
        cliente, ref = texto(ws.cell(r, 1).value), texto(ws.cell(r, 4).value)
        if not cliente or cliente.upper().startswith("SUB TOTAL") or not (ref or ws.cell(r, 7).value):
            continue
        estado = texto(ws.cell(r, 9).value).lower()
        resultado = ("ganada" if estado.startswith("ganad") else "perdida" if estado in ("perdido", "lnc")
                     else "a_enviar" if estado == "a enviar" else "enviada_sin_resultado" if estado == "enviado"
                     else "")
        filas.append([fecha(ws.cell(r, 5).value), cliente, texto(ws.cell(r, 2).value), texto(ws.cell(r, 3).value),
                      ref, familia(ref), numero(ws.cell(r, 7).value), texto(ws.cell(r, 8).value),
                      texto(ws.cell(r, 9).value), resultado, texto(ws.cell(r, 10).value),
                      texto(ws.cell(r, 11).value), numero(ws.cell(r, 12).value), numero(ws.cell(r, 13).value)])
    escribir("comercial/cotizaciones_2024-2026.csv",
             ["fecha_presentacion", "cliente", "ref_interna", "isis", "referencia_cliente", "familia", "monto",
              "moneda", "estado", "resultado", "comentarios", "contacto", "probabilidad_pct", "factor_venta"], filas)


if __name__ == "__main__":
    print(f"Fuentes: {ORIGEN}")
    for paso in (factores_soldadura, perfiles, codificacion, precios_elementos, lista_renar, stock,
                 registro_cotizaciones, ventas_equipos, plazos_proyectos, plazos_historicos, cotizaciones_recientes, costo_planta):
        print(paso.__name__)
        paso()
