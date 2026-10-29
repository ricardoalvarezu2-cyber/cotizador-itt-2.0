"""Prepara web/datos.json: todo lo que necesita la página del cotizador (catálogos, índices, tarifas, tablas técnicas,
clientes, plantillas de oferta). Se corre después de actualizar la base y antes de publicar la página.

Uso: python web/construir_datos.py

No incluye sueldos ni costos internos de planta: solo precios y tarifas para cotizar (la página puede compartirse).
Las plantillas de oferta salen de plantillas/oferta_itt_2026.docx con el mismo recorte que herramientas/generar_oferta.py:
se deja la introducción, una marca {{CUERPO}} y el cierre (notas y firma en la económica; firma en la técnica). La página
completa los textos e inserta el cuerpo en la marca.
"""
import base64
import copy
import csv
import io
import json
import re
import sys
from datetime import date
from pathlib import Path

import docx
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "herramientas"))
from catalogo_materiales import FAMILIAS  # noqa: E402

C = RAIZ / "conocimiento"
I_TABLA_REV, I_RECUADRO, I_FIN_INTRO, I_NOTAS, I_FIRMA = 4, 8, 29, 88, 102


def leer(p):
    return list(csv.DictReader(open(p, encoding="utf-8")))


def f(v):
    try:
        return round(float(v), 4)
    except (TypeError, ValueError):
        return None


def plantilla(tipo):
    d = docx.Document(str(RAIZ / "plantillas" / "oferta_itt_2026.docx"))
    body = d.element.body
    el = list(body)
    hasta = I_NOTAS if tipo == "economica" else I_FIRMA
    ancla = el[hasta]
    for e in el[I_FIN_INTRO + 1:hasta]:
        body.remove(e)
    p = OxmlElement("w:p")
    r = OxmlElement("w:r")
    t = OxmlElement("w:t")
    t.text = "{{CUERPO}}"
    r.append(t)
    p.append(r)
    ancla.addprevious(p)
    b = io.BytesIO()
    d.save(b)
    return base64.b64encode(b.getvalue()).decode()


def logo():
    """Logo del encabezado de la plantilla (image3), achicado para el informe y el PDF de las ofertas."""
    import zipfile
    from PIL import Image
    z = zipfile.ZipFile(RAIZ / "plantillas" / "oferta_itt_2026.docx")
    im = Image.open(io.BytesIO(z.read("word/media/image3.jpeg"))).convert("RGB")
    im.thumbnail((640, 200))
    b = io.BytesIO()
    im.save(b, "JPEG", quality=85)
    return "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()


def modelo_titulo():
    d = docx.Document(str(RAIZ / "plantillas" / "oferta_itt_2026.docx"))
    from lxml import etree
    return etree.tostring(copy.deepcopy(list(d.element.body)[57])).decode()


def indices():
    return [{"mes": r["mes"][:7], "ipc": f(r["ipc_argentina"]), "dolar": f(r["dolar_bna"]), "local": f(r["indice_local_usd"]), "cpi": f(r["cpi_eeuu"]),
             "oi": r["origen_ipc"], "od": r["origen_dolar"], "oc": r["origen_cpi"]} for r in leer(C / "costos" / "indices_ajuste.csv")]


def dolar():
    return leer(C / "costos" / "dolar_mensual.csv")[-12:]


