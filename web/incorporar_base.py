"""Pasa una cotización de la página al repositorio y la suma a la biblioteca (botón de Resumen; pedido "incorporar_base").

Claude baja el documento con ArtifactData (action "get", collection "cotizaciones", doc_id <id>, out_dir <carpeta>) y corre:
    python web/incorporar_base.py <carpeta>/cotizaciones/<id>.json
1. Biblioteca: deja la cotización en biblioteca_cotizaciones/<id>/ (cotizacion.json, oferta.json e incorporacion.json con
   fecha, estado y versión). Si ya estaba, la reemplaza: vale la última incorporada (decisión de Matías, 29-10-2026).
2. Repositorio: si hay una carpeta cotizaciones/<código>_* con el mismo código, la versión de la página reemplaza su
   cotizacion.json y oferta.json (lo que la página no guarda, como la firma, se conserva) y se vuelve a armar
   (armar_cotizacion.py). Lo que había queda en el historial de git.
Si la carpeta del repositorio cambió después de la copia que tiene la página (semilla.py guarda su huella en
cot.huella_repo), frena: comparar y, solo si después de revisar vale la de la página, repetir con --forzar.
Para una cotización del repositorio tal como está ahí: python web/incorporar_base.py --repo cotizaciones/<carpeta> [...]
Después: python herramientas/actualizar_base.py (catálogo e índice de antecedentes toman la biblioteca), construir_datos,
armar_pagina y republicar (ver web/LEEME.md, "Pedidos desde la página").
"""
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
BIB = RAIZ / "biblioteca_cotizaciones"
sys.path.insert(0, str(RAIZ / "herramientas"))
from numeros import a_vista, fmt  # noqa: E402


