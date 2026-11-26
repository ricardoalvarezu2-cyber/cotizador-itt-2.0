# Cruce SC-OC y datos del sistema (ERP de ITT y Taval)

Herramienta hecha por Matías y registrada en el repositorio el 26-11-2026. Lee la base del sistema de gestión, que es SQL Server y solo está en la red de ITT, y arma una página local con el cruce de solicitudes (SC) y órdenes de compra (OC), las fórmulas, las ventas y un cotizador simple con los últimos costos. **No es parte del cotizador automático del repositorio.** Es una fuente de datos que puede alimentarlo; los pendientes están al final.

## Archivos

| Archivo | Qué hace |
|---|---|
| `ACTUALIZAR.bat` | Lo único que se ejecuta. Desbloquea los archivos de la carpeta y corre `cruce_erp.ps1` **como texto** (`[scriptblock]::Create`), pasándole la carpeta en `CRUCE_DIR`. Así Windows no muestra la "Advertencia de seguridad" de archivos bajados de Internet o en unidad de red (pasó en `N:` el 26-11-2026). |
| `cruce_erp.ps1` | Se conecta a cada base, corre 6 consultas (solo `SELECT`), mete los datos en la plantilla y abre el resultado. |
| `plantilla.html` | La página. Lleva adentro xlsx-js-style 1.2.0-beta para leer y escribir Excel. Sin datos funciona en modo manual: se arrastran los reportes .xls del sistema. |
| `ITTSA_ERP.udl`, `Taval_ERP.udl` | Conexiones OLE DB. **No están en el repositorio** porque tienen la contraseña (`.gitignore`); están en la carpeta de la PC de ITT. |
| `Cruce SC-OC (sistema).html` | Salida generada, con datos. No va en `main` (`.gitignore`); la copia sube a la rama `datos-erp`. |
| `github_token.txt` | Token de GitHub para subir la copia. No se sube (`.gitignore`); está en la carpeta de la PC de ITT. |

Los cuatro archivos tienen que estar en la misma carpeta. `.bat` y `.ps1` van con fin de línea CRLF, y el `.ps1` en UTF-8 **con BOM** (sin BOM, PowerShell 5 lee mal los acentos). `.gitattributes` evita que git los convierta.

## Conexiones

| Empresa | Base | Servidor | Usuario |
|---|---|---|---|
| ITT | `ITTSA` | `192.168.0.61,1436` | `sa` |
| TAVAL | `Taval` | `WS2020\WS2020`; si no conecta, el script prueba el servidor de ITT con `ITTSA_ERP.udl` y `USE [Taval]` | `sa` |

Proveedor `SQLOLEDB.1`, idioma `spanish`. **Riesgo:** `sa` es el administrador total. Las consultas son solo de lectura, pero conviene que Sistemas cree un usuario de solo lectura para estas tablas y cambiar la contraseña de `sa` si los `.udl` circularon. Pendiente de Sistemas de ITT.

## Copia en el repositorio (rama `datos-erp`, desde el 26-11-2026)

Pedido de Matías: tener la base de ITT y de Taval accesible desde cualquier lado y que el repositorio se actualice cada vez que se corre `ACTUALIZAR.bat`. El script primero abre la planilla y después sube la copia por la API de GitHub, así que la PC no necesita git.

- **Dónde:** rama `datos-erp` del repositorio preferido `ricardoalvarezu2-cyber/cotizador-itt-2.0` (`$REPO`), separada de `main`. **Si el repositorio es público, no sube nada** y lo avisa. Cada subida es un commit nuevo sin padre que reemplaza la rama entera. Siempre queda solo la última lectura (una sola versión vigente) y el repositorio no crece con cada corrida. No hay que pasarla a `main`.
- **Qué sube:**
  - `LEEME.md` con la fecha de lectura, los períodos, la PC, los errores y las filas por archivo.
  - Por empresa (`ITT/`, `TAVAL/`): `solicitudes.tsv`, `ordenes_compra.tsv`, `remitos.tsv`, `precios.tsv`, `ventas_nv.tsv` y `formulas.tsv`. Son TSV en UTF-8, con encabezado y las mismas columnas de abajo.
  - `Cruce SC-OC (sistema).html`, la página con datos, para bajarla y abrirla en cualquier PC.
