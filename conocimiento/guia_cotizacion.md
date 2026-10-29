# Guía para cotizar un pedido, paso a paso

Cómo se cotiza un pedido nuevo con el cotizador, de principio a fin. Las reglas obligatorias están en [`procedimiento_cotizacion.md`](procedimiento_cotizacion.md) (P1–P10). Esta guía dice **qué hacer, con qué archivo y con qué comando** en cada paso. El caso modelo es la [COT26-1003-001 (CAPEX OQ8209)](../cotizaciones/COT26-1003-001_CAPEX_OQ8209/bitacora.md).

## Resumen

El proceso tiene dos etapas. El **presupuesto preliminar** se arma con antecedentes y piezas similares, marcando qué es igual y qué es similar. El **presupuesto definitivo** se arma con los precios que trae Compras. Recién el definitivo se revisa, se aprueba y pasa a oferta.

```
 1. Recibir planos e información licitatoria            pedido/ (pliego técnico y comercial, planos, mails)
 2. Lista de materiales del plano + especificación      pedido/lista_materiales_plano.csv (la revisa otro)
 3. Buscar antecedentes: precios de piezas iguales      cotizacion.json → fuentes, cada una marcada
    o similares (aclarando en qué difieren)             "igual" / "similar" + diferencia / "sin_ref"
 4. Ajuste por inflación hasta hoy                      automático (conocimiento/costos/indices_ajuste.csv)
 5. Lo que no es material: soldaduras (de los extremos), cotizacion.json → grupo "mo" / "servicio";
    armado, PH, END, pintura, revestimientos, insumos,  flete y embalaje en "parametros"
    ingeniería y calidad, embalaje, transporte
 6. Plazo: llegada del material más largo + taller      cotizacion.json → plazo
 7. PRESUPUESTO PRELIMINAR                              python herramientas/armar_cotizacion.py <carpeta>
    → informe.html con botones "Descargar presupuesto (Excel)" y "Descargar lista para Compras (Excel)"
 8. Compras pide precio a los proveedores               compras/<codigo>_pedido_materiales_compras.xlsx
 9. Cargar las respuestas (pasan a "igual", tipo cot)   cotizacion.json → volver a armar
10. PRESUPUESTO DEFINITIVO + comparación con antecedentes (P8)
11. Revisión independiente (P9)                         otro agente o persona → "revisado"
12. Factor y aprobación (dirección / Matías)            "aprobado" → ofertas sin marca de borrador
13. Enviar (lo hace Matías) y registrar el resultado    cotizaciones/README.md, bitacora.md
```

## 1. Abrir la carpeta

- Código: `COT[AA]-[código de cliente de 4 dígitos]-[NNN]`. El código del cliente está en `conocimiento/comercial/clientes.csv` (por ejemplo, CAPEX = 1003).
- Copiar `cotizaciones/_plantilla/` a `cotizaciones/COT26-1003-001_CAPEX_OQ8209/` (código, cliente y pedido).
- Guardar los originales del cliente en `pedido/`: orden o pliego, planos y especificaciones. Si el plano viene en DWG: `python herramientas/leer_dwg.py`.
- Anotar la cotización en [`cotizaciones/README.md`](../cotizaciones/README.md) con estado `borrador`.

## 2. Transcribir la tabla del plano (P1, P2)

- `pedido/lista_materiales_plano.csv`: **una fila por posición del plano, con todas sus columnas** (pos, descripción, Ø, serie o schedule, material, extremos, modelo o fabricante, cantidad, unidad). Se copia tal cual, sin interpretar.
- Leer también las **notas del plano** (pintura, revestimientos, alternativas) y el **dibujo**, para ver qué extremos se sueldan en taller y cuáles quedan para campo.
- Anotar los requisitos del pedido: ensayos, registros, marcas exigidas, fechas y lugar de entrega.
- Leer el **pliego y la especificación técnica** y hacer un resumen de una página: alcance, normas, ensayos, pintura, certificados y dossier, plazo pedido, forma de pago, moneda, lugar de entrega, multas y garantía. Lo dudoso va a una lista de **consultas al cliente**.
- **Marcas:** cruzar con `conocimiento/comercial/marcas_aprobadas.csv` (por cliente y rubro). Si el pliego exige marcas, se cotizan esas; otra marca es un desvío declarado.

