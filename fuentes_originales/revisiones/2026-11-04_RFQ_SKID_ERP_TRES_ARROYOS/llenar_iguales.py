import openpyxl, copy, sys
from openpyxl.styles import Font, Alignment
S=sys.argv[1]
wb=openpyxl.load_workbook(f"{S}/rfq.xlsx"); ws=wb.worksheets[0]
iguales={
 "M05":("Lista Renard 12-2025, cód. 11294 · catálogo BRI-01278","26-12-2025",26.61,27.43,"IGUAL: Bridas WN 3\" Sch40 S150 RF ASTM A105/ANSI B16.5 (Sch STD/40 según plano SCE-RE-315-0048 (cómputo COT26-0135-001)). Marca: el listado del cliente (SCE-IN-501-0015) admite para bridas solo Futura y Francovigh; Renard no figura."),
 "M5B":("Planilla de costo ITT: TECHINT Proyecto Los Toldos, Skid Sand Jetting Desarenado (LM costo Desarenador rev ventas REV.1) · catálogo JUN-01698","23-12-2025",6.00,6.18,"IGUAL: junta espiralada 3\" 150# AISI 316/grafito c/anillo ext. ac. zinc. e int. Proveedor y marca no figuran en la planilla: comprar Klinger/Teadit/Garlock (marca homologada)."),
 "M06":("Lista Renard 12-2025, cód. 11297 · catálogo BRI-01313","26-12-2025",58.91,60.72,"IGUAL: Bridas WN 6\" Sch40 S150 RF ASTM A105/ANSI B16.5 (Sch STD/40 según plano SCE-RE-315-0048 (cómputo COT26-0135-001)). Marca: el listado del cliente (SCE-IN-501-0015) admite para bridas solo Futura y Francovigh; Renard no figura."),
 "M6B":("Planilla de compras ITT: TAVAL 3-YPF Separador Bifásicos (precios compras V1) · catálogo JUN-01702","27-03-2025",15.00,13.71,"IGUAL: junta espiralada 6\" 150# AISI 316/grafito c/anillo int. Precio ESTIMADO (período con cepo, dólar sin aclarar: USD 15,00 llevado a 12,99 y ajustado a hoy): pedir cotización. Proveedor y marca no figuran en la planilla: comprar Klinger/Teadit/Garlock (marca homologada)."),
 "M07":("Lista Renard 12-2025, cód. 11298 · catálogo BRI-01328","26-12-2025",92.62,95.47,"IGUAL: Bridas WN 8\" Sch40 S150 RF ASTM A105/ANSI B16.5 (Sch STD/40 según plano SCE-RE-315-0048 (cómputo COT26-0135-001)). Marca: el listado del cliente (SCE-IN-501-0015) admite para bridas solo Futura y Francovigh; Renard no figura."),
 "M08":("Lista Renard 12-2025, cód. 8030 · catálogo BRI-01061","26-12-2025",88.17,90.88,"IGUAL: Bridas BL 8\" S150 RF ASTM A105/ANSI B16.5 (cara RF según plano SCE-RE-315-0048 (cómputo COT26-0135-001)). Marca: el listado del cliente (SCE-IN-501-0015) admite para bridas solo Futura y Francovigh; Renard no figura."),
 "M10":("Lista Renard 12-2025, cód. 3533 · catálogo ABW-00423","26-12-2025",283.84,292.56,"IGUAL: Tee reducción 8\" x 6\" Std ASTM A234 WPB. Marca: el listado del cliente (SCE-IN-501-0015) admite para accesorios a soldar solo Curvo Sold; Renard no figura. (Curvo Sold, lista Cintolo 29.1 del 17-02-2025, art. 7086: USD 351,50, período con cepo.)"),
 "M12":("Lista Renard 12-2025, cód. 3435 · catálogo ABW-00032","26-12-2025",25.76,26.55,"IGUAL: Casquete Semieliptico 6\" Std ASTM A234 WPB. Marca: el listado del cliente (SCE-IN-501-0015) admite para accesorios a soldar solo Curvo Sold; Renard no figura."),
 "M13":("Lista Renard 12-2025, cód. 3436 · catálogo ABW-00034","26-12-2025",39.61,40.83,"IGUAL: Casquete Semieliptico 8\" Std ASTM A234 WPB. Marca: el listado del cliente (SCE-IN-501-0015) admite para accesorios a soldar solo Curvo Sold; Renard no figura."),
 "M17B":("Lista Renard 12-2025, cód. 5292 · catálogo AFO-00715","26-12-2025",2.71,2.79,"IGUAL: Cupla 1/2\" NPT S3000 ASTM A105 (NPT según plano SCE-RE-315-0048 (cómputo COT26-0135-001))."),
 "M18B":("Lista Renard 12-2025, cód. 5293 · catálogo AFO-00721","26-12-2025",3.51,3.62,"IGUAL: Cupla 3/4\" NPT S3000 ASTM A105 (NPT según plano SCE-RE-315-0048 (cómputo COT26-0135-001))."),
}
V='Sin igual en el catálogo: no hay precio de esta válvula. Pedir cotización (Fiorentini/Fisher/Tormene).'
ESP='Sin igual: falta la medida del espárrago (Ø x largo) y no hay precio A193 B7/A194 2H de esa medida.'
APF="Sin igual: el material es 'S/ Esp. CAMUZZI' (plano SCE-RE-315-0048) y no hay precio de esférica paso reducido #150 RF con ese material definido y marca del listado SCE-IN-501-0008."
def cano(d,s,extra=""): return f'Sin igual: no hay caño ASTM A53 Gr B {d}" {s} con precio en el catálogo{extra}.'
TRI=" (solo triple certificación A53/A106/API 5L, que el buscador no toma como igual)"
sin={"M01":V,"M02":V,
 "M2B":"Sin igual: renglón global sin medidas ni cantidades de tubing y fittings.",
 "M03":APF,"M04":APF,
 "M5C":ESP,"M6C":ESP,"M7C":ESP,
 "M7B":'Sin igual en el catálogo: no hay precio de junta espiralada 8" 150# AISI 316/grafito.',
 "M09":'Sin igual: no hay tee 6" STD en ASTM A105 en el catálogo.',
 "M11":"Sin igual: el plano dice material 'S/ Esp. CAMUZZI', sin definir.",
 "M14":"Sin igual: el plano pide la cupla en ASTM A-106 (norma de caño; las cuplas B16.11 son A-105) y no hay precio del conjunto con válvula; consulta al cliente.",
 "M15":"Sin igual en el catálogo: no hay precio de la toma multiport ABAC.",
 "M16":"Sin igual en el catálogo: no hay precio de la válvula de alivio S71.",
 "M17":"Sin igual en el catálogo: cupla con tapón como conjunto.",
 "M18":"Sin igual: faltan largo de inserción y conexión de la termovaina.",
 "M19":"Sin igual en el catálogo: no hay precio del conjunto bloqueo y purga con manómetro.",
 "M20":"Fabricación ITT según SCE-RE-110-0006: no es material de catálogo.",
 "M20B":"Sin igual en el catálogo: la única placa AISI 304 con precio es de 2022 (período con cepo).",
 "M21":cano(3,"Sch40"),"M21B":cano(3,"Sch40"),"M22":cano(6,"Sch40"),"M22B":cano(6,"Sch40"),
 "M23":cano(6,"Sch80",TRI),"M23B":cano(6,"Sch80",TRI),"M24":cano(8,"Sch40"),"M24B":cano(8,"Sch40"),
 "M25":"Sin igual en el catálogo: no hay transmisor de presión 0-25 bar de las marcas homologadas con precio.",
 "M26":"Sin igual en el catálogo: no hay transmisor de temperatura 0-100 °C de las marcas homologadas con precio.",
 "M27":"Sin igual en el catálogo: no hay precio del switch indicador.",
}
NUM='#,##0.00'
for row in range(6,47):
    id_=ws[f"B{row}"].value; ref=ws[f"H{row}"]
    def put(col,val,fmt=None,wrap=False):
        c=ws[f"{col}{row}"]; c.value=val
        if ref.has_style:
            c.font=copy.copy(ref.font); c.border=copy.copy(ref.border); c.fill=copy.copy(ref.fill)
        c.alignment=Alignment(wrap_text=wrap, vertical="top")
        if fmt: c.number_format=fmt
    if id_ in iguales:
        a,f,n,o,q=iguales[id_]
        put("L",a,wrap=True); put("M",f); put("N",n,NUM); put("O",o,NUM); put("P",f"=F{row}*O{row}",NUM); put("Q",q,wrap=True)
    else:
        put("Q",sin[id_],wrap=True)
ws["O47"]="Total iguales (USD, sin IVA)"; ws["P47"]="=SUM(P6:P46)"; ws["P47"].number_format=NUM
ws["O47"].font=Font(bold=True); ws["P47"].font=Font(bold=True)
ws["A4"]="Precios: solo productos IGUALES del catálogo de ITT (sin similares ni sugeridos). USD sin IVA, ajustados al 04-11-2026. Borrador, sin revisar."
ws["A4"].font=Font(bold=True, color="C00000")
ws.column_dimensions["L"].width=45; ws.column_dimensions["Q"].width=60; ws.column_dimensions["M"].width=12
out=f"{S}/RFQ_REV4_1_SKID_ERP_TRES_ARROYOS_precios_iguales.xlsx"; wb.save(out)
print(sum(ws[f"F{x}"].value*iguales[ws[f"B{x}"].value][3] for x in range(6,47) if ws[f"B{x}"].value in iguales))
