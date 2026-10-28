from common import *
PL="Edgardo Ledesma (taller)"; MS="más IVA (lo dice)"
PAGO="Pago al dólar divisa BNA del día anterior a la facturación, 5 días FF."
R=[]
R.append(T(HF,"MO fabricación de filtro (tercero)","Armado, trazado, soldadura, internos y pollera de un filtro FM simple módulo S600, espesor de cuerpo 20,62 mm (Ledesma, presupuesto 0001-0000020039)",PL,"2025-07-31",2700,"global",
  "CAMUZZI/25. valvula mas filtro FM","5.Proveedores 3ros/Presupuesto ITT N° 20039 31-07-25.docx","Precio USD 2.700 Más I",iva=MS,equipo="Filtro FM simple módulo S600 Camuzzi, cuerpo 20,62 mm",incluye="armado, trazado, soldadura, internos, pollera; M.O, herramientas, SVO, ART",nota=PAGO))
C="ENDRESS HAUSER/24- Baypass radares"; A="5.Proveedores 3ros/Presupuesto ITT N° 20075 Bypass Enders 22-08-25.docx"
R.append(T(HS,"MO armado de bypass 2\" (tercero)","Bypass doble 2\" Sch 160 cromo, mano de obra por conjunto (8 conjuntos)",PL,"2025-08-22",800,"global",C,A,"Bypass doble 2” 160 Cromo ---------------------- Cantidad 8 conjuntos Precio por conjunto USD 800.00 MÁS IVA",
  iva=MS,magnitud="",equipo="Bypass doble 2\" Sch160 cromo (Endress+Hauser)",incluye="M.O, herramientas, SVO, ART",no_incluye="PH, pintura y consumibles (los pone ITT)",nota=PAGO+" Validez 10 días."))
R.append(T(HS,"MO armado de bypass 2\" (tercero)","Bypass simple 2\" Sch 80 inoxidable, mano de obra por unidad (12 unidades)",PL,"2025-08-22",380,"global",C,A,"Bypass simple 2” 80 Inoxidable. -------------------- Cantidad 12 unidades Precio por unidad USD 380.00 MÁS IVA",
  iva=MS,equipo="Bypass simple 2\" Sch80 inox (Endress+Hauser)",incluye="M.O, herramientas, SVO, ART",no_incluye="PH, pintura y consumibles (los pone ITT)",nota=PAGO+" Validez 10 días."))
C="TAVAL/16-Calentador Mexico"
R.append(T(HF,"MO fabricación calentador indirecto (tercero)","Mano de obra del calentador indirecto 276 kW: cuerpo Ø1740 x 4400 mm, serpentina (9 codos 6\" Sch 80, 2 bridas), tubo de fuego 12\" Sch 30, chimenea, tren de combustión, montaje para dimensional",PL,"2025-08-08",18300,"global",C,
  "5.Proveedores 3ros/Presupuesto ITT CALENTADOR N° 20060 Albanesi 08-25.doc","PRECIO USD 18.300 MÁS IVA",iva=MS,equipo="Calentador indirecto 276 kW (Albanesi, ref. AR 1013-EKD-M-DWQ-26590)",incluye="M.O, ART, SVO (ver detalle en el presupuesto)",
  no_incluye="cortes, cáncamos, chapas para serpentina, rolado de chapas, perforado, cuna, soporte (por ITT)",nota=PAGO+" Validez 10 días."))
R.append(T(HF,"MO fabricación skid y estructura por kg (tercero)","Skid, plataforma, escalera y soportería del calentador indirecto 276 kW, precio por kg (Ledesma, presupuesto 0001-0000020061)",PL,"2025-08-08",2,"USD/kg",C,
  "5.Proveedores 3ros/Presupuesto ITT N° 20061 Calentador Indirecto 276 KW.doc","PRECIO por Kg. USD 2.00 MÁS IVA.",iva=MS,equipo="Calentador indirecto 276 kW (skid, plataforma, escalera, soportería)",incluye="herramientas, M.O., ART, SVO",nota=PAGO+" Validez 10 días."))
