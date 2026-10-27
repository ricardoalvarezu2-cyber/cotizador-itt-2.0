# Procedimiento de cotización (obligatorio)

Las reglas. El paso a paso con archivos y comandos está en [`guia_cotizacion.md`](guia_cotizacion.md).

Vigente desde el 27/10/2026. Se escribió a partir de los errores de la COT26-1003-001 (ver [`errores_y_lecciones.md`](errores_y_lecciones.md)). **Ningún número sale hacia el cliente, ni se le presenta a Matías como precio, sin haber pasado por estos pasos.** Si un paso no se puede cumplir, se dice explícitamente qué quedó sin verificar.

## Estados de una cotización

`borrador` → `revisado` (pasó P1–P9) → `aprobado` (Matías o la dirección) → `enviado` → `ganada / perdida`

- Solo una cotización **aprobada** puede enviarse al cliente. **El cotizador nunca envía nada al cliente.**
- Mientras esté en `borrador`, todo número que se muestre lleva la aclaración "borrador, sin revisar".
- El estado se anota al principio de `cotizacion.md` y en el encabezado del informe.

## Pasos

**P1. Leer el pedido completo.** Leer la orden o el pliego, el plano (tabla de materiales, notas y dibujo) y las especificaciones. Anotar requisitos, fechas, lugar de entrega, ensayos, pintura y marcas exigidas. Transcribir la tabla de materiales del plano **completa, con todas sus columnas** (posición, descripción, Ø, serie o schedule, material, extremos, modelo o fabricante, cantidad) en `pedido/lista_materiales_plano.csv`.

**P2. El cómputo copia el plano, renglón por renglón.** Una fila por posición del plano, con la **misma cantidad y unidad** del plano. Lo que se compra de más (tira mínima, sobrantes, cortes) va en una fila aparte con el sufijo `b` (ejemplo: `14b`), nunca mezclado. Descripción, Ø, serie, material y extremos se copian del plano. Si se ofrece otra cosa, se anota como desvío (P4).

**P3. Los extremos definen los procesos.** Recorrer la columna de extremos: cada BW, SW o NPT/BW es una soldadura que hay que ubicar en el dibujo (taller o campo) y contar. Cada rosca que haga ITT es un roscado. Las soldaduras se listan junta por junta en la fila de MO (ejemplo: "12–13, 13–14, cupla 23 sobre niple 4…"). Las pulgadas equivalentes salen de `tecnico/factores_soldadura.csv` y `tecnico/factores_accesorios.csv`.

**P4. Cada precio, con fuente y misma especificación.** Cada precio lleva proveedor, carpeta o documento de origen, fecha y **la especificación de lo que se cotizó**. Se compara con el plano campo por campo: Ø, serie, material de cuerpo y de trim, extremos o conexión, modelo. Si algo no coincide, o se ajusta el precio (y se dice cuánto y por qué) o se declara como desvío.
- **Un precio de memoria o de un resumen no vale.** Hay que abrir el documento original (planilla, PDF, captura).
- Un valor "aproximado", verbal o por WhatsApp es **estimado**: nunca es precio de base.
- `cot` solo cuando hay documento del proveedor con esa especificación. Un valor de una planilla interna de ITT es `ant`. Un recargo supuesto (por ejemplo "+30% por asiento metálico") es `est`.
- Hay que leer la especificación completa del documento del proveedor: modelo, código de trim (TRIM 8 = 13Cr, no 316), material de asientos, extremos (M-H, BW/NPT, BSPT vs. NPT).
- Se prefiere el precio más reciente **con la misma especificación**. Si es de más de 6 meses o el proveedor da una validez corta, se marca para actualizar.

**P4 bis. Ajuste por inflación.** Cada precio se actualiza desde su fecha hasta hoy con `conocimiento/costos/indices_ajuste.csv` (se arma con `herramientas/indices_inflacion.py`; se agregan los meses nuevos cuando se publican el IPC y el dólar). Materiales en dólares: CPI de EE.UU. MO, talleres y servicios locales: IPC del INDEC ÷ dólar BNA. **No usar una tasa anual fija:** en algunos años el costo local en dólares sube y en otros baja, según cuánto suba el dólar frente a la inflación. La planilla y el informe muestran el subtotal a la fecha del precio, el factor y el subtotal ajustado.

**P5. Mano de obra con el mismo alcance.** Para la MO de terceros se usa el presupuesto más reciente **de un trabajo equivalente**, y se anota qué incluye y qué no (corte, roscado, soldadura, PH, pintura, montaje, consumibles). Si hay varios, se muestran todos y se elige con criterio escrito.

**P6. Factores según la planilla de ITT.**
- Hay dos factores: **materiales** (materiales y contingencia) y **mano de obra y servicios** (MO propia o de terceros dentro del equipo, PH, pintura, END, calidad).
- Los dos van en **1,35** por defecto. El 1,40 solo se usa para MO que se vende sola. Las válvulas Taval, la caución y el transporte van a 1,00.
- Si se toma un criterio de una cotización anterior, hay que verificarlo en **su planilla original**, no en el resumen de la ficha.
- El factor final lo decide la dirección.

**P7. Los números salen de la herramienta, no del chat.** Todo total que se informe sale de `herramientas/armar_cotizacion.py`, que arma la planilla y el informe desde `cotizacion.json`, recalcula el precio en Python y lo compara con la planilla recalculada con LibreOffice. Si no coinciden, frena. No se escriben en un mensaje cuentas hechas a mano.

**P8. Contrastar con antecedentes.** Comparar con al menos dos cotizaciones parecidas (mismo cliente o mismo tipo de equipo) de `comercial/`. Si la diferencia es mayor al 15%, explicarla rubro por rubro **antes** de presentar el número.

**P9. Control automático y revisión independiente.**
1. Correr `python herramientas/armar_cotizacion.py <carpeta>` (incluye `verificar_computo.py`). Tiene que terminar sin errores. Los avisos se revisan uno por uno.
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
