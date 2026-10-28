# Registro de cotizaciones

Una carpeta por cotización: `COT[AA]-[código de cliente]-[NNN]_<CLIENTE>_<PEDIDO>/`. Para empezar una nueva, copiar [`_plantilla/`](_plantilla/README.md) y seguir la [guía](../conocimiento/guia_cotizacion.md).

| Código | Cliente | Pedido | Equipo | Cant. | Precio c/u USD | Total USD sin IVA | Plazo | Estado | Enviada | Resultado | Carpeta |
|---|---|---|---|---|---|---|---|---|---|---|---|
| COT26-1003-001 | CAPEX S.A. (1003) | OQ 8209 / OR 53081 (19/10/2026) | Puente armado BBO MEC 1500 | 2 | 7.620,59 (provisorio, 63% estimado) | 15.241,18 | 75 días | borrador; revisión independiente hecha (3 críticos), esperando precios de Compras | — | — | [COT26-1003-001_CAPEX_OQ8209](COT26-1003-001_CAPEX_OQ8209/bitacora.md) |
| COT26-0330-001 | YPF S.A. (0330) | Lic 69343 skids concentradores VCD26217 (10-10-2026) | Skid concentrador 1000623713 | 3 | 211.445,38 (borrador; 61% estimado, de la PC0) | 634.336,14 | 120 días | borrador; recotización de la planilla PC0, sin plano | — | — | [COT26-0330-001_YPF_LIC69343_SKID713](COT26-0330-001_YPF_LIC69343_SKID713/bitacora.md) |
| COT26-0330-002 | YPF S.A. (0330) | Lic 69343 skids concentradores VCD26217 (10-10-2026) | Skid concentrador 1000623708 | 6 | 125.367,82 (borrador; 64% estimado, repuestos sin precio) | 752.206,92 | 120 días | borrador; recotización de la planilla PC0, sin plano | — | — | [COT26-0330-002_YPF_LIC69343_SKID708](COT26-0330-002_YPF_LIC69343_SKID708/bitacora.md) |

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
