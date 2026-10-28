from common import *
C="PAN AMERICAN ENERGY/62- Contrato marco AM Prefabricado Skids 3000059425"
PL="Edgardo Ledesma (taller)"
COND="Pago al dólar divisa BNA del día anterior a la facturación, 5 días FF, validez 15 días."
R=[]
a33="5.Proveedores 3ros/Presupuesto ITT N° 20033 30-07-25.docx"
for sk,pr,txt in [(8,1600,"Skid 8 USD 1,600 Más IVA"),(9,2250,"Skid 9 USD 2,250 Más IVA"),(10,2700,"Skid 10 USD 2,700 Más IVA"),(11,2700,"Skid 11 USD 2,700 Más IVA (no incluye fabricación de filtro)"),
  (12,1650,"Skid 12 USD 1,650 Más IVA"),(13,1050,"Skid 13 USD 1,050 Más IVA"),(14,2700,"Skid 14 USD 2,700 Más IVA"),(15,750,"Skid 15 USD 750 Más IVA"),(16,1200,"Skid 16 USD 1,200 Más IVA"),
  (18,600,"Skid 18 USD 600 Más IVA"),(19,600,"Skid 19 USD 600 Más IVA"),(20,330,"Skid 20 USD 330 Más IVA")]:
    R.append(T(HF,"Montaje dimensional, desmontaje para pintura y montaje final de cañerías en skid (tercero)",f"Montaje de cañerías para dimensional, desmontaje para pintura y montaje final del skid {sk} (Ledesma, presupuesto 0001-0000020033)",
      PL,"2025-07-30",pr,"global",C,a33,txt,iva="más IVA (lo dice)",equipo=f"Skid {sk} PAE contrato marco prefabricado (montaje de cañerías)",incluye="M.O, herramientas, SVO, ART",nota=COND))
for n,nom,arc in [("20034","Trampa lanzadora APO-SP-1170","5.Proveedores 3ros/Presupuesto ITT N° 20034 30-07-25.doc"),("20035","Trampa receptora APO-SP-1180","5.Proveedores 3ros/Presupuesto ITT N° 20035 30-07-25.doc")]:
    R.append(T(HS,"MO soldadura y armado de piping por pulgada (tercero)",f"Mano de obra de piping de la {nom}, USD 15 más IVA por pulgada (317 pulgadas aprox.)",PL,"2025-07-30",15,"USD/pulg-eq",C,arc,
      "317” aprox. USD 15,00 Más IVA por Pulgada.",iva="más IVA (lo dice)",magnitud="317 pulg-eq",equipo=nom,incluye="mano de obra, herramientas, ART, SVO",nota=COND+" Precio global del piping = 15 × 317 = 4.755 (aprox.): lo dice 'aprox.'."))
    R.append(T(HF,"MO fabricación skid y estructura por kg (tercero)",f"Mano de obra del skid de la {nom}, USD 2 más IVA por kg (1.548 kg aprox.)",PL,"2025-07-30",2,"USD/kg",C,arc,
      "Skid 1548 Kg aprox. USD 2,00 Más IVA por Kg.",iva="más IVA (lo dice)",magnitud="1548 kg",equipo=nom,incluye="mano de obra, herramientas, ART, SVO",nota=COND))
    R.append(T(HF,"Montaje dimensional, desmontaje para pintura y montaje final de trampa (tercero)",f"Montaje/desmontaje para pintura y montaje final de la {nom}",PL,"2025-07-30",1800,"global",C,arc,
      "Montaje /Desmontaje para Pintura/Montaje final USD 1,800 Más IVA.",iva="más IVA (lo dice)",equipo=nom,incluye="mano de obra, herramientas, ART, SVO",nota=COND))
R.append(T(HS,"MO soldadura y armado de piping por pulgada (tercero)","Prefabricado de cañerías SCH 40 de los skids 8 a 20: corte y biselado y soldadura de piping, USD 13 más IVA por pulgada",PL,"2025-07-30",13,"USD/pulg-eq",C,
  "5.Proveedores 3ros/Presupuesto ITT N° 20036 30-07-25.docx","Precio USD 13,00 Más IVA por Pulgada.",iva="más IVA (lo dice)",equipo="Prefabricado cañerías SCH 40 skids 8-20 PAE",incluye="corte y biselado, soldadura de piping; M.O, herramientas, SVO, ART",
  nota="Pago al dólar divisa BNA del día anterior a la facturación, 5 días FF, validez 15 días. Cañería SCH 40."))
agregar(R,"PAE/62")
