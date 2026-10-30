"""Informe de cambios del buscador de materiales: qué renglones de las cotizaciones cambian de resultado entre una versión
anterior de las herramientas y la actual (solo informa; no cambia nada — Matías, 30-10-2026).

Uso: python herramientas/revisar_cambio_busqueda.py [--ref HEAD] [--salida archivo.md]
     --ref: versión de git contra la que se compara (por defecto HEAD, lo último guardado; ej. main, HEAD~1).

Para cada renglón de cotizaciones/*/pedido/lista_materiales_plano.csv busca con las herramientas de --ref y con las de
ahora (los dos con los datos actuales del catálogo) y lista los que cambian: antes / ahora / motivo de descarte si la
regla nueva lo descartó. Correrlo antes de subir cualquier cambio en buscar_material.py, compatibilidad.py o el catálogo
de reglas, y revisar cada cambio (lección del 30-10-2026: una regla mal hecha descartaba bridas iguales al pedido).
"""
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

SONDA = r"""
import json, sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
import buscar_material as bm, precotizar as pc
out = []
for f in sorted(Path(sys.argv[2]).glob("cotizaciones/*/pedido/lista_materiales_plano.csv")):
    for r in pc.leer(f):
        t = pc.texto_busqueda(r)
        fam, at, _, _, res = bm.buscar(t)
        x = res[0] if res else None
        out.append({"cot": f.parent.parent.name, "pos": r.get("pos", ""), "texto": t, "fam": fam,
                    "codigo": x[-1]["codigo"] if x else "", "desc": x[-1]["descripcion"][:80] if x else "",
                    "igual": bool(x and x[0]), "precio": x[-1]["ultimo_precio_usd"] if x else ""})
print(json.dumps(out, ensure_ascii=False))
"""


def correr(dir_herr):
    r = subprocess.run([sys.executable, "-c", SONDA, str(dir_herr), str(RAIZ)], cwd=RAIZ, capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"Falló la búsqueda con {dir_herr}:\n{r.stderr[-1500:]}")
    return json.loads(r.stdout.strip().splitlines()[-1])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ref", default="HEAD")
    ap.add_argument("--salida")
    a = ap.parse_args()
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        arch = subprocess.run(["git", "archive", a.ref, "herramientas"], cwd=RAIZ, capture_output=True)
        if arch.returncode:
            sys.exit(f"No se pudo leer {a.ref}: {arch.stderr.decode()[-300:]}")
        subprocess.run(["tar", "-x", "-C", str(tmp)], input=arch.stdout, check=True)
        (tmp / "conocimiento").symlink_to(RAIZ / "conocimiento")  # mismos datos: solo cambia el código
        (tmp / "fuentes_originales").symlink_to(RAIZ / "fuentes_originales")
        antes = correr(tmp / "herramientas")
    ahora = correr(RAIZ / "herramientas")
    sys.path.insert(0, str(RAIZ / "herramientas"))
    import buscar_material as bm
    from compatibilidad import incompatible
    bm.buscar("brida")
    por_cod = {r["codigo"]: r for r in bm._FILAS}
    lineas = [f"# Cambios del buscador de materiales: {a.ref} → ahora", "",
              "Generado por `herramientas/revisar_cambio_busqueda.py`. Revisar cada cambio antes de subir.", ""]
    n = 0
    for x, y in zip(antes, ahora):
        if x["codigo"] == y["codigo"]:
            continue
        n += 1
        motivo = ""
        if x["codigo"] in por_cod:
            _, at, *_ = bm.buscar(x["texto"])
            motivo = incompatible(x["fam"], at, por_cod[x["codigo"]], x["texto"], por_cod[x["codigo"]]["descripcion"])
        fmt = lambda z: (f"{'IGUAL' if z['igual'] else 'similar'} {z['codigo']} {z['desc']} (USD {z['precio']})" if z["codigo"] else "SIN PRECIO")
        lineas += [f"## {x['cot']} · pos {x['pos']}", f"- Pedido: {x['texto'][:120]}", f"- Antes: {fmt(x)}", f"- Ahora: {fmt(y)}"]
        if motivo:
            lineas.append(f"- Motivo del descarte: {motivo}")
        lineas.append("")
    lineas.insert(3, f"**{n} de {len(ahora)} renglones cambian.**\n")
    texto = "\n".join(lineas) + "\n"
    if a.salida:
        Path(a.salida).write_text(texto, encoding="utf-8")
    print(texto if n <= 40 or not a.salida else f"{n} renglones cambian → {a.salida}")


if __name__ == "__main__":
    main()
