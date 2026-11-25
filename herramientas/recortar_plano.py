"""Recorta una página de un plano o P&ID en una grilla de imágenes de alta resolución para leerla por partes.

Uso:
  python herramientas/recortar_plano.py PLANO.pdf PAGINA CARPETA_SALIDA [--dpi 200] [--grilla 3x3] [--solapa 0.04]

Deja CARPETA_SALIDA/<plano>_p<PAGINA>_f<fila>c<col>.png (y la página entera a 80 dpi, _completo.png, para ubicarse).
Con un P&ID A1 a 200 dpi y grilla 3x3 se leen bien los tags, diámetros, series y notas. Los recortes van al
scratchpad: no se suben al repositorio.
"""
import argparse
import subprocess
from pathlib import Path

from PIL import Image

Image.MAX_IMAGE_PIXELS = None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("pagina", type=int)
    ap.add_argument("salida")
    ap.add_argument("--dpi", type=int, default=200)
    ap.add_argument("--grilla", default="3x3")
    ap.add_argument("--solapa", type=float, default=0.04)
    a = ap.parse_args()
    out = Path(a.salida)
    out.mkdir(parents=True, exist_ok=True)
    base = out / f"{Path(a.pdf).stem}_p{a.pagina}"
    subprocess.run(["pdftoppm", "-r", "80", "-png", "-singlefile", "-f", str(a.pagina), "-l", str(a.pagina), a.pdf,
                    str(base) + "_completo"], check=True)
    subprocess.run(["pdftoppm", "-r", str(a.dpi), "-png", "-singlefile", "-f", str(a.pagina), "-l", str(a.pagina), a.pdf,
                    str(base) + "_hi"], check=True)
    im = Image.open(str(base) + "_hi.png")
    W, H = im.size
    filas, cols = (int(x) for x in a.grilla.lower().split("x"))
    n = 0
    for i in range(filas):
        for j in range(cols):
            x0 = max(0.0, j / cols - a.solapa)
            x1 = min(1.0, (j + 1) / cols + a.solapa)
            y0 = max(0.0, i / filas - a.solapa)
            y1 = min(1.0, (i + 1) / filas + a.solapa)
            im.crop((int(W * x0), int(H * y0), int(W * x1), int(H * y1))).save(f"{base}_f{i}c{j}.png")
            n += 1
    Path(str(base) + "_hi.png").unlink()
    print(f"Listo: {n} recortes en {out} (y {base.name}_completo.png)")


if __name__ == "__main__":
    main()
