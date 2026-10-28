# CTRL-SK01: errores de la app (skid concentrador 1000623708, YPF Lic 69343)

Caso de control, no es una cotización. Costo **por equipo** (serie de 6), USD sin IVA y sin ajuste por inflación. Revisión del 28-10-2026.

- **REAL**: planilla PC0 de ITT `YPF/28- Lic 69343 - SKIDS CONCENTRADORES VCD26217 - BLOQUE LAN/4.Armado de la Oferta Comercial/Cotización Lic 69343 Skid concentradores VCD26217 PC0.xlsx`, hoja 1000623708 (10-10-2026). Costo de la PC0: USD 103.326,16; **corregido y con el alcance del plano: USD 85.995,15** (detalle en `bitacora.md` y `historico.csv`).
- **APP**: precotización automática sin completar nada a mano:
  `python herramientas/precotizar.py cotizaciones/CTRL-SK01_YPF28_SKID708 --excluir "YPF/28" --excluir "pedidos_web" --excluir "COT26-0330"`
  y `python herramientas/comparar_historico.py cotizaciones/CTRL-SK01_YPF28_SKID708` → `comparacion_historico.md`.
- **AGENTE**: recotización a mano con las herramientas y las fuentes abiertas, sin precios de YPF/28 ni de COT26-0330 (`cotizacion_agente.json`; `comparar_historico.py ... --json cotizacion_agente.json` → `comparacion_cotizacion_agente.md`).

## Tabla por rubro (por equipo)

| Rubro | REAL | APP | AGENTE | APP vs REAL |
|---|---:|---:|---:|---:|
| Válvulas Taval (pos 25–30) | 27.002,86 | 15.157,37 | 26.997,54 | −44% |
| Resto del piping (pos 1–24, con compras extra) | 32.105,59 | 24.882,67 | 27.611,67 | −22% |
| Perfilería del bastidor (pos 31) | 1.700,00 | 1.611,00 | 1.615,00 | −5% |
| **Materiales** | **60.808,45** | **41.651,04** | **56.224,21** | **−32%** |
| Soldadura y armado de piping | 10.700,00 (Ledesma) | 6.826,96 | 7.594,72 | −36% |
| Fabricación de la estructura | 2.550,00 | 2.550,00 | 3.400,00 | 0% |
| Radiografía y LP | 5.000,00 | 2.753,00 | 2.747,00 | −45% |
| Granallado y pintura | 2.360,00 | 1.964,50 | 2.555,00 | −17% |
| Ingeniería, calidad, montaje y PH | 4.117,50 | 5.501,15 | 2.888,00 | +34% |
| Seguro de caución | 459,20 | 0,00 | 450,00 | −100% |
| **MO y servicios** | **25.186,70** | **19.595,61** | **19.634,72** | **−22%** |
| **TOTAL por equipo** | **85.995,15** | **61.246,65** | **75.858,93** | **−29%** |
| Total sin lo que la app deja SIN PRECIO (pos 21 y 28) | 85.876,05 | 61.246,65 | 75.763,83 | −29% |

AGENTE contra REAL: −12% (materiales −8%, MO y servicios −22%). La MO del agente es propia (pulgada a 16 USD + 176 h de montaje); la PC0 terceriza armado y soldadura en Ledesma (10.700 + 3.000 de montaje), que es más cara. Ver "Diferencias del agente".

**La app da −29% y esta vez no hay compensación**: los materiales quedan USD 19.157 abajo, casi todo por **dos válvulas de 12" mal identificadas** (−11.892).

## Errores de la app, por impacto (USD por equipo)

