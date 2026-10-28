from common import *
PL="Edgardo Ledesma (taller)"; MS="más IVA (lo dice)"
PAGO="Pago al dólar divisa BNA del día anterior a la facturación, 5 días FF."
R=[]
R.append(T(HF,"MO fabricación skid y estructura por kg (tercero)","Mano de obra de construcción del cuerpo del calentador 370 KTBU (cuerpo, recuperador, brida, tapa), por kg sobre 770 kg; soldadores calificados ASME IX",
  "J. C. Quesada (presupuesto JQ-019-2026, Quilmes)","2026-04-22",4.20,"USD/kg","APSA/10 - Cuerpo de Calentador 370 KTBU Camuzzi","5.Proveedores 3ros/Cotizacion JQ-019-2026.pdf","Precio por kg (Total de kg 770) U$S 4,20.- U$S 3.234,00-",
  iva="sin IVA (lo dice)",magnitud="770 kg",equipo="Cuerpo calentador 370 KTBU Camuzzi",incluye="consumibles, maquinaria, herramental, mano de obra calificada, calificación de soldadores ASME IX nivel II",
  no_incluye="materiales, virolas punteadas, tapas y aros mecanizados (los provee el cliente); arenado, pintura, END, prueba hidráulica",
  nota="Aclaración del documento: 'Los valores indicados no incluyen IVA'. Nombre del proveedor inferido por el prefijo JQ (otros presupuestos JQ-0xx-2026 de J. C. Quesada). El documento dice 'Desgasificador' en el objeto aunque el título es calentador 370 KTBU. Entrega en el establecimiento del proveedor, 20 días."))
R.append(T(HF,"MO fabricación de separador (tercero)","Fabricación de separador de polvo y líquidos 28\" #600 + skid: armado y soldadura, tapa de cierre rápido Ø28\", colector Ø12\", conexiones, refuerzos, cunas, internos, skid, montaje del separador sobre skid",
  PL,"2026-05-10",13000,"global","CAMUZZI/30 - Separador Polvo y Líquido (2 unid) - Lic 22737","5.Proveedores 3ros/E Ledesma - Cotización de Separador de polvo y líquido 28_ #600.pdf","Precio USD 13.000 Más Iva",iva=MS,
  equipo="Separador de polvo y líquido 28\" #600 + skid (Camuzzi, Lic 22737)",incluye="consumibles, gases, EPP, procedimiento de soldadura y calificación de soldadores",no_incluye="plegado de cunas de apoyo, PH, END",nota="Mail de Ledesma del 10/05/2026, oferta válida 10 días."))
R.append(T(HO,"MO rolado y cilindrado de virolas y caños (tercero)","Cilindrado y punteado de caño DN 26\" (Ø ext. 660,4 mm), largo 2500 mm, espesor 1\" A-516 Gr.70N, cantidad 2, precio unitario",
  "Juan y Víctor Sandri S.A.","2026-03-25",2550000,"global","CAMUZZI/30 - Separador Polvo y Líquido (2 unid) - Lic 22737","5.Proveedores 3ros/Sandri rolado de chapa esp 1.docx","Precio unitario: $ 2.550.000 + iva",moneda="ARS",iva=MS,
  equipo="Caño DN26\" x 2500 mm x 1\" A516 Gr70N cilindrado",incluye="mano de obra de cilindrado y punteado",no_incluye="materiales; chapas cortadas al desarrollo (2500 x 2300 x 1\") que provee ITT",nota="Munro, 25/03/2026. Plazo 7 días de recibidas las chapas. Pago contra transferencia. Entrega sobre transporte de ITT en el taller de Sandri."))
C="APSA/16 - Virolas y tapas calentadores"; A="5.Proveedores 3ros/Rolados Sandri oferta del 14 08 2026.docx"
for desc,pr,q,eq in [("Virola Ø ext. 1390 mm, largo 4490 mm (2 tramos 2480 + 2010), esp. 1/4\" A-36, cantidad 1, con biseles exteriores longitudinales y circunferenciales en Y a 60°, cilindrado, armado y punteado",3760000,"Cantidad: 1. Precio: $ 3.760000 + iva.","Virola Ø1390 x 4490 x 1/4\" A-36"),
  ("Virola Ø ext. 1390 mm, largo 990 mm, esp. 3/8\" A-36, cantidad 1",1950000,"Cantidad: 1. Precio: $ 1.950.000 + iva.","Virola Ø1390 x 990 x 3/8\" A-36"),
  ("Brida Ø ext. 1540 mm, Ø int. 1390 mm, planchuela 3\" x 3/8\" A-36, cantidad 4, precio unitario",950000,"Cantidad: 4. Precio unitario: $ 950.000 + iva.","Brida Ø1540/1390 planchuela 3\" x 3/8\" A-36"),
  ("Tapa Ø 1540 mm, esp. 3/8\" A-36, cantidad 4, precio unitario",800000,"Cantidad: 4. Precio unitario: $ 800.000 + iva.","Tapa Ø1540 x 3/8\" A-36")]:
    q=q.replace("3.760000","3.760.000")
    R.append(T(HO,"MO rolado y cilindrado de virolas y caños (tercero)",desc,"Juan y Víctor Sandri S.A.","2026-08-14",pr,"global",C,A,q,moneda="ARS",iva=MS,equipo=eq,incluye="mano de obra de rolado/cilindrado y armado",
      no_incluye="materiales (los entrega ITT)",nota="Oferta de rolados del 14/08/2026 (fecha del nombre del archivo). Plazo 20 días de recibidos los materiales. Total de la oferta $ 12.710.000 + IVA."))
