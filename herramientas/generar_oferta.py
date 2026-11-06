"""Genera la oferta técnica y la oferta económica de ITT en Word (y PDF) con el formato vigente.

Uso: python herramientas/generar_oferta.py cotizaciones/<carpeta>

Lee <carpeta>/oferta.json (textos, desvíos, condiciones) y toma los precios de la planilla de la
cotización (<carpeta>/*.xlsx, celdas con nombre del Resumen), recalculada con LibreOffice. Los precios nunca se
escriben a mano en el JSON (procedimiento P7).
Plantilla: plantillas/oferta_itt_2026.docx (ver plantillas/README.md).

Mientras la cotización no esté aprobada (estado distinto de "aprobado"), el documento lleva la marca
"BORRADOR – SIN REVISAR – NO ENVIAR" en el encabezado.
"""
import copy
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import docx
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor
from openpyxl import load_workbook

sys.path.insert(0, str(Path(__file__).resolve().parent))
from candado import perfil_soffice  # noqa: E402
from numeros import a_vista, fmt, fmtg  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
PLANTILLA = RAIZ / "plantillas" / "oferta_itt_2026.docx"
AZUL = RGBColor(0x00, 0x20, 0x60)
ROJO = RGBColor(0xC0, 0x00, 0x00)
FUENTE = "Aptos"

# Índices de los elementos del cuerpo de la plantilla (ver plantillas/README.md)
I_TABLA_REV, I_RECUADRO, I_FIN_INTRO, I_NOTAS, I_FIRMA = 4, 8, 29, 88, 102


def completar(cfg, cot):
    """La oferta toma de la cotización lo que ya está cargado (igual que Documentos.completarOferta en la página): plazo y
    revisión siempre de la cotización; cliente, contacto y fecha si en la oferta siguen vacíos o entre [corchetes]."""
    o = json.loads(json.dumps(cfg))
    vacio = lambda v: v is None or not str(v).strip() or re.search(r"\[[^\]]*\]", str(v))
    ok = lambda v: v is not None and str(v).strip() and "[" not in str(v)
    for k in ("oferta", "cliente", "item"):
        o.setdefault(k, {})
    cli = cot.get("cliente", {})
    if vacio(o["cliente"].get("nombre")) and ok(cli.get("nombre")):
        o["cliente"]["nombre"] = cli["nombre"]
    if vacio(o["cliente"].get("contacto")) and ok(cli.get("comprador")):
        o["cliente"]["contacto"] = cli["comprador"]
    if vacio(o["oferta"].get("fecha")) and ok(cot.get("fecha")):
        o["oferta"]["fecha"] = cot["fecha"]
    rv = re.sub(r"^rev\.?\s*", "", str(cot.get("revision", "")), flags=re.I).strip()
    if rv:
        o["oferta"]["revision"] = rv
    d = (cot.get("plazo") or {}).get("dias")
    if d:
        o["item"]["plazo_dias"] = str(d)
        cambia = lambda l: re.sub(r"\[d[ií]as\]", str(d), re.sub(r"^(\[d[ií]as\]|\d+)(?= d[ií]as)", str(d), str(l), flags=re.I), flags=re.I)
        o["condiciones"] = {k: ([cambia(x) for x in v] if isinstance(v, list) else cambia(v)) for k, v in o.get("condiciones", {}).items()}
    return o


def transporte_incluido(cot):
    """Transporte cargado con precio en MO y servicios (ítem global del rubro transporte): va dentro del precio unitario."""
    for it in cot.get("items", []):
        if it.get("global") and it.get("rubro") == "transporte" and float((it.get("fuentes") or [{}])[0].get("precio") or 0) > 0:
            return {"destino": (cot.get("transporte") or {}).get("destino", "")}
    return None


def usd(v):
    return f"USD {fmt(v, 2)}"


def cot_equipo(carpeta):
    c = json.load(open(Path(carpeta) / "cotizacion.json", encoding="utf-8"))
    return c.get("equipo", {}).get("singular", "equipo")


