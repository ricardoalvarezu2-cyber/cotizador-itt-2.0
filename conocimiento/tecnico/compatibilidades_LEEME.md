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

## Auditoría independiente (30-10-2026, segunda vuelta)
- Las reglas se aplican sobre el **texto** del plano y de la descripción del proveedor (`material_texto`), no sobre el
  atributo "material" del buscador, que pierde el grado (WC6 → WCB, 316L → 316, WPL6 → vacío).
- Bulonería: si el candidato no dice ningún grado de bulón ni de tuerca ("espárrago 304"), no se puede comparar.
- Patrones corregidos: tuerca 8M solo pegado ("8m", no "4,8 m"); API 5L X sin espacio fuera de "API 5L" ("x60" sí,
  "5/8 x 60" no); A516-60/65 con "Gr"; A194 4/7; A53 Gr A como clase propia (no reemplaza a A53 B).
- Válvulas con cuerpo e internos ("WCB, internos 316"): el candidato tiene que decir los dos; uno que solo dice el cuerpo
  no prueba los internos (caso real: la retención WCB de USD 533 era trim 13Cr).
- P9 (`verificar_computo.py`) controla todas las filas con precio: las de compra extra contra su fila madre si usan la
  misma pieza, las agregadas por ITT contra su propia descripción, las fuentes sin código contra el texto de la fuente.
  Otra serie es ERROR (salvo que la diferencia esté escrita en la fuente); otro Ø u otro tipo, AVISO.
- Efecto: 25 renglones de las precotizaciones cambian (revisados uno por uno y aceptados); en las cotizaciones cargadas,
  7 renglones de Camuzzi 001 y 002 (ver bitácoras). Control TS01 78.293 → 59.014.

## Segunda auditoría independiente (30-10-2026)
- **Válvulas: cuerpo e internos por separado.** Los internos (int, trim, esfera, vástago, asientos, clapeta, resorte,
  disco…) son una exigencia aparte; el cuerpo del candidato tiene que reemplazar al cuerpo pedido. "Retención a clapeta"
  y "válvula de esfera" son el tipo, no internos. Si el candidato nombra carbono e inoxidable sin decir cuál es el cuerpo
  ("F316 … A105 forjada"), no se compara.
- **Lo negado no es el material:** se saca "no …", "en lugar de …", "falta …", "cotizar …" antes de leer.
- **Notaciones:** "GR°B" = Gr B; "SA-516-60" = A516-60; "A53" sin grado es una clase propia que no reemplaza a A53 B;
  "5/8 x 70" es una medida, no API 5L X70; 8M solo junto a A194, tuerca o Gr.
- **P9:** filas b/c sin material propio se comparan con la fila madre; "Renard · cód. N" con su pieza del catálogo;
  fuentes sin código también por conexión y serie (sin lo que la fuente dice del pedido: "el plano pide…", "(pedido …)");
  una serie mayor solo si está escrita en la fuente, nunca en juntas; un ESTIMADO sobre otra pieza es AVISO.

## Tercera auditoría independiente (30-10-2026)
- Grado X después de un número ("sch 40 X52", "e=19,05 X65") se lee como grado si el texto nombra API 5L o PSL.
- "Cuerpo bipartido/tripartito" (sin material) no es un cuerpo explícito; los internos cortan en "cuerpo"; si el pedido
  nombra metal solo en los internos, no se compara.
- Schedule por extremo ("80x40", "STD x XS", "SCH XS x SCH 60"): el candidato tiene que decir los dos y coincidir.
- Revestimiento: PP reemplaza a PE, no al revés; sin revestimiento no reemplaza a uno revestido.
- P9: una pieza que la norma no admite solo pasa como **desvío declarado en la oferta** en esa posición (aviso; si sigue
  entre corchetes, "a confirmar"). Sin desvío declarado es ERROR, también si el precio es estimado.
- **Para sumar o cambiar reglas:** correr `python herramientas/revisar_pares_compatibilidad.py --control --salida x.md`
  (o `--ref main`) y revisar cada NUEVO ACEPTADO (¿la norma permite ese reemplazo?); `verificar_todo.py` falla mientras
  no se acepten (`--aceptar`, después de revisarlos). Además `revisar_cambio_busqueda.py --ref main` para los resultados.

## Cuarta auditoría independiente (30-10-2026)
- **Desvío declarado:** vale solo si el texto de aclaraciones y desvíos de la oferta que nombra la posición habla de lo
  que no cumple (serie, material, extremos, revestimiento, schedule, NACE) y no tiene [corchetes]. Con corchetes es
  "DESVÍO A CONFIRMAR": ERROR que frena el paso a revisado (en borradores `verificar_todo` lo lista sin frenar).
- Candidato con schedule por extremo para un pedido de uno solo: los dos extremos tienen que ser el del pedido.
- Grado X después de "sch NN" ("sch 40 X52") es grado, no medida.
- Revestimiento: "revestido/tricapa" sin polímero exige que el candidato esté revestido; PU; "sin revestimiento de …"
  no cuenta como revestido.
- Costura: con costura (c/c, ERW, SAW, tipo E/F) no reemplaza a sin costura (s/c, S/COSTURA, SMLS, tipo S); A106 es sin
  costura por norma.
- **Línea base de pares:** `revisar_pares_compatibilidad.py --control` (en `verificar_todo`) compara con
  `pares_linea_base.json`; ante cambios, revisar cada uno (`--salida`) y recién ahí `--aceptar`.

## Quinta auditoría independiente (30-10-2026): desvío estructurado
- Un reemplazo que la norma no admite solo pasa con un **desvío en el renglón** de `cotizacion.json`:
  `"desvio": [{"que": "serie", "ofrecido": "serie 3000", "pedido": "serie 2000"}]` (que: material, extremos, schedule,
  revestimiento, costura, nace, serie), uno por cada diferencia, sin "a confirmar", y lo ofrecido tiene que figurar en un
  texto de aclaraciones y desvíos de la oferta que nombre la posición. Un desvío "a confirmar" es ERROR "DESVÍO A
  CONFIRMAR": el borrador se arma, pero no pasa a revisado.
- `compatibilidad.motivos()` devuelve todos los motivos; P9 pide un desvío para cada uno.
- La página hace el mismo control con las piezas del catálogo y no deja pasar a revisado o aprobado con referencias
  incompatibles o desvíos sin resolver (también los de la oferta entre [corchetes] o "a confirmar").
- Pendiente conocido: NPT/BW pedido contra NPT/NPT (el BW que falta de un lado no cuenta, decisión del 30-10-2026).

## Sexta auditoría independiente (30-10-2026)
- La página no deja pasar a revisado ni aprobar sin el P9 del repositorio sobre la misma versión (`cot.p9`, firma de
  los renglones de material; `semilla.py` la escribe al pasar la cotización a la página).
- Desvío: el texto de la oferta tiene que tener lo ofrecido y lo pedido; no genérico, no repetido; el de serie tiene que
  coincidir con la serie de la fuente y la del plano.
- Extremos: el candidato no puede tener un tipo de extremo que el pedido no tiene (salvo el BW de una brida WN).
- Fuentes sin código: lo que pide el plano y la fuente no dice (revestimiento, costura, schedule por extremo, NACE)
  frena el paso a revisado hasta verificarlo en el original.
- Pendientes conocidos: texto de fuente escrito a mano que afirma cumplir; material no dicho por una planilla (aviso);
  código con el precio de otra pieza.