C="ENDRESS HAUSER/33 - Skid de medición ULACT CA1-MO-381"
R.append(T(HS,"MO armado de spools y skid (tercero)","Armado y soldadura de spools 980\" SCH 80 y de skid + soportes 1.300 kg (unidad LAC Pan American Energy); superada la cantidad cotizada, se considera adicional",PL,"2026-06-02",19600,"global",C,
  "5.Proveedores 3ros/E Ledesma Presupuesto ITT N° 200276 UNIDAD LAC PANAMERICAN ENERGY 02-06-2026.docx","Precio USD 19.600 Más IVA",iva=MS,equipo="Skid de medición ULACT CA1-MO-381 (980 pulg SCH 80 + 1300 kg de skid)",
  incluye="M.O, soldaduras, herramientas, SVO, consumibles, gases, alambres/varillas, calificación de soldadores, EPP",no_incluye="PH, pintura, montaje",
  nota=PAGO+" Mezcla pulgadas y kg en un solo precio: sin tarifa unitaria (980 pulg-eq + 1.300 kg)."))
R.append(T(HO,"Asistencia de puesta en marcha en obra (proveedor de equipo)","Asistencia de puesta en marcha en obra del calentador eléctrico 50 kW: 2 días",
  "Tapigar","2026-06-03",1950,"global",C,"5.Proveedores 3ros/6581-ITTT-Calentador electrico 50Kw Oferta Comercial.pdf","2 DÍAS ASISTENCIA PUESTA EN MARCHA EN OBRA USD 1.950.-",iva="sin IVA (lo dice)",
  magnitud="2 dia",equipo="Calentador eléctrico 50 kW 12\"#300 Tapigar",lugar="campo",nota="Dentro de la oferta comercial 6581-ITTT del fabricante. 'Los precios no incluyen IVA'. No dice cantidad de personas ni viáticos."))
C="FLARGENT/01- O1403 - Antorchas HP-LP– EPF2"
R.append(T(HF,"MO fabricación de antorcha (tercero)","Mano de obra de antorcha LBE-3052/3053 (obra 1403): torcha de 3 tramos (36.400 mm de ducto), caño interior Ø20\" y exterior Ø14\", trunnions, escaleras, plataformas, soportería, dispositivos para sopladores; peso 24.500 kg aprox.",
  PL,"2026-03-02",81000,"global",C,"5.Proveedores 3ros/E Ledesma Presupuesto ITT N° 200249 02-03-26 Antorcha.docx","Precio USD 81.000 Más IVA",iva=MS,magnitud="24500 kg",equipo="Antorcha LBE-3052/3053 Flargent obra 1403",
  incluye="M.O, herramientas, SVO, consumibles, discos abrasivos, alambre tubular, varillas 7053, CO2, argón",no_incluye="montaje de sopladores, PH, END, pintura, desarme para pintura, armado final para transporte, cilindrado de chapas, planchuelas, UPN, ángulos, chapas oxicortadas, techo protector, montaje de pico, calificación de soldador",
  nota=PAGO+" Peso 24.500 kg aprox. según el presupuesto."))
C="PAMPA ENERGIA/6- Licitación contrato marco Skid de Produccion Sierra Chata"; NI="Facturación por avance de obra. "+PAGO+" Validez 15 días."
for n,arc,pr,desc,eq in [("200311","5.Proveedores 3ros/Presupuesto ITT N° 200311 PAMPA ENERGÍA Skid Válv Hipps  11-08-2026.docx",3400,"Módulo 1 (skid válvulas HIPPS): skid y soportes, caño 6\" y 4\" SCH 120 de único tramo, armado y soldaduras","Módulo 1 skid válvulas HIPPS Pampa Sierra Chata"),
  ("200310","5.Proveedores 3ros/E Ledesma Presupuesto ITT N° 200310 MODULO 2 FLOWLINES  11-08-2026.docx",9800,"Módulo 2 flowlines: skid y soportes, armado de spool, soldaduras (precio c/u)","Módulo 2 flowlines Pampa Sierra Chata"),
  ("200309","5.Proveedores 3ros/E Leesma Presupuesto ITT N° 200309 COLECTOR 6 BOCAS SCH 120 MODULO 3  11-08-2026.docx",23250,"Módulo 3 colector 6 bocas SCH 120: skid y soportes, armado de spool, soldaduras (precio c/u)","Módulo 3 colector 6 bocas SCH 120 Pampa Sierra Chata")]:
    pf={3400:"Precio USD 3.400 Más IVA C/U",9800:"Precio USD 9.800 Más IVA C/U",23250:"Precio USD 23.250 Más IVA C/U"}[pr]
    R.append(T(HF,"MO fabricación de skid y spools (tercero)",desc+f" (Ledesma, presupuesto {n})",PL,"2026-08-11",pr,"global",C,arc,pf,iva=MS,equipo=eq,incluye="skid y soportes, soldaduras, calificación de soldadores, procedimientos, herramientas, consumibles, EPP, SVO",no_incluye="montaje, PH, pintura, END",nota=NI))
R.append(T(HF,"MO fabricación de skid y spools (tercero)","Colector de campo con cañerías de 2\", 3\" y 6\" + skid: armado y soldadura (Ledesma, presupuesto 200283)",PL,"2026-06-20",8350,"global","PAMPA ENERGIA/7- Licitacion contrato Marco Skid PAD Rincon de Aranda",
  "5.Proveedores 3ros/Presupuesto ITT N° 200283  Presupuesto Colector de campo 20-06-2026.docx","Precio USD 8.350 Más IVA C/U",iva=MS,equipo="Colector de campo 2\"/3\"/6\" + skid Pampa PAD Rincón de Aranda",incluye="armado y soldadura, SVO, consumibles, calificación de soldadores, EPP",no_incluye="PH, END, pintura, montaje",nota=PAGO+" Validez 10 días."))
agregar(R,"2026 a")
