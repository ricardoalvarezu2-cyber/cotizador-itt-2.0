# Estructura de costo de las planillas 2021–2024 (29-10-2026)

`estructura_costo_historica.csv`: 103 equipos de 59 carpetas de 2021–2024 con planilla de costo (95 con MO cargada).
Una fila por equipo, montos **por unidad** en la moneda de la planilla, con el reparto materiales / MO propia /
terceros / otros, factor y precio. Extraído con `herramientas/horas_planillas_instrucciones.md` (12 agentes, revisado:
las 103 filas cierran con el costo total de la planilla y 3 muestras coinciden con el original).

## Lo que se buscaba y no está
- **Horas**: ninguna planilla de 2021–2024 trae horas de ingeniería, calidad o montaje. La MO es un monto global en USD
  por equipo ("MANO DE OBRA 5.100"), sin tarifa ni detalle. Por eso no se sumó nada a `horas_por_equipo.csv` (las 2
  filas que salieron no sirven: 792 h dudosas de un borrador de calentador y pulgadas sin horas de un manifold).
- **Pulgadas de soldadura**: las tablas "Soldaduras" de esas planillas vienen sin cantidades.

## Cómo usarla
- Los montos son del cepo: **solo como proporción y tamaño relativo**, nunca como costo.
- Aun las proporciones están corridas: los materiales importados y la MO local se pasaban a dólares con tipos de cambio
  distintos. En 2021–2022 la MO pesa 8–23% del costo; en las fichas 2025–2026, bastante más (materiales 51–68%).
- Supuestos de los agentes (anotados en `nota` de cada fila): la línea "MANO DE OBRA" va como MO propia (las planillas no
  dicen si es tercerizada); RX, rolado, tratamiento térmico y casquetes como terceros; pintura, aislación y transporte
  según la planilla en terceros u otros.

## Medianas por tipo (equipos con MO cargada)
| Tipo | Equipos | Materiales | MO propia | Terceros | Otros | Factor |
|---|---|---|---|---|---|---|
| Calentador | 7 | 90% | 8% | 0% | 2% | 1,40 |
| Filtro | 9 | 78% | 10% | 7% | 2% | 1,65 |
| Manifold | 10 | 84% | 14% | 2% | 1% | 1,50 |
| Prefabricado | 13 | 81% | 11% | 3% | 0% | 1,50 |
| Puente | 9 | 85% | 11% | 4% | 0% | 1,50 |
| Separador | 6 | 77% | 9% | 10% | 0% | 1,80 |
| Skid | 28 | 56% | 20% | 20% | 0% | 1,80 |
| Tanque | 9 | 70% | 14% | 13% | 0% | 1,50 |
| Trampa | 4 | 66% | 23% | 9% | 1% | 1,80 |

Factores usados entonces: 1,4 a 1,8 (AESA 1,8; PAE 1,4–1,6; Pluspetrol 1,5).
