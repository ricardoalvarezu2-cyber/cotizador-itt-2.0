import csv
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
import os
from datetime import date
D=os.path.dirname(os.path.abspath(__file__))+'/'
rows=list(csv.DictReader(open(D+'computo.csv',encoding='utf-8')))
mat=[r for r in rows if r['id'].startswith('M')]; srv=[r for r in rows if r['id'].startswith('S')]
grp={'S01':'MO','S02':'MO'}
wb=Workbook()
H=Font(bold=True,color='FFFFFF'); HF=PatternFill('solid',fgColor='1D5F86')
INP=PatternFill('solid',fgColor='FBEFD6'); TOT=PatternFill('solid',fgColor='E8EDF0')
thin=Side(style='thin',color='C9D3D9'); B=Border(bottom=thin)
TF={'cotización':'DDF1E4','lista':'DCEBF4','stock':'DCEBF4','antecedente':'FBEFD6','estimado':'F8E1DE'}
USD='#,##0.00'
def head(ws,r,cols,widths):
    for i,(c,w) in enumerate(zip(cols,widths),1):
        x=ws.cell(r,i,c);x.font=H;x.fill=HF;x.alignment=Alignment(wrap_text=True,vertical='center')
        ws.column_dimensions[chr(64+i)].width=w
    ws.freeze_panes=ws.cell(r+1,1)

# --- Cotización
ws=wb.active; ws.title='Cotización'
ws['A1']='COT26-1003-001 Rev 0 · CAPEX S.A. · PDC OQ 8209 / OR 53081'; ws['A1'].font=Font(bold=True,size=14)
ws['A2']='2 puentes armados BBO MEC 1500 · plano 23001-PDC-YAC-PC-P-001 rev 1 · USD sin IVA · EXW Quilmes Oeste · borrador 27/10/2026'
ws['A2'].font=Font(italic=True,color='5D6B75')
ws['A4']='PARÁMETROS (celdas amarillas editables)'; ws['A4'].font=Font(bold=True)
P=[('Cantidad de puentes',2,'0'),('Factor de materiales (materiales y contingencia)',1.35,'0.00'),('Factor de mano de obra y servicios',1.35,'0.00'),('Contingencia materiales',0.05,'0%'),('Incluir flete (1 = sí, 0 = no)',0,'0'),('Tipo de cambio ARS/USD (supuesto: cargar BNA)',1450,'#,##0'),('Flete BAI–CRD ARS por envío (jun-2026)',3500000,'#,##0'),('Embalaje USD por envío (estimado)',40,USD),('Factor flete',1.0,'0.00')]
for i,(n,v,f) in enumerate(P,5):
    ws.cell(i,1,n); c=ws.cell(i,2,v); c.fill=INP; c.number_format=f
# names: B5..B13
# --- Ajuste por inflación (columnas G:H) con la tabla de índices de la base
IDX=list(csv.DictReader(open(D+'../../conocimiento/costos/indices_ajuste.csv',encoding='utf-8')))
NI=len(IDX)+1
RNG=f'Índices!$A$2:$E${NI}'
ws['G5']='AJUSTE POR INFLACIÓN (desde la fecha de cada precio hasta hoy)'; ws['G5'].font=Font(bold=True)
for r,(n,v,f) in enumerate([('Aplicar ajuste (1 = sí, 0 = no)',1,'0'),('Fecha de hoy (referencia)',date(2026,10,27),'dd/mm/yyyy')],6):
    ws.cell(r,7,n); x=ws.cell(r,8,v); x.fill=INP; x.number_format=f
ws['G8']='Variación 12 meses — materiales (CPI EE.UU.)'; ws['H8']=f'=VLOOKUP(H7,{RNG},5,1)/VLOOKUP(EDATE(H7,-12),{RNG},5,1)-1'
ws['G9']='Variación 12 meses — MO y servicios (costo local en USD)'; ws['H9']=f'=VLOOKUP(H7,{RNG},4,1)/VLOOKUP(EDATE(H7,-12),{RNG},4,1)-1'
ws['H8'].number_format=ws['H9'].number_format='0.0%'
for i,t in enumerate(['Factor de cada fila = índice del mes de hoy / índice del mes del precio (hoja Índices).',
  'Materiales: CPI de EE.UU. (los precios ya están en dólares).',
  'MO y servicios: costo local en dólares = IPC INDEC / dólar BNA vendedor. Si el dólar sube menos que la inflación, el costo en USD sube.',
  'Fuentes y meses interpolados o estimados: hoja Índices (conocimiento/costos/indices_ajuste.csv).'],10):
    ws.cell(i,7,t).font=Font(italic=True,color='5D6B75',size=9)
