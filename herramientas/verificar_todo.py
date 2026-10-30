"""Corre todos los controles del cotizador de una vez. Tiene que terminar en "TODO OK" antes de dar por bueno un cambio.

Uso: python herramientas/verificar_todo.py

1. Tests de regresión: catálogo de materiales, catálogo de servicios, precotización (CAPEX como caso de control) y
   errores sembrados (cada error ya cometido, metido en una copia de la CAPEX, tiene que frenarse).
2. Armado determinístico: dos corridas de cada catálogo dan el mismo CSV.
3. La cotización de control (CAPEX) se vuelve a armar: Python y planilla iguales, verificar_computo sin errores y
   el precio unitario igual al registrado en CONTROL (si cambia a propósito, actualizar CONTROL y anotar por qué).
4. Deja el repositorio como lo encontró: si solo se regeneraron archivos derivados (Excel, Word, PDF, HTML) que estaban
   sin cambios y no cambió ningún dato (CSV, JSON, MD), se restauran. Así el control no deja "cambios" de fechas internas
   que traban el git pull de la sesión de la tarea semanal (lección 43).
"""
import csv
import hashlib
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
H = RAIZ / "herramientas"
CAPEX = "cotizaciones/COT26-1003-001_CAPEX_OQ8209"
CONTROL = {"precio_unitario": "7.324,57"}  # 30-10-2026: pos 10 (BSPT por NPT) y 23 (otra serie y extremos) SIN PRECIO por compatibilidad; antes 7.366,12
fallas = []
sys.path.insert(0, str(H))
from candado import candado  # noqa: E402
_CANDADO = candado("verificar_todo.py")  # se guarda: si no, se libera enseguida
_CANDADO.__enter__()  # una corrida por vez; se libera al terminar el proceso (auditoría 29-10-2026)


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


def modificados():
    r = subprocess.run(["git", "diff", "--name-only", "-z", "HEAD"], cwd=RAIZ, capture_output=True, text=True)
    return set(x for x in r.stdout.split("\0") if x) if r.returncode == 0 else None  # -z: nombres con espacios y acentos


DERIVADOS = (".xlsx", ".docx", ".pdf", ".html")
antes = modificados()

for t in ("test_catalogo.py", "test_catalogo_servicios.py", "test_precotizar.py", "test_antecedentes.py", "test_compatibilidad.py",
          "test_errores_sembrados.py"):
    correr(t, [str(H / t)])
# índice de precios: se regenera siempre (auditoría 30-10-2026: quedaba viejo si no se corría actualizar_base.py)
correr("indice_precios.py", [str(H / "indice_precios.py")])
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
# motor de la página (JS) igual a Python: CAPEX y una cotización con válvulas Taval (factor aparte)
r = subprocess.run(["node", "web/probar_motor.js"], cwd=RAIZ, capture_output=True, text=True)
print(f"{'OK  ' if r.returncode == 0 else 'FALLA'} motor de la página (web/probar_motor.js)")
if r.returncode:
    fallas.append("motor JS distinto de Python")
    print((r.stdout + r.stderr)[-800:])
# modo detallado / global por rubro: página igual a Python (ficha_rubros.py)
r = subprocess.run(["node", "web/probar_rubros.js"], cwd=RAIZ, capture_output=True, text=True)
print(f"{'OK  ' if r.returncode == 0 else 'FALLA'} rubros detallado/global de la página (web/probar_rubros.js)")
if r.returncode:
    fallas.append("rubros JS distinto de Python")
    print((r.stdout + r.stderr)[-800:])
r = subprocess.run(["node", "web/probar_ficha.js"], cwd=RAIZ, capture_output=True, text=True)
print(f"{'OK  ' if r.returncode == 0 else 'FALLA'} ficha de la página igual a Python (web/probar_ficha.js)")
if r.returncode:
    fallas.append("ficha JS distinta de Python")
    print((r.stdout + r.stderr)[-800:])
# casos de control (precotización contra el costo real): el total de la app no puede moverse sin que alguien lo decida
import json  # noqa: E402
out = correr("casos de control (correr_controles.py)", [str(H / "correr_controles.py")])
esperado = json.loads((RAIZ / "cotizaciones" / "controles_esperado.json").read_text(encoding="utf-8"))["casos"]
movidos = []
for caso, app in esperado.items():
    m = re.search(rf"\| {re.escape(caso)} \| [\d.]+ \| ([\d.]+) \|", out)
    v = int(m.group(1).replace(".", "")) if m else None
    if v is None or abs(v - app) > max(1, 0.005 * app):
        movidos.append(f"{caso}: {v} (esperado {app})")
if movidos:
    fallas.append("casos de control movidos")
    print("FALLA casos de control: " + "; ".join(movidos) + ". Si es a propósito, actualizar cotizaciones/controles_esperado.json y anotar por qué.")
