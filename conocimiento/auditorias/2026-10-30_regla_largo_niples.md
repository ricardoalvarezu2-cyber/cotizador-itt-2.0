# Revisión independiente · largo del niple como diferencia crítica (30-10-2026)

Cambio: `largo_mm` entra en las diferencias críticas del buscador (`herramientas/buscar_material.py` y `web/src/busqueda.js`, misma lista) y el largo del niple se lee también de "L:100", "L=100" y "Largo 150" (`herramientas/catalogo_materiales.py`). Aprobado por Matías el 30-10-2026.

Revisor: agente que no hizo el cambio.
- `largo_mm` solo es atributo de Niples: no afecta otras familias. Python y página aplican la misma lista.
- El patrón nuevo leyó bien los 3 niples que lo usan (NIP-02866, NIP-02872, NIP-05009), sin falsos positivos con rosca, libras ni "LB".
- Casos de prueba: 2" sch 80 de 1.000 mm → NIP-03373 (1.000 mm, USD 40,00), el de 100 mm queda segundo; 1/2" sch 160 NPT/BW 100 mm → NIP-05009 (USD 10,00); 1" sch 80 100 mm → NIP-01788 (100 mm, estimado con alerta).
- Hallazgo 1 (se deja así): un niple sin largo conocido puede quedar primero frente a uno de otro largo con precio firme, porque "sin dato" y "largo distinto" cuentan igual. Ninguno tiene el largo pedido y el aviso se ve. 11 niples del catálogo no tienen largo.
- Hallazgo 2 (corregido): "NIPLE APE ½ NPT + Zincado - Largo 150" (NIP-01813) no leía el largo; ahora lee 150.

Casos de prueba que quedan: los 5 renglones aceptados en `conocimiento/tecnico/buscador_resultados_aceptados.json` (CAPEX pos 12 y 25, P02 pos 16 y 23, TS01 pos 17).
