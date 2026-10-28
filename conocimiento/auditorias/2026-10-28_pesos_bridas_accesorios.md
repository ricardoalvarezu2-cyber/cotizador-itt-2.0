# Auditoría independiente: tablas de pesos de bridas y accesorios

Fecha: 28/10/2026. Revisó: agente independiente (no armó las tablas). Archivos auditados, sin modificar: `conocimiento/tecnico/bridas_peso.csv`, `accesorios_peso.csv`, `pesos_LEEME.md`. También se cruzó con `canos_peso_superficie.csv`.

**Estado de lo auditado: borrador. Esta auditoría no corrige nada en las tablas; propone correcciones.**

## 1. Resumen

| Concepto | Resultado |
|---|---|
| Renglones comparados contra la fuente | **Todos**, no una muestra: bridas 801 de 801 (788 Wermac + 13 Thermometrics) y accesorios 1.306 de 1.306 (860 BW Wermac + 401 Bonney Forge + 45 Smith-Cooper) |
| Errores de transcripción (CSV distinto de la fuente) | **0** de 2.107. El valor, la fila y la columna (DN, clase, schedule) coinciden en todos |
| Conversión lb a kg (x0,4536) | **0 errores**: los 401 de Bonney coinciden al milésimo; Smith-Cooper y Thermometrics también; Wermac publica kg y lb y son coherentes entre sí |
| Unidad de Bonney Forge | **Es libra: confirmado** con un cálculo geométrico (apartado 3) |
| Errores de la fuente confirmados (el CSV copia bien un valor que está mal en el original) | **14 renglones** de las dos tablas auditadas (E1 a E8: bridas, tees BW, Smith-Cooper y codos de 45°), más el error del DN 2,75 en otras tres tablas (E9, 13 renglones) |
| Sospechosos (sin poder confirmar) | unos 20 renglones o grupos, listados en los apartados 6 y 7 |
| Incoherencias físicas | Pocas y casi todas pequeñas. Detalle en el apartado 4 |

En una frase: **la transcripción es fiel; el riesgo está en los datos de origen (aproximados, con tipeos del catálogo) y en cómo se usan**. Para estimar kg en cotizaciones sirven, con los márgenes de la conclusión (apartado 8).

### Cómo se verificó

- **Bridas Wermac**: se bajó la página con curl y se parseó la tabla completa (788 valores numéricos) para compararla con el CSV por clase, DN y tipo. Se compararon los 13 duplicados con los PDF de Thermometrics y, además, 331 valores de Thermometrics contra Wermac (clases 150, 300, 600, 900, 1500 y 2500).
- **BW Wermac**: las 7 páginas de pesos y la de casquetes, parseadas por tabla. Se mapeó el orden de las tablas con sus títulos (por ejemplo "ELBOWS 90° LR SCHEDULE XS") y se comparó tipo, schedule, DN y valor kg. Además se verificó que lb x 0,4536 sea igual a kg en todas las filas de la fuente.
- **Bonney Forge (FSFU.pdf)**: se extrajeron las coordenadas de cada palabra (`pdftotext -bbox`) y se asignó cada peso a la columna de tamaño más cercana. Importa porque muchas filas tienen la primera celda vacía (la de 1/8") y una lectura por orden se corre una columna. Los 401 pares (DN, valor) coinciden.
- **Smith-Cooper**: texto del PDF; los 45 valores coinciden.
- **Estimación por volumen**: acero 7,85 kg/dm³ (0,2836 lb/in³) con dimensiones de B16.5 (tabla de Thermometrics con O, Q, X, Y, bore) y de B16.9 / B16.11 (radio del codo, caño de `canos_peso_superficie.csv`, dimensiones A y B de Bonney).
- Los scripts de análisis quedaron fuera del repositorio (carpeta temporal). Si se quiere reproducir, hay que volver a escribirlos; los pasos están descriptos arriba.

## 2. Muestra contra la URL de origen

| Fuente | Renglones | Coinciden | Notas |
|---|---|---|---|
| Wermac, bridas B16.5 | 788 | 788 | Valores en kg, redondeos de lb enteras (0,9 = 2 lb; 1,4 = 3 lb) |
| Thermometrics, duplicados | 13 | 13 | 8 lb = 3,63 kg, 10 = 4,54, etc.: correcto |
| Wermac, BW (codos, tees, reducciones, casquetes) | 860 | 860 | Tipo, schedule y DN verificados contra el título de cada tabla |
| Bonney Forge FSFU.pdf | 401 | 401 | Alineación por columna verificada con coordenadas |
| Smith-Cooper | 45 | 45 | |

Observaciones sobre `pesos_LEEME.md`:

1. Dice que el restante de los 30 valores de bridas "fue un error de mi control (fila de 3 1/2")". No: **esa fila está mal en la fuente** (ver E1). El CSV copia fielmente el valor de Wermac, pero el valor de Wermac para 3 1/2" #150 SO/LJ/SW está mal.
2. Dice que "class-900 no se pudo leer el texto". Se pudo leer con `pdftotext` y da 102 valores comparables: coinciden con Wermac salvo dos tipeos evidentes de Thermometrics (4113 lb por 411 y 6855 por 685) y el caso del 3" (ver apartado 6).
3. Dice "incoherencias de la propia fuente ... 18 renglones" en BW. En el CSV hay **12** renglones BW con "ATENCION"; los 18 son BW (12) más forjados (6).
4. Los renglones de bridas SO #900, #1500 y #2500, SW de más de 3" y los de 22" no existen en B16.5 (ver apartado 6).

