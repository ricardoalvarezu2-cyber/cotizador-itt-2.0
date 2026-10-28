# Listas cargadas por el vendedor el 28-10-2026

Las subió Matías Russo (Ventas) en el chat de Claude Code el 28-10-2026. Cada precio conserva la fecha del documento
(para el ajuste por inflación y para saber cuál es el más nuevo); la fecha de carga es la de esta carpeta.

| Archivo | Proveedor | Fecha del documento | Contenido |
|---|---|---|---|
| renard_lista_2025-05-27.xlsx | Tubos Renard | 27-05-2025 | Lista de caños, accesorios y bridas (USD, sin IVA) |
| cintolo_lista_29-1_2025-02-17.xlsx | Cintolo Hnos. | 17-02-2025 (vigencia de la lista 29.1) | Accesorios BW ASME B16.9 (USD) |
| provemet_cotizacion_236623_perfiles_2025-07-01.pdf | Grupo Provemet | 01-07-2025 | Perfiles UPN, IPN, HEB por metro (USD netos sin IVA); cotización dirigida a Tormene Americana, se usa como referencia |

Las convierte `herramientas/listas_vendedor.py` a `conocimiento/precios/listas_vendedor.csv`, que lee el catálogo de materiales.
La lista Renard que ya estaba (`renar_lista_2025-12.xlsx`, 12-2025) es más nueva: donde hay la misma pieza, vale esa.
