# Separadores coalescentes: modelos de oferta de ITT 2017–2020

Fuente: carpeta "15-SEPARADOR COALESCENTE" de ITT (12 planillas de oferta con la plantilla vieja Pres./Mat./M.O.), que Matías pasó el 06-11-2026 para sumar la información técnica. Originales y texto extraído en `fuentes_originales/planillas_modelo/15-SEPARADOR COALESCENTE/`.

## Tablas

| Archivo | Qué tiene |
|---|---|
| `separadores_coalescentes_modelos.csv` | Un renglón por planilla: Ø y serie, cuerpo (caño o chapa rolada, material, espesor, largo), casquete, cierre (tapa de acción rápida o brida + ciega), conexiones, cantidad y tipo de elementos coalescentes, caja de chicanas, soporte, instrumentos y válvulas, repuestos, costos del presupuesto y notas. Armada a mano leyendo cada planilla (06-11-2026). |
| `separadores_coalescentes_componentes.csv` | La lista de materiales completa: 609 renglones con cantidad, con columnas fijas (ítem, descripción, material, Ø, largo, schedule, serie, espesor, ancho, proveedor, plazo, notas al margen, precio unitario y total) y el renglón original. Generada con `python herramientas/extraer_modelos_planilla.py "fuentes_originales/planillas_modelo/15-SEPARADOR COALESCENTE" conocimiento/tecnico/separadores_coalescentes_componentes.csv`. |

Modelos: 14" #600 (2018) y 14" #150 con skid (2019); 18" #600 y 30" #600 tipo TGS (2019); 22" #300 (2020); 22" #600 de 2017 (con BC); 22" #600 tipo Camuzzi, sin skid (2017) y con purga automática (2018); 24" #600 con skid (2019); 36" #300 CAPEX (2019); 42" #600 Pluspetrol en SA-36 38 mm y en A-516 Gr. 70 32 mm (2019).

## Para qué sirven

- **Diseño de referencia** al cotizar un separador o filtro coalescente: qué lleva (cuerpo, casquete, cierre, internos, elementos, caja de chicanas, pollera o skid, instrumentos, purga) y en qué cantidad según el Ø y la serie. Sirven de lista de control para que no falte nada en el cómputo.
- **Elementos coalescentes usados:** 5,5" × 915 mm de 5 µm (Gora o Peco) en los tipo Camuzzi; 915 × 114 o 141 × 915 mm de 0,3 µm (Gora; Peco NGGC-336-PL01) en los demás. Cantidad: 3 en 14", 4 en 18", 7 en 22" #300, 8 en 22" #600 y en 42", 9 en 24", 23 en 36" (provistos por el cliente).
- **Cierre:** tapa de acción rápida vertical (Futura o TAG) hasta 36"; en 42" brida WN + brida ciega. En el 18" TGS se cotizaron las dos opciones aparte (tapa rápida USD 9.245,41; brida + ciega USD 3.816,60, de 2019).
- **Chapa del cuerpo:** las planillas compran un ancho de π × Ø nominal + 250 mm (14" a 42"); la tipo Camuzzi de 2018 usa π × Ø sin sobrante. Es el criterio de esas planillas, no una regla revisada.
- **MO del piping de un skid (36" CAPEX):** la hoja "Calculo MO" cuenta 354 pulgadas de soldadura, 25 pulgadas por día y 664 horas en total.

## Cuidados (no usar sin revisar)

1. **Precios de 2017–2020, no vigentes.** Están en USD como figuran en la planilla, antes y durante el cepo de 2019. No se cargaron al catálogo de materiales ni al de servicios: no hay dólar mensual de esos años en `costos/dolar_mensual.csv` para aplicar la regla del cepo, y para cada pieza hay precios más nuevos. Sirven solo para ver proporciones (por ejemplo, la tapa rápida pesa el 20–40% de los materiales del recipiente).
2. **Datos de plantilla que no son del equipo:** el "PESO TOTAL 2500 kg" de la hoja Mat., las hojas "Pintura" y "m2 Pintura" (26,31 m² en todas), la hoja M.O. (los mismos números en casi todas) y la hoja "CALCULO PB-2" son restos de la plantilla. El bloque de arriba de la hoja Mát. (tags PSV21103 y LV21103, proveedores CONVER, FUTURA y ESFEROMATIC, sin cantidad) también viene de otra oferta. El extractor lee desde el título del equipo y solo renglones con cantidad.
3. **El peso de los casquetes está mal calculado en la planilla** (0,03 a 0,26 kg): no usar esas columnas. Para pesos, usar las tablas de `tecnico/`.
4. **Factor:** en estas planillas el FACTOR (0,75 y 0,80 en la 36") divide al costo (venta = costo / 0,75, o sea ×1,33). Se suman ingeniería y calidad (2–4%) y embalaje (1%). No es el criterio vigente (1,35).
5. **Material del cuerpo:** varios modelos usan chapa SA-36 de 19 a 38 mm en recipientes #300 y #600. Hay que revisarlo contra ASME VIII (UCS-6 limita el uso de SA-36 en partes a presión); el 42" de 2019 ya se rehízo en A-516 Gr. 70. No copiar el material sin revisar el código.
6. En el 22" "con BC" el título dice conexiones de Ø16" pero la lista trae bridas de 6"; "BC" no está aclarado.
7. Las cantidades de instrumentos y válvulas dependen del alcance de cada oferta (con o sin skid, piping, purga automática). Antes de tomar uno como antecedente, comparar el alcance.

## Antecedentes

Estos modelos no entran al índice de antecedentes (`buscar_antecedentes.py`): son de 2017–2020 (2021–2024 se muestra sin ficha y anterior no se indexa) y no son proyectos con carpeta. Para un separador o filtro coalescente, consultar esta tabla además del buscador. El más parecido al separador de Camuzzi CP 24578 (COT26-0135-003) son los dos tipo Camuzzi 22" #600 (cuerpo, tapa rápida, 8 elementos de 5 µm, caja de chicanas inox, purga automática con válvulas 357), aunque el diseño de 2026 sigue el plano tipo SCE-RE-112-0001 (36", 20 cartuchos).