## 3. Unidad del catálogo de Bonney Forge: libras (confirmado)

El PDF no rotula la columna `Weight` (solo dice "All dimensions are in inches" y "Weights based on carbon steel (A105)"), así que no hay evidencia dentro del texto. Se resolvió con geometría: codo 90° NPT clase 3000, con las dimensiones A (centro a extremo) y B (diámetro exterior) del propio catálogo, el calibre de Sch 80 y densidad del acero. Peso estimado de la pieza maciza menos el taladro:

| NPS | Estimado (lb) | Tabla Bonney | Tabla / estimado |
|---|---|---|---|
| 1/2" | 1,00 | 0,97 | 0,97 |
| 1" | 2,39 | 2,29 | 0,96 |
| 2" | 5,77 | 5,87 | 1,02 |
| 2 1/2" | 11,08 | 11,03 | 1,00 |
| 3" | 16,48 | 17,50 | 1,06 |
| 4" | 28,39 | 33,20 | 1,17 |

Todos entre 0,9 y 1,17. Si la unidad fuera kg, la relación sería de 2,2 a 2,6 (el catálogo diría que un codo de 2" pesa 12,9 lb). **Es libra.** La conversión x0,4536 del CSV es la correcta, y el control por Smith-Cooper (que sí rotula "Weight LB") queda como segunda evidencia.

## 4. Coherencia física

### Bridas (`bridas_peso.csv`, 788 filas Wermac)

- **El peso crece con el DN**: 6 violaciones, 2 de ellas reales (E1, E2). Las otras son 3" a 3 1/2" #150 (E1 de nuevo, en SO, LJ y SW) y 20" a 22" #600 en SO, SW y roscada (E2).
- **El peso crece con la serie**: 5 violaciones, todas chicas y de redondeo (#300 a #400 en LJ 1 1/4", 2 1/2", 3", SW 1/2" y WN 1 1/4": diferencias de 0,05 a 0,5 kg). Sin impacto.
- **WN mayor que SO** (igual DN y serie): 24 casos con WN menor o igual a SO. Son los de 1/2" y 3/4" (redondeo de lb enteras: 0,9 y 0,9) y, sobre todo, **18 de los 38 renglones SO de #900 y #1500, donde el valor de SO es idéntico al de WN** (SO no existe en esas clases; Wermac/Texas repitió el WN). Para #150 a #600 WN siempre es mayor que SO desde 2".
- **Blind contra SO**: el blind es mayor o igual en todos desde 2" (correcto físicamente, el blind es un disco macizo).
- **Peso contra estimación por volumen** (acero 7,85, dimensiones de B16.5; blind, SO y WN de 2" a 24"; WN con bore de Sch STD en #150/#300, XS en #600 a #1500, Sch 160 en #2500). Relación estimado / Wermac:

  | Tipo y clase | Mediana | Rango |
  |---|---|---|
  | Blind (todas las clases) | 0,90 a 0,99 | 0,82 a 1,00 (1,33 en 2 1/2" #150) |
  | SO #150 a #600 | 0,90 a 0,99 | 0,83 a 1,05 |
  | WN #150 a #600 | 0,88 a 1,04 | 0,83 a 1,25 |
  | WN #900 | 0,98 | 0,72 a 1,12 (0,72 a 0,76 en 14" a 24": Wermac pesa 30 a 40% más que el estimado) |
  | WN #1500 y #2500 | 0,90 a 0,96 | 0,85 a 1,06 |

  Ningún error grosero (x2, x0,5) en 2" o más. Wermac es en general 0 a 12% más pesado que el cálculo, es decir, conservador. **Por debajo de 1 1/2" no sirve el valor exacto**: 1/2" y 3/4" valen lo mismo en casi todos los tipos y clases (0,9 kg = 2 lb enteras) y el cálculo da 1,1 a 1,4 lb contra 2: sobreestima hasta x1,8 (en valores de menos de 1 kg, irrelevante en kg totales).
- **LJ #150 14" a 24"**: Wermac 104 a 273 lb, Thermometrics 77 a 195 lb, estimado 91 a 229 lb. Wermac es 12 a 19% más alto que el cálculo; Thermometrics queda por debajo del SO de la misma medida, lo cual no es posible (el LJ tiene el cuello más largo). Vale Wermac.

### Accesorios BW (860 filas)

- **Peso contra DN**: en codos, tees rectas y casquetes, ninguna violación.
- **Peso contra schedule** (STD < XS < 160 < XXS): 15 violaciones. De ellas, 12 están marcadas "ATENCION". Las 3 sin marcar **no son error**: codo 8" Sch 160 (54,43 kg) contra XXS (53,52 kg), casquete 8" 160 contra XXS, y tee 8" de la misma serie, porque a 8" el espesor de Sch 160 (23,01 mm) es mayor que el de XXS (22,23 mm). Es un caso físico real que conviene aclarar en la nota.
- **Estimación geométrica** (caño del `canos_peso_superficie.csv` por el largo del arco, radio 1,5 DN en el largo, 1 DN en el corto):

  | Pieza | Relación tabla / estimado |
  |---|---|
  | Codo 90° radio largo STD, XS, 160, XXS | mediana 1,00 a 1,06; rango 0,92 a 1,19 |
  | Codo 90° radio corto STD, XS | mediana 1,04; rango 0,98 a 1,21 |
  | Codo 45° STD, XS | mediana 1,04 a 1,06; rango 0,94 a 1,22 |
  | Tee recta (3 x C x kg/m) | mediana 1,05; p5 a p95 de 0,85 a 1,31 |
  | Reducciones (largo H de B16.9 tomado de memoria, promedio de los dos caños) | mediana 1,16; rango 1,01 a 1,36 |
  | Casquetes (largo E de B16.9 tomado de memoria) | mediana 1,18; rango 0,95 a 1,46 |

  Sin ningún valor grosero. Los codos coinciden con el cálculo (1,0 a 1,06), como corresponde a piezas de espesor casi igual al del caño. Para reducciones y casquetes los largos H y E se tomaron de memoria, así que esas dos filas del cuadro son orientativas.

### Forjados B16.11

- **Peso contra DN**: 12 violaciones, 8 en 1/8" contra 1/4" (diferencias de 0,02 a 0,04 kg, sin impacto). Las que no son del 1/8":
  - Codo 45° y codo 90° NPT clase 6000, 3" mayor que 4": **física del catálogo**, no error (4" #6000 tiene el mismo cuerpo que #3000; cálculo 33 a 36 lb en 3" y 34 en 4").
  - Cupla SW 9000 de 1" mayor que 1 1/4" (1,71 contra 1,69 lb) y media cupla SW 9000 de 1/2" mayor que 3/4": diferencia de 1 a 10%, ruido.
  - Buje embutido 3/8" (0,07) mayor que 1/2" (0,03) y buje hexagonal 1 1/4" (0,38) mayor que 1 1/2" (0,37). **Los bujes son reductores y el CSV los guarda con un solo DN** (apartado 6).
- **Clase contra clase** (2000 < 3000 < 6000 < 9000): 6 violaciones, todas marcadas "ATENCION" en el CSV. Ninguna sin marcar.
- **Codo de 45° mayor o igual que el de 90°** de igual DN y clase: 5 casos (todos del catálogo): NPT 2000 2 1/2" (8,07 contra 7,09 lb), SW 3000 2 1/2" (7,76 contra 6,67), SW 3000 4" (24,06 contra 22,59), NPT 3000 3/8" (empate) y NPT 6000 1/8" (0,56 contra 0,37). Geométricamente un 45° debe pesar menos. Ver E8.
- **Contra estimación por volumen**: los codos 90° NPT 3000 están entre 0,9 y 1,17 del cálculo (apartado 3). Para el resto de las piezas no hay dimensiones suficientes en el catálogo para estimar.

## 5. Cruce con `canos_peso_superficie.csv`

- **Fórmulas verificadas**: kg/m = π(OD−e)e x 7,85e-3, ID = OD−2e y m²/m = π·OD/1000, en las 168 filas: **0 diferencias**. La tabla de caños es correcta.
- **Error en esa tabla (confirmado)**: el DN **1 1/4" (OD 42,2 mm) está cargado como `2.75`** (4 filas: STD, XS, 160, XXS). El dato viene de `factores_soldadura.csv` (misma falla, 4 filas), que alimenta a `herramientas/tablas_pesos.py`; `esparragos_por_brida.csv` tiene lo mismo (5 filas; "2.75,150,1/2" X 2 3/4" es la brida de 1 1/4" #150). Consecuencia: **toda búsqueda de caño o espárragos de 1 1/4" falla**, y `controles_tablas.py` informa "sin schedule reconocido" y no suma los kg. Como el DN 2,75 no existe en ninguna norma, es un tipeo de conversión (1 1/4").
- Codos (apartado 4): coherentes con el caño. Casquetes: 0,95 a 1,46 veces el caño del largo de B16.9. Tees: 0,85 a 1,31.

## 6. Tabla de errores confirmados y corrección propuesta

"Fuente mala" quiere decir que el CSV copia fiel un valor que está mal en el original. Corrección propuesta: usar el valor indicado y anotar el motivo en el CSV; la decisión es de Matías.

| ID | Archivo y renglón(es) | Valor actual | Evidencia | Corrección propuesta |
|---|---|---|---|---|
| E1 | `bridas_peso.csv`: SO, LJ y SW, 3 1/2", #150 | 4,0 kg (8,8 lb) en las tres | Es menor que el de 3" (4,1 kg), y el WN, el roscado y el blind de 3 1/2" son 5,4 / 5,4 / 5,9 kg. Thermometrics da 11 lb (4,99 kg); el cálculo con dimensiones B16.5 da 11,5 lb (5,2 kg) | **5,0 kg** (11 lb). Además SW 3 1/2" no existe en B16.5 (SW llega a 3") |
| E2 | `bridas_peso.csv`: SO, SW y roscada, 22", #600 | 265,5 kg | Menor que el de 20" (275,4 kg), cuando el WN, el LJ y el blind de 22" crecen (324 / 301 / 450 kg). La relación SO/blind es 0,70 a 0,72 en 20" y 24" | **aprox. 320 kg** (0,71 x blind 450). Marcar como interpolado. 22" no figura en B16.5 (hay 20" y 24") |
| E3 | `accesorios_peso.csv`: tee recta BW 5" Sch 160 | 24,95 kg | Las tees reductoras 5x4 y 5x3 Sch 160 pesan 16,8 y 16,3 kg, y la XXS recta 18,14 kg; el cálculo da 18 a 19 kg. 24,95 es un tipeo de la fuente (el marcado "ATENCION" estaba en la fila XXS, pero **la mala es la 160**) | **aprox. 17,5 kg** (rango 17 a 19); marcar la fila 160 en lugar de la XXS |
| E4 | `accesorios_peso.csv`: tee reductora BW 6x5 Sch 160 | 14,06 kg | Las otras 6xN 160 pesan 25,9 a 27,2 kg y la recta de 6" 28,12 kg. Es aproximadamente la mitad (31 lb en lugar de unas 61) | **aprox. 27,7 kg** (tendencia: 6x4 27,22 + 0,45) |
| E5 | `accesorios_peso.csv`: Smith-Cooper codo 90° NPT 3000 1/4" | 0,318 kg (0,7 lb) | Smith-Cooper tiene 3/8" en 0,6 lb, o sea que 1/4" > 3/8": tipeo del catálogo. Bonney da 0,35 lb | **0,16 kg** (el valor de Bonney) y descartar el renglón de Smith-Cooper |
| E6 | `accesorios_peso.csv`: Smith-Cooper tee SW 3000 4" | 17,87 kg (39,4 lb) | Es igual a la tee NPT (39,6 lb), que es mucho más pesada que la SW. Bonney da 28,6 lb, y la relación tee/codo SW de Bonney (1,19 a 1,27) también la da Smith-Cooper en las demás medidas | **12,97 kg** (Bonney, 28,6 lb); descartar el de Smith-Cooper |
| E7 | `accesorios_peso.csv`: Smith-Cooper tee SW 6000 1" | 2,132 kg (4,7 lb) | Mayor que la de 1 1/4" del propio catálogo (4,2 lb). Bonney da 3,17 lb | **1,44 kg** (Bonney); descartar el de Smith-Cooper |
| E8 | `accesorios_peso.csv`: Bonney codo 45° NPT 2000 2 1/2" (8,07 lb), SW 3000 2 1/2" (7,76 lb) y SW 3000 4" (24,06 lb) | 3,66 / 3,52 / 10,91 kg | Pesan más que el codo 90° del mismo DN y clase (7,09 / 6,67 / 22,59 lb), lo cual no puede ser. El de NPT 2000 2 1/2" también pesa más que el 3000 (7,83). El cálculo geométrico del 45° de 2 1/2" 2000 da unas 6,4 lb. Smith-Cooper da 5,5 y 20,7 lb para SW 3000 de 2 1/2" y 4" | NPT 2000 2 1/2": **aprox. 2,9 kg**; SW 3000 2 1/2": **2,5 kg** (SC, 5,5 lb); SW 3000 4": **9,4 kg** (SC, 20,7 lb). Sirve el criterio "45° = 0,75 a 0,9 x el 90°" |
| E9 | `canos_peso_superficie.csv` (4 filas), `factores_soldadura.csv` (4) y `esparragos_por_brida.csv` (5) | DN `2.75` | 2,75" no es una medida nominal: el OD 42,2 mm es el de 1 1/4", y la tabla de espárragos 1/2" x 2 3/4" con 4 agujeros es la brida de 1 1/4" #150 | **Cambiar 2.75 por 1.25** en las tres tablas (hoy `controles_tablas.py` no encuentra caños ni espárragos de 1 1/4") |

Total: 9 errores confirmados (E1 a E9). E1 a E8 afectan 14 renglones (3 + 3 + 1 + 1 + 1 + 1 + 1 + 3) de los 2.107 de las dos tablas auditadas, aproximadamente el 0,7%; E9 afecta otros 13 renglones de tres tablas de apoyo. Ninguno de los 14 es un error de copia: todos vienen de la fuente.

### Lo que no es error pero conviene saber (y qué hacer con cada uno)

| Tema | Detalle | Recomendación |
|---|---|---|
| Bujes (22 renglones) | `buje_embutido` y `buje_hexagonal` tienen un solo DN, pero un buje es reductor ("3/4 x 1/2"). Bonney da un peso por columna de tamaño sin decir qué reducción (los valores no son monótonos: embutido 3/8" 0,07 y 1/2" 0,03 lb) | No usar para estimar. Cargar con DN2 o descartar |
| Bridas SO #900 y #1500 (38 renglones) | B16.5 no tiene SO en esas clases; los valores de #900 y #1500 son copias del WN (18 de 38 idénticos) | Marcar "no existe en B16.5" y que `controles_tablas.py` no los use |
| Bridas SW de más de 3" (76 renglones; 2 1/2" en #900 y #1500) | B16.5 llega a 3" (según la norma, a verificar) | Ídem |
| Bridas de 22" (clases 150 a 600) | La B16.5 no tiene 22" (hay 20" y 24") | Ídem; son datos de una tabla vieja |
| Duplicados con Thermometrics (13 pares) | Dos filas con el mismo tipo, DN y serie. La herramienta toma la primera (Wermac) | Ver "DIFIERE" |
| Casos de 3" #900 | Wermac pesa más (16,2 kg WN, 15,8 blind) que el de 2 1/2" (13,9 / 14,4) aunque en B16.5 la 3" #900 tiene menor diámetro exterior y menor espesor (OD 9,5 y 1,5 pulgadas, contra 9,62 y 1,62 de la de 2 1/2"). Cálculo: 14,3 kg WN, 13,1 blind. Thermometrics: 29 lb (13,2 kg) | Sospechoso, 13 a 20% alto. Poco material |

## 7. Renglones "DIFIERE" y "ATENCION"

### DIFIERE, bridas (Wermac contra Thermometrics, 13 pares)

Criterio: estimación por volumen con las dimensiones B16.5 (WN con bore Sch STD y XS: rango; SO, roscada y LJ con las dimensiones del cuello).

| Brida | Wermac | Thermometrics | Estimado | Razonable | Por qué |
|---|---|---|---|---|---|
| WN 2" #300 | 4,10 | 3,63 | 3,8 a 4,2 | 4,1 (cualquiera sirve; Δ 10%) | Cae dentro del rango; Thermometrics redondea a lb enteras |
| WN 2" #600 | 5,40 | 4,54 | 4,4 a 4,9 | **4,54 a 4,7** | El cálculo da la razón a Thermometrics; Wermac, 15 a 20% alto |
| WN 2 1/2" #600 | 8,10 | 6,35 | 6,5 a 7,0 | **6,5** | Ídem |
| WN 3" #600 | 10,40 | 8,16 | 8,7 a 9,5 | **9,1** (en el medio) | Ninguno de los dos cae en el rango |
| SO 2" #600 | 4,10 | 3,63 | 3,8 | **3,63 a 3,8** | Ídem |
| SO 2" #1500 | 11,30 | 9,98 | 9,98 | **9,98** | Cálculo = Thermometrics (esa SO no existe en B16.5 igual) |
| ciega 2" #150 | 2,30 | 1,81 | 2,6 | **2,3** | Wermac cerca del cálculo; Thermometrics bajo |
| SW 3" #150 | 4,10 | 3,63 | ~3,9 | 3,9 a 4,1 | Ambos dentro de 7% |
| roscada 2" #600 | 4,10 | 3,63 | 3,8 | **3,63 a 3,8** | Igual que SO |
| roscada 2" #1500 | 11,30 | 9,98 | 9,98 | **9,98** | Igual que SO |
| LJ 2" #600 | 4,10 | 3,63 | 3,8 | **3,63 a 3,8** | Igual que SO |
| LJ 2" #1500 | 11,30 | 9,53 | 9,98 | **9,8** | Wermac 15% alto |
| LJ 2 1/2" #1500 | 15,80 | 13,15 | 13,8 | **13,5** | Wermac 15% alto |

Patrón: en 2" a 3" de #600 y #1500, **Wermac está 10 a 25% alto**; Thermometrics y el cálculo coinciden entre sí con diferencia de menos de 5%. Como el CSV mantiene las dos filas y la herramienta toma la primera, hoy sale el valor alto de Wermac (conservador para flete, pero sobrestima). Recomendación: en esos 13 casos dejar como vigente el valor de la columna "Razonable".

### DIFIERE, forjados (Smith-Cooper contra Bonney, 45 pares)

Relación Smith-Cooper / Bonney: mediana 0,88; rango 0,37 a 2,00. Sin dimensiones suficientes para dirimir cada par. Los que se pudieron dirimir están en E5, E6, E7 y E8. Para el resto (casquetes, cuplas y codos, 0,59 a 1,58) el criterio es: **Bonney es el catálogo de fuente primaria y fue verificado con geometría; Smith-Cooper tiene tipeos propios** (E5 a E7). Usar Bonney y, cuando importe el peso, tomar el mayor de los dos como margen.

### ATENCION, accesorios BW (12 renglones)

| Renglón marcado | ¿Cuál es el razonable? |
|---|---|
| Codo radio largo 1 1/2" XXS 0,68 (menos que el 160: 0,82) | El XXS es el bajo: el cálculo da 0,86 kg (el 160 da 0,65, y la tabla trae 0,82). Usar **aprox. 0,9 kg**. Impacto mínimo |
| Tee 1/2" 160 0,16 y 3/4" 160 0,26 (menos que XS) | Valores de menos de 0,3 kg, la diferencia con el XS es de 0,01 a 0,04 kg: **inmaterial** |
| Tee 5" XXS 18,14 (menos que 160: 24,95) | **El malo es el 160** (E3); el XXS (18,14) es coherente con 5x4 XXS (17,24) |
| Tee reductora 2 1/2 x (2; 1 1/2; 1 1/4; 1) 160 (menos que XS) | Los XS de 2 1/2"xN no bajan con el ramal (3,26 a 3,18, casi iguales a la tee recta) y quedan sobre el STD (2,27 a 2,72): son sobreestimados. Con el 160 (2,95 a 3,18) hay 3 a 8% de diferencia: **inmaterial en kg totales** |
| Tee reductora 6 x 5 160 (14,06) | **Error** (E4) |
| Tee reductora 6x4, 6x3, 6x2 1/2 XXS (25,85; 24,95; 24,49), menores que el 160 | Probablemente bajos: el cálculo da unos 30 kg para 6x4 XXS (13 a 17% más). Usar el 160 mas 15% si el espesor es XXS |

### ATENCION, forjados (6 renglones)

Todos son del catálogo: codo 45° NPT 3000 y 6000 de 4" (iguales), media cupla SW 6000 y 9000 de 3/4", 1 1/2" y 2" (iguales o casi) y codo 45° NPT 2000 y 3000 de 2 1/2". Bonney usa el mismo cuerpo en clases contiguas, así que los empates se explican. El único que tiene un problema de fondo es el codo de 2 1/2" NPT (E8).

## 8. Conclusión: ¿sirven para estimar kg en cotizaciones?

**Sí, con márgenes.** Hay cero errores de copia, la conversión es correcta y la geometría confirma los órdenes de magnitud (ningún valor grosero de x2 o x0,5 desde 2"). Los pesos son aproximados por naturaleza (las normas no los fijan).

| Tabla | Margen razonable para estimar kg |
|---|---|
| Bridas B16.5, 2" a 24", #150 a #2500 | **±15%** (Wermac tiende a quedar 0 a 12% alto; el WN depende del schedule del cuello, que la tabla no distingue: otro ±10%). Para #900 WN de 14" a 24" Wermac está 30 a 40% por encima del cálculo: tomar como cota alta. |
| Bridas de 1/2" a 1 1/2" | Valores redondeados a lb enteras: hasta x1,8 de más en 1/2" y 3/4". Sin importancia en kg totales, no sirven para pesar una pieza sola |
| Accesorios BW (codos, tees, reducciones, casquetes) | **±10% en codos, ±15% en tees, reducciones y casquetes** (el cálculo geométrico cae entre 0,92 y 1,2 de la tabla; la fuente Hackney Ladish dice "approximated or estimated") |
| Forjados B16.11 (Bonney) | **±25%**. Los dos fabricantes difieren hasta ese orden (mediana de la relación 0,88; casos extremos de 0,37 a 2,0 en piezas de menos de 1 kg o con tipeos) |

Condiciones de uso:

1. **No usar** los renglones E1 a E8 con el valor actual, y corregir E9 (hoy hace fallar las búsquedas de 1 1/4").
2. **No usar** bujes (sin DN2), SO de #900 o más, SW de más de 3" y bridas de 22" hasta que se marquen como "no existe en B16.5".
3. Para los 13 pares duplicados de bridas, usar la columna "Razonable" del apartado 7.
4. Los kg salen de tablas aproximadas: mostrarlos como **estimados**, no como pesos garantizados. Para un límite de transporte, sumar una reserva del 10%.
5. `herramientas/controles_tablas.py` toma la primera fila que coincide (`next(...)`) y no mira el schedule del cuello de la WN, ni distingue entre Bonney y Smith-Cooper ni entre filas duplicadas. Hoy da el valor de Wermac y de Bonney (el primero del archivo), que es lo correcto, pero hay que dejarlo documentado.

## 9. Pendientes que no resolvió esta auditoría

- Las tablas de pesos de B16.5 de Wermac vienen "de Texas Flange" según la página; esa fuente no se consultó (no estaba en la lista y no se pudo verificar).
- No se verificó contra un catálogo impreso de Bonney la unidad "libras" más allá de la geometría (ver apartado 3). La geometría la deja fuera de duda, pero si Matías tiene el catálogo, sirve.
- No se verificaron los largos H y E de reducciones y casquetes de B16.9 con la norma (tomados de memoria); las relaciones 1,16 y 1,18 de esos dos grupos son orientativas.
- No se revisó `factores_accesorios.csv` ni el resto de `esparragos_por_brida.csv` más allá del error del 2,75.
