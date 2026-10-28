# Prueba de uso del Cotizador ITT desde el lado del vendedor

Fecha: 28-10-2026. Lo probé haciéndome pasar por un vendedor de ITT que cotiza todos los días: sabe de cañerías y válvulas y no sabe de computación.
Probé la página local (`web/cotizador.html`) con Playwright, en pantalla de computadora (1280x900) y de celular (390x844). La base, las descargas, el chat y el conector estaban simulados con `mock.js` y `mock2.js`.
Capturas: `/tmp/claude-0/-home-user-cotizador-itt/82ad64dc-b6db-5ba7-866e-adf8ec6ac548/scratchpad/agentes/usuario/cap/` (en adelante, `cap/`). Scripts: `.../agentes/usuario/s*.js`.

Aclaraciones sobre el entorno de prueba:
- Las fuentes de Google y las librerías de los CDN se sirvieron desde una copia local, porque a mitad de la prueba la carga desde la red se colgaba.
- Los textos nativos del navegador ("Choose Files") salen en inglés por el Chromium sin idioma. En un Chrome en español saldrían bien.
- El chat de Claude estaba simulado, así que no evalúo cómo responde.

---

## 1. Primera impresión

- **Lo bueno:** la pantalla de inicio es limpia: un botón "Nueva cotización" y una tabla con código, cliente, estado, unitario y total (`cap/01_inicio.png`). Se ve profesional y se parece a los informes de ITT. Arriba dice el dólar del día ("BNA 1.540,74 al 28-10-2026"), y eso da confianza.
- **Por dónde empiezo:** se entiende rápido (Nueva cotización o clic en la existente). Pero no hay ninguna explicación de qué es la página ni del orden de trabajo recomendado (Datos → Materiales → MO → Plazo → Oferta → Resumen).
- Al abrir la CAPEX (`cap/02_capex.png`) se ven costo, precio unitario, cantidad y total, con el cartel "Borrador, sin revisar". **Eso se entiende bien.** Lo que confunde:
  - Los factores aparecen como "1.35 / 1.35", con punto, mientras el resto de los números va con coma.
  - Arriba dice "ajuste por inflación incluido 162,77", pero después hay decenas de avisos "precio de hace 10 meses, actualizar". No queda claro si ya está actualizado o no.
  - La pestaña Resumen abre con **59 avisos** en una lista larguísima (`cap/02_capex_full.png`) que mezcla lo importante con lo menor. No sé por dónde empezar.

## 2. Recorrido tarea por tarea

### 2.1 Abrir la CAPEX y entender estado, costo, precio y avisos
- **Estado:** los 4 botones (borrador / revisado / aprobado / enviado) se entienden. El cartel amarillo explica que los números son borrador. Bien.
- **Tabla "Costo y precio por puente":** la fila "Costo" muestra 5.644,88 y 7.620,59 en la columna de los factores, sin encabezado. Me costó entender que 7.620,59 es el precio de venta.
- **Escenarios de factor:** útiles y claros. El margen en % se agradece.
- **Antecedentes (P8):**
  - "P8" es jerga interna.
  - La columna "Esta vs. antecedente" muestra "-50%" o "otra escala", y la de "Materiales" muestra 0%, 100% o 90% sin explicar qué mide.
  - Aparece "precio unitario 97.461 USD" para "24 puentes de medición 2"", y no sé si es el precio de un puente o del lote. "APSA: Puente 315 USD" parece un error del índice.
- **Avisos:** usan códigos internos (PIN, CAL, INS, PH, MO) y frases como "precio del período con cepo sin tipo de cambio explícito". Un vendedor no sabe qué tiene que hacer con eso.
- **Materiales** (`cap/03_tab_materiales.png`): la tabla es completa (fuente, fecha, Igual/Similar, avisos). La columna "USD ajustado" es el **total de la línea con inflación**, pero el nombre no lo dice: parece un unitario.
- **Datos** (`cap/03_tab_datos.png`): está bien organizado. Llama la atención que el flete use TC 1450, que la cotización nueva traiga 1550 y que arriba diga 1.540,74.

### 2.2 Crear "2 skids de medición 3" #600 para YPF"
1. **Nueva cotización** (`cap/10_nueva.png`):
   - Abre en Datos, con el código "COT26-CCCC-NNN" y el equipo "puente/puentes" por defecto. Tuve que cambiarlos a mano.
   - Al elegir el cliente "YPF S.A." de la lista (aparece con su código 0330), **el "Código de cliente ITT" no se completa solo**.
