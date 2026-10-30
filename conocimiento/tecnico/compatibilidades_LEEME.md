# Compatibilidades para el buscador de materiales (30-10-2026)

Qué pieza del catálogo puede usarse como **similar** (precio de referencia) de lo que pide el cliente. Pedido de Matías
(30-10-2026): "no poner una comparativa entre dos válvulas que la norma no lo permite". ITT no tiene normas compradas: las
reglas salen de datos públicos de las normas (tablas que publican fabricantes y distribuidores) y del criterio técnico
habitual. El código está en `herramientas/compatibilidad.py` (y en la página, `web/src/busqueda.js`, con la misma tabla);
`herramientas/test_compatibilidad.py` controla los casos y que la página dé lo mismo.

Esto **no cambia la regla crítica**: se cotiza lo que pide el cliente. Un similar es solo un precio de referencia, marcado
"similar" con su diferencia; lo que acá figura como incompatible ni siquiera se ofrece como referencia.

## Reglas
| # | Regla | Ejemplo sí | Ejemplo no | Fuente |
|---|---|---|---|---|
| 1 | Material de la misma clase (`compatibilidad_materiales.csv`) | A105 ↔ A216 WCB (forjado/fundido, grupo 1.1); F316 ↔ CF8M ↔ TP316 | 304 por 316; A105 por A350 LF2; B8M por B7; inoxidable por carbono | ASTM; ASME B16.5 tabla 1A (grupos de material) |
| 1b | Reemplazo "hacia arriba" que la norma admite | LF2 por A105; 316L por 316; B7M por B7; A516 por A36 | al revés | ídem; NACE MR0175 (B7M/2HM) |
| 1c | Válvulas y bridas: mismo grupo de presión-temperatura de B16.5 | WCB (1.1) por A105 (1.1) | WCC (1.2) por WCB (1.1) | ASME B16.5 tabla 1A |
| 1d | Alta resistencia: el grado tiene que coincidir | X52 por X52 | X60 por X52; WPHY 65 por WPHY 52 | API 5L, MSS SP-75 / ASTM A860, A694 |
| 2 | Cara de brida igual | RF por RF | RTJ por RF; FF por RF | ASME B16.5 (caras), B16.20 (juntas RTJ) |
| 3 | Roscas iguales; roscado no reemplaza a SW | NPT por NPT | BSPT por NPT; NPT por SW | ASME B1.20.1 (NPT) vs ISO 7 (BSPT); B16.11 |
| 3b | El extremo para soldar que el catálogo no anota no cuenta | Brida WN "RF" del catálogo para un pedido "RF/BW" | — | criterio (el catálogo no registra el BW de las WN) |
| 4 | Schedule igual en caños, niples y accesorios a tope | STD por 40 hasta 10"; XS por 80 hasta 8" | 80 por 160; XS por 80 en 12" | ASME B36.10 / B36.19 |
| 5 | Servicio ácido: el candidato tiene que decir NACE | — | válvula común para un pedido NACE MR0175 | NACE MR0175 / ISO 15156 |

Ya existían (29-10-2026, `buscar_material.py`): otra serie u otra norma de la pieza (B16.5 vs B16.47, API 6D vs 608) no es
similar. Diferencias que **sí** se aceptan como similar, con la diferencia anotada: diámetro, trim, marca, paso, largo.

## Efecto al activarlas (30-10-2026)
Revisadas una por una en los renglones de todas las cotizaciones: 12 descartes correctos (cupla BSPT por NPT, brida ciega
304L por A105, niple sch 80 por 160, codo sch 160 por 120, tee sch 80 por 160, espárrago B8M por B7, media cupla NPT por SW,
juntas y válvulas RTJ por RF). Se corrigieron 2 falsos descartes al probar: bridas WN "RF/BW" contra "RF" del catálogo y
espárragos "B7 / 2H" con bulón y tuerca juntos.

## Para sumar reglas
Agregar el material a `compatibilidad_materiales.csv` (patrón, clase, grupo B16.5) o la regla a `compatibilidad.py` y a
`web/src/busqueda.js`, con un caso en `test_compatibilidad.py`. Ante dudas, el criterio con más sentido técnico,
documentado acá.