| # | Error | Evidencia | APP − REAL | APP − AGENTE | Cómo corregir (herramienta) |
|---|---|---|---:|---:|---|
| 1 | **Retención 12" #300 cotizada con una retención wafer 3" #150 (USD 114).** VAL-03284 dice `VALVULA WAFER \| 3 \| 150# \| ... RETENCION WAFER` (Sacde/15): el "3" sin comillas no se lee como diámetro, queda "diametro: sin dato" y la regla del error 53 (más de 1,6 veces de diferencia = SIN PRECIO) no se aplica cuando falta el diámetro del candidato. La serie distinta (150 vs 300) tampoco frena | `precotizacion.md` pos 27 · `catalogo_materiales.csv` VAL-03284 · `LM-TANQUE GLICOL.xlsx` fila 39 | **−9.144** | −9.468 | En válvulas y bridas, un candidato **sin diámetro** no puede ser similar de un pedido con diámetro: SIN PRECIO. En `catalogo_materiales.atributos`, leer el Ø de planillas con columnas sueltas ("\| 3 \|" después del tipo). Alerta si el precio por unidad de una válvula ≥ 8" es menor que USD 500 |
| 2 | **Esférica 12" #300 PT con caja reductora cotizada con una válvula de retención 12" #600.** VAL-03171 es `TAVAL \| VALVULA ESFERICA \| Ø 12 - Ret \| RF \| 600#` (Sacde/12, fila 136): la planilla de Sacde pone "VALVULA ESFERICA" en la columna de tipo y "Ret" (retención, alternativa wafer) en el detalle; el catálogo la clasificó como esférica. La esférica 12" #600 PT real de la misma planilla (fila 131, USD 7.634) no se eligió. Se mostró como "similar: serie 600" sin avisar que es otro tipo de válvula | `precotizacion.md` pos 30 · `catalogo_materiales.csv` VAL-03171 · `LM costos Filtro Coalecedor FC 301 y 302 #600 PC0-C.xlsx` filas 131 y 136 | **−2.748** | −2.418 | `catalogo_materiales`: si el detalle dice "Ret", "retención", "check" o "wafer", el tipo es retención aunque la columna diga esférica (manda la palabra más específica). En válvulas, tipo distinto = nunca similar. Similar de otra serie: ajustar o avisar en rojo |
| 3 | **Similares de menor diámetro (o de otro largo) usados sin escalar el precio.** Brida WN 16" #300 con una de 10" (257,80; la relación 16/10 = 1,6 justo pasa la regla de "más de 1,6"); ciega 16" con la de 12"; caño 16" con un caño c/c 12" (133,36) aunque la lista Renard tiene el 16" s/c 406,4 × 9,52 (248,98, cód. 1212): el atributo "costura" pesó más que el diámetro; espárrago 1 1/8" × 186 con uno de 3/4" × 100 (5,00); espárrago 1 1/4" × 207 con uno de 7/8" (10,00); junta 16" con la de 12" #600 | `precotizacion.md` pos 2, 6, 8, 10, 11, 14 · `lista_renar_2025-12.csv` cód. 1212 | **−3.515** | −3.740 | Regla de diámetro más estricta en piezas grandes (el costo crece con Ø²: tope 1,25× desde 8"); si se usa un similar de otro Ø, escalar por (Ø/Ø)² y marcarlo `est`. En caños, el diámetro y el espesor mandan sobre la costura (s/c en lugar de c/c es aceptable, al revés no). En espárragos, el diámetro manda |
| 4 | **Schedule distinto aceptado sin ajuste.** Tee 12" XS cotizada con la tee 12" STD de Renard (962,15); Cintolo cotizó la tee 12" sch 80 a 2.425,08 (16-07-2026). Brida WN 12" XS con la sch 40. La tee de reducción 16"×12" STD × XS se tomó IGUAL con la de Renard STD × STD | `precotizacion.md` pos 3, 4, 5 · `TAVAL/69 .../Cot Cíntolo 33764.pdf` | **−1.486** (pos 3) | −2.399 | Schedule más liviano que el pedido = SIN PRECIO o recargo por espesor (XS/STD ≈ 1,5–2 en tees grandes). Comparar también el segundo schedule de las reducciones |
| 5 | **Las fuentes de los dos antecedentes más cercanos no están en el catálogo.** TAVAL/72 (skid gemelo 3×8" + 12", 07-2026) y TAVAL/78 (concentrador 10", 08-2026) tienen 0 filas en `catalogo_materiales.csv`: listas Taval (`Valvulas Taval.xlsx`, `Valvulas.xlsx`, lista × 0,52), Complemet 275397 (brida WN 12" XS #300 218,49; ciega 12" 257,65; SW 1 1/2" 14,88), MS Juntas 48.729 y 49.323 (espiral 12" #300 9,11 / 9,31). Por eso la globo 1/2" 800 queda SIN PRECIO (Taval: 35,10), la esférica 1/2" sale a 65,20 (Taval: 35,88), y las bridas 12" a lista Renard | `grep` de "TAVAL\\72" y "TAVAL\\78" en el catálogo = 0 · archivos citados | −305 (pos 7), −35 (pos 28) | **+3.588** (pos 5, 7, 9, 13, 25, 28) | Extraer `5.Proveedores 3ros` y `Valvulas*.xlsx` de TAVAL/69–78 (y revisar qué otras carpetas de 2026 quedaron afuera). Para Taval, guardar lista y factor (×0,52) por separado |
| 6 | **Horas de montaje de un skid de bomba de 4"** (Sacde/14, 1 u) para un concentrador de 16" en serie de 6: 368 h × 13 = 4.784. La PC0 pone 40 h propias (movimientos y PH) porque el armado lo hace Ledesma, y 3.000 de montaje y dimensional de tercero. El tipo "skid" junta desarenadores, skids de bomba y concentradores; el aviso de "sin antecedente del mismo tipo" no salta | `precotizacion.md` §3 · `conocimiento/costos/horas_por_equipo.csv` filas 26–27 | **+1.384** | +2.613 | `estimar_horas`: subtipo de skid (concentrador/colector, bomba, medición, desarenador); si no hay del mismo subtipo, avisar en rojo. Escalar por juntas y no solo por pulgadas (pocas juntas grandes = menos horas). Si la MO de piping es de tercero con armado, no sumar montaje propio completo |
| 7 | **El schedule XS no se lee y las bridas toman el schedule de su serie.** `precotizar.sch_de("XS")` devuelve "" porque parte el texto con `[xX/ ]` ("XS" → "", "S"); también falla "XXS". Las piezas de 12" XS se sueldan con el factor de sch 40 (1,083 en lugar de 1,334). Las bridas y tees de 16" (serie "300", sin schedule) toman el sch 40 por defecto (12,70 mm, factor 1,334) aunque el caño del colector es STD 9,52 mm (factor 1,0) | `precotizacion.md` §2 (pos 3 y 5: × 1,0830; pos 6: × 1,3340) · `herramientas/precotizar.py` `sch_de()` línea 59 | −989 (61,8 pulg-eq) | −768 | Partir solo por espacios, "/" y " x " con espacios. Las bridas WN, tees y reducciones toman el schedule del caño del mismo Ø de la tabla. Test con "XS", "XXS", "STD x XS" |
| 8 | **Pintura baja en skids con válvulas grandes:** piping = caños × 3 = 13,8 m², contra ~31 m² contando 6 válvulas de 12", 26 bridas y 6 tees. Con poco caño (4 m) y mucha válvula, la regla ×3 no alcanza | `precotizacion.md` §3 | −396 | −591 | m² por pieza con las tablas de peso de bridas, accesorios y válvulas (o factor por kg de válvulas y bridas), no proporcional al caño |
| 9 | **Caución no se calcula ni se pide** (la PC0: 459,20) | §4 de `precotizacion.md` | −459 | −450 | Aviso en "a completar" cuando el cliente es YPF o el pliego pide caución |
| 10 | **`--excluir` no alcanza a las tarifas ni a los servicios:** la fila EST (3 USD/kg, "tercero Ledesma, 2026-10") sale de `conocimiento/costos/tarifas.csv` fila 60, cuyo origen es **esta misma PC0**. `tarifa()` no aplica `excluido()`. En `catalogo_servicios` también están FAB-00565/566/567 de YPF/28. `buscar_antecedentes --excluir "YPF/28"` deja en 1° y 2° lugar las copias COT26-0330-001/002 del mismo proyecto | `cotizacion_auto.json` S05 · `tarifas.csv` fila 60 · `precotizar.py` `tarifa()` | 0 (mismo valor) | −850 | `tarifa()` y `servicio_catalogo()` filtran por `excluido()` también el campo fuente/origen. Las cotizaciones `cotizaciones/COT*` guardan el proyecto de origen y se excluyen con él |
| 11 | **Código del catálogo con productos mezclados en el historial:** NIP-01780 (niple 1/2" sch 80) tiene en su historial un niple **2"** de TAVAL/55 (USD 20). Al excluir YPF/28, la pos 16 queda IGUAL a USD 20 y la pos 17 (3/4") la toma como similar; el stock tiene el niple 1/2" sch 80 L 100 (ACI015FN1ICK100) a 4,76 | `precotizacion.md` pos 16–17 (⚠) · `stock_2024-11.csv` | +31 | +30 | Al volver al historial por una exclusión, verificar que la fila del historial tenga los mismos atributos que el código; si no, descartarla |
| 12 | Menores: (a) "P.T." del plano no se lee como paso (pos 25–26 "faltan: paso") y la 3/4" toma una de paso reducido; (b) globo 3/4" NPT cotizada con una 1" RF #600 (otro extremo); (c) medidas de espárragos en mm mal leídas ("1.25x207" → "25 x 20"; "1.125x186" → "1 1/8 x 18"), error ya visto en CTRL-M01; (d) en los sockolets la diferencia dice "diametro: 0.5" (pedido 12")" (mide el caño) mientras la regla de 1,6× mide la salida: la pos 21 queda SIN PRECIO y las 22–24 pasan; (e) compra extra con barra de 6 m para caños de 12" y 16" (Renard: 10,5–11,8 m); (f) fecha inválida "2026-02-31" en la fuente de la soldadura (`precotizar.py` línea 476 agrega "-31" a "2026-02"); (g) `comparar_historico --json` sigue titulando "precotización automática" | `precotizacion.md`, `cotizacion_auto.json` | ±100 | — | (a) leer "P.T." / "P.R." con puntos; (b) extremos distintos (NPT vs RF) = no similar; (c) largo en mm completo; (d) usar la salida también en el texto; (e) barra de 12 m desde 3"; (f) último día real del mes o "-15"; (g) título según el JSON |

**Peso:** la suma de los desvíos por rubro (APP contra REAL) es USD 27.516 por equipo. Los errores 1 y 2 (dos válvulas de 12" de otro tipo o tamaño) explican USD 11.892, el 43%; con el 3 y el 4 (similares sin escalar), el 61%. Otros USD 7.500 son diferencias de criterio que no son errores de la app: la MO tercerizada en Ledesma y la radiografía.

## ¿Siguen los errores de los controles anteriores?

| Error anterior (auditoría 28-10-2026) | Estado en este caso |
|---|---|
| 1 Horas de otro tipo de equipo | **Sigue** (error 6): "skid" es un tipo demasiado amplio |
| 2 Soldaduras sobrecontadas / tarifa | Conteo corregido (28,5 juntas contra 28 del skid gemelo TAVAL/72) y tarifa 16 ✓. **Nuevo:** XS no se lee (error 7) |
| 3 Pintura solo de caños | Mejoró (−17%), pero la regla ×3 queda corta con válvulas grandes (error 8) |
| 4 Radiografía con tarifa vieja | Corregido: DB NDT 08-2026 y servicios repartidos en la serie (2.753, igual que el agente). La PC0 puso 5.000 (nivel Antonelli: 4.514) |
| 5 Piezas mal identificadas | **Sigue y es el más caro** (errores 1, 2 y 12b) |
| 6 Filas del catálogo que mezclan productos | **Sigue** (VAL-03171 retención como esférica; NIP-01780 con un niple 2") |
| 7 Perfiles por metro / acero por kg | Corregido para kg (bastidor 1,90 USD/kg) |
| 8 Exclusión débil | **Sigue** en tarifas, servicios y antecedentes (error 10) |
| 9 Cotizaciones de proveedores fuera del catálogo | **Sigue** (error 5: TAVAL/72 y /78 enteros) |
| 10 Rubros que no calcula | Estructura ✓ ahora se calcula; caución y transporte no (error 9) |
| 11 Taval marcado por un similar | Bien: las 6 válvulas dicen Taval en el plano |
| 12 `comparar_historico` | Rubros y salida por archivo ✓; el título no |
| Menores (barra 6 m, mm de espárragos) | **Siguen** |

## Diferencias del agente que no son errores de la app

- **MO de piping:** el agente la calcula propia (474,67 pulg-eq × 16 = 7.594,72 + 176 h de montaje × 13). La PC0 la terceriza en Ledesma: 10.700 de piping + 3.000 de montaje y dimensional. El único presupuesto de Ledesma con el mismo alcance (TAVAL/78, presupuesto 200317, 17-08-2026: USD 28.000 c/u con skid y soportes para un concentrador de 4 entradas de 10") es bastante más caro. Hace falta un presupuesto de Ledesma para este plano.
- **Juntas:** 21 de 12" y 7 de 16". Salen de la tabla "Costuras" del skid gemelo TAVAL/72, que tiene la misma disposición con 8" y 12". No hay plano del 708.
- **Bridas 12":** se usó Complemet 275397 (06-07-2026). Es la mitad de la lista Renard y de la PC0 (Miyashiro 425,09). Las 16" son estimadas desde la lista Renard (no hay WN ni ciega 16" #300): hay que pedirlas a Compras.
- **Válvulas Taval 12":** no hay precio fuera del proyecto. Se estimaron desde las de 10" de TAVAL/78 (lista × 0,52) y las 12" #600 de Sacde/12. Retención 3.270 y esférica 5.640, contra 3.162 y 5.750 de la PC0.
- **Juntas espiraladas 12":** MS cotizó 9,31 (14-08-2026); la PC0 pone 45 en el skid y 9,11 en su propia lista de repuestos.
- **Radiografía:** DB NDT da 2.747. Con Antonelli serían 4.514. La PC0 puso 5.000 globales.
