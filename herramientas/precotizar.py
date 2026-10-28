"""Precotización automática (sin IA) desde la tabla del plano.

Uso: python herramientas/precotizar.py cotizaciones/<carpeta> [--comparar]

Lee <carpeta>/pedido/lista_materiales_plano.csv y arma <carpeta>/cotizacion_auto.json + <carpeta>/precotizacion.md:
1. Materiales: cada renglón del plano se busca en el catálogo (misma lógica que buscar_material.py). Se toma el IGUAL con
   precio; si no hay, el SIMILAR más parecido con precio, con su diferencia; si no hay ninguno, el renglón queda en 0 con
   "SIN PRECIO: pedir cotización". Fuente, fecha y origen salen del catálogo. Precios sin IVA.
2. Soldaduras: de la columna de extremos, junta por junta. Los extremos BW se juntan de a dos (una junta = dos extremos);
   cada extremo SW es una junta; la cupla, media cupla u olet BW/SW es una junta sobre el caño con el factor de
   factores_accesorios.csv (1,75; weldolet 2,5). Pulgadas equivalentes = DN × factor de espesor (factores_soldadura.csv).
   La columna opcional `extremos_campo` (por unidad) dice cuántos extremos BW quedan abiertos para soldar en campo o con
   la línea del cliente: no suman soldadura de taller. Sin esa columna se avisa que hay que confirmarlo en el dibujo.
   Tarifa: costo propio de planta vigente de costos/tarifas.csv.
3. Servicios calculados: pintura (m² exteriores de caños y niples × última tarifa USD/m² del catálogo de servicios),
   prueba hidráulica (volumen; precio del último global del catálogo, como similar) y radiografía si `parametros.rx_pct` > 0
   (placas por junta de factores_soldadura.csv × tarifas de Antonelli).
Lo que no se puede calcular (armado, ingeniería y calidad, embalaje, flete) queda listado "a completar".

La IA o una persona solo revisa lo que el informe marca: similares, sin precio, estimados y extremos de campo.
Para usarla: revisar precotizacion.md y copiar cotizacion_auto.json a cotizacion.json (o pasar los ítems a mano).
"""
import argparse
import csv
import json
import math
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from buscar_material import buscar  # noqa: E402
from catalogo_materiales import unidad_norm  # noqa: E402
from indice_proyectos import frac, norm  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
TEC = RAIZ / "conocimiento" / "tecnico"
TIPO = {"lista": "lista", "compra": "stock", "stock (precio maestro)": "stock", "cotización": "cot", "planilla interna": "ant",
        "estimado (cepo)": "est"}
SERIES = {"150", "300", "600", "900", "1500", "2500", "2000", "3000", "6000", "9000"}
SCHEDULES = {"5", "10", "20", "30", "40", "60", "80", "100", "120", "140", "160", "STD", "XS", "XXS"}
OLETS = r"cupla|sockolet|threadolet|weldolet|elbowlet|latrolet|\bolet"


def leer(p):
    return list(csv.DictReader(open(p, encoding="utf-8"))) if p.exists() else []


def dn_de(txt):
    m = re.findall(r"(\d+\s\d/\d|\d+/\d+|\d+(?:[.,]\d+)?)", str(txt).replace('"', " "))
    try:
        return frac(m[0].replace(",", ".")) if m else None
    except (ValueError, ZeroDivisionError):
        return None


def sch_de(v):
    for p in re.split(r"[xX/ ]", str(v).upper()):
        if p in SCHEDULES:
            return p
    return ""


def serie_de(v):
    return next((p for p in re.split(r"[x/ ]", str(v)) if p in SERIES), "")


def largo_m(desc):
    m = re.search(r"(\d[\d.]*)\s?mm", norm(desc))
    return float(m.group(1).replace(".", "")) / 1000 if m else None


