import sys; sys.path.insert(0,'/tmp/claude-0/-home-user-cotizador-itt/82ad64dc-b6db-5ba7-866e-adf8ec6ac548/scratchpad')
from agregar import agregar
R=[]
M="costos_mo_master_2024-09.xlsx"
NM=("Fecha: es la 'FECHA PRESENTACION' de la hoja (28/05/2024, skid de medición de aceite E+H). El archivo se guardó como 2024-09 y tarifas.csv usa 2024-09; "
    "dentro del documento no hay otra fecha. Valores en USD sin tipo de cambio visible (período con cepo). Es un valor del modelo de costos de ITT, no un presupuesto de proveedor.")
def m(hoja,servicio,desc,precio,unidad,quote,**k):
    d=dict(hoja=hoja,servicio=servicio,descripcion=desc,proveedor="ITT (modelo Costos MO Master)",fecha="2024-05-28",precio=precio,moneda="USD",
           iva_origen="no corresponde (valor interno de costos)",unidad=unidad,lugar="",carpeta_origen="FUENTE",archivo_origen=M,texto_original=quote,confianza="alta",nota=NM)
    d.update(k); return d
R.append(m("MO propia","Soldadura piping (valor del modelo MO Master)","Precio por pulgada de diámetro equivalente de soldadura de tramos de cañería, modelo Costos MO Master",28,"USD/pulg-eq",
   "16 | 28 | 28 | 12544",nota="Hoja 'Mano de Obra', fila TRAMOS A: columnas 'Diámetro equivalente (pulgadas)' 16, 'Cantidad de soldaduras' 28, 'Precio por pulgada' 28, 'Sub total (costo)' 12544. "+NM))
R.append(m("MO propia","Soldadura estructura (valor del modelo MO Master)","Precio por kg de mano de obra de estructura (perfiles IPN/UPN y chapa), modelo Costos MO Master",10,"USD/kg",
   "262.8 | 10 | 2628 | 30 | 90 | 82.56",nota="Hoja 'Mano de Obra', estructura IPN 180: 'Precio por Kg' 10. "+NM))
R.append(m("Pintura y revestimientos","Granallado (valor del modelo MO Master, tramos)","Precio por m2 de granallado de tramos de cañería, modelo Costos MO Master",25,"USD/m2",
   "7.8999 | 7.8999 | 25 | 70 | 750.4874",nota="Hoja 'Mano de Obra', tramos: 'Precio por Granallado' 25. "+NM))
R.append(m("Pintura y revestimientos","Pintura (valor del modelo MO Master, tramos)","Precio por m2 de pintura de tramos de cañería, modelo Costos MO Master",70,"USD/m2",
   "7.8999 | 7.8999 | 25 | 70 | 750.4874",nota="Hoja 'Mano de Obra', tramos: 'Precio por Pintura' 70. "+NM))
R.append(m("Pintura y revestimientos","Granallado (valor del modelo MO Master, estructura)","Precio por m2 de granallado de estructura, modelo Costos MO Master",30,"USD/m2",
   "262.8 | 10 | 2628 | 30 | 90 | 82.56",nota="Hoja 'Mano de Obra', estructura: 'Precio por Granallado m2' 30. "+NM))
R.append(m("Pintura y revestimientos","Pintura (valor del modelo MO Master, estructura)","Precio por m2 de pintura de estructura, modelo Costos MO Master (la planilla de tarifas.csv lo marca como alto frente a VARPAT)",90,"USD/m2",
   "262.8 | 10 | 2628 | 30 | 90 | 82.56",confianza="media",nota="Hoja 'Mano de Obra', estructura: 'Precio por Pintura m2' 90. Mucho más alto que la pintura de tramos del mismo modelo (70) y que VARPAT (35,28 todo el esquema). "+NM))
R.append(m("Ensayos y END","Placa radiográfica chica (modelo MO Master)","Precio por placa radiográfica chica, modelo Costos MO Master (reemplazado por Antonelli en 11/2025)",17,"USD/placa",
   "3 | 0 | 84 | 17 | 24 | 400 | 1428",nota="Hoja 'Mano de Obra', tramos A: 'Precio por placa (Chicas)' 17. "+NM))
