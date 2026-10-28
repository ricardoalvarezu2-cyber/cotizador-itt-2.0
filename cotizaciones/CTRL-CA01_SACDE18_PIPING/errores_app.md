# CTRL-CA01: errores de la app (prefabricado de piping, Sacde 18 / TGS)

Es un caso de control, no una cotización. Costos por "conjunto de spools" (ver la definición abajo), en USD sin IVA y sin ajuste por inflación. Revisión del 28-10-2026.

- **REAL**: planilla de ITT `Sacde/18 …/7.Propuesta Comercial (envío al Cliente)/Sacde - Cotización piping x pulgada+END y mtr2 Rev4 Direccion.xlsx` (oferta PRES 147 rev A del 20-04-2026). Es la única planilla de costo del proyecto: la carpeta "4.Armado de la Oferta Comercial" solo tiene la oferta técnica 147A, sin precios.
- **APP**: `python herramientas/precotizar.py cotizaciones/CTRL-CA01_SACDE18_PIPING --excluir "Sacde/18"`, sin completar nada a mano (`cotizacion_auto.json`, `precotizacion.md`). Después, `comparar_historico.py` (ver el error 8: se cae, y se corrió con un envoltorio que no modifica la herramienta).
- **AGENTE**: recotización a mano con las herramientas, sin precios de Sacde/18 (`cotizacion_agente.json`, `comparacion_cotizacion_agente.md`).

## Recorte del alcance: qué es un "equipo"

La oferta es un acuerdo marco por pulgada diametral para 5 plantas: 21.533 + 22.919 + 3.155 + 7.618 + 16.588 pulgadas y USD 2,21 M. Los materiales los provee el cliente (TGS y SACDE). ITT pone la soldadura, los END, los consumibles, el QA/QC y el data book. La pintura se vende aparte, a USD 40/m².

La planilla costea **por diámetro y por planta**: pulgadas × (soldadura + END) × 1,05 de rechazo. Como unidad se tomaron dos renglones que la planilla costea por separado:

- **PC Chacharramendi, 36"**: 2.700 pulgadas. Son las líneas 5001-GSS-36-A, 5018-GSS-36-A y 5301-GSD-36-A de la hoja PIP 2.
- **PC Chacharramendi, 12"**: 228 pulgadas. Es la línea 7XXX-VTA-12-C.

Para la tabla del plano se usó la MTO de TGS, TE-B10-202.503-LM-PI-1001 Rev 1 (hoja PIP 3), con la columna "CANT. FINAL MONTAJE". Es la MTO ajustada por la planilla a las pulgadas del layout (factor 0,9105 en 36"; 1,0204 en 12"):

- caño 36" sch 40 X70: 325 m;
- caño 36" sch 10 X60: 181 m;
- 7 bridas WN 36" #600;
- 6 codos 36";
- caño 12" sch 20: 190 m.

Esta unidad prueba lo que el caso tenía que probar: caño por metro, muchas juntas, soldadura por pulgada, RX y pintura.

## Tabla por rubro (por conjunto de spools)

| Rubro | REAL | APP | AGENTE | APP vs REAL |
|---|---:|---:|---:|---:|
| Materiales (provistos por el cliente) | 0,00 | 286.407,48 | 0,00 | +286.407 |
| Soldadura (+5% de rechazo en REAL y AGENTE) | 32.281,20 | 16.407,79 | 35.103,60 | −49% |
| Radiografía 100% (+5% de rechazo en REAL y AGENTE) | 25.430,74 | 2.024,00 | 19.477,50 | −92% |
| Ingeniería, calidad, movimientos y PH | 0,00 (incluido en la pulgada) | 13.353,80 | 3.024,00 | +13.354 |
| **Total sin pintura (lo que cotiza la planilla)** | **57.711,94** | **318.193,07** | **57.605,10** | **+451%** |
| Total sin pintura y sin materiales | 57.711,94 | 31.785,59 | 57.605,10 | −45% |
| Granallado y pintura (se vende aparte por m²) | no está en el costo; se vende a 40 USD/m² | 4.938,82 m² × 50 = 246.940,85 | 1.688,25 m² × 40 = 67.530,00 | m² ×2,9 |
| Total con pintura | — | 565.133,92 | 125.135,10 | — |

