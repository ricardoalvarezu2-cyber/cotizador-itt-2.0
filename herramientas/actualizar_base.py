"""Rearma toda la base en el orden correcto y después corre verificar_todo.py.

Uso: python herramientas/actualizar_base.py [--sin-red]

1. Dólar mensual (baja los datos diarios; con --sin-red usa la copia del repo) e índices de inflación.
   Si el mes nuevo necesita IPC o CPI, primero sumar el dato con su fuente en indices_inflacion.py.
2. Índice de precios, planillas de costo unidas, catálogo de materiales y catálogo de servicios.
3. Índice de proyectos (antecedentes).
4. verificar_todo.py: si algo falla, no dar por buena la actualización.
"""
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
H = RAIZ / "herramientas"
pasos = [["dolar_mensual.py"] + (["--sin-red"] if "--sin-red" in sys.argv else []), ["indices_inflacion.py"], ["indice_precios.py"],
         ["unir_planillas_costo.py"], ["catalogo_materiales.py"], ["catalogo_servicios.py"], ["indice_proyectos.py"], ["pesos_valvulas.py"]]
for p in pasos:
    print(f"→ {' '.join(p)}")
    r = subprocess.run([sys.executable, str(H / p[0])] + p[1:], cwd=RAIZ)
    if r.returncode:
        sys.exit(f"ERROR en {p[0]}: se corta la actualización")
sys.exit(subprocess.run([sys.executable, str(H / "verificar_todo.py")], cwd=RAIZ).returncode)
