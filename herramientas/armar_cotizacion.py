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
  plazo_calculado.md     acopio + taller sin superponer, margen y comparación con el plazo real (plazo.py)
  ficha_rubros.md/.json  ficha por rubro (MO piping, estructura, pintura, END, transporte) para el modo global (ficha_rubros.py)
  comparacion_antecedentes.md  precio contra los 5 antecedentes más parecidos (comparar_antecedentes.py, paso P8)
  verificacion_origen.md      avisos de precios que no figuran en su documento de origen (verificar_origen.py; solo avisa)
  frenos                 pendientes antes de enviar (herramientas/frenos.py); solo avisan, desde el 30-10-2026: plazo, transcripción
                         doble, matriz de requisitos, estimado > 15%, antecedentes, cotizaciones vencidas
  <codigo>_<...>.xlsx    planilla con fórmulas: Planilla ITT, Resumen, Materiales, MO y servicios, Antecedentes y desvíos,
                         Índices (planilla_excel.py)
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

sys.path.insert(0, str(Path(__file__).resolve().parent))
from candado import perfil_soffice  # noqa: E402
from numeros import FMT_TECNICO, a_vista, celda_excel, fmt, fmtg, precio_csv  # noqa: E402
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

RAIZ = Path(__file__).resolve().parent.parent
INDICES = RAIZ / "conocimiento" / "costos" / "indices_ajuste.csv"
PLANTILLA_INFORME = RAIZ / "plantillas" / "informe_cotizacion.html"
TIPOS = {"cot": "cotización", "lista": "lista", "stock": "stock", "ant": "antecedente", "est": "estimado"}
MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]


def sin_html(t):
    return html.unescape(re.sub(r"<[^>]+>", "", str(t)))


def filas_indices(cfg=None):
    """Filas de la tabla de índices. Si la cotización tiene "indices_congelados" (se congelan al pasar a revisado, para que
    el precio no cambie solo cuando se publica un mes nuevo), se usan esos; si no, la tabla vigente de la base."""
    cg = (cfg or {}).get("indices_congelados")
    if cg:
        return [{"mes": r["mes"][:7] + "-01", "ipc_argentina": r["ipc"], "dolar_bna": r["dolar"], "indice_local_usd": r["local"],
                 "cpi_eeuu": r["cpi"], "origen_ipc": r.get("oi", ""), "origen_dolar": r.get("od", ""), "origen_cpi": r.get("oc", "")}
                for r in cg["filas"]]
    return list(csv.DictReader(open(INDICES, encoding="utf-8")))


def leer_indices(cfg=None):
    return [(r["mes"][:7], float(r["indice_local_usd"]), float(r["cpi_eeuu"])) for r in filas_indices(cfg)]


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


def es_taval(it):
    """Válvula Taval (empresa del grupo): lleva su propio factor de venta, FTV (por defecto 1; decisión de Matías, 28-10-2026)."""
    return it["grupo"] == "material" and bool(it.get("taval"))


def calcular(cfg, idx):
    p = cfg["parametros"]
    fref = p["fecha_referencia"][:7]
    ftv = p.get("FTV", 1.0)
    sub = {"material": 0.0, "mo": 0.0, "servicio": 0.0, "taval": 0.0}
    for it in cfg["items"]:
        sub["taval" if es_taval(it) else it["grupo"]] += it["cantidad"] * it["fuentes"][0]["precio"] * factor(it, idx, fref, p["AJ"])
    cont = sub["material"] * p["CONT"] / 100
    tav = sub["taval"] * (1 + p["CONT"] / 100)  # válvulas Taval con su contingencia
    costo = sub["material"] + cont + tav + sub["mo"] + sub["servicio"]
    precio = round((sub["material"] + cont) * p["FM"] + tav * ftv + (sub["mo"] + sub["servicio"]) * p["FMO"], 2)
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
            w.writerow([it["id"], it["pos"], it["descripcion"], f"{it['cantidad']:.4f}".rstrip("0").rstrip("."), it["unidad"], precio_csv(s["precio"]),
                        f"{it['cantidad'] * s['precio']:.2f}", TIPOS[s["tipo"]], s["proveedor"], s["origen"], s["fecha"],
                        s.get("coincide", ""), s.get("diferencia", "")])


