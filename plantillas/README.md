# Plantillas

| Archivo | Uso | Origen |
|---|---|---|
| `informe_cotizacion.html` | Plantilla del informe interactivo de una cotización (marcadores `{{...}}`). La completa `herramientas/armar_cotizacion.py` | Informe de la COT26-1003-001 (CAPEX OQ8209), 27/10/2026 |
| `oferta_itt_2026.docx` | Plantilla de oferta de ITT (portada "Oferta Comercial", recuadro azul con los datos, secciones numeradas, tablas azules, notas y firma). La usa `herramientas/generar_oferta.py` para las ofertas técnica y económica | Oferta económica 138 de ITT a Flargent (Calentador indirecto EAP-3541, 18/03/2026), carpeta `FLARGENT/02` de la tanda 1. El formato de la oferta técnica sigue la PRES 24879 (Taval/Tecpetrol, 22/04/2026) |

El generador reemplaza todos los datos de Flargent. No editar la plantilla a mano salvo para actualizar el formato de ITT.