## 2 bis. Pedir precios a Compras

**Matías no compra: los precios nuevos los pide Compras.** En la sección `compras` de `cotizacion.json` se cargan los requisitos por posición (lo que el proveedor tiene que respetar), los proveedores sugeridos y los servicios (armado, pintura, flete). `armar_cotizacion.py` genera `compras/<codigo>_pedido_materiales_compras.xlsx`, con la especificación del plano, la cantidad total, el último precio de referencia (uso interno) y columnas amarillas para cargar las respuestas. Esas respuestas se cargan en `cotizacion.json` como fuente de base (`tipo: cot`, con proveedor, número de cotización y fecha), y se vuelve a armar.

## 3. Buscar antecedentes y precios (P4, P5, P8)

**Primero, el buscador de antecedentes.** El mismo criterio para todas las familias (Matías, 29-10-2026): busca entre los de la misma familia o del mismo **subtipo** (coalescente, canasto, FM, bifásico, puente de medición, skid de regulación…) y ordena por parecido técnico. A igual parecido, gana el más nuevo.

```bash
python herramientas/buscar_antecedentes.py --familias      # familias y subtipos, con cuántos proyectos hay
python herramientas/buscar_antecedentes.py --cotizacion cotizaciones/<carpeta>   # consulta armada desde cotizacion.json
python herramientas/buscar_antecedentes.py --texto "separador vertical coalescente" --cuerpo 55 --serie 600 --cliente CAMUZZI
python herramientas/buscar_antecedentes.py --familia CO --texto "colector de campo produccion 6 ingresos" \
       --diametro 6 --serie 300 --material carbono --union bridado --cliente PAMPA
```

- Sin `--familia` ni `--subtipo`, se deducen del texto. En `cotizacion.json` se pueden fijar con `equipo.familia` y `equipo.subtipo`; si no, salen del título y del nombre del equipo, nunca de los ítems.
- Lo que más pesa es el subtipo (30), después el texto (25, con sinónimos: coalescedor = coalescente, FM06 = FM6, tramo = puente de medición), el tamaño (15), la serie (12), el material (8), la unión (5) y el cliente (4).
- En recipientes (separadores, filtros, tanques, calentadores) el tamaño es el **Ø del cuerpo** (`--cuerpo`), no el de las conexiones.
- Un dato que falta en el antecedente no le resta puntos: el resultado dice "sin dato".
- Si hay menos de 5 del mismo subtipo en 2025–2026, muestra aparte las **carpetas sin ficha de 2021–2024** (`indice_historico.csv`, año estimado, sin precios). Sirven para comparar diseño y alcance, no precios. Las carpetas de 2025–2026 sin ficha salen en la lista principal marcadas SIN FICHA.
- Subtipos y sinónimos nuevos se agregan en `SUBTIPOS` y `SINONIMOS` de `herramientas/indice_proyectos.py` y se prueban con `python herramientas/test_antecedentes.py`.

- Revisar los **3 a 5 primeros**, en orden.
- Primero, los que dicen **PLANILLA DE COSTO**: traen el desglose completo y son el mejor modelo.
- Cada resultado dice por qué se parece y qué carpeta abrir.
- El índice (`conocimiento/comercial/indice_proyectos.csv`) cubre las cotizaciones de 2025–2026 y las de la biblioteca. Se actualiza solo con `armar_cotizacion.py`, o a mano con `python herramientas/indice_proyectos.py` (que arma también `indice_historico.csv`).

**Precotización automática (sin IA), primero:**

```bash
python herramientas/precotizar.py cotizaciones/<carpeta> [--comparar]
```

