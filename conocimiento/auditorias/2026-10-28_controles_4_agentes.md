# Recotización de control con 4 agentes (28-10-2026)

Cuatro agentes (Opus) recotizaron cada uno un proyecto con planilla de costo real, sin usar precios del propio proyecto, y compararon REAL (planilla de ITT), APP (precotización automática, sin completar) y AGENTE (recotización a mano con el procedimiento). Detalle y evidencia en `cotizaciones/CTRL-*/errores_app.md`.

| Caso | Equipo | REAL | APP | AGENTE |
|---|---|---|---|---|
| CTRL-T01 | Tanque de choque Ø36" (Sacde 20) | 22.624,65 | 30.547,60 (+35%) | 20.954,05 (−7%) |
| CTRL-C01 | Skid colector PAD 6 pozos (Pampa 7) | 66.490,02 | 66.180,03 (−0,5%; +11% sin la copia del propio proyecto) | 69.702,46 (+5%) |
| CTRL-P01 | Puente de inyección y regulación 2" #600 (Taval 70) | 68.559,60 | 39.583,40 (−42%) | 76.141,56 (+11%; −0,6% sin canalizaciones) |
| CTRL-M01 | Skid manifold S600 A6BM (Tecpetrol 9, REV C) | 44.462,22 | 43.579,22 (−2%) | 40.662,64 (−9%) |

Costo por equipo, USD sin IVA. Los totales de la APP que "dan bien" son compensación de errores: materiales bajos y MO alta.

## Errores que se repiten (prioridad por impacto)

| # | Error | Casos | Impacto típico por equipo | Dónde se corrige |
|---|---|---|---|---|
| 1 | **Horas de ingeniería/calidad/montaje de otro tipo de equipo** (trampa para un manifold, TK de glicol para un tanque de choque, puente de serie de 442 para un skid de medición); la penalidad por otro tipo es chica y no se ve el alcance (montaje tercerizado o con pintura incluida) | T01, C01, P01, M01 | +3.000 a +10.000 | `estimar_horas.py`: penalidad fuerte por otro tipo, escala por materiales, avisar "sin antecedente del mismo tipo"; no sumar montaje propio si la MO es de terceros |
| 2 | **Soldaduras sobrecontadas** con caño por metro: brida–accesorio directas cuentan doble; el ×2 se aplica a virolas y casquetes; espesor "3/8"" no se lee; tarifa 19,73 de oct-2024 contra 16–16,5 de las planillas 2026 | T01, P01, M01 | +3.000 a +5.000 | `precotizar.soldaduras` y `tarifas.csv` |
| 3 | **Pintura solo de caños y niples** (faltan bridas, accesorios, válvulas, bastidor, envolvente) | todos | −400 a −4.100 | `precotizar`: m² por kg de bridas/accesorios/válvulas/estructura (tablas de peso) o por regla de antecedentes |
| 4 | **Radiografía con tarifa Antonelli 11-2025** cuando hay DB NDT 14-08-2026 (6,50 placa, 408 servicio); servicios por equipo en series; sin LP para SW y olets | C01, P01, M01, T01 | +700 a +4.700 | `precotizar` RX: tarifa más reciente del catálogo de servicios; servicios por serie; LP |
| 5 | **Piezas mal identificadas**: válvula de control con actuador como globo manual; V-Cone como electromagnético; esférica PT con una PR; #3000 como #300; WNRF/SA-105/SA-36/A-36/UPN no se leen; espesor de casquete no se compara | P01, M01, T01 | hasta −17.000 | `catalogo_materiales` (atributos: paso, actuador, principio de medición, espesor, prefijo SA-, A-36) y `buscar_material` |
| 6 | **Filas del catálogo que mezclan productos** (computador de caudal ABB a 864 en vez de 7.346; Doma a 1.380 en vez de 8.206) — error 28 repetido | P01 | −8.400 | `catalogo_materiales`: no mezclar precios de renglones distintos de una cotización |
| 7 | **Virolas y chapa rolada sin precio**; perfiles en metros (UPN) no van por kg | T01, M01 | −2.000 a −4.400 | `precotizar.acero_kg`: virola = kg × acero + rolado; perfiles en m → kg |
| 8 | **Exclusión débil**: copias de planillas entre carpetas (Pampa 7 dentro de Pampa 5; Tecpetrol 9 dentro de Techint 12); `--excluir` borra la pieza entera aunque tenga otros precios | C01, M01 | oculta hasta 7.700 | catálogo: identificar el proyecto por el documento; excluir solo ese precio del historial |
| 9 | **Cotizaciones de proveedores que no entraron al catálogo** (Valvtronic, Valbol, MS Juntas mal leída) | C01 | ±4.500 | extracción de proveedores_2026 |
| 10 | **Rubros que no calcula ni pide**: estructura/bastidor, caución, transporte, MO de terceros | todos | −250 a −2.000 | `precotizar` sección 4 |
| 11 | Válvula marcada Taval por un similar descartado | P01 | −6.000 en la venta | `precotizar`: marcar Taval solo con precio Taval elegido o modelo del plano |
| 12 | Herramientas de control: `comparar_historico` pone el montaje bajo "prueba hidráulica" y pisa su salida con `--json`; falta `--excluir` en `buscar_material/servicio/antecedentes` | todos | — | `comparar_historico.py`, buscadores |

Menores: barra fija de 6 m (los caños de 3"+ vienen en 12 m) y compra extra para 0,25 m; precio más bajo del historial sin alerta (brida WN 4" Provemet); medidas en mm de espárragos; posiciones duplicadas sin aviso; precio verbal tomado como antecedente; catálogo con casquete duplicado; dato mal atribuido en `tarifas.csv` (Ledesma 16,03/pulg).
