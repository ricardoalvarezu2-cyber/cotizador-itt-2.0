"""Lee un plano DWG/DXF: lo convierte a DXF, extrae los textos por capa y genera imágenes de cada zona dibujada.

Uso: python herramientas/leer_dwg.py PLANO.dwg [carpeta_salida]
"""
import collections
import json
import sys
from pathlib import Path

import ezdxf
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from ezdxf import bbox
from ezdxf.addons.drawing import Frontend, RenderContext
from ezdxf.addons.drawing.config import BackgroundPolicy, ColorPolicy, Configuration
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend

CELDA = 3000  # tamaño de la grilla (unidades del dibujo) para agrupar zonas


def a_dxf(origen: Path, salida: Path) -> Path:
    if origen.suffix.lower() == ".dxf":
        return origen
    import ezdwg

    destino = salida / (origen.stem + ".dxf")
    r = ezdwg.to_dxf(str(origen), str(destino), dxf_version="R2018")
    print(f"DWG -> DXF: {r.written_entities} entidades, omitidas {r.skipped_by_type}")
    return destino


def textos_por_capa(doc) -> dict:
    capas = collections.defaultdict(list)
    for e in doc.modelspace().query("TEXT MTEXT"):
        texto = e.plain_text() if e.dxftype() == "MTEXT" else e.dxf.text
        texto = " ".join(texto.split())
        if texto:
            capas[e.dxf.layer].append({"x": round(e.dxf.insert.x), "y": round(e.dxf.insert.y), "texto": texto})
    for items in capas.values():
        items.sort(key=lambda i: (-i["y"], i["x"]))
    return dict(capas)


def zonas(doc, minimo=300) -> list:
    """Agrupa las entidades en celdas de grilla contiguas y devuelve el rectángulo de cada zona."""
    celdas = collections.Counter()
    for e in doc.modelspace():
        b = bbox.extents([e], fast=True)
        if b.has_data:
            c = (b.extmin + b.extmax) / 2
            celdas[(int(c.x // CELDA), int(c.y // CELDA))] += 1
    pendientes = {k for k, n in celdas.items() if n >= 20}
    grupos = []
    while pendientes:
        pila, grupo = [pendientes.pop()], []
        while pila:
            cx, cy = pila.pop()
            grupo.append((cx, cy))
            for v in [(cx + dx, cy + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]:
                if v in pendientes:
                    pendientes.remove(v)
                    pila.append(v)
        if sum(celdas[g] for g in grupo) >= minimo:
            xs, ys = [g[0] for g in grupo], [g[1] for g in grupo]
            grupos.append((min(xs) * CELDA, min(ys) * CELDA, (max(xs) + 1) * CELDA, (max(ys) + 1) * CELDA))
    return grupos


def dibujar(doc, rect, archivo: Path):
    x0, y0, x1, y1 = rect
    ancho = 24
    fig = plt.figure(figsize=(ancho, ancho * (y1 - y0) / (x1 - x0)))
    ax = fig.add_axes([0, 0, 1, 1])
    cfg = Configuration(background_policy=BackgroundPolicy.WHITE, color_policy=ColorPolicy.BLACK)
    Frontend(RenderContext(doc), MatplotlibBackend(ax), config=cfg).draw_layout(doc.modelspace(), finalize=False)
    ax.set_xlim(x0, x1)
    ax.set_ylim(y0, y1)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.savefig(archivo, dpi=100)
    plt.close(fig)


def main():
    origen = Path(sys.argv[1])
    salida = Path(sys.argv[2]) if len(sys.argv) > 2 else origen.parent / (origen.stem + "_lectura")
    salida.mkdir(parents=True, exist_ok=True)
    doc = ezdxf.readfile(a_dxf(origen, salida))

    textos = textos_por_capa(doc)
    (salida / "textos.json").write_text(json.dumps(textos, ensure_ascii=False, indent=1))
    print(f"Textos: {sum(len(v) for v in textos.values())} en {len(textos)} capas -> textos.json")

    for i, rect in enumerate(zonas(doc), 1):
        dibujar(doc, rect, salida / f"zona_{i}.png")
        print(f"Zona {i}: {rect} -> zona_{i}.png")


if __name__ == "__main__":
    main()