# ---------------------------------------------------------------- planilla
def escribir_planilla(cfg, carpeta, idx_rows):
    """Planilla con fórmulas (diseño en planilla_excel.py; rediseño del 05-11-2026)."""
    import planilla_excel
    return planilla_excel.escribir(cfg, carpeta, idx_rows)


def leer_planilla(ruta):
    import planilla_excel
    v = planilla_excel.leer_valores(ruta)
    return {"costo": v["CostoUnitario"], "precio_unitario": v["PrecioUnitario"], "total": v["TotalOferta"]}


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
        if es_taval(it):
            o["tv"] = 1
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
    ante = "\n".join(f'      <tr><td>{a["carpeta_html"]}</td><td class="mono">{e(a_vista(a["fecha"]))}</td><td>{a["que"]}</td><td class="n">{a["precio"]}</td><td>{a["tomado_html"]}</td></tr>'
                     for a in cfg.get("antecedentes", []))
    pend = "\n".join(f'    <div class="bloque"><h3>{e(b["titulo"])}</h3><ol class="lista small">\n' + "\n".join(f"      <li>{x}</li>" for x in b["items"]) + "\n    </ol></div>"
                     for b in cfg.get("pendientes", []))
    dias = cfg["plazo"]["dias"]
    ticks = "".join(f"<span>{round(dias * k / 4)}</span>" for k in range(5))
    params = {"FTV": 1.0, **{k: v for k, v in p.items() if k != "fecha_referencia"}}
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
    idx_rows = filas_indices(cfg)
    idx = leer_indices(cfg)
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
    print(f"Python : costo {fmt(py['costo'], 2)} · precio unitario {fmt(py['precio_unitario'], 2)} · total {fmt(py['total'], 2)}")
    print(f"Planilla: costo {fmt(xl['costo'], 2)} · precio unitario {fmt(xl['precio_unitario'], 2)} · total {fmt(xl['total'], 2)}")
    if any(abs(py[k] - xl[k]) > 0.011 for k in py):
        sys.exit("ERROR: el cálculo en Python y la planilla no coinciden. Revisar antes de seguir.")
    import verificar_computo
    if verificar_computo.main(carpeta) not in (0, 2):  # 2: solo desvíos a confirmar en un borrador (no frena el armado)
        sys.exit("ERROR: verificar_computo.py encontró errores.")
    import controles_tablas
    controles_tablas.main(carpeta)  # kilos y m², plazos de material y marcas del cliente → controles_tablas.md
    import plazo
    plazo.main(carpeta)  # camino crítico sin superponer y margen de la regla → plazo_calculado.md
    import ficha_rubros
    ficha_rubros.main(carpeta)  # datos por rubro para un precio global (soldaduras, kg, m², placas, medidas) → ficha_rubros.md
    import comparar_antecedentes
    comparar_antecedentes.main(carpeta, py["precio_unitario"], py["costo"])  # P8 → comparacion_antecedentes.md
    import verificar_origen
    verificar_origen.main(carpeta)  # aviso de precio que no figura en su documento de origen → verificacion_origen.md
    import frenos
    lista_frenos = frenos.frenos(carpeta, recalcular=False)  # pendientes antes de enviar (plazo, transcripción, requisitos, estimado, etc.)
    # Desde el 30-10-2026 (Matías) son avisos, no frenos: las ofertas se generan igual (en borrador) y la aprobación la
    # decide el usuario sin restricción.
    if lista_frenos:
        print(f"PENDIENTES ANTES DE ENVIAR ({len(lista_frenos)}, no impiden generar ni aprobar):")
        for k, t in lista_frenos:
            print(f"  · [{k}] {t}")
    if (carpeta / "oferta.json").exists():
        import generar_oferta
        generar_oferta.main(carpeta, frenos_revisados=True)
    import indice_proyectos
    indice_proyectos.main()  # la cotización queda en el índice de antecedentes
    print(f"\nListo: {carpeta}/computo.csv, {ruta.name}, informe.html" + (", oferta/" if (carpeta / "oferta.json").exists() else ""))
    print(f"Estado: {cfg['estado']}. Recordar: revisión independiente y aprobación antes de enviar (procedimiento P9).")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    from candado import candado
    with candado("armar_cotizacion.py"):
        main(sys.argv[1])
