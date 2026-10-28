from core import R
FAB="Fabricación y armado (terceros)"
c="AESA/44-Doc5319481557 - AESA - SRV FABRICACION EQUIPOS - F5064"
for ppto,desc,eq,precio,inc,noinc,f in [
 ("Presupuesto ITT N° 20078 Desgasificador SB 301-571 27-08-25.docx","Fabricación (MO) desgasificador SB-301/571","Desgasificador SB-301/571, 1 unidad",28500,
  "Armado de virolas y soldadura longitudinal, refuerzos (ponchos), conexiones, base (pollera), plataforma escalera, soportes para cañería externa, montaje de internos, placa de desgaste, vane, bafle, rompevórtice; MO, herramientas, SVO, ART por Ledesma",
  "Cilindrado, chapas, caños, perfiles, PH, perforado de bridas de pollera","USD 28.500 MÁS IVA"),
 ("Presupuesto ITT N° 20079 Desgasificador SB - 211 27-08-25.docx","Fabricación (MO) desgasificador SB-211","Desgasificador SB-211, 1 unidad",37200,
  "Armado de virolas y soldaduras, ponchos, casquetes semielípticos, conexiones 20/24/2/4 pulg, trunnions, soportería, paso de hombre, escalera/plataforma, placa deflectora, bafle, rompevórtice; MO, herramientas, SVO, ART por Ledesma",
  "Cilindrado de perfiles y chapas, caños, perfiles, PH, consumibles, perforado de bridas de pollera","USD 37.200 MÁS IVA"),
 ("Presupuesto ITT N° 20080 Scrubber de succión SB 003-004  27-08-25.docx","Fabricación (MO) scrubber de succión compresores SB-003/004","Scrubber de succión SB-003/004, 1 unidad",37200,
  "Armado de virolas y soldaduras, ponchos, casquetes, conexiones, paso de hombre, pollera, internos, demister, vanes, placa deflectora, ánodos de sacrificio, plataforma escalera, cáncamos de izaje; MO, herramientas, SVO, ART por Ledesma",
  "Cilindrado de perfiles, caños para barandas, perfiles, consumibles, perforado de bridas de pollera","USD 37.200 MÁS IVA"),
 ("Presupuesto ITT N° 20081 Desgasificador VTR SB 211  27-08-25.docx","Fabricación (MO) desgasificador VRT SB-211","Desgasificador VRT SB-211, 1 unidad",33000,
  "Armado de virolas y soldaduras, ponchos, casquetes, base de pollera, soportería, plataformas y escaleras, internos, placa de desgaste, cañería, bafle, rompevórtice; MO, herramientas, SVO, ART por Ledesma",
  "Cilindrado de chapas, caños, perfiles, consumibles, perforado de bridas de pollera, PH, pintura","USD 33.000 MÁS IVA"),
 ("Presupuesto ITT N° 20082 Desgasificador VRT SB 402-442-475  27-08-25.docx","Fabricación (MO) desgasificador VRT SB-402/442/475","Desgasificador VRT SB-402/442/475, 1 unidad",33000,
  "Armado de virolas y soldaduras, ponchos, casquetes, base de pollera, soportería, plataformas y escaleras, internos, placa de desgaste, cañería, bafle, rompevórtice; MO, herramientas, SVO, ART por Ledesma",
  "Cilindrado de chapas, perfiles, cañería, perforado de bridas de pollera, PH, pintura","USD 33.000 MÁS IVA"),
 ("Presupuesto ITT N° 20083 Recipiente de recirculación SB - 705  27-08-25.docx","Fabricación (MO) recipiente de recirculación SB-705","Recipiente de recirculación SB-705, 1 unidad",11200,
  "Armado de virolas y soldaduras, ponchos, conexiones externas, refuerzos, cáncamos, paso de hombre, patas de apoyo, internos, ánodos de sacrificio, placas de desgaste, vane, bafle, rompevórtice, soportes; MO, herramientas, SVO, ART por Ledesma",
  "PH, pintura","USD 11.200 MÁS IVA")]:
    R(FAB,"fabricación equipo",desc,"Ledesma (Edgardo Ledesma, taller)","2025-08-27",precio,"USD","+ IVA","global","",eq,"taller tercero",inc,noinc,c,"5.Proveedores 3ros/"+ppto,f,"alta","Precio por unidad; pago 5 días F.F.; validez 10 días. No dice kg ni pulgadas del equipo.")
R(FAB,"fabricación equipo","Armado, trazado, soldadura, internos y pollera de filtro FM simple módulo S600","Ledesma (Edgardo Ledesma, taller)","2025-07-31",2700,"USD","+ IVA","global","","Filtro FM simple módulo S600, espesor de cuerpo 20,62 mm, 1 unidad","taller tercero",
  "Armado, trazado, soldadura, internos, pollera; MO, herramientas, SVO, ART","No lo dice (el presupuesto no lista exclusiones)","CAMUZZI/25. valvula mas filtro FM","5.Proveedores 3ros/Presupuesto ITT N° 20039 31-07-25.docx","Precio USD 2.700 Más IVA","alta","Presupuesto 0001-0000020039; validez 15 días.")
c="ENDRESS HAUSER/24- Baypass radares"
R(FAB,"armado bypass","MO de bypass doble 2\" 160 cromo (por conjunto)","Ledesma (Edgardo Ledesma, taller)","2025-08-22",800,"USD","+ IVA","global","","8 conjuntos bypass doble 2\" Sch160 cromo (precio por conjunto)","taller tercero",
  "MO, herramientas, SVO, ART por Ledesma","PH, pintura y consumibles (los pone ITT)",c,"5.Proveedores 3ros/Presupuesto ITT N° 20075 Bypass Enders 22-08-25.docx","Precio por conjunto USD 800.00 MÁS IVA","alta","Presupuesto 0001-0000020075.")
R(FAB,"armado bypass","MO de bypass simple 2\" 80 inoxidable (por unidad)","Ledesma (Edgardo Ledesma, taller)","2025-08-22",380,"USD","+ IVA","global","","12 unidades bypass simple 2\" Sch80 inoxidable (precio por unidad)","taller tercero",
  "MO, herramientas, SVO, ART por Ledesma","PH, pintura y consumibles (los pone ITT)",c,"5.Proveedores 3ros/Presupuesto ITT N° 20075 Bypass Enders 22-08-25.docx","Precio por unidad USD 380.00 MÁS IVA","alta","Presupuesto 0001-0000020075.")
