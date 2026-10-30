"""Pares pedido–candidato que pasan de incompatibles a compatibles (NUEVOS ACEPTADOS) o al revés cuando cambian las reglas
de compatibilidad (tercera y cuarta auditoría, 30-10-2026: cada corrección que amplió lo que se lee abrió falsos aceptados
que nadie buscó). Solo informa.

Uso: python herramientas/revisar_pares_compatibilidad.py --control      compara con la línea base guardada
                                                                       (lo corre verificar_todo.py: falla si algo cambió)
     python herramientas/revisar_pares_compatibilidad.py --aceptar      guarda lo de ahora como línea base: SOLO después de
                                                                       revisar cada nuevo aceptado (¿la norma permite ese reemplazo?)
     python herramientas/revisar_pares_compatibilidad.py --ref main     compara con las reglas de otra versión de git
     [--salida archivo.md]

Pares: cada renglón de cotizaciones/*/pedido/lista_materiales_plano.csv contra los candidatos que devuelve el buscador,
todos los de su familia del mismo tipo y Ø, los primeros 60 de la familia y 90 al azar (fijos). Se emparejan por
(cotización, pos, código). La línea base está en conocimiento/tecnico/pares_linea_base.json; un par nuevo (otra
cotización, otra pieza del catálogo) no cuenta como cambio de reglas.
"""
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
BASE = RAIZ / "conocimiento" / "tecnico" / "pares_linea_base.json"

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
out = {}
for f in sorted(Path(sys.argv[2]).glob("cotizaciones/*/pedido/lista_materiales_plano.csv")):
    cot = f.parent.parent.name
    if cot.startswith("_"):
        continue
    for r in pc.leer(f):
        t = pc.texto_busqueda(r)
        fam, at, _, _, res = bm.buscar(t)
        todos = [c for c in filas if bm.NOMBRE_A_COD.get(c["familia"]) == fam]
        mismo = [c for c in todos if at.get("tipo") and bm.norm(c.get("tipo", "")) == bm.norm(at.get("tipo", ""))
                 and cp.dn_de(c.get("diametro")) == cp.dn_de(at.get("diametro"))]
        cands = [x[-1] for x in res] + mismo + todos[:60] + random.Random(f"{cot}{r.get('pos')}").sample(todos[60:], min(90, len(todos[60:])))
        vistos = set()
        for c in cands:
            if c["codigo"] in vistos:
                continue
            vistos.add(c["codigo"])
            mo = cp.motivos(fam, at, c, t, c["descripcion"]) if hasattr(cp, "motivos") else ([("?", cp.incompatible(fam, at, c, t, c["descripcion"]))] if cp.incompatible(fam, at, c, t, c["descripcion"]) else [])
            out[f"{cot}|{r.get('pos', '')}|{c['codigo']}"] = [t[:110], c["descripcion"][:90], mo[0][1] if mo else "", ",".join(sorted({m[0] for m in mo}))]
