"""Llena la "Planilla modelo de cotizacion.xlsx" (formato de Ventas) con el cómputo de esta cotización.

Uso: python cotizaciones/COT26-0330-003_YPF_LIC70243_PUENTEMED/llenar_planilla_modelo.py

Lee computo.csv (lo genera armar_cotizacion.py desde cotizacion.json) y escribe
COT26-0330-003_YPF_Lic70243_PuenteMed_planilla_modelo.xlsx con las hojas del modelo:
Pie de Venta, DISEÑO, RESUMEN, EQUIPO 1 y VALVULAS. Mark up de cotizacion.json (parametros.FM, 1,5 desde el 16-11-2026) en todos los renglones; se conservan
las convenciones del modelo (piping × 1,2, pintura × 1,2): el precio puede diferir del de la planilla del
repositorio (factores 1,35 / 1,35 y contingencia 5 %). No editar la salida a mano: se edita cotizacion.json y se vuelve a correr.
"""
import csv
from copy import copy
from pathlib import Path

import openpyxl

C = Path(__file__).resolve().parent
MODELO = C / "pedido" / "Planilla modelo de cotizacion.xlsx"
SALIDA = C / "COT26-0330-003_YPF_Lic70243_PuenteMed_planilla_modelo.xlsx"

cp = {r["id"]: r for r in csv.DictReader(open(C / "computo.csv", encoding="utf-8"))}


def fila(i, desc=None, ampliada=None):
    r = cp[i]
    return {"pos": r["pos"], "desc": desc or r["descripcion"].split(" · Ø")[0], "amp": ampliada or "",
            "cant": float(r["cant_por_puente"]), "un": r["unidad"], "pu": float(r["precio_unit_usd"]),
            "nota": f'{r["proveedor_o_criterio"][:90]} · {r["fecha_precio"]} · {r["coincidencia"]}'}


SECCIONES = [
    ("piping", "Piping", ["M01", "M01B", "M02", "M03", "M04", "M05", "M06", "M07", "M08", "M09", "M10", "M11", "M12",
                          "M13", "M17", "M18", "M19", "M20", "M21", "M22"], "=SUM({r})*1.2"),
    ("skid", "Skid", ["M29", "M30"], "=SUM({r})"),
    ("valv", "Válvulas Manuales", ["M14", "M15", "M16", "M28"], "=SUM({r})"),
    ("mo3", "Mano de obra de 3ros", ["S20"], "=SUBTOTAL(9,{r})"),
    ("moitt", "Mano de obra de ITT", ["S12H", "S13C", "S13A", "S24"], "=SUBTOTAL(9,{r})"),
    ("pint", "Granallado y pintura", ["S02"], "=SUM({r})*1.2"),
    ("end", "Ensayos NO Destructivos", ["S04"], "=SUBTOTAL(9,{r})"),
    ("tra", "Transporte", ["S21"], "=SUBTOTAL(9,{r})"),
    ("ins", "Instrumental", ["M23", "M24", "M25", "M26", "M27", "M31", "M32", "M33"], "=SUM({r})"),
    ("rep", "REPUESTOS PEM - 10% DE BULONERIA Y JUNTAS", ["S22"], "=SUM({r})"),
]
DESC = {"M14": 'VALVULA ESFERICA FLG RF 600 LB P.TOTAL OP. A VOLANTE Y CJA RED. 4" (VF-1809/1810/1811/1812/1814/1815)',
        "M15": 'VALVULA DE RETENCION A CLAPETA FLG RF 600 LB ASTM A105 4" (VR-1813)',
        "M16": 'VALVULA ESFERICA NPT WOG 2000 P. TOTAL 3/4"', "M28": 'VALVULA ESFERICA NPT WOG 2000 P. TOTAL 2" (purga batea, ET 4.2)'}


def estilo(dst, src):
    dst.font, dst.border, dst.fill = copy(src.font), copy(src.border), copy(src.fill)
    dst.number_format, dst.alignment = src.number_format, copy(src.alignment)


