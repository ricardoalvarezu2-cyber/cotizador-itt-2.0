# Horas hombre por equipo (ITT): notas de extraccion

Resultado: `horas_por_equipo.csv` (37 filas, 18 carpetas de proyecto; 34 equipos vigentes + 3 filas marcadas como superadas/alternativas). Todas las fuentes salen de `fuentes_originales/ofertas_texto/`. Columnas: las 24 pedidas + `pulgadas_tipo` al final.

## Criterios
- Revision: se usa la mas nueva; si hay varias iguales se anota. Tecpetrol 9 Manifold: REV A a E tienen las mismas horas (se usa REV E, `REV.3 OS`). Tecpetrol 13 Trampas: se usa `8.Orden de Compra/...REV 1` (las horas son iguales en `4.Armado` y en `REV 1-0`). Taval 70: REV 1 oferta mejorada (REV 0 tiene las mismas horas 6/6/126). Sacde 13: rev.3 (rev.2 igual). Los Toldos: REV B vigente, REV A como superada (fila marcada).
- **Los Toldos REV C no se extrajo**: `OFERTA REV C/ESTRUCTURA DE COSTOS- LM de Manifold S600 CM - PC0-C REV.1 OS.xlsx` es una copia de la planilla del manifold de Tecpetrol 9 (mismas horas 1.14/24/256.5), no del desarenador.
- Filas marcadas como NO vigentes: Los Toldos REV A, Tecpetrol 10 hoja `Soldadura + HH ` (la vigente es `Soldadura + HH_`, la que cuadra con el RESUMEN), Tanque glicol Opcion 2 (alternativa de menor alcance).
- Se agregaron 3 fuentes que no salian del grep "horas de ingenier" con las celdas tipicas pero tienen horas: Taval 43 (puentes de produccion YPF; horas derivadas de USD/tarifa), AESA 29 (HH de ingenieria por documento, 2023) y Endress+Hauser 17 (lista de cantidades ISOIL: 100 h ing, 150 h calidad). Los .msg/.docx quedaron afuera, como se pidio.
- `base_horas`: en todas las planillas con cantidad > 1 el costo unitario de MO incluye las horas **por unidad** (verificado que MO unitaria = MO planilla + total HH en Tecpetrol 10, Inarteco, Sacde 12, Los Toldos). Lo que varia es como se prorratea: Inarteco "Se divide en 2 unidades" (9 h totales -> 4,5 por unidad), Taval 70 "Se prorratean las horas en la cantidad total de 24 unidades" (6 h = parte por unidad), Los Toldos "REDUCCION DE 2 EQUIPOS" (calidad 180->90; PH, presentacion de piping y despacho x0,8). Manifold Tecpetrol 9: ingenieria 1,142857 = 40/35 (inferido; no hay rotulo).
- Valor hora: ingenieria y calidad 15 USD; montaje 13 USD (16 USD en filtros coalescedores y tanque de glicol); AESA 7500 ARS/h (21,43 USD a TC 350 del propio documento).
- `pulgadas_soldadura`: por defecto es el **equivalente** = costo de soldadura de la hoja "Mano de Obra de ITT" / precio por pulgada (16, 16,2, 16,5 o 19 USD segun el archivo; sube con el tiempo y con la serie: 16 en #600, 19 en #900 en Sacde 12). En Tecpetrol 13 y Taval 70 solo hay tabla de soldaduras sin hoja MO: ahi es DN x cantidad de soldaduras (`pulgadas_tipo` lo aclara). Sacde 15/SK-xxxx y la columna `dudoso` traen tambien el "Total Pulgadas" que escribe la planilla (DN x cantidad: 554, 558, 251).
- Resto de plantilla: "Total de Pulgadas | 53,97" (y 49,827 en las planillas mas nuevas) es la suma de la equivalencia de la estructura (3 x 17,99); NO es el tamano del equipo. No se uso en ninguna fila. Tambien son plantilla las filas "Estructura HEB 300 / UPN 200 / Se usa una equivalencia" y los rotulos heredados (hoja MO de Sacde 12 rotulada "COALESCENTE"; Sacde 37 "SEPARADOR BIFASICO"; hoja HH de skids E+H con rotulos "TRAMPA").
- Peso: casi nunca esta. Donde figura es solo de la estructura (bastidor/percha) o una estimacion de cabecera (filtros coalescedores); se anoto en `dudoso`.
- `posiciones`: filas de la primera tabla de la lista de materiales (aproximado). `costo_materiales_usd`: la linea "Materiales" del RESUMEN (sin valvulas Taval ni instrumentos salvo nota); para trampas Tecpetrol 13 es "Materiales, MO y SVC" (incluye MO de terceros).

## Lo que no estaba claro
1. Montaje: en varias planillas hay actividades con dias x hombres pero SIN total en la celda de horas; esas no suman al "Total HH montaje". Siempre faltan **soldadura** (se cobra por pulgada) y **granallado y pintura** (se cobra por m2). En Sacde 12/37 falta ademas "presentacion soldadura conexionado" (270 h) en las planillas de 2 filtros (1719 vs 1989 h). En E+H Ø12/Ø3 solo suman 5 actividades de 12 (130,5 / 121,5 h).
2. Taval 41 (manifold pozo de agua): "Hora de montaje 0" aunque hay dias x hombres (calculable ~261 h). No usar el 0 como estimador.
3. Taval 40, FM8: montaje 49,5 = 45 + "10% mas por tamano" (unico caso con ese comentario; aparece en una celda suelta "10% mas por tamaño").
4. Sacde 15 tanque glicol: montaje 554,4 = 504 x 1,10 (inferido); la planilla solo rotula el total 504.
5. Sacde 14 (TK conico): la celda "Total HH montaje" aparece con 571,5 y 535,5 cruzados; se tomo 535,5 (= celda "Hora de montaje"). Ingenieria 240 / 200 h; hay textos "Ingenieria Bastidor 80 h" que no estan cargados.
6. Tecpetrol 10: ingenieria 251,5 h (mismo valor para lanzadora y receptora, trampas de 8x6); hay una nota "cada trampa empleara unas 630 Hs. Hombre si la PH es conjunta".
7. Sacde 15 SKIDs: un unico bloque de horas "Skid 2104 y 2105" (27/90/216) cargado a cada skid (verificado por la diferencia de MO entre ambos). El "montaje" es solo PH.
8. Tecpetrol 13: el nombre de la hoja "Rec 20x16" dice "lanzadora" en NOMBRE (error de la planilla). Las 6 trampas usan 100 h ing + 120 h cal fijas ("valores tomados de cotizacion anterior para Tecpetrol (ganada)").
9. Serie de las trampas 20x16: Pie de venta dice Serie-600 y las bridas de la hoja dicen 900.
10. Taval 43: la planilla dice "Hs de Ingenieria y Calidad | 150 | 150" y "Hs de montaje | 351 | 390": son USD (150 = 10 h x 15; 351/13 = 27 h; 390/13 = 30 h). Horas derivadas.

## Patrones
- **Ingenieria**: casi nunca depende del tamano. Valores repetidos: 100 h (trampas Tecpetrol 13; E+H ISOIL), 250 h (filtros/tanque grandes Sacde y Taval 37), 30 h (skids de medicion E+H), 9 h (Inarteco, manifold pozo; ~equipos chicos), 6 h (puente serie de 24), 50 h (tanque de choque). Los equipos de serie dividen un monto fijo por unidades (9 h/2, 40 h/35, 6 h x 24). Casos distintos: 403,5 y 356,9 h en AESA (suma de documentos: ~17 documentos x HH STD con Rev A 70%, B 20%, 0 10%) y 150 h skid desarenador. Hay ademas ingenieria externa (Ing. GORA 4985 USD) en los coalescedores.
- **Calidad**: tambien un monto fijo por tipo: 250 h (grandes), 120 h (trampas Tecpetrol 13, booster), 90 h (skids Sacde, tanque de choque, TK conico), 45 h (skids de medicion), 24 h (manifold 35 u), 9-18 h (chicos), 1 h (puentes en serie), 75 h (trampas 8x6 Tecpetrol 10). Suele ser igual o parecida a ingenieria.
- **Montaje**: es lo unico que se calcula de abajo hacia arriba: dias x hombres x 9 h por actividad (corte y presentacion, armado, PH, armado final, movimientos, acondicionamiento de despacho; en equipos grandes: armado de tacho, internos, pollera). No esta atado a las pulgadas: relacion montaje/pulgada equivalente entre 0,3 y 3,7 h/pulg (mediana ~1,2), asi que para estimar conviene usar el detalle de actividades del equipo mas parecido, no una regla por pulgada. Referencias por tipo en el resumen.
- Reduccion por serie: PH, presentacion de piping y acondicionamiento x0,8 si son 2 equipos (Los Toldos); no se vio otro caso.
- Costo de MO tercerizada (soldadura de Ledesma/Quesada): el equipo queda con menos horas propias de soldadura (Tecpetrol 13, Sacde 13, TK choque alternativa 10700 USD).
- Tarifas: 15 USD ing/cal, 13 USD montaje, 16 USD en las planillas de coalescedores y glicol (2025/2026).

## Rangos (horas por unidad)
| Tipo | Ing | Cal | Montaje | Fuente principal |
|---|---|---|---|---|
| Trampa (20x16 a 12x8) | 100 | 120 | 90-130 | Tecpetrol 13 (estimado en bloque) |
| Trampa 8x6 con detalle | 251,5 | 75 | 756 | Tecpetrol 10 |
| Skid de medicion (Ø3-12) | 30 | 45 | 121-131 | E+H 26/27 |
| Skid grande (valvulas/bombas, UFLO, desarenador) | 27-280 | 70-120 | 135-535 (508 desarenador) | Sacde 13/14/15, Los Toldos |
| Filtro chico (Inarteco) | 4,5-9 | 4,5-9 | 45-49,5 | Taval 40 |
| Filtro coalescedor 36in | 250 | 250 | 1719-1989 | Sacde 12, Taval 37 |
| Manifold de 35 u | 1,14 | 24 | 256,5 | Tecpetrol 9 |
| Manifold chico | 9 | 18 | 0 cargado (261 calculable) | Taval 41 |
| Tanque (glicol, choque 36in) | 50-250 | 90-250 | 234-554 | Sacde 15/20 |
| Puente 2in-4in | 6-9 | 1-6 | 27-126 | Taval 43/70 |
| Puente Ø12in / Filtro FS-214 (AESA) | 357 / 404 | sin dato | sin dato | AESA 29 |
