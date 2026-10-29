# Auditoría de estructura de tablas, 29-10-2026

Auditor de datos, sin modificar datos ni código. Se revisaron 80 archivos de `conocimiento/` (77 CSV y 3 XLSX presentes en el árbol, más las vistas Excel), los 16 `cotizacion.json`, `lista_materiales_plano.csv`, `computo.csv` e `historico.csv` de `cotizaciones/*/` y la estructura de `web/datos.json`. Los scripts de revisión quedaron fuera del repo (en el scratchpad de la sesión).

Aviso de método: durante la corrida otra sesión estaba regenerando los catálogos (`verificar_todo.py` / `actualizar_base.py`), así que unos minutos los CSV de `precios/catalogo_*` cambiaron en disco. Todo lo de abajo se midió sobre el estado ya estable (`git status` limpio, 4.549 materiales y 570 servicios, igual que `web/datos.json`).

## Resumen

- **0 críticos, 4 altos, 10 medios, varios bajos.** No encontré nada que por sí solo ponga un número equivocado en una oferta, pero A1 y A2 son trampas latentes: un dato en la columna equivocada que las herramientas hoy no filtran.
- Lo que está bien: claves de catálogo (`codigo`) únicas y cruzadas entre catálogo, historial y registro de códigos; `catalogo_materiales.csv` 43 columnas = las que escribe `catalogo_materiales.py`; fechas del catálogo de materiales, de plazos y de los `cotizacion.json` en AAAA-MM-DD válidas y sin futuras (el historial, salvo 3 vacías); sin precios negativos; subtotales de `computo.csv` = cantidad x precio; `datos.json` coincide con el catálogo (4.549 códigos, mismos precios); fórmulas de kg/m de `canos_peso_superficie.csv` verificadas en las 167 filas; TC de los `cotizacion.json` de octubre coincide con el promedio BNA del mes en las tres Camuzzi.
- Patrón general: cada tabla se armó con su propio criterio para moneda, IVA, unidad, diámetro y clase de presión (ver M4 a M8). Hoy funciona porque cada lector sabe cómo es su tabla; no funciona si se cruzan por texto.


## Hallazgos altos

**A1. Importes en pesos en columnas de dólares, sin moneda (`indice_proyectos.csv`, `cotizaciones_2026.csv`)**
- Archivo/columna: `comercial/indice_proyectos.csv` columnas `costo` y `precio_unitario_principal`; `comercial/cotizaciones_2026.csv` columna `costo_total`.
- Ejemplo: `indice_proyectos.csv` fila 14 (`APSA/16 - Virolas y tapas calentadores`): `costo` = 12710000.0, `precio_unitario_principal` = 3760000.0, `moneda` vacía. En `cotizaciones_2026.csv` fila 12: `costo_total` = 12710000.0, moneda vacía. Son pesos (coinciden con los ARS 12.710.000 y 3.760.000 de `indice_precios.csv`).
- Qué pasa: el nombre de las columnas es "en dólares" por convención; la única marca de pesos es la moneda vacía. `comparar_antecedentes.py` (líneas 50 a 77) descarta solo las filas sin `precio_unitario_principal` y no mira `moneda`, así que una cotización de calentadores se compararía contra "USD 3.760.000". Hay otras 3 filas con precio y moneda vacía (`TAVAL/74`, `PHOENIX/2`, `TECPETROL/12` con 12,87) que habría que mirar igual.
- Corrección propuesta: llevar a USD con el promedio BNA del mes del documento (regla de Matías) o dejar la celda vacía con la nota "en pesos"; exigir `moneda` = USD en `comparar_antecedentes.py` y `buscar_antecedentes.py`.

**A2. `precios_componentes.csv` sin IVA ni unidad: 129 precios del catálogo sin unidad**
- Archivo/columna: `precios/precios_componentes.csv`, columnas `unidad` (vacía en 194 de 300 filas), `en_stock`, `oferta_valida`, `cotizacion_proveedor`; no existe columna de IVA.
- Ejemplo: fila 2 (bomba dosificadora, precio 4550.0, `unidad` vacía). Fila 128: `en_stock` = "2025-09-04 00:00:00" (una fecha en la columna de stock). Efecto aguas abajo: `catalogo_materiales.csv` tiene 129 materiales con `ultimo_precio_usd` y `unidad` vacía (por ejemplo `ABW-00174`, fila 175, reducción 12"x6" a USD 981,10, "Cintolo cot 26/03/26") y 200 filas del historial.
- Qué pasa: no se sabe si el precio es por pieza, por metro o por juego, ni si la cotización traía IVA ("no dice: se toma sin IVA" se aplica sin que el origen lo haya dicho). `buscar_material.py` muestra el precio con "unidad s/d".
- Corrección propuesta: agregar `iva` y completar `unidad` desde el original (Cintolo/Provemet) o marcar la alerta "sin unidad" en el catálogo; normalizar `en_stock`/`oferta_valida` a una columna de plazo en días y otra de validez en fecha.