- **Si hubo errores de lectura** pregunta "¿Subir igual?" (s/n), para no pisar una copia buena con una incompleta. Si la subida falla, la planilla igual queda abierta y el error se muestra en la ventana.
- **Archivos de más de 90 MB** no se suben (GitHub no acepta más de 100 MB); avisa en la ventana.
- **Token (una sola vez):** en GitHub, Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token. Se crea **desde la cuenta `ricardoalvarezu2-cyber`**, con Resource owner `ricardoalvarezu2-cyber` y Repository access solo `cotizador-itt-2.0`. Permissions → Repository permissions → **Contents: Read and write**. Se copia el token en un archivo `github_token.txt` en la carpeta del `.bat`. Cuando vence, se genera otro y se reemplaza el archivo.
- **Apagarlo:** `$SUBIR_REPO = $false` en los ajustes.
- **Leerla desde una sesión de Claude** (sin cambiar de rama):

  ```bash
  git fetch origin datos-erp
  git show FETCH_HEAD:LEEME.md
  git show FETCH_HEAD:ITT/precios.tsv | head
  ```

  Para trabajar con los archivos: `git worktree add ../datos-erp FETCH_HEAD`.

## Ajustes (arriba de `cruce_erp.ps1`)

- `$EMPRESAS`: las bases que se leen.
- `$MESES_ATRAS = 12`: meses de SC, OC y remitos.
- `$MESES_VENTAS = 24`: meses de pedidos de clientes (NV).
- `$FORMULAS = 'ITT2[5-9]-%'`: productos cuyas fórmulas se leen. También se leen las de todo artículo vendido en el período de ventas.

## Cómo pasan los datos

1. `Leer` corre cada consulta y la guarda como texto TSV: tabulador entre columnas y `\n` entre filas. Los tabuladores y saltos de los textos se cambian por espacio. Los números van con punto decimal y sin miles. Las fechas van como `yyyy-MM-dd`. NULL queda vacío.
2. Con todo eso se arma `window.DATOS_ERP = {fecha, desde, err, emp: [{nombre, sc, oc, rem, pr, vt, fl}, …]}`, que **reemplaza exactamente** `<script>/*DATOS_ERP*/</script>` de la plantilla. Si ese marcador cambia, la página queda sin datos y no avisa.
3. En la página, `Cruce.desdeERP` reparte cada bloque con `desdeERP1(bloque, empresa)`. Lee **por posición de columna**, así que el orden del `SELECT` y los índices `r[n]` del JS tienen que coincidir.

### Columnas de cada bloque (índice → campo en la página)

- **`sc`**, solicitudes (`SolicitudCompraCab/Det`, `Articulo`, `UnidadMedida`, `CentrosCostos`, `Usuarios`, `ConceptoOperacion`):
  - 0 N° SC (módulo 1.000.000) · 1 fecha · 2 comentario · 3 centro de costo
  - 4 baja (se descarta) · 5 final · 6 usuario que ingresó · 7 usuario que autorizó
  - 8 id del renglón · 9 código · 10 descripción (la del renglón si la usa, si no la del artículo) · 11 unidad
  - 12 cantidad pedida · 13 autorizada · 14 en OC según el sistema · 15 fecha límite · 16 rechazado · 17 concepto (sector)
- **`oc`**, órdenes de compra (`OrdenCompraCab/Det`, `Proveedor`, `Comprador`, `Usuarios`, `Moneda`, `CentrosCostos`):
  - 0 N° OC · 1 fecha · 2 código del proveedor · 3 proveedor · 4 comentario · 5 baja (se descarta)
  - 6 autorización técnica (usuario) · 7 fecha de autorización · 8 autorización de importe (usuario) · 9 total · 10 comprador
  - 11 id del renglón (une con los remitos) · 12 código · 13 descripción · 14 unidad · 15 cantidad · 16 recibido · 17 final
  - 18 entrega · 19 precio · 20 importe · 21 moneda · 22 centro de costo · 23 comentario del renglón
  - 24 cotización del renglón · 25 cotización de la cabecera
- **`rem`**, remitos de proveedor: 0 id del renglón de OC · 1 N° de remito · 2 fecha.
- **`pr`**, últimos 3 precios de cada artículo, sin límite de fecha, sin OC de baja y con cantidad e importe > 0:
  - 0 código · 1 fecha · 2 N° OC · 3 proveedor · 4 cantidad · 5 importe · 6 moneda
  - 7 cotización del renglón · 8 cotización de la cabecera · 9 descripción · 10 unidad · 11 orden (1 = el último)
- **`vt`**, pedidos de clientes o NV (`PedidoClteCab/Det`, `Cliente`):
  - 0 N° NV · 1 fecha · 2 cliente · 3 OC del cliente · 4 código · 5 descripción · 6 cantidad · 7 precio · 8 importe · 9 moneda
  - 10 cotización del renglón · 11 cotización de la cabecera · 12 entrega · 13 entregado
  - 14 tiene fórmula (1/0) · 15 leyenda · 16 N° de ítem
