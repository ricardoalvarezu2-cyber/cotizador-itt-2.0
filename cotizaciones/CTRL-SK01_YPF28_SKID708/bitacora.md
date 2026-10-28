# CTRL-SK01: caso de control con el skid concentrador 1000623708 (YPF Lic 69343, Bloque LAN)

**No es una cotización para el cliente.** Es un caso de control del cotizador. Se comparan tres números: el costo **REAL** de la planilla PC0 de ITT, corregido; la precotización automática (**APP**); y la recotización a mano del **AGENTE**. El detalle está en `errores_app.md`.

Equipo: 3 entradas de 12" XS y un colector de 16" STD, #300, CE22, 6 unidades, 100% RX (hoja DISEÑO de la PC0). Fecha de la PC0: 10-10-2026. Fecha del control: 28-10-2026.

## Fuentes
- PC0: `fuentes_originales/ofertas_texto/YPF/28- Lic 69343 - SKIDS CONCENTRADORES VCD26217 - BLOQUE LAN/4.Armado de la Oferta Comercial/Cotización Lic 69343 Skid concentradores VCD26217 PC0.xlsx.txt`, hoja 1000623708. Es el único documento del proyecto en el repositorio: no hay plano.
- Referencia: `cotizaciones/COT26-0330-002_YPF_LIC69343_SKID708/` (bitácora con 12 inconsistencias de la PC0). Su tabla de materiales coincide renglón por renglón con la PC0, así que se copió.
- Antecedentes abiertos:
  - **TAVAL/72**, skid gemelo SCC-010 de 3×8" + 12", de la misma red YPF VCD21223. Se usaron sus listas de materiales, válvulas Taval y "Costuras", Complemet 275397, MS 48.729 y la propuesta Galvanotecnia.
  - **TAVAL/78**, concentrador de 10". Se usaron la lista Taval × 0,52, MS 49.323 y Ledesma 200317.
  - **TAVAL/69**, Cintolo 33764 y Ledesma 200296/7.
  - **TECPETROL/9 REV C**: estructura a 4 USD/kg.
  - **TECPETROL/13**: espárragos.
  - **ENDRESS HAUSER/33**: Ledesma 200276.
  - Lista Renard 12-2025, stock 11-2024, acero por kg 02-2026 y tarifas DB NDT.

## Errores de la PC0 corregidos en `historico.csv` (costo por equipo)
1. **La MO de terceros se cuenta dos veces.** "Materiales, MO y SVC" (56.698,70) ya suma Ledesma 13.250, y el Resumen la vuelve a sumar como "Mano de obra de terceros" 13.250. Comprobado: 32.105,58 + 3.552 + 1.117,50 + 1.320 + 5.000 + 13.250 + 353,62 = 56.698,70. Se cuenta una vez. **Este error no estaba en la bitácora de COT26-0330-002.**
2. **Los repuestos también se cuentan dos veces.** Van 353,62 dentro de materiales y 2.305,40 en el Resumen. Además, la lista de repuestos es la del skid 713. Se excluyen porque son un ítem comercial aparte.
3. **El 20% de overspray se aplica dos veces:** al skid (3.552 en lugar de 2.960, con el 20% también sobre la perfilería) y al piping (1.320 en lugar de 1.100).
4. **Montaje + dimensional + desmontaje (3.000)** figura en el bloque de MO de terceros, pero la PC0 no lo suma. En el 713 sí. Se agrega.
5. **Instrumentos (1.110):** el alcance dice «Instrumental: NO» y no están en la tabla de materiales. Se excluyen.
6. **Transporte (2.500):** la hoja dice EXW Quilmes Oeste. Se excluye.

Resultado: PC0 103.326,16 → **REAL corregido 85.995,15** (60.808,45 de materiales + 25.186,70 de MO y servicios). La caución (459,20) queda.

