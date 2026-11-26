# Planilla verificada (método de Ricardo, skill `cotizar-skids-equipos`)

Pedido de Ricardo Álvarez (26-11-2026): "hacer lo mismo y aprenderlo". Se usa cuando Ricardo pasa **su planilla de Ventas** (hojas por SAP o equipo, Resumen, Pie de Venta) con planos y quiere la **planilla final verificada**. Es un camino distinto del cotizador del repositorio (`armar_cotizacion.py`): acá se trabaja **sobre el Excel de Ricardo**, que sigue vivo y con fórmulas.

## Dónde está todo
- **Pasos completos:** el skill `.claude/skills/cotizar-skids-equipos/SKILL.md`. Es copia del skill de la cuenta del 26-11-2026; si cambia en la cuenta, se vuelve a copiar.
- **Modelo 1, sin script:** la PC0 de la Lic 69343 (skids concentradores, 2 SAP) en `fuentes_originales/revisiones/2026-11-26_YPF_Lic69343_PC0_modelo_planilla_verificada/`. Ahí se ve el formato de cada hoja.
- **Modelo 2, con script reproducible:** `cotizaciones/COT26-0330-004_YPF_GASLIFT_PUENTEINYREG/armar_planilla_verificada.py` (puente de inyección y regulación, 1 equipo). Para un caso nuevo, copiar el script y cambiar los datos del principio: `precio(...)`, `COR`, `NUEVAS_*` y perfiles.
- **Insertar filas:** `herramientas/excel_filas.py` corre todas las referencias de las fórmulas del libro, porque openpyxl no lo hace. Prueba: `herramientas/test_excel_filas.py`. Para que el subtotal crezca solo, las filas se insertan antes de la **última** fila de cada bloque.

## Resumen del formato (lo que espera Ricardo)
1. Se trabaja sobre una **copia** y se entrega con revisión numerada (`<nombre>_revN.xlsx`). Si Ricardo pasa una planilla con cambios suyos, se parte de esa.
2. **Hoja de costo corregida contra el plano:**
   - amarillo claro = valor cambiado; verde = fila agregada;
   - columna **Aclaración** con el porqué y una columna con la cantidad anterior;
   - los renglones que no van quedan en 0 con su aclaración, no se borran.
3. **Precios proveedores:**
   - una columna por proveedor, con solo las cotizaciones que **cumplen** (igual o mayor espesor, espárragos iguales o más largos, misma serie y norma);
   - precio anterior, precio sin confirmar = MIN, precio adoptado, ahorro, proveedor elegido, cotización utilizada (N° y fecha) y observaciones;
   - la hoja de costo toma de acá precio, proveedor y cotización por fórmula;
   - perfiles en USD/kg: USD/m ÷ kg/m.
4. **Precios a confirmar:**
   - es el **único lugar de carga**: columnas amarillas para precio confirmado, proveedor y N° de cotización;
   - precio vigente, diferencia, estado PENDIENTE/CONFIRMADO y contador de pendientes;
   - un formato condicional pinta de amarillo los precios pendientes en la hoja de costo y en el comparativo;
   - el provisorio sale de la columna "sin confirmar", para evitar referencias circulares.
5. **Pintura m2:** caño π·OD·L; tees y bridas por unidad (ASME B16.9; bridas sin la cara RF); estructura según el plano o por m²/m de perfil. USD 50/m², sin overspray.
6. **Soldaduras:** juntas a tope = (extremos BW + 2 × tramos) / 2, por diámetro; más olets y socket weld; USD 22 por pulgada-diámetro y USD 2/kg de estructura. La MO de terceros de la hoja de costo toma este total.
7. **END:** presupuesto ITT en pesos (servicio RX y LP por jornada, placas); juntas × % RX; 40 juntas por jornada. TC: **promedio mensual del oficial BNA venta**, regla del proyecto (la PC0 usó el TC de Miyashiro: no repetir).
8. **Verif. espesores (B31.3 304.1.2):** lo que no cumple se cambia (por ejemplo, niples roscados de ½"–1" de Sch 80 a Sch 160).
9. **Verificación (para la dirección):**
   - por rubro, todo vinculado a la hoja de costo;
   - en el modelo 2 suma la **cantidad del plano** y la diferencia;
   - **controles contra la hoja de costo, que tienen que dar 0**.
10. **Cierre:**
    - recalcular con LibreOffice (`soffice --headless --calc --convert-to xlsx`) y comprobar que no queden errores (#VALUE!, #NAME?…) y que los controles den 0;
    - informar el total antes y después, qué cambió y qué queda a confirmar.

## Tropiezos ya vistos
- Un texto con comillas de pulgadas (`3/4"`) dentro de una fórmula da #VALUE!/#NAME?: hay que duplicar las comillas (`""`).
- Al insertar filas, los SUM no crecen si la inserción va debajo del rango (igual que en Excel).
- Las válvulas Taval se confirman con el skill `cotizar-valvulas-taval` (lista de Drive + stock). Si no se corrió, hay que decirlo.
