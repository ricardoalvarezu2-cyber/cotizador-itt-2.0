# Listas cargadas por el vendedor el 30-10-2026

Las subió Matías Russo (Ventas) en el chat de Claude Code el 30-10-2026, pedido: "anotar como último precio actualizado a fecha
de hoy; ajustar el precio de los ítems que ya existen en el catálogo y agregar los que no existen". Todas son cotizaciones de
Grupo Provemet (contacto Esteban Acuña, eacuna@provemet.com, (011) 4441-0247), en USD netos, **sin IVA** ("Los precios no
incluyen I.V.A."), entrega CABA/GBA, validez 15 días, pago contado. Se carga el precio neto (con la bonificación por ítem, que
vale solo comprando toda la cotización). Cada precio conserva la fecha del documento.

| Archivo | Original | Fecha del documento | Cliente | Contenido |
|---|---|---|---|---|
| provemet_cotizacion_288974_canos_2026-10-29.pdf | Grupo_Provemet_Cotizacion_0000288974_TAVAL_SA.pdf | 29-10-2026 | Taval S.A. | 12 caños S/C A53/A106/API 5L B, 2" a 20", por metro |
| provemet_cotizacion_288977_perfiles_2026-10-29.pdf | Grupo_Provemet_Cotizacion_0000288977_TAVAL_SA (1).pdf | 29-10-2026 | Taval S.A. | 24 perfiles UPN, IPN, HEB por metro (HEB 260: "Lamentamos no cotizar", no se carga) |
| provemet_cotizacion_288978_bridas_2026-10-29.pdf | Grupo_Provemet_Cotizacion_0000288978_TAVAL_SA (1).pdf | 29-10-2026 | Taval S.A. | 24 bridas WN RF A105 B16.5, 1" a 24", #150/#300/#600 |
| provemet_cotizacion_288979_bridas_2026-10-29.pdf | Grupo_Provemet_Cotizacion_0000288979_TAVAL_SA (1).pdf | 29-10-2026 | Taval S.A. | 6 bridas WN RF A105 2" y 4", #150 a #900 |
| provemet_cotizacion_212464-01_bridas_2025-02-12.pdf | 02- Grupo_Provemet_Cotizacion_0000212464-01 Brida generales.pdf | 12-02-2025 | Tormene Americana | Antecedente de la 288978 (mismos ítems) |
| provemet_cotizacion_224190_canos_2025-02-12.pdf | Cotizacion 224190 TORMENE AMERICANA SA ReqTA7374 CANOS 2025.pdf | 12-02-2025 | Tormene Americana | Antecedente de la 288974 |
| provemet_cotizacion_228859_bridas_2025-04-04.pdf | 02- Cotizacion 228859 TORMENE AMERICANA BRIDAS 2s600 Y 4s600.pdf | 04-04-2025 | Tormene Americana | Antecedente de la 288979 |

Vinieron en dos zip: "Re: COTIZACION ACCESORIOS Y BRIDAS" (las 2026) y "RV: COTIZACION ACCESORIOS Y BRIDAS" (las 2025, que se
mandaron a Provemet para recotizar). La 236623 de perfiles del zip "RV" es idéntica (mismo md5) a la ya cargada el 28-10-2026
y no se duplica. Las de 2025 quedan como historial: el catálogo toma la más nueva.

**Para revisar (no corregido, se cargó lo que dice el documento):** en la 288978 cinco bridas repiten exacto el precio de
febrero 2025 (14" #300 706,87; 16" #150 479,12; 16" #300 822,61; 20" #150 764,47; 20" #300 1.495,56; en 2025 estaban "en
análisis - a confirmar"), mientras el resto bajó 35–50%. Por eso 14", 16" y 20" #300 quedan más caras que las #600. La brida
2" #900 sch 160 (288979) también repite el precio de 04-2025 (75,97). Conviene confirmar esos precios con Provemet.

Las convierte `herramientas/listas_vendedor.py` (lector `provemet`, ampliado el 30-10-2026 a caños y bridas con descripción en
dos renglones) a `conocimiento/precios/listas_vendedor.csv`.
