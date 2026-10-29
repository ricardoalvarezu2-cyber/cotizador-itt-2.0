# Pesos de bridas y accesorios de cañería

Tablas para calcular kg de un equipo (flete, galvanizado, fabricación por kg) y m² a pintar. Creadas el 28/10/2026 a partir de tablas públicas. **Estado: borrador, sin revisar por Matías.** Ningún valor está inventado ni extrapolado: cada renglón tiene su URL y su fuente. Los pesos son **aproximados** (los propios fabricantes lo dicen: B16.5 y B16.9 no fijan pesos y varían entre fabricantes).

## Archivos

| Archivo | Renglones | Contenido |
|---|---|---|
| `bridas_peso.csv` | 801 | Bridas ASME B16.5: WN, SO, ciega, SW, roscada, LJ. Series 150 a 2500 (más la 400, que la fuente publica). |
| `accesorios_peso.csv` | 1.306 | Accesorios a tope ASME B16.9 (860) y forjados ASME B16.11 (446: 401 de Bonney Forge + 45 de Smith-Cooper por diferencia con Bonney). |

Unidad: **kg** en `peso_kg`. `dn_pulg` y `dn2_pulg` en decimal (0.5, 0.75, 1.25, 1.5, 2.5...), igual que `esparragos_por_brida.csv`. Verificar la columna `nota` de cada renglón antes de usar el valor.

## Fuentes

1. **Bridas B16.5**: Wermac.org, "ASME B16.5 Forged Flanges Weight Chart" (pesos en kg, "approximately given"; la página dice que toma los datos de Texas Flange; los valores son lb enteras convertidas). https://www.wermac.org/flanges/weightchart_asme_b16-5.html
   - Control cruzado: Thermometrics Corp, "Dimensions for Class N Flanges" (tabla Weight L.B.S., "approximate values", ANSI B16.5): https://rtd.thermometricscorp.com/PDFs/Flange-Dimensions-Weight/class-150-flanges.pdf (y `class-300`, `-600`, `-1500`, `-2500`; `class-900` no se pudo leer el texto, `class-400` da 404). Esa fuente es más tosca (lb enteras, tipeos evidentes como "448" o "3144", filas incompletas), por eso solo sirvió para controlar las filas de 6 valores completos de las clases 150, 300, 600 y 1500 (156 valores comparados).
2. **Accesorios a tope B16.9**: Wermac.org, tablas "Weights of Butt Weld Elbows / Tees / Reducing Tees / Reducers / Caps", que toman los pesos de **Hackney Ladish** ("approximated or estimated"). Páginas: `https://www.wermac.org/fittings/weights_bw_elbows.html`, `weights_bw_tees.html`, `weights_bw_tees_red.html`, `weights_bw_reducers.html`, `weights_bw_reducers_xs.html`, `weights_bw_reducers_160.html`, `weights_bw_reducers_xxs.html`, `dim_caps.html` (la tabla de pesos de casquetes está al pie).
3. **Forjados B16.11**: Bonney Forge, catálogo "Forged Steel Fittings & Unions" (FSFU.pdf), pesos "based on carbon steel (A105)": https://bonneyforge.com/assets/files/FSFU.pdf (págs. del catálogo 6-9, 14-16).
   - **Atención con la unidad**: el catálogo rotula la columna "Weight" **sin unidad**. Se tomó como **lb** y se convirtió × 0,4536. Justificación: Smith-Cooper (catálogo que sí rotula "Weight LB") da casi lo mismo en la mayoría de las medidas (por ejemplo codo 90 NPT 3000: 2" 5,87 vs 5,4; 4" 33,2 vs 32,7), y un cálculo grueso de volumen del codo 1/2" da ~0,4 kg, o sea ~0,9 lb. Es la única suposición de unidad de todo el trabajo; si Matías tiene el catálogo impreso conviene confirmarlo.
   - Control cruzado: Smith-Cooper International, "Forged Carbon Steel Pipe Fittings 3000 & 6000 LB": https://www.buyfittingsonline.com/content/pipe-fittings-forged-carbon-steel-specifications-sizing-3000-6000-lb.pdf (pesos en lb con 0,1 lb de resolución). Se comparó codo 90/45, tee, cupla y casquete, clases 2000/3000/6000 (191 valores).

## Cobertura real