- Lee `pedido/lista_materiales_plano.csv` y arma `cotizacion_auto.json` + `precotizacion.md`: cada renglón buscado en el catálogo (igual con precio real > similar con precio real > estimado del cepo), soldaduras calculadas de la columna de extremos, pintura (m² × tarifa), prueba hidráulica (horas × tarifa) y radiografía si `parametros.rx_pct` > 0.
- **Transcripción literal (28-10-2026):** además de `lista_materiales_plano.csv` (tabla de trabajo), guardar `pedido/transcripcion.json` con las tablas TAL CUAL el documento de origen (`{"fuente", "tablas": [{"titulo", "columnas", "filas"}], "nota"}`; la primera columna es la posición). El Excel para Compras sale de ahí, sin agregados: a la derecha van la cantidad a comprar calculada, los kg y las columnas Proveedor, Precio, Plazo y Anotaciones (`lista_compras.py`).
- Parámetros opcionales de la precotización (28-10-2026): `parametros.modo = "prefabricado"` (spools por pulgada: pulgada diametral base sch 40, tarifa de prefabricado de terceros, `rechazo_pct` 5% por defecto, sin horas ni PH), `parametros.pintura_aparte` (la pintura no entra en el total; por defecto sí en prefabricado). Material que provee el cliente: columna `provee` = `cliente` en la tabla del plano (o el texto "provisto por el cliente"): va a precio 0 y cuenta para soldadura, pintura y PH.
- Si el catálogo de servicios tiene la fabricación de un tercero del mismo tipo de equipo (trampa, tanque, filtro, separador) y tamaño, la precotización la propone en lugar de la soldadura y el montaje propios. Sin antecedente de horas del mismo tipo y tamaño, no suma horas: hay que cargarlas a mano.
- En la tabla del plano, la columna **`extremos_campo`** (por unidad) dice cuántos extremos BW quedan abiertos para campo o para la línea del cliente. Sin ella se suponen todos de taller y se avisa.
- Parámetros: `ph_horas` (horas de prueba hidráulica; sin dato se suponen 6 y se avisa) y `rx_pct` (porcentaje de juntas radiografiadas).
- Después, revisar en `precotizacion.md` solo lo marcado (SIMILAR, SIN PRECIO, estimados, ⚠), completar lo que no se calcula (armado, ingeniería, embalaje, flete, insumos) y copiar a `cotizacion.json`. Probado con la CAPEX: 16 de 25 renglones iguales a la cotización hecha a mano y la soldadura 13,37 contra 13,09 pulgadas (`herramientas/test_precotizar.py`).

**Para los materiales que no estén en los antecedentes, el catálogo de materiales:**

```bash
python herramientas/buscar_material.py "valvula retencion 2\" serie 600 cuerpo A216 WCB trim 316 NPT"
```

- Muestra primero los precios de una pieza **IGUAL** y después las **SIMILARES**, diciendo en qué difieren.
- De cada uno da el último precio de costo, la fecha, el proveedor y la ruta de origen (carpeta de Z: o planilla, y el archivo).
- Un similar se carga en `cotizacion.json` con `"coincide": "similar"` y su diferencia.
- El catálogo (`conocimiento/precios/catalogo_materiales.xlsx`) tiene una hoja por familia de material.
- **Marca (válvulas e instrumentos):** cada marca es un renglón aparte, con su precio. La marca no cuenta para igual/similar: con `--marca Danco` salen primero los iguales de esa marca y después los "IGUAL (otra marca)", para elegir. Si el cliente o el pliego piden una marca, cotizar otra es un desvío (`coincide: similar`, diferencia "marca").
- Los precios se comparan siempre en la misma unidad (un, m, tira de 6 m, m2, kg): un precio por metro nunca se junta con uno por unidad.
- Las compras del stock anteriores a 2022 no se usan (hay compras de 2009): en su lugar va el precio maestro de nov-2024.
**Mano de obra y servicios:** `python herramientas/buscar_servicio.py "soldadura piping por pulgada"` (catálogo `conocimiento/precios/catalogo_servicios.xlsx`): tarifa unitaria cuando existe, qué incluye y qué no, último precio sin IVA y origen. Un precio global (sin magnitud) solo sirve si el trabajo tiene el mismo alcance.