def leer_precios(carpeta):
    """Precios de la planilla recalculada, por las celdas con nombre del Resumen (planilla_excel.py)."""
    import planilla_excel
    xlsx = sorted(Path(carpeta).glob("*.xlsx"))[0]
    v = planilla_excel.leer_valores(xlsx)
    precios = {"cantidad": v["Cantidad"], "precio_unitario": v["PrecioUnitario"], "total": v["TotalOferta"],
               "flete_incluido": v["IncluirFlete"] == 1, "flete": v["Flete"] or 0}
    if abs(precios["precio_unitario"] * precios["cantidad"] + precios["flete"] - precios["total"]) > 0.001:
        sys.exit(f"La planilla no cierra: unitario × cantidad + flete ≠ total ({precios})")
    return precios


def set_texto(p_el, texto):
    """Pone 'texto' en el primer run del párrafo (con su formato) y vacía los demás."""
    ts = list(p_el.iter(qn("w:t")))
    if not ts:
        return
    ts[0].text = texto
    ts[0].set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    for t in ts[1:]:
        t.text = ""


def reemplazar_parrafos(raiz, reemplazos):
    """Reemplaza párrafos (también dentro de cuadros de texto) cuyo texto empieza con una clave."""
    for p in raiz.iter(qn("w:p")):
        if p.find(".//" + qn("w:p")) is not None:  # párrafo que contiene un cuadro de texto: se tratan los internos
            continue
        txt = "".join(t.text or "" for t in p.iter(qn("w:t"))).strip()
        for clave, nuevo in reemplazos.items():
            if txt.startswith(clave):
                set_texto(p, nuevo)
                break


def run(p, texto, negrita=False, tam=10, color=AZUL, italica=False, resaltar=False):
    r = p.add_run(texto)
    r.font.name = FUENTE
    r._element.rPr.rFonts.set(qn("w:hAnsi"), FUENTE)
    r.font.size = Pt(tam)
    r.font.bold = negrita
    r.font.italic = italica
    r.font.color.rgb = color
    if resaltar:
        hl = OxmlElement("w:highlight")
        hl.set(qn("w:val"), "yellow")
        r._element.rPr.append(hl)
    return r


def con_marcadores(p, texto, **kw):
    """Escribe texto y resalta en amarillo lo que esté entre [corchetes] (datos a completar)."""
    import re
    for parte in re.split(r"(\[[^\]]+\])", texto):
        if parte:
            run(p, parte, resaltar=parte.startswith("["), **kw)


