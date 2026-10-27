#!/usr/bin/env bash
# Instala el entorno del Cotizador ITT en un entorno virtual local (.venv)
set -euo pipefail
cd "$(dirname "$0")"
python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "Listo. Activar con: source .venv/bin/activate"
