"""Copia al repositorio las cotizaciones guardadas en la base de la página (respaldo semanal en GitHub).

Claude baja la base con ArtifactData (action "list", collection "cotizaciones", out_dir <carpeta>) y después corre:
    python web/respaldo_base.py <carpeta>/cotizaciones
Deja cada cotización en cotizaciones_web/<id>/cotizacion.json y oferta.json (el mismo formato que cotizaciones/<carpeta>),
más cotizaciones_web/README.md con la lista. Las cotizaciones borradas de la página quedan en el repositorio (no se borran).
"""
import json
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DEST = RAIZ / "cotizaciones_web"


def main(carpeta):
    filas = []
    for f in sorted(Path(carpeta).glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        d = d.get("data", d)
        if "cot" not in d:
            continue
        out = DEST / f.stem
        out.mkdir(parents=True, exist_ok=True)
        (out / "cotizacion.json").write_text(json.dumps(d["cot"], ensure_ascii=False, indent=1), encoding="utf-8")
        (out / "oferta.json").write_text(json.dumps(d.get("oferta", {}), ensure_ascii=False, indent=1), encoding="utf-8")
        c = d["cot"]
        filas.append(f"| {f.stem} | {c.get('codigo', '')} | {c.get('titulo', '')} | {c.get('estado', '')} | {d.get('guardado', '')[:16]} |")
    DEST.mkdir(exist_ok=True)
    viejas = [p.name for p in DEST.iterdir() if p.is_dir() and p.name not in {r.split(" | ")[0][2:] for r in filas}]
    (DEST / "README.md").write_text(
        f"# Respaldo de las cotizaciones de la página\n\nÚltimo respaldo: {date.today().isoformat()} (lo hace la tarea semanal; ver web/LEEME.md).\n\n"
        "| id | código | título | estado | guardado |\n|---|---|---|---|---|\n" + "\n".join(filas) + "\n"
        + (f"\nYa no están en la página (se conservan acá): {', '.join(sorted(viejas))}\n" if viejas else ""), encoding="utf-8")
    print(f"{len(filas)} cotizaciones respaldadas en cotizaciones_web/")


if __name__ == "__main__":
    main(sys.argv[1])
