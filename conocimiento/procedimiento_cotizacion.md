# Procedimiento de cotización (obligatorio)

Las reglas. El paso a paso con archivos y comandos está en [`guia_cotizacion.md`](guia_cotizacion.md).

Vigente desde el 27/10/2026. Se escribió a partir de los errores de la COT26-1003-001 (ver [`errores_y_lecciones.md`](errores_y_lecciones.md)). **Ningún número sale hacia el cliente, ni se le presenta a Matías como precio, sin haber pasado por estos pasos.** Si un paso no se puede cumplir, se dice explícitamente qué quedó sin verificar.

## Flujo unificado (30-10-2026)

Salió de comparar dos diseños hechos desde cero (el de Claude y el de un revisor independiente que leyó todo el repositorio) contra los errores registrados; Matías lo aprobó el 30-10-2026 **sin candados de estados**. Los principios:

1. **Lo que se ve, se avisa; aprueba el usuario.** Los controles de abajo marcados ■ son *pendientes*: se muestran claros en la página (Resumen, "Para revisar antes de enviar al cliente") y en `armar_cotizacion.py`, pero **no impiden generar las ofertas ni aprobar** (Matías, 30-10-2026: antes frenaban las ofertas y no se entendía; las aprobaciones las hace el usuario desde la página sin restricción). Cada pendiente se resuelve corrigiendo el dato o escribiendo la justificación en `cotizacion.json`.
2. **Todo requisito del cliente tiene destino.** Nada se pierde en silencio.
3. **La IA lee (dos veces, por separado); los programas calculan; las personas aprueban.**
4. **Lo que falta frena; no se completa con un valor por defecto.**
5. **Cada número importante se controla por otro camino** (renglones contra antecedentes, extremos contra dibujo).
6. **Cada error se vuelve una prueba automática** (`test_errores_sembrados.py`), no solo una nota.

| # | Paso | Quién | Sale | Control que lo cierra |
|---|---|---|---|---|
| 1 | Recepción: originales en `pedido/`, con su revisión. Si llega otra revisión del cliente, se compara con la anterior y se rehace lo que cambió | IA | inventario de documentos | — |
| 2 | **Matriz de requisitos** (P1): cada requisito del pedido (OC, pliego, ET, notas del plano, condiciones comerciales) con su texto literal, documento y página. **Las consultas al cliente salen ese mismo día** | IA | `pedido/requisitos.csv` | ■ requisitos: cada uno con destino `cumple`, `renglon` (posición o rubro), `desvio` o `exclusion` (con referencia a la oferta); `consulta` sin respuesta frena |
| 3 | **Doble lectura** de la tabla del cliente (P2): dos agentes o personas, cada uno sin ver al otro | 2 IA | `pedido/transcripcion.json` (A) y `transcripcion_b.json` (B) | ■ transcripción / doble lectura: el programa compara celda por celda; cada diferencia se resuelve mirando el original y se anota en `diferencias_resueltas`. Si no hay tabla del cliente (diseño de ITT), se declara `origen_lista: {tipo: diseno_itt, motivo}` |
| 4 | Lista de materiales: descripción y cantidad del cliente, atributos aparte, lo de ITT en `nota` | IA | `lista_materiales_plano.csv` | ERROR en `verificar_computo.py` si la descripción o la cantidad no son las del cliente |
| 5 | Cantidades derivadas (P3): kg, m², soldaduras junta por junta (taller/campo), roscados, PH, RX | programa | `precotizacion.md`, `ficha_rubros.md` | reglas con casos de prueba |
| 6 | Precios (P4): catálogo y antecedentes con compatibilidades; lo que no tiene precio queda en 0 y **va a Compras en ese momento** (la lista para Compras sale con el preliminar) | programa propone, IA elige | `cotizacion.json`, `compras/` | ERROR si es incompatible, sin fuente o sin fecha; ■ estimado > 15% del costo; ■ cotización de proveedor vencida (validez escrita o 30 días) |
| 7 | MO y servicios (P5) desde las cantidades del paso 5 y los requisitos del paso 2 | programa e IA | `cotizacion.json` | mismo alcance que la fuente |
| 8 | Plazo: llegada del último material + taller + dossier | programa | `plazo_calculado.md` | ■ plazo menor que el calculado sin justificar |
| 9 | Cálculo y documentos (P6, P7) | programa | planilla, informe | Python = planilla = página |
| 10 | Contraste por otro camino (P8): costo contra el antecedente más parecido con costo | programa | `comparacion_antecedentes.md` | ■ antecedentes: sin antecedente comparable o más de 15% sin explicar |
| 11 | Revisión independiente a ciegas (P9) | otro agente o persona | revisión en la bitácora | — |
| 12 | Ofertas (P9 bis) y aprobación de Matías o la dirección | programa y persona | `oferta/` | los pendientes se avisan; aprueba el usuario |
| 13 | Cierre (P10): resultado, costo real si se gana, y cada error nuevo con su prueba en `test_errores_sembrados.py` | persona y programa | `errores_y_lecciones.md`, prueba nueva | `verificar_todo.py` |

