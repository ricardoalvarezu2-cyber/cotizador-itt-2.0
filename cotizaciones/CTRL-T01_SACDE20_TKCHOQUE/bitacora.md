# CTRL-T01: caso de control del tanque de choque Ø36" x 5000 mm #150 (Sacde para TGS, PRES 130)

**No es una cotización para el cliente.** Es un caso de control del cotizador. Se toma un recipiente que ITT ya costeó
(planilla `Sacde/20 - SE-3121-ASTORD-014 - TK DE CHOQUE/4.Armado de la Oferta Comercial/LM - SACDE - TK Choque.xlsx`, 03-03-2026)
y se compara contra la precotización automática (APP) y contra una recotización a mano del agente (AGENTE), que no usa precios
del propio proyecto. Es el primer control de un recipiente: chapa por kg, virolas roladas y casquetes.

## Cómo se arma (28-10-2026)
1. `pedido/lista_materiales_plano.csv`: los 20 renglones de la hoja "LM TK Choque". No hay plano con tabla en el repositorio:
   el típico TGS I-GIO-TIP-TM-G-013 no está extraído. Las piezas de chapa van en kg, como las costea la planilla. Las virolas
   y los casquetes van por unidad, y la serie "esp. 3/8"" se dejó como dice el documento. Extremos supuestos en `errores_app.md`.
2. `historico.csv`: costo real por tanque. Materiales 6.104,65; Quesada 10.700 (soldadura, armado y PH); Rx + LP 2.720;
   pintura 25 m² × 40 = 1.000; ingeniería 50 h y calidad 90 h a USD 15 = 2.100. **Total 22.624,65**, igual que el Resumen
   de la planilla.
3. `cotizacion.json`: N = 1, `rx_pct` = 100, `ph_horas` = 36, `equipo.tipo` = tanque, `diametro_pulg` = 36, fecha 03-03-2026.
4. APP: `python herramientas/precotizar.py cotizaciones/CTRL-T01_SACDE20_TKCHOQUE --excluir "Sacde/20"` y luego
   `python herramientas/comparar_historico.py cotizaciones/CTRL-T01_SACDE20_TKCHOQUE` → `comparacion_historico.md`.
   El `--excluir` funcionó en materiales, servicios y horas: ningún precio salió del propio proyecto.
5. AGENTE: `cotizacion_agente.json`, armado por el agente con el criterio que se detalla abajo, y luego
   `comparar_historico.py … --json cotizacion_agente.json` → `comparacion_agente.md`.

## Criterio del AGENTE (fuentes abiertas en el original)
- Virolas: chapa A-516 Gr70 3/8" de Chapaferro (presupuesto 00189032, 23-03-2026, ARS 2.332/kg sin IVA ÷ BNA de mar-26
  1.416,29 = USD 1,6466/kg). Una hoja de 2500 x 6000 (1.121,6 kg) alcanza para las dos virolas (desarrollo 2 × 2.842 mm), y el
  sobrante se usa para el refuerzo. Rolado: Sandri 14-08-2026, ARS 1.950.000 por virola de 3/8" (incluye corte, biseles,
  cilindrado, armado y punteado) ÷ BNA de ago-26 = USD 1.282,76 por pieza (similar).
- Casquetes: Cintolo 20-11-2025, 36" **1/4"** A516-70, USD 828,35 c/u (similar: el espesor pedido es 3/8"; pedir cotización).
- Chapa A-36 por kg: `acero_por_kg.csv` (feb-2026). Bridas, caños y codo: Renard 12-2025 y la planilla Sacde/15. Caño 2" de stock.
- Soldadura junta por junta: 265 pulg × USD 16,2 (planilla Sacde/15, 20-02-2026). Incluye 3 circunferenciales de 36", 2
  longitudinales, injertos, bridas SO, juntas de 2", la media cupla, el refuerzo y el sombrerete. Detalle en el ítem S01.
- Radiografía (Antonelli 11-2025): 35 placas grandes y 6 chicas, 2 servicios de RX y 1 de LP = 2.260.
- Pintura: 22 m² × USD 40,43 (granallado + pintura de Sacde/15) = 889,46.
- Horas: ingeniería 80 h y calidad 100 h a USD 15; montaje 225 h (por actividad, incluye PH) a USD 16.
- Alternativa cargada como segunda fuente: fabricación tercerizada por kg (Ledesma 3,31 USD/kg, 02-03-2026).

## Resultado (costo por tanque, borrador, sin revisar)
| | REAL | APP | AGENTE |
|---|---:|---:|---:|
| Materiales | 6.104,65 | 2.562,40 | 7.211,75 |
| MO y servicios | 16.520,00 | 27.985,21 | 13.742,30 |
| **Total** | **22.624,65** | **30.547,60 (+35%)** | **20.954,05 (−7%)** |

La APP da +35%, pero por errores que se compensan: materiales −58% (virolas sin precio) y MO +69% (horas de un TK de glicol
de 12" y juntas de 36" contadas dos veces con factor Sch 40). Los 14 errores y sus correcciones están en `errores_app.md`.
El AGENTE queda 7% abajo porque usa MO propia (soldadura por pulgada + horas) en lugar de Quesada. La planilla también
tenía esa opción ("ITT propio", 18.294,65). Los materiales del AGENTE dan +18%: el rolado de Sandri por pieza y el casquete
de 1/4" a USD 828 son más caros que lo que consiguió ITT en feb-2026.

## Pendiente para las herramientas (no se tocaron en este caso)
Ver `errores_app.md`. Lo más urgente es `estimar_horas.py` (antecedente de otro tamaño y tipo) y `precotizar.soldaduras()`
(multiplicador del caño aplicado a virolas y casquetes, Sch 40 por defecto, sin longitudinales ni injertos). Después vienen
la virola como pieza (chapa por kg + rolado) y la pintura de la envolvente.
