"""Catálogo de mano de obra y servicios de ITT (etapa 1): armado determinístico a partir de la extracción leída por IA.

Uso: python herramientas/catalogo_servicios.py

Entrada (extracción verificada en los originales, un renglón por precio):
  conocimiento/precios/servicios_extraidos.csv
Salidas:
  conocimiento/precios/catalogo_servicios_historial.csv   un renglón por precio, con su estado (vigente / descartado)
  conocimiento/precios/catalogo_servicios.csv             un renglón por servicio: último precio confiable + historial
  conocimiento/precios/catalogo_servicios.xlsx            8 hojas por rubro + "Todos"
  conocimiento/precios/catalogo_servicios_codigos.csv     registro de códigos estables (clave -> código)
Se busca con herramientas/buscar_servicio.py.

Reglas (instrucciones del 27/10/2026 y cambio de regla del 28/10/2026):
- Siempre SIN IVA: con IVA se divide por 1,21 o 1,105; si el documento no dice, se toma sin IVA.
- Números y fechas con numeros.py (fecha de mes solamente "AAAA-MM" se acepta como está; nunca se inventa una fecha).
- Pesos a USD con el promedio mensual del dólar oficial BNA venta (indices_ajuste.csv, dolar_bna), salvo que el documento
  tenga su propio tipo de cambio (columna tc_documento: solo informativa, el precio ya viene en USD).
- Ajuste a hoy con indice_local_usd (costo local en USD), no con el CPI de EE.UU.
- Solo se juntan precios del mismo servicio, misma unidad de tarifa y alcance comparable. Los globales de distinto equipo no se juntan.
- CEPO (decisión de Matías 28/10/2026): un valor en USD con fecha anterior al 14/04/2025 cuyo documento NO dice con qué tipo de
  cambio se calculó NO se usa como precio. Queda en el historial con la nota "descartado: período con cepo, dólar sin aclarar".
  El último precio es el último valor confiable (posterior al 14/04/2025, o anterior pero con tipo de cambio explícito, o en
  pesos con fecha). Si no queda ninguno, el renglón queda sin último precio y con la alerta "sin precio confiable: pedir
  cotización"; el valor descartado se muestra solo como referencia.
"""
import csv
import re
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from catalogo_materiales import factor_cepo, en_mes, iva_de, unidad_norm  # noqa: E402
from indice_proyectos import norm  # noqa: E402
from numeros import fecha_iso, leer_numero, fmt, fmtg, precio_csv, celda_excel  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
PRECIOS = RAIZ / "conocimiento" / "precios"
Z = "Z:\\VENTAS\\OFERTAS Y LICITACIONES\\"
FIN_CEPO = "2025-04-14"
NOTA_CEPO = "descartado: período con cepo, dólar sin aclarar"

HOJAS = [("MOP", "MO propia"), ("FAB", "Fabricación y armado (terceros)"), ("SOL", "Soldadura y piping"), ("END", "Ensayos y END"),
         ("PIN", "Pintura y revestimientos"), ("TRA", "Transporte e izaje"), ("ING", "Ingeniería, calidad e inspección"), ("OTR", "Otros servicios")]
COD_DE = {n: c for c, n in HOJAS}

COMUNES = ["codigo", "hoja", "servicio", "descripcion", "unidad", "ultimo_precio_usd", "iva", "fecha_ultimo_precio", "proveedor", "ruta_origen", "archivo_origen",
           "ruta_repo", "precio_ajustado_hoy_usd", "tarifa_unitaria_usd", "unidad_tarifa", "tarifa_ajustada_hoy_usd", "alcance_comparable", "incluye", "no_incluye",
           "lugar", "equipo_referencia", "precios_en_historial", "precio_min_usd", "precio_max_usd", "alerta", "confianza", "referencia_descartada_usd",
           "fecha_referencia_descartada", "nota"]