**Otras tablas de apoyo (borrador, revisar antes de usar en una oferta).** `armar_cotizacion.py` las cruza solo con la cotización y deja `controles_tablas.md` (kilos y m² del equipo, plazo típico de cada rubro con aviso si supera el plazo ofrecido, marcas del cliente):
- `conocimiento/comercial/marcas_aprobadas.csv` (+ `_resumen.md`): marcas exigidas o sugeridas por cliente y rubro, con cita y documento. YPF tiene listas completas; PAE, Pampa y Pluspetrol solo parciales (sus vendor lists no están extraídos).
- `conocimiento/comercial/plazos_proveedores.csv` (+ `_resumen.md`): plazo de entrega por rubro y proveedor, en días corridos, con cita. Para el camino crítico usar el máximo del rubro cuando el dato es "stock salvo venta". Sin datos de pintura ni de END.
- `conocimiento/tecnico/canos_peso_superficie.csv` (kg/m, m²/m, litros/m), `bridas_peso.csv` y `accesorios_peso.csv` (kg por pieza, con URL de origen; ver `pesos_LEEME.md`): para kg de flete, galvanizado y fabricación por kg, y m² de pintura.
- `conocimiento/costos/dolar_mensual.csv`: dólar oficial, mayorista, MEP y blue por mes desde 2024. Para convertir se usa el promedio mensual del oficial BNA venta, salvo que el documento diga su tipo de cambio.

- La columna **alerta** del catálogo marca precios a revisar antes de usarlos: historial con precios muy distintos, posible precio en pesos, sin fecha o número ambiguo.
- Después de modificar el catálogo: `python herramientas/test_catalogo.py` (casos reales de errores ya corregidos).
- **Todo precio va SIN IVA** (catálogo y `cotizacion.json`). Si la fuente da el precio con IVA, se divide por la alícuota que corresponda (21%, o 10,5% si la cotización lo indica) y se anota el valor original en la fuente. Si no dice nada, se toma como sin IVA. Decisión de Matías del 27/10/2026.

Después, completar con las fuentes de abajo:

Por orden de prioridad:

| Qué | Dónde |
|---|---|
| Ofertas parecidas (mismo cliente o mismo equipo) | `conocimiento/comercial/cotizaciones_2026.csv`, `cotizaciones_2024-2026.csv`, `fichas_2026/`, y el texto original en `fuentes_originales/ofertas_texto/<CLIENTE>/<carpeta>/` |
| **Planilla de costo de una oferta equivalente** (es el mejor modelo) | `fuentes_originales/ofertas_texto/.../4.Armado de la Oferta Comercial/*.xlsx.txt` o `7.Propuesta.../*.xlsx.txt` |
| Precios de proveedores con fecha | `conocimiento/precios/indice_precios.csv` (2.680 precios) y `proveedores_2026.csv` |
| Accesorios, caños y bridas | `conocimiento/precios/lista_renar_2025-12.csv` (con código) |
| Stock ITT | `conocimiento/precios/stock_2024-11.csv` (lo que hay en stock no suma plazo) |
| Mano de obra de terceros | `indice_precios.csv` (Ledesma, Quesada…) y `costos/tarifas.csv` |
| Costo propio de planta | `costos/costo_hora_planta.csv`, `costos/tarifas.csv` (soldador 19,73 USD/pulg-eq, oct-2024) |
| Soldadura | `tecnico/factores_soldadura.csv` (pulg-eq = DN × factor de espesor) y `tecnico/factores_accesorios.csv` (cupla/olet ×1,75) |
| Plazos | `conocimiento/plazos.md` |
| Errores que ya pasaron | [`errores_y_lecciones.md`](errores_y_lecciones.md) |

**Igual o similar.** Cada precio de base lleva `coincide`:
- `igual`: misma pieza que el plano (Ø, serie, material, trim, extremos, modelo).
- `similar`: otra pieza parecida. En `diferencia` va en qué difiere (por ejemplo "trim 8 en lugar de AISI 316" o "BW/NPT en lugar de BW/BW").
- `sin_ref`: un supuesto sin pieza de referencia.

El informe lo muestra en cada fila, la planilla en una columna y el control lo lista como aviso. **Si falta, `armar_cotizacion.py` no arma.** Un precio de una pieza similar sirve para el preliminar, pero no para afirmar en la oferta que se cumple la especificación.

**Reglas que más se olvidan:**
- Abrir el documento original de cada precio. **Nunca usar un precio de memoria ni de un resumen.**
- Comparar la especificación cotizada con la del plano: Ø, serie, material de cuerpo y trim, extremos, modelo.
- La MO de terceros tiene que salir de un trabajo con el **mismo alcance**.
- Un precio "aproximado", verbal o por WhatsApp es `est` (estimado), nunca precio de base.
- Si el original es una imagen (WhatsApp, escaneo), está en el RAR de Drive (ver `CLAUDE.md`). Hay que extraerlo y leerlo.