def antecedentes():
    """Índice de proyectos 2025–2026 y las constantes de buscar_antecedentes.py, para comparar en la página (paso P8)."""
    import indice_proyectos as ip
    import buscar_antecedentes as ba
    filas = []
    for r in leer(C / "comercial" / "indice_proyectos.csv"):
        rep = None
        ficha = RAIZ / r["ficha"] if r["ficha"].endswith(".json") else None
        if ficha and ficha.exists():
            d = json.load(open(ficha, encoding="utf-8")).get("desglose_costo") or {}
            m, mo, te = (d.get("materiales") or 0), (d.get("mano_obra") or 0), (d.get("terceros") or 0)
            if m + mo + te:
                rep = round(m / (m + mo + te), 3)
        filas.append({"id": r["id"], "fe": r["fecha"], "cl": r["cliente"], "clf": r["cliente_final"], "fam": r["familia"], "tags": r["etiquetas"],
                      "d": r["descripcion"][:200], "of": r["numero_oferta"], "dia": r["diametros"], "ser": r["series"], "mat": r["material"], "un": r["union"],
                      "pu": f(r["precio_unitario_principal"]), "mon": r["moneda"], "fac": r["factor"], "plazo": r["plazo_dias"], "res": r["resultado"],
                      "pl": bool(r["tiene_planilla_costo"]), "prov": r["proveedores"], "oc": bool(r["tiene_oc"]), "conf": r["confianza"], "w": r["palabras"], "rep": rep})
    return {"proyectos": filas, "claves": ip.CLAVES, "familias": ip.FAMILIAS, "vacias": sorted(ip.VACIAS), "cortas": sorted(ip.CORTAS), "tamanos": ba.TAMANOS}


def pesos_tablas():
    """Tablas de pesos para la ficha de la página (web/src/ficha.js, espejo de controles_tablas.peso_item). Compactas: listas."""
    T = C / "tecnico"
    bri = [[r["tipo"], f(r["dn_pulg"]), r["serie"], f(r["peso_kg"])] for r in leer(T / "bridas_peso.csv") if "no usar" not in r["nota"]]
    acc = [[r["tipo"], f(r["dn_pulg"]), f(r["dn2_pulg"]) if r["dn2_pulg"] else None, r["schedule_o_clase"], r["extremos"], f(r["peso_kg"]),
            1 if r["nota"].startswith("ATENCION") else 0, r["norma"]]
           for nombre in ("accesorios_peso.csv", "accesorios_peso_complemento.csv") for r in leer(T / nombre)
           if "no sirve" not in r["nota"] and r["peso_kg"]]
    olets = [[r["tipo"], f(r["dn_salida_pulg"]), r["schedule_o_clase"], f(r["peso_kg"])] for r in leer(T / "olets_peso.csv") if r["configuracion"] == "reducing"]
    esp = {"var": {}, "tue": {}}
    for r in leer(T / "esparragos_peso.csv"):
        if r["tipo"] == "varilla_por_pulgada":
            esp["var"][r["diametro_pulg"]] = f(r["peso_unidad_kg"])
        elif r["tipo"] == "tuerca_heavy_hex_2H":
            esp["tue"][r["diametro_pulg"]] = f(r["peso_unidad_kg"])
    valv = [[r["tipo"], f(r["dn_pulg"]), r["serie"], r["material"], f(r["kg"]), 1 if r["nota"].startswith("pesa menos") else 0, r["hoja"], r["celda"]]
            for r in leer(T / "valvulas_peso.csv")]
    perf = {re.sub(r"\s", "", r["designacion"].lower()): [f(r["kg_por_m"]), f(r["m2_por_m"]) if r["m2_por_m"] else 0] for r in leer(T / "perfiles.csv")}
    return {"bridas": bri, "acc": acc, "olets": olets, "esp": esp, "valv": valv, "perfiles": perf}