Justificaciones que levantan frenos (en `cotizacion.json`): `justificaciones.estimado`, `justificaciones.vencidas`, `justificaciones.antecedentes`, `plazo.justificacion`; por fuente, `validez_hasta` y `reconfirmado` (AAAA-MM-DD).

### Errores sembrados (validación del proceso)

`herramientas/test_errores_sembrados.py` mete cada error en una copia de la CAPEX y exige que un control lo frene. Hoy cubre: descripción con palabras agregadas (regla crítica), cantidad distinta de la del cliente (#6, #14, Camuzzi), posición faltante, fecha futura o supuesta (PC0), precio sin referencia (P4 ter), subtotal a mano, precio sin fuente, referencia incompatible (BSPT por NPT), sin transcripción, sin segunda lectura, lecturas distintas (NPT-M/NPT-H, #7), sin matriz de requisitos, requisito sin destino y consulta abierta (separador Camuzzi), estimado > 15% (#17), cotización vencida (#18), antecedentes sin explicar (#19) y plazo menor (YPF 120/180). **No cubre todavía:** factor 1,40 mal aplicado (#1, #4), alcance de MO distinto (#58), juntas contadas en kg (30-10), errores de tablas técnicas (espesores, HEB/UL) y de dimensionamiento de ingeniería (#82). Al anotar un error nuevo, sumar su siembra.

## Estados de una cotización

`borrador` → `revisado` (pasó P1–P9) → `aprobado` (Matías o la dirección) → `enviado` → `ganada / perdida`

- Solo una cotización **aprobada** puede enviarse al cliente. **El cotizador nunca envía nada al cliente.**
- Mientras esté en `borrador`, todo número que se muestre lleva la aclaración "borrador, sin revisar".
- El estado se anota al principio de `cotizacion.md` y en el encabezado del informe.

## Pasos

**P1. Leer el pedido completo.** Leer la orden o el pliego, el plano (tabla de materiales, notas y dibujo) y las especificaciones. Anotar requisitos, fechas, lugar de entrega, ensayos, pintura y marcas exigidas. Transcribir la tabla de materiales del plano **completa, con todas sus columnas** (posición, descripción, Ø, serie o schedule, material, extremos, modelo o fabricante, cantidad) en `pedido/lista_materiales_plano.csv`.

**P2. El cómputo copia el plano, renglón por renglón.** Una fila por posición del plano, con la **misma cantidad y unidad** del plano. Lo que se compra de más (tira mínima, sobrantes, cortes) va en una fila aparte con el sufijo `b` (ejemplo: `14b`), nunca mezclado. Descripción, Ø, serie, material y extremos se copian del plano. Si se ofrece otra cosa, se anota como desvío (P4).

**REGLA CRÍTICA — descripción del cliente (Matías, 29-10-2026):** en la descripción va siempre, sin excepción, el texto exacto del documento del cliente (plano, pliego o planilla), tal cual figura: sin corregir, traducir, abreviar ni agregar palabras ("RF", "radio largo", marcas, normas). Lo mismo con el material: se cotiza lo que pide el cliente. Lo que agrega ITT va en la columna `nota` de `lista_materiales_plano.csv`; el Ø va aparte. Si el cliente no indica cantidad y ITT la calcula, se aclara siempre en `cantidad_origen` ("El cliente no indica cantidad: calculada por ITT según el plano / la ET") y la oferta la marca con (*). Se copia de `pedido/transcripcion.json` y `verificar_computo.py` da error si no coincide.

**Todos los datos de cada material, en columnas (Matías, 03-11-2026):** catálogo, lista de materiales y planilla usan los mismos datos con los mismos nombres: tipo, Ø, Ø2, serie, schedule, espesor, material, extremos, cara, norma, marca, modelo, rango, trim, paso, costura, revestimiento, largo y medida. En `lista_materiales_plano.csv` se conservan las columnas literales del cliente y se suman esas columnas: `python herramientas/atributos_plano.py cotizaciones/<carpeta>` las completa leyendo el texto (sin pisar lo cargado), y lo que no está se completa a mano o se pide al cliente (`verificar_computo.py` avisa "faltan datos del pedido"). La búsqueda de antecedentes usa esos datos y lista toda diferencia (norma, rango, cara, marca…). La hoja Materiales de la planilla trae, por renglón, los datos del pedido, los del antecedente usado y los que faltan.

**Lista para Compras: ET y marcas (Matías, 06-11-2026).** Si un renglón remite a una ET ("S/ Esp. CAMUZZI" u otra), se busca esa ET en la base propia (`conocimiento/tecnico/`, `fuentes_originales/`, pedido) y en la web, y la columna "Material según la ET" (`compras.material[pos]`) dice lo que pide para ese caso, con la fuente (código, revisión y punto). Si no se encuentra, `compras.material_sin_et[pos]` dice qué se buscó y dónde (sale como "Sin dato: …"); `verificar_computo.py` avisa si falta. La columna del documento queda literal. Si el proyecto o el cliente tiene vendor list o listado de marcas aprobadas, la columna "Marcas aprobadas" lleva, por artículo, las marcas de ese listado con sus observaciones: se carga el listado en `conocimiento/comercial/listados_marcas.csv` (subgrupos con patrón, una vez por cliente o proyecto) y `herramientas/marcas_cliente.py` lo aplica solo en el repositorio y en la página; `compras.marcas[pos]` manda para un caso particular. Las anotaciones (`compras.notas`) llevan el resto del detalle para comprar.

**P3. Los extremos definen los procesos.** Recorrer la columna de extremos: cada BW, SW o NPT/BW es una soldadura que hay que ubicar en el dibujo (taller o campo) y contar. Cada rosca que haga ITT es un roscado. Las soldaduras se listan junta por junta en la fila de MO (ejemplo: "12–13, 13–14, cupla 23 sobre niple 4…"). Las pulgadas equivalentes salen de `tecnico/factores_soldadura.csv` y `tecnico/factores_accesorios.csv`.

**P4. Cada precio, con fuente y misma especificación.** Cada precio lleva proveedor, carpeta o documento de origen, fecha y **la especificación de lo que se cotizó**. Se compara con el plano campo por campo: Ø, serie, material de cuerpo y de trim, extremos o conexión, modelo. Si algo no coincide, o se ajusta el precio (y se dice cuánto y por qué) o se declara como desvío.
- **Un precio de memoria o de un resumen no vale.** Hay que abrir el documento original (planilla, PDF, captura).
- Un valor "aproximado", verbal o por WhatsApp es **estimado**: nunca es precio de base.
- Cada precio de base se marca `igual`, `similar` (con la diferencia) o `sin_ref`. Con piezas similares se arma el **presupuesto preliminar**. El **definitivo** necesita cotización de Compras con la especificación del plano para todo lo que pese en el precio o en lo que se le promete al cliente.
- `cot` solo cuando hay documento del proveedor con esa especificación. Un valor de una planilla interna de ITT es `ant`. Un recargo supuesto (por ejemplo "+30% por asiento metálico") es `est`.
- Hay que leer la especificación completa del documento del proveedor: modelo, código de trim (TRIM 8 = 13Cr, no 316), material de asientos, extremos (M-H, BW/NPT, BSPT vs. NPT).
- Se prefiere el precio más reciente **con la misma especificación**. Si es de más de 6 meses o el proveedor da una validez corta, se marca para actualizar.

**P4 compatibilidad (30-10-2026).** Un precio de otra pieza sirve de referencia solo si la norma permite el reemplazo: igual o superior en todo (material y grupo de B16.5, cara, rosca, schedule, servicio NACE). Sin material conocido no es similar. Lo aplica el buscador (`compatibilidad.py`, `conocimiento/tecnico/compatibilidades_LEEME.md`) y lo controla `verificar_computo.py` en P9 (error).

**P4 ter. Sin referencia no se adivina** (decisión de Matías, 28-10-2026). Si no hay precio de la pieza ni de un producto parecido (otra medida, serie o marca de la misma pieza), el renglón va en **0 con "SIN PRECIO: pedir cotización"** y entra en la lista para Compras. Un estimado solo vale si sale de una referencia concreta (pieza parecida, antecedente, tarifa × cantidad) que se cita. `verificar_computo.py` da error si encuentra un estimado "sin referencia" con precio.

**P4 bis. Ajuste por inflación.** Cada precio se actualiza desde su fecha hasta hoy con `conocimiento/costos/indices_ajuste.csv` (se arma con `herramientas/indices_inflacion.py`; se agregan los meses nuevos cuando se publican el IPC y el dólar). Materiales en dólares: CPI de EE.UU. MO, talleres y servicios locales: IPC del INDEC ÷ dólar BNA. **No usar una tasa anual fija:** en algunos años el costo local en dólares sube y en otros baja, según cuánto suba el dólar frente a la inflación. La planilla y el informe muestran el subtotal a la fecha del precio, el factor y el subtotal ajustado.

**P5. Mano de obra con el mismo alcance.** Para la MO de terceros se usa el presupuesto más reciente **de un trabajo equivalente**, y se anota qué incluye y qué no (corte, roscado, soldadura, PH, pintura, montaje, consumibles). Si hay varios, se muestran todos y se elige con criterio escrito.

**P6. Factores según la planilla de ITT.**
- Hay dos factores: **materiales** (materiales y contingencia) y **mano de obra y servicios** (MO propia o de terceros dentro del equipo, PH, pintura, END, calidad).
- Los dos van en **1,35** por defecto. El 1,40 solo se usa para MO que se vende sola. Las válvulas Taval, la caución y el transporte van a 1,00.
- Si se toma un criterio de una cotización anterior, hay que verificarlo en **su planilla original**, no en el resumen de la ficha.
- El factor final lo decide la dirección.

**P7. Los números salen de la herramienta, no del chat.** Todo total que se informe sale de `herramientas/armar_cotizacion.py`, que arma la planilla y el informe desde `cotizacion.json`, recalcula el precio en Python y lo compara con la planilla recalculada con LibreOffice. Si no coinciden, frena. No se escriben en un mensaje cuentas hechas a mano.

**P8. Contrastar con antecedentes.** Comparar con al menos dos cotizaciones parecidas (mismo cliente o mismo tipo de equipo) de `comercial/`, **costo contra costo** (Matías, 30-10-2026): `comparacion_antecedentes.md` muestra el costo por equipo y el reparto materiales / MO y servicios de cada antecedente que tiene planilla; el precio de venta queda solo como referencia. Si la diferencia es mayor al 15%, explicarla rubro por rubro **antes** de presentar el número.

**P9. Control automático y revisión independiente.**
1. Correr `python herramientas/armar_cotizacion.py <carpeta>` (incluye `verificar_computo.py`). Tiene que terminar sin errores. Los avisos se revisan uno por uno, también los de `verificacion_origen.md` (precios que no figuran tal cual en su documento de origen; solo avisa, no confirma nada).
1b. Sin errores de compatibilidad: ningún renglón con una referencia que la norma no permite (`verificar_computo.py` lo da como error).
2. Revisión independiente: alguien que no armó el cómputo (otro agente o una persona) compara la lista de materiales del plano con el cómputo y el informe, y busca cantidades, especificaciones, extremos, soldaduras y precios sin fuente. Lo que encuentre se corrige o se justifica.
3. Recién ahí la cotización pasa a `revisado`.

**P9 bis. Oferta al cliente.** La oferta técnica y la económica se generan con `armar_cotizacion.py` (o solo `python herramientas/generar_oferta.py cotizaciones/<carpeta>`). Usa la plantilla de ITT (`plantillas/oferta_itt_2026.docx`), los textos de `oferta.json` y los precios de la planilla (unitario redondeado × cantidad = total). Los datos pendientes van entre [corchetes] y salen resaltados en amarillo. La marca "BORRADOR – SIN REVISAR – NO ENVIAR" se quita solo cuando `oferta.json` tiene `"estado": "aprobado"`.

**P10. Registrar.** Guardar todo en `cotizaciones/<código>/`: el pedido, la lista del plano, el cómputo, el informe y la planilla. Cada error que se detecte, aunque sea a tiempo, se anota en [`errores_y_lecciones.md`](errores_y_lecciones.md), y si hace falta se ajusta este procedimiento.

## Lista de control antes de pedir aprobación

- [ ] Todas las posiciones del plano están en el cómputo, con la misma cantidad (`verificar_computo.py` sin errores).
- [ ] Extremos y soldaduras contados junta por junta, y separados entre taller y campo.
- [ ] Ningún precio de base estimado sin marcar. Lo estimado está listado y suma menos del 15% del costo, o está justificado.
- [ ] La especificación cotizada coincide con la del plano, o el desvío está declarado.
- [ ] La MO tiene el mismo alcance que el trabajo, con la fuente a la vista.
- [ ] Los factores son los de ITT (1,35 / 1,35). La dirección confirma el factor final.
- [ ] El informe y el Excel dan el mismo total.
- [ ] El precio está contrastado con 2 antecedentes y las diferencias explicadas.
- [ ] El plazo está calculado por el material más largo: **llegada del último material + taller + dossier, sin superponer**. Si no llega a la fecha del cliente o la oferta va fuera de término, la oferta lo dice.
- [ ] Ninguna cotización de proveedor está vencida al emitir la oferta, o está reconfirmada.
- [ ] La oferta no afirma "según pedido" ni "cumple" en ítems sin cotización con la especificación del plano.
- [ ] Desvíos, exclusiones, condiciones y consultas al cliente están escritos.
- [ ] Hubo revisión independiente.
