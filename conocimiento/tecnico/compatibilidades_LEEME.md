# Compatibilidades para el buscador de materiales (30-10-2026)

Qué pieza del catálogo puede usarse como **similar** (precio de referencia) de lo que pide el cliente. Pedido de Matías
(30-10-2026): "no poner una comparativa entre dos válvulas que la norma no lo permite". ITT no tiene normas compradas: las
reglas salen de datos públicos de las normas (tablas que publican fabricantes y distribuidores) y del criterio técnico
habitual. El código está en `herramientas/compatibilidad.py` (y en la página, `web/src/busqueda.js`, con la misma tabla);
`herramientas/test_compatibilidad.py` controla los casos y que la página dé lo mismo.

Esto **no cambia la regla crítica**: se cotiza lo que pide el cliente. Un similar es solo un precio de referencia, marcado
"similar" con su diferencia; lo que acá figura como incompatible ni siquiera se ofrece como referencia.

## Reglas (corregidas el 30-10-2026 tras la revisión independiente)
Criterio: un reemplazo vale solo si el candidato es **igual o superior en todo** (resistencia, rating presión-temperatura,
tenacidad, servicio). Si no se puede probar, no es similar.

| # | Regla | Ejemplo sí | Ejemplo no |
|---|---|---|---|
| 1 | Material de la misma clase (`compatibilidad_materiales.csv`); doble certificación: el candidato cumple cada una | A105 ↔ A216 WCB; F316 ↔ CF8M ↔ TP316; 316/316L por 316 | 304 por 316; 316L por 316/316L; WP304 por F316 |
| 1b | Reemplazos admitidos (`REEMPLAZA`) | LF2 / LCC por A105; WCC por WCB; A106 B por A53 o API 5L B; A333 Gr 6 por A106 B; 316 por 304; CF3M por CF8M; súper dúplex por dúplex; L7 por B7; B8M Cl 2 por B8M | 316L por 316 (grupo 2.3 < 2.2); 304L por 304; B7M por B7 y 2HM por 2H (menor resistencia); A53 por A106; LCB por A105 (1.3) |
| 1c | Grupo de B16.5: el del candidato con rating igual o mayor (`GRUPOS`) | 1.2 por 1.1; 2.2 por 2.1 | 1.3 por 1.1; 2.3 por 2.2 |
| 1d | Alta resistencia: el grado tiene que coincidir | X52 por X52 | X60 por X52; API 5L B por X-52 |
| 1e | Candidato **sin material** (ni en la descripción): no es similar si el pedido dice el material | — | válvula sin material para un pedido A105 |
| 1f | Material del pedido que no está en la tabla: solo el mismo texto | Monel 400 por Monel 400 | A105 por A182 F11 |
| 1g | Galvanizado y negro no se mezclan; genéricos ("acero al carbono", "inoxidable") solo del lado del pedido | A105 por "acero al carbono" | "acero al carbono" por A105 |
| 2 | Conexión: tipo brida / rosca / SW / BW en común; dentro del tipo, misma cara y misma rosca | WN "RF" del catálogo para "RF/BW" | bridada por roscada; BSPT por NPT; RTJ por RF; SW por NPT |
| 3 | Schedule igual (caños, niples, accesorios a tope): 40S = STD, 80S = XS; STD = 40 hasta 10", XS = 80 hasta 8"; sin diámetro no se iguala | STD por 40 en 4" | XS por 80 en 12"; STD por 40 en "DN 300" sin leer |
| 4 | Servicio ácido: MR0175 / ISO 15156 exige lo mismo; "NACE", "sour" o "H2S" exige NACE | — | MR0103 por MR0175 |

Fuentes: ASTM de cada material, ASME B16.5 tabla 1A (grupos), B16.34, B31.3 (factor de junta), B36.10/B36.19, API 5L,
NACE MR0175 / ISO 15156. ITT no tiene las normas compradas: datos públicos y criterio técnico, revisados por un revisor
independiente (30-10-2026).

Ya existían (29-10-2026, `buscar_material.py`): otra serie u otra norma de la pieza (B16.5 vs B16.47, API 6D vs 608) no es
similar. Diferencias que **sí** se aceptan como similar, con la diferencia anotada: diámetro, trim, marca, paso, largo.

## Efecto al activarlas (30-10-2026, primera versión)
Revisadas una por una en los renglones de todas las cotizaciones: 12 descartes correctos (cupla BSPT por NPT, brida ciega
304L por A105, niple sch 80 por 160, codo sch 160 por 120, tee sch 80 por 160, espárrago B8M por B7, media cupla NPT por SW,
juntas y válvulas RTJ por RF). Se corrigieron 2 falsos descartes al probar: bridas WN "RF/BW" contra "RF" del catálogo y
espárragos "B7 / 2H" con bulón y tuerca juntos.

## Para sumar reglas
Agregar el material a `compatibilidad_materiales.csv` (patrón, clase, grupo B16.5) o la regla a `compatibilidad.py` y a
`web/src/busqueda.js`, con un caso en `test_compatibilidad.py`. Ante dudas, el criterio con más sentido técnico,
documentado acá.

## Revisión independiente (30-10-2026)
Un revisor que no escribió las reglas encontró errores de la primera versión: reemplazos que no son "igual o superior"
(316L por 316, 304L por 304, B7M por B7, 2HM por 2H), grupo de B16.5 sin controlar en los reemplazos, candidatos sin
material que pasaban como similares, bridada contra roscada sin comparar, patrones que no leían "WP316", "TP304", "CF8",
"SA-106", "API 5L X-52", Cr-Mo (WC6, F11, F22), A420 WPL6, A333 por grado, A516 por grado, dúplex/súper dúplex,
bulonería B8/L7, y NACE MR0103 aceptado por MR0175. Todo corregido.
Efecto sobre las cotizaciones: 40 renglones de las precotizaciones cambian (28 por candidato sin material); en las
cotizaciones cargadas, 5 renglones de Camuzzi 001, 002 y 003 (4 quedan SIN PRECIO, 1 pasa a un caño A106 al mismo precio).
Controles: C01 baja de 73.198 a 44.161 (la válvula de 3 vías motorizada y otras quedan sin precio; sin contarlas da −2%).
Para que haya menos SIN PRECIO hay que cargar el material que falta en el catálogo (1.407 renglones sin material).
