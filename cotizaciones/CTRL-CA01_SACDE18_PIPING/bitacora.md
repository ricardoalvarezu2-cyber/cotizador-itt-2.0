# CTRL-CA01: caso de control con el prefabricado de piping de Sacde para TGS (PRES 147)

**No es una cotización para el cliente.** Es un caso de control del cotizador, para medir la app en piping prefabricado: caño por metro, muchas juntas, soldadura por pulgada, RX y pintura. Se compararon tres números: el costo **REAL** de la planilla de ITT, la precotización automática (**APP**) y la recotización a mano del **AGENTE**. El detalle está en `errores_app.md`.

## Fuentes (28-10-2026)
- Planilla de costo: `fuentes_originales/ofertas_texto/Sacde/18- PREFABRICADO PIPING - Plantas Compresoras TGS/7.Propuesta Comercial (envío al Cliente)/Sacde - Cotización piping x pulgada+END y mtr2 Rev4 Direccion.xlsx.txt`. La carpeta "4.Armado de la Oferta Comercial" solo tiene la oferta técnica 147A, sin precios. La planilla está en la carpeta 7.
- Oferta PRES 147 rev A del 20-04-2026: USD 2.209.596,57 sin IVA (con un 7% previsto para negociar), acuerdo marco, 5 plantas. La pintura se vende aparte a USD 40/m².
- Cómo costea la planilla: pulgadas × (soldadura 10,50 USD/pulg + END por pulgada según diámetro) × 1,05 de rechazo. Después aplica × 1,13 de rentabilidad y × 1,07 de negociación. Hoja Resumen: "Costo" 660.706,34 en Chacharramendi, que es el precio a 1,13. "TOTAL de VENTA VERIFICADO" 1.827.050 es el costo total.
- END: Antonelli, placa grande 20, chica 15, servicio 490 cada 40 placas. 36": 9 placas por junta (8,0625 USD/pulg). 12": 4 placas (10,75 USD/pulg).
- La misma planilla trae una variante con factor de espesor (36" sch 40 = 72 pulg × 16 USD) que no se usó ("TODO FACTOR 1 en soldadura").

## Decisiones
1. **Unidad ("equipo")**: las 2.700 pulgadas de 36" (3 líneas) y las 228 de 12" (1 línea) de la PC Chacharramendi, renglones que la planilla costea por separado. N = 1. El alcance completo (5 plantas, 71.813 pulgadas) no entra en el modelo de la app, que piensa en equipos.
2. **Tabla del plano**: la MTO de TGS (TE-B10-202.503-LM-PI-1001 Rev 1, hoja PIP 3) para 36" y 12", con "CANT. FINAL MONTAJE", que es la MTO ajustada a las pulgadas del layout. Los materiales los provee el cliente: se anotó en `modelo_fabricante`. `extremos_campo` = 0, porque la planilla cobra todas las pulgadas.
3. **`historico.csv`**: materiales en 0 (provistos por el cliente), soldadura 2.928 pulg × 10,50 × 1,05 = 32.281,20 y RX 25.430,74. Total 57.711,94, que coincide con la planilla: 2.700 × 19,490625 + 228 × 22,3125. La pintura no está en el costo real, porque se vende aparte.
4. **`cotizacion.json`**: `rx_pct` = 100 (oferta: END 100% RX y tintas), `ph_horas` = 18 (PH solo de spools bridados, 2 jornadas, criterio), `equipo.tipo` = manifold (el más cercano; no hay tipo "prefabricado"), `diametro_pulg` = 36, `fecha_referencia` = 2026-04-20.

## Qué se hizo
1. Carpeta copiada de `_plantilla/` (sin su README).
2. APP: `python herramientas/precotizar.py cotizaciones/CTRL-CA01_SACDE18_PIPING --excluir "Sacde/18"`. Después, `python herramientas/comparar_historico.py cotizaciones/CTRL-CA01_SACDE18_PIPING`, que **se cae** (`TypeError` en la línea 82: `pct()` devuelve None con material real 0). Se corrió con un envoltorio en el scratchpad que reemplaza `pct()` en memoria, sin tocar la herramienta → `comparacion_historico.md` y `comparacion_cotizacion_agente.md`.
3. AGENTE:
   - `buscar_antecedentes.py --familia CA`: el único prefabricado por pulgada parecido es PAN AMERICAN ENERGY/62 (contrato marco de prefabricado, 2025). De ahí sale el presupuesto Ledesma N° 20036 del 30-07-2025: prefabricado de cañerías sch 40 a 13 USD/pulg más IVA.
   - `buscar_servicio.py` para soldadura, placas y pintura, salteando los renglones de Sacde/18 (el buscador no tiene `--excluir`).
   - Fuentes abiertas: Ledesma 20036, Antonelli 11-2025 (tarifas.csv), DB NDT en la hoja ENOD de Pampa 7, pintura de Sacde/14 (20,03 + 20,41 USD/m²) y Sacde/20 (40 USD/m²).
   - El JSON se armó con un script en el scratchpad → `cotizacion_agente.json`.
4. No se corrió `armar_cotizacion.py` ni `verificar_todo.py`. `precotizar` no modificó archivos compartidos: `git status` muestra solo esta carpeta.

## Resultado (por conjunto, USD sin IVA)

| | Sin pintura | Pintura (aparte) | Con pintura | Sin pintura, contra REAL |
|---|---:|---:|---:|---:|
| REAL | **57.711,94** | se vende a 40/m² | — | — |
| APP | 318.193,07 (MO y servicios 31.785,59 + materiales 286.407,48) | 246.940,85 | 565.133,92 | +451% (MO y servicios −45%) |
| AGENTE | **57.605,10** | 67.530,00 | 125.135,10 | −0,2% |

Errores principales de la app:
- materiales del cliente cotizados: +286.407;
- pintura ×3 sobre caño recto: +246.941;
- juntas entre barras sin contar: −72.462;
- factor de espesor y tarifa que no son de prefabricado: +47.144;
- RX con DB NDT: −13.962;
- horas de un skid: +13.354.

## Criterios del agente (estimados)
- Juntas: 1 por barra de 12 m + 2 por codo + 1 por brida. Da 61 de 36" y 16 de 12", 2.388 pulg diametrales.
- Soldadura: 13 USD/pulg (Ledesma) + 1 de consumibles, × 1,05 de reparaciones. Riesgo: el 36" sch 40 tiene 19 mm de espesor; con factor de espesor serían unos USD 24.000 más.
- RX: Antonelli, 8 placas grandes por junta de 36" y 6 chicas por junta de 12", × 1,05. DB NDT queda como alternativa: −58%.
- Calidad: 30 h. Movimientos y carga: 180 h. PH: 18 h.
- Pintura: 1.688 m² × 40 USD/m², cotizada aparte.
- El agente leyó la planilla real antes de recotizar (había que definir la unidad): sus tarifas pueden estar sesgadas.