ws.column_dimensions['G'].width=58; ws.column_dimensions['H'].width=13
ws['A16']='RESUMEN'; ws['A16'].font=Font(bold=True)
for j,t in enumerate(['Rubro','Costo / puente','Factor','Precio / puente','Total'],1):
    c=ws.cell(17,j,t); c.font=H; c.fill=HF
R=[('Materiales (con ajuste por inflación)',"=SUM(Materiales!P2:P27)",'=$B$6'),
   ('Contingencia',"=B18*$B$8",'=$B$6'),
   ('Mano de obra (armado y soldadura)',"=SUMIF('MO y servicios'!B2:B7,\"MO\",'MO y servicios'!P2:P7)",'=$B$7'),
   ('Servicios e insumos (PH, pintura, calidad, sellador)',"=SUMIF('MO y servicios'!B2:B7,\"Servicio\",'MO y servicios'!P2:P7)",'=$B$7')]
for i,(n,f,fa) in enumerate(R,18):
    ws.cell(i,1,n); ws.cell(i,2,f).number_format=USD; ws.cell(i,3,fa).number_format='0.00'
    ws.cell(i,4,f'=B{i}*C{i}').number_format=USD; ws.cell(i,5,f'=D{i}*$B$5').number_format=USD
ws['A22']='Flete a Comodoro + embalaje (por envío)'; ws['C22']='=$B$13'; ws['E22']='=IF($B$9=1,($B$11/$B$10+$B$12)*$B$13,0)'
ws['C22'].number_format='0.00'; ws['E22'].number_format=USD
ws['A23']='TOTAL SIN IVA'; ws['B23']='=SUM(B18:B21)'; ws['D23']='=SUM(D18:D21)'; ws['E23']='=SUM(E18:E22)'; ws['C23']='=D23/B23'
ws['A24']='IVA 21%'; ws['E24']='=E23*0.21'
ws['A25']='TOTAL CON IVA'; ws['E25']='=E23+E24'
ws['A26']='Margen sobre precio'; ws['D26']='=1-B23/D23'; ws['D26'].number_format='0.0%'
for r in range(23,26):
    for c in range(1,6):
        x=ws.cell(r,c); x.fill=TOT; x.font=Font(bold=True)
        if c in(2,4,5): x.number_format=USD
ws['C23'].number_format='0.00'
ws['A27']='PRECIO UNITARIO DE VENTA (redondeado, va a la oferta)'; ws['D27']='=ROUND(D23,2)'
ws['A28']='TOTAL DE LA OFERTA SIN IVA (unitario redondeado × cantidad + flete)'; ws['E28']='=D27*B5+E22'
for c in ('A27','D27','A28','E28'): ws[c].font=Font(bold=True,color='1D5F86')
ws['D27'].number_format=USD; ws['E28'].number_format=USD
ws['A29']='Costo / puente SIN ajuste por inflación'; ws['B29']="=SUM(Materiales!G2:G27)*(1+B8)+SUM('MO y servicios'!G2:G7)"
ws['A30']='Ajuste por inflación incluido en el costo / puente'; ws['B30']='=B23-B29'; ws['C30']='=B30/B29'
ws['B29'].number_format=USD; ws['B30'].number_format=USD; ws['C30'].number_format='+0.0%'
ws['A32']='Plazo: 60 días desde OC (crítico: esféricas 2" Indave 60 días; con stock Taval, 45 días). Fecha de necesidad 09/11/2026: no se puede cumplir.'
ws['A33']='Condiciones (como OE 332-24): USD facturado en pesos al TC BNA vendedor · contado contra entrega · entrega en planta ITT · validez 15 días.'
ws['A34']='Modelo de costo: PRES 24879 rev A (TAVAL/55, Tecpetrol, 22/04/2026), puente convencional de bombeo mecánico. Factor 1,35 sobre todo el puente (incluida la MO de Ledesma); 1,40 solo para MO vendida sola.'
ws.column_dimensions['A'].width=52
for c in 'BCDE': ws.column_dimensions[c].width=16

# --- detalle
def fecha(t):
    p=[int(x) for x in t.split('-')]
    return date(p[0],p[1] if len(p)>1 else 7,p[2] if len(p)>2 else 1)  # solo año: mitad de año; solo mes: día 1
