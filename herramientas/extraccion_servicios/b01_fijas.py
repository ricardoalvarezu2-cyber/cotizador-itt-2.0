import sys; sys.path.insert(0,'/tmp/claude-0/-home-user-cotizador-itt/82ad64dc-b6db-5ba7-866e-adf8ec6ac548/scratchpad')
from agregar import agregar
P="costo_mo_planta_2024-10.xlsx"
def mp(servicio,desc,precio,unidad,quote,hoja="MO propia",fecha="2024-10-31",prov="ITT (costo propio de planta)",**k):
    d=dict(hoja=hoja,servicio=servicio,descripcion=desc,proveedor=prov,fecha=fecha,precio=precio,moneda="USD",iva_origen="no corresponde (costo propio)",
           unidad=unidad,lugar="taller ITT",carpeta_origen="FUENTE",archivo_origen=P,texto_original=quote,confianza="alta",tc_documento="997 (hoja Sueldos del mismo archivo)")
    d.update(k); return d
R=[]
R.append(mp("Soldadura piping (costo propio calculado)","Costo MO de pulgada estándar de soldadura de piping, velocidad teórica 3,1 pulg/hora",19.7293,"USD/pulg-eq",
  "Costo MO de Pulgada stándar | N/A | 1 plg. | 19.7293 | velocidad teorica 3.1 plg por hora",nota="Hoja 'Costo standar ITT'. Costo = 61,16 USD/hh ÷ 3,1 pulg/h. Tipo de cambio de los sueldos: 997 (visible en hoja Sueldos)."))
R.append(mp("Soldadura estructura (costo propio calculado)","Costo MO de soldadura por kg de estructura, deposición teórica 12 kg/h (MIG tubular con protección)",5.0967,"USD/kg",
  "Costo MO soldadura por Kg de estructura | N/A | 1 Kg. | 5.0967 | Media Deposición teorico 12 Kg/h (MIG tabular c/protec)",nota="Hoja 'Costo standar ITT'."))
R.append(mp("Hora hombre soldador (costo empresa)","Costo por hora de un operario soldador, con prorrateo de indirectos y consumibles",61.1609,"USD/hora",
  "Costo MO de Soldadura | 1 | 1 hh | 61.1609",nota="Hoja 'Costo standar ITT'. Ver hoja Reparto: costo hora empresa del centro SOLDADURA 183,48 ÷ 3 operarios."))
R.append(mp("Pintura MO propia (por hora)","Costo MO pintura base por hora de operario, velocidad teórica 2,5 m por hora",15.0241,"USD/hora",
  "Costo MO pintura base | 1 | 1 hh | 15.0241 | velocidad teorica 2.5m por hora",hoja="MO propia",nota="Hoja 'Costo standar ITT'. La hoja 'Costo hora' usa 2 m2 por hora para el mismo centro: inconsistencia de la planilla (2,5 m vs 2 m2)."))
R.append(mp("Pintura epoxi MO propia (por hora)","Costo MO pintura base epoxi por hora de operario (+5% sobre pintura base)",15.7753,"USD/hora",
  "Costo MO pintura base epox | 1 | 1 hh | 15.7753 | factor +5% pintura base",nota="Hoja 'Costo standar ITT'."))
R.append(mp("Pintura MO propia (por m2)","Costo MO de granallado y pintura por m2, velocidad teórica 2 m2 por hora, sin materiales",7.5121,"USD/m2",
  "GRANALLADO Y PINTURA | 1 | 2 | 30.0483 | 15.0241 | 7.5121 | /m2 | velocidad teorica 2m2 por hora",hoja="Pintura y revestimientos",nota="Hoja 'Costo hora' (título 'COSTO HORA ITT MAYO 2024'; sueldos de octubre 2024). 15,02 USD/hh ÷ 2 m2/h. No incluye materiales."))
R.append(mp("Hora hombre ingeniería (costo empresa)","Costo por hora de una persona del centro INGENIERÍA (2 personas)",15.3988,"USD/hora",
  "INGENIERÍA | 1 | 2 | 30.7976 | 15.3988",nota="Hoja 'Costo hora'.",hoja="MO propia"))
R.append(mp("Hora hombre granallado y pintura (costo empresa)","Costo por hora de un operario del centro GRANALLADO Y PINTURA (2 personas)",15.0241,"USD/hora",
  "GRANALLADO Y PINTURA | 1 | 2 | 30.0483 | 15.0241",nota="Hoja 'Costo hora'."))
R.append(mp("Costo hora del centro de soldadura","Costo hora planta del centro SOLDADURA completo (3 operarios)",183.4826,"USD/hora",
  "SOLDADURA | 1 | 3 | 183.4826 | 61.1609 | 19.7293 | /plg | velocidad teorica 3.1 plg por hora",nota="Hoja 'Costo hora'. Es el costo del centro entero por hora, no de un operario."))
R.append(mp("Costo hora del centro de ingeniería","Costo hora planta del centro INGENIERÍA completo (2 personas)",30.7976,"USD/hora",
  "INGENIERÍA | 1 | 2 | 30.7976 | 15.3988",nota="Hoja 'Costo hora'. Costo del centro entero por hora."))
R.append(mp("Costo hora del centro de granallado y pintura","Costo hora planta del centro GRANALLADO Y PINTURA completo (2 operarios)",30.0483,"USD/hora",
  "GRANALLADO Y PINTURA | 1 | 2 | 30.0483 | 15.0241",nota="Hoja 'Costo hora'. Costo del centro entero por hora."))
