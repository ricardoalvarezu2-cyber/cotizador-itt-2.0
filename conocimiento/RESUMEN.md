# Resumen para cotizar — ITT S.A.

Los parámetros clave en una página. El detalle y la fuente de cada número están en los archivos enlazados. Actualizado al 27/10/2026.

## Precio de venta

| Concepto | Valor habitual | Fuente |
|---|---|---|
| Factor sobre materiales, MO y servicios | **1,35** (MO a veces 1,40; instrumentos 1,35–1,50) | Planillas de costo 2026 |
| Factor sobre válvulas Taval, caución y transporte | **1,00** (a costo) | Planillas de costo |
| Factores en planillas de costo 2025 | 1,25 – 1,41 (6 casos con dato); en algunas, materiales a 1,2 y MO a 1,3 | `comercial/cotizaciones_2025.csv` |
| Factor efectivo de las ofertas **ganadas** en 2026 | **1,28 – 1,35** (mediana de todas las ofertas: 1,34) | `comercial/cotizaciones_2026.csv` |
| Ofertas grandes y competitivas | 1,15 – 1,25 | Ídem |
| Bonificación al negociar | 1,5 – 7% | `aprendizajes_2026.md` |
| IVA | 21%, aparte | — |
| Moneda y entrega | USD, facturado en pesos al TC BNA · EXW planta Quilmes Oeste | Ofertas 2026 |

El factor lo define la dirección en cada cotización. La herramienta propone 1,35 y muestra escenarios.

## Costos de referencia

| Rubro | Valor | Tipo |
|---|---|---|
| Soldadura piping | **19,7 USD/pulg-eq** (costo propio 2024) · 16–22 USD/pulg (taller Ledesma 2026) | `costos/tarifas.csv` |
| Estructura | 5,1 USD/kg (costo propio) · 2,5–2,8 USD/kg (Ledesma 2026) | Ídem |
| Fabricación de separador + skid por tercero | USD 13.000 / unidad (Ledesma 2026) | Ídem |
| Radiografía (Antonelli nov-2025) | 490 USD/servicio cada 40 placas · placa chica 15 USD · grande 20 USD | Ídem |
| Granallado + pintura (tercero) | ~35 USD/m² + 19 USD/m² de suministro | Ídem |
| Chapa A36 | ~1,16 USD/kg (+10% de recortes) | Ídem |
| Precios de materiales y componentes | 2.680 precios con fecha y fuente | `precios/indice_precios.csv` |

Cómo se calcula cada rubro (pulgadas equivalentes, placas, superficie, kg): [`reglas_de_calculo.md`](reglas_de_calculo.md).

## Plazo

| Familia | Plazo ofrecido en 2026 (mediana) | Plazo real histórico |
|---|---|---|
| Filtros | ~70 días | — |
| Manifolds y colectores | ~90 días | ~60 días (se cumplen) |
| Puentes de medición | ~110 días | atrasos de 100+ días en 2025 |
| Skids | ~110 días | ~160 días |
| Calentadores | ~120 días | ~430 días en 2022–23 |
| Separadores, trampas y tanques | 140–150 días | ~370 días en 2022–23 |

**Lo que define el plazo es el material, no el taller.** Con el material en planta, un equipo mediano lleva 6–10 semanas de taller. Los ítems críticos son las bridas API 6A (75–90 días), las tapas de cierre rápido (90–110 días), las válvulas de control y de seguridad (2–3+ meses), la instrumentación (12–14 semanas) y todo lo importado. Ver [`plazos.md`](plazos.md).

## Condiciones que se repiten

- **Pago:** contra entrega a 30 días F.R.F. en ofertas chicas. **Por encima de ~USD 100.000:** hitos 30% anticipo (con caución del 100% del anticipo y fiel cumplimiento del 10%) / 20% compra de materiales principales / 20% prueba hidráulica / 30% liberación para despacho. A veces, fondo de reparo del 10%.
- **Validez:** 30 días (cuidado: las ofertas de proveedores vencen en 10–30 días).
- **Exclusiones habituales:** multas por mora en material importado o con licencias, montaje en sitio, transporte (se cotiza aparte a costo) y repuestos (aparte, con factor ~1,5).
- **Declarar siempre los desvíos** a la especificación del cliente.

## Antes de enviar una oferta, revisar

**Seguir [`procedimiento_cotizacion.md`](procedimiento_cotizacion.md) completo (P1–P10), con su lista de control, y correr `herramientas/verificar_computo.py`.** Los errores ya cometidos están en [`errores_y_lecciones.md`](errores_y_lecciones.md). Además:


1. Que el plazo ofrecido cubra el ítem de material más largo.
2. Que el factor efectivo, después de bonificaciones, no quede por debajo de ~1,28 sin decisión de la dirección.
3. Comparar el precio con cotizaciones parecidas de `comercial/cotizaciones_2026.csv` y `comercial/ventas_2022-2023.csv`.
4. Repasar los aprendizajes de la familia en [`aprendizajes_2026.md`](aprendizajes_2026.md).
5. Registrar la cotización y, más adelante, **su resultado** (ganada o perdida y por qué). Es el dato que más falta hoy.
