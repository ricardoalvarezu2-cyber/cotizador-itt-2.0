# Cruce SC - OC - Fórmulas leyendo directo de la base ITTSA (SOLO LECTURA: únicamente SELECT).
# Necesita en la misma carpeta: el archivo .udl de conexión y plantilla.html
# Genera "Cruce SC-OC (sistema).html", lo abre en el navegador y sube una copia de los datos al repositorio (rama datos-erp).

# ---------- Ajustes ----------
$EMPRESAS = @(                 # bases a leer: archivo de conexión .udl (en esta carpeta) y nombre de la base
  @{ nombre = 'ITT';   udl = 'ITTSA_ERP.udl'; base = 'ITTSA' },
  @{ nombre = 'TAVAL'; udl = 'Taval_ERP.udl'; base = 'Taval'; alt = 'ITTSA_ERP.udl' }   # alt: si no conecta, prueba la base Taval por el servidor de ITT
)
$MESES_ATRAS = 12           # cuántos meses hacia atrás leer solicitudes, órdenes y remitos
$FORMULAS    = 'ITT2[5-9]-%' # productos cuyas fórmulas se leen (códigos de proyecto ITT25..ITT29)
$MESES_VENTAS = 24          # cuántos meses hacia atrás leer pedidos de clientes (NV)
$SUBIR_REPO  = $true        # subir una copia de los datos al repositorio (rama datos-erp) después de abrir la planilla
$REPO        = 'ricardoalvarezu2-cyber/cotizador-itt-2.0'   # repositorio preferido (26-11-2026); tiene que ser PRIVADO
$RAMA_DATOS  = 'datos-erp'  # rama solo de datos: cada subida la reemplaza entera (no acumula historia)
$PERMITIR_PUBLICO = $true   # Matias, 26-11-2026: decide subir los datos aunque el repositorio sea publico. En $false, no sube si es publico.
$TOKEN_ARCH  = 'github_token.txt'   # token de GitHub en esta carpeta (no se sube; ver herramientas/erp/LEEME.md)
# ------------------------------