2. **Parámetros:**
   - Al tipear "1,4" en Factor de materiales quedó **14**. El precio se multiplicó por 10 sin ningún aviso (`cap/13_factor_coma.png`).
   - Al tipear "3.500.000" en Flete ARS quedó **3,5**.
   - Lo probé con el navegador en es-AR y en en-US: pasa igual.
   - La fecha acepta 28/10/2026 y la convierte a 28-10-2026: bien. Una fecha inválida se pinta en rojo, pero no dice por qué.
3. **Buscar materiales:**
   - El buscador está **al final de la pestaña**. En la CAPEX hay que bajar más allá de los 27 ítems para encontrarlo (`cap/03_tab_materiales.png`).
   - La carátula ocupa unos 460 px fijos antes de cualquier contenido.
   - "esferica 3 600" encuentra 2 resultados.
   - "valvula esferica 3 serie 600 bridada" encuentra **0**: no entiende "bridada" por RF ni "serie".
   - "placa orificio 3" y "medidor turbina 3" dan 0 (lógico si no hay en el catálogo, pero sería mejor que lo sugiera cargar a mano o pedir cotización).
   - "esferica 2 600" trae una válvula de **Ø12"** (toma el "2" de "12").
   - "1 1/2 npt" trae primero un buje 1" x 1/2".
4. **Filtro por familia:**
   - Al elegir Válvulas aparecen filtros (tipo, Ø, serie, material, trim, extremos, marca) (`cap/24_filtro_esf3_600.png`). Muy bueno como idea.
   - Los diámetros aparecen como "0.5"", "1.5"" en lugar de 1/2" o 1 1/2", que es como habla un vendedor.
   - Con esférica + 3" + 600 el contador sigue en "**120 resultado(s)**". Los filtros no filtran: ordenan y marcan Similar. Entre los "similares" aparecen esféricas #300 motorizadas de USD 3.406. Confunde.
   - Las dos esféricas 3" #600 salen como SIMILAR "porque difiere en extremos RF (no pedido)", cuando yo no pedí ningún extremo.
   - La primera, un "estimado (cepo)" de 2025 llevado a "dólar blue", aparece **antes** que la de lista de Taval de 2026.
   - En Bridas 3" 600 el primer resultado fue una brida API 6A 2-9/16" 10K.
   - La brida WNRF 3" 600# a **USD 19,78** parece barata para lo que es; habría que confirmar el dato en el catálogo.
5. **Selección múltiple:**
   - Funciona: marqué dos válvulas, cambié a bridas, marqué una más y "Agregar seleccionados" sumó las 3 (`cap/25_seleccion.png`).
   - Lo que no se ve es qué cantidad entra con cada uno: entraron todos con cantidad 1.
6. **Ítem a mano** (`cap/30_manual_vacio.png`):
   - El formulario es claro, y si falta algo lo dice ("Falta la descripción").
   - **Pero** guardé un medidor ultrasónico de USD 18.500 **sin origen ni documento**. Quedó marcado "Igual" y "Cotización" porque son los valores por defecto, y **no generó ningún aviso**. Va en contra de la regla "cada precio verificado en el documento original".
7. **Calculadoras (MO y servicios)** (`cap/41_soldaduras.png`):
   - Soldaduras: cargué 3" sch80 con 8 BW y 2 cuplas, más 1/2" con 4 SW. El cálculo da 45,81 pulgadas equivalentes por USD 19,73 y se entiende.
   - El texto "BW se suman de a dos extremos" no deja claro si hay que cargar juntas o extremos.
   - La tarifa es de 10-2024 (época del cepo) y la calculadora no avisa nada.
   - La calculadora no lee los ítems ya cargados (bridas WN, cuplas): hay que contar las juntas a mano.
   - RX, prueba hidráulica y pintura: se agregan con un clic, bien.
   - "Calcular m² de los caños cargados" dio 1,68 m², que no sirve para un skid porque no cuenta la estructura. Lo aclara en el mensaje emergente, pero igual lo deja cargar.
   - Al buscar MO "armado skid", el primer resultado es "Hs planta para movimientos internos". "ledesma" da 92 resultados.
8. **Plazo** (`cap/51_plazo.png`):
   - Es la pestaña más clara de todas: tareas, plazo calculado y margen de 15–20%.
   - La cotización nueva arranca con "60 días desde OC" fijo.
   - Cambié el plazo a 175 días y en la pestaña Oferta **siguió en 60**, tanto en el ítem como en "PLAZO DE ENTREGA".
