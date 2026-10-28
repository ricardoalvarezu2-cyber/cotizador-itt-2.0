"""Corre todos los controles del cotizador de una vez. Tiene que terminar en "TODO OK" antes de dar por bueno un cambio.

Uso: python herramientas/verificar_todo.py

1. Tests de regresión: catálogo de materiales, catálogo de servicios, precotización (CAPEX como caso de control).
2. Armado determinístico: dos corridas de cada catálogo dan el mismo CSV.
3. La cotización de control (CAPEX) se vuelve a armar: Python y planilla iguales, verificar_computo sin errores y
   el precio unitario igual al registrado en CONTROL (si cambia a propósito, actualizar CONTROL y anotar por qué).
"""
import hashlib
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
H = RAIZ / "herramientas"
CAPEX = "cotizaciones/COT26-1003-001_CAPEX_OQ8209"
CONTROL = {"precio_unitario": "7,620.59"}  # 28/10/2026: dólar promedio BNA, valores del cepo estimados, sin renglones de IVA
fallas = []


def correr(nombre, args):
    r = subprocess.run([sys.executable] + args, cwd=RAIZ, capture_output=True, text=True)
    ok = r.returncode == 0
    print(f"{'OK  ' if ok else 'FALLA'} {nombre}")
    if not ok:
        fallas.append(nombre)
        print((r.stdout + r.stderr)[-1500:])
    return r.stdout


def md5(p):
    return hashlib.md5((RAIZ / p).read_bytes()).hexdigest()


for t in ("test_catalogo.py", "test_catalogo_servicios.py", "test_precotizar.py"):
    correr(t, [str(H / t)])
for script, salida in (("catalogo_materiales.py", "conocimiento/precios/catalogo_materiales.csv"),
                       ("catalogo_servicios.py", "conocimiento/precios/catalogo_servicios.csv")):
    correr(script, [str(H / script)])
    a = md5(salida)
    correr(script + " (segunda corrida)", [str(H / script)])
    if md5(salida) != a:
        fallas.append(f"{script} no es determinístico")
        print(f"FALLA {script}: dos corridas dan distinto resultado")
out = correr("armar CAPEX (caso de control)", [str(H / "armar_cotizacion.py"), CAPEX])
m = re.search(r"Planilla: .*precio unitario ([\d,.]+)", out)
if not m or m.group(1) != CONTROL["precio_unitario"]:
    fallas.append("precio de control de la CAPEX")
    print(f"FALLA precio de control: dio {m.group(1) if m else '—'}, se esperaba {CONTROL['precio_unitario']}")
print("\nTODO OK" if not fallas else f"\nFALLAN {len(fallas)}: {', '.join(fallas)}")
sys.exit(1 if fallas else 0)