def detalle(name,data,isS):
    w=wb.create_sheet(name)
    cols=['Pos','Grupo' if isS else 'ID','Descripción','Cant. / puente','Unidad','USD unit. (a la fecha del precio)','Subtotal USD (sin ajuste)','Tipo de origen','Proveedor o criterio','Carpeta de origen','Fecha del precio','ID','Meses hasta hoy','Factor inflación ('+('costo local USD' if isS else 'CPI EE.UU.')+')','USD unit. ajustado','Subtotal USD ajustado']
    head(w,1,cols,[6,10,44,10,8,13,13,13,48,26,12,6,9,10,12,13])
    col=4 if isS else 5
    for i,r in enumerate(data,2):
        g=('MO' if r['id'] in grp else 'Servicio') if isS else r['id']
        vals=[r['pos'],g,r['descripcion'],float(r['cant_por_puente']),r['unidad'],float(r['precio_unit_usd']),f'=D{i}*F{i}',r['tipo_origen'],r['proveedor_o_criterio'],r['carpeta_origen'],fecha(r['fecha_precio']),r['id'],
              f'=MAX(0,(Cotización!$H$7-K{i})/30.4375)',f'=IF(Cotización!$H$6=1,VLOOKUP(Cotización!$H$7,{RNG},{col},1)/VLOOKUP(K{i},{RNG},{col},1),1)',f'=F{i}*N{i}',f'=D{i}*O{i}']
        for j,v in enumerate(vals,1):
            c=w.cell(i,j,v); c.border=B
            if j in(4,6): c.fill=INP
            if j in(6,7,15,16): c.number_format=USD
            if j==11: c.number_format='dd/mm/yyyy'
            if j==13: c.number_format='0.0'
            if j==14: c.number_format='0.000'
        w.cell(i,8).fill=PatternFill('solid',fgColor=TF.get(r['tipo_origen'],'FFFFFF'))
    n=len(data)+2
    w.cell(n,3,'Subtotal por puente').font=Font(bold=True)
    c=w.cell(n,7,f'=SUM(G2:G{n-1})'); c.font=Font(bold=True); c.number_format=USD
    c=w.cell(n,16,f'=SUM(P2:P{n-1})'); c.font=Font(bold=True); c.number_format=USD
    for j in range(1,17): w.cell(n,j).fill=TOT
    w.auto_filter.ref=f'A1:P{n-1}'
    return w
detalle('Materiales',mat,False)
w=detalle('MO y servicios',srv,True)
alts=['Alternativas de armado: J. Quesada USD 380 (JQ-016-2026, TAVAL/51 CGC, 07/04/2026) · Ledesma USD 1.800 (ppto 20099, TAVAL/26 CAPSA, 24/09/2025, incluye corte de caño) · OE 150-22 USD 550 (2022).',
      'Alternativa de soldadura: Ledesma 16,31 USD/pulg-diám (sep-2024).','No incluye soportes (no figuran en el plano) ni radiografía (no se pide).']
for k,t in enumerate(alts): w.cell(len(srv)+4+k,3,t).font=Font(italic=True,color='5D6B75')
# alternativas materiales
m=wb['Materiales']; base=len(mat)+4
for k,t in enumerate(['Alternativas: Pos 7 retención Danco ~USD 240 WOG3000, sin confirmar (WhatsApp 11/06/2026, APSA/15) · Ing. en Fluidos cl.800 A105 USD 279 (TAVAL/55, abr-2026).',
 'Pos 2 y 5: Taval 1/2" 1500# USD 35,88 y 2" 1500# USD 113,88, con asiento blando (TAVAL/55, abr-2026). El 30% por asiento metálico es estimado.',
 'Pos 13: Duralitte USD 280 (APSA/9, feb-2026). Pos 21: extensible S3000 USD 220 (OE 150-22, 2022).',
 'Pos 14: 1,9 m por puente; 14b es el sobrante de la tira de 12 m. Precio de caño tricapa PE; el pedido es PP o cinta Canusa (Workene, sin precio). Pos 20: con el manómetro de stock (1/4") + buje sería desvío.']):
    m.cell(base+k,3,t).font=Font(italic=True,color='5D6B75')