UNIDAD_MAGNITUD = {"pulg": "pulg-eq", "pulgada": "pulg-eq", "pulgadas": "pulg-eq", "pulg-eq": "pulg-eq", "pulg-diam": "pulg-eq", "pulg-diam-eq": "pulg-eq",
                   "kg": "kg", "placa": "placa", "placas": "placa", "dia": "dia", "dias": "dia", "hora": "hora", "horas": "hora", "m2": "m2", "documento": "documento",
                   "documentos": "documento", "carretel": "carretel", "carreteles": "carretel", "skid": "skid", "skids": "skid", "viaje": "viaje", "visita": "visita",
                   "procedimiento": "procedimiento", "unidad": "unidad"}
# tarifas que no pueden ser un total sin que algo esté mal (alerta de "total tomado como unitario / pesos como USD")
TOPE = {"USD/pulg-eq": 200, "USD/kg": 100, "USD/hora": 500, "USD/m2": 500, "USD/placa": 200, "USD/dia": 8000, "USD/persona-mes": 20000, "USD/documento": 5000}


# ---------------------------------------------------------------- tablas de tipo de cambio y de ajuste
def tabla_ajuste():
    """{mes: (dolar_bna, indice_local_usd)} de indices_ajuste.csv."""
    ruta = RAIZ / "conocimiento" / "costos" / "indices_ajuste.csv"
    return {r["mes"][:7]: (float(r["dolar_bna"]), float(r["indice_local_usd"])) for r in csv.DictReader(open(ruta, encoding="utf-8"))}


def fecha_valida(f, hoy=None):
    """AAAA-MM-DD (por numeros.fecha_iso) o AAAA-MM (solo mes); "" si no hay fecha válida. Nunca una fecha por defecto."""
    f = (f or "").strip()
    if not f:
        return ""
    hoy = hoy or date.today()
    if re.fullmatch(r"\d{4}", f):  # solo el año (planillas viejas): sirve para el corte del cepo, no para ajustar
        return f if 2000 <= int(f) <= hoy.year else ""
    m = re.fullmatch(r"(\d{4})-(\d{2})", f)
    if m:
        a, me = int(m.group(1)), int(m.group(2))
        return f if 1 <= me <= 12 and 2000 <= a <= hoy.year and (a, me) <= (hoy.year, hoy.month) else ""
    return fecha_iso(f, hoy)


def clave_fecha(f):
    """Para ordenar: un mes sin día se ordena a mitad de mes y un año solo a mitad de año (solo orden; no se muestra ni se usa para ajustar)."""
    if re.fullmatch(r"\d{4}", f or ""):
        return f + "-07-01"
    return f + "-15" if re.fullmatch(r"\d{4}-\d{2}", f or "") else (f or "")


def precio_sin_iva(r):
    """(precio sin IVA en la moneda original, texto del IVA, alerta)."""
    s = norm(r["iva_origen"])
    precio = float(r["precio"])
    alerta = ""
    if "con iva" in s:
        alic = 1.105 if re.search(r"10[.,]5", s) else 1.21
        iva = f"con IVA: dividido por {alic:.3f}".replace(".", ",")
        return precio / alic, iva, alerta
    iva = r["iva_origen"].strip() or "no dice: se toma sin IVA"
    if iva_de(r["texto_original"])[1] != 1.0 and not ("sin iva" in s or "mas iva" in s):
        alerta = "la cita parece decir que el precio lleva IVA: revisar"
    return precio, iva, alerta


def magnitud_de(txt):
    """'770 kg' -> (770.0, 'kg'); '' -> (None, '')."""
    m = re.match(r"\s*(\d[\d.,]*)\s*(\S*)", txt or "")
    if not m:
        return None, ""
    v, _ = leer_numero(m.group(1))
    u = norm(m.group(2)).strip(" .")
    return v, UNIDAD_MAGNITUD.get(u, unidad_norm(u) or u)


