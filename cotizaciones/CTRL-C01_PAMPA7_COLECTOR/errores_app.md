# CTRL-C01 — Errores de la app (skid colector para PAD de 6 pozos, Pampa 7)

Caso de control, no es una cotización. Equipo: **skid colector 6"/3" #300 para PAD de 6 pozos** (ítem 2 del contrato marco
PAMPA ENERGIA/7, PRES 169 rev. A del 14-08-2026, 18 colectores). Costos por colector, USD sin IVA, a la fecha de cada fuente
(sin ajuste por inflación), EXW Quilmes (sin transporte).

- **REAL**: hoja "Colector RDA" de `Cot Skid Manifolds Colectores RDA Contrato Marco (2da RDA).xlsx` (materiales, MO y servicios 63.946,41 + válvulas Taval 2.289,95 + caución 253,66).
- **APP**: `precotizar.py --excluir "PAMPA ENERGIA/7"` → `cotizacion_auto.json`, `comparacion_historico.md`.
- **APP sin fuga**: lo mismo, excluyendo también la copia de la planilla de Pampa 7 que está dentro de la carpeta de Pampa 5 (`--excluir "ADICIONAL DE OC"`, corrida en el scratchpad, no se guardó). Es lo que la app daría si la exclusión funcionara.
- **AGENTE**: recotización a mano (`cotizacion_agente.json`, `comparacion_agente.md`), sin precios de Pampa 7 ni de su copia; antecedente Pampa 5 (2 colectores iguales, junio de 2026) y cotizaciones de proveedores.

## Totales por rubro y por colector

| Rubro | REAL | APP | APP sin fuga | AGENTE | APP − REAL | AGENTE − REAL |
|---|---|---|---|---|---|---|
| Otros materiales (piping, instrumentos, bastidor) | 12.928,91 | 10.410,22 | 12.402,12 | 13.727,88 | −2.518,69 | +798,97 |
| Válvulas 3 vías motorizadas (pos 31) | 20.436,00 | 20.436,00 | 26.044,48 | 21.519,48 | 0,00 | +1.083,48 |
| Tablero eléctrico (pos 35) | 12.000,00 | 12.000,00 | 12.000,00 | 12.000,00 | 0,00 | 0,00 |
| Válvulas Taval (pos 27–30) | 2.289,95 | 1.144,90 | 1.282,60 | 3.520,32 | −1.145,05 | +1.230,37 |
| Armado y soldadura | 8.350,00 | 8.877,22 | 8.877,22 | 8.350,00 | +527,22 | 0,00 |
| Horas ITT (ingeniería, calidad, planta y PH) | 1.227,00 | 3.711,64 | 3.711,64 | 1.339,50 | +2.484,64 | +112,50 |
| Granallado y pintura | 4.410,00 | 270,05 | 270,05 | 4.410,00 | −4.139,95 | 0,00 |
| Radiografía y LP | 4.594,50 | 9.330,00 | 9.330,00 | 4.594,50 | +4.735,50 | 0,00 |
| Caución | 253,66 | 0,00 | 0,00 | 240,78 | −253,66 | −12,88 |
| **Total por colector** | **66.490,02** | **66.180,03 (−0,5%)** | **73.918,11 (+11,2%)** | **69.702,46 (+4,8%)** | **−309,99** | **+3.212,44** |

**Lectura:** el −0,5% de la app es casualidad: sobrestima la radiografía y las horas en ~7.200, subestima la pintura y algunos
materiales en ~7.500 y, además, **copia precios del propio proyecto** (error 1). Sin esa fuga da +11%. Solo 13 de 35
renglones caen dentro de ±15% y 6 quedan sin precio.

La diferencia del agente (+4,8%) se explica así: retención wafer a 401,98 de Pampa 5 contra 200 en Pampa 7 (+1.212); válvula
de 3 vías según la cotización de Valvtronic (3.586,58) contra 3.406 en la planilla (+1.083; la OC real fue de 4.215,21);
espárragos a 10 USD de antecedentes contra 8 estimados (+584); sockolets a 14 USD de Futura/Francovigh contra 6 estimados (+158).