### Bridas (`bridas_peso.csv`)
- WN, SO, ciega, SW, roscada, LJ: series 150, 300, 400, 600, 900, 1500 (todas con 1/2" a 24", salvo 900 y 1500 sin 3 1/2" ni 22"); 2500 solo WN, ciega, roscada y LJ de 1/2" a 12" (B16.5 no tiene SO ni SW en 2500).
- **No distingue cara (RF/RTJ)** ni **schedule de cuello** en WN: columnas `cara` y `schedule_cuello` quedan vacías y la nota lo dice.
- Diferencias de más de 10% con Thermometrics (y más de 1 lb, porque esa fuente redondea a lb enteras): 13 valores. Para esos están las dos filas (la de Thermometrics lleva "convertido de lb" y la URL de su PDF).
- Los valores de Wermac/Texas son lb enteras convertidas, así que la precisión real es de ±0,5 lb.

### Accesorios BW (B16.9)
- Tipos: codo 90° radio largo (STD, XS, 160, XXS), codo 90° radio corto (STD, XS), codo 45° (STD, XS), tee recta (STD, XS, 160, XXS), tee reducción (STD, XS, 160, XXS), reducción concéntrica/excéntrica (un solo valor para ambas, según la fuente) y casquete.
- STD y XS: 1/2" (1" en radio corto, reducciones y casquetes) a 24", y también 26", 30" y 36" donde la fuente los da.
- Sch 160: codo y tee hasta 14" y 12"; casquete hasta 12"; reducciones hasta 12". XXS hasta 8".
- **Sch 40**: la fuente publica STD, no Sch 40. Coinciden hasta 10", pero **de 12" para arriba STD no es Sch 40**; esos renglones lo avisan en la nota. No se llenó "Sch 40" copiando STD.
- Reducciones y tees reducción: la columna `dn_pulg`/`dn2_pulg` respeta el orden "A-B" de la fuente (mayor-menor). Faltan combinaciones que la fuente no publica (marcadas con "-").
- Hay **incoherencias de la propia fuente** (un schedule más pesado que pesa menos que uno más liviano, 18 renglones). Se dejó el valor y la nota empieza con "ATENCION". Ejemplos: tee 5" Sch 160 24,95 kg contra XXS 18,14 kg; tee 1/2" Sch 160 menor que XS.