R.append(m("Ensayos y END","Placa radiográfica grande (modelo MO Master)","Precio por placa radiográfica grande, modelo Costos MO Master (reemplazado por Antonelli en 11/2025)",24,"USD/placa",
   "3 | 0 | 84 | 17 | 24 | 400 | 1428",nota="Hoja 'Mano de Obra', tramos A: 'Precio por placa (Grandes)' 24. "+NM))
R.append(m("Ensayos y END","Servicio de radiografía (modelo MO Master, hasta 40 placas)","Servicio de RX: 1 servicio cubre hasta 40 placas (tabla 'Placas vs Servicios'), modelo Costos MO Master",400,"USD/servicio",
   "Placa | 40 | 1 | 400 | 400",magnitud="40 placa",nota="Hoja 'Mano de Obra': fila 'Placa | 40 | 1 | 400' y tabla Placas vs Servicios (1–40 placas = 1 servicio). Precio por servicio de hasta 40 placas. "+NM))
# planilla de costo master (PAE calentadores B)
PM="planilla_costo_master_2024-11.xlsx"
def p(servicio,desc,precio,unidad,quote,conf,nota,magn=""):
    return dict(hoja="Otros servicios",servicio=servicio,descripcion=desc,proveedor="ITT (planilla de costo master, calentadores B Pan American Energy)",fecha="2024-12-03",
        precio=precio,moneda="USD",iva_origen="no corresponde (costo interno)",unidad=unidad,magnitud=magn,equipo_referencia='Calentadores "B" CASE (Pan American Energy)',lugar="campo",
        carpeta_origen="FUENTE",archivo_origen=PM,texto_original=quote,confianza=conf,
        nota=nota+" Fecha: 'FECHA PRESENTACION' de la hoja H Calculo (03/12/2024). Costo unitario de la planilla; la unidad en la planilla dice solo 'Unid'.")
R.append(p("Visita de relevamiento en campo","Visita de relevamiento de mano de obra en campo, 1 unidad, costo unitario de la planilla",1597.8,"USD/visita",
   "MANO DE OBRA | VISITA DE RELEVAMIENTO | Unid | 1 | 1 | 1597.8","media","El rubro dice 'VISITA DE RELEVAMIENTO' y la cantidad es 1."))
R.append(p("Día de campo: reposición","Días de reposición de mano de obra en campo, costo por unidad (3 unidades en la planilla)",2380.28,"USD/dia",
   "MANO DE OBRA | DIAS DE REPOSICION | Unid | 3 | 3 | 2380.28 | 7140.84","media","El rubro dice 'DIAS' y la unidad de la planilla es 'Unid': se toma como día."))
R.append(p("Día de campo: pre-comisionado","PRE-COM, costo por unidad (6 unidades en la planilla)",2380.28,"USD/dia",
   "MANO DE OBRA | PRE-COM | Unid | 6 | 6 | 2380.28 | 14281.68","baja","La planilla no dice la unidad (solo 'Unid'): mismo costo unitario que 'días de reposición', se asume día. PRE-COM = pre-comisionado (interpretación)."))
R.append(p("Día de campo: comisionado","COM, costo por unidad (7 unidades en la planilla)",2380.28,"USD/dia",
   "MANO DE OBRA | COM | Unid | 7 | 7 | 2380.28 | 16661.96","baja","La planilla no dice la unidad (solo 'Unid'): se asume día. COM = comisionado (interpretación)."))
R.append(p("Día de campo: puesta en marcha","PEM, costo por unidad (7 unidades en la planilla)",2380.28,"USD/dia",
   "PEM | Unid | 7 | 7 | 2380.28 | 16661.96","baja","La planilla no dice la unidad (solo 'Unid'): se asume día. PEM = puesta en marcha (interpretación)."))
# Antonelli
A="antonelli_end_2025-11.pdf"
NA=("NDT Antonelli (JCA & Asociados), presupuesto 1788-JCA-1125 del 03/11/2025 a Innovación Técnica Total S.A. por servicios en la planta de Quilmes Oeste. "
    "El documento da pesos y USD (1 USD divisa BNA = $1482 al 03/11/2025) y dice que los valores no incluyen IVA. El documento no aclara qué abarca un 'servicio' (jornada, visita).")