## 4. Cargar `cotizacion.json`

Cada ítem lleva todas sus fuentes de precio. **La primera fuente es la de base**; las demás son alternativas que se pueden elegir en el informe. Los campos se explican en [`cotizaciones/_plantilla/README.md`](../cotizaciones/_plantilla/README.md).

- `grupo`: `material`, `mo` (armado, soldadura) o `servicio` (PH, pintura, calidad, insumos).
- `tipo` de cada fuente: `cot` (cotización de proveedor), `lista`, `stock`, `ant` (antecedente de otra oferta ITT), `est` (estimado).
- `fecha` de cada fuente: la fecha del precio. Con esa fecha se hace el ajuste por inflación.
- Una fila por posición del plano, con la cantidad del plano. Lo que se compra de más va en una fila `14b`.
- Soldaduras: una fila de MO con las pulgadas equivalentes, junta por junta en la especificación.
- Parámetros: factores 1,35 / 1,35, **factor de válvulas Taval `FTV` = 1** (todas las válvulas marcadas `"taval": true`; las marca solo `precotizar.py` y la página al agregarlas del catálogo), contingencia 5%, ajuste por inflación activado y `fecha_referencia` igual a la de hoy.

## 5. Armar todo

```bash
python herramientas/indices_inflacion.py            # solo si se cargaron meses nuevos de IPC, dólar o CPI
python herramientas/armar_cotizacion.py cotizaciones/<carpeta>
```

Genera `computo.csv`, la planilla `.xlsx` con fórmulas, `informe.html` y, si hay `oferta.json`, las ofertas técnica y económica en Word y PDF. También:
- calcula el precio en Python y lo compara con la planilla recalculada con LibreOffice. Si no coinciden, frena;
- corre `verificar_computo.py` contra la tabla del plano. Si hay errores, frena.

Para publicar o actualizar el informe web se usa la herramienta Artifact con `informe.html`.

## 6. Revisar (P8)

`armar_cotizacion.py` deja además, en la carpeta de la cotización:
- `plazo_calculado.md`: acopio (material más largo) + taller sin superponer, con el margen de 15–20% y el plazo real histórico de la familia. Avisa si el ofrecido es menor o no tiene margen.
- `comparacion_antecedentes.md`: precio unitario contra los 5 antecedentes más parecidos (marca ⚠ más del 15%; "otra escala" si el antecedente no es comparable). Cada ⚠ se explica rubro por rubro antes de presentar el número.
- `controles_tablas.md`: kilos y m², plazo típico por rubro y marcas del cliente.


- Revisar **uno por uno los avisos** del control: soldaduras de campo o taller, modelos exigidos, estimados, precios viejos.
- Comparar el precio con al menos 2 antecedentes. **Si la diferencia es mayor al 15%, explicarla rubro por rubro.**
- Verificar que el plazo cubra el material más largo.
- Dejar los desvíos y los pendientes escritos en `cotizacion.json`.

## 7. Revisión independiente (P9)

Alguien que no armó el cómputo (otro agente o una persona) compara `pedido/lista_materiales_plano.csv` y el plano con `computo.csv`, el informe y la planilla. Lo que encuentre se corrige o se justifica, y se anota en el historial (`historial_html`) y en [`errores_y_lecciones.md`](errores_y_lecciones.md) si fue un error. Recién ahí `"estado": "revisado"`.

## 8. Aprobación y oferta

- La dirección o Matías definen el factor final y aprueban.
- En `cotizacion.json` y `oferta.json`: `"estado": "aprobado"`. Completar los datos marcados entre [corchetes]: número de PRES, teléfonos, marcas a confirmar.
- Volver a correr `armar_cotizacion.py`. Sin el estado "aprobado", la oferta sale con la marca **"BORRADOR – NO ENVIAR"**.
- **El cotizador nunca envía nada al cliente.** La oferta la manda Matías.

## 9. Registrar

- `cotizaciones/README.md`: estado, precio, fecha de envío y, después, **el resultado** (ganada o perdida y por qué).
- `bitacora.md` de la cotización: qué se hizo, qué se decidió y por qué.
- Todo se sube al repositorio (`git commit` + `git push`). Lo que no se sube se pierde.

## Mantenimiento de la base