9. **Oferta:**
   - La cotización nueva viene **con todos los textos de la CAPEX** (ver el error 1).
   - Cliente, contacto y proyecto quedan vacíos aunque cargué YPF en Datos.
10. **Avisos y antecedentes** (`cap/53_resumen.png`):
    - Los antecedentes son razonables (TAVAL/70 YPF, Endress).
    - Los avisos dicen "**0 para corregir**" aunque la cotización del skid **no tiene ni un peso de mano de obra** y tiene un precio de USD 18.500 sin documento.
    - Los avisos muestran importes con formato inglés ("USD 2459.79", "USD 295.75") y el importe es el total de la línea, no el unitario.
11. **Vista previa** (`cap/60_vista_tecnica.png`, `cap/60_vista_economica.png`):
    - Se ve como la oferta de ITT, con el sello BORRADOR – SIN REVISAR – NO ENVIAR. Bien.
    - **Pero la oferta del skid de YPF dice "PUENTE ARMADO BBO MEC 1500, OQ 8209, artículo C01A930098080", con cliente vacío.**
    - El precio de la económica sale en formato inglés: "USD 30,423.60".
12. **Descargas:**
    - El zip y el Excel bajaron, pero con el nombre "**COT26-1003-001 - CAPEX OQ8209 - PUENTE ARMADO BBO MEC 1500**.zip" (`.../usuario/descargas/`).
    - En el Excel, el subtítulo quedó "[cantidad] [equipo] · plano [número]", sin reemplazar.
13. **Deshacer / rehacer:**
    - Funcionan con los botones y con Ctrl+Z / Ctrl+Y.
    - "Quitar" un ítem no pide confirmación, pero se puede deshacer, así que está bien.
    - Ctrl+Z adentro de un campo deshace el último cambio de la cotización, no lo que estoy tipeando. Es raro.
14. **Filtrar y ordenar ítems:** funciona y se entiende (Todos / Con avisos / Para corregir / Sin precio / Estimados / Similares; orden por posición, importe, descripción y precio más viejo) (`cap/70_filtro_similares.png`).
15. **Estado:**
    - Pasé de borrador a "**enviado**" con un solo clic: sin confirmación, sin revisión y con avisos pendientes.
    - El cartel de "borrador" desapareció (`cap/61_enviado.png`).

### 2.3 Catálogos (consultar un precio sin cotización)
- Se entiende (`cap/80_catalogos.png`, `cap/81_catalogo_busq.png`). Cada resultado muestra el precio, la fecha, el tipo y la ruta de origen.
- Las rutas `Z:\VENTAS\...` largas meten mucho ruido visual.
- "2 precios en el historial (416,00 a 416,00)" no se puede abrir para ver el historial.
- Un resultado muestra "USD 4.834" y en la descripción dice "USD 2406". No sé cuál vale.
- No hay forma de llevar un precio a una cotización desde acá (dice "abrí una cotización"). Es aceptable.

### 2.4 Pedidos
- Es simple y claro (`cap/90_pedidos.png`, `cap/93_pedido_enviado.png`): tipo, cotización, texto y archivo. "Guardar y mandar" lo dejó en "ENVIADO, mandado a Claude Code". Si no hay texto ni archivo, avisa.
- Confusión: el estado "**ENVIADO**" del pedido es la misma palabra que el estado "enviado" (al cliente) de una cotización.
- "Claude Code" es jerga para un vendedor.
- El desplegable "Qué es" corta el texto.

### 2.5 Firmantes
- Agregar y editar anda bien, y si falta el nombre lo avisa (`cap/95_firmantes.png`, `cap/96_firmante_nuevo.png`).
- **No se puede borrar** un firmante.
- El email no se valida.