def escribir(carpeta, cot, oferta):
    carpeta.mkdir(parents=True, exist_ok=True)
    (carpeta / "cotizacion.json").write_text(json.dumps(cot, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    (carpeta / "oferta.json").write_text(json.dumps(oferta or {}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


# lo que semilla.py agrega para la página desde otros archivos del repositorio (plano, transcripción, ficha): no se
# vuelve a escribir en cotizacion.json (tercera auditoría 30-10-2026: dejaba copias que después quedaban viejas)
DERIVADOS_COT = ("transcripcion", "kg_compras", "ficha", "huella_repo")
DERIVADOS_ITEM = ("plano", "fam", "at")


def sin_derivados(cot):
    cot = {k: v for k, v in cot.items() if k not in DERIVADOS_COT}
    cot["items"] = [{k: v for k, v in it.items() if k not in DERIVADOS_ITEM} for it in cot.get("items", [])]
    return cot


def indice():
    filas = []
    for m in sorted(BIB.glob("*/incorporacion.json")):
        x = json.loads(m.read_text(encoding="utf-8"))
        filas.append(f"| {m.parent.name} | {x.get('codigo', '')} | {x.get('titulo', '')} | {x.get('estado', '')} | "
                     f"{a_vista(x.get('incorporada', '')[:10])} | {x.get('veces', 1)} | {x.get('carpeta_repo', '') or '—'} |")
    (BIB / "README.md").write_text(
        "# Biblioteca de cotizaciones\n\nLas que alimentan el catálogo y el índice de antecedentes. Entran solo con el botón "
        "\"Pasar al repositorio y a la biblioteca\" de la página (`web/incorporar_base.py`); si se incorpora de nuevo, la última "
        "versión reemplaza a la anterior.\n\n| id | código | título | estado | incorporada | veces | carpeta en el repositorio |\n"
        "|---|---|---|---|---|---|---|\n" + "\n".join(filas) + "\n", encoding="utf-8")


def main(archivo, forzar=False):
    d = json.loads(Path(archivo).read_text(encoding="utf-8"))
    d = d.get("data", d)
    cot, oferta = d["cot"], d.get("oferta", {})
    if not cot.get("items"):
        sys.exit("La cotización no tiene ítems: no se incorpora.")
    codigo = cot.get("codigo", "")
    repo = [p for p in sorted((RAIZ / "cotizaciones").glob(f"{codigo}_*")) if (p / "cotizacion.json").exists()] if codigo else []
    huella_pagina = cot.pop("huella_repo", "")
    sys.path.insert(0, str(RAIZ / "web"))
    from semilla import huella
    id_ = Path(archivo).stem
    meta_vieja = BIB / id_ / "incorporacion.json"
    # el repositorio no cambió desde la última vez que se pasó esta cotización de la página: no hay correcciones que pisar
    # (segunda auditoría 30-10-2026: sin esto la segunda incorporación frenaba siempre y terminaba en --forzar)
    ultima = json.loads(meta_vieja.read_text(encoding="utf-8")).get("huella_repo_despues", "") if meta_vieja.exists() else ""
    if repo and not forzar:
        if huella(repo[0]) not in (huella_pagina, ultima):
            sys.exit(f"FRENADO: {repo[0].relative_to(RAIZ)} cambió en el repositorio después de la copia que tiene la página "
                     f"({'la página no dice de qué versión salió' if not huella_pagina else 'huella ' + huella_pagina + ' ≠ ' + huella(repo[0])}). "
                     "Pasarla pisaría las correcciones del repositorio. Comparar las dos versiones, pasar a la página lo que falte "
                     "(semilla.py --previo) o, si después de revisar vale la de la página, volver a correr con --forzar.")
    destino = BIB / id_
    veces = (json.loads(meta_vieja.read_text(encoding="utf-8")).get("veces", 1) + 1) if meta_vieja.exists() else 1
    escribir(destino, cot, oferta)
    meta = {"id": id_, "codigo": codigo, "titulo": cot.get("titulo", ""), "estado": cot.get("estado", ""),
            "incorporada": datetime.now().isoformat(timespec="seconds"), "guardado_pagina": d.get("guardado", ""),
            "veces": veces, "carpeta_repo": str(repo[0].relative_to(RAIZ)) if repo else ""}
    (destino / "incorporacion.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    indice()
    print(f"Biblioteca: {destino.relative_to(RAIZ)} ({'reemplazó la versión anterior' if veces > 1 else 'nueva'}; estado {meta['estado']})")
    if repo:
        # Lo que la página no guarda (por ejemplo la firma de la oferta, que la página toma de "firmantes") se conserva del repositorio
        viejo = lambda n: json.loads((repo[0] / n).read_text(encoding="utf-8")) if (repo[0] / n).exists() else {}
        escribir(repo[0], sin_derivados({**viejo("cotizacion.json"), **cot}), {**viejo("oferta.json"), **(oferta or {})})
        r = subprocess.run([sys.executable, str(RAIZ / "herramientas" / "armar_cotizacion.py"), str(repo[0])], capture_output=True, text=True)
        linea = next((l for l in r.stdout.splitlines() if l.startswith("Planilla:")), "")
        print(f"Repositorio: {repo[0].relative_to(RAIZ)} reemplazada con la versión de la página y rearmada · {linea or 'ver salida de armar_cotizacion'}")
        if r.returncode:
            print(r.stdout[-1500:], r.stderr[-1500:])
            sys.exit("armar_cotizacion.py falló: revisar antes de subir.")
        meta["huella_repo_despues"] = huella(repo[0])
        (destino / "incorporacion.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"Huella del repositorio después de pasarla: {meta['huella_repo_despues']} (escribirla en cot.huella_repo de la página)")
    else:
        print("Repositorio: no hay carpeta cotizaciones/ con ese código; queda solo en la biblioteca.")


def desde_repo(carpeta):
    """Incorpora una cotización armada en el repositorio (cotizaciones/<carpeta>) tal como está en el repositorio."""
    c = Path(carpeta)
    cot = json.loads((c / "cotizacion.json").read_text(encoding="utf-8"))
    of = json.loads((c / "oferta.json").read_text(encoding="utf-8")) if (c / "oferta.json").exists() else {}
    id_ = "c" + cot["codigo"].lower().replace("cot", "")
    destino = BIB / id_
    meta_vieja = destino / "incorporacion.json"
    veces = (json.loads(meta_vieja.read_text(encoding="utf-8")).get("veces", 1) + 1) if meta_vieja.exists() else 1
    escribir(destino, cot, of)
    meta = {"id": id_, "codigo": cot["codigo"], "titulo": cot.get("titulo", ""), "estado": cot.get("estado", ""),
            "incorporada": datetime.now().isoformat(timespec="seconds"), "guardado_pagina": "", "veces": veces,
            "carpeta_repo": str(c.resolve().relative_to(RAIZ)), "origen": "repositorio"}
    (destino / "incorporacion.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    indice()
    print(f"Biblioteca: {destino.relative_to(RAIZ)} desde {meta['carpeta_repo']} ({'reemplazó la anterior' if veces > 1 else 'nueva'})")


if __name__ == "__main__":
    if sys.argv[1] == "--repo":
        for x in sys.argv[2:]:
            desde_repo(x)
    else:
        main(sys.argv[1], forzar="--forzar" in sys.argv[2:])
