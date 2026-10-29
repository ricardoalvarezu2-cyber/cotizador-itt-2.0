# Prueba de usuario: vendedor con dislexia (29-10-2026)

Prueba hecha por un agente que hizo de vendedor de ITT con dislexia: no programa, se pierde con los bloques de texto y confunde palabras parecidas. Usó la página (`web/cotizador.html`) en un navegador automático, con una base en memoria, en escritorio (1300×900) y en celular (390×844). Las capturas están en `2026-10-29_prueba_usuario/`. No se tocó el código.

Lo que hice:
1. Una cotización nueva: COT26-1029-001, un puente de medición de gas 4" #600 para "Gasandes Patagonia S.A." (cliente inventado), con 10 materiales del catálogo.
2. La MO y los servicios, el plazo y los datos de la oferta.
3. En la CAPEX cambié la cantidad y el precio de la válvula de retención (2 → 3 y 533 → 480).
4. Leí los avisos.
5. Miré el resumen, el informe y la oferta económica.

## Puntaje: 5 de 10

Para cargar materiales anda bien. El problema está en MO, en la oferta y en los avisos: ahí hay que saber cosas que la pantalla no dice. Además encontré un error que podría llegarle al cliente (el problema 1).

## Lo que me resultó fácil

- **La lista de inicio y "Nueva cotización".** Un solo botón grande y claro.
- **Los pasos numerados 1 a 6 en pestañas.** Sé en qué paso estoy y cuál sigue.
- **Los cuatro números grandes de arriba** (costo, precio unitario, cantidad y total). Están siempre a la vista y cambian al momento.
- **El buscador de materiales.** Escribí "caño 4 sch 80" o "brida 4 600 WN" y salió lo correcto. Cada resultado tiene el precio grande a la derecha, con la fecha, y el botón Agregar con la cantidad al lado.
- **La tabla de materiales.** La cantidad y el precio se cambian en la misma fila, sin abrir nada.
- **El aviso del plazo.** "El plazo ofrecido (120 d) no tiene el margen de 15-20% (sugerido 132-138 d)" es claro: dice qué está mal y qué número poner.
- **La oferta económica en pantalla.** Se ve como un documento de verdad y lleva el sello "BORRADOR – SIN REVISAR – NO ENVIAR".
- **En el celular** las pestañas se acomodan en dos columnas y los botones se tocan bien.

## Dónde me trabé (de lo que más me molestó a lo que menos)

1. **Cobro el transporte y la oferta dice que no está incluido.** En MO › Transporte cargué USD 850 con destino Neuquén. Ese importe entró en "Servicios e insumos" (2.149,11 = 850 + RX 600 + pintura 165 + prueba hidráulica 84 + horas 450), o sea que está dentro del precio. Pero el resumen dice "Flete + embalaje 0,00 · no incluido", y la oferta dice "Precio en planta ITT (EXW Quilmes Oeste). El flete hasta [lugar de entrega del cliente] puede cotizarse por separado" y "Lugar de entrega: planta de ITT". Yo no me habría dado cuenta, y al cliente le llega una oferta que se contradice. (Captura 1.)
2. **En MO todo arranca en "sin costo" y no se entiende por qué.** Todos los rubros vienen con "Antecedentes" marcado (parece ya elegido) y 0,00. Apreté "Recalcular" y siguió en 0. Recién al abrir cada rubro con la flechita apareció el botón "Aplicar al costo", y hay que apretarlo uno por uno. Nada avisa que ese paso existe.
3. **Radiografía se contradice.** Arriba dice "4 juntas a tope" y adentro dice "Sin juntas a tope ni placas: completá los datos del plano y Recalculá". No hay ningún lugar para cargar el % de RX ni los "datos del plano". Lo resolví pasando a "Manual" y escribiendo un número a ojo. "Horas de ITT" dice que se estima con la "precotización de Claude Code", que yo no puedo correr. Las cargué desde el catálogo de MO. (Captura 2.)
4. **Los 17 avisos de mi cotización (59 en la CAPEX) son una pared de texto.** Están al fondo de "Resumen", en una lista larga que se repite: cada material aparece dos veces ("pieza SIMILAR…" y "precio de hace 8 meses…"). Hay textos cortados ("sin co"), y no puedo tocar un aviso para ir a la fila que hay que arreglar. La pestaña muestra "17 avisos" en rojo aunque abajo dice "0 para corregir": me asusté por nada. Además, todo lo que agregué desde el catálogo salió como "pieza SIMILAR (completar en qué difiere)", aunque elegí exactamente lo que quería. (Captura 3.)
5. **La oferta no toma lo que ya cargué.** En "Oferta" el cliente aparecía vacío, aunque ya lo había cargado en Datos. El plazo seguía en "[días]", aunque en Plazo había puesto 135. El nombre del archivo decía "[COT26-CCCC-NNN] - [CLIENTE]", y la Revisión era "A" (en Datos es "Rev 0"). Tuve que escribir todo dos veces. Encima la pestaña tiene unos 20 cuadros de texto largos con [corchetes] por todos lados, y en la vista previa los corchetes no se resaltan: es fácil mandar "[el pedido de cotización N°]" sin darse cuenta.
6. **El subtotal de materiales aparece vacío.** Al entrar a Materiales, la fila "Subtotal por puente de medición" está en blanco. Recién muestra el número después de cambiar algo. Pensé que no había sumado. (Captura 4.)
7. **Para borrar un material hay que adivinar dónde está el botón.** No hay un botón de borrar en la fila. Hay que entrar a "Editar", bajar hasta el fondo de un formulario largo y ahí aparece "Quitar ítem". Además lo borra sin preguntar. (Captura 5.)
8. **El buscador del catálogo de MO se cierra solo.** Después de agregar una hora de ingeniería, la sección se cerró y tuve que abrirla otra vez para agregar la de calidad.
9. **No sé cuánto cambió el total.** En la CAPEX cambié cantidad y precio. El total pasó de 15.241,18 a 16.313,26, pero tuve que acordarme del número de antes: la página no dice "+1.072,08". Y la columna "USD ajustado" (1.457,54 cuando 3 × 480 = 1.440) no explica de dónde sale la diferencia.
10. **El informe escribe los números distinto.** El informe muestra "USD 7,153.05" y la página "7.153,05". Para mí eso es un número distinto: me tuve que frenar a pensar. Los avisos también usan punto: "USD 1440.00".
11. **En el celular** la tabla de materiales queda cortada a la derecha (no se ven la unidad, el precio ni el estado). Además, hay que pasar varias pantallas de encabezado antes de llegar a la tabla.

