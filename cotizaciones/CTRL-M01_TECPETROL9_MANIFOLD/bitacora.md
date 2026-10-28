# CTRL-M01: caso de control con el skid manifold PAD S-600 de Tecpetrol (PR 51456)

**No es una cotización para el cliente.** Es un caso de control del cotizador. Se tomó un equipo que ITT ya costeó y ganó (Nota de Pedido Abierta 4650000923, 06-03-2026) y se compararon tres números: el costo **REAL** de la planilla de ITT, la precotización automática (**APP**) y la recotización a mano del **AGENTE**. El detalle está en `errores_app.md`.

## Fuentes (28-10-2026)
- Planilla vigente pedida: `fuentes_originales/ofertas_texto/TECPETROL/9. CM SKID MANIFOLD PAD S-600/4.Armado de la Oferta Comercial/REV C/ESTRUCTURA DE COSTOS- LM de Manifold S600 CM - PC0-C REV.1 OS.xlsx.txt`, hoja PC0-C (13-01-2026): costo USD 44.462,22 por equipo. Materiales: 27.353,62 = 11.742,02 + 15.611,60 de válvulas Taval. MO y servicios: 17.108,60.
- **Decisión sobre el A6BM:** el despiece renglón por renglón solo existe en REV A a C, como un único modelo (sch 80) para los 35 skids. En REV D/E (26-01-2026) se separan A6BM (28 u, "sch 40") y A6CM (7 u, sch 80). El A6BM quedó sin despiece: materiales como un global de USD 9.202 ("variación por cambio de material, caños y bridas", ×1/1,296) y MO como un global de USD 12.000. Por eso el cómputo y el histórico son los de REV C, que en ese momento incluían a los 28 A6BM. El costo A6BM de REV E (USD 37.375,83) queda como referencia en `errores_app.md`.
- El "Plano de referencia.pdf" es una imagen sin texto. El RAR de Drive no se bajó: no hacía falta para la tabla de materiales, que está completa en la LM.

## Qué se hizo
1. Carpeta copiada de `_plantilla/` (sin su README). `pedido/lista_materiales_plano.csv`: las 17 posiciones de la hoja PC0-C, con la misma cantidad y unidad. Extremos deducidos del armado de un manifold bridado:
   - bridas WN RF/BW;
   - caños por metro;
   - tees BW;
   - sockolet BW/SW (sobre el caño, con el niple SW adentro);
   - niple PE/NPT, para no contar dos veces la soldadura del sockolet;
   - válvulas RF o NPT.

   `extremos_campo` = 0 en todos los renglones: las conexiones con el cliente son bridadas.
2. `historico.csv`: costo real por equipo, con los mismos totales que la planilla. Soldadura 322,52 pulg-eq × 16,5. Bastidor 384 kg × 4. RX 5.502,50. Pintura 523,86. Ingeniería, calidad y montaje 3.711,64 (incluye PH). Pólizas 111,02. Transporte 402.
3. `cotizacion.json`: N = 28 (A6BM), `rx_pct` = 100 (condiciones de diseño de la serie 600), `ph_horas` = 27 (PH de 3 días de 9 h, de la hoja de montaje), `equipo.tipo` = manifold, `diametro_pulg` = 8. Se cargó antes de correr.
4. APP: `python herramientas/precotizar.py cotizaciones/CTRL-M01_TECPETROL9_MANIFOLD --excluir "TECPETROL/9" --excluir "TECHINT/12"`. La carpeta TECHINT/12 tiene una copia de esta misma planilla (OFERTA REV C) y sus precios estaban en el catálogo: bridas, drip ring, válvulas, niple y sockolet. Después, `python herramientas/comparar_historico.py cotizaciones/CTRL-M01_TECPETROL9_MANIFOLD` → `comparacion_historico.md`.
5. AGENTE: `buscar_antecedentes.py --familia M` (el más parecido después del propio es TECPETROL/8, manifold #600 de 2025, con las horas de ingeniería y calidad por mail). Después, `buscar_material.py` y `buscar_servicio.py` renglón por renglón, salteando los precios de TECPETROL/9 y TECHINT/12, y abriendo las fuentes: `precios_componentes.csv` (bridas), planilla TAVAL/43 (Taval −35% −20%), TAVAL/40 (pulgada a USD 16), TAVAL/41 (detalle de montaje), Suan (flete a Neuquén) y mails de TECPETROL/8. Resultado en `cotizacion_agente.json`, comparado con `comparar_historico.py --json cotizacion_agente.json` → `comparacion_agente.md`.
6. No se corrió `armar_cotizacion.py` ni `verificar_todo.py`. No se modificó nada fuera de esta carpeta: `git status` solo muestra la carpeta nueva.

## Resultado (por equipo, sin IVA)

| | Materiales | MO y servicios | Total | contra REAL |
|---|---:|---:|---:|---:|
| REAL (REV C) | 27.353,62 | 17.108,60 | **44.462,22** | — |
| APP | 17.950,78 | 25.628,44 | **43.579,22** | −2% |
| AGENTE | 23.411,66 | 17.250,97 | **40.662,64** | −9% |

La app da cerca del total por compensación: materiales −34% y MO +50%. Los errores principales son:
- montaje copiado de una trampa: +6.466;
- esférica 4" de paso reducido usada como si fuera de paso total: −5.441;
- soldadura con juntas de más y tarifa de 2024: +3.776;
- bastidor, pólizas y flete que no se calculan: −2.049;
- tres renglones sin precio: −1.992;
- brida 4" al precio atípico más bajo: −1.507.

## Criterios del agente (estimados, a confirmar en una cotización real)
- Drip ring 4" #600: USD 180 (chapa + mecanizado), sin antecedente.
- Esférica 4" #600 PT: PR × 1,30 = USD 1.256.
- Calidad: 20 h por equipo.
- Montaje: 230 h, escalado de TAVAL/41.
- Pólizas: USD 120.
- Espárragos: se cotizaron a 7/8 x 145 mm. El largo de 100 mm de la LM no alcanza para una brida 4" #600 RF; la hoja de MO de la misma planilla usa 7/8 x 5 3/4".