def main():
    mats = []
    for r in leer(C / "precios" / "catalogo_materiales.csv"):
        fam = next((k for k, v in FAMILIAS.items() if v[0] == r["familia"]), "OTR")
        at = {k: r[k] for k in ("tipo", "diametro", "diametro2", "serie", "schedule", "material", "trim", "extremos", "marca", "modelo",
                               "cara", "medida", "largo_mm", "espesor_mm", "costura", "revestimiento", "rango", "conexion", "designacion") if r.get(k)}
        mats.append({"c": r["codigo"], "f": fam, "d": r["descripcion"], "u": r["unidad"], "p": f(r["ultimo_precio_usd"]), "pa": f(r["precio_ajustado_hoy_usd"]),
                     "fe": r["fecha_ultimo_precio"], "tp": r["tipo_precio"], "pr": r["proveedor"],
                     "o": (r["ruta_origen"] + (" · " + r["archivo_origen"] if r["archivo_origen"] else ""))[:240],
                     "al": r["alerta"], "iva": r["iva"], "rd": f(r["referencia_descartada_usd"]), "rf": r["fecha_referencia_descartada"],
                     "n": int(r["precios_en_historial"] or 1), "mn": f(r["precio_min_usd"]), "mx": f(r["precio_max_usd"]), "a": at})
    srv = []
    for r in leer(C / "precios" / "catalogo_servicios.csv"):
        if r["hoja"] == "MO propia" and "sueldo" in (r["servicio"] + r["descripcion"]).lower():
            continue  # los sueldos no van a la página
        srv.append({"c": r["codigo"], "h": r["hoja"], "s": r["servicio"], "d": r["descripcion"][:300], "u": r["unidad"],
                    "p": f(r["ultimo_precio_usd"]), "pa": f(r["precio_ajustado_hoy_usd"]), "t": f(r["tarifa_unitaria_usd"]), "ut": r["unidad_tarifa"],
                    "ta": f(r["tarifa_ajustada_hoy_usd"]), "fe": r["fecha_ultimo_precio"], "pr": r["proveedor"],
                    "o": (r["ruta_origen"] + (" · " + r["archivo_origen"] if r["archivo_origen"] else ""))[:240], "inc": r["incluye"][:200],
                    "ninc": r["no_incluye"][:200], "eq": r["equipo_referencia"][:120], "al": r["alerta"], "iva": r["iva"]})
    idx = indices()
    dol = dolar()
    tar = [{"rubro": r["rubro"], "concepto": r["concepto"], "unidad": r["unidad"], "valor": r["valor_usd"], "tipo": r["tipo"], "fecha": r["fecha"],
            "fuente": r["fuente"], "nota": r["nota"]} for r in leer(C / "costos" / "tarifas.csv")
           if r["vigente"] == "si" and r["rubro"] in ("soldadura", "end", "pintura", "hora_hombre")]
    fs = [{"dn": f(r["dn_pulg"]), "od": f(r["diam_ext_mm"]), "sch": r["schedule"], "cl": r["clase"], "e": f(r["espesor_mm"]), "fe": f(r["factor_espesor"]),
           "pch": f(r["placas_rx_chicas"]), "pgr": f(r["placas_rx_grandes"])} for r in leer(C / "tecnico" / "factores_soldadura.csv")]
    canos = [{"dn": f(r["dn_pulg"]), "sch": r["schedule"], "cl": r["clase"], "kg": f(r["kg_m_carbono"]), "m2": f(r["m2_m_exterior"]), "l": f(r["litros_m_interior"])}
             for r in leer(C / "tecnico" / "canos_peso_superficie.csv")]
    acc = [{"a": r["accesorio"], "f": f(r["factor"])} for r in leer(C / "tecnico" / "factores_accesorios.csv")]
    pesos = pesos_tablas()
    clientes = [{"c": r["codigo"], "n": r["razon_social"]} for r in leer(C / "comercial" / "clientes.csv") if r["estado"].lower().startswith("activ")]
    fam = {k: {"n": v[0], "cols": v[1], "clave": v[2]} for k, v in FAMILIAS.items()}
    ant = antecedentes()
    datos = {
        "generado": date.today().isoformat(),
        "materiales": mats, "servicios": srv, "indices": idx, "dolar": dol, "tarifas": tar, "soldadura": fs, "canos": canos,
        "accesorios": acc, "pesos": pesos, "clientes": clientes, "familias": fam, "antecedentes": ant,
        "plantilla_cotizacion": json.load(open(RAIZ / "cotizaciones" / "_plantilla" / "cotizacion.json", encoding="utf-8")),
        "plantilla_oferta": json.load(open(RAIZ / "cotizaciones" / "_plantilla" / "oferta.json", encoding="utf-8")),
        "logo": logo(),
        "docx_tecnica": plantilla("tecnica"), "docx_economica": plantilla("economica"), "docx_titulo": modelo_titulo(),
    }
    salida = RAIZ / "web" / "datos.json"
    salida.write_text(json.dumps(datos, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"{salida.relative_to(RAIZ)}: {salida.stat().st_size / 1e6:.2f} MB · {len(mats)} materiales · {len(srv)} servicios · {len(idx)} meses de índices")


if __name__ == "__main__":
    main()