def texto_busqueda(r):
    partes = [r["descripcion"], r["diametro"]]
    sr, sc = serie_de(r["serie_sch"]), sch_de(r["serie_sch"])
    if sr:
        partes.append(f"#{sr}")
    if sc:
        partes.append(f"sch {sc}")
    partes += [r["material"], r["extremos"].replace("-M", "").replace("-H", ""), r.get("modelo_fabricante", "")]
    return " ".join(p for p in partes if p)


def material(r, n):
    """Ítem de cotizacion.json para un renglón del plano, más el renglón del informe."""
    fam, at, _, faltan, res = buscar(texto_busqueda(r))
    cant, unidad = float(r["cantidad"] or 0), (r["unidad"] or "un").strip()
    l = largo_m(r["descripcion"])
    if fam == "CAN" and unidad_norm(unidad) == "un" and l:
        cant, unidad = round(cant * l, 3), "m"  # "caño longitud 1900 mm × 1" se compra por metro
    con_precio = [x for x in res if x[7]["ultimo_precio_usd"]]
    # orden: igual con precio real > similar con precio real > igual estimado (cepo) > similar estimado
    real = [x for x in con_precio if x[7]["tipo_precio"] != "estimado (cepo)"]
    est = [x for x in con_precio if x[7]["tipo_precio"] == "estimado (cepo)"]
    orden = [x for x in real if x[0]] + [x for x in real if not x[0]] + [x for x in est if x[0]] + [x for x in est if not x[0]]
    elegido = orden[0] if orden else None
    item = {"id": f"M{n:02d}", "pos": r["pos"], "grupo": "material",
            "descripcion": f"{r['descripcion'][:60]} {r['diametro']}".strip(), "cantidad": cant, "unidad": unidad,
            "especificacion": f"Plano: {r['diametro']} · {r['serie_sch']} · {r['material']} · {r['extremos']}" + (f" · {r['modelo_fabricante']}" if r.get("modelo_fabricante") else "")}
    if not elegido:
        item["fuentes"] = [{"tipo": "est", "precio": 0, "proveedor": "SIN PRECIO EN EL CATÁLOGO: pedir cotización", "origen": "—",
                            "fecha": date.today().isoformat(), "coincide": "sin_ref", "diferencia": "No hay pieza de esa familia y tipo con precio"}]
        return item, f"| {r['pos']} | {item['descripcion'][:45]} | **SIN PRECIO** | — | — | pedir cotización |"
    igual, _, _, _, _, _, difs, c = elegido
    precio = float(c["ultimo_precio_usd"])
    nota_u = ""
    uc, up = unidad_norm(c["unidad"]), unidad_norm(unidad)
    m = re.fullmatch(r"tira de (\d+) m", uc)
    if m and up == "m":
        precio, nota_u = precio / float(m.group(1)), f"precio de tira de {m.group(1)} m pasado a metro"
    elif uc and up and uc != up:
        nota_u = f"unidad distinta: catálogo por {uc}, plano por {up}"
    coincide = "igual" if igual and not nota_u.startswith("unidad distinta") else "similar"
    dif = "; ".join(difs + ([nota_u] if nota_u else []))
    tipo = TIPO.get(c["tipo_precio"], "ant")
    item["fuentes"] = [{"tipo": tipo, "precio": round(precio, 4), "proveedor": f"{c['proveedor'][:70]} · {c['codigo']}",
                        "origen": (c["ruta_origen"] + (" · " + c["archivo_origen"] if c["archivo_origen"] else ""))[:200],
                        "fecha": c["fecha_ultimo_precio"], "coincide": coincide, **({"diferencia": dif} if coincide == "similar" else {})}]
    estado = "IGUAL" if coincide == "igual" else "SIMILAR"
    if tipo == "est":
        estado += " (estimado cepo)"
    if c.get("alerta"):
        estado += " ⚠"
    fila = (f"| {r['pos']} | {item['descripcion'][:45]} | {estado} | {precio:,.2f} / {unidad} | {c['fecha_ultimo_precio']} · {c['tipo_precio']} | "
            f"{(dif or '—')[:110]}{' · faltan: ' + ', '.join(faltan) if faltan else ''} |")
    return item, fila


