# Cotizaciones de la carpeta de Drive de precios — tarea diaria del 06-11-2026

Entraron a la carpeta de Ventas en Drive (1gCEHg1TNIoa5UVKoa4x7AM8buw3Yjyck) el 05-11-2026. Cada `.md` es la transcripción del PDF
(texto leído con el conector de Drive, con el enlace al original); el PDF no se bajó porque el conector solo lo entrega codificado.
Cada renglón se controló: cantidad × precio neto = importe. Los precios se cargaron en `conocimiento/precios/listas_nuevas.csv`
(30 renglones; sin los de precio 0, sin repetidos y sin los 7 espárragos «sin tuercas» de Delgado 1556).

| Transcripción | Proveedor | Fecha | Contenido |
|---|---|---|---|
| provemet_cotizacion_289909_2026-11-05.md | Grupo Provemet → Taval | 05-11-2026 | tee #6000 NPT 2", niples Sch 160, espárragos 1 1/4" c/tuercas, brida WN RTJ #1500 4" Sch 80 (la Sch 120 y la rosca con tuerca sin precio) |
| provemet_cotizacion_289897_bridas12_2026-11-05.md | Grupo Provemet → Taval | 05-11-2026 | bridas #300 12" WN XS, ciega 8", SW 1 1/2"; espárragos 1 1/8"; niples; tapones; sockolets (5 % de bonificación en bridas solo por compra total) |
| provemet_cotizacion_289894_canos12_2026-11-05.md | Grupo Provemet → Taval | 05-11-2026 | caño s/c 12" XS y 8" Sch 60 (por metro) |
| delgado_cotizacion_0202600001542_2026-11-03.md | Industrias Delgado → ITT | 03-11-2026 | espárragos B7 c/2 tuercas 2H 1 1/8" x 7 1/4" y 7/8" x 6" (5 % por adjudicación total) |
| delgado_cotizacion_0202600001556_2026-11-05.md | Industrias Delgado → ITT | 05-11-2026 | espárragos B7 sin tuercas y tuercas 2H sueltas (5/8" a 1 1/8") |
| bripetrol_cotizacion_0001-00016310_2026-11-03.md | Bripetrol → ITT | 03-11-2026 | bridas #300 A105: WN 12" XS, WN 8" Sch 60, ciegas 12" y 8", SW 1 1/2" Sch 80 (neto; IVA 21 % aparte) |

Decisiones de la carga:
- Delgado cotiza en «EXT» (moneda extranjera): se tomó USD (los valores coinciden con los de Provemet para la misma pieza). IVA no dice: sin IVA.
- Descripciones normalizadas para el catálogo (espárragos de Delgado y Provemet, brida RTJ de Provemet, bridas de Bripetrol); el texto
  literal del proveedor queda en la transcripción y en la nota del renglón. Los espárragos con 2 tuercas van por «juego» (convención del catálogo).
- La subcarpeta «juntas» trae las Miyashiro 50627–50630 y 50594, ya cargadas el 05-11-2026.
- **Los 7 espárragos «sin tuercas» de Delgado 1556 no se cargaron todavía:** el catálogo no distingue espárrago con y sin tuercas, y
  en el control C01 un espárrago pedido «con 2 tuercas» pasaba a tomar el precio de uno sin tuercas (USD 1,31 contra 10,00).
  Se cargan cuando el buscador tenga la regla con/sin tuercas (pendiente en `conocimiento/estado_y_pendientes.md`). Las tuercas sueltas sí entraron.