def numero_ambiguo(r):
    """Alerta si el precio sale de un número de la cita escrito '27,200' (4.500 vs 4500)."""
    precio = float(r["precio"])
    for tok in re.findall(r"\d[\d.,]*\d|\d", r["texto_original"]):
        v, amb = leer_numero(tok)
        if amb and v is not None and abs(v * 1000 - precio) < 0.5:
            return f"número ambiguo en el origen ('{tok}' leído como {fmtg(precio)}, no como {fmtg(v)}): verificar"
    return ""


# ---------------------------------------------------------------- carga
def leer_extraccion():
    tabla = tabla_ajuste()
    ref = tabla[max(tabla)][1]
    regs = []
    # etapa 1 (cotizaciones de proveedores y tarifas) + etapa 2 (planillas de costo, armado por unir_planillas_costo.py)
    entradas = [(PRECIOS / "servicios_extraidos.csv", "")]
    if (PRECIOS / "servicios_desde_planillas.csv").exists():
        entradas.append((PRECIOS / "servicios_desde_planillas.csv", "P"))
    filas_in = [(f"{pre}{i}", r) for ruta, pre in entradas for i, r in enumerate(csv.DictReader(open(ruta, encoding="utf-8")), 2)]
    for i, r in filas_in:
        if not r["precio"].strip():
            continue
        if str(i).startswith("P"):  # planillas de costo: texto de Excel, el punto es decimal ("131.131" = 131,13)
            precio, ambiguo = float(r["precio"]), False
        else:
            precio, ambiguo = leer_numero(r["precio"])
        if precio is None or precio <= 0:
            continue
        r = {**r, "precio": precio}
        fecha = fecha_valida(r["fecha"])
        precio_sin, iva, alerta_iva = precio_sin_iva(r)
        notas, alertas = [], []
        if alerta_iva:
            alertas.append(alerta_iva)
        if ambiguo or numero_ambiguo(r):
            alertas.append(numero_ambiguo(r) or "número ambiguo en el origen")
        moneda = (r["moneda"] or "USD").upper()
        usd = None
        if moneda.startswith("ARS") or moneda == "$":
            if fecha:
                tc, viejo = en_mes(tabla, fecha, 0) if not re.fullmatch(r"\d{4}", fecha) else (None, None)
                if tc is None:
                    raise ValueError("pesos con fecha de solo año: no se puede convertir")
                usd = precio_sin / tc
                notas.append(f"convertido de ARS a USD con dólar BNA {fmt(tc, 2)}" + (" (fecha anterior a la tabla)" if viejo else ""))
        else:
            usd = precio_sin
        # tarifa unitaria: precio ÷ magnitud (el precio está en USD/algo o es global con magnitud)
        cant, um = magnitud_de(r["magnitud"])
        u = r["unidad"].strip()
        tarifa_u = ""
        if u.upper().startswith("USD/"):
            tarifa_u = u
        elif cant and um:
            tarifa_u = f"USD/{um}"
        tarifa = None
        if usd is not None and tarifa_u:
            tarifa = usd if u.upper().startswith("USD/") else usd / cant
        # cepo
        sin_tc = not r["tc_documento"].strip()
        descartado = bool(moneda == "USD" and fecha and fecha < FIN_CEPO and sin_tc)
        if moneda == "USD" and fecha and fecha < FIN_CEPO and not sin_tc:
            notas.append(f"anterior al 14/04/2025 pero con tipo de cambio en el documento ({r['tc_documento'].strip()}): se usa")
        if descartado:
            notas.append(NOTA_CEPO)
        if not fecha:
            alertas.append("sin fecha válida en el origen")
        if r["confianza"].strip().lower() == "baja":
            alertas.append("confianza baja en la lectura del origen")
        aj = None
        factor = None
        solo_anio = bool(re.fullmatch(r"\d{4}", fecha))
        if solo_anio:
            notas.append("fecha solo con año: sin ajuste a hoy")
        if usd is not None and fecha and not solo_anio:
            idx, viejo = en_mes(tabla, fecha, 1)
            factor = ref / idx
            aj = usd * factor
            if viejo:
                notas.append("ajuste parcial: fecha anterior a ene-2024")
        if usd is None:
            alertas.append("no se puede pasar a USD (pesos sin fecha)")
        regs.append(dict(r, _linea=i, fecha=fecha, usd=usd, usd_aj=aj, tarifa=tarifa, tarifa_aj=(tarifa * factor if tarifa is not None and factor else None),
                         tarifa_u=tarifa_u, cant=cant, um=um, iva=iva, descartado=descartado, notas=notas, alertas=alertas, moneda=moneda))
    return regs


