"""Ofertas técnica y económica PRES 25856 (formato Taval) para YPF Lic 70243, sobre los modelos PRES 25594.

Uso: python cotizaciones/COT26-0330-003_YPF_LIC70243_PUENTEMED/generar_ofertas_taval.py

Lee los modelos de oferta/modelo_taval/ (PRES 25594, Lic 66944 colectores) y escribe en oferta/:
  PRES 25856- OFERTA TECNICA Lic 70243 PUENTE MED.docx
  PRES 25856- OFERTA ECONOMICA Lic 70243 PUENTE MED.docx
El precio sale de la planilla modelo de Ventas (Pie de Venta F3, recalculada con LibreOffice), nunca del chat.
Los textos se editan acá (DATOS / listas) y se vuelve a correr; no editar los .docx a mano.
"""
import copy
import subprocess
import sys
import tempfile
from pathlib import Path

import docx
import openpyxl
from docx.oxml.ns import qn
from docx.shared import Cm

C = Path(__file__).resolve().parent
sys.path.insert(0, str(C.parent.parent / "herramientas"))
from numeros import fmt  # noqa: E402

MOD = C / "oferta" / "modelo_taval"
OUT = C / "oferta"
PRES = "PRES 25856"
FECHA = "16-11-2026"
TAG, SAP = "SCC-112A", "1000653168"
DESC = "PUENTE MED.SAL.BAT.CORR.MED 500KM3D CAU*"  # texto literal de la planilla Ariba del cliente
NECESIDAD = "01-07-2027"
PLAZO = 150
REFERENCIA = "Lic 70243 - PUENTE MED.SAL.BAT.CORR.MED 500KM3D CAU - UTE LACH"
PROYECTO = "Lic 70243 - ESTÁNDAR GAS LIFT - UP-UTE LA AMARGA CHICA"
CONTACTO = "A confirmar"
LUGAR = "RUTA 17 APROX A 2 KM DE AÑELO S/N, Neuquén (8305) - UP-UTE La Amarga Chica (planta 1036)."


def precio_unitario():
    """Pie de Venta F3 de la planilla modelo, recalculada (openpyxl no calcula fórmulas)."""
    xl = C / "COT26-0330-003_YPF_Lic70243_PuenteMed_planilla_modelo.xlsx"
    with tempfile.TemporaryDirectory() as t:
        subprocess.run(["soffice", "--headless", "--convert-to", "xlsx", "--outdir", t, str(xl)],
                       check=True, capture_output=True, timeout=300)
        ws = openpyxl.load_workbook(Path(t) / xl.name, data_only=True)["Pie de Venta"]
        v = ws["F3"].value
    if not isinstance(v, (int, float)):
        raise SystemExit(f"Pie de Venta F3 no tiene número: {v!r}")
    return round(v, 2)


# ---------- utilidades sobre el .docx ----------
def portada(d):
    """Cambia los datos de la portada (cuadro de texto, versión DrawingML y VML) corrida por corrida, para no tocar el formato."""
    for tb in d.element.body.iter(qn("w:txbxContent")):
        for p in tb.iter(qn("w:p")):
            ts = list(p.iter(qn("w:t")))
            tx = [t.text or "" for t in ts]
            if "PRES" in tx and any(x.startswith("25594") for x in tx):
                for t in ts:
                    if t.text.startswith("25594"):
                        t.text = t.text.replace("25594", PRES.split()[1])
                k = tx.index("Fecha ")
                dd, mm, aa = FECHA.split("-")
                for t, v in zip(ts[k + 1:k + 6], [dd, "-", mm, "-" + aa[:3], aa[3]]):
                    t.text = v
            elif "VIÑAS, GONZALO AGUSTIN" in tx:
                ts[tx.index("VIÑAS, GONZALO AGUSTIN")].text = CONTACTO
            elif tx and tx[0].startswith("Referencia"):
                idx = [i for i, x in enumerate(tx) if x.startswith(" 66944")]
                for i, nuevo in zip(idx, [REFERENCIA[3:], PROYECTO[3:]]):
                    ts[i].text = nuevo
                    if i + 1 < len(ts) and ts[i + 1].text.startswith("ALES"):
                        ts[i + 1].text = ts[i + 1].text[4:]


def poner(p, texto):
    """Cambia el texto de un párrafo conservando el formato de su primer run."""
    rs = p.runs
    if not rs:
        p.add_run(texto)
        return
    rs[0].text = texto
    for r in rs[1:]:
        r._r.getparent().remove(r._r)


def borrar(el):
    el.getparent().remove(el)


def celda(c, texto):
    ps = c.paragraphs
    poner(ps[0], texto)
    for p in ps[1:]:
        borrar(p._p)


