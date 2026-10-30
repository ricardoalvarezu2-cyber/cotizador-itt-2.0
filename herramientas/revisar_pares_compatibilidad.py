"""Pares pedido–candidato que cambian de compatible a incompatible (o al revés) entre una versión anterior de las reglas
y la actual (tercera auditoría, 30-10-2026: cada corrección que amplió lo que se lee abrió falsos aceptados que nadie
buscó). Solo informa.

Uso: python herramientas/revisar_pares_compatibilidad.py [--ref main] [--salida archivo.md] [--control | --aceptar]
     --control (lo corre verificar_todo.py contra HEAD): falla si hay nuevos aceptados sin revisar.
     --aceptar: los anota como revisados en conocimiento/tecnico/pares_aceptados_revisados.json (solo después de revisar
     cada uno y anotar el motivo en compatibilidades_LEEME.md).
     Compara compatibilidad.incompatible de --ref (código y tabla compatibilidad_materiales.csv de esa versión) con el de
     ahora, en todos los renglones de cotizaciones/*/pedido/lista_materiales_plano.csv contra los primeros 60 candidatos
     de su familia y 90 al azar (fijos). Los NUEVOS ACEPTADOS se revisan uno por uno antes de subir un cambio de reglas
     (conocimiento/tecnico/compatibilidades_LEEME.md, "Para sumar reglas").
"""
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
REVISADOS = RAIZ / "conocimiento" / "tecnico" / "pares_aceptados_revisados.json"

SONDA = r"""
import json, random, sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
import compatibilidad as cp
if len(sys.argv) > 3:
    cp.TABLA = Path(sys.argv[3])
import buscar_material as bm, precotizar as pc
bm.buscar("brida")
filas = bm._FILAS
out = []
for f in sorted(Path(sys.argv[2]).glob("cotizaciones/*/pedido/lista_materiales_plano.csv")):
    for r in pc.leer(f):
        t = pc.texto_busqueda(r)
        fam, at, *_ = bm.buscar(t)
        todos = [c for c in filas if bm.NOMBRE_A_COD.get(c["familia"]) == fam]
        cands = todos[:60] + random.Random(f"{f.parent.parent.name}{r.get('pos')}").sample(todos[60:], min(90, len(todos[60:])))
        for c in cands:
            out.append([f.parent.parent.name, r.get("pos", ""), t[:110], c["codigo"], c["descripcion"][:90],
                        cp.incompatible(fam, at, c, t, c["descripcion"])])
print(json.dumps(out, ensure_ascii=False))
"""


def correr(dir_herr, tabla=None):
    args = [sys.executable, "-c", SONDA, str(dir_herr), str(RAIZ)] + ([str(tabla)] if tabla else [])
    r = subprocess.run(args, cwd=RAIZ, capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"Falló con {dir_herr}:\n{r.stderr[-1500:]}")
    return json.loads(r.stdout.strip().splitlines()[-1])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ref", default="main")
    ap.add_argument("--salida")
    ap.add_argument("--control", action="store_true", help="falla si hay nuevos aceptados que no estén revisados")
    ap.add_argument("--aceptar", action="store_true", help="anota los nuevos aceptados como revisados (después de revisarlos)")
    a = ap.parse_args()
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        arch = subprocess.run(["git", "archive", a.ref, "herramientas", "conocimiento/tecnico/compatibilidad_materiales.csv"],
                              cwd=RAIZ, capture_output=True)
        if arch.returncode:
            sys.exit(f"No se pudo leer {a.ref}: {arch.stderr.decode()[-300:]}")
        subprocess.run(["tar", "-x", "-C", str(tmp)], input=arch.stdout, check=True)
        tabla_vieja = tmp / "conocimiento" / "tecnico" / "compatibilidad_materiales.csv"
        for d in (RAIZ / "conocimiento").iterdir():  # el resto de los datos, los de ahora
            if not (tmp / "conocimiento" / d.name).exists():
                (tmp / "conocimiento" / d.name).symlink_to(d)
        for d in (RAIZ / "conocimiento" / "tecnico").iterdir():
            if not (tmp / "conocimiento" / "tecnico" / d.name).exists():
                (tmp / "conocimiento" / "tecnico" / d.name).symlink_to(d)
        (tmp / "fuentes_originales").symlink_to(RAIZ / "fuentes_originales")
        # el resto de los datos (catálogo) es el de ahora: solo cambian las reglas
        antes = correr(tmp / "herramientas", tabla_vieja)
    ahora = correr(RAIZ / "herramientas")
    acept, rech = [], []
    for x, y in zip(antes, ahora):
        if bool(x[5]) == bool(y[5]):
            continue
        (acept if x[5] and not y[5] else rech).append((x, y))
    lin = [f"# Pares que cambian: reglas de {a.ref} → ahora", "",
           f"**{len(acept)} nuevos aceptados** (revisar uno por uno: ¿la norma permite ese reemplazo?) · {len(rech)} nuevos rechazados.", "",
           "## Nuevos aceptados", ""]
    lin += [f"- {x[0]} pos {x[1]} · {x[2]}\n  ← {x[3]} {x[4]}\n  antes: {x[5]}" for x, _ in acept]
    lin += ["", "## Nuevos rechazados", ""]
    lin += [f"- {x[0]} pos {x[1]} · {x[2][:70]} ← {x[3]} {x[4][:60]}: {y[5][:120]}" for x, y in rech]
    texto = "\n".join(lin) + "\n"
    revisados = json.loads(REVISADOS.read_text(encoding="utf-8")) if REVISADOS.exists() else {}
    clave = lambda x: f"{x[0]} · pos {x[1]} · {x[3]}"
    if a.aceptar:
        revisados.update({clave(x): "revisado" for x, _ in acept})
        REVISADOS.write_text(json.dumps(revisados, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        print(f"{len(acept)} nuevos aceptados anotados como revisados → {REVISADOS.relative_to(RAIZ)}")
        return 0
    if a.control:
        sin = [clave(x) for x, _ in acept if clave(x) not in revisados]
        for k in sin[:20]:
            print("  nuevo aceptado sin revisar:", k)
        print(f"Pares nuevos aceptados contra {a.ref}: {len(acept)} ({len(sin)} sin revisar)")
        return 1 if sin else 0
    if a.salida:
        Path(a.salida).write_text(texto, encoding="utf-8")
    print(f"{len(acept)} nuevos aceptados · {len(rech)} nuevos rechazados" + (f" → {a.salida}" if a.salida else ""))
    if not a.salida:
        print(texto[:6000])


if __name__ == "__main__":
    sys.exit(main())