**A3. Claves repetidas sin marca de cuál vale (tablas técnicas con varias fuentes)**
- Archivos: `tecnico/accesorios_peso.csv` (42 claves repetidas), `accesorios_peso_complemento.csv` (98), `bridas_peso.csv` (13), `estructura_tubos.csv` (173 designaciones), `estructura_perfiles_laminados.csv` (146), `estructura_planchuelas.csv` (90), `estructura_angulos.csv` (53), `estructura_perfiles_chapa.csv` (25), `estructura_barras.csv` (14), `estructura_chapas.csv` (4).
- Ejemplo: `accesorios_peso.csv` filas 416 y 417, tee recta 1/4" #3000 SW, 0,122 kg contra 0,045 kg; en el complemento, cruz 1/4" #3000 SW 0,113 kg contra 0,499 kg (4,4 veces). `bridas_peso.csv` filas 28 y 29: WN 2" #300, 4,1 kg contra 3,63 kg.
- Qué pasa: la regla del proyecto es una sola versión vigente por dato. Acá las dos fuentes conviven en filas con la misma clave y no hay columna `vigente` ni `principal`; el consumidor se queda con la primera (`controles_tablas.leer_acc`: "la base manda"), lo cual funciona solo mientras el orden del archivo no cambie. En `bridas_peso` está documentado (13 valores con más de 10% de diferencia, `pesos_LEEME.md` línea 28), en el resto no.
- Corrección propuesta: agregar columna `vigente` (sí/no) y `motivo`, o mover las filas de control a un archivo `_control`. Mínimo: un test que falle si aparece una clave repetida sin `vigente`.

**A4. IVA y moneda: tres conceptos en la misma columna y cuatro vocabularios distintos**
- Archivos/columnas: `precios/proveedores_2025.csv` y `proveedores_2026.csv` (`moneda`), `precios/indice_precios.csv` (`moneda`), y el vocabulario de `iva` / `iva_origen` en `catalogo_materiales.csv`, `catalogo_servicios.csv`, `listas_vendedor.csv`, `planillas_costo_items.csv`, `servicios_extraidos.csv`.
- Ejemplo: `proveedores_2026.csv` fila 130: `moneda` = "USD por kg (+IVA) (~USD 1.640 el disco)" y fila 131 "USD por kg (+IVA)". En `indice_precios.csv` hay 15 valores distintos de `moneda` (USD, ARS, EUR, "USD + IVA por unidad", "USD por m2 + IVA", "ARS (declarada en el ppto; valores coherentes con USD)"). Vocabularios de IVA: materiales ("no dice: se toma sin IVA", "sin IVA (lo dice)", "con IVA en el documento: ya dividido por 1,21"); servicios ("no dice", "más IVA (lo dice)", "no corresponde (costo propio)" ...); listas ("sin IVA (lista Renard en USD)"); planillas ("no dice", "+ IVA").
- Qué pasa: la unidad, el IVA y la moneda viajan juntos en un texto libre; hay que interpretarlo con expresiones regulares y quien no lo haga lee "USD por kg" como USD por pieza. Las tablas de proveedores no tienen columnas `unidad` ni `iva`, por eso `catalogo_materiales.py` tiene que adivinar. `indice_precios.csv` además mezcla ARS (11), EUR (3) y USD en la columna `precio` sin columna de precio en USD.
- Corrección propuesta: tres columnas (`moneda` ISO, `iva` con valores `sin|mas|con|no_dice`, `unidad`) y un único vocabulario para `iva` en todas las tablas; agregar `precio_usd` calculado donde la moneda no es USD.

## Hallazgos medios

**M1. Fechas con texto agregado o parciales (`marcas_aprobadas.csv`, `indice_precios.csv`, `cotizaciones_2026.csv`)**
- `comercial/marcas_aprobadas.csv` `fecha`: 211 de 217 filas no son AAAA-MM-DD puro; fila 2 = "2023-09-29 (por nombre de archivo 230929, leído AAMMDD)". `precios/indice_precios.csv` `fecha`: 530 filas "2024-11 (sin fecha de compra)", 3 vacías. `comercial/cotizaciones_2026.csv` `oc_fecha`: "2025-11-05 (pedido original); versión revisada ... 2025-12-02". Correcto: la fecha limpia en `fecha` y la aclaración en `nota`; la fecha "inferida" en columna aparte (`fecha_origen`).
- Fechas parciales AAAA-MM o AAAA: `costos/tarifas.csv` `fecha` (59 de 59 filas), `precios/servicios_extraidos.csv` (18), `catalogo_servicios_historial.csv` (18), `catalogo_servicios.csv` (`fecha_ultimo_precio` 3, `fecha_referencia_descartada` 5). Están documentadas en `catalogo_servicios_LEEME.md` como decisión ("nunca se completa un día"), pero contradicen la regla general; conviene decirlo en `CLAUDE.md` o agregar una columna `precision_fecha` (dia/mes/año).
- 3 filas del historial de materiales sin fecha (`BRI-01033`, `BRI-01255`, `CAN-01383`, proveedores COMPLEMET y PROVEMET) con precio cargado; el catálogo de `CAN-01383` también tiene precio sin `fecha_ultimo_precio`.

