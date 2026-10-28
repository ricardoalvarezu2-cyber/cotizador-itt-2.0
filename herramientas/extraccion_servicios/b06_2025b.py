from common import *
PL="Edgardo Ledesma (taller)"; MS="más IVA (lo dice)"
PAGO="Pago al dólar divisa tipo vendedor BNA del día anterior a la facturación, 5 días FF."
R=[]
R.append(T(HI,"Ingeniería de detalle de módulo (tercero)","Ingeniería de detalle del módulo KOD de Pluma de Venteo SK-2455 (Pampa Energía / Sacde), plazo 75 días corridos",
  "NEOCONSULT (NEO, Rolando Caviedes)","2025-02-20",25500000,"global","Sacde/2.KOD de Pluma de Venteo( Bomba + tanque)","5.Proveedores 3ros/684-ITT-KOD 2455 Pampa Sacde.pdf","AR$ 25.500.000,00- + IVA",
  moneda="ARS",iva=MS,equipo="Módulo KOD de Pluma de Venteo SK-2455",lugar="",nota="Oferta 684-ITT-KOD 2455 del 20/02/2025, en pesos con actualización por IPCBA (base enero 2025: 1673,49). El documento dice 'Los montos anteriores son en pesos y no incluyen IVA'."))
R.append(T(HI,"Ingeniería de documentos por juego (tercero)","Ingeniería de skids de inyección de químicos: 11 juegos de 15 documentos (especificación, filosofía de operación, P&ID, hojas de datos, arreglo general, estructura, PSV, unifilares, etc.)",
  "CIAR Ingeniería (Veronica Mesa)","2025-09-09",112996187.48,"global","Sacde/7-Pedido de precios - 3029-SE-CPF-044 - INYECCION DE QUIMICOS",
  "5.Proveedores 3ros/Ciar ingenieria _ FW_ Solicitud de reunión por Invitación de cotización – Skid de inyección de químicos.msg","TOTAL $ 112.996.187,48",moneda="ARS",iva="no dice",
  magnitud="165 documento",equipo="Skids inyección de químicos Sacde 3029-SE-CPF-044",lugar="",conf="media",
  nota="Total en pesos del mail de CIAR del 09/09/2025. 165 = 11 juegos × 15 documentos (cantidad deducida de la tabla del mail, que lista cada documento con 11). Moneda del '$' asumida pesos argentinos (el documento no dice 'ARS' ni 'USD'); el valor equivale a unos USD 80.000 al dólar BNA de septiembre 2025."))
R.append(T(HF,"MO fabricación de separador (tercero)","Mano de obra de armado y soldadura del separador bifásico: virolas longitudinales esp. 2\", empalme de 3 virolas, casquetes, montaje de internos, cunas de apoyo (Ledesma, presupuesto 0001-00000200102)",
  PL,"2025-03-17",73400,"global","TAVAL/3-YPF Separador Bifasicos - Separadores para satelites","5.Proveedores 3ros/Presupuesto ITT Bifasico YPF - Ledesma.docx","Precio USD 73.400 Mas IVA",iva=MS,
  equipo="Separador bifásico YPF para satélites (esp. 2\")",incluye="mano de obra, herramientas, ART, SVO; soldadura circunferencial y longitudinal raíz y refuerzo (no terminación), repelado exterior",
  no_incluye="biseles, consumibles, tintas penetrantes, END, PH, terminación de soldadura por arco sumergido (por ITT)",nota=PAGO+" Validez 10 días. Valor USD de marzo-2025 sin tipo de cambio visible: queda descartado por la regla del cepo (anterior al 14/04/2025)."))
R.append(T(HF,"MO fabricación de colector y skid (tercero)","Fabricación y soldadura de colector Ø8\" + colector 4\" + tee de derivación 4\", cuplas 3/4\", skid y soportería, por unidad",
  PL,"2025-09-01",5100,"global","TECPETROL/8. Manifold","5.Proveedores 3ros/RE_ Ledesma_Horas de ingeniería.msg","Precio Por Unidad USD 5.100 MAS IVA",iva=MS,equipo="Manifold Tecpetrol 2 skids (colector 8\" + colector 4\")",
  nota="Mail de Ledesma del 01/09/2025 respondiendo un pedido de cotización urgente de ITT por 2 skids."))
agregar(R,"2025 b")