# --- índices
x=wb.create_sheet('Índices')
head(x,1,['Mes','IPC Argentina (oct-24=100)','Dólar BNA vendedor','Costo local en USD (IPC/dólar, oct-24=100)','CPI EE.UU. (oct-24=100)','Origen IPC','Origen dólar','Origen CPI'],[11,13,12,16,12,40,40,40])
for i,r in enumerate(IDX,2):
    y,m,_=map(int,r['mes'].split('-'))
    for j,v in enumerate([date(y,m,1),float(r['ipc_argentina']),float(r['dolar_bna']),float(r['indice_local_usd']),float(r['cpi_eeuu']),r['origen_ipc'],r['origen_dolar'],r['origen_cpi']],1):
        c=x.cell(i,j,v); c.border=B
        if j==1: c.number_format='mm/yyyy'
        if j in(2,4,5): c.number_format='0.00'
        if j==3: c.number_format='#,##0.00'
        if j>=6 and str(v).startswith('dato'): c.font=Font(color='2C7A4B')
        if j>=6 and 'ESTIMADO' in str(v) or 'APROXIMADO' in str(v): c.font=Font(color='A3392F')
x.cell(NI+2,1,'Generado con herramientas/indices_inflacion.py. Verde: dato publicado. Rojo: estimado o aproximado. El resto, interpolado entre datos.').font=Font(italic=True,color='5D6B75')

# --- desvíos
d=wb.create_sheet('Desvíos'); head(d,1,['Pos','Pedido','Ofrecido / criterio'],[16,50,70])
for i,r in enumerate([
 ('2, 5','Esféricas asiento metálico, cuerpo enterizo sin bulones','Precio de referencia con asiento blando + 30%. Confirmar modelo con Taval/Indave'),
 ('7','Retención 2" #600 clapeta A216/AISI316','Base Ing. en Fluidos S600 (cumple). Si es Danco WOG3000, declarar desvío'),
 ('1, 8, 10, 11, 17, 18, 23','Accesorios forjados #2000','S3000 A105 (serie mayor, cumple)'),
 ('14','Caño revestido polipropileno','Referencia tricapa PE. Consultar PE o cinta Canusa'),
 ('21','Extensible marca Duralite, sello metal-metal','Precio Adita metal-metal; si exigen marca, cotizar Duralitte'),
 ('19','Bloqueo y purga ABAC VI 550-M','Precio ABAC 1/2" AISI 316, confirmar modelo'),
 ('20','Manómetro 0–40 bar','Stock ITT 2,5" conexión 1/4" clase 1,6; confirmar o agregar buje'),
 ('Entrega','Pampa del Castillo (Comodoro)','EXW Quilmes Oeste; flete aparte'),
 ('Plazo','Necesidad 09/11/2026','60 días desde OC')],2):
    for j,v in enumerate(r,1): c=d.cell(i,j,v); c.alignment=Alignment(wrap_text=True,vertical='top'); c.border=B

# --- antecedentes
a=wb.create_sheet('Antecedentes'); head(a,1,['Carpeta / oferta','Fecha','Qué es','Precio c/u USD','Qué se tomó'],[34,12,52,14,60])
for i,r in enumerate([
 ('TAVAL/55 · PRES 24879 rev A','2026-04-22','Puente convencional de bombeo mecánico (Tecpetrol), planilla de costo completa','costo 6.015','Estructura de costo: armado 400, pintura 100, niples, ABAC 137, factores 1,35 / 1,40'),
 ('APSA/15 · OR 33661','2026-06-11','7 puentes de producción con AIB para CAPEX, sin resultado',6729,'Indave, Ing. en Fluidos, Adita, Danco, flete'),
 ('APSA/8 · OE 332-24','2024-11-05','5 puentes para bomba electrosumergible serie 1500',6200,'Condiciones y plazo 45/60 días'),
 ('APSA/3 · OE 150-22','2022-08-25','5 puentes de producción 1500, costo 3.957 × 1,5',5935,'Control de alcance'),
 ('APSA/12 · Duralitte P_16838','2026-05-13','Junta monolítica 2"',315,'Pos 13'),
 ('TAVAL/51 · JQ-016-2026','2026-04-07','Armado y sellado de puente roscado (Quesada)',380,'Alternativa de MO'),
 ('TAVAL/26 · Ledesma ppto 20099','2025-09-24','Cuadro de puente CBM roscado',1800,'Alternativa de MO'),
 ('APSA/9 · Danco','2026-02-05','Puente AIB llave en mano, 45 días','costo 3.665','Referencia para tercerizar')],2):
    for j,v in enumerate(r,1): c=a.cell(i,j,v); c.alignment=Alignment(wrap_text=True,vertical='top'); c.border=B
    a.cell(i,4).number_format='#,##0'
wb.save(D+'COT26-1003-001_CAPEX_OQ8209.xlsx')