def tabla_filas(t, filas, ancla=1):
    """Deja en la tabla la fila de encabezado y una fila de datos por elemento de `filas` (copiando el formato de la fila `ancla`)."""
    modelo = t.rows[ancla]._tr
    for r in list(t.rows)[1:]:
        borrar(r._tr)
    for f in filas:
        tr = copy.deepcopy(modelo)
        t._tbl.append(tr)
        row = t.rows[-1]
        celdas = []
        for c in row.cells:
            if not celdas or celdas[-1]._tc is not c._tc:
                celdas.append(c)
        for c, v in zip(celdas, f):
            celda(c, v)


def lista(paras, textos):
    """Reescribe una lista con viñetas: usa el primer párrafo como modelo, copia o borra el resto."""
    base = paras[0]
    for p in paras[1:]:
        borrar(p._p)
    ant = base._p
    poner(base, textos[0])
    for t in textos[1:]:
        nuevo = copy.deepcopy(base._p)
        ant.addnext(nuevo)
        ant = nuevo
        from docx.text.paragraph import Paragraph
        poner(Paragraph(nuevo, base._parent), t)


def comunes(d, titulo):
    portada(d)
    rev = d.tables[0]
    celda(rev.rows[1].cells[1], FECHA)
    for p in d.paragraphs:
        if p.text.startswith("Establecer el alcance de nuestro propuesto"):
            poner(p, "Establecer el alcance de nuestro propuesto según los requerimientos solicitados por el cliente en la "
                     f"Licitación 70243, de acuerdo con la oferta técnica {PRES}- OFERTA TECNICA, para la provisión del "
                     "artículo detallado a continuación.")


def por_texto(d, inicio):
    for i, p in enumerate(d.paragraphs):
        if p.text.strip().startswith(inicio):
            return i
    raise SystemExit(f"No encuentro el párrafo «{inicio}» en el modelo")


# ---------- oferta económica ----------
def economica(pu):
    d = docx.Document(MOD / "PRES 25594- OFERTA ECONOMICA AM COLECTORES MAN.docx")
    comunes(d, "OFERTA ECONOMICA")
    t = d.tables[1]
    total = d.tables[1].rows[-1]._tr
    tabla_filas(t, [[TAG, SAP, DESC, "1", f"USD {fmt(pu)}", f"USD {fmt(pu)}", NECESIDAD]])
    t._tbl.append(total)
    tot = t.rows[-1]
    vistos = []
    for c in tot.cells:
        if c._tc not in vistos:
            vistos.append(c._tc)
            if c.text.strip().startswith("USD"):
                celda(c, f"USD {fmt(pu)}")
    # Borrador sin revisar (regla del proyecto: sacar esta línea recién con la cotización aprobada)
    from docx.text.paragraph import Paragraph
    t._tbl.addnext(copy.deepcopy(d.paragraphs[por_texto(d, "Establecer el alcance")]._p))
    aviso = Paragraph(t._tbl.getnext(), d.paragraphs[0]._parent)
    poner(aviso, "BORRADOR, SIN REVISAR: precio a confirmar antes de enviar (borrar esta línea al aprobar).")
    aviso.runs[0].bold = True
    aviso.runs[0].font.color.rgb = docx.shared.RGBColor(0xC0, 0x00, 0x00)

    i = por_texto(d, "De acuerdo a la tabla 2")
    poner(d.paragraphs[i], f"{PLAZO} días corridos a partir de la recepción de la Orden de Compra "
                           f"(fecha de necesidad solicitada: {NECESIDAD}).")
    i = por_texto(d, "En Almacenes de Neuquen")
    poner(d.paragraphs[i], f"Incoterm DDP - Entrega destino final: {LUGAR} Flete incluido en el precio.")
    i = por_texto(d, "La presente tiene una validez")
    poner(d.paragraphs[i], "La presente tiene una validez de 30 días corridos.")
    sal = OUT / f"{PRES}- OFERTA ECONOMICA Lic 70243 PUENTE MED.docx"
    d.save(sal)
    return sal


# ---------- oferta técnica ----------
CARACT = [("TAG", TAG), ("NORMA DE DISEÑO", "ASME B31.3"), ("NOMBRE", "PUENTE DE MEDICIÓN SALIDA DE BATERÍA (SKID DE MEDICIÓN)"),
          ("ESQUEMA", "MEDICIÓN CON BY-PASS"), ("MEDIDOR", 'CORIOLIS 3" #600 RF (FE/FIT-1800A)'),
          ("CAUDAL", "500 KM3D (RANGO CALIBRADO 0 - 600.000 SM3/D)"), ("DN COLECTOR", '4"'), ("DN BY-PASS", '4"'),
          ("PRESIÓN OPER./DISEÑO", "65-90 / 94,6 KG/CM²G"), ("TEMP. OPER./DISEÑO", "33,5-60,6 / 100 °C"),
          ("MATERIAL", "ACERO AL CARBONO"), ("SERIE/CLASE", "#600 RF / CA31"), ("RADIOGRAFIADO", "30 %"),
          ("DIMENSIONES BASTIDOR", "6.960 X 1.535 MM (CON BATEA DE CONTENCIÓN)")]
