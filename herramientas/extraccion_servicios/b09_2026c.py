from common import *
PL="Edgardo Ledesma (taller)"; MS="más IVA (lo dice)"
PAGO="Pago al dólar divisa BNA del día anterior a la facturación, 5 días FF."
R=[]
C="Sacde/20 - SE-3121-ASTORD-014 - TK DE CHOQUE"
R.append(T(HF,"MO fabricación skid y estructura por kg (tercero)","Mano de obra de construcción del tanque de choque 36\" (planos típicos TGS) por kg sobre 1802 kg; consumibles, maquinaria, herramental, mano de obra calificada",
  "J. C. Quesada (presupuesto JQ-012-2026)","2026-02-27",10700,"global",C,"5.Proveedores 3ros/Cotizacion JQ-012-2026.pdf","Precio Kg totales 1802 kg U$S 10.700,00.-",iva="no dice",magnitud="1802 kg",
  equipo="Tanque de choque 36\" TGS (1802 kg)",incluye="consumibles, maquinaria, herramental, mano de obra calificada",no_incluye="pintura, END, materiales",
  nota="Precio total por 1802 kg (USD 5,94/kg). Plazo 45 días dependiendo de la materia prima, entrega en su establecimiento. Fecha 27/02/2026 del encabezado. El documento menciona prueba hidráulica solo para otros trabajos; no confirmar PH incluida sin leer el original."))
R.append(T(HF,"MO fabricación de tanque (tercero)","Fabricación completa del tanque de choque Ø36\" (típico gasoducto): virolas esp. 9,52 mm, casquetes, conexiones 2\" a 6\", cáncamos; soldadura GTAW raíz TIG y FCAW (Ledesma, presupuesto 200245)",
  PL,"2026-02-27",11800,"global",C,"5.Proveedores 3ros/Ledesma Presupuesto ITT N° 200245 20-02-26 Tanque de Choque 2.docx","Precio USD 11.800 Más IVA",iva=MS,equipo="Tanque de choque 36\" TGS (1802 kg)",
  no_incluye="pintura, END, elementos para PH",nota=PAGO+" Fecha 27/02/2026 del encabezado (el nombre del archivo dice 20-02-26)."))
C="Sacde/6- 3029-SE-CPF-042 - SKID CALENTADOR DE GAS DE PROCESO"
R.append(T(HF,"MO fabricación de skid y spools (tercero)","Skid del calentador eléctrico envolvente 16\": plataformas, escaleras, baranda, cañerías ~315 pulgadas, para dimensional, desmontaje para pintura y montaje final (Ledesma, presupuesto 20070)",
  PL,"2025-08-11",9700,"global",C,"5.Proveedores 3ros/LEDESMA Presupuesto ITT N° 20070 Calentador eléctrico-11-08-2025.docx","Precio USD 9.700 Más IVA",iva=MS,equipo="Skid calentador eléctrico de gas de proceso Sacde 3029-SE-CPF-042",
  incluye="M.O, herramientas, SVO, ART",no_incluye="fabricación del interior del calentador; PH y pintura (por ITT)",nota=PAGO+" Validez 15 días. Fecha 11/08/2025 del nombre del archivo."))
R.append(T(HF,"MO fabricación skid y estructura por kg (tercero)","Mano de obra de plataforma y escalera: 1287,30 kg a USD 4,10/kg",
  "J. C. Quesada (presupuesto JQ-010-2026)","2026-02-12",4.10,"USD/kg",C,"5.Proveedores 3ros/Cotizacion JQ-010-2026 estructura de Calentador eléctrico.pdf","Precio Kg totales 1287,30 kg U$S 4,10.- U$S 5.278,00.-",iva="sin IVA (lo dice)",
  magnitud="1287.3 kg",equipo="Plataforma y escalera calentador eléctrico Sacde 3029-SE-CPF-042",no_incluye="arenado, pintura, END, prueba hidráulica con certificado, materiales",
  nota="Aclaración: 'Los valores indicados no incluyen IVA'. Plazo 30 días dependiendo de la materia prima. Fecha 12/02/2026 del encabezado del documento."))
R.append(T(HS,"MO soldadura y armado de piping por pulgada (tercero)","Cañerías del colector de drenaje del calentador eléctrico 90 kW: prefabricado y soldadura de patines, 200\" aproximado de 2\", 6\" y 1\" SCH 80, 5 isométricos (Ledesma, presupuesto 200229)",
  PL,"2026-02-04",3200,"global",C,"5.Proveedores 3ros/Presupuesto ITT cañerías colector de drenaje N°229- 4-02-26.docx","PRECIO USD 3.200 MÁS IVA.",iva=MS,magnitud="200 pulg-eq",
  equipo="Colector de drenaje calentador eléctrico 90 kW Sacde 3029-SE-CPF-042 (200 pulg)",no_incluye="consumibles, PH, montaje",
  nota=PAGO+" Tarifa derivada: 3.200 ÷ 200\" aprox. = 16 USD/pulgada (incluye patines)."))