- **`fl`**, fórmulas (`FormulaArticuloCab/Det`, `ProduccionProcesos`; recursiva hasta 6 niveles, se toma la fórmula de número menor y la cantidad va por unidad del producto):
  - 0 código del producto · 1 descripción del producto · 2 nivel · 3 etapa · 4 código del componente · 5 descripción
  - 6 unidad · 7 cantidad por unidad · 8 `SE` (tiene fórmula propia) o `MP` · 9 proceso · 10 ruta de ids (`a/b/c`)

## Qué muestra la página

- **Artículos pedidos y Solicitudes:** cada renglón de SC se une con las OC que citan "SC nnnn" o "NV nnnn" en el comentario (`scsDe`, que también entiende "SC 2693, 94 y 95"). Primero busca el mismo código. Si no lo encuentra, toma las primeras 5 palabras iguales de la descripción y lo marca "Probable". Con datos del sistema, la cantidad en OC que registra la base manda aunque la OC no cite la SC.
- **Órdenes de compra:** recibido, remitos e importe en USD. Si la moneda no es dólar, divide por la cotización de la OC o por la de la OC más cercana en fecha.
- **Fórmulas vs SC-OC:** lo que falta pedir para cada fórmula. Con "Solo SC del mismo proyecto", solo cuenta las SC que nombran la NV de la fórmula, que sale de los 3 dígitos de `ITTaa-n-NNN`.
- **Equipos vendidos:** precio de venta contra costo de materiales por NV. El costo es el de la fórmula (`costoFormula`): si una pieza tiene precio de compra, se usa ese precio y no se abren sus partes; si no, se suman sus partes.
- **Cotizador:** el último costo de cada código con su variación contra el anterior. Se arma una cotización con margen % y se exporta a Excel interno o para el cliente. Las cotizaciones quedan en el `localStorage` de ese navegador (`cruceSCOC_cotizador_v1`).

## Diferencias con las reglas del cotizador del repositorio

Antes de usar estos datos en el cotizador hay que resolver estas diferencias:

1. **Dólar:** usa la cotización de la OC. El cotizador usa el promedio mensual BNA venta (`conocimiento/costos/dolar_mensual.csv`), salvo que el documento diga otro tipo de cambio. La cotización de la OC sería ese caso, pero hay que decidirlo.
2. **Precio de venta:** usa costo × (1 + margen %), sin los factores 1,35 / 1,40 ni los estados borrador → revisado → aprobado. El Excel "para el cliente" no dice "borrador, sin revisar".
3. **Formatos:** las fechas salen DD/MM/AAAA y no DD-MM-AAAA. Los números a la vista no siempre van como 1.234,56.
4. **IVA:** toma los importes de la OC como sin IVA. No está comprobado que `ImpoTotal_OrdCpDet` venga sin IVA en todos los casos.
5. **Cotización usada:** en `pr` manda la de la cabecera y en `vt` la del renglón. No está claro si es a propósito.

## Cómo modificarla sin romperla

- **Solo `SELECT`.** Nunca `INSERT`, `UPDATE`, `DELETE`, `EXEC` ni tablas temporales: el usuario es `sa`.
- **Columnas nuevas, siempre al final del `SELECT`**, para no correr los índices. Después se lee la nueva `r[n]` en `desdeERP1`.
- **Bloque nuevo:** sumarlo en `LeerEmpresa` (return), en la línea `$partes += …` del armado, en `$BLOQUES` (archivo y encabezados para el repositorio) y en `desdeERP1`/`desdeERP` de la página. Si se agrega una columna, sumar también su encabezado en `$BLOQUES`.
- **No tocar el marcador** `<script>/*DATOS_ERP*/</script>`.
- **Mantener CRLF y el BOM del `.ps1`.** Editar con Python leyendo y escribiendo bytes, o con Edit, y comprobar después con `file`.
- **Prueba acá, sin la base:** generar una copia de la plantilla con un `DATOS_ERP` de prueba (TSV inventado con las mismas columnas), abrirla con Playwright y comprobar que no hay errores en la consola y que las vistas cargan. El SQL nuevo solo se prueba en ITT: Matías corre `ACTUALIZAR.bat` y manda lo que muestra la ventana; el script lista los errores de cada lectura y sigue con las demás.

## Pendientes

- Probar la subida en la PC de ITT: el script no se pudo correr fuera de ITT (no hay PowerShell en el entorno de Claude) y se revisó solo leyéndolo. Si falla, pasar el texto de la ventana.

- Usuario de solo lectura en SQL Server y cambio de la contraseña de `sa` (Sistemas de ITT).
- Decidir si el historial de precios (`pr`, o una exportación más larga) pasa al catálogo de materiales (`buscar_material.py`) como fuente con fecha, OC y proveedor, convertido con el dólar BNA mensual.
- Resolver las diferencias de arriba si la herramienta se va a usar para cotizar al cliente.