### Forjados (B16.11), 1/8" a 4"
- Codo 90° y 45°, tee recta, cupla, media cupla, casquete: NPT (clases 2000, 3000, 6000; la cupla y el casquete solo 3000 y 6000) y SW (3000, 6000, 9000). El 9000 solo figura de 1/2" a 2" en las tablas del catálogo.
- Tapones (redondo, hexagonal, cuadrado) y bujes (hexagonal y embutido/flush): tabla común de clases 3000/6000, rosca NPT.
- No hay forjados clase 2000 para cupla/media cupla/casquete en la fuente (el catálogo no los publica),.
- **Reducciones forjadas** (buje reductor, cupla reductora, insertos): no se cargaron; Bonney da "peso de cupla de la medida mayor" para las cuplas reductoras, que no sirve como peso real.
- Hay incoherencias del catálogo (peso de la clase más alta igual o menor que el de la clase más baja, 6 renglones, por ejemplo codo 45° 4" 3000 y 6000 con 24,75 lb los dos). Quedaron con nota "ATENCION".
- Smith-Cooper difiere más de 10% (y más de 0,1 lb) en 45 de 191 valores; es otro fabricante y el Bonney tiene medidas distintas. Están las dos filas.

## Huecos para completar
- Bridas con cara RF/RTJ y WN por schedule de cuello (el peso de WN depende del espesor del cuello): ninguna fuente pública consultada lo da. Un catálogo de fabricante (Texas Flange, Galperti, Coprosider) o el cálculo desde dimensiones B16.5 lo resolverían.
- Bridas B16.47 (más de 24") no se tocaron.
- Sch 40 propiamente dicho en 12" a 24", y Sch 80 propiamente dicho (XS coincide con 80 hasta 8", no desde 10").
- Forjados con reducción, olets (ya tienen factores en `factores_accesorios.csv`), clase 9000 NPT.
- Los hosts `wermac.org`, `bonneyforge.com`, `buyfittingsonline.com` y `rtd.thermometricscorp.com` respondieron; `blog.projectmaterials.com` (tablas B16.5 en lb y kg) devolvió 403 de control de bots y no se usó; `vytlcontrols.com` también 403. `scribd.com` y `texasflange` no se consultaron.

## Verificación hecha (28/10/2026)
- Bridas: 30 valores de Wermac al azar releídos con una segunda lectura de la página recién descargada: 29 coinciden y el restante fue un error de mi control (fila de 3 1/2") y no del CSV; la lectura por filas del CSV es la correcta.
- BW: 40 valores al azar releídos en las páginas descargadas de nuevo: 40 de 40 coinciden con la tabla. Control de coherencia lb/kg: ninguna diferencia (la fuente da ambas columnas).
- Forjados: más de 50 valores comparados a ojo contra la imagen de las páginas del catálogo (codo 90 NPT 3000, tee SW 3000, cupla SW 3000, tapón redondo, buje embutido, codo 45 SW 9000, media cupla NPT 6000, etc.): todos coinciden.
- Pendiente: revisión independiente por Matías o por otro agente antes de usar en una cotización.


## Revisión independiente (28/10/2026)

Informe: `conocimiento/auditorias/2026-10-28_pesos_bridas_accesorios.md`. Transcripción fiel en los 2.107 renglones; la unidad de Bonney Forge es libra (verificado por volumen). Se corrigieron en las tablas los errores que venían de las fuentes (E1–E8, anotados en la columna `nota` como "CORREGIDO auditoría"), se eliminaron 3 renglones de Smith-Cooper con tipeos (vale Bonney), y se marcaron con "no usar" las bridas que no existen en B16.5 (SO #900/#1500, SW grandes, 22") y con "no sirve" los bujes (tienen un solo DN). E9: el DN "2.75" de `factores_soldadura.csv` y `esparragos_por_brida.csv` era 1 1/4" mal leído ("11/4"); corregido en `construir_base.pulgadas`.

**Márgenes para estimar kg (mostrar siempre como estimado):** bridas 2"–24" ±15% (WN #900 de 14"–24" es cota superior, +30–40%; el cuello WN depende del schedule, ±10% más); BW codos ±10%, tees, reducciones y casquetes ±15%; forjados B16.11 ±25%.

## Válvulas (28-10-2026)

`valvulas_peso.csv` (383 pesos, 13 tipos) sale de la **Lista 30 de Taval (09-2025)** con `herramientas/pesos_valvulas.py`. Es el peso que Taval usa para su precio por kg, así que es dato propio del grupo, no un catálogo genérico.
- Tipos: esclusa, globo, retención a clapeta y wafer dual plate, esféricas PT y PR (flotante y guiada) bridadas, esféricas roscadas NPT (API 608) forjadas (A105/F316) y fundidas (WCB/CF8M), esclusa y globo API 602 y filtro Y. Series 150 a 2500 (bridadas), 2000/3000/5000 (NPT) y 800/1500 (API 602).
- El código Taval se descifra con el codificador (`codificador_taval_2023-07.xlsx`): tipo, diámetro, serie, extremos, material. El tipo sale de la hoja de la lista (hay códigos de otro modelo dentro de una hoja; el del código queda en `tipo_codificador`).
- La lista tiene códigos mal cargados (por ejemplo, `R050504R01010S` en la columna de 20"). Cuando código y columna no coinciden, vale la medida cuyo peso se confirma en otra fila de la lista. Control: el peso crece con el diámetro en cada tipo, serie y material (0 casos para revisar).
- Uso en `controles_tablas.py`: esférica roscada → forjada si es A105/F316, fundida si es A216/WCB/CF8M (el cuerpo manda: "A216 / AISI 316" es carbono); esférica bridada → paso total y flotante salvo que diga lo contrario (si no hay, guiada), y se anota "supuesto"; retención roscada y válvulas de otros tipos (bloqueo y purga, aguja, control, PSV) quedan sin dato. Inoxidable sin peso propio: se usa el de carbono y se anota.
- Margen: el peso de lista de Taval es el de su modelo; otra marca puede diferir ±20%.

## Peso aproximado cuando no hay tabla (29-10-2026, pedido de Matías)
`herramientas/peso_aproximado.py` (y su espejo en `web/src/ficha.js`) completa el peso por volumen × densidad cuando ninguna tabla lo tiene; el resultado dice "APROXIMADO" y la ficha lo lista aparte. Accesorios a tope: kg/m del caño × OD × largo equivalente calibrado con las tablas (`factores_peso_aproximado.csv`); forjados y válvulas: la clase o serie más cercana; juntas: anillo × densidad; termovaina bridada: brida ciega. Instrumentos (manómetros, termómetros, transmisores, bloqueo y purga) no se pesan: peso despreciable, no entran en la estimación (Matías, 29-10-2026).