def factor_espesor(dn, sch, tabla):
    sch = sch or "40"
    for r in tabla:
        if dn is not None and abs(float(r["dn_pulg"]) - dn) < 1e-6 and (r["schedule"] == sch or r["clase"] == sch):
            return float(r["factor_espesor"]), float(r["placas_rx_chicas"] or 0), float(r["placas_rx_grandes"] or 0)
    return 1.0, 0.0, 0.0


def soldaduras(filas):
    tabla = leer(TEC / "factores_soldadura.csv")
    fac_acc = {norm(r["accesorio"]): float(r["factor"]) for r in leer(TEC / "factores_accesorios.csv")}
    bw_eq, juntas_olet, juntas_sw, detalle, placas = 0.0, 0.0, 0.0, [], [0.0, 0.0]
    extremos_bw = 0
    hay_campo = any("extremos_campo" in r for r in filas)
    for r in filas:
        ext = r["extremos"].upper().replace("-M", "").replace("-H", "")
        toks = [t.strip() for t in re.split(r"[/]", ext) if t.strip()]
        d = norm(r["descripcion"])
        if len(toks) == 1:
            n_ext = 3 if re.search(r"\btee\b|\bte\b", d) else (1 if re.search(r"casquete|\bcap\b|brida|" + OLETS, d) else 2)
            toks = toks * n_ext
        n_bw, n_sw = toks.count("BW"), toks.count("SW")
        if not (n_bw or n_sw):
            continue
        q = float(r["cantidad"] or 0)
        dn, sch = dn_de(r["diametro"]), sch_de(r["serie_sch"])
        f, pch, pgr = factor_espesor(dn, sch, tabla)
        if re.search(OLETS, d):
            fa = 2.5 if "weldolet" in d else fac_acc.get("sockolets", 1.75)
            juntas_olet += (n_bw + n_sw) * q * (dn or 0) * fa
            detalle.append(f"pos {r['pos']}: {int((n_bw + n_sw) * q)} junta(s) de {r['descripcion'][:25]} sobre caño × {dn:g}\" × {fa} = {(n_bw + n_sw) * q * dn * fa:.2f}")
            continue
        campo = float(r.get("extremos_campo") or 0)
        bw_taller = max(0.0, n_bw - campo) * q
        extremos_bw += bw_taller
        bw_eq += bw_taller * (dn or 0) * f
        juntas_sw += n_sw * q * (dn or 0) * f
        placas[0] += bw_taller / 2 * pch
        placas[1] += bw_taller / 2 * pgr
        if n_bw:
            detalle.append(f"pos {r['pos']}: {bw_taller:g} extremo(s) BW de taller ({n_bw:g} por unidad × {q:g}{f' − {campo:g} de campo por unidad' if campo else ''}) × {dn:g}\" × {f:.4f}")
        if n_sw:
            detalle.append(f"pos {r['pos']}: {n_sw * q:g} junta(s) SW × {dn:g}\" × {f:.4f}")
    juntas_bw = extremos_bw / 2
    total = bw_eq / 2 + juntas_sw + juntas_olet
    avisos = []
    if extremos_bw % 2:
        avisos.append(f"Quedan {extremos_bw:g} extremos BW de taller (número impar): falta marcar algún extremo de campo o una pieza")
    if not hay_campo and extremos_bw:
        avisos.append("La tabla no tiene la columna extremos_campo: se supuso que TODOS los extremos BW se sueldan en taller. Confirmar en el dibujo cuáles quedan para campo")
    return {"juntas_bw": juntas_bw, "pulg_eq": round(total, 3), "detalle": detalle, "avisos": avisos, "placas": placas}