| Para… | Se hace |
|---|---|
| Actualizar la inflación | Agregar el IPC, el dólar BNA y el CPI del mes en `herramientas/indices_inflacion.py` (con su fuente) y correrlo |
| Sumar precios de una cotización nueva | Los precios con fuente quedan en `cotizacion.json`. Para sumarlos a la base general: `herramientas/indice_precios.py` |
| Cambiar el formato de la oferta | `plantillas/oferta_itt_2026.docx` (ver `plantillas/README.md`) |
| Cambiar el diseño del informe | `plantillas/informe_cotizacion.html` |

## Detallado o global por rubro (28-10-2026, pedido de Matías)
- Cinco rubros se pueden cotizar **detallado** (como siempre) o **global** (un precio del tercero por equipo): MO de armado y soldadura del piping, MO de fabricación de la estructura (por separado, así hay ficha de los dos; si cotizan todo junto, repartir o poner uno en 0), granallado y pintura, RX/END/procedimientos y transporte.
- La ficha (`ficha_rubros.md`, la arma `armar_cotizacion.py`) trae lo necesario para pedir y controlar el global: juntas a tope y SW, pulgadas equivalentes, kg de piping y de estructura, m², placas de RX, juntas con LP, procedimientos, y para el transporte largo × ancho × alto, kg, equipos por semirremolque y viajes (avisa carga especial: más de 2,60 m de ancho o 4,10 m de alto cargado).
- Cambiar de modo: en la página (MO y servicios → "Cotizar por rubro") o `python herramientas/ficha_rubros.py cotizaciones/<carpeta> --global <rubro>` / `--detallado <rubro>`. El global arranca en 0 (P4 ter) hasta cargar la cotización con proveedor, fecha y documento; se compara con el cálculo detallado y avisa si se aparta más del 15%.
- Horas de ITT (ingeniería, calidad, planta y PH), caución y repuestos no entran en ningún rubro: quedan como renglones propios.

## Mano de obra y servicios por rubro (29-10-2026, pedido de Matías)
- La pestaña MO y servicios es una lista de rubros de fabricación: skid (estructura), piping, granallado y pintura, radiografía y END, procedimientos, prueba hidráulica, horas de ITT y transporte; lo demás va en "Otros servicios".
- Cada rubro tiene su ficha (kg, juntas, pulgadas, m², placas, procedimientos, litros) y su costo **por antecedentes** (tarifa del historial elegida en una lista × cantidad de la ficha; "Aplicar al costo" reemplaza los renglones del rubro) o **manual** (precio del tercero con fuente).
- Procedimientos: la ficha arma la lista (WPS/PQR por material y tipo de junta, WPQ, RX, LP, PH, pintura). Solo los de END tienen costo de antecedente (USD 250 por trabajo, repartido entre los equipos); los demás se piden si hacen falta nuevos.
- Piping: se cotiza **por pulgada de soldadura o por kg** (hay terceros que cobran por kilo). En cualquier rubro se puede elegir "Tarifa propia" y cargar valor, fecha y proveedor (29-10-2026).


## Similares: misma serie y misma norma (Matías, 29-10-2026)
Un precio de referencia "similar" solo vale si la pieza es de la **misma serie** (#150/#300/#600/#900, 2000/3000/6000) y de la **misma norma** (B16.5, B16.47, B16.9, B16.11, API 6D, API 608, etc.) que la del plano. Otra marca, otro material o una diferencia menor se anotan como diferencia; otra serie u otra norma no son referencia: se pide cotización.

## Descripción exacta del cliente (regla crítica)
**REGLA CRÍTICA — descripción del cliente (Matías, 29-10-2026):** en la descripción va siempre, sin excepción, el texto exacto del documento del cliente (plano, pliego o planilla), tal cual figura: sin corregir, traducir, abreviar ni agregar palabras ("RF", "radio largo", marcas, normas). Lo mismo con el material: se cotiza lo que pide el cliente. Lo que agrega ITT va en la columna `nota` de `lista_materiales_plano.csv`; el Ø va aparte. Si el cliente no indica cantidad y ITT la calcula, se aclara siempre en `cantidad_origen` ("El cliente no indica cantidad: calculada por ITT según el plano / la ET") y la oferta la marca con (*). Se copia de `pedido/transcripcion.json` y `verificar_computo.py` da error si no coincide.