### 2.6 Fechas y números
- **Fechas:** en la pantalla las vi todas en DD-MM-AAAA (lista, fuentes, avisos, oferta, pedidos). Bien. La única excepción es la hora "guardado 10:01 a. m.", que está bien.
- **Números con formato equivocado:**
  - Campos de factor ("1.35"), precios unitarios en la tabla ("614.948", que un vendedor lee como 614 mil), cantidades ("45.812 pulg"), diámetros ("0.5"") y TC ("1550").
  - Montos en los avisos ("USD 2459.79").
  - Ofertas Word y PDF ("USD 30,423.60", con `toLocaleString("en-US")` en `web/src/documentos.js` línea 9).
  - Factores de escenarios y antecedentes ("1.25", "1.307").

### 2.7 Celular (`cap/m_combo.png`, `cap/m_materiales_crop.png`)
- Las pantallas de inicio y de cotización se adaptan bien (tarjetas, sin desplazamiento horizontal de la página).
- El menú corta "Firman…" y las pestañas cortan "Pla…", sin ninguna señal de que se puede deslizar.
- La tabla de materiales mide 943 px en una pantalla de 340: precio, fuente y total quedan fuera de la vista y cada fila ocupa media pantalla. Para trabajar ítems en el celular no sirve. Para consultar, sí.
- Varios botones miden 25 px de alto (estado, Deshacer, Editar, Quitar), por debajo de los 44 px recomendados para el dedo.
- El chat ocupa toda la pantalla, bien.

### 2.8 Accesibilidad básica
- El contraste está bien en general y el foco se ve (contorno azul).
- **Teclado:**
  - Al activar una pestaña con Enter el foco se va al principio de la página.
  - Las flechas no cambian de pestaña.
  - Al abrir "Editar" el foco no entra al cuadro y **Escape no lo cierra**.
  - En Tareas, después de editar con Tab el foco también se pierde.
- Los 81 campos de las tablas no tienen etiqueta para lector de pantalla.

---

## 3. Errores encontrados (con pasos para reproducir)

| # | Gravedad | Error | Cómo reproducirlo |
|---|---|---|---|
| 1 | **Crítica** | Una cotización nueva hereda toda la oferta de la CAPEX (objeto, ítem "PUENTE ARMADO BBO MEC 1500", código C01A930098080, documentos OQ 8209, aclaraciones con posiciones del plano CAPEX, nombre de archivo). Las ofertas y el zip de otro cliente salen con datos de CAPEX. Causa: `cotizaciones/_plantilla/oferta.json` tiene el contenido real de la CAPEX y `crearCotizacion` (`web/src/app.js:143`) lo copia. | Nueva cotización → pestaña Oferta, o Resumen → Oferta técnica, o Descargar todo. `cap/60_vista_tecnica.png`, `cap/60_vista_economica.png`. |
| 2 | **Crítica** | Los campos numéricos no aceptan formato argentino: "1,4" queda 14 y "3.500.000" queda 3,5, sin aviso. El precio se multiplica por 10. | Datos → Factor de materiales → tipear 1,4. `cap/13_factor_coma.png`. |
| 3 | Alta | Se puede marcar "aprobado" o "enviado" con un clic, sin confirmación y con avisos o mano de obra en cero. | Cualquier cotización → botón "enviado". `cap/61_enviado.png`. |
| 4 | Alta | El plazo de la pestaña Plazo no pasa a la Oferta (ítem y condiciones siguen en 60 días). | Plazo → Días 175 → Oferta: sigue "60 días corridos". |
| 5 | Alta | El cliente cargado en Datos no pasa a la Oferta (encabezado "Cliente:" vacío). | Nueva → Datos: cliente YPF S.A. → vista de la oferta. |
| 6 | Alta | Los avisos no detectan una cotización sin mano de obra ni un ítem cargado a mano sin origen; muestran "0 para corregir". | Nueva con 4 materiales y 0 MO → Resumen. `cap/53_resumen.png`. |
| 7 | Media | La fila "Subtotal por puente/skid" de Materiales y de MO aparece **vacía** hasta que se edita una celda (solo la completa `refrescar()`, no el primer render). | Abrir la CAPEX → Materiales → bajar al final. `cap/04_subtotal.png`. |
| 8 | Media | El ítem a mano trae por defecto "Igual" y "Cotización" y no exige origen. | Materiales → Cargar a mano → completar descripción, precio, proveedor y fecha → Guardar. |
| 9 | Media | Los filtros de familia no reducen el contador ("120 resultados" con esférica 3" 600) y marcan "difiere en extremos" aunque no se pidieron extremos. | Materiales → Familia Válvulas → esférica, 3", 600. `cap/24_filtro_esf3_600.png`. |
| 10 | Media | El buscador toma "2" dentro de "12" ("esferica 2 600" trae una Ø12"), y "1 1/2" trae piezas de 1" x 1/2". | Catálogos → "esferica 2 600". `cap/81_catalogo_busq.png`. |
| 11 | Media | Números en formato inglés en avisos, campos y ofertas ("USD 2459.79", "614.948", "USD 30,423.60"). | Ver 2.6. |
| 12 | Baja | Excel: subtítulo "[cantidad] [equipo] · plano [número]" sin reemplazar. | Descargar 1_Presupuesto.xlsx de una cotización nueva. |
| 13 | Baja | En los cuadros de diálogo, Escape no cierra y el foco no entra; al cambiar de pestaña con Enter se pierde el foco. | Editar un ítem → Escape. |
| 14 | Baja | No se puede borrar un firmante. | Firmantes. |
| 15 | Baja | Typo en el catálogo: "levado a dólar blue" (dice "levado" en vez de "llevado"). Además, usar el dólar blue choca con la regla de no mezclar cotizaciones del dólar en una serie. | Buscar "esferica 3 600" → resultado VAL-03253. |

## 4. Cosas confusas
- **Dos plazos** (pestaña Plazo y "Plazo de entrega (días)" en Oferta) que no se sincronizan.
- **Tres tipos de cambio distintos** a la vista: 1.540,74 arriba, 1550 en una cotización nueva y 1450 en la CAPEX.
- "USD ajustado" (es el total de la línea con inflación), "Contingencia", "Factor flete", "pulg-diám-eq".
- Jerga interna: "P8", "cepo", "sin tipo de cambio explícito", códigos PIN/CAL/INS/PH, "Claude Code", "estimado (cepo)".
- "Igual" contra "Similar": la idea es buena, pero el sistema marca Similar por campos que no pedí.
- "enviado" tiene dos significados (pedido a Claude o cotización al cliente).
- 59 avisos sin agrupar ni priorizar. Faltan "¿qué hago con esto?" y un enlace al ítem.
- El estado "guardado" aparece en letra chica gris. Recién al ver "cambios sin guardar…" uno entiende que guarda solo.

## 5. Sugerencias, ordenadas por impacto
1. **Plantilla de oferta neutra** para cotizaciones nuevas: textos con [corchetes] y cliente, título, plazo y nombre de archivo tomados de Datos y Plazo. Es el riesgo más grande, porque una oferta con datos de otro cliente puede llegar a YPF.
2. **Campos numéricos con formato argentino**: aceptar "1,4" y "3.500.000", y mostrar con coma decimal y punto de miles. Pedir confirmación si un factor queda fuera de 1–2.
3. **Pasar a revisado, aprobado o enviado con confirmación** y bloqueo si hay avisos "para corregir", MO en cero o ítems sin origen. Que "aprobado" pida quién aprueba.
4. **Avisos nuevos:** "no hay mano de obra", "no hay armado", "ítem sin documento de origen", "plazo de la oferta distinto al calculado". Agrupar los avisos por ítem y gravedad, con enlace al renglón y una frase de qué hacer.
5. **Buscador arriba** de la tabla, o en un panel lateral, con sinónimos del rubro (bridada = RF/WN, serie = #, Ø en fracciones) y coincidencia de medidas por número completo. Que los filtros de familia filtren de verdad y que el contador baje.
6. **Ítem a mano:** sin "Igual" por defecto y con el origen obligatorio (o el ítem pasa a ser Estimado).
7. Completar el **subtotal** en el primer render. Renombrar "USD ajustado" a "Total línea USD (c/ inflación)".
8. Un solo TC visible, con la explicación de dónde sale.
9. Pantalla de inicio con 3 pasos ("1. Datos y cliente · 2. Materiales y MO · 3. Plazo y oferta · 4. Revisar avisos y descargar").
10. Celular: tarjetas para los ítems (como en el inicio), botones de 40 px o más, y una señal de que menú y pestañas se deslizan.
11. Accesibilidad: Escape y foco en los cuadros de diálogo, flechas en las pestañas, `aria-label` en los campos de las tablas.
12. Firmantes: botón Borrar y validar el email. Pedidos: usar "Mandado" o "En cola" en lugar de "Enviado".

## 6. Nota de facilidad de uso: **6/10**

**A favor:**
- La estructura es lógica y las pestañas siguen el orden en que se cotiza.
- Totales siempre a la vista, escenarios de factor y una calculadora de plazo excelente.
- Selección múltiple que se mantiene entre búsquedas, deshacer y rehacer, guardado automático y fechas DD-MM-AAAA en pantalla.
- Pedidos y Firmantes, simples.
- Para un vendedor que conoce el rubro, en 20 minutos se arma una cotización.

**En contra:**
- Dos fallas pueden llevar un número o un texto equivocado al cliente sin que el vendedor lo note: la oferta heredada de la CAPEX y la coma decimal que multiplica por 10.
- El cambio a "enviado" no tiene protección.
- Los avisos son demasiados y con jerga, pero no detectan lo más grave (MO en cero, precio sin documento).
- El buscador exige escribir "como el catálogo".
- En el celular sirve para consultar, no para cargar.

Si se arreglan los puntos 1 a 4 de las sugerencias, la nota sube a 8.