class Cuerpo:
    """Inserta contenido antes de un elemento ancla del cuerpo, con el estilo de la plantilla."""

    def __init__(self, doc, ancla, modelo_titulo):
        self.doc, self.ancla, self.modelo_titulo = doc, ancla, modelo_titulo

    def _nuevo_p(self):
        p = self.doc.add_paragraph()
        self.ancla.addprevious(p._element)
        return p

    def salto_pagina(self):
        self._nuevo_p().add_run().add_break(WD_BREAK.PAGE)
        for _ in range(2):  # el logo del encabezado es flotante: bajar el texto para que no lo rodee
            self.espacio()

    def espacio(self):
        self._nuevo_p()

    def titulo(self, texto):
        el = copy.deepcopy(self.modelo_titulo)  # estilo Título 2 numerado de la plantilla
        set_texto(el, texto)
        el.find(qn("w:pPr")).append(OxmlElement("w:keepNext"))  # que el título no quede solo al pie de la página
        self.ancla.addprevious(el)
        self._nuevo_p().paragraph_format.keep_with_next = True

    def texto(self, texto, sangria=0.75, negrita=False, alinear=WD_ALIGN_PARAGRAPH.JUSTIFY):
        p = self._nuevo_p()
        p.paragraph_format.left_indent = Cm(sangria)
        p.paragraph_format.first_line_indent = Cm(0)
        p.alignment = alinear
        p.paragraph_format.space_after = Pt(4)
        con_marcadores(p, texto, negrita=negrita)
        return p

    def vinetas(self, items, sangria=1.25):
        for it in items:
            p = self._nuevo_p()
            p.paragraph_format.left_indent = Cm(sangria)
            p.paragraph_format.first_line_indent = Cm(-0.4)
            p.paragraph_format.space_after = Pt(2)
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            run(p, "•  ")
            con_marcadores(p, it)

    def imagen(self, ruta, ancho_cm):
        p = self._nuevo_p()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(str(ruta), width=Cm(ancho_cm))

    def tabla(self, encabezado, filas, anchos_cm, total=None, tam=9, alinear=None):
        t = self.doc.add_table(rows=1, cols=len(encabezado))
        self.ancla.addprevious(t._element)
        t.alignment = 1
        borde = OxmlElement("w:tblBorders")
        for lado in ("top", "left", "bottom", "right", "insideH", "insideV"):
            b = OxmlElement(f"w:{lado}")
            b.set(qn("w:val"), "single"), b.set(qn("w:sz"), "4"), b.set(qn("w:color"), "002060")
            borde.append(b)
        t._element.tblPr.append(borde)

        def celda(c, texto, cab=False, negrita=False, al=WD_ALIGN_PARAGRAPH.CENTER):
            p = c.paragraphs[0]
            p.alignment = al
            con_marcadores(p, str(texto), negrita=cab or negrita, tam=tam,
                           color=RGBColor(0xFF, 0xFF, 0xFF) if cab else AZUL)
            if cab:
                shd = OxmlElement("w:shd")
                shd.set(qn("w:val"), "clear"), shd.set(qn("w:color"), "auto"), shd.set(qn("w:fill"), "002060")
                c._tc.get_or_add_tcPr().append(shd)
            c.vertical_alignment = 1

        for i, h in enumerate(encabezado):
            celda(t.rows[0].cells[i], h, cab=True)
        for fila in filas:
            cs = t.add_row().cells
            for i, v in enumerate(fila):
                al = (alinear or [WD_ALIGN_PARAGRAPH.CENTER] * len(fila))[i]
                celda(cs[i], v, al=al)
        if total:
            cs = t.add_row().cells
            a = cs[0].merge(cs[len(encabezado) - 3])
            celda(a, total[0], negrita=True)
            celda(cs[len(encabezado) - 2], total[1], negrita=True)
        t.autofit = False
        lay = OxmlElement("w:tblLayout")
        lay.set(qn("w:type"), "fixed")
        t._element.tblPr.append(lay)
        for gc, w in zip(t._element.tblGrid.findall(qn("w:gridCol")), anchos_cm):
            gc.set(qn("w:w"), str(int(w * 567)))
        for fila in t.rows:
            for tc in fila._tr.findall(qn("w:tc")):
                i = list(fila._tr.findall(qn("w:tc"))).index(tc)
                span = tc.tcPr.find(qn("w:gridSpan")) if tc.tcPr is not None else None
                n = int(span.get(qn("w:val"))) if span is not None else 1
                inicio = sum(int(x.tcPr.find(qn("w:gridSpan")).get(qn("w:val"))) if x.tcPr is not None and x.tcPr.find(qn("w:gridSpan")) is not None else 1
                             for x in list(fila._tr.findall(qn("w:tc")))[:i])
                tcw = tc.get_or_add_tcPr().get_or_add_tcW()
                tcw.set(qn("w:w"), str(int(sum(anchos_cm[inicio:inicio + n]) * 567)))
                tcw.set(qn("w:type"), "dxa")
        self.espacio()
        return t


