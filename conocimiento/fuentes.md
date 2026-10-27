# Inventario de fuentes

Todos los archivos de ITT revisados para armar esta base, en orden cronológico (por fecha de última modificación). Revisado el 27/10/2026.

**Estados:** ✅ vigente (se usa en la base) · 📚 referencia histórica · ❌ reemplazado · 🗑️ duplicado

## Técnico: factores de soldadura, END, espárragos y perfiles

| Fecha | Archivo | Autor | Estado | Comentario |
|---|---|---|---|---|
| 2022-10 | Soldadura, factores por diámetro.docx | L. Bustamante | 📚 | Escaneo del documento fuente de los factores. **Respalda la regla `espesor / espesor STD`** |
| 2023-01 | Copia de Factores de Soldadura por diámetro.xlsx | L. Bustamante | ❌ | Placas de RX sobreestimadas (48" = 29 placas) |
| 2023-05 | Tabla_I.xlsx | L. Bustamante | ❌ | Catálogo de nomenclatura. Integrado después como "TABLA GENERAL" |
| 2024-02 | Factores de Soldadura por diámetro.xlsx | L. Bustamante | ❌ | Corrige placas (215/430 mm), agrega perfiles y pintura |
| 2025-05 | Factores_de_Soldadura_p_MOMaster_.xlsx | C. Alfonso | ❌ | Agrega 17 hojas de perfiles y tubos, y espárragos por serie |
| 2025-11 | Factores_de_Soldadura_p_MOMaster.xlsx | C. Alfonso | ❌ | |
| 2025-11 | Factores_de_Soldadura_p_MO.xlsx | C. Alfonso | 🗑️ | Idéntico byte a byte al anterior |
| 2026-02 | Factores de Soldadura p MO - rev 2025.xlsx | J. Elejondo | ❌ | Pone factor 1 a SCH40 de 12" a 20" |
| 2026-03 | **Factores_de_Soldadura_p_MO - rev 02.2026.xlsx** | J. Elejondo | ✅ | Base de `tecnico/*`. Revierte el cambio anterior, 2 placas en 1"–1½", corrige la clave de 2" SCH160 |
| 2023-04 | Planilla de Acero Inox.xlsx | L. Bustamante | 📚 | Pesos de caño inoxidable A312. Pasada por OCR, con errores |
| 2024-02 | PLanilla Caños de Acero Inoxidable.xlsx | L. Bustamante | 📚 | Presiones admisibles B31.1. Pasada por OCR, con errores |

## Mano de obra y costos

| Fecha | Archivo | Autor | Estado | Comentario |
|---|---|---|---|---|
| 2022-10 | Copia de Anexo 1 4562.xlsx (TGS, spools Joule Thomson) | J. Alfonso / L. Bustamante | 📚 | Precio de venta de MO por pulg-eq en pesos (mar-2022). Cómputo por línea y por clase |
| 2023-12 | Costos_MO.xlsx | L. Bustamante | ❌ | Primera versión del modelo de MO. Llena de #REF! |
| 2024-01 | PLANILLA DE COSTO - TANQUE DE MEZCLA.xlsx | L. Bustamante | ❌ | Antecesora de la Planilla de Costo Master |
| 2024-02 | Costos_MO_Master_II-SEP_TRIFASICO-19-4-24.xlsx | L. Bustamante | 📚 | Caso: separador trifásico AESA (32 USD/pulg, 7,4 USD/kg) |
| 2024-09 | **Costos_MO_Master.xlsx** | L. Bustamante | ✅ | Modelo de estimación de MO (28 USD/pulg, 10 USD/kg). Tiene errores, ver reglas §7 |
| 2024-11 | **PLANILLA DE COSTO -Master.xlsx** | C. Alfonso | ✅ | Planilla de costo y venta (factor 1,33, IVA, hitos de pago) |
| 2024-12 | **Costo MO de ITT Octubre.24.xlsx** | O. Fuentes / C. Alfonso | ✅ | Costo real de planta por hora y por pulgada, más benchmarking de terceros. ⚠️ Incluye una hoja de sueldos con datos personales: no se copia a esta base |
| 2024 | Planilla base para cotizaciones.xlsx | — | ❌ | Tarifas de END desactualizadas. Errores de fórmula, ver reglas §7 |

## Precios

| Fecha | Archivo | Autor | Estado | Comentario |
|---|---|---|---|---|
| 2024-08 | reporte de compras.pdf (453 páginas) | Sistema | 📚 | Órdenes de compra por artículo de dic-2021 a ago-2024, mayormente en pesos. **Pendiente de procesar** |
| 2024-11 | STOCK VALORIZADO ITT.xlsx | O. Fuentes | ✅ | Base de `precios/stock_2024-11.csv`. La hoja oculta "borrador19.09" es una versión previa. 601 artículos sin fecha de compra |
| 2025-09 | Lista TAVAL 30 vigencia 01-09-2025 - ventas.xlsx | Taval | ✅ | Coeficiente 1,25 y USD/kg. Columnas de precio con #REF!: **pendiente de obtener una versión sana** |
| 2025-11 | 1788-JCA-1125 - ITT SA.pdf (Antonelli) | Antonelli | ✅ | Tarifas de END, en `costos/tarifas.csv` |
| 2025-12 | RENAR ListaPrecios_ittSA_20251226.xlsx | Renard | ✅ | Base de `precios/lista_renar_2025-12.csv` |
| 2026-02 | Precios varios materiales de acero, chapa, angulo, etc.xlsx | J. Elejondo | ✅ | Chapa, perfiles y caño estructural en USD/kg, en `costos/tarifas.csv` |
| 2026-03 | **COTIZACION ELEMENTOS DE EQUIPOS.xlsx** | Lautaro / J. Elejondo | ✅ | Base de `precios/precios_componentes.csv`. 25 rubros con proveedor y fecha |

## Comercial y codificación

| Fecha | Archivo | Autor | Estado | Comentario |
|---|---|---|---|---|
| 2022-05 | Registro de presupuesto.xlsx | L. Bustamante | ✅ | Base de `comercial/registro_cotizaciones_2020-2022.csv` y `codificacion/familias_producto.csv` |
| 2022-09 | ITTSA-Diagrama de Proceso.docx | L. Bustamante | ✅ | Proceso comercial y de ejecución de ITT (ver README) |
| 2023-02 | especificacion de una valvula Rev A.pdf | C. Sorrentino | 📚 | Explicación escrita del codificador |
| 2023-05 | vta_remitoporcliente.xls | Sistema | ✅ | Base de `comercial/ventas_2022-2023.csv` |
| 2023-05 | vta_remitoporcliente_i.xls | Sistema | 🗑️ | Mismo contenido, con fechas como texto |
| 2023-07 | **HD Instructivo de codificacion.xlsx** | S. Giron / C. Sorrentino | ✅ | Base de `codificacion/*` y `comercial/clientes.csv` |

## Técnicos de ingeniería (para futuros módulos)

| Fecha | Archivo | Autor | Estado | Comentario |
|---|---|---|---|---|
| 2024-11 | Cálculo calentador.xlsx y Cálculo calentador BAGSA.docx | G. Vicens | 📚 | Dimensionamiento térmico de un calentador indirecto (API 12K). Los dos tienen el mismo cálculo |

## Pedidos y planos de prueba

| Fecha | Archivo | Uso |
|---|---|---|
| 2026-10 | Mail Almacenes Petroleros (carreteles 3" CL900) | Caso piloto de cotización |
| 2026-04 | ACO-CNV-PTIP-M-PL-005 Rev0.dwg (manifold 8×4 S600, Tecpetrol) | Prueba de lectura de DWG. Confidencial de Tecpetrol |

## Faltantes conocidos

1. **Plazos:** no hay datos de tiempos de entrega de proveedores ni de duración de fabricación.
2. **Costo real de proyectos terminados** para comparar con lo cotizado.
3. **Registro de cotizaciones de 2022 a hoy** (el último es de mayo 2022).
4. **Lista Taval sin #REF!**.
5. **Reporte de compras** (PDF de 453 páginas) sin procesar: es el historial de precios de compra.