R.append(T(HF,"MO armado de cuadro roscado de puente (tercero)","Mano de obra, herramientas, corte de caño para roscar y armado de cuadro del puente CBM (parte roscada), por cuadro",PL,"2025-09-24",1800,"global","TAVAL/18- YPF Puente de inyeccion",
  "5.Proveedores 3ros/Presupuesto ITT N° 20099 Puente CBM roscado 24-09-25.doc","Precio por cada cuadro USD 1.800 MÁS IVA.",iva=MS,equipo="Puente CBM roscado (cuadro)",incluye="mano de obra, herramientas, corte de caño para roscar, armado de cuadro, SVO, ART",
  no_incluye="materiales y roscas en extremos de caños (por ITT); recomienda hacer las NPT con torno",nota=PAGO+" Validez 15 días. El mismo documento está en TAVAL/26 (carpeta OQ32673 puente AIB): no se duplicó."))
C="Sacde/7-Pedido de precios - 3029-SE-CPF-044 - INYECCION DE QUIMICOS"
R.append(T(HF,"MO fabricación módulo de inyección de químicos (tercero)","Módulo de inyección de químicos: montaje de 2 tanques de polietileno, cañerías, válvulas, tubing y accesorios; precio por unidad (versión original)",PL,"2025-08-28",2200,"global",C,
  "5.Proveedores 3ros/Ledesma Presupuesto ITT N° 20086 Modulos de inyección de químicos  28-08-25.docx","Precio por unidad USD 2.200 MÁS IVA",iva=MS,equipo="Módulo de inyección de químicos Sacde 3029-SE-CPF-044",incluye="M.O, herramientas, SVO, ART",no_incluye="consumibles y pintura (por ITT)",nota=PAGO+" Validez 10 días. Reemplazado por la versión del 26/09/2025."))
R.append(T(HF,"MO fabricación skid y estructura por kg (tercero)","Skid y soportería para cañería y tablero del módulo de inyección, precio por kg (versión original)",PL,"2025-08-28",2,"USD/kg",C,
  "5.Proveedores 3ros/Ledesma Presupuesto ITT N° 20086 Modulos de inyección de químicos  28-08-25.docx","Precio por KG USD 2.00 MÁS IVA",iva=MS,equipo="Módulo de inyección de químicos Sacde 3029-SE-CPF-044 (skid y soportería)",incluye="M.O, herramientas, SVO, ART",nota=PAGO+" Reemplazado por la versión del 26/09/2025."))
R.append(T(HF,"MO fabricación módulo de inyección de químicos (tercero)","Módulo de inyección de químicos, precio por unidad (versión modificada el 26/09/2025)",PL,"2025-09-26",1750,"global",C,
  "5.Proveedores 3ros/Presupuesto ITT N° 20086 Modulos de inyección de químicos  28-08-25.docx","Precio por unidad USD 1.750 MÁS IVA",iva=MS,equipo="Módulo de inyección de químicos Sacde 3029-SE-CPF-044",incluye="M.O, herramientas, SVO, ART",no_incluye="consumibles y pintura (por ITT)",
  nota=PAGO+" Validez 10 días. Nota 1 del documento: presupuesto modificado según lo conversado el 26/09/25. Fecha 26/09/2025 tomada de esa nota."))
R.append(T(HF,"MO fabricación skid y estructura por kg (tercero)","Skid y soportería para cañería y tablero del módulo de inyección, precio por kg (versión modificada el 26/09/2025)",PL,"2025-09-26",1.5,"USD/kg",C,
  "5.Proveedores 3ros/Presupuesto ITT N° 20086 Modulos de inyección de químicos  28-08-25.docx","Precio por KG USD 1,50 MÁS IVA",iva=MS,equipo="Módulo de inyección de químicos Sacde 3029-SE-CPF-044 (skid y soportería)",incluye="M.O, herramientas, SVO, ART",nota=PAGO+" Fecha 26/09/2025 de la nota 1 del documento."))
agregar(R,"2025 a")