## Palabras y textos que no entendí o que me confundieron

- **"sin costo" (amarillo) y "sin precio" (rojo)**: son casi la misma palabra con dos colores. No sé cuál es más grave.
- **"Antecedentes"**, como botón que parece apretado aunque no aplicó nada.
- **"Revisar · 2"**, en cada fila: ¿revisar qué? Hay que abrir la flechita para saberlo.
- **"(P8)"**, en "Antecedentes parecidos (P8)": no sé qué es P8.
- **"familia OT"**.
- **"extremos_campo"**: parece un nombre de columna de programador.
- **"ficha_rubros.md (pedir con la ficha)"**.
- **"WPS/PQR", "WPQ"**: los entiendo del trabajo, pero mezclados con texto chico cansan.
- **"PR" y "PT"**, en las válvulas esféricas (paso reducido y paso total): son dos letras casi iguales con precios de 966 y 1.646, y nada lo explica.
- **"S/C" y "c/c"**, en los caños.
- **"Sin superponer"** y **"margen de 15-20%: 0-0 días"**.
- **"Factor de válvulas Taval (todas)" = 1**: no sabía que con eso las válvulas Taval se venden al costo. En el resumen aparece "× 1" sin ninguna explicación.
- **"Equipo (singular)" y "Equipo (plural)"**: no entendí para qué son hasta que vi "1 puentes de medición" en el informe.
- **"Tipo de cambio 1550"** en Datos, contra "BNA 1.541,43" arriba: ¿cuál vale?
- **"COT26-CCCC-NNN"**: no sé qué número poner. Inventé COT26-1029-001.
- **"Choose File / No file chosen"**: está en inglés.
- **"Cantidad de equipos" en 2** al crear la cotización: casi cotizo dos puentes sin querer.

## Qué cambiaría (concreto)

1. **Transporte**: si tiene precio, que la oferta diga "Entrega en [destino], flete incluido", que cambie la Nota de flete y el Lugar de entrega, y que el resumen lo muestre en la fila "Flete". Si no, que haya un aviso "para corregir".
2. **MO**: que "Antecedentes" aplique la tarifa sola cuando hay una sola posible, o que cada rubro en 0 muestre un botón grande "Aplicar USD 273" en la misma fila, sin tener que abrirla. "Recalcular" tiene que dejar los costos cargados, no en 0.
3. **RX**: agregar un campo "% de radiografía" en el rubro, y no mostrar "sin juntas" cuando hay juntas.
4. **Avisos**:
   - Ponerlos arriba, en una caja con un número grande por color (rojo = corregir, amarillo = revisar).
   - Juntar los avisos de cada material en una sola línea.
   - Que tocar un aviso lleve a la fila.
   - No marcar como "SIMILAR" lo que se agregó desde el catálogo sin plano.
   - Que la pestaña muestre en rojo solo los "para corregir".
5. **Oferta**: llenar sola los datos que ya están en Datos y en Plazo (cliente, comprador, plazo en días y en texto, nombre de archivo, revisión). Mostrar los [corchetes] resaltados en amarillo también en la vista previa, con un contador del tipo "Faltan 6 datos".
6. **Materiales**: un tachito en cada fila (con "¿Seguro?" y Deshacer), y el subtotal calculado desde que se abre la pestaña.
7. **Al cambiar un número**, mostrar unos segundos "Total: 15.241,18 → 16.313,26 (+1.072,08)".
8. **Un solo formato de número** en todo (1.234,56): página, informe, avisos y Excel.
9. **Palabras**: cambiar "sin costo" y "sin precio" por "Falta precio" (una sola palabra y un solo color). Cambiar "Revisar · 2" por "2 dudas". Sacar P8, OT, extremos_campo y ficha_rubros.md, o explicarlos con un globito. En el resultado de la búsqueda, PR y PT con texto: "paso reducido" o "paso total".
10. **Nueva cotización**: que pida el cliente y el título antes de crearla, que proponga el código siguiente y que arranque con cantidad 1.
11. **Celular**: que la tabla de materiales se vea como tarjetas (como el buscador), y que el encabezado se achique al bajar.
12. **Buscador**: que "brida ciega 4 600" traiga primero bridas ciegas (hoy trae primero una junta) y que "te 4 sch 80" traiga primero la te normal antes que las de reducción.