$ErrorActionPreference = 'Stop'
# ACTUALIZAR.bat lo corre como texto (sin la advertencia de seguridad de Windows) y pasa la carpeta en CRUCE_DIR
$carpeta = if ($env:CRUCE_DIR) { $env:CRUCE_DIR.TrimEnd('\') } elseif ($PSCommandPath) { Split-Path -Parent $PSCommandPath } else { (Get-Location).Path }
$plantilla = Join-Path $carpeta 'plantilla.html'
$salida = Join-Path $carpeta 'Cruce SC-OC (sistema).html'
if (-not (Test-Path $plantilla)) { Write-Host "Falta plantilla.html en $carpeta" -ForegroundColor Red; Read-Host "Enter para salir"; exit }
Add-Type -AssemblyName System.Web
$inv = [System.Globalization.CultureInfo]::InvariantCulture
$desde = (Get-Date).AddMonths(-$MESES_ATRAS)
$desdeSQL = $desde.ToString('yyyyMMdd')
$desdeVentasSQL = (Get-Date).AddMonths(-$MESES_VENTAS).ToString('yyyyMMdd')
$errores = @()

$BLOQUES = [ordered]@{
  sc  = @{ arch = 'solicitudes.tsv';    enc = 'N_SC','Fecha','Comentario','Centro_costo','Baja','Final','Usuario_ingreso','Usuario_autorizo','Id_renglon','Codigo','Descripcion','Unidad','Cant_pedida','Cant_autorizada','Cant_en_OC','Fecha_limite','Rechazado','Concepto' }
  oc  = @{ arch = 'ordenes_compra.tsv'; enc = 'N_OC','Fecha','Cod_proveedor','Proveedor','Comentario','Baja','Aut_tecnica','Fecha_aut','Aut_importe','Total','Comprador','Id_renglon','Codigo','Descripcion','Unidad','Cantidad','Recibido','Final','Entrega','Precio','Importe','Moneda','Centro_costo','Comentario_renglon','Cotiz_renglon','Cotiz_cabecera' }
  rem = @{ arch = 'remitos.tsv';        enc = 'Id_renglon_OC','N_remito','Fecha' }
  pr  = @{ arch = 'precios.tsv';        enc = 'Codigo','Fecha','N_OC','Proveedor','Cantidad','Importe','Moneda','Cotiz_renglon','Cotiz_cabecera','Descripcion','Unidad','Orden' }
  vt  = @{ arch = 'ventas_nv.tsv';      enc = 'N_NV','Fecha','Cliente','OC_cliente','Codigo','Descripcion','Cantidad','Precio','Importe','Moneda','Cotiz_renglon','Cotiz_cabecera','Entrega','Entregado','Tiene_formula','Leyenda','Item' }
  fl  = @{ arch = 'formulas.tsv';       enc = 'Producto','Desc_producto','Nivel','Etapa','Componente','Desc_componente','Unidad','Cant_por_unidad','Tipo_SE_MP','Proceso','Ruta' }
}

# Sube los archivos a la rama $RAMA_DATOS con un solo commit nuevo (sin padre) que reemplaza al anterior.
# Usa la API de GitHub, así que no hace falta tener git instalado.
function SubirRepo($archivos, $mensaje) {
  $rutaTok = Join-Path $carpeta $TOKEN_ARCH
  if (-not (Test-Path $rutaTok)) {
    # Bloc de notas suele guardarlo como github_token.txt.txt
    $otro = Get-ChildItem -LiteralPath $carpeta -Filter 'github_token*' -File -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($otro) { $rutaTok = $otro.FullName }
    else {
      Write-Host ""
      Write-Host "Falta el token de GitHub (se pide una sola vez; ver LEEME.txt para crearlo)." -ForegroundColor Yellow
      $nuevo = (Read-Host "Pega el token (empieza con github_pat_) y Enter, o solo Enter para no subir") -replace '\s', ''
      if (-not $nuevo) { throw "no se cargo el token: no se subio la copia" }
      [System.IO.File]::WriteAllText($rutaTok, $nuevo, (New-Object System.Text.UTF8Encoding($false)))
      Write-Host ("  Token guardado en " + $rutaTok) -ForegroundColor Green
    }
  }
  $tok = ((Get-Content -LiteralPath $rutaTok -Raw) -replace '\s', '')
  if ($tok -notmatch '^(github_pat_|ghp_)') { throw ("el archivo " + (Split-Path -Leaf $rutaTok) + " no tiene un token de GitHub (tiene que empezar con github_pat_)") }
  [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
  $h = @{ Authorization = "Bearer $tok"; Accept = 'application/vnd.github+json'; 'X-GitHub-Api-Version' = '2022-11-28'; 'User-Agent' = 'cruce-erp-itt' }
  $api = "https://api.github.com/repos/$REPO/git"
  # Freno: los datos de compras y ventas nunca van a un repositorio publico.
  try { $info = Invoke-RestMethod -Uri "https://api.github.com/repos/$REPO" -Headers $h -TimeoutSec 60 }
  catch { throw ("no pude entrar al repositorio " + $REPO + " (revisar que el token sea de esa cuenta y tenga acceso a ese repositorio): " + $_.Exception.Message) }
  if (-not $info.private -and $PERMITIR_PUBLICO) { Write-Host ("  Aviso: " + $REPO + " es PUBLICO; los datos quedan visibles para cualquiera (decision de Matias, 26-11-2026).") -ForegroundColor Yellow }
  elseif (-not $info.private) { throw ("el repositorio " + $REPO + " es PUBLICO: no se suben los datos. Pasarlo a privado en GitHub (Settings > General > Danger Zone > Change visibility) y volver a correr.") }
  $post = {
    param($url, $json, $metodo)
    if (-not $metodo) { $metodo = 'Post' }
    Invoke-RestMethod -Uri $url -Method $metodo -Headers $h -ContentType 'application/json; charset=utf-8' -Body ([System.Text.Encoding]::UTF8.GetBytes($json)) -TimeoutSec 900
  }
  $arbol = @()
  foreach ($k in $archivos.Keys) {
    $bytes = $archivos[$k]
    Write-Host ("  Subiendo " + $k + " (" + [math]::Round($bytes.Length / 1MB, 1) + " MB)...")
    if ($bytes.Length -gt 90MB) { Write-Host "    Muy grande para GitHub, no se sube" -ForegroundColor Yellow; continue }
    $b = & $post "$api/blobs" ('{"encoding":"base64","content":"' + [Convert]::ToBase64String($bytes) + '"}')
    $arbol += @{ path = $k; mode = '100644'; type = 'blob'; sha = $b.sha }
  }
  $t = & $post "$api/trees" (ConvertTo-Json @{ tree = $arbol } -Depth 5 -Compress)
  $c = & $post "$api/commits" (ConvertTo-Json @{ message = $mensaje; tree = $t.sha; parents = @() } -Compress)
  $existe = $true
  try { [void](Invoke-RestMethod -Uri "$api/ref/heads/$RAMA_DATOS" -Headers $h -TimeoutSec 60) } catch { $existe = $false }
  if ($existe) { [void](& $post "$api/refs/heads/$RAMA_DATOS" (ConvertTo-Json @{ sha = $c.sha; force = $true } -Compress) 'Patch') }
  else { [void](& $post "$api/refs" (ConvertTo-Json @{ ref = "refs/heads/$RAMA_DATOS"; sha = $c.sha } -Compress)) }
}

function Leer($nombre, $sql) {
  Write-Host ("  " + $script:empActual + ": leyendo " + $nombre + "...") -NoNewline
  $sb = New-Object System.Text.StringBuilder
  try {
    $cmd = $script:cn.CreateCommand(); $cmd.CommandText = $sql; $cmd.CommandTimeout = 300
    $rd = $cmd.ExecuteReader(); $n = 0
    while ($rd.Read()) {
      $vals = New-Object string[] $rd.FieldCount
      for ($i = 0; $i -lt $rd.FieldCount; $i++) {
        $v = $rd.GetValue($i)
        if ($v -is [DBNull]) { $s = '' }
        elseif ($v -is [decimal] -or $v -is [double] -or $v -is [single]) { $s = ([decimal]$v).ToString('0.######', $inv) }
        elseif ($v -is [datetime]) { $s = $v.ToString('yyyy-MM-dd') }
        else { $s = ([string]$v) -replace "[`t`r`n]+", ' ' }
        $vals[$i] = $s.Trim()
      }
      [void]$sb.Append(($vals -join "`t")).Append("`n"); $n++
    }
    $rd.Close()
    Write-Host (" " + $n + " filas") -ForegroundColor Green
  } catch {
    Write-Host " ERROR" -ForegroundColor Red
    Write-Host ("    " + $_.Exception.Message) -ForegroundColor Red
    $script:errores += ($script:empActual + ' - ' + $nombre + ': ' + $_.Exception.Message)
  }
  return $sb.ToString()
}

function LeerEmpresa($emp) {
  Write-Host ""
  Write-Host ("=== " + $emp.nombre + " (base " + $emp.base + ") ===") -ForegroundColor Cyan
  $opciones = @($emp.udl); if ($emp.alt) { $opciones += $emp.alt }
  $conectado = $false; $ultimoError = ''
  foreach ($arch in $opciones) {
    $ruta = Join-Path $carpeta $arch
    if (-not (Test-Path $ruta)) { $ultimoError = 'falta el archivo ' + $arch; continue }
    try {
      Write-Host ("  Conectando con " + $arch + "...")
      $script:cn = New-Object System.Data.OleDb.OleDbConnection("File Name=$ruta")
      $script:cn.Open()
      $u = $script:cn.CreateCommand(); $u.CommandText = "USE [" + $emp.base + "]"; [void]$u.ExecuteNonQuery()
      $conectado = $true; Write-Host ("  Conectado (" + $arch + ")") -ForegroundColor Green; break
    } catch {
      $ultimoError = $_.Exception.Message
      Write-Host ("  No conecto con " + $arch + ": " + $ultimoError) -ForegroundColor Yellow
    }
  }
  if (-not $conectado) {
    Write-Host ("  No pude conectar a " + $emp.nombre) -ForegroundColor Red
    $script:errores += ($emp.nombre + ': no pude conectar (' + $ultimoError + ')'); return $null
  }
  $script:empActual = $emp.nombre
  $sc = Leer 'solicitudes de compra' @"
SELECT CAST(c.Numero_SoliCab AS bigint) % 1000000, c.Fecha_SoliCab, c.Comentario_SoliCab, cc.DescrCtroCosto,
 c.Baja_SoliCab, c.Final_SoliCab, ui.Usuario, ua.Usuario,
 d.Regis_SoliDet, a.CodInternoArti,
 CASE WHEN d.UsoDescri_SoliDet = 0 OR d.DescripcionArti_SoliDet IS NULL OR d.DescripcionArti_SoliDet = '' THEN a.DescripcionArti ELSE d.DescripcionArti_SoliDet END,
 um.DescrUniMed, d.CantSoli1_SoliDet, d.CantAuto1_SoliDet, d.CantOCpra1_SoliDet, d.FechaLimite_SoliDet, d.Rechazado_SoliDet, co.DescrConceOpe
FROM SolicitudCompraDet d
JOIN SolicitudCompraCab c ON c.Regis_SoliCab = d.Regis_SoliCab
LEFT JOIN Articulo a ON a.Regis_Arti = d.Regis_Arti
LEFT JOIN UnidadMedida um ON um.Regis_UniMed = a.Regis_UniMedPri
LEFT JOIN CentrosCostos cc ON cc.Regis_CCo = c.Regis_CCo
LEFT JOIN Usuarios ui ON ui.Regis_Usu = c.Regis_UsuIng
LEFT JOIN Usuarios ua ON ua.Regis_Usu = c.Regis_UsuAuto
LEFT JOIN ConceptoOperacion co ON co.Regis_ConceOpe = d.Regis_ConceOpe
WHERE c.Fecha_SoliCab >= '$desdeSQL'
ORDER BY c.Numero_SoliCab, d.Regis_SoliDet
"@

  $oc = Leer 'ordenes de compra' @"
SELECT o.Numero_OrdCpCab, o.Fecha_OrdCpCab, p.CodigoProve, p.RazonSocialProve, o.Comentario_OrdCpCab, o.Baja_OrdCpCab,
 ut.Usuario, o.FecAut_OrdCpCab, um2.Usuario, o.Total_OrdCpCab, cp.NombreCprador,
 d.Regis_OrdCpDet, a.CodInternoArti,
 CASE WHEN d.UsoDescri_OrdCpDet = 0 OR d.DescripcionArti_OrdCpDet IS NULL OR d.DescripcionArti_OrdCpDet = '' THEN a.DescripcionArti ELSE d.DescripcionArti_OrdCpDet END,
 um.DescrUniMed, d.Cant1_OrdCpDet, d.CanRec1_OrdCpDet, d.Final_OrdCpDet, d.FechaEntrega_OrdCpDet, d.PrFinal_OrdCpDet, d.ImpoTotal_OrdCpDet,
 m.Descr_Mda, cc.DescrCtroCosto, d.Comentario_OrdCpDet, d.Cotizacion_OrdCpDet, o.CotizMda1_OrdCpCab
FROM OrdenCompraDet d
JOIN OrdenCompraCab o ON o.Regis_OrdCpCab = d.Regis_OrdCpCab
LEFT JOIN Proveedor p ON p.Regis_Prove = o.Regis_Prove
LEFT JOIN Comprador cp ON cp.Regis_Cprador = o.Regis_Cprador
LEFT JOIN Usuarios ut ON ut.Regis_Usu = o.RegUsuAut_OrdCpCab
LEFT JOIN Usuarios um2 ON um2.Regis_Usu = o.RegUsuAutImp_OrdCpCab
LEFT JOIN Articulo a ON a.Regis_Arti = d.Regis_Arti
LEFT JOIN UnidadMedida um ON um.Regis_UniMed = a.Regis_UniMedPri
LEFT JOIN Moneda m ON m.Regis_Mda = d.Regis_Mda
LEFT JOIN CentrosCostos cc ON cc.Regis_CCo = d.Regis_CCo
WHERE o.Fecha_OrdCpCab >= '$desdeSQL'
ORDER BY o.Numero_OrdCpCab, d.Regis_OrdCpDet
"@

  $rem = Leer 'remitos de proveedor' @"
SELECT d.Regis_OrdCpDet, CAST(c.NroComprob_RtoProveCab AS bigint), c.Fecha_RtoProveCab
FROM RemitoProveDet d JOIN RemitoProveCab c ON c.Regis_RtoProveCab = d.Regis_RtoProveCab
WHERE d.Regis_OrdCpDet IS NOT NULL AND c.Fecha_RtoProveCab >= '$desdeSQL'
"@

  $pr = Leer 'ultimos precios de cada articulo' @"
SELECT a.CodInternoArti, u.Fecha_OrdCpCab, u.Numero_OrdCpCab, p.RazonSocialProve, u.Cant1_OrdCpDet, u.ImpoTotal_OrdCpDet, m.Descr_Mda, u.Cotizacion_OrdCpDet, u.CotizMda1_OrdCpCab,
       a.DescripcionArti, um.DescrUniMed, u.n
FROM (
  SELECT d.Regis_Arti, o.Fecha_OrdCpCab, o.Numero_OrdCpCab, o.Regis_Prove, d.Cant1_OrdCpDet, d.ImpoTotal_OrdCpDet, d.Regis_Mda, d.Cotizacion_OrdCpDet, o.CotizMda1_OrdCpCab,
         ROW_NUMBER() OVER (PARTITION BY d.Regis_Arti ORDER BY o.Fecha_OrdCpCab DESC, d.Regis_OrdCpDet DESC) AS n
  FROM OrdenCompraDet d JOIN OrdenCompraCab o ON o.Regis_OrdCpCab = d.Regis_OrdCpCab
  WHERE o.Baja_OrdCpCab = 0 AND d.Cant1_OrdCpDet > 0 AND d.ImpoTotal_OrdCpDet > 0
) u
JOIN Articulo a ON a.Regis_Arti = u.Regis_Arti
LEFT JOIN UnidadMedida um ON um.Regis_UniMed = a.Regis_UniMedPri
LEFT JOIN Proveedor p ON p.Regis_Prove = u.Regis_Prove
LEFT JOIN Moneda m ON m.Regis_Mda = u.Regis_Mda
WHERE u.n <= 3
"@

  $vt = Leer 'pedidos de clientes (NV)' @"
SELECT CAST(c.Numero_PedCliCab AS bigint), c.Fecha_PedCliCab, cl.RazonSocialCli, c.OrdCpra_PedCliCab, a.CodInternoArti,
 CASE WHEN d.UsoDescri_PedCliDet = 0 OR d.Descripcion_PedCliDet IS NULL OR d.Descripcion_PedCliDet = '' THEN a.DescripcionArti ELSE d.Descripcion_PedCliDet END,
 d.CanPed1_PedCliDet, d.Precio_PedCliDet, d.Importe_PedCliDet, m.Descr_Mda, d.Cotiz_Mda, c.CotizMda1_PedCliCab, d.FecEntrega_PedCliDet, d.CanEnt1_PedCliDet,
 CASE WHEN EXISTS (SELECT 1 FROM FormulaArticuloCab z WHERE z.Regis_Arti = d.Regis_Arti) THEN 1 ELSE 0 END, c.Leye1_PedCliCab, d.NumeroItem_PedCliDet
FROM PedidoClteDet d
JOIN PedidoClteCab c ON c.Regis_PedCliCab = d.Regis_PedCliCab
LEFT JOIN Articulo a ON a.Regis_Arti = d.Regis_Arti
LEFT JOIN Cliente cl ON cl.Regis_Cli = c.Regis_Cli
LEFT JOIN Moneda m ON m.Regis_Mda = d.Regis_Mda
WHERE c.Fecha_PedCliCab >= '$desdeVentasSQL'
ORDER BY c.Numero_PedCliCab, d.Regis_PedCliDet
"@

  $fl = Leer 'formulas de proyectos y equipos vendidos' @"
WITH F AS (
  SELECT fc.Regis_ForArtiC, fc.Regis_Arti, CASE WHEN fc.Cantidad1_ForArtiC > 0 THEN fc.Cantidad1_ForArtiC ELSE 1 END AS base
  FROM FormulaArticuloCab fc
  WHERE fc.NroFormula_ForArtiC = (SELECT MIN(x.NroFormula_ForArtiC) FROM FormulaArticuloCab x WHERE x.Regis_Arti = fc.Regis_Arti)
), X AS (
  SELECT f.Regis_Arti AS raiz, 1 AS nivel, CAST(d.Etapa_ForArtiD AS varchar(10)) AS etapa, d.Regis_Arti AS comp,
         CAST(d.Cantidad1_ForArtiD / f.base AS decimal(18,6)) AS cant, d.Regis_ProdPro AS prpro,
         CAST(CAST(d.Regis_ForArtiD AS varchar(12)) AS varchar(300)) AS ruta
  FROM F f JOIN FormulaArticuloDet d ON d.Regis_ForArtiC = f.Regis_ForArtiC
  JOIN Articulo ar ON ar.Regis_Arti = f.Regis_Arti
  WHERE ar.CodInternoArti LIKE '$FORMULAS'
     OR f.Regis_Arti IN (SELECT pd.Regis_Arti FROM PedidoClteDet pd JOIN PedidoClteCab pc ON pc.Regis_PedCliCab = pd.Regis_PedCliCab WHERE pc.Fecha_PedCliCab >= '$desdeVentasSQL')
  UNION ALL
  SELECT x.raiz, x.nivel + 1, x.etapa, d.Regis_Arti, CAST(x.cant * d.Cantidad1_ForArtiD / f.base AS decimal(18,6)), d.Regis_ProdPro,
         CAST(x.ruta + '/' + CAST(d.Regis_ForArtiD AS varchar(12)) AS varchar(300))
  FROM X x JOIN F f ON f.Regis_Arti = x.comp JOIN FormulaArticuloDet d ON d.Regis_ForArtiC = f.Regis_ForArtiC
  WHERE x.nivel < 6
)
SELECT r.CodInternoArti, r.DescripcionArti, X.nivel, X.etapa, a.CodInternoArti, a.DescripcionArti, um.DescrUniMed, X.cant,
  CASE WHEN EXISTS (SELECT 1 FROM FormulaArticuloCab z WHERE z.Regis_Arti = X.comp) THEN 'SE' ELSE 'MP' END,
  pp.AbrevProdPro, X.ruta
FROM X
JOIN Articulo r ON r.Regis_Arti = X.raiz
JOIN Articulo a ON a.Regis_Arti = X.comp
LEFT JOIN UnidadMedida um ON um.Regis_UniMed = a.Regis_UniMedPri
LEFT JOIN ProduccionProcesos pp ON pp.Regis_ProdPro = X.prpro
ORDER BY r.CodInternoArti, X.etapa, X.nivel
OPTION (MAXRECURSION 10)
"@

  $script:cn.Close()
  return @{ nombre = $emp.nombre; sc = $sc; oc = $oc; rem = $rem; pr = $pr; vt = $vt; fl = $fl }
}

try {
  Write-Host ("Leyendo desde " + $desde.ToString('dd/MM/yyyy') + "...") -ForegroundColor Green
  $datosEmp = @()
  foreach ($e in $EMPRESAS) { $r = LeerEmpresa $e; if ($r) { $datosEmp += $r } }
  if ($datosEmp.Count -eq 0) { throw "No pude leer ninguna base." }

  $J = { param($s) [System.Web.HttpUtility]::JavaScriptStringEncode($s) }
  $partes = @()
  foreach ($d in $datosEmp) {
    $partes += ('{nombre: "' + (& $J $d.nombre) + '", sc: "' + (& $J $d.sc) + '", oc: "' + (& $J $d.oc) + '", rem: "' + (& $J $d.rem) + '", pr: "' + (& $J $d.pr) + '", vt: "' + (& $J $d.vt) + '", fl: "' + (& $J $d.fl) + '"}')
  }
  $datos = 'window.DATOS_ERP = {' +
    'fecha: "' + (& $J (Get-Date).ToString('dd/MM/yyyy HH:mm')) + '", ' +
    'desde: "' + (& $J $desde.ToString('dd/MM/yyyy')) + '", ' +
    'err: "' + (& $J ($errores -join ' | ')) + '", ' +
    'emp: [' + ($partes -join ', ') + ']};'
  $html = [System.IO.File]::ReadAllText($plantilla, [System.Text.Encoding]::UTF8)
  $html = $html.Replace('<script>/*DATOS_ERP*/</script>', '<script>' + $datos + '</script>')
  [System.IO.File]::WriteAllText($salida, $html, (New-Object System.Text.UTF8Encoding($false)))
  Write-Host ""
  Write-Host "LISTO. Abriendo la herramienta..." -ForegroundColor Green
  Start-Process $salida

  if ($SUBIR_REPO) {
    Write-Host ""
    Write-Host ("Subiendo copia al repositorio (rama " + $RAMA_DATOS + ")...") -ForegroundColor Cyan
    $subir = $true
    if ($errores.Count -gt 0) {
      Write-Host "Hubo errores de lectura: la copia del repositorio quedaria incompleta y reemplazaria la anterior." -ForegroundColor Yellow
      $subir = (Read-Host "Subir igual? (s/n)") -match '^[sS]'
    }
    if ($subir) {
      try {
        $u8 = New-Object System.Text.UTF8Encoding($false)
        $arch = [ordered]@{}
        $meta = @("# Datos del sistema (ERP) de ITT y Taval", "",
          "Generado por herramientas/erp/ACTUALIZAR.bat. Esta rama se reemplaza entera en cada subida: siempre tiene solo la ultima lectura.", "",
          ("- Leido: " + (Get-Date).ToString('dd-MM-yyyy HH:mm')),
          ("- SC, OC y remitos desde: " + $desde.ToString('dd-MM-yyyy') + " (" + $MESES_ATRAS + " meses)"),
          ("- Ventas (NV) desde: " + (Get-Date).AddMonths(-$MESES_VENTAS).ToString('dd-MM-yyyy') + " (" + $MESES_VENTAS + " meses)"),
          ("- Formulas: productos " + $FORMULAS + " y los vendidos en el periodo"),
          ("- PC: " + $env:COMPUTERNAME + " / usuario " + $env:USERNAME),
          ("- Errores: " + $(if ($errores.Count) { $errores -join ' | ' } else { 'ninguno' })), "",
          "| Empresa | Archivo | Filas |", "|---|---|---|")
        foreach ($d in $datosEmp) {
          foreach ($k in $BLOQUES.Keys) {
            $txt = ($BLOQUES[$k].enc -join "`t") + "`n" + $d[$k]
            $arch[$d.nombre + '/' + $BLOQUES[$k].arch] = $u8.GetBytes($txt)
            $meta += ('| ' + $d.nombre + ' | ' + $BLOQUES[$k].arch + ' | ' + ($d[$k].Split("`n").Where({ $_ -ne '' }).Count) + ' |')
          }
        }
        $arch['LEEME.md'] = $u8.GetBytes(($meta -join "`n") + "`n")
        $arch['Cruce SC-OC (sistema).html'] = [System.IO.File]::ReadAllBytes($salida)
        # GitHub Pages: la misma pagina como index.html (https://ricardoalvarezu2-cyber.github.io/cotizador-itt-2.0/)
        $arch['index.html'] = $arch['Cruce SC-OC (sistema).html']
        $arch['.nojekyll'] = [byte[]]@(10)
        SubirRepo $arch ("Datos ERP " + (Get-Date).ToString('dd-MM-yyyy HH:mm') + " (" + $env:COMPUTERNAME + ")")
        Write-Host "Copia subida al repositorio." -ForegroundColor Green
      } catch {
        Write-Host ("No pude subir la copia al repositorio: " + $_.Exception.Message) -ForegroundColor Red
        $errores += ('Subida al repositorio: ' + $_.Exception.Message)
      }
    } else { Write-Host "No se subio la copia." -ForegroundColor Yellow }
  }

  if ($errores.Count -gt 0) {
    Write-Host ""
    Write-Host "Hubo errores (ver arriba). Copialos y mandaselos a Claude." -ForegroundColor Yellow
    Read-Host "Enter para cerrar"
  } else { Start-Sleep -Seconds 3 }
} catch {
  Write-Host ("ERROR: " + $_.Exception.Message) -ForegroundColor Red
  Read-Host "Enter para cerrar"
}
