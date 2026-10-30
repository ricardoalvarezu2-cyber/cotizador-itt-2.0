"""Sube el trabajo y lo pasa a main en un solo paso (regla de CLAUDE.md: todo trabajo termina en main, sin PR).

Uso: python herramientas/subir_a_main.py "Mensaje del commit" [--archivo-mensaje ruta]
     (el mensaje puede traer las líneas de atribución al final; con --archivo-mensaje se lee de un archivo)

Pasos: git add -A → commit (si hay cambios) → push de la rama → fetch de main → main avanza a la rama (fast-forward; si no
se puede, merge común) → push de main → vuelve a la rama. Nunca hace force-push. Si hay conflicto, se detiene sin tocar
main y lo dice (se resuelve con las reglas de siempre). No toca datos: es solo git.
"""
import argparse
import subprocess
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def git(*args, ok=False):
    r = subprocess.run(["git", *args], cwd=RAIZ, capture_output=True, text=True)
    if r.returncode and not ok:
        sys.exit(f"git {' '.join(args)} falló:\n{(r.stdout + r.stderr)[-1500:]}")
    return r


def push(*args):
    for espera in (0, 2, 4, 8, 16):  # reintentos solo por fallas de red
        time.sleep(espera)
        r = git("push", *args, ok=True)
        if not r.returncode:
            return
        if "rejected" in r.stderr or "non-fast-forward" in r.stderr:
            sys.exit(f"push rechazado (no se fuerza):\n{r.stderr[-800:]}")
    sys.exit(f"push falló tras reintentos:\n{r.stderr[-800:]}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mensaje", nargs="?")
    ap.add_argument("--archivo-mensaje")
    a = ap.parse_args()
    rama = git("rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    if rama == "main":
        sys.exit("Estás en main: trabajá en la rama de trabajo y corré esto desde ahí.")
    git("add", "-A")
    if git("diff", "--cached", "--quiet", ok=True).returncode:
        if not (a.mensaje or a.archivo_mensaje):
            sys.exit("Hay cambios para subir: falta el mensaje del commit.")
        git("commit", *(["-F", a.archivo_mensaje] if a.archivo_mensaje else ["-m", a.mensaje]))
    push("-u", "origin", rama)
    git("fetch", "origin", "main")
    git("checkout", "main")
    try:
        git("merge", "--ff-only", "origin/main")
        if git("merge", "--ff-only", rama, ok=True).returncode:
            r = git("merge", "--no-edit", rama, ok=True)
            if r.returncode:
                git("merge", "--abort", ok=True)
                sys.exit(f"Conflicto al pasar {rama} a main: no se tocó main. Resolverlo a mano.\n{r.stdout[-800:]}")
        push("origin", "main")
    finally:
        git("checkout", rama)
    print(f"Listo: {rama} subida y main en {git('rev-parse', '--short', 'origin/main').stdout.strip()}")


if __name__ == "__main__":
    main()