r = subprocess.run(["node", "web/probar_busqueda.js"], cwd=RAIZ, capture_output=True, text=True)
print(f"{'OK  ' if r.returncode == 0 else 'FALLA'} búsqueda y avisos de la página (web/probar_busqueda.js)")
if r.returncode:
    fallas.append("búsqueda de la página")
    print((r.stdout + r.stderr)[-800:])
# Compatibilidades (Matías, 30-10-2026): 1) el buscador da los resultados aceptados (un cambio de reglas o de catálogo se
# revisa renglón por renglón y se acepta a propósito); 2) ninguna cotización del repositorio usa una referencia que la
# norma no permite (el mismo control que verificar_computo.py hace en P9).
correr("resultados del buscador iguales a los aceptados (revisar_cambio_busqueda.py --control)", [str(H / "revisar_cambio_busqueda.py"), "--control"])
# tercera auditoría (30-10-2026): un cambio de reglas que amplía lo que se lee puede ACEPTAR reemplazos prohibidos
correr("pares de compatibilidad iguales a la línea base (revisar_pares_compatibilidad.py --control)",
       [str(H / "revisar_pares_compatibilidad.py"), "--control"])
import verificar_computo  # noqa: E402
incomp, a_confirmar = [], []
for carpeta in sorted((RAIZ / "cotizaciones").iterdir()):
    if (carpeta / "cotizacion.json").exists() and (carpeta / "pedido" / "lista_materiales_plano.csv").exists() and not carpeta.name.startswith("_"):
        plano = list(csv.DictReader(open(carpeta / "pedido" / "lista_materiales_plano.csv", encoding="utf-8")))
        est = json.load(open(carpeta / "cotizacion.json", encoding="utf-8")).get("estado", "borrador")
        for e in verificar_computo.control_compatibilidad(carpeta, plano):
            if e.startswith(verificar_computo.A_CONFIRMAR) and est == "borrador":
                a_confirmar.append(f"{carpeta.name}: {e[len(verificar_computo.A_CONFIRMAR):]}")
            else:  # un desvío a confirmar no frena un borrador, pero sí una cotización revisada o aprobada
                incomp.append(f"{carpeta.name}: {e}")
print(f"{'OK  ' if not incomp else 'FALLA'} referencias compatibles con la norma en todas las cotizaciones ({len(incomp)} problemas)")
if a_confirmar:
    print(f"     {len(a_confirmar)} desvíos de la oferta a confirmar en borradores (frenan el paso a revisado):")
    print("\n".join("       " + x[:150] for x in a_confirmar[:12]))
if incomp:
    fallas.append("cotizaciones con referencias incompatibles")
    print("\n".join("  " + x for x in incomp[:20]))
# Fichas (auditoría 30-10-2026): ninguna ficha consolidada tiene en sus ítems un precio que solo figura en documentos de
# proveedores (error de ALUAR/1; consolidar_fichas.py ya no las deja entrar, esto controla las que ya están).
import validar_fichas  # noqa: E402
mal = [f"{f.parent.name}/{f.name}: {x[len(validar_fichas.CRITICO):]}" for f in sorted((RAIZ / "conocimiento").glob("fichas_*/*.json"))
       for x in validar_fichas.criticos(validar_fichas.validar(json.load(open(f, encoding="utf-8")))) if "documentos de proveedores" in x]
print(f"{'OK  ' if not mal else 'FALLA'} fichas sin precios de proveedor en los ítems ({len(mal)} problemas)")
if mal:
    fallas.append("fichas con precios de proveedor en los ítems")
    print("\n".join("  " + x for x in mal[:20]))
# Frenos de la oferta (proceso unificado, 30-10-2026): no fallan el control (son de cada cotización), se informan para que
# se vea qué le falta a cada una antes de generar ofertas.
import contextlib  # noqa: E402
import io  # noqa: E402
import frenos  # noqa: E402
print("Frenos de la oferta por cotización (informativo):")
for carpeta in sorted((RAIZ / "cotizaciones").iterdir()):
    if carpeta.name.startswith("COT") and (carpeta / "cotizacion.json").exists():
        with contextlib.redirect_stdout(io.StringIO()):
            fr = frenos.frenos(carpeta)
        print(f"  {carpeta.name}: " + (", ".join(k for k, _ in fr) if fr else "sin frenos"))
despues = modificados()
if antes is not None and despues is not None:
    nuevos = sorted(despues - antes)
    if nuevos and all(f.endswith(DERIVADOS) for f in nuevos):
        subprocess.run(["git", "checkout", "--"] + nuevos, cwd=RAIZ, check=False)
        print(f"Restaurados {len(nuevos)} archivos derivados que solo cambiaron por regenerarse (sin cambios de datos)")
    elif nuevos and not fallas:
        print(f"Cambiaron datos: quedan {len(nuevos)} archivos modificados para revisar y subir")
    elif nuevos:
        print(f"Cambiaron {len(nuevos)} archivos, pero el control FALLÓ: no subir nada hasta corregirlo")
print("\nTODO OK" if not fallas else f"\nFALLAN {len(fallas)}: {', '.join(fallas)}")
sys.exit(1 if fallas else 0)
