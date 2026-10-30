# Registro de cotizaciones

Una carpeta por cotización: `COT[AA]-[código de cliente]-[NNN]_<CLIENTE>_<PEDIDO>/`. Para empezar una nueva, copiar [`_plantilla/`](_plantilla/README.md) y seguir la [guía](../conocimiento/guia_cotizacion.md).

| Código | Cliente | Pedido | Equipo | Cant. | Precio c/u USD | Total USD sin IVA | Plazo | Estado | Enviada | Resultado | Carpeta |
|---|---|---|---|---|---|---|---|---|---|---|---|
| COT26-1003-001 | CAPEX S.A. (1003) | OQ 8209 / OR 53081 (19/10/2026) | Puente armado BBO MEC 1500 | 2 | 7.366,12 (provisorio; 3 renglones sin precio, pedir cotización) | 14.732,24 | 75 días | borrador; revisión independiente hecha (3 críticos), esperando precios de Compras | — | — | [COT26-1003-001_CAPEX_OQ8209](COT26-1003-001_CAPEX_OQ8209/bitacora.md) |
| COT26-0330-001 | YPF S.A. (0330) | Lic 69343 skids concentradores VCD26217 (10-10-2026) | Skid concentrador 1000623713 | 3 | 182.162,41 (borrador; 61% estimado, de la PC0; soldaduras recalculadas y precios a 2 decimales 29-10-2026) | 546.487,23 | 120 días | borrador; recotización de la planilla PC0, sin plano | — | — | [COT26-0330-001_YPF_LIC69343_SKID713](COT26-0330-001_YPF_LIC69343_SKID713/bitacora.md) |
| COT26-0330-002 | YPF S.A. (0330) | Lic 69343 skids concentradores VCD26217 (10-10-2026) | Skid concentrador 1000623708 | 6 | 110.297,42 (borrador; 64% estimado, repuestos sin precio; soldaduras recalculadas y precios a 2 decimales 29-10-2026) | 661.784,52 | 120 días | borrador; recotización de la planilla PC0, sin plano | — | — | [COT26-0330-002_YPF_LIC69343_SKID708](COT26-0330-002_YPF_LIC69343_SKID708/bitacora.md) |
| COT26-0135-001 | CAMUZZI GAS PAMPEANA S.A. (0135) | CP 24578 ítem 2 (ERP P. I. Tres Arroyos, 10-2026) | Skid de regulación SCE-RE-315-0048 | 1 | 76.498,56 (borrador; cupla c/ válvula SIN PRECIO por compatibilidad; reguladoras Tormene #300 con OPSO de referencia; esféricas de marca del listado) | 77.290,86 | 120 días | borrador; revisión independiente hecha, falta cotizar reguladoras #150 | — | — | [COT26-0135-001_CAMUZZI_CP24578_SKIDREG](COT26-0135-001_CAMUZZI_CP24578_SKIDREG/bitacora.md) |
| COT26-0135-002 | CAMUZZI GAS PAMPEANA S.A. (0135) | CP 24578 ítem 3 | Skid puente de medición SCE-ME-315-039 | 1 | 29.395,10 (borrador; cupla c/ válvula SIN PRECIO por compatibilidad; filtro FM-6 estimado; esféricas de marca del listado) | 30.189,16 | 105 días | borrador; revisión independiente hecha, falta costear el filtro FM-6 | — | — | [COT26-0135-002_CAMUZZI_CP24578_PUENTE](COT26-0135-002_CAMUZZI_CP24578_PUENTE/bitacora.md) |
| COT26-0135-003 | CAMUZZI GAS PAMPEANA S.A. (0135) | CP 24578 ítem 1 / Concurso 24527 | Separador vertical coalescente (diseño preliminar ITT según la ET de Camuzzi) | 2 | 285.832,80 (preliminar ±30%; 3 renglones SIN PRECIO por compatibilidad; válvula esférica 1/2" roscada SIN PRECIO por regla de compatibilidad; RX con precio confirmado e ingeniería y calidad 250 h, Matías 30-10-2026; DI 1.280 mm × 2 1/4" a la presión de la serie #600, 37 elementos + juego de repuesto) | 566.824,87 | 165 días | borrador; corregida contra la ET el 29-10-2026; faltan memoria de cálculo, caudal por elemento y cotizar purgas, switches, chicanas y API 1104 | — | — | [COT26-0135-003_CAMUZZI_CP24578_SEPARADOR](COT26-0135-003_CAMUZZI_CP24578_SEPARADOR/bitacora.md) |

**Estados:** borrador → revisado → aprobado → enviado → ganada / perdida (con motivo: precio, técnica, plazo, otros) / cancelada. Registrar el resultado es lo que permite aprender qué factor y qué plazo ganan.

## Casos de control (no son cotizaciones para clientes)

Resumen de los 4 controles con agentes y errores repetidos: `conocimiento/auditorias/2026-10-28_controles_4_agentes.md`. Resultado actual de la app en los 5 casos: `controles_resultado.md` (lo arma `python herramientas/correr_controles.py`; correrlo antes y después de cambiar una herramienta).

| Carpeta | Qué controla | Resultado |
|---|---|---|
| `CTRL-F01_INARTECO_FM2_S300` | Precotización automática contra el costo real de un filtro FM2 #300 (planilla TAVAL/40, 15-01-2026) | −75% sin completar; ver `bitacora.md` y `comparacion_historico.md` |
| `CTRL-T01_SACDE20_TKCHOQUE` | Tanque de choque Ø36" (Sacde 20), recotizado por un agente | APP +35% (materiales −58%, MO +69%) · agente −7% |
| `CTRL-C01_PAMPA7_COLECTOR` | Skid colector PAD 6 pozos (Pampa 7) | APP −0,5% (se copió a sí misma; +11% sin eso) · agente +5% |
| `CTRL-P01_TAVAL70_PUENTE2` | Puente de inyección y regulación 2" #600 (Taval 70) | APP −42% · agente +11% |
| `CTRL-M01_TECPETROL9_MANIFOLD` | Skid manifold S600 (Tecpetrol 9) | APP −2% (materiales −34%, MO +50%) · agente −9% |
| `CTRL-TS01_TECPETROL13_TRAMPA` | Trampa receptora 16"x12" #900 (Tecpetrol 13) | APP −19% · agente +1% |
| `CTRL-P02_PAMPA5_PUENTE3` | Puente de producción 3" #300 (Pampa 5) | APP +15% · agente +0,5% |
| `CTRL-SK01_YPF28_SKID708` | Skid concentrador 708 (YPF 28, PC0 corregida) | APP −29% · agente −12% |
| `CTRL-CA01_SACDE18_PIPING` | Prefabricado de piping (Sacde 18, materiales del cliente) | APP +451% sin pintura · agente −0,2%: la app no tiene modo prefabricado |