**M2. `costos/tarifas.csv`: valor numérico con rangos en texto, claves repetidas, `vigente` sin tilde**
- `valor_usd` filas 9, 10, 52 y 2 más: "17.2-28.8", "24.5-40.3", "1.32-1.72", "1.48-1.70", "2.50-2.80" (5 de 59). Un lector numérico falla o toma el primer número. En `web/datos.json` `tarifas[].valor` viaja como texto ("19.73"), el resto de los números van como float.
- Dos pares (`soldadura` / "Mano de obra soldadura piping" y `estructura` / "Mano de obra estructura soldada") tienen más de una fila con `vigente` = "si". `vigente` usa "si"/"no", mientras `cepo`, `alcance_comparable` y otros usan "sí"/"no".
- Unidad `USD/pulg-diam-eq` (tarifas) contra `USD/pulg-eq` (catálogo de servicios): la misma magnitud con dos nombres.
- Corrección: `valor_min` / `valor_max` en lugar del rango en texto; una sola fila vigente por concepto; un solo vocabulario de unidades y de sí/no.

**M3. Series de dólar: claves de mes distintas y un dato fuera de rango**
- `costos/dolar_mensual.csv` `mes` = AAAA-MM (2024-01) y `costos/indices_ajuste.csv` `mes` = AAAA-MM-DD con día 01 (2024-01-01): la misma clave con dos formatos; hay que recortar a mano para cruzar (la tabla `dolar_bna` coincide con `oficial_promedio` en los 34 meses, verificado).
- `dolar_mensual.csv` fila de 2024-01: `mayorista_minimo` = 366.45 y `mayorista_promedio` = 685.57 contra `oficial_promedio` 837.4 y `mayorista_cierre` 839.57. 366,45 parece un dato de diciembre de 2023 (antes de la devaluación) que se coló en enero y arrastra el promedio. No afecta cotizaciones (se usa el oficial) pero es una serie incorrecta. `cepo` = "parcial (hasta el 14/04)" en 2025-04 en una columna sí/no.
- `cotizacion.json` `parametros.TC` se carga a mano y no sale de `dolar_mensual.csv`: COT26-1003-001 (CAPEX) usa 1450 con fecha de referencia 27-10-2026, cuando el promedio BNA de octubre es 1541,43 (6% menos); las COT26-0330 usan 1550; los CTRL-* usan 1550 contra 1520,16 / 1406,17 / 1472,74 / 1508,71 / 1416,29 del mes de su `fecha_referencia`. Hoy solo toca el flete en pesos (`armar_cotizacion.py` línea 106), pero incumple "promedio mensual BNA venta". Corrección: que `armar_cotizacion.py` lo complete desde `dolar_mensual.csv` y avise si difiere.

**M4. Mismo nombre de columna, distinto dominio**
- `familia`: `catalogo_materiales.csv` usa el nombre ("Válvulas"); `catalogo_materiales_historial.csv` usa el código ("VAL") en las 6.288 filas; en las tablas comerciales es el código de producto de `codificacion/familias_producto.csv` (SK, TS, C...), y en `cotizaciones/*` la familia viene de otro mapa. Una unión por `familia` entre catálogo e historial no cruza nunca.
- `unidad`: hasta 51 grafías por tabla (`planillas_costo_items.csv`) para las mismas dos unidades, "unidad" y "metro": `un`, `u`, `uni`, `uni.`, `unid`, `Unid`, `UN`, `unidad`; `m`, `Mts`, `mtr2`, `metro`. Ejemplos: `catalogo_materiales.csv` mezcla `un` (3.850) y `uni` (36); `planillas_costo_items.csv` tiene 51 grafías; `stock_2024-11.csv` `Unid`; `listas_vendedor.csv` `unidad`/`un`/`metro`.
- `tipo_precio`: el historial agrega "stock (precio maestro)", que el catálogo no tiene (queda como "compra" o "lista").
- `computo.csv` (todas las cotizaciones) llama `cant_por_puente` a la cantidad aunque el equipo sea skid o separador; `tipo_origen` de `computo.csv` ("lista", "antecedente", "estimado", "cotización") no coincide con `fuentes[].tipo` del JSON ("lista", "ant", "est", "cot", "stock").