def main():
    wb = openpyxl.load_workbook(MODELO)
    wb._external_links = []  # el modelo apuntaba a otro libro ('[4]Man. Conc...'): se reemplaza por referencias internas
    ws = wb["EQUIPO 1"]
    ref = {k: [ws.cell(row=n, column=c) for c in range(1, 10)] for k, n in
           {"tit": 54, "cab": 55, "item": 56, "sub": 93}.items()}
    ref = {k: [copy(c._style) for c in v] for k, v in ref.items()}
    vals_ref = {"cab": [ws.cell(row=55, column=c).value for c in range(1, 10)]}
    for row in ws.iter_rows(min_row=32, max_row=ws.max_row):
        for c in row:
            if type(c).__name__ != "MergedCell":
                c.value = None
            c._style = copy(ws.cell(row=1, column=12)._style)

    def pone(n, c, v, k):
        cell = ws.cell(row=n, column=c, value=v)
        cell._style = copy(ref[k][c - 1])

    # Encabezado
    for n, v in {1: "YPF S.A.", 2: "Licitación 70243 - Puente de medición (Estándar Gas Lift, IISS Batería 2.1)",
                 3: "Skid de medición SCC-112A · borrador, sin revisar", 4: "COT26-0330-003 Rev 0", 5: 1,
                 6: "SKID DE MEDICIÓN N° SCC-112A", 7: "1 (a confirmar)", 8: "16-11-2026", 9: "a confirmar",
                 10: "YPF-GASLIFTBAT21-VCD24299-P-PL-003001 D1 · R-PI-003010 D0 · I-HD-003001 D1 · ET VCD16011-G-ET-001005 D2"}.items():
        ws.cell(row=n, column=3, value=v)
    ws["B28"] = "Plazo de entrega : 150 días corridos desde OC (fija el plazo el Coriolis importado: ABB 122 días, Yokogawa 130-140)"
    ws["B29"] = "Entrega: EXW, ITT SA, Av. 12 de Octubre 4004, Quilmes Oeste, más transporte a Neuquén (ítem Transporte)"

    alcance = [("Recipiente", "NO"), ("Piping", "SI"), ("Skid", "SI"), ("Plataforma / escaleras", "NO"),
               ("Válvulas manuales", "SI"), ("Instrumental", "SI"), ("Instalación eléctrica", "SI"), ("Aislación", "SI"),
               ("Tracing eléctrico", "SI"), ("Mano de obra de 3ros", "SI"), ("Mano de obra ITT", "SI"),
               ("Granallado y pintura", "SI"), ("Ensayos no destructivos", "SI"), ("Embalaje", "SI"),
               ("Transporte a destino final", "SI"), ("Seguro de Caución", "SI")]
    n = 32
    ws.cell(row=n, column=2, value="MATERIA PRIMA Y MATERIALES")
    for i, (a, b) in enumerate(alcance, start=33):
        ws.cell(row=i, column=2, value=a); ws.cell(row=i, column=3, value=b)
    ws["D43"] = "Ingeniería de detalle - Calidad - Montaje, PH, FAT"
    ws["D39"] = "Caja de conexionado Ex-d y cableado de instrumentos (ET 7)"
    ws["D40"] = "Toma del PIT-1800A (P&ID nota 4)"
    ws["D41"] = "Toma del PIT-1800A (P&ID nota 4)"
    ws["B50"] = "Material principal:"
    ws["C50"] = "Tubo S/C ASTM A106 Gr.B Sch 80, accesorios ASTM A234 WPB, bridas ASTM A105 #600 RF (clase CA31: 600# RF, AºCº, CA 1,6 mm)"
    ws["B51"] = "END"
    ws["C51"] = "30% Rx (clase CA31, L0200), y donde no se pueda Rx se harán LP"

    sub = {}
    n = 54
    for clave, titulo, ids, formula in SECCIONES:
        pone(n, 2, titulo, "tit"); pone(n, 3, "SI", "tit")
        n += 1
        for c, v in enumerate(vals_ref["cab"], start=1):
            pone(n, c, v, "cab")
        ws.cell(row=n, column=8, value="Fuente del precio · fecha · coincidencia")
        n += 1
        ini = n
        for i in ids:
            f = fila(i, DESC.get(i))
            pone(n, 1, f["pos"], "item"); pone(n, 2, f["desc"], "item"); pone(n, 3, f["amp"], "item")
            pone(n, 4, f["cant"], "item"); pone(n, 5, f["un"], "item"); pone(n, 6, f["pu"], "item")
            pone(n, 7, f"=F{n}*D{n}", "item")
            ws.cell(row=n, column=8, value=f["nota"] + (" · SIN PRECIO: pedir cotización" if f["pu"] == 0 else ""))
            n += 1
        pone(n, 7, formula.format(r=f"G{ini}:G{n - 1}"), "sub")
        sub[clave] = f"G{n}"
        n += 3

    # Cuadro de rentabilidad: mismos renglones y factores del modelo
    ws["D15"] = f"={sub['piping']}+{sub['skid']}+{sub['moitt']}+{sub['pint']}+{sub['end']}"
    ws["D16"] = f"={sub['valv']}"
    ws["D17"] = f"={sub['ins']}"
    ws["D18"] = f"={sub['mo3']}"
    ws["D19"] = f"={sub['tra']}"
    ws["D20"] = f"={sub['rep']}"
    ws["D21"] = float(cp["S23"]["precio_unit_usd"])
    ws["B20"] = "Repuestos puesta en marcha (ET 3.1)"
    ws["B21"] = "Seguro de caución (catálogo OTR-00459, a recalcular con el monto)"
    import json
    mk = json.load(open(C / "cotizacion.json", encoding="utf-8"))["parametros"]["FM"]
    for r in range(15, 22):
        ws.cell(row=r, column=3, value=1)
        ws.cell(row=r, column=5, value=mk)  # mark up único (Ricardo Álvarez, 16-11-2026)

    # RESUMEN: sin vínculos a otro libro
    rs = wb["RESUMEN"]
    rs["B2"] = rs["B3"] = "Lic 70243 - Puente de medición SCC-112A (YPF Estándar Gas Lift, IISS Batería 2.1)"
    rs["B4"] = "COT26-0330-003 Rev 0 (borrador, sin revisar)"
    rs["B6"] = "RICARDO ALVAREZ"; rs["B7"] = 1
    rs["B8"] = "16-11-2026"; rs["B9"] = "a confirmar"
    rs["B10"] = "YPF-GASLIFTBAT21-VCD24299-P-PL-003001 D1"
    rs["A14"] = "SKID DE MEDICIÓN SCC-112A 4\" #600 c/ Coriolis 3\""
    for r in range(15, 22):
        rs[f"A{r}"] = f"='EQUIPO 1'!B{r}"
        rs[f"F{r}"] = f"=E{r}"
        rs[f"C{r}"] = f"='EQUIPO 1'!D{r}"  # el modelo tenía el transporte fijo (C19 = 2500)
    rs["B23"] = "='EQUIPO 1'!C15"
    rs["A31"] = "Plazo de entrega : "
    rs["A32"] = "150 días corridos desde OC (Coriolis importado)."
    rs["A33"] = "Entrega: EXW Quilmes Oeste + transporte a Neuquén incluido."

    # Pie de Venta
    pv = wb["Pie de Venta"]
    for row in pv.iter_rows(min_row=3, max_row=pv.max_row):
        for c in row:
            if type(c).__name__ != "MergedCell":
                c.value = None
    pv["A3"] = "SCC-112A"; pv["B3"] = 10; pv["C3"] = "a confirmar"
    pv["D3"] = "SKID DE MEDICION SCC-112A 4\" #600 C/CORIOLIS 3\" VCD24299"; pv["E3"] = 1
    pv["F3"] = "=RESUMEN!F23"; pv["G3"] = "=F3*E3"; pv["H3"] = "a confirmar"; pv["I3"] = 150
    pv["A4"] = "TOTAL (SIN IVA)"; pv["G4"] = "=SUM(G3:G3)"

    # DISEÑO
    ds = wb["DISEÑO"]
    for row in ds.iter_rows(min_row=8, max_row=ds.max_row):
        for c in row:
            if type(c).__name__ != "MergedCell":
                c.value = None
    ds["B2"] = "ASME B31.3 (clase CA31, L0200)"; ds["B3"] = 30
    ds["A4"] = "Presión de operación (mín / nor / máx)"; ds["B4"] = "65 / 88,6 / 90"
    ds["A5"] = "Presión de diseño (HD PIT-1800A)"; ds["B5"] = 94.6
    ds["A6"] = "Temperatura de operación / Temp. de diseño"; ds["B6"] = "33,5 - 60,6 / 100"
    ds["B7"] = "ES__-0002657 (B0600) - Protección anticorrosiva con recubrimientos"
    ds["A8"] = "Presión de prueba hidráulica"; ds["B8"] = "1,5 × P diseño (a confirmar con la clase CA31)"
    ds["A9"] = "Fluido"; ds["B9"] = "Gas natural (gas lift)"

    # VALVULAS: pedido para Taval
    vs = wb["VALVULAS"]
    for row in vs.iter_rows(min_row=2, max_row=vs.max_row):
        for c in row:
            if type(c).__name__ != "MergedCell":
                c.value = None
    vs["B2"] = "SCC-112A"; vs["C2"] = "TOTAL DE EQUIPOS"; vs["E2"] = 1
    vs["B3"] = "Manual Valves"; vs["D3"] = "Delivery times- EXW"
    for c, v in zip("BCDEF", ["Description", "Ø", "Quantity", "Unid", "TOTAL"]):
        vs[f"{c}4"] = v
    lista = [("BALL VALVE, FLANGED RF, 600 LB, FULL BORE, ASTM A105/A216 Gr.WCB, HANDWHEEL AND GEARBOX OPERATED", '4"', 6),
             ("SWING CHECK VALVE, FLANGED RF, 600 LB, ASTM A105 (RAG6R)", '4"', 1),
             ("BALL VALVE, NPT, WOG 2000, FULL BORE, ASTM A105", '3/4"', 5),
             ("BALL VALVE, NPT, WOG 2000, FULL BORE, ASTM A105 (drip tray drain)", '2"', 1)]
    for i, (dsc, d, q) in enumerate(lista, start=5):
        vs[f"B{i}"], vs[f"C{i}"], vs[f"D{i}"], vs[f"E{i}"], vs[f"F{i}"] = dsc, d, q, "un", f"=D{i}*$E$2"

    wb.save(SALIDA)
    print(SALIDA)


if __name__ == "__main__":
    main()