def clave_de(r):
    if r["tarifa_u"]:
        return f"{r['hoja']}|{norm(r['servicio'])}|{r['tarifa_u']}"
    return f"{r['hoja']}|{norm(r['servicio'])}|global|{norm(r['equipo_referencia'])}|{norm(r['carpeta_origen'])}"


def rutas(r):
    c, a = r["carpeta_origen"], r["archivo_origen"]
    if c == "FUENTE":
        return f"fuentes_originales/{a}", a, f"fuentes_originales/{a}"
    if c == "REPO":
        return a, "tarifas.csv", a
    return Z + c.replace("/", "\\"), a, f"fuentes_originales/ofertas_texto/{c}/{a}.txt"


# ---------------------------------------------------------------- armado
def main():
    regs = leer_extraccion()
    grupos = defaultdict(list)
    for r in regs:
        r["clave"] = clave_de(r)
        grupos[r["clave"]].append(r)
    # códigos estables
    reg_ruta = PRECIOS / "catalogo_servicios_codigos.csv"
    registro = {x["clave"]: x["codigo"] for x in csv.DictReader(open(reg_ruta, encoding="utf-8"))} if reg_ruta.exists() else {}
    ultimo = max([int(c.split("-")[1]) for c in registro.values()] or [0])
    for k in sorted(grupos, key=lambda k: (COD_DE[grupos[k][0]["hoja"]], k)):
        if k not in registro:
            ultimo += 1
            registro[k] = f"{COD_DE[grupos[k][0]['hoja']]}-{ultimo:05d}"
    with open(reg_ruta, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["codigo", "clave"])
        for k, c in sorted(registro.items(), key=lambda kv: kv[1]):
            w.writerow([c, k])
    filas, hist = [], []
    for k, hs in sorted(grupos.items(), key=lambda kv: registro[kv[0]]):
        cod = registro[k]
        hs.sort(key=lambda h: (clave_fecha(h["fecha"]), h["usd"] or 0, h["_linea"]), reverse=True)
        base = hs[0]
        unit = bool(base["tarifa_u"])
        valor = (lambda h: h["tarifa"]) if unit else (lambda h: h["usd"])
        valor_aj = (lambda h: h["tarifa_aj"]) if unit else (lambda h: h["usd_aj"])
        confiables = [h for h in hs if h["usd"] is not None and not h["descartado"]]
        alertas = []
        if not confiables:  # valor verosímil para los del cepo (decisión de Matías, 28/10/2026): × oficial ÷ blue del mes
            for h in hs:
                f, txt = factor_cepo(h["fecha"]) if h["descartado"] and h["usd"] is not None else (None, "")
                if f:
                    confiables.append({**h, "usd": h["usd"] * f, "usd_aj": h["usd_aj"] * f if h["usd_aj"] is not None else None,
                                       "tarifa": h["tarifa"] * f if h["tarifa"] is not None else None,
                                       "tarifa_aj": h["tarifa_aj"] * f if h["tarifa_aj"] is not None else None,
                                       "descartado": False, "notas": h["notas"] + [f"ESTIMADO: {txt}; valor original USD {fmt(h['usd'], 2)}"],
                                       "alertas": h["alertas"] + [f"ESTIMADO: valor del período con cepo {txt}; pedir cotización"]})
        fechados = [h for h in confiables if h["fecha"]]
        usable = (fechados or confiables)
        ultimo_h = usable[0] if usable else None
        if ultimo_h:
            u = ultimo_h
            vals = [valor(h) for h in confiables if valor(h)]
            if vals and max(vals) > 3 * min(vals):
                alertas.append(f"historial disperso (>3×): {fmt(min(vals), 2)} a {fmt(max(vals), 2)}: revisar")
            alertas += u["alertas"]
            tu = u["tarifa_u"]
            if tu in TOPE and valor(u) and valor(u) > TOPE[tu]:
                alertas.append(f"{fmt(valor(u), 2)} {tu}: ¿total tomado como unitario o pesos tomados como dólares?")
            if len(vals) >= 3:
                med = sorted(vals)[len(vals) // 2]
                if valor(u) > 20 * med:
                    alertas.append(f"{fmt(valor(u) / med, 0)} veces la mediana del historial: ¿total como unitario o pesos como USD?")
                elif valor(u) < med / 20:
                    alertas.append(f"1/{fmt(med / valor(u), 0)} de la mediana del historial: ¿precio mal leído?")
            if not fechados:
                alertas.append("ningún precio con fecha: el último no se puede ordenar")
        else:
            alertas.append("sin precio confiable: pedir cotización")
        desc = [h for h in hs if h["descartado"]]
        ref_h = desc[0] if (not ultimo_h and desc) else None
        if desc and ultimo_h:
            alertas.append(f"{len(desc)} valor(es) descartado(s) por cepo en el historial")
        src = ultimo_h or ref_h or base
        ro, ar, rr = rutas(src)
        precios = [valor(h) for h in confiables if valor(h) is not None]
        fl = {"codigo": cod, "hoja": base["hoja"], "servicio": base["servicio"], "descripcion": (src["descripcion"] or "")[:260],
              "unidad": src["tarifa_u"] if unit else "global",
              "ultimo_precio_usd": round(valor(ultimo_h), 2) if ultimo_h else "", "iva": src["iva"],
              "fecha_ultimo_precio": ultimo_h["fecha"] if ultimo_h else "", "proveedor": (ultimo_h or src)["proveedor"],
              "ruta_origen": ro, "archivo_origen": ar, "ruta_repo": rr,
              "precio_ajustado_hoy_usd": round(valor_aj(ultimo_h), 2) if ultimo_h and valor_aj(ultimo_h) is not None else "",
              "tarifa_unitaria_usd": round(ultimo_h["tarifa"], 2) if ultimo_h and ultimo_h["tarifa"] is not None else "",
              "unidad_tarifa": src["tarifa_u"],
              "tarifa_ajustada_hoy_usd": round(ultimo_h["tarifa_aj"], 2) if ultimo_h and ultimo_h["tarifa_aj"] is not None else "",
              "alcance_comparable": "sí" if (ultimo_h and ultimo_h["tarifa"] is not None) else "no",
              "incluye": src["incluye"], "no_incluye": src["no_incluye"], "lugar": src["lugar"], "equipo_referencia": src["equipo_referencia"],
              "precios_en_historial": len(hs), "precio_min_usd": round(min(precios), 2) if precios else "", "precio_max_usd": round(max(precios), 2) if precios else "",
              "alerta": "; ".join(dict.fromkeys(alertas)), "confianza": src["confianza"],
              "referencia_descartada_usd": round(valor(ref_h), 2) if ref_h and valor(ref_h) is not None else "",
              "fecha_referencia_descartada": ref_h["fecha"] if ref_h else "",
              "nota": "; ".join(dict.fromkeys(src["notas"] + ([src["nota"]] if src["nota"] else [])))}
        filas.append(fl)
        for h in hs:
            ro2, ar2, rr2 = rutas(h)
            estado = "descartado (cepo)" if h["descartado"] else ("vigente" if h is ultimo_h else "anterior")
            if h["usd"] is None:
                estado = "sin conversión a USD"
            hist.append([cod, base["hoja"], k, h["fecha"], round(valor(h), 2) if valor(h) is not None else "", h["moneda"], precio_csv(h["precio"]), h["iva"],
                         round(h["usd"], 2) if h["usd"] is not None else "", round(valor_aj(h), 2) if valor_aj(h) is not None else "",
                         h["tarifa_u"] if unit else "global", estado, h["proveedor"], h["descripcion"], h["equipo_referencia"], ro2, ar2, rr2,
                         h["texto_original"], h["confianza"], "; ".join(h["notas"] + h["alertas"] + ([h["nota"]] if h["nota"] else []))])
    # CSV
    with open(PRECIOS / "catalogo_servicios_historial.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["codigo", "hoja", "clave", "fecha", "valor_usd", "moneda_origen", "precio_origen", "iva", "precio_total_usd", "valor_ajustado_hoy_usd", "unidad",
                    "estado", "proveedor", "descripcion", "equipo_referencia", "ruta_origen", "archivo_origen", "ruta_repo", "texto_original", "confianza", "nota"])
        for h in sorted(hist, key=lambda x: (x[0], clave_fecha(x[3]), x[4] if x[4] != "" else 0)):
            w.writerow(h)
    with open(PRECIOS / "catalogo_servicios.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(COMUNES)
        for fl in filas:
            w.writerow([fl[c] for c in COMUNES])
    escribir_excel(filas)
    resumen(filas, regs)


def resumen(filas, regs):
    from collections import Counter
    print(f"{len(regs)} precios extraídos → {len(filas)} servicios distintos")
    c = Counter(fl["hoja"] for fl in filas)
    for _, n in HOJAS:
        sub = [fl for fl in filas if fl["hoja"] == n]
        print(f"  {n:36} {c.get(n, 0):4} servicios · con tarifa unitaria {sum(1 for x in sub if x['alcance_comparable'] == 'sí'):3} · con alerta {sum(1 for x in sub if x['alerta']):3}")
    print(f"con tarifa unitaria: {sum(1 for fl in filas if fl['alcance_comparable'] == 'sí')} · con alerta: {sum(1 for fl in filas if fl['alerta'])} · sin precio confiable: "
          f"{sum(1 for fl in filas if fl['ultimo_precio_usd'] == '')} · descartados por cepo (precios): {sum(1 for r in regs if r['descartado'])}")


def nombre_hoja_excel(n):
    """Excel admite 31 caracteres: 'Ingeniería, calidad e inspección' (32) pasa a 'Ingeniería, calidad, inspección'."""
    return n.replace("calidad e inspección", "calidad, inspección")


def escribir_excel(filas):
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    H = Font(bold=True, color="FFFFFF")
    HF = PatternFill("solid", fgColor="1D5F86")
    wb = Workbook()
    wb.remove(wb.active)
    ancho = {"descripcion": 60, "ruta_origen": 50, "archivo_origen": 40, "ruta_repo": 45, "proveedor": 30, "nota": 50, "alerta": 45, "servicio": 38,
             "incluye": 40, "no_incluye": 40, "equipo_referencia": 36}

    def hoja(nombre, rows):
        ws = wb.create_sheet(re.sub(r"[/\\?*\[\]:]", "-", nombre_hoja_excel(nombre))[:31])
        for j, c in enumerate(COMUNES, 1):
            x = ws.cell(1, j, c.replace("_", " "))
            x.font = H
            x.fill = HF
            x.alignment = Alignment(wrap_text=True, vertical="center")
            ws.column_dimensions[x.column_letter].width = ancho.get(c, 14)
        for i, fl in enumerate(rows, 2):
            for j, c in enumerate(COMUNES, 1):
                celda_excel(ws.cell(i, j), fl[c], c)
        ws.freeze_panes = "C2"
        ws.auto_filter.ref = ws.dimensions
    hoja("Todos", filas)
    for _, n in HOJAS:
        hoja(n, [fl for fl in filas if fl["hoja"] == n])
    wb.save(PRECIOS / "catalogo_servicios.xlsx")


if __name__ == "__main__":
    main()