**M5. Duplicados y columnas muertas en tablas comerciales**
- `comercial/ventas_2022-2023.csv`: 24 de 77 filas son copias exactas de la fila anterior (pares 2-3, 5-6, 7-8...: misma fecha, OC, artículo, cantidad e importe). Si son una copia de armado, las ventas del período están sobrestimadas en casi un tercio; hay que verificarlo contra los remitos. Además fila con `cantidad` = 0.4973148148148148 e importe 13.0 (cantidad derivada de dividir).
- `comercial/registro_cotizaciones_2020-2022.csv`: `fecha_emision` 100% vacía; `situacion` mezcla probabilidades ("0.5", "1") con códigos ("L4", "L3", "L1", "C", "$") y `resultado` es otra columna; `numero` se repite (una fila por renglón: filas 3 a 11 = "0-07520"), por lo que no es clave; `monto_oc_usd` con 12 decimales de punto flotante (41748.157449275364).
- `comercial/plazos_historicos_2019-2024.csv` filas 180, 182, 183: `plazo_pedido_dias` = 0 (OP 1187, 1189-1, 1189-2): debería ser vacío.
- Columnas 100% vacías: `planillas_costo_items.csv` `tc_explicito` (y en las 4 partes); `servicios_desde_planillas.csv` `magnitud`, `lugar`, `incluye`, `no_incluye`, `tc_documento` (sin `magnitud` no se puede derivar tarifa unitaria de esos 481 servicios); `bridas_peso.csv` `cara` y `schedule_cuello`; `valvulas_peso.csv` `nota`; `precios/listas_nuevas.csv` sin filas. Sacar las que no se usan o documentar que son reserva.

**M6. Formato numérico: dos lectores y un riesgo con `numeros.py`**
- Las tablas internas guardan decimales con punto y 3 decimales ("6.408", "38.656", "0.122"): 463 filas de `listas_vendedor.csv`, 491 de `catalogo_materiales_historial.csv`, 1.633 de `accesorios_peso_complemento.csv`, 819 de `estructura_tubos.csv`, etc. `numeros.leer_numero("38.656")` devuelve 38656,0 (punto + 3 cifras = miles). Hoy no pasa nada porque `catalogo_materiales.py` lee esos CSV con su propia `num()` (`float`), pero `CLAUDE.md` dice "leer siempre con numeros.py". Quien siga la regla al pie de la letra sobre un CSV interno multiplica por mil.
- Corrección: aclararlo en `numeros.py` y `CLAUDE.md` ("los CSV generados por las herramientas usan punto decimal; `numeros.py` es solo para documentos de terceros"), o escribir los CSV con decimales fijos (siempre 2 o 4) para que no haya ambigüedad.
- Excepciones de formato en el catálogo: `espesor_mm` con coma decimal en filas 3473 (`PER-03031` = "1,6") y 3513 ("7,9"); `diametro` con "OD 21,3 mm" en 4 materiales (el resto es `2"`, `0.5"`).

**M7. Clientes y familias sin clave común**
- `cliente` es texto libre en todas las tablas comerciales y no cruza con `clientes.csv` (912 clientes, `codigo` único, `estado` = "Activo" en las 912): solo 2 de 42 clientes de `cotizaciones_2025.csv`, 5 de 64 de `cotizaciones_2026.csv` y 8 de 95 de `indice_proyectos.csv` están en la lista. Valores como "YPF - AESA (según planilla de costos)", "Roma (inferido del nombre de carpeta; cotiza TAVAL)", "Camuzzi Gas del Sur S.A. / Camuzzi Gas Pampeana S.A." mezclan cliente con comentarios. `cotizacion.json` sí usa `cliente.codigo_itt` (0135, 0330, 1003), pero los 9 CTRL-* lo dejan vacío.
- Códigos de familia fuera de `codificacion/familias_producto.csv`: `EST` (5 filas de `indice_proyectos.csv`), `ERM` (2 en `registro_cotizaciones_2020-2022.csv`), `Sk` con minúscula (1). La familia `S` = "SERVICIOS" aparece en cotizaciones 2025 para mano de obra, y `C` = "CALENTADORES" convive con `CO` = "COLECTOR" (ver filas de ejemplo en `cotizaciones_2025.csv`).

**M8. Datos en la columna equivocada (casos puntuales)**
- `lista_materiales_plano.csv`: `serie_sch` guarda a la vez la clase y el schedule ("600 x 80", "150 / STD", "40 (STD)") en 56 de 404 renglones, y en algunos el espesor: `COT26-0135-003` fila 2 = "e = 1 5/8"" (también "esp. 5/8"", "esp. 3/8""). Las tablas técnicas y el catálogo separan `serie` y `schedule`; `precotizar.py` los separa con `serie_de()` y `sch_de()`, pero el espesor dentro de `serie_sch` solo lo ve la regex de la línea 374. `extremos` usa "—" como vacío en 14 renglones y `extremos_campo` es una bandera 0/1 que a veces es vacía (24); `material` escribe A105 y A106 de varias maneras ("ASTM A-105", "ASTM A105", "ASTM A-106 Gr. B", "ASTM A106 Gr.B", "ASTM A-106 Gr B").
- `tecnico/accesorios_peso_complemento.csv`: `extremos` contiene el largo ("NPT L=1-1/2in", fila 2555; 22 filas por largo) y "sin especificar" (35); `schedule_o_clase` contiene "STD/XS sin discriminar" (fila 2471) y "2000/3000/6000". `norma` mezcla "MSS SP-43 / ASME B16.9".
- `tecnico/estructura_chapas.csv`: `norma` guarda descripciones ("densidad 7.850 kg/m3", "fabricante brasilero (GME)"), y `hoja_mm` / `malla_mm` son texto ("1245x2440", "D=25 x d=11, nervio H=2") en una columna que el resto de la tabla trata como numérica.
- `precios/precios_componentes.csv`: `tipo` mezcla terminaciones ("RF", "RF.", "B.W", "RL") que en el resto del proyecto se llaman `extremos` / `cara`; `unidad` incluye "1", "-" y "6mts".
- `precios/stock_2024-11.csv` `deposito`: "Almacne" (5), "Stock"/"stock" y "Semielaborado"/"Semielaborados"; 73 `precio_maestro_usd` en 0,0 sin marca de "sin precio".

