# Auditoría del proceso de cotización · Camuzzi CP 24578 (28-10-2026)

Agente independiente; no revisó números (eso está en la sección "Revisión independiente" de cada bitácora).

**Veredicto:** base sólida (trazabilidad por fuente, revisión independiente efectiva, P4 ter aplicada), pero los paquetes no son presentables: la oferta dice "según plano" con renglones en 0 y desvíos sin declarar, hay totales distintos entre bitácoras y README, y el separador no tiene memoria de cálculo.

## Alto
1. Renglones en 0 (sin_ref) no aparecen en la oferta: bloquear `generar_oferta.py` o marcarlos en portada.
2. Desvíos sin declarar (reguladora #300 con OPSO): volcar a "Aclaraciones y desvíos" los `similar` que pesan >5%.
3. Tres versiones del precio (bitácoras vs README/ofertas): totales generados por `armar_cotizacion.py`, control en `verificar_todo.py`.
4. P8 tarde y contra antecedentes equivocados (no está CAMUZZI/23): priorizar mismo cliente/plano tipo, familia separador/filtro, no publicar con desvío >15% sin explicación.
5. Sin fecha límite ni entregables del concurso (planilla del cliente, DDJJ, portal): campos `pedido.fecha_limite` y `entregables_cliente`.
6. Separador sin memoria: `herramientas/dimensionar_recipiente.py` (ASME VIII, arreglo real, kilos, memoria preliminar); mientras tanto la 003 como consulta al cliente.

## Medio
7. Plazo: ofrecido 120 contra 125 calculados; PSV y bridas de `controles_tablas` sin cargar; avisos que bloqueen.
8. `armar_json.py` ad hoc por carpeta: `correcciones.yaml` + `precotizar.py --aplicar`; juntas y espárragos internos, pintura del skid y media tira a la herramienta; textos comunes en `cotizaciones/_licitaciones/`.
9. Caños medidos del dibujo: columna `origen_cantidad`; `controles_tablas` lee mal el schedule.
10. Revisión independiente con formato fijo (`revision.md` con lista por ítem).
11. Registrar "lecciones leídas hasta #N" al empezar (se repitió un error conocido).
12. Lista para Compras: priorizar sin_ref y lo que pesa; marcar cotizaciones de más de 90 días (Tormene 16-06).

## Bajo
13. Tres copias de `pedido/`: una sola en `fuentes_originales/pedidos_web/`.
14. Horas "por criterio" sin referencia citada (roza P4 ter).

## Tres cotizaciones o una
Bien partir en tres; falta un nivel de licitación (fecha, entregables, planilla del cliente, total) y el flete como escenario (hoy se cobran tres fletes).

## Mantener
Fuente por renglón con `coincide` y diferencia · consultas al cliente en vez de suponer · revisión independiente con correcciones reales · P4 ter con error en `verificar_computo.py` · separador ±30% con sensibilidad · marca BORRADOR · controles de plazo, antecedentes y tablas (falta que bloqueen).