MATERIALES = [("Colector y by-pass", "ASTM A106 B", "PROVEMET/ ROYO/ SIDERCA"),
              ("Accesorios soldables", "ASTM A234 WPB", "OIL METAL/ CINTOLO/ RENARD"),
              ("Bridas", "ASTM A105", "PROVEMET/ FRANCOVIGH/ FUTURA"),
              ("Accesorios forjados y niples", "ASTM A105 / ASTM A106 B", "PROVEMET/ RENARD"),
              ("Espárragos", "ASTM A193 B7/ ASTM A194 2H", "DELGADO/ OIL METAL"),
              ("Juntas", "Espiralada AISI 316L + Grafito / Juntas dieléctricas", "MIYASHIRO/ FLEXSEAL"),
              ("Bastidor y batea", "Acero comercial (IPN/UPN/HEB) / chapa", "PROVEMET"),
              ("Medidor Coriolis", "AISI 316", "ABB/ EMERSON/ ENDRESS+HAUSER"),
              ("Transmisores y computador de caudal", "Comercial", "ABB/ ROSEMOUNT/ YOKOGAWA"),
              ("Termovaina y sensor", "AISI 316", "WEISZ/ ROSEMOUNT"),
              ("Válvulas manuales", "API 6D/ API 594/ API 608 - A105/ WCB", "TAVAL")]
INCLUYE = ["Válvulas y accesorios.",
           "Instrumentación del P&ID: FE/FIT-1800A (Coriolis), PIT-1800A con manifold, TE/TIT-1800A con termovaina y computador de caudal FQIT-1800A (nota 2 del P&ID).",
           "Juntas dieléctricas a ambos lados del medidor.",
           "Bulonería y juntas.",
           "Cableado de instrumentos hasta caja de conexionado Ex-d en el skid (ET, punto 7).",
           "Aislación y tracing eléctrico de la toma del PIT-1800A (nota 4 del P&ID).",
           "Bastidor con batea de contención y válvula de purga de 2\" (ET, punto 4.2).",
           "Pintura exterior de acuerdo a la ES-0002657 (B0600) de YPF.",
           "Placa de identificación y orejas de puesta a tierra según especificaciones de YPF.",
           "Radiografiado 30 % (clase CA31), tintas penetrantes y prueba hidráulica.",
           "Pruebas FAT.",
           "Preparación para transporte.",
           "Ingeniería de Detalle y documentación técnica (planos de detalle, hoja de datos del fabricante, etc.).",
           "Documentación de calidad / Data Book (plan de inspección y ensayos, documentos de soldadura, registros de END, registros de pruebas, certificados de materiales, actas de inspección, etc.)",
           "Transporte a destino final: UP-UTE La Amarga Chica, Añelo, Neuquén.",
           "Repuestos para puesta en marcha (10 % de bulonería y juntas).",
           "Instrumentos según la hoja de datos YPF-GASLIFTBAT21-VCD24299-I-HD-003001 D1; la HD-003002 citada en el pedido no fue recibida.",
           "Las medidas del tramo del medidor (NOTA 6 del plano) las fija el modelo de Coriolis y se ajustan en la ingeniería de detalle."]
EXCLUYE = ["Instrumentación no declarada en nuestra oferta.",
           "Indicaciones FI, PI, TI y FQI-1800A en SCADA/SCP (sala de control).",
           "Canalizaciones eléctricas y de instrumentos fuera del skid.",
           "Obra civil, montaje e interconexión en campo.",
           "Juntas de transición, ni monolíticas.",
           "Rejillas y plataformas (no indicadas en el plano).",
           "U-Stamp (no requerido).",
           "Bulones de anclaje ni plantillas de colocación, ni cálculo de anclajes.",
           "Percha de Izaje."]
ALCANCE = ["Ingeniería, Diseño y fabricación", "Placas de identificación",
           "Inspección y pruebas de todos los materiales en taller, incluso suministro de sub-proveedor",
           "Suministro de todo los Materiales dentro de nuestro alcance especificado.", "Preparación de superficies y pintura.",
           "Orejas de izaje", "Orejas de Puesta a Tierra", "Data-Book y certificado de materiales (1 copia Fiel + soporte Digital)",
           "Documentación técnica completa de acuerdo con la requisición de materiales", "Pruebas FAT",
           "Embalaje para transporte terrestre",
           "Documentación a elaborar y presentar una vez recibida la orden de compra, según corresponda para cada equipo:"]