**M9. Dos versiones de la misma tabla**
- `tecnico/perfiles.csv` (196 filas, familias `W(I)`, `IPN`, `HEB`) y `tecnico/estructura_perfiles_laminados.csv` (515 filas): 81 designaciones iguales con el mismo peso; nombres de familia distintos (`W(I)` contra `IPE`). Regla de una sola versión vigente: indicar cuál manda en `estructura_pesos_LEEME.md` o retirar `perfiles.csv`.
- `estructura_tubos.csv`: 53 filas con `kg_por_m` de la fuente a más de 10% del cálculo (`kg_por_m_calc`), por ejemplo tubo cuadrado 10x10x1,25: 0,353 contra 0,312; probablemente los radios de esquina, sin explicar en `nota`.

**M10. Cruces que no cierran**
- `tecnico/valvulas_peso.csv`: 104 `codigo_taval` (por ejemplo `E020501R01001V`, esclusa 2" #150 trim 1) no existen en `precios/taval_lista30.csv`, que tiene la misma válvula con trim 5, 8, 10 y 12; además hay 85 válvulas sin código en ambas. Habría que confirmar si el trim 1 existe en la lista o si la columna `trim` está corrida.
- `precios/catalogo_codigos.csv`: 373 claves sin material en el catálogo vigente (es el registro de códigos estables, a propósito), pero no hay columna `estado` para distinguirlas de un error.
- `codificacion/*`: el `codigo` no es clave única: `componentes.csv` (`7U` x2, `4Z` x3, `5A` x2), `valvula_tipos.csv` (`G08`, `F42`, `VA1` con dos descripciones distintas y `EF5`, `I44` duplicados exactos), `mandos.csv` (`A3` con "ACTUADOR A DIAFRAGMA" y "PALANCA CON INDICADOR DE POSICION"), `series.csv` (`H` = "125" y "SCH 10"), `diametros.csv` (`065` = 2,5 y 2,5625; `103` = 4,0625 y "|"), más "N/A" y fracciones como texto ("2 9/16"). `componentes.csv` fila 252: abreviatura "HOJAS CIERRA 27 DIENTES" para la descripción "7 DIENTES".
- Provenencia: `ruta_origen` / `ruta_repo` / `carpeta` / `carpeta_origen` usan cuatro estilos de ruta: `Z:\VENTAS\...` (solo 7 de 64 `ruta_origen` del catálogo existen en el repo), ruta relativa al repo, ruta relativa a `fuentes_originales/ofertas_texto/`, y "4.Armado de la Oferta Comercial/ADICIONAL" (sin raíz) en `planillas_costo_items.csv`. Para volver a un original conviene una sola convención.

## Hallazgos bajos

- `cotizacion.json`: los renglones sin precio guardan `precio` = 0 con `proveedor` = "SIN PRECIO: pedir cotización" (14 renglones en 5 cotizaciones: COT26-0135-001 M16, M18, M27, S06; COT26-0135-002 M11...). El estado va en una columna de texto y el 0 es un número válido; conviene `precio: null`.
- `catalogo_materiales.csv`: el `diametro` va en comillas (`2"`, `0.5"`) y las tablas técnicas usan `dn_pulg` numérico, que además aparece como "2" en unas y "2.0" en otras (`accesorios_peso`, `bridas_peso` enteros; `canos_peso_superficie`, `valvulas_peso`, `taval_lista30` con ".0"). Nombres: `dn_pulg`, `diametro_pulg`, `dn_brida_pulg`, `dn_salida_pulg`, `diam_equivalente_pulg`. Clase de presión: `serie` (bridas, válvulas, catálogo), `clase` (cañería, figuras 8), `schedule_o_clase` (accesorios), `serie_b1647`. Peso: `peso_kg`, `kg`, `kg_m_carbono`, `kg_por_m`. Funciona porque cada lector conoce su tabla.
- Vocabulario de schedule: `accesorios_peso.csv` usa STD / XS / XXS / 160, y el complemento y los cañerías usan 40 / 80 / 40S / 80S: la clave no cruza entre ambas sin una tabla de equivalencias.
- `costos/horas_por_equipo_LEEME.md` dice 37 filas y 25 columnas; el CSV tiene 39 filas y 26 (`cita`); `serie` con texto libre ("600 (Pie de venta; brindas de la hoja dicen 900)"); `vigente` y `usar_montaje` en "si"/"no"; 4 `fecha` vacías.
- `costos/costo_hora_planta.csv`: 6 de 9 centros de costo sin calcular; `personas` como "2.0".
- `catalogo_servicios_historial.csv`: 11 filas ARS con `valor_usd` calculado correctamente a partir del dólar del mes (verificado en las 11); FAB-00026 y ING-00085 muestran `valor_usd` (281,61 y 482,10) distinto de `precio_total_usd` (9.856,37 y 79.546,77) porque `valor_usd` es por unidad de la tarifa (skid, documento): es consistente pero la columna no lo dice.
- `web/datos.json`: tiene 561 servicios contra 570 del catálogo (faltan los 9 `MOP-00102` a `MOP-00110`, mano de obra propia con sueldos) y 34 tarifas de 59 (las vigentes). Si es intencional, aclararlo en `web/LEEME.md`; si no, es una pérdida de datos en la página.
- Las hojas por familia de `catalogo_materiales.xlsx` guardan números como texto en 98 a 866 celdas por hoja (schedule, serie); el CSV es la fuente y el Excel es de lectura, así que molesta solo al filtrar.
- Duplicados exactos que no hace falta tener: `valvula_tipos.csv` (2), `catalogo_materiales_historial.csv` (4), `indice_precios.csv` (1), `precios_componentes.csv` (1), `planillas_costo_items_parte3.csv` (4).
- `comercial/cotizaciones_2025_items.csv`: 8 renglones con total distinto de cantidad x unitario (por ejemplo TAVAL/14 6 x 10.063,05 = 60.378,30 contra 63.944,85); `cotizaciones_2024-2026.csv` `moneda` con "-" y "usd" en minúscula; `indice_proyectos.csv`: factor distinto de monto/costo en varias filas (costo parcial, por ejemplo Sacde/17 factor 1,25 contra 2,5 calculado).

## Qué no pude verificar
- Los originales en `Z:\` y los RAR no están en el entorno: no se contrastaron valores contra documentos de origen, solo la estructura y la coherencia interna.
- Las hojas de `cotizaciones/*/*.xlsx` (planillas de cálculo) no se revisaron columna por columna; son salida de `armar_cotizacion.py` a partir de `cotizacion.json`.

## Tabla resumen por archivo

Estado: OK = sin observaciones de estructura; Observaciones = detalles menores o ya documentados; Con problemas = incluye un hallazgo alto o medio. Las referencias A1 a A4 y M1 a M10 son los hallazgos de arriba.

| Archivo | Filas | Columnas | Estado | Comentario |
|---|---:|---:|---|---|
| `codificacion/componentes.csv` | 506 | 3 | Observaciones | H5: códigos 7U, 4Z, 5A repetidos con otra descripción |
| `codificacion/diametros.csv` | 85 | 2 | Observaciones | H5: códigos 065 y 103 repetidos; valor "|" y "N/A" en pulgadas; fracciones como texto |
| `codificacion/extremos.csv` | 49 | 3 | OK |  |
| `codificacion/familias_producto.csv` | 18 | 2 | OK | faltan los códigos EST y ERM que usan otras tablas (M7) |
| `codificacion/filtros_mesh.csv` | 32 | 3 | OK |  |
| `codificacion/mandos.csv` | 35 | 3 | Observaciones | H5: código A3 repetido; abreviatura vacía |
| `codificacion/materiales.csv` | 251 | 3 | Observaciones | 1 abreviatura vacía (PR) |
| `codificacion/series.csv` | 39 | 2 | Observaciones | H5: código H repetido (125 y SCH 10) |
| `codificacion/valvula_tipos.csv` | 309 | 3 | Observaciones | H5: 2 filas duplicadas, 3 códigos con 2 descripciones |
| `comercial/carpetas_ofertas.csv` | 532 | 11 | OK con vacíos | muchos vacíos esperables (analizada, resultado); cliente en texto libre (M7) |
| `comercial/clientes.csv` | 912 | 4 | Observaciones | estado constante "Activo" en 912 filas; no hay clave que lo cruce con las demás (M7) |
| `comercial/cotizaciones_2024-2026.csv` | 284 | 14 | Observaciones | moneda "-" / "usd" / vacía; columna isis con "x"; cliente libre |
| `comercial/cotizaciones_2025.csv` | 66 | 21 | Observaciones | validez en texto; plazo_ofrecido y pago en texto libre; cliente libre |
| `comercial/cotizaciones_2025_items.csv` | 277 | 11 | Observaciones | 8 renglones con total distinto de cantidad x unitario |
| `comercial/cotizaciones_2026.csv` | 93 | 21 | Con problemas | A1: costo_total en pesos (12.710.000) sin moneda; oc_fecha con texto |
| `comercial/cotizaciones_2026_items.csv` | 153 | 11 | Observaciones | 9 renglones sin moneda, 4 en ARS |
| `comercial/indice_proyectos.csv` | 164 | 30 | Con problemas | A1: montos en pesos sin moneda; código de familia EST fuera de familias_producto |
| `comercial/marcas_aprobadas.csv` | 217 | 10 | Con problemas | M1: fecha con texto agregado en 211 de 217 filas |
| `comercial/plazos_historicos_2019-2024.csv` | 191 | 11 | Observaciones | 3 plazos pedidos = 0 |
| `comercial/plazos_proveedores.csv` | 213 | 13 | OK | borrador según el estado del proyecto |
| `comercial/plazos_proyectos.csv` | 57 | 15 | OK | fechas y plazos coherentes entre sí |
| `comercial/registro_cotizaciones_2020-2022.csv` | 200 | 13 | Observaciones | M5: fecha_emision 100% vacía, "situacion" mezcla códigos, montos con 12 decimales de punto flotante |
| `comercial/ventas_2022-2023.csv` | 77 | 8 | Observaciones | M5: 24 de 77 filas son duplicados exactos |
| `costos/costo_hora_planta.csv` | 9 | 8 | Observaciones | 6 de 9 centros sin costo calculado |
| `costos/dolar_mensual.csv` | 34 | 25 | Observaciones | M3: mayorista 2024-01 con mínimo 366,45; "cepo" con un valor fuera de sí/no; mes AAAA-MM |
| `costos/dolar_mensual.xlsx` | 37 | 15 | OK | presentación: 15 columnas de 25; encabezados con espacios (normal en Excel) |
| `costos/horas_por_equipo.csv` | 39 | 26 | Observaciones | LEEME dice 37 filas y 25 columnas; hay 39 y 26; "serie" con texto libre |
| `costos/indices_ajuste.csv` | 34 | 8 | Observaciones | M3: mes AAAA-MM-01 (el dólar usa AAAA-MM) |
| `costos/sueldos_2024-10.csv` | 7 | 7 | OK |  |
| `costos/tarifas.csv` | 59 | 9 | Con problemas | M2: valor_usd con rangos en texto, conceptos repetidos con vigente=si, fechas AAAA-MM / AAAA |
| `precios/acero_por_kg.csv` | 9 | 15 | OK | 9 filas |
| `precios/catalogo_codigos.csv` | 4922 | 2 | OK | 373 claves sin material (registro de códigos estables, a propósito) |
| `precios/catalogo_materiales.csv` | 4549 | 43 | Con problemas | A2: 129 precios sin unidad; M4: unidad un/uni; espesor con coma en 2 filas |
| `precios/catalogo_materiales.xlsx` | 4549 | 20 | OK | vista de 20 a 29 columnas por hoja; mismas 4.549 filas |
| `precios/catalogo_materiales_historial.csv` | 6288 | 16 | Con problemas | M4: familia en código (el catálogo usa el nombre); 3 filas sin fecha; 4 duplicadas |
| `precios/catalogo_servicios.csv` | 570 | 29 | Observaciones | fechas AAAA-MM / AAAA (documentadas); 5 sin precio; iva con otro vocabulario (A4) |
| `precios/catalogo_servicios.xlsx` | 570 | 29 | OK |  |
| `precios/catalogo_servicios_codigos.csv` | 570 | 2 | OK |  |
| `precios/catalogo_servicios_historial.csv` | 662 | 21 | Observaciones | 18 fechas parciales, 2 vacías |
| `precios/indice_precios.csv` | 2749 | 10 | Con problemas | A4: moneda con IVA y unidades dentro; 530 fechas con texto; 3 vacías; unidades con 25 grafías |
| `precios/lista_renar_2025-12.csv` | 1074 | 5 | OK |  |
| `precios/listas_nuevas.csv` | 0 | 12 | OK | vacía (solo encabezado) |
| `precios/listas_vendedor.csv` | 1649 | 12 | Observaciones | precios con 3 decimales con punto ("6.408"): ver M6 |
| `precios/planillas_costo_items.csv` | 2568 | 22 | Observaciones | tc_explicito 100% vacía; unidad con 51 grafías; 16 costos en 0 |
| `precios/planillas_costo_items_parte1.csv` | 677 | 19 | OK | entrada de unir_planillas_costo.py; tc_explicito vacía |
| `precios/planillas_costo_items_parte2.csv` | 1651 | 19 | OK | entrada de unir_planillas_costo.py |
| `precios/planillas_costo_items_parte3.csv` | 825 | 19 | Observaciones | 4 filas duplicadas exactas |
| `precios/planillas_costo_items_parte4.csv` | 79 | 19 | OK |  |
| `precios/precios_componentes.csv` | 300 | 19 | Con problemas | A2: sin columna IVA; unidad vacía en 194 de 300; en_stock/oferta_valida con texto y fechas |
| `precios/proveedores_2025.csv` | 72 | 7 | Con problemas | A4: moneda con IVA y unidad adentro; sin columnas unidad ni iva |
| `precios/proveedores_2026.csv` | 369 | 7 | Con problemas | A4: igual; plazo_entrega con fechas DD/MM |
| `precios/servicios_desde_planillas.csv` | 481 | 20 | Observaciones | magnitud, lugar, incluye, no_incluye y tc_documento 100% vacías |
| `precios/servicios_extraidos.csv` | 181 | 20 | Observaciones | fechas parciales (documentado) |
| `precios/stock_2024-11.csv` | 1186 | 10 | Observaciones | deposito con errores de tipeo (Almacne, stock/Stock); 73 precios maestro en 0 |
| `precios/taval_lista30.csv` | 720 | 15 | OK |  |
| `tecnico/accesorios_peso.csv` | 1303 | 10 | Con problemas | A3: 42 claves repetidas con pesos distintos |
| `tecnico/accesorios_peso_complemento.csv` | 2893 | 10 | Con problemas | A3: 98 claves repetidas; M8: largo dentro de "extremos" |
| `tecnico/bridas_b1647_peso.csv` | 372 | 12 | OK |  |
| `tecnico/bridas_orificio_b1636_peso.csv` | 70 | 10 | OK |  |
| `tecnico/bridas_peso.csv` | 801 | 10 | Con problemas | A3: 13 claves repetidas; cara y schedule_cuello 100% vacías |
| `tecnico/canos_complemento_b3610.csv` | 86 | 11 | OK |  |
| `tecnico/canos_inox_b3619.csv` | 93 | 11 | OK |  |
| `tecnico/canos_peso_superficie.csv` | 167 | 11 | OK | fórmula de kg/m verificada en las 167 filas |
| `tecnico/esparragos_peso.csv` | 194 | 12 | OK |  |
| `tecnico/esparragos_por_brida.csv` | 95 | 4 | OK |  |
| `tecnico/estructura_angulos.csv` | 394 | 14 | Observaciones | A3: 53 designaciones repetidas |
| `tecnico/estructura_barras.csv` | 202 | 13 | Observaciones | A3: 14 repetidas |
| `tecnico/estructura_chapas.csv` | 163 | 14 | Observaciones | 4 repetidas; "norma" con texto descriptivo |
| `tecnico/estructura_inox_densidad.csv` | 85 | 9 | OK |  |
| `tecnico/estructura_perfiles_chapa.csv` | 108 | 17 | Observaciones | A3: 25 repetidas |
| `tecnico/estructura_perfiles_laminados.csv` | 515 | 13 | Observaciones | A3: 146 repetidas; duplica a perfiles.csv (M9) |
| `tecnico/estructura_planchuelas.csv` | 657 | 14 | Observaciones | A3: 90 repetidas |
| `tecnico/estructura_tubos.csv` | 1154 | 15 | Observaciones | A3: 173 repetidas |
| `tecnico/factores_accesorios.csv` | 8 | 3 | OK |  |
| `tecnico/factores_peso_aproximado.csv` | 14 | 5 | OK |  |
| `tecnico/factores_soldadura.csv` | 167 | 11 | OK |  |
| `tecnico/figuras8_peso.csv` | 183 | 9 | OK |  |
| `tecnico/olets_peso.csv` | 182 | 12 | OK |  |
| `tecnico/perfiles.csv` | 196 | 4 | Observaciones | M9: versión paralela de estructura_perfiles_laminados (81 designaciones iguales) |
| `tecnico/valvulas_peso.csv` | 383 | 14 | Observaciones | M10: 104 codigo_taval no están en taval_lista30; nota 100% vacía |

### Archivos de `cotizaciones/` y `web/`

| Archivo | Filas | Columnas | Estado | Comentario |
|---|---:|---:|---|---|
| `cotizaciones/*/pedido/lista_materiales_plano.csv` (16, con la plantilla) | 2 a 50 por archivo (404 en total) | 10 | Observaciones | M8: `serie_sch` mezcla clase, schedule y espesor; `extremos` con "—"; mismas 10 columnas en las 16 |
| `cotizaciones/*/computo.csv` (6 cotizaciones del cotizador) | 32 a 47 | 13 | OK | subtotal = cantidad x precio (1 diferencia de 0,04 en COT26-0135-003 M03); M4: nombre `cant_por_puente` |
| `cotizaciones/CTRL-*/historico.csv` (9) | 7 a 58 | 9 | OK | 2 totales distintos de cantidad x unitario en CTRL-F01 (filas 4 y 5) |
| `cotizaciones/*/cotizacion.json` (16, con la plantilla) | 16 documentos, 250 renglones | claves iguales en los 16 | Observaciones | M3: `parametros.TC` a mano; renglones sin precio con 0 (bajo); todas las `fecha` y `fuentes[].fecha` en AAAA-MM-DD; estado "borrador" en los 16 |
| `web/datos.json` | 19 claves | n/a | Observaciones | materiales 4.549 = catálogo; servicios 561 de 570; tarifas 34 de 59, `valor` como texto |