## Qué se hizo
1. Se copió `_plantilla/`.
2. `pedido/lista_materiales_plano.csv`: la tabla de COT26-0330-002, revisada contra la PC0. Las cantidades se verificaron:
   - 288 espárragos 1 1/8" = 18 uniones de 12" × 16;
   - 40 espárragos 1 1/4" = 2 uniones de 16" × 20;
   - 18 juntas de 12" = 6 por entrada.

   Se agregó la pos 31, bastidor de 850 kg (A-36). En `extremos_campo` va 0 en todas las filas: las conexiones con el cliente son bridadas.
3. `cotizacion.json`: N = 6, `rx_pct` = 100, `ph_horas` = 8, `equipo.tipo` = skid, `diametro_pulg` = 16 y `fecha_referencia` = 10-10-2026.
4. APP: `python herramientas/precotizar.py cotizaciones/CTRL-SK01_YPF28_SKID708 --excluir "YPF/28" --excluir "pedidos_web" --excluir "COT26-0330"` → `precotizacion.md`, `cotizacion_auto.json`. Después, `python herramientas/comparar_historico.py cotizaciones/CTRL-SK01_YPF28_SKID708` → `comparacion_historico.md`.
5. AGENTE: `buscar_antecedentes.py --familia SK` (los dos primeros son las copias COT26-0330, que se saltearon), `buscar_material.py` y `buscar_servicio.py` renglón por renglón, abriendo los originales. El resultado está en `cotizacion_agente.json`. Se comparó con `comparar_historico.py ... --json cotizacion_agente.json` → `comparacion_cotizacion_agente.md`. El JSON se arma con `python cotizaciones/CTRL-SK01_YPF28_SKID708/armar_agente.py cotizaciones/CTRL-SK01_YPF28_SKID708`.
6. No se corrieron `armar_cotizacion.py` ni `verificar_todo.py`, ni se modificó nada fuera de esta carpeta.

## Resultado (por equipo, USD sin IVA)

| | Materiales | MO y servicios | Total | contra REAL |
|---|---:|---:|---:|---:|
| REAL (PC0 corregida) | 60.808,45 | 25.186,70 | **85.995,15** | — |
| APP | 41.651,04 | 19.595,61 | **61.246,65** | −29% |
| AGENTE | 56.224,21 | 19.634,72 | **75.858,93** | −12% |

Sin lo que la app deja SIN PRECIO (pos 21 y 28): REAL 85.876,05 · APP 61.246,65 · AGENTE 75.763,83.

Errores principales de la app:
- retención 12" cotizada con una wafer de 3": −9.144;
- esférica 12" cotizada con una retención 12" #600: −2.748;
- similares de menor diámetro sin escalar: −3.515;
- tee XS cotizada con una STD: −1.486;
- las fuentes de TAVAL/72 y TAVAL/78 no están en el catálogo;
- horas de un skid de bomba de 4": +1.384;
- schedule XS no leído en la soldadura: −989.

## Criterios del agente (estimados, para confirmar en una cotización real)
- **Juntas:** las del skid gemelo TAVAL/72 (21 + 7), con factores 12" XS 1,334 y 16" STD 1,0.
- **Soldadura:** propia, a 16 USD/pulg-eq. La alternativa es Ledesma, sin presupuesto del mismo alcance.
- **Horas:**
  - montaje: 176 h (detalle en el JSON);
  - ingeniería: 25 h por equipo (150 h por la serie);
  - calidad: 15 h por equipo.
- **Estructura:** 4 USD/kg, según TECPETROL/9.
- **Pintura:** 51,1 m² × 50 USD/m².
- **Caución:** 450, estimada.
- **Válvulas Taval 12":**
  - retención: 3.270;
  - esférica: 5.640.

  Son estimadas desde las de 10" de TAVAL/78 y las 12" #600 de Sacde/12; hay que pedir la lista Taval.
- **Bridas y junta de 16":** estimadas desde la lista Renard y MS.