print(json.dumps(out, ensure_ascii=False))
"""


def huella(v):
    import hashlib
    return hashlib.sha1(f"{v[0]}|{v[1]}".encode()).hexdigest()[:8]


def correr(dir_herr, tabla=None):
    args = [sys.executable, "-c", SONDA, str(dir_herr), str(RAIZ)] + ([str(tabla)] if tabla else [])
    r = subprocess.run(args, cwd=RAIZ, capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"Falló con {dir_herr}:\n{r.stderr[-1500:]}")
    return json.loads(r.stdout.strip().splitlines()[-1])


def con_ref(ref):
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        arch = subprocess.run(["git", "archive", ref, "herramientas", "conocimiento/tecnico/compatibilidad_materiales.csv"],
                              cwd=RAIZ, capture_output=True)
        if arch.returncode:
            sys.exit(f"No se pudo leer {ref}: {arch.stderr.decode()[-300:]}")
        subprocess.run(["tar", "-x", "-C", str(tmp)], input=arch.stdout, check=True)
        for d in (RAIZ / "conocimiento").iterdir():  # el resto de los datos, los de ahora: solo cambian las reglas
            if not (tmp / "conocimiento" / d.name).exists():
                (tmp / "conocimiento" / d.name).symlink_to(d)
        for d in (RAIZ / "conocimiento" / "tecnico").iterdir():
            if not (tmp / "conocimiento" / "tecnico" / d.name).exists():
                (tmp / "conocimiento" / "tecnico" / d.name).symlink_to(d)
        (tmp / "fuentes_originales").symlink_to(RAIZ / "fuentes_originales")
        return correr(tmp / "herramientas", tmp / "conocimiento" / "tecnico" / "compatibilidad_materiales.csv")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ref")
    ap.add_argument("--salida")
    ap.add_argument("--control", action="store_true")
    ap.add_argument("--aceptar", action="store_true")
    a = ap.parse_args()
    ahora = correr(RAIZ / "herramientas")
    if a.aceptar:
        BASE.write_text(json.dumps({k: [huella(v), v[3]] for k, v in sorted(ahora.items())},
                                   ensure_ascii=False, separators=(",", ":")).replace('],"', '],\n"') + "\n", encoding="utf-8")
        print(f"Línea base de pares guardada: {len(ahora)} pares → {BASE.relative_to(RAIZ)}")
        return 0
    if a.ref:
        antes = {k: v[3] for k, v in con_ref(a.ref).items()}
        datos = []
        nombre = a.ref
    else:
        if not BASE.exists():
            print("No hay línea base de pares: correr --aceptar después de revisar")
            return 1
        b = json.loads(BASE.read_text(encoding="utf-8"))
        # solo cuentan los pares con los MISMOS textos de pedido y candidato: si cambió el dato (el renglón del plano o la
        # descripción del catálogo), no es un cambio de reglas (quinta auditoría 30-10-2026)
        antes = {k: v[1] for k, v in b.items() if k in ahora and v[0] == huella(ahora[k])}
        # un par con otros textos (cambió el plano, el catálogo o cómo se arma el texto) también frena: si no, quedaría
        # sin comparar para siempre (sexta auditoría 30-10-2026)
        datos = [k for k, v in b.items() if k in ahora and v[0] != huella(ahora[k])]
        nombre = f"la línea base ({len(datos)} pares con textos cambiados)"
    # se comparan los TIPOS de motivo (sexta auditoría: comparar solo compatible/incompatible no veía una regla borrada
    # si otro motivo seguía rechazando el par)
    acept = [k for k, v in ahora.items() if k in antes and set(filter(None, antes[k].split(","))) - set(filter(None, v[3].split(",")))]
    rech = [k for k, v in ahora.items() if k in antes and set(filter(None, v[3].split(","))) - set(filter(None, antes[k].split(",")))]
    nuevos = sum(1 for k in ahora if k not in antes)
    lin = [f"# Pares que cambian: reglas de {nombre} → ahora", "",
           f"**{len(acept)} nuevos aceptados** (revisar uno por uno: ¿la norma permite ese reemplazo?) · {len(rech)} nuevos "
           f"rechazados · {nuevos} pares sin comparar (renglones o piezas nuevas)", "", "## Nuevos aceptados", ""]
    lin += [f"- {k.replace('|', ' · ')} (deja de dar: {', '.join(sorted(set(antes[k].split(',')) - set(ahora[k][3].split(','))))})\n  pedido: {ahora[k][0]}\n  candidato: {ahora[k][1]}" for k in acept]
    lin += ["", "## Pares con textos cambiados (revisar si el cambio de texto es correcto)", ""]
    lin += [f"- {k.replace('|', ' · ')}: {ahora[k][0][:80]} ← {ahora[k][1][:60]}" for k in datos[:300]]
    lin += ["", "## Nuevos rechazados", ""]
    lin += [f"- {k.replace('|', ' · ')} · {ahora[k][1][:60]}: {ahora[k][2][:120]}" for k in rech]
    texto = "\n".join(lin) + "\n"
    if a.salida:
        Path(a.salida).write_text(texto, encoding="utf-8")
    print(f"Pares contra {nombre}: {len(acept)} nuevos aceptados · {len(rech)} nuevos rechazados · {nuevos} sin comparar"
          + (f" → {a.salida}" if a.salida else ""))
    if a.control:
        for k in acept[:20]:
            print("  nuevo aceptado sin revisar:", k.replace("|", " · "), "←", ahora[k][1][:60])
        if acept or rech or datos:
            print("  Revisar cada cambio (--salida para el detalle) y, si está bien, --aceptar")
        return 1 if (acept or rech or datos) else 0
    if not a.salida:
        print(texto[:6000])
    return 0


if __name__ == "__main__":
    sys.exit(main())