La app no deja renglones SIN PRECIO, así que no hay "total sin lo que queda SIN PRECIO" que mostrar. AGENTE contra REAL da −0,2% sin pintura: soldadura +9%, RX −23% y +3.024 en horas que la planilla no separa.

**Nada del −45% en MO y servicios es casualidad.** Hay dos errores grandes que se compensan en parte. Las juntas de caño no se cuentan, lo que da −63.017 en soldadura y −9.445 en RX. El factor de espesor más la tarifa empujan para arriba: +47.144 en soldadura.

## Errores de la app, ordenados por impacto (USD por conjunto, APP − REAL)

| # | Error | Evidencia | Impacto | Cómo corregirlo (herramienta) |
|---|---|---|---:|---|
| 1 | **No se puede decir "materiales provistos por el cliente".** La app cotiza los 5 renglones: 286.407, incluidas las compras extra de barra. La tabla lo dice en `modelo_fabricante` ("provisto por el cliente") y el pliego también (columnas "CANT. POR TGS / SUM. POR SACDE"). Es un caso típico de prefabricado, de MO vendida sola (familia CA/S) | `precotizacion.md` §1 · `precotizar.material()` no tiene la opción | **+286.407** | Columna opcional `provee` (itt/cliente) en la tabla del plano, o un parámetro `materiales_cliente`. Con "cliente", el material va a precio 0 con la fuente "provisto por el cliente", sin compra extra. Igual cuenta para soldadura, pintura y PH. Avisar si la descripción o `modelo_fabricante` dicen "provisto/suministro del cliente" |
| 2 | **Pintura ×3 sobre todos los caños**, porque "hay bridas o accesorios" (`FACTOR_ACCESORIOS = 3`, lección 60). Con 696 m de caño recto y 13 accesorios, 1.646 m² de caño pasan a 4.939 m², cuando reales hay 1.688 (la MTO de TGS dice 1.637 m² para 36"). A eso se suman la tarifa de 50 USD/m² (criterio ITT de 10-2026, posterior a la fecha de referencia) y el hecho de que la pintura entra en el costo del equipo, cuando el pliego la pide aparte por m² ("NO INCLUYE PINTURA"; ítem f de la oferta) y sin mano final | `precotizacion.md` §3 · `precotizar.superficie_pintura()` | **+246.941** (m² de más +162.528; tarifa +16.883; alcance +67.530) | Sumar m² por pieza con las tablas de bridas y accesorios (o un factor que dependa de accesorios por metro de caño), no ×3 fijo. Opción "pintura por m² aparte" que la deje fuera del total. Tarifa con fecha ≤ `fecha_referencia` |
| 3 | **No cuenta las juntas entre barras de caño.** Con caño por metro, las juntas salen solo de los extremos de accesorios y bridas (×1,5). Así quedan 14,25 juntas, contra 94 reales (75 de 36" y 19 de 12"). La línea de 12", que es de caño recto (190 m), da **0 soldaduras** | `precotizacion.md` §2 · `precotizar.soldaduras()` (`por_metro`, `mult = 2 × 0,75`) | **−63.017** en soldadura y **−9.445** en RX (a las tarifas de la app) | Sumar las juntas de empalme: ceil(metros ÷ largo de barra) por renglón de caño (12 m desde 3", 6 m en diámetros chicos), además de las de accesorios. Avisar si un renglón de caño no genera ninguna junta |
| 4 | **Factor de espesor y tarifa que no corresponden a prefabricado por pulgada diametral.** La app usa pulg-eq por espesor (36" sch 40 = ×2,0) × 16 USD. El prefabricado de volumen se cotiza por pulgada diametral con base sch 40 = 1, y se ajusta solo por schedule distinto (la planilla: 10,50 USD/pulg; terceros Ledesma 13 en 2025 y Quesada 12 en 2026). Con las 94 juntas reales, la app daría 4.964 pulg-eq × 16 = 79.425, 2,5 veces lo real. La planilla calculó también esa variante (hoja "Soldadura + END ITT", "36" = 72 pulg × 16") y la descartó. Tampoco se modela el 5% de rechazo y reparaciones con RX 100% | `precotizar.soldaduras()` · `tarifas.csv` (soldadura 16) · planilla Sacde/18, hojas Resumen y PIP 1 (factor por sch) | **+47.144** (en soldadura, una vez corregido el error 3) | Para familia CA o servicio de prefabricado: `parametros.modo_pulgada = "diametral_sch40"` con la tarifa de prefabricado de terceros (catálogo SOL-*). Factor de rechazo (`parametros.rechazo_pct`, 5%) sobre soldadura y END |
| 5 | **Radiografía con tarifa DB NDT y placas de tabla.** La app usa 8 USD la placa grande y 408 el servicio (lista DB NDT citada en una planilla de Pampa de 08-2026, sin el documento del proveedor y posterior a la fecha de referencia del 20-04-2026). Lo real, de Antonelli y vigente en abril: placa grande 20 y servicio 490. Además, 7 placas por junta de 36" (la planilla usa 9) y 6 chicas en 12" (la planilla, 4 grandes) | `precotizacion.md` §3 · `tarifas.csv` (end DB NDT 2026-08) · `factores_soldadura.csv` | **−13.962** (una vez corregido el error 3) | Elegir la tarifa con fecha ≤ `fecha_referencia` y con documento original. Si DB NDT y Antonelli difieren más del 50%, mostrar las dos y avisar. Revisar las placas por junta de los diámetros grandes (solape) |
| 6 | **Horas de ingeniería, calidad y montaje de un skid con bombas** (Sacde/14) para un prefabricado de spools: 282 h de ingeniería, 114 de calidad y 570 de montaje. En el prefabricado, la ingeniería (isométricos) la pone el cliente. QA/QC, data book, movimientos y PH van dentro de la pulgada. `estimar_horas` no tiene un tipo "piping/spools/prefabricado" y avisa "sin antecedente del mismo tipo", pero igual las suma | `precotizacion.md` §3 · `estimar_horas.TIPOS` | **+13.354** | Tipo "prefabricado" (familia CA): sin ingeniería ni montaje, calidad por spool o por pulgada. Si no hay antecedente del mismo tipo, dejar las horas en 0 con ⚠ en lugar de sumarlas |
| 7 | **Similares de materiales inválidos para diámetros grandes:** caño 24" sch 20 para un 36" sch 40 (la regla de 1,6× lo deja pasar: 141 contra 420 kg/m); brida 32" para una 36"; **codo de 10" XS para uno de 36"** (ABW-02343: el catálogo no lee el diámetro "10" sin comillas, y la regla de 1,6× no corre cuando falta el diámetro; un codo 36" sch 40 pesa 951 kg, uno de 10", ~40) | `precotizacion.md` pos 1–4 · `catalogo_materiales.csv` ABW-02343, CAN-01480, BRI-01289 | 0 en este caso (enmascarado por el error 1); en un caso con materiales de ITT, codos −4.000 a −5.000 c/u y caño −30% | Rechazar el similar con diámetro desconocido en piezas de 12" o más. En diámetros grandes, comparar por kg/m o por peso de la pieza, no por 1,6× de diámetro. Leer "CODO … 90º 10 BW" como 10" |
| 8 | **`comparar_historico.py` se cae** si el material real es 0 (provisto por el cliente): `pct()` devuelve None y el f-string falla (`TypeError` en la línea 82). Tampoco tiene un rubro para "otros servicios" que la planilla incluye en la pulgada | traceback en la bitácora | 0 (impide el control) | `pct()` con real 0: mostrar "—" o "n/a" |
| 9 | **Barra de compra de 6 m fija** (menor, ya conocido): suma 5 m de 36" y 2 m de 12" de compra extra (caño que, además, provee el cliente; en 36" la barra es de 12 m). Prueba hidráulica: calcula 324.960 l de volumen y 18 h, y después la saca porque el montaje "incluye PH" | `precotizacion.md` 1b, 2b, 5b y §3 | +5.050 (dentro del error 1) | Largo de barra por diámetro. Sin compra extra si provee el cliente |
| 10 | **`buscar_servicio.py` no tiene `--excluir`** (ya conocido): los primeros resultados de END eran los del propio Sacde/18 (END-00149 a 00153, 00212 y 00213). Hubo que salteárselos a mano | salida de `buscar_servicio.py "soldadura prefabricado piping pulgada"` | 0 | Agregar `--excluir` a los buscadores |

**Peso:** sin materiales ni pintura, la app queda en −45%. Los errores 3 (juntas) y 4 (factor y tarifa) se compensan en parte (−72.462 y +47.144). Con materiales y pintura, el total sale 9,8 veces el real (+507.422). Los errores 1 y 2 (+533.348) explican más que todo ese desvío. El resto es negativo: juntas, RX y tarifa.

## ¿Siguen los errores de los controles anteriores (lecciones 51–66)?

| Lección | Estado en este caso |
|---|---|
| 58 (horas de otro tipo) | **Sigue**: no hay un tipo para prefabricado. Avisa, pero suma 13.354 |
| 59 (soldaduras sobrecontadas) | **Se invirtió**: con caño largo y pocos accesorios, ahora las juntas quedan subcontadas (−85%) |
| 60 (pintura solo de caños) | **Sobrecorregida**: el ×3 fijo triplica los caños rectos |
| 61 (RX con Antonelli) | El cambio a DB NDT baja la RX 60% sin documento original y con fecha posterior a la referencia |
| 63 (similares inválidos) | **Sigue** en diámetros grandes y con diámetro no leído |
| 65 (exclusión) | Funciona en precotizar (no tomó nada de Sacde/18). Falta en `buscar_servicio` |
| 66 (comparar_historico) | El rubro ya no se confunde, pero se cae con material real 0 |

## Diferencias del agente que no son errores de la app

- **Juntas:** el agente cuenta 77 (61 de 36" y 16 de 12": una por barra de 12 m + 2 por codo + 1 por brida); la planilla, 94 (desde el layout); la MTO de TGS, ~82. En un prefabricado real, los empalmes entre spools de 12 m van en campo. Acá se tomaron todas como de taller, igual que la planilla (`extremos_campo` = 0).
- **Tarifa de soldadura:** el agente usa 13 (Ledesma) + 1 de consumibles × 1,05 = 14,70 USD/pulg, contra 10,50 × 1,05 = 11,03 de la planilla. Con factor de espesor (36" sch 40 = ×2), la soldadura del agente sumaría unos USD 24.000 más: es un riesgo técnico de la tarifa de la planilla.
- **RX:** el agente usa Antonelli con 8 placas por junta de 36" (desarrollo de 2.871 mm con solape); la planilla, 9.
- **Horas:** el agente agrega calidad (30 h), movimientos y carga de unas 180 t (180 h) y PH (18 h): USD 3.024. La planilla no los separa.
- **Pintura:** se vende a 40 USD/m², el mismo valor que el costo de referencia de Sacde/14 y Sacde/20 (20,03 + 20,41). Prácticamente sin margen, salvo que la mano final excluida baje el costo.
- **Sesgo:** el agente leyó la planilla real antes de recotizar (había que definir la unidad), así que sus criterios de tarifa pueden estar sesgados hacia lo real.