def armar(carpeta, tipo, cfg, precios):
    doc = docx.Document(str(PLANTILLA))
    body = doc.element.body
    el = list(body)
    tabla_rev, recuadro, notas, firma = el[I_TABLA_REV], el[I_RECUADRO], el[I_NOTAS], el[I_FIRMA]
    modelo_titulo = copy.deepcopy(el[57])
    of, cli = cfg["oferta"], cfg["cliente"]
    titulo = "OFERTA TÉCNICA" if tipo == "tecnica" else "OFERTA ECONÓMICA"

    # Tabla de revisiones y recuadro azul (está dos veces: versión nueva y alternativa del cuadro de texto)
    celdas = list(tabla_rev.iter(qn("w:tc")))
    set_texto(celdas[3], of["revision"]), set_texto(celdas[4], a_vista(of["fecha"]))
    set_texto(celdas[5], of["descripcion_revision"])
    espacios = " " * 29
    reemplazar_parrafos(recuadro, {
        "OFERTA ECONÓMICA": titulo,
        "Oferta:": f"Oferta: {of['numero']}{espacios}Revisión {of['revision']}{' ' * 19}Fecha {a_vista(of['fecha'])}",
        "Cliente:": f"Cliente: {cli['nombre']}",
        "Contacto:": f"Contacto: {cli['contacto']}",
        "Referencia:": f"Referencia: {cli['referencia']}",
        "Proyecto:": f"Proyecto: {cli['proyecto']}",
        "ITT S.A.:": f"ITT S.A.: {cfg['firma']['nombre']}",
    })
    reemplazar_parrafos(body, {"Agradecemos su pedido": "Agradecemos su pedido y nos complace presentarles nuestra mejor propuesta "
                               + ("Técnica" if tipo == "tecnica" else "Económica") + " para la provisión de la referencia solicitada."})

    # Firma
    f = cfg["firma"]
    reemplazar_parrafos(firma, {"Lucas Valdez": f["nombre"], "Representante": f["cargo"]})
    for p in firma.iter(qn("w:p")):
        ts = list(p.iter(qn("w:t")))
        txt = "".join(t.text or "" for t in ts)
        for emoji, valor in (("☎", f["telefono"]), ("📱", f["celular"])):
            if txt.startswith(emoji) and len(ts) > 1:
                i = next(k for k, t in enumerate(ts) if not any(ch in (t.text or "") for ch in "☎📱️"))
                ts[i].text = f": {valor}"
                for t in ts[i + 1:]:
                    t.text = ""
    for t in firma.iter(qn("w:t")):
        if "[" in (t.text or ""):
            r = t.getparent()
            rpr = r.find(qn("w:rPr"))
            if rpr is None:
                rpr = OxmlElement("w:rPr")
                r.insert(0, rpr)
            hl = OxmlElement("w:highlight")
            hl.set(qn("w:val"), "yellow")
            rpr.append(hl)

    # Borrar el cuerpo de la plantilla entre la introducción y las notas (o la firma)
    hasta = I_NOTAS if tipo == "economica" else I_FIRMA
    for e in el[I_FIN_INTRO + 1:hasta]:
        body.remove(e)
    ancla = notas if tipo == "economica" else firma
    c = Cuerpo(doc, ancla, modelo_titulo)
    c.salto_pagina()

    obj = cfg["objeto"].replace("{tipo}", "Técnica" if tipo == "tecnica" else "Comercial")
    pres = of["numero"]
    if tipo == "economica":
        c.titulo("OBJETO"); c.texto(obj)
        c.titulo("PRECIO DE LA PROVISIÓN")
        it = cfg["item"]
        c.tabla(["ITEM", "CÓDIGO", "DESCRIPCIÓN", "CANTIDAD", "USD UNIDAD", "USD SUBTOTAL", "Plazo de entrega (días)"],
                [[it["item"], it["codigo"], it["descripcion"], f"{fmtg(precios['cantidad'])}", usd(precios["precio_unitario"]),
                  usd(precios["precio_unitario"] * precios["cantidad"]), it["plazo_dias"]]]
                + ([["", "", cfg.get("descripcion_flete", "Flete y embalaje hasta destino"), "1", usd(precios["flete"]), usd(precios["flete"]), ""]]
                   if precios["flete"] else []),
                [1.3, 3.1, 5.0, 2.1, 2.4, 2.6, 1.9], total=("TOTAL (SIN IVA)", usd(precios["total"])),
                alinear=[1, 1, 0, 1, 1, 1, 1])
        tr = transporte_incluido(cfg.get("_cot", {}))
        if tr:
            c.texto(f"Precio puesto en {tr['destino'] or 'el lugar de entrega acordado'}: el transporte está incluido en el precio unitario.", sangria=0.75)
        elif not precios["flete_incluido"]:
            c.texto(cfg["nota_flete"], sangria=0.75)
        for n, (tit, txt) in enumerate(cfg["condiciones"].items(), 3):
            c.titulo(tit)
            for linea in (txt if isinstance(txt, list) else [txt]):
                c.texto(linea, sangria=1.25)
        c.espacio()
    else:
        c.titulo("OBJETO"); c.texto(obj)
        c.titulo("ALCANCE")
        it = cfg["item"]
        c.tabla(["ITEM", "CANTIDAD", "DESCRIPCIÓN", "OBSERVACIÓN / DESVÍO", "Plazo de entrega (días)"],
                [[it["item"], f"{fmtg(precios['cantidad'])}", it["descripcion"], it["observacion"], it["plazo_dias"]]],
                [1.4, 2.2, 7.2, 4.2, 2.2], alinear=[1, 1, 0, 1, 1])
        c.titulo("EMBALAJE"); c.texto(cfg["embalaje"])
        c.titulo("DOCUMENTOS QUE FORMAN PARTE DE LA PROPUESTA")
        c.vinetas([f"{pres} – OFERTA TÉCNICA", f"{pres} – OFERTA ECONÓMICA"] + cfg.get("documentos_cliente", []))
        c.titulo("CARACTERÍSTICAS GENERALES SEGÚN PLANO")
        c.texto(cfg["caracteristicas"])
        img = Path(carpeta) / cfg.get("imagen_plano", "")
        if cfg.get("imagen_plano") and img.is_file():
            c.imagen(img, 15)
        c.titulo(cfg.get("titulo_materiales") or f"MATERIALES CONSIDERADOS (POR {cot_equipo(carpeta).upper()})")  # título propio si la lista es de ITT
        import csv

        def cant_vista(v):  # el CSV guarda 0.8 (formato de máquina); a la vista va 0,8
            try:
                return fmtg(float(v))
            except (TypeError, ValueError):
                return v
        # descripción tal cual la del cliente; la cantidad que el cliente no indicó lleva (*) y la aclaración (Matías, 29-10-2026)
        lm = list(csv.DictReader(open(Path(carpeta) / "pedido" / "lista_materiales_plano.csv", encoding="utf-8")))
        filas = [[r["pos"], r["descripcion"] + (f" ({r['modelo_fabricante']})" if r["modelo_fabricante"] else ""),
                  r["diametro"], r["serie_sch"], r["material"], r["extremos"], cant_vista(r["cantidad"]) + (" (*)" if r.get("cantidad_origen") else "")]
                 for r in lm]
        c.tabla(["POS", "DESCRIPCIÓN", "Ø", "SERIE / SCH", "MATERIAL", "EXT.", "CANT."], filas,
                [1.0, 7.4, 1.6, 1.6, 3.3, 1.6, 1.1], tam=7.5, alinear=[1, 0, 1, 1, 1, 1, 1])
        sin_cant = [r["pos"] for r in lm if r.get("cantidad_origen")]
        if sin_cant:
            c.texto(f"(*) Pos. {', '.join(sin_cant)}: el cliente no indica cantidad; ITT la calculó según el plano / especificación técnica.")
        for clave in ("aclaraciones_y_desvios", "exclusiones", "alcance_general"):
            c.titulo(cfg[clave]["titulo"]); c.vinetas(cfg[clave]["items"])
        c.titulo("GARANTÍA"); c.texto(cfg["garantia"])
        c.espacio()

    if cfg.get("estado") != "aprobado":
        h = doc.sections[-1].header
        p = h.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        run(p, "BORRADOR – SIN REVISAR – NO ENVIAR", negrita=True, tam=11, color=ROJO)
        for s in doc.sections[:-1]:
            if not s.header.is_linked_to_previous:
                p = s.header.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                run(p, "BORRADOR – SIN REVISAR – NO ENVIAR", negrita=True, tam=11, color=ROJO)
    return doc