# sueldos mensuales por persona (hoja Reparto: personas, costo ajustado a mayo, sueldos octubre)
for cen,n,ajust,suel,hoja in [("INGENIERÍA",2,"2885.4444","2651.7723","MO propia"),("SOLDADURA",3,"4541.937","4174.1171","MO propia"),
        ("GRANALLADO Y PINTURA",2,"2754.7583","2531.6696","MO propia"),("ARMADO Y PREARMADO",10,"11538.3276","10603.9187","MO propia"),
        ("CALIDAD",2,"3713.4071","3412.6841","MO propia"),("ADMINISTRACION",4,"8517.0568","7827.3196","MO propia"),
        ("COMERCIAL",1,"5613.7784","5159.1575","MO propia"),("MANTENIMIENTO",1,"965.3424","887.166","MO propia"),("SUMINISTROS",2,"1953.9738","1795.735","MO propia")]:
    pp=round(float(suel)/n,2)
    R.append(mp(f"Sueldo mensual por persona, centro {cen.title()}",f"Sueldos de octubre 2024 del centro {cen} divididos por sus {n} personas (sin cargas sociales: la planilla las reparte aparte)",pp,"USD/persona-mes",
      f"{cen} | {n} | {ajust} | {suel}",confianza="media",
      nota=f"Calculado: {suel} USD de sueldos de octubre 2024 ÷ {n} personas. Hoja 'Reparto' (col. 'Sueldos Octubre'). Tipo de cambio de la hoja Sueldos: 997. Promedio del centro, no es el sueldo de una persona."))
# benchmarking Ledesma
LB="Precio por Pulgada USD 4,60 MAS IVA. | presup abril.24 usd 6 por pulgada | presup sep.24 usd 16.31 por pulgada"
KB="Precio por Kg USD 2,75 MAS IVA. | presup abril.24 usd 3.60 por kg | presup sep.24 usd 1.90 por kg"
def led(servicio,desc,precio,unidad,quote,fecha,iva,hoja,**k):
    return mp(servicio,desc,precio,unidad,quote,hoja=hoja,fecha=fecha,prov="Edgardo Ledesma (taller de terceros)",iva_origen=iva,lugar="taller tercero",confianza="alta",tc_documento="",**k)
for precio,fecha,iva in [(4.60,"2024-02","más IVA (lo dice)"),(6,"2024-04","no dice (la planilla anota 'más IVA' solo en febrero)"),(16.31,"2024-09","no dice (la planilla anota 'más IVA' solo en febrero)")]:
    R.append(led("MO soldadura y armado de piping por pulgada (tercero)","Mano de obra de soldadura de piping por pulgada-diámetro, presupuesto de Ledesma (benchmarking de la planilla de costo MO)",precio,"USD/pulg-eq",LB,fecha,iva,"Soldadura y piping",
       nota="Hoja 'Costo standar ITT' (benchmarking). Solo se sabe el mes. Tarifa en USD de ene-2024 a abr-2025 sin tipo de cambio visible. La planilla dice 'Proveedor: Edgardo Ledasma Febrero/2024'."))
for precio,fecha,iva in [(2.75,"2024-02","más IVA (lo dice)"),(3.60,"2024-04","no dice (la planilla anota 'más IVA' solo en febrero)"),(1.90,"2024-09","no dice (la planilla anota 'más IVA' solo en febrero)")]:
    R.append(led("MO fabricación skid y estructura por kg (tercero)","Mano de obra de estructura por kg, presupuesto de Ledesma (benchmarking de la planilla de costo MO)",precio,"USD/kg",KB,fecha,iva,"Fabricación y armado (terceros)",
       nota="Hoja 'Costo standar ITT' (benchmarking). Solo se sabe el mes. Tarifa en USD de ene-2024 a abr-2025 sin tipo de cambio visible."))
R.append(led("Hora hombre armado (tercero)","Precio de la hora hombre de armado, Ledesma",7.00,"USD/hora","Precio H.H. Armado USD 7,00 MAS IVA","2024-02","más IVA (lo dice)","Fabricación y armado (terceros)",
   nota="Hoja 'Costo standar ITT' (benchmarking), Febrero/2024. USD sin tipo de cambio visible (período con cepo)."))
R.append(mp("Granallado y pintura esquema completo","Granallado/arenado y esquema de pintura por m2, VARPAT (en la planilla: $ 31.750 = USD 35,28)",35.28,"USD/m2",
   "Granallado/Arenado y esquema de pintura 1m2 $ 31.750 = usd 35.28",hoja="Pintura y revestimientos",fecha="2024-05",prov="VARPAT",iva_origen="no dice",lugar="taller tercero",
   moneda="USD",tc_documento="899,9 implícito: $31.750 = USD 35,28 en la misma línea",nota="Hoja 'Costo standar ITT' (benchmarking: 'Proveedor: VARPAT Mayo/2024'). La planilla da pesos y dólares: 31.750 ÷ 35,28 = 899,9 $/USD (tipo de cambio implícito). No dice qué incluye la pintura (esquema) ni IVA."))
R.append(mp("Suministro de pintura por m2","Costo de la pintura (solo suministro) por m2, VARPAT",19,"USD/m2",
   "Costo de pintura (suministro) 1m2 usd 19",hoja="Pintura y revestimientos",fecha="2024-05",prov="VARPAT",iva_origen="no dice",lugar="taller tercero",tc_documento="",
   nota="Hoja 'Costo standar ITT' (benchmarking: 'Proveedor: VARPAT Mayo/2024'). Solo suministro, sin aplicación."))
agregar(R,"planta 2024-10")
