@echo off
cd /d "%~dp0"
set "CRUCE_DIR=%~dp0"
rem Corre el script como texto: asi Windows no muestra la advertencia de seguridad (archivo bajado de Internet o en unidad de red).
powershell -NoProfile -ExecutionPolicy Bypass -Command "$f = Join-Path $env:CRUCE_DIR 'cruce_erp.ps1'; Get-ChildItem -LiteralPath $env:CRUCE_DIR -File | Unblock-File -ErrorAction SilentlyContinue; & ([scriptblock]::Create([IO.File]::ReadAllText($f)))"