## Errores de la app, por impacto (USD por colector)

| # | Error | Evidencia | Impacto | Cómo corregirlo en la herramienta |
|---|---|---|---|---|
| 1 | **El control se copia a sí mismo: `--excluir` no saca el propio proyecto.** `fuentes_originales/.../PAMPA ENERGIA/5 .../4.Armado de la Oferta Comercial/ADICIONAL/ADICIONAL DE OC Colectores.xlsx` contiene las hojas completas de Pampa 7 ("PEDIDO DE PRECIOS Doc 5806149694", recepción 29-07-2026). El catálogo las carga como origen Pampa 5, con fecha 29-07-2026, y la exclusión por carpeta no las ve | `cotizacion_auto.json`: pos 31 VAL-03228 3.406 (el precio exacto de Pampa 7; la planilla de Pampa 5 usó 4.340,75), pos 33 INS-02707 856,63, pos 27 VAL-03188 29,53, pos 28 VAL-03181 120, pos 29 VAL-03184 131,131. Mismo caso en VAL-03283 y otros | **Esconde +7.738** (APP 66.180 contra 73.918 sin fuga); la válvula 31 sola, 5.608 | Identificar el proyecto por el contenido (n.º de pedido "Doc …", cliente y fecha de recepción de la hoja), no por la carpeta; marcar las hojas duplicadas entre carpetas (hash de contenido) y atribuirlas a su proyecto original; que `--excluir` también acepte el n.º de pedido |
| 2 | **Radiografía con tarifa y cantidad de servicios que no son las del cliente.** Placas a 15 + servicio 490 cada 40 placas (Antonelli 11-2025) sobre 104 juntas; la planilla de 2026 de Pampa usa DB NDT a 6,5 por placa, 408 por servicio y 294 de LP (92 juntas, 6 servicios). En `tarifas.csv` la tarifa de 6,5 figura "reemplazada" (2024) aunque las planillas de 2026 la siguen usando. No calcula la LP de las soldaduras SW y de los olets | `precotizacion.md` §3: "328 placas chicas + 0 grandes + 9 servicio(s) = USD 9,330.00"; planilla, hoja ENOD Colector: 4.594,50 | **+4.735,50** | Tomar la tarifa de END más reciente del catálogo de servicios del mismo cliente o la familia (END-00211, DB NDT 6,5), no una sola tarifa fija; parámetro de placas por servicio; sumar LP cuando hay SW u olets; revisar el campo `vigente` de `tarifas.csv` |
| 3 | **Pintura solo de caños y niples.** Calcula 5,40 m² (12,8 m de caño y los niples) e ignora bridas, tees, válvulas (6 de 3 vías de 3") y el bastidor del skid (800 kg). La planilla: 33,6 m² de piping + 54,6 m² de skid | `precotizacion.md` §3: "5.40 m² … = USD 270.04" | **−4.139,95** | Sumar m² de accesorios, bridas y válvulas (tablas de pesos y superficies o un factor por pieza) y del bastidor (m² por kg de perfil, unos 0,03 m²/kg en UPN), con el overspray de las planillas (20–30%) |
| 4 | **Las cotizaciones de proveedores del proyecto no están en el catálogo de materiales.** Valvtronic QQ-3273105-00 (3.586,58), Valbol 85071827 (4.378) y MS Juntas 48.445 (2" 2,30 y 3" 3,98) solo están resumidas en `proveedores_2026.csv`, y la de MS Juntas mal leída ("Juntas RTJ BX153 y esparragos 316L… importes truncados": son espiraladas "ESP SWI", con precios legibles). La app usa entonces estimados de planilla. Sin la fuga, el transmisor sale Rosemount 2.848,53 aunque el plano pide ABB | APP sin fuga: pos 31 4.340,75 (Pampa 5, un promedio) contra 3.586,58 de la cotización; pos 33 INS-02709 Rosemount 2.848,53 | **+4.525** (pos 31) **+1.947** (pos 33, marca) en el escenario sin fuga | Cargar al catálogo, con tipo `cot`, los PDF de `5.Proveedores 3ros` (precio, especificación y fecha); en instrumentos, priorizar la marca de `modelo_fabricante` antes que el precio "otra marca" |
| 5 | **Horas y soldadura duplicadas, con un antecedente de otro alcance.** La app suma soldadura propia (449,94 pulg × 19,73 de costo de planta de 10-2024), montaje de 256,5 h de TECPETROL/9 (manifold S-600 armado por ITT) e ingeniería y calidad. En Pampa, el armado y la soldadura los hace Ledesma (presupuesto 200283, 8.350, mismo alcance, en `buscar_servicio`: FAB-00053), e ITT pone 54 h de planta. `horas_por_equipo.csv` no tiene ni Pampa 5 ni Pampa 7 | `precotizacion.md` §2 y "Horas…": montaje 256,5 h × 13 = 3.334,50 | **+3.011,86** (horas +2.484,64; soldadura +527,22) | Cargar Pampa 5/7 en `horas_por_equipo.csv`; si el antecedente más parecido tiene MO de terceros global (Ledesma), proponer esa MO y solo las horas de planta del antecedente, en lugar de soldadura propia + montaje propio |
| 6 | **Excluir un precio borra la pieza entera, y el similar se elige mal.** Si el último precio de una pieza es del proyecto excluido, se descarta toda la fila del catálogo aunque el historial tenga la lista Renard (BRI-01031 cód. 8252 18,50; ABW-00390 cód. 3830 64,11; ABW-00413 cód. 3527 164,91; JUN-02775). Después ordena los similares poniendo otro diámetro principal antes que otro ramal o schedule (tee 6"x3" → 4"x3" a 86,29 habiendo 6"x2½" a 164,88), y si el primer similar no pasa la regla de 1,6 veces deja SIN PRECIO sin probar el siguiente (brida ciega 2": el 12" primero y el 3" quinto). En los olets compara el diámetro del caño (12"x3/4") y no la salida | Pos 6, 12, 22, 23, 24, 30 SIN PRECIO; pos 19 4"x2" 111,28; pos 21 4"x3" 86,29; pos 20 PROVEMET 69,95 de 2025 en lugar de Renard XS 60,36 | **−1.733,66** (neto de sin precio y similares) | Con la exclusión, volver al precio anterior del historial del mismo código (`catalogo_materiales_historial.csv`); ordenar similares por distancia (igual Ø principal > igual ramal > schedule) y probar el siguiente candidato si falla la regla de 1,6; en olets medir por la salida |
| 7 | **Espárragos: la medida se lee mal.** `texto_busqueda` pega el diámetro después de la descripción ("… 3/4 x 6" + "3/4"" → "3/4 x 6 3/4"; "5/8 x 3.5" → "5/8 x 3"), y los 4 renglones caen en un 3/4 x 10 de 5 USD (INARTECO). Además marca "unidad distinta: catálogo por uni, plano por un" | `precotizacion.md` pos 15–18 | **−876** (292 espárragos × 3) | No agregar el diámetro si la descripción ya trae la medida; aceptar decimales en la medida; normalizar "uni" = "un" en `unidad_norm` |
| 8 | **No se toma el precio más reciente con la misma especificación.** Bloqueo y purga 1/2" 316: elige VAL-03198 a 137 (TAVAL/55, 22-04-2026) habiendo VAL-03200 ABAC a 180 (Pampa 5, 26-06-2026) | `cotizacion_auto.json` pos 26 | **−645** | A igual coincidencia, ganar el más reciente (regla P4) |
| 9 | **Bastidor valorizado como chapa de 1/2" con 10% de recortes.** "Bastidor (perfiles)" entra como "chapa negra lisa 1/2"" a 1,27/kg; la planilla usa 1,5/kg y 20% de desperdicio (960 kg) | pos 34: 800 kg × 1,2744 = 1.019,52 contra 1.440 | **−420,48** | Reconocer bastidor, perfil, UPN o IPN como perfil (hierro ángulo o UPN de `acero_por_kg.csv`) y aplicar el desperdicio de estructura (20%) |
| 10 | **Caución no prevista.** La planilla suma el seguro de caución (253,66; 354,91 en la hoja Resumen) | `precotizacion.md` §4 no lo lista | **−253,66** | Agregarla a "a completar" o calcularla como % del precio cuando el pliego pide pólizas |
| 11 | **Un precio verbal entra como antecedente, y el paso no se compara.** Pos 28 (1" #300) toma VAL-03181 a 120 = "Precio verbal R Alvarez" (hoja Deriv a 2 Tronc) como `ant`, y es paso total cuando el plano pide paso reducido. El tablero eléctrico (12.000, el 25% de los materiales) es un estimado de planilla sin cotización y sale como `ant` similar | Planilla Pampa 7, hoja Deriv a 2 Tronc: "V. Esférica 1" #300 RF PT … Precio verbal R Alvarez"; `cotizacion_auto.json` pos 28 y 35 | **+105** (pos 28); riesgo sin cuantificar en el tablero | Pasar a `est` los precios con nota "verbal", "aprox." o "estimado" en el origen; comparar el atributo `paso` (PT/PR); avisar cuando un estimado pesa más del 10% |
| 12 | **Barra fija de 6 m.** Agrega compra extra (7b, 8b) suponiendo barras de 6 m; los caños de 3" y 6" A106 vienen en tiras de unos 12 m (la planilla: "media tira de 12,8 m"), y 18 × 6,4 m = 9 tiras justas | `precotizacion.md` 7b, 8b | **+22,86** | Largo de barra por diámetro y origen (6 m hasta 2"; 12 m DRL desde 3"), o tomarlo del catálogo |
| 13 | **`comparar_historico.py`: el rubro sale mal y pisa su propia salida.** (a) "Horas de montaje en planta (armado, movimientos, prueba hidráulica)" (pos ARM) va a "prueba hidráulica", porque la palabra se evalúa antes que la posición del rubro siguiente. (b) Con `--json` escribe igual `comparacion_historico.md` y pisa la comparación de la app | `comparacion_historico.md`: "prueba hidráulica 0,00 / 3.334,50" e "ingeniería, calidad y montaje −69%" | 0 USD (el informe engaña) | Buscar primero la posición en todos los rubros y después las palabras; nombrar la salida según el JSON (`comparacion_<json>.md`) |

## Lo que la app hizo bien
- Bridas WN, SW y ciegas de 1": iguales a la lista Renard 12-2025 (las mismas que usó la planilla).
- Caño por metro sin contar sus extremos (lección 51) y olets medidos por la salida (lección 52).
- Marca `taval: true` en las válvulas 27–30 (`FTV` = 1).
- Cuenta de soldaduras razonable: 104 juntas a tope contra las 92 de la hoja ENOD (cuenta un caño intermedio en uniones accesorio–accesorio).

## Observaciones de la planilla real (no son errores de la app)
- La caución del colector es 253,66 en su hoja y 354,91 en la hoja Resumen; el Resumen suma además 1.500 de transporte.
- La válvula de 3 vías está costeada a 3.406, debajo de las dos cotizaciones (3.586,58 y 4.378); la OC posterior fue de 4.215,21 ("gasto de más").
- Juntas, espárragos, niples, sockolets y tablero (12.000) son estimados de la planilla ("Estimado"), sin cotización de proveedor.
