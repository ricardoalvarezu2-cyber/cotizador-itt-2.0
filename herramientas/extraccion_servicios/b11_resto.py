from common import *
PL="Edgardo Ledesma (taller)"; MS="más IVA (lo dice)"
PAGO="Pago al dólar divisa BNA del día anterior a la facturación, 5 días FF."
R=[]
R.append(T(HF,"MO fabricación skid y estructura por kg (tercero)","Skid del manifold PAD S-600, precio por kg (Ledesma, presupuesto 200240)",PL,"2026-02-18",2.5,"USD/kg","TECPETROL/9. CM SKID MANIFOLD PAD S-600","5.Proveedores 3ros/Ledesma/Presupuesto ITT N° 200240 18-02-26 Skid Manifold.docx","Precio por KG USD 2.50 Más IVA",
  iva=MS,equipo="Skid manifold PAD S-600 Tecpetrol",incluye="M.O, herramientas, SVO",no_incluye="pintura, END",nota=PAGO+" Validez 10 días."))
R.append(T(HF,"MO fabricación skid y estructura por kg (tercero)","Skid, plataforma, escalera y soportería del skid de calentador, precio por kg (Ledesma, presupuesto 20071)",PL,"2025-08-11",2,"USD/kg","Sacde/6- 3029-SE-CPF-042 - SKID CALENTADOR DE GAS DE PROCESO",
  "5.Proveedores 3ros/LEDESMA Presupuesto ITT N°20071 Skid de Calentador 11-08-22025.doc","PRECIO Por Kg. USD 2.00 MÁS IVA",iva=MS,equipo="Skid calentador de gas de proceso Sacde 3029-SE-CPF-042",incluye="skid, plataforma, escalera, soportería, M.O, ART, SVO",nota=PAGO+" Validez 10 días."))
TA="conocimiento/costos/tarifas.csv"
def tf(hoja,servicio,desc,precio,unidad,quote,prov,**k):
    d=dict(hoja=hoja,servicio=servicio,descripcion=desc,proveedor=prov,fecha="",precio=precio,moneda="USD",iva_origen="no dice",unidad=unidad,lugar="",carpeta_origen="REPO",archivo_origen=TA,texto_original=quote,confianza="baja",
           nota="NO VERIFICADO en el original: el archivo fuente (planilla de costos base de cotizaciones 2024 / Costos MO Master II) no está en el repositorio ni en las carpetas extraídas; se toma de costos/tarifas.csv. La fecha es solo el año (o el mes) que figura en tarifas.csv.",tc_documento="")
    d.update(k); return d
R.append(tf(HM,"Soldadura piping (valor del modelo MO Master)","Mano de obra de soldadura de piping usada en la cotización del separador trifásico AESA (modelo Costos MO Master II)",32,"USD/pulg-eq",
  "soldadura,Mano de obra soldadura piping,USD/pulg-diam-eq,32,usado_en_cotizacion,2024-02,Costos_MO_Master_II-SEP_TRIFASICO,no,Separador trifásico AESA; mismo valor en Costos_MO dic-2023","ITT (modelo Costos MO Master II)",fecha="2024-02"))
R.append(tf(HM,"Soldadura estructura (valor del modelo MO Master)","Mano de obra de estructura soldada usada en la cotización del separador trifásico (modelo Costos MO Master II)",7.40,"USD/kg",
  "estructura,Mano de obra estructura soldada,USD/kg,7.40,usado_en_cotizacion,2024-02,Costos_MO_Master_II-SEP_TRIFASICO,no,","ITT (modelo Costos MO Master II)",fecha="2024-02"))
for sv,pr,q in [("Hora hombre ingeniería (valor de la planilla base)",15,"hora_hombre,Ingeniería,USD/hh,15,usado_en_cotizacion,2024,planilla_base_cotizaciones,no,"),
                ("Hora hombre calidad (valor de la planilla base)",15,"hora_hombre,Calidad,USD/hh,15,usado_en_cotizacion,2024,planilla_base_cotizaciones,no,"),
                ("Hora hombre planta: movimientos internos y prueba hidráulica (valor de la planilla base)",13,"hora_hombre,Planta (movimientos internos y prueba hidráulica),USD/hh,13,usado_en_cotizacion,2024,planilla_base_cotizaciones,no,")]:
    R.append(tf(HM,sv,sv,pr,"USD/hora",q,"ITT (planilla base de cotizaciones 2024)",lugar="taller ITT",fecha="2024"))
R.append(tf(HE,"Placa radiográfica (valor de la planilla base)","Placa radiográfica, valor de la planilla base de cotizaciones 2024 (reemplazado por Antonelli 11/2025)",6.5,"USD/placa","end,Placa radiográfica,USD/placa,6.5,tercero,2024,planilla_base_cotizaciones,no,Reemplazado por Antonelli 2025-11","ITT (planilla base de cotizaciones 2024)",fecha="2024"))
R.append(tf(HE,"Radiografía (servicio)","Servicio de radiografía, planilla base de cotizaciones 2024 (reemplazado por Antonelli 11/2025)",408,"USD/servicio","end,Servicio de radiografía,USD/servicio,408,tercero,2024,planilla_base_cotizaciones,no,Reemplazado por Antonelli 2025-11","ITT (planilla base de cotizaciones 2024)",fecha="2024"))
R.append(tf(HE,"Líquidos penetrantes (servicio)","Servicio de líquidos penetrantes, planilla base de cotizaciones 2024 (reemplazado por Antonelli 11/2025)",294,"USD/servicio","end,Servicio de líquidos penetrantes,USD/servicio,294,tercero,2024,planilla_base_cotizaciones,no,Reemplazado por Antonelli 2025-11","ITT (planilla base de cotizaciones 2024)",fecha="2024"))
R.append(tf(HP,"Granallado y pintura con materiales (valor de la planilla base)","Granallado y pintura con materiales por m2, planilla base de cotizaciones 2024",50,"USD/m2","pintura,Granallado y pintura con materiales,USD/m2,50,usado_en_cotizacion,2024,planilla_base_cotizaciones,no,","ITT (planilla base de cotizaciones 2024)",fecha="2024"))
agregar(R,"resto")