def a(servicio,desc,precio,quote,unidad="USD/servicio",**k):
    d=dict(hoja="Ensayos y END",servicio=servicio,descripcion=desc,proveedor="NDT Antonelli (JCA & Asociados)",fecha="2025-11-03",precio=precio,moneda="USD",iva_origen="sin IVA (lo dice)",
       unidad=unidad,lugar="taller ITT",carpeta_origen="FUENTE",archivo_origen=A,texto_original=quote,confianza="alta",nota=NA,tc_documento="1482 (BNA divisa 03/11/2025)")
    d.update(k); return d
R.append(a("Radiografía (servicio)","Servicio de investigación radiográfica",490,"1 Servicios de investigación Radiográfica $726.180 USD 490"))
R.append(a("Radiografía, adicional sábado","Adicional por servicio de investigación radiográfica en sábado",245,"2 Adicional servicio de investigación Radiográfica (Sábado) $363.090 USD 245"))
R.append(a("Radiografía, adicional domingo y feriado","Adicional por servicio de investigación radiográfica en domingos y feriados",368,"Adicional servicio de investigación Radiográfica 3 $544.635 USD 368 (Domingos y Feriados)"))
R.append(a("Ultrasonido (servicio)","Servicio de investigación con ultrasonidos",490,"4 Servicios de investigación con Ultrasonidos $726.180 USD 490"))
R.append(a("Ultrasonido, adicional fin de semana y feriado","Adicional por servicio de ultrasonidos en sábados, domingos y feriados",490,"Adicional servicio de investigación con Ultrasonidos 5 $726.180 USD 490 (Sábados, Domingos y Feriados)"))
R.append(a("Partículas magnetizables (servicio)","Servicio de investigación con partículas magnetizables",490,"6 Servicios de investigación con Particulas Magnetizables $726.180 USD 490"))
R.append(a("Partículas magnetizables, adicional sábado","Adicional por partículas magnetizables en sábado",245,"Adicional servicio de investigación con Particulas 7 $363.090 USD 245 Magnetizables (Sábado)"))
R.append(a("Partículas magnetizables, adicional domingo y feriado","Adicional por partículas magnetizables en domingos y feriados",368,"Adicional servicio de investigación con Partículas 8 $544.635 USD 368 Magnetizables (Domingos y Feriados)"))
R.append(a("Líquidos penetrantes (servicio)","Servicio de investigación con líquidos penetrantes",490,"9 Servicios de investigación con Liquidos Penetrantes $726.180 USD 490"))
R.append(a("Líquidos penetrantes, adicional sábado","Adicional por líquidos penetrantes en sábado",245,"Adicional servicio de investigación con Liquidos Penetrantes 10 $363.090 USD 245 (Sabado)"))
R.append(a("Líquidos penetrantes, adicional domingo y feriado","Adicional por líquidos penetrantes en domingos y feriados",368,"Adicional servicio de investigación con Liquidos Penetrantes 11 $544.635 USD 368 (Domingos y Feriados)"))
R.append(a("Placa radiográfica chica 9x21,5","Por cada placa radiográfica de 9 x 21,5 cm",15,"12 Por cada placa radiográfica (9 x 21.5 cm) $22.230 USD 15",unidad="USD/placa"))
R.append(a("Placa radiográfica grande 9x43","Por cada placa radiográfica de 9 x 43 cm",20,"13 Por cada placa radiográfica (9 x 43 cm) $29.640 USD 20",unidad="USD/placa"))
R.append(a("Procedimiento escrito END nivel 3","Procedimientos escritos generales elaborados y firmados por Nivel 3, norma IRAM NM ISO 9712:2014",250,
   "Procedimientos Escritos General , elaborados y firmados por 14 $370.500 USD 250 Nivel 3, segun Norma IRAM NM ISO 9712:2014",unidad="global",hoja="Ingeniería, calidad e inspección",magnitud="1 procedimiento"))
R.append(a("Medición de dureza","Medición de dureza por Inspector en Soldadura Nivel 2, norma IRAM-IAS U 500-169:2019",325,
   "Medicion de Dureza, realizado por Inspector en Soldadura 15 $481.650 USD 325 Nivel 2, según Norma IRAM-IAS U 500-169:2019"))
agregar(R,"master+planilla+antonelli")
