# RFQ REV.4.1 definitiva · Skid de regulación ERP Parque Industrial Tres Arroyos (04-11-2026)

- Original: `RFQ_REV4_1_DEFINITIVA_SKID_ERP_TRES_ARROYOS.xlsx` (lo pasó Matías el 04-11-2026). Base: plano SCE-RE-315-0048 y especificación SCE-RE-515-0032: es el mismo skid de `cotizaciones/COT26-0135-001_CAMUZZI_CP24578_SKIDREG`.
- Pedido de Matías: completar la primera hoja (columnas L a Q) **solo con productos iguales**, sin similares ni sugeridos.
- Completado: `RFQ_REV4_1_SKID_ERP_TRES_ARROYOS_precios_iguales.xlsx` (lo genera `llenar_iguales.py`). Borrador, sin revisar. USD sin IVA, ajustado al 04-11-2026.
- Criterio: igual = buscador de materiales (`buscar_material.py`) sin diferencias, con los datos que el RFQ no trae (schedule de las bridas, cara de la ciega, NPT de las cuplas) tomados del plano a través del cómputo de la COT26-0135-001. La marca no cuenta para igual (regla del buscador): donde el listado del cliente SCE-IN-501-0015 no incluye al proveedor, se aclara en Observaciones.
- Resultado: 11 renglones iguales (M05, M5B, M06, M6B, M07, M08, M10, M12, M13, M17B, M18B), total USD 2.013,62. M6B es un precio ESTIMADO (período con cepo). El resto queda sin precio, con el motivo.