C="TAVAL/40- INARTECO FILTROS LIC 9333"
base="5.Proveedores 3ros/Presupuestos MO Filtros/"
for n,doc,pr,fl,q in [("200231","LEDESMA/Presupuesto ITT Filtro FM 8 S 600 lado derecho- Nº 200231.docx",2100,"FM8 S600 lado derecho","PRECIO USD 2.100 MÁS IVA."),
   ("200232","LEDESMA/Presupuesto ITT Filtro FM 8 S 600 lado izquierdo - Nº 200232.docx",2100,"FM8 S600 lado izquierdo","PRECIO USD 2.100 MÁS IVA."),
   ("200233","LEDESMA/Presupuesto ITT Filtro FM 2 S 300 lado derecho - Nº 200233.docx",800,"FM2 S300 lado derecho","PRECIO USD 800 MÁS IVA."),
   ("200234","LEDESMA/Presupuesto ITT Filtro FM 2 S 300 lado izquierdo - Nº 200234.docx",800,"FM2 S300 lado izquierdo","PRECIO USD 800 MÁS IVA."),
   ("200235","LEDESMA/Presupuesto ITT Filtro FM 3 S 150 - Nº 200235.docx",950,"FM3 S150","PRECIO USD 950 MÁS IVA.")]:
    R.append(T(HF,"MO fabricación de filtro (tercero)",f"Mano de obra del filtro {fl} (Ledesma, presupuesto {n}): herramientas, mano de obra, SVO",PL,"2026-02-09",pr,"global",C,base+doc,q,iva=MS,equipo=f"Filtro {fl} Inarteco Lic 9333",
      incluye="herramientas, mano de obra, SVO",no_incluye="consumibles, PH, END, pintura",nota=PAGO))
for fl,pr,q in [("FM8 S600 lado derecho",3900,"Usd 3.900,00 + iva.-"),("FM8 S600 lado izquierdo",3900,"Usd 3.900,00 + iva.-"),("FM3 S150",2250,"Usd 2.250,00 + iva.-"),("FM2 S300 lado derecho",2100,"Usd 2.100,00 + iva.-"),("FM2 S300 lado izquierdo",2100,"Usd 2.100,00 + iva.-")]:
    R.append(T(HF,"MO fabricación de filtro (tercero)",f"Mano de obra común y especializada del filtro {fl}, precio unitario con consumibles (Finder Arg S.A., presupuesto 3075)","Finder Arg S.A. (Burzaco)","2026-03-02",pr,"global",C,base+"FINDER/FINDER F-76 Presupuesto N° 3075 - Filtros.pdf",q,iva="más IVA (lo dice)",
      equipo=f"Filtro {fl} Inarteco Lic 9333",incluye="consumibles",no_incluye="PH (según comparativa de ITT)",tc="1397 (consignado en el presupuesto)",
      nota="Presupuesto F-76 N° 3075, Burzaco, 02/03/2026. Cotizado en USD con tipo de cambio consignado de 1.397; nota de débito si la diferencia al cobro es ≥ 2,5%. Reajuste Pr = Po x (0,20 Mat/Mat0 + 0,80 Mo/Mo0). Validez 15 días. La línea del documento tiene puntos de relleno que no se copian en la cita."))
R.append(T(HF,"MO fabricación de filtro (tercero)","Mano de obra, piping, soldadura, armado y prueba hidráulica de 5 cámaras reguladoras 40/10/2,5 bar (filtros FM8 x2, FM2 x2, FM3); personal: 1 soldador calificado, 1 cañista, 1 medio oficial; 390 horas, 13 días hábiles",
  "MCD Montajes Industriales SRL","2026-02-12",27000000,"global",C,base+"MCD MONTAJES INDUSTRIALES/PRESUPUESTO- Sr. Carlos Alfonso ( ITT Quilmes ) (1).pdf","Presupuesto final : $ 27.000.000 más IVA",moneda="ARS",iva=MS,
  equipo="Lote de 5 filtros Inarteco Lic 9333 (cámaras reguladoras)",incluye="piping, soldaduras, armado, prueba hidráulica, herramientas, insumos, transporte y viáticos del personal, seguro de accidentes personales",
  nota="12/02/2026, validez hasta el 05/03/2026, anticipo 40%. Precio del lote de 5 equipos. 'Reduje personal y horas' según el mail del mismo día."))
R.append(T(HF,"MO fabricación de filtro (tercero)","Mano de obra de lote de 5 filtros incluyendo consumibles y prueba hidráulica, según la comparativa de ITT (el presupuesto de Quesada es un PDF escaneado sin texto)",
  "J. C. Quesada (valor de la comparativa de ITT)","",8319,"global",C,base+"Comparativa MO Filtros Inarteco.xlsx","Oferta x lote de 5 filtros | 8319 | 6750 | 14250 | 19354",iva="no dice",
  equipo="Lote de 5 filtros Inarteco Lic 9333 (cámaras reguladoras)",incluye="mano de obra, maquinaria, herramientas, soldadores calificados, consumibles, PH",conf="media",
  nota="Valor tomado de 'Comparativa MO Filtros Inarteco.xlsx' (columnas J C Quesada | E Ledesma | Finder | MCD). Sin fecha: la comparativa no trae fecha (la ficha de la carpeta usaba 15/01/2026, que no se pudo confirmar en el documento). El PDF original de Quesada no tiene texto. Ledesma 6750 y Finder 14250 coinciden con sus presupuestos."))
agregar(R,"2026 c")