def main(carpeta, frenos_revisados=False):
    """frenos_revisados=True: la llama armar_cotizacion.py, que ya corrió los frenos con el cómputo recién armado."""
    carpeta = Path(carpeta)
    cot = json.load(open(carpeta / "cotizacion.json", encoding="utf-8"))
    cfg = completar(json.load(open(carpeta / "oferta.json", encoding="utf-8")), cot)
    cfg["_cot"] = cot
    import frenos
    fr = [] if frenos_revisados else frenos.frenos(carpeta)  # solo avisan (Matías, 30-10-2026): la oferta se genera igual
    if fr:
        print("PENDIENTES ANTES DE ENVIAR (no impiden generar ni aprobar):\n" + "\n".join(f"  · [{k}] {t}" for k, t in fr))
    precios = leer_precios(carpeta)
    salida = carpeta / "oferta"
    salida.mkdir(exist_ok=True)
    base = cfg["archivo_base"]
    for tipo, nombre in (("tecnica", "OFERTA TECNICA"), ("economica", "OFERTA ECONOMICA")):
        ruta = salida / f"{base} - {nombre}.docx"
        armar(carpeta, tipo, cfg, precios).save(ruta)
        subprocess.run(["soffice", perfil_soffice(), "--headless", "--convert-to", "pdf", "--outdir", str(salida), str(ruta)],
                       check=True, capture_output=True)
        print(ruta)
    print(f"Precio unitario {usd(precios['precio_unitario'])} · total {usd(precios['total'])} (de la planilla)")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