def tarifa(rubro, texto, tipos=("costo_propio",)):
    for r in leer(RAIZ / "conocimiento" / "costos" / "tarifas.csv"):
        if r["rubro"] == rubro and texto in norm(r["concepto"]) and r["tipo"] in tipos and r["vigente"] == "si":
            return float(r["valor_usd"]), r
    return None, None


def servicio_catalogo(hoja, unidad, palabras):
    mejor = None
    for r in leer(RAIZ / "conocimiento" / "precios" / "catalogo_servicios.csv"):
        if r["hoja"].startswith(hoja) and r["ultimo_precio_usd"] and "ESTIMADO" not in r["alerta"] and \
                (unidad is None or r["unidad_tarifa"] == unidad) and all(p in norm(r["servicio"] + " " + r["descripcion"]) for p in palabras):
            if mejor is None or r["fecha_ultimo_precio"] > mejor["fecha_ultimo_precio"]:
                mejor = r
    return mejor


def main(carpeta, comparar=False):
    carpeta = Path(carpeta)
    filas = leer(carpeta / "pedido" / "lista_materiales_plano.csv")
    if not filas:
        sys.exit(f"No está {carpeta}/pedido/lista_materiales_plano.csv")
    base_ruta = carpeta / "cotizacion.json" if (carpeta / "cotizacion.json").exists() else RAIZ / "cotizaciones" / "_plantilla" / "cotizacion.json"
    base = json.load(open(base_ruta, encoding="utf-8"))
    hoy = base.get("parametros", {}).get("fecha_referencia", "")
    items, informe = [], [f"# Precotización automática — {base.get('codigo', carpeta.name)}", "",
                          "Generada por `herramientas/precotizar.py`, sin IA. **Borrador: revisar los SIMILAR, SIN PRECIO, estimados y ⚠ antes de usarla.**", "",
                          "## 1. Materiales", "", "| Pos | Ítem | Resultado | Precio | Fecha y tipo | Diferencias / faltantes |", "|---|---|---|---|---|---|"]
    for n, r in enumerate(filas, 1):
        it, fila = material(r, n)
        items.append(it)
        informe.append(fila)
    # 2. soldaduras
    s = soldaduras(filas)
    tar, fila_t = tarifa("soldadura", "soldadura piping")
    informe += ["", "## 2. Soldaduras (de la columna de extremos)", "",
                f"**{s['juntas_bw']:g} juntas a tope de taller + juntas SW y olets = {s['pulg_eq']:.2f} pulgadas equivalentes**"
                + (f" × USD {tar:.2f} (costo propio de planta {fila_t['fecha']}) = USD {s['pulg_eq'] * tar:,.2f}" if tar else ""), ""]
    informe += [f"- {d}" for d in s["detalle"]] + [f"- ⚠ {a}" for a in s["avisos"]]
    if s["pulg_eq"] and tar:
        items.append({"id": "S01", "pos": "MO", "grupo": "mo", "descripcion": f"Soldaduras: {s['juntas_bw']:g} a tope + SW y olets (calculado)",
                      "especificacion": "; ".join(s["detalle"])[:400], "cantidad": s["pulg_eq"], "unidad": "pulg",
                      "fuentes": [{"tipo": "ant", "precio": tar, "proveedor": f"Costo propio de planta: {fila_t['nota']}", "origen": fila_t["fuente"],
                                   "fecha": fila_t["fecha"] if len(fila_t["fecha"]) > 7 else fila_t["fecha"] + "-31", "coincide": "igual" if not s["avisos"] else "similar",
                                   **({"diferencia": " · ".join(s["avisos"])} if s["avisos"] else {})}]})
    # 3. servicios calculados
    canos = leer(TEC / "canos_peso_superficie.csv")
    m2, litros = 0.0, 0.0
    for r in filas:
        if not re.search(r"\bcano\b|\bniple|\btubo\b", norm(r["descripcion"])):
            continue
        dn, sch = dn_de(r["diametro"]), sch_de(r["serie_sch"]) or "40"
        fila = next((c for c in canos if abs(float(c["dn_pulg"]) - (dn or -1)) < 1e-6 and (c["schedule"] == sch or c["clase"] == sch)), None)
        l = largo_m(r["descripcion"]) or (float(r["cantidad"]) if norm(r["unidad"]).startswith("m") else None)
        if fila and l:
            q = float(r["cantidad"]) if not norm(r["unidad"]).startswith("m") else 1
            m2 += float(fila["m2_m_exterior"]) * l * q
            litros += float(fila["litros_m_interior"]) * l * q
    informe += ["", "## 3. Servicios calculados", ""]
    pin = servicio_catalogo("Pintura", "USD/m2", ["granallado", "pintura"])
    if pin and m2:
        t = float(pin["tarifa_unitaria_usd"])
        informe.append(f"- **Pintura:** {m2:.2f} m² de caños y niples × USD {t:.2f}/m² ({pin['servicio'][:50]}, {pin['proveedor'][:30]}, {pin['fecha_ultimo_precio']}) = USD {m2 * t:,.2f}. No incluye accesorios ni válvulas: sumarlos si se pintan.")
        items.append({"id": "S02", "pos": "PIN", "grupo": "servicio", "descripcion": "Granallado y pintura (m² calculados de caños y niples)",
                      "especificacion": f"{m2:.2f} m² exteriores (tabla ASME B36.10)", "cantidad": round(max(m2, 0.01), 3), "unidad": "m2",
                      "fuentes": [{"tipo": "ant", "precio": round(t, 4), "proveedor": f"{pin['proveedor'][:60]} · {pin['codigo']}", "origen": pin["ruta_origen"][:200],
                                   "fecha": pin["fecha_ultimo_precio"], "coincide": "similar", "diferencia": "m² solo de caños y niples; esquema de pintura a confirmar con el pliego"}]})
    # prueba hidráulica: las planillas 2025–2026 la cobran por hora de planta; horas = parametros.ph_horas (supuesto 6 h)
    ph = servicio_catalogo("Ensayos", "USD/hora", ["hidr"])
    horas = float(base.get("parametros", {}).get("ph_horas", 0) or 0)
    supuesto = not horas
    horas = horas or 6
    if ph:
        t = float(ph["tarifa_unitaria_usd"] or ph["ultimo_precio_usd"])
        informe.append(f"- **Prueba hidráulica:** {horas:g} h × USD {t:.2f}/h ({ph['servicio'][:40]}, {ph['fecha_ultimo_precio']}) = USD {horas * t:,.2f}"
                       + (" · ⚠ horas supuestas: cargar `parametros.ph_horas`" if supuesto else "") + f" · volumen interior de caños y niples {litros:.1f} l.")
        items.append({"id": "S03", "pos": "PH", "grupo": "servicio", "descripcion": "Prueba hidráulica (horas de planta)",
                      "especificacion": f"{horas:g} h · volumen interior {litros:.1f} l", "cantidad": horas, "unidad": "h",
                      "fuentes": [{"tipo": "ant", "precio": t, "proveedor": f"{ph['proveedor'][:60]} · {ph['codigo']}", "origen": ph["ruta_origen"][:200],
                                   "fecha": ph["fecha_ultimo_precio"], "coincide": "similar" if supuesto else "igual",
                                   **({"diferencia": "horas supuestas (6 h): confirmar"} if supuesto else {})}]})
    rx = float(base.get("parametros", {}).get("rx_pct", 0) or 0)
    if rx > 0 and s["juntas_bw"]:
        pch, pgr = (math.ceil(p * rx / 100) for p in s["placas"])
        t_ch, f_ch = tarifa("end", "placa radiografica chica", ("tercero",))
        t_gr, _ = tarifa("end", "placa radiografica grande", ("tercero",))
        t_sv, _ = tarifa("end", "servicio de radiografia (antonelli)", ("tercero",))
        servs = max(1, math.ceil((pch + pgr) / 40))
        costo = pch * (t_ch or 0) + pgr * (t_gr or 0) + servs * (t_sv or 0)
        informe.append(f"- **Radiografía {rx:g}%:** {pch} placas chicas + {pgr} grandes + {servs} servicio(s) = USD {costo:,.2f} (Antonelli {f_ch['fecha'] if f_ch else ''}).")
        items.append({"id": "S04", "pos": "RX", "grupo": "servicio", "descripcion": f"Radiografía {rx:g}% de las juntas a tope",
                      "especificacion": f"{pch} placas chicas, {pgr} grandes, {servs} servicio(s)", "cantidad": 1, "unidad": "gl",
                      "fuentes": [{"tipo": "cot", "precio": round(costo, 2), "proveedor": "NDT Antonelli (tarifas nov-2025)", "origen": "fuentes_originales/antonelli_end_2025-11.pdf",
                                   "fecha": "2025-11-03", "coincide": "igual"}]})
    else:
        informe.append("- **Radiografía:** no se calculó (`parametros.rx_pct` = 0). Si el pliego la pide, cargar el porcentaje y volver a correr.")
    informe += ["", "## 4. A completar (no se puede calcular)", "",
                "- Armado y montaje (mano de obra de armado roscado o de terceros con el mismo alcance: `buscar_servicio.py`).",
                "- Ingeniería, calidad y dossier · embalaje · flete (kilos en `controles_tablas.md` al armar) · insumos.",
                "- Plazo (camino crítico con `comercial/plazos_proveedores.csv`)."]
    total_mat = sum(i["cantidad"] * i["fuentes"][0]["precio"] for i in items if i["grupo"] == "material")
    total_srv = sum(i["cantidad"] * i["fuentes"][0]["precio"] for i in items if i["grupo"] != "material")
    sin = [i["pos"] for i in items if i["fuentes"][0]["precio"] == 0]
    sim = [i["pos"] for i in items if i["grupo"] == "material" and i["fuentes"][0]["coincide"] == "similar"]
    informe[3:3] = [f"**Resumen:** materiales USD {total_mat:,.2f} por equipo · soldadura y servicios calculados USD {total_srv:,.2f} · "
                    f"{len(sim)} similares ({', '.join(sim) or '—'}) · {len(sin)} sin precio ({', '.join(sin) or '—'}).", ""]
    if comparar and (carpeta / "cotizacion.json").exists():
        man = {i["pos"]: i for i in json.load(open(carpeta / "cotizacion.json", encoding="utf-8"))["items"]}
        informe += ["", "## 5. Comparación con cotizacion.json (armada a mano)", "", "| Pos | Automático | A mano | Diferencia |", "|---|---|---|---|"]
        for i in items:
            m = man.get(i["pos"])
            if m:
                a, b = i["cantidad"] * i["fuentes"][0]["precio"], m["cantidad"] * m["fuentes"][0]["precio"]
                informe.append(f"| {i['pos']} | {a:,.2f} | {b:,.2f} | {a - b:+,.2f} |")
        tm = sum(m["cantidad"] * m["fuentes"][0]["precio"] for m in man.values() if m["grupo"] == "material")
        informe.append(f"| **Materiales** | **{total_mat:,.2f}** | **{tm:,.2f}** | **{total_mat - tm:+,.2f}** |")
    auto = {**base, "items": items, "estado": "borrador",
            "nota_precotizacion": "Generado por precotizar.py: revisar precotizacion.md antes de usarlo como cotizacion.json"}
    json.dump(auto, open(carpeta / "cotizacion_auto.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    (carpeta / "precotizacion.md").write_text("\n".join(informe) + "\n", encoding="utf-8")
    print(informe[3])
    print(f"→ {carpeta / 'cotizacion_auto.json'} y {carpeta / 'precotizacion.md'}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("carpeta")
    ap.add_argument("--comparar", action="store_true", help="comparar con el cotizacion.json armado a mano")
    q = ap.parse_args()
    main(q.carpeta, q.comparar)