def tecnica():
    d = docx.Document(MOD / "PRES 25594- OFERTA TECNICA AM COLECTORES MAN.docx")
    comunes(d, "OFERTA TECNICA")
    tabla_filas(d.tables[1], [[TAG, SAP, DESC, "1", NECESIDAD]])
    # captura de carpeta que quedó en el modelo (página 4)
    for p in d.paragraphs[45:56]:
        if p._p.findall(".//" + qn("w:drawing")):
            borrar(p._p)
            break
    i = por_texto(d, "PRES 25292- OFERTA TECNICA")
    poner(d.paragraphs[i], f"{PRES}- OFERTA TECNICA")
    poner(d.paragraphs[i + 1], f"{PRES}- OFERTA ECONOMICA")
    # Características: una sola tabla
    t2, t3, t4, t5, t6, t7, t8, t9, t10 = d.tables[2:11]
    filas = [r for r in t2.rows]
    mod = filas[1]._tr
    cab = [c for i, c in enumerate(filas[0].cells) if i == 0 or c._tc is not filas[0].cells[i - 1]._tc]
    celda(cab[1], TAG)  # la fila de encabezado (TAG) conserva su formato
    for r in filas[1:]:
        borrar(r._tr)
    for k, v in CARACT[1:]:
        tr = copy.deepcopy(mod)
        t2._tbl.append(tr)
        row = t2.rows[-1]
        cs = []
        for c in row.cells:
            if not cs or cs[-1]._tc is not c._tc:
                cs.append(c)
        celda(cs[0], k)
        celda(cs[1], v)
    # el encabezado (TAG) en negrita como el modelo: primera fila con el formato de la original
    for t in (t3, t4, t5):
        borrar(t._tbl)
    # Planos: una tabla y el plano del cliente
    tabla_filas(t6, [[TAG, SAP, DESC]])
    d.paragraphs[por_texto(d, "PLANOS ESQUEMATICOS")].paragraph_format.page_break_before = True
    body = d.element.body
    elems = list(body.iterchildren())
    ini, fin = elems.index(t6._tbl), elems.index(d.paragraphs[por_texto(d, "MATERIALES CONSIDERADOS")]._p)
    imagen_puesta = False
    for el in elems[ini + 1:fin]:
        if el.tag == qn("w:p") and el.findall(".//" + qn("w:drawing")) and not imagen_puesta:
            for r in el.findall(qn("w:r")):
                el.remove(r)
            from docx.text.paragraph import Paragraph
            p = Paragraph(el, d.paragraphs[0]._parent)
            p.add_run().add_picture(str(C / "oferta" / "plano_SCC-112A.png"), width=Cm(15.5))
            p.add_run().add_break()
            p.add_run("Plano YPF-GASLIFTBAT21-VCD24299-P-PL-003001 D1, hoja 1: planta y vistas del skid de medición SCC-112A.")
            imagen_puesta = True
        elif imagen_puesta and el.tag in (qn("w:p"), qn("w:tbl")):
            body.remove(el)
    # Materiales considerados
    tabla_filas(t10, [list(m) for m in MATERIALES], ancla=2)
    # el modelo tiene 2 filas de encabezado (PROVISIÓN / columnas): restaurarlas
    # (tabla_filas dejó solo la primera; se agrega la de columnas desde una copia del modelo)
    m10 = docx.Document(MOD / "PRES 25594- OFERTA TECNICA AM COLECTORES MAN.docx").tables[10]
    t10.rows[0]._tr.addnext(copy.deepcopy(m10.rows[1]._tr))
    # Listas
    def bloque(titulo, siguiente):
        i = por_texto(d, titulo)
        j = por_texto(d, siguiente)
        return [p for p in d.paragraphs[i + 1:j] if p.text.strip()]
    lista(bloque("ACLARACIONES E INCLUSIONES", "EXCLUSIONES GENERALES"), INCLUYE)
    lista(bloque("EXCLUSIONES GENERALES", "ALCANCE GENERAL"), EXCLUYE)
    al = bloque("ALCANCE GENERAL", "Lista de Documentos")
    lista(al, ALCANCE)
    # Procedimientos: sin tratamiento térmico (no requerido); el resto de la lista de documentos queda igual
    sal = OUT / f"{PRES}- OFERTA TECNICA Lic 70243 PUENTE MED.docx"
    d.save(sal)
    return sal


def main():
    pu = precio_unitario()
    for f in (tecnica(), economica(pu)):
        print(f)
    print(f"Precio unitario de la planilla modelo: USD {fmt(pu)}")


if __name__ == "__main__":
    main()
