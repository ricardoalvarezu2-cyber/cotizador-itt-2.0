"""Lee la planilla PC0 (Excel convertido a Markdown) y devuelve, por hoja, los precios por posición y los bloques."""
import csv, io, re
F = "/home/user/cotizador-itt/fuentes_originales/pedidos_web/pmvrzbrh616ftx/Cotización Lic 69343 Skid concentradores VCD26217 PC0.xlsx.md"

def hojas():
    t = open(F, encoding="utf-8").read()
    out = {}
    for m in re.finditer(r"## Hoja: (.+?)\n\n```csv\n(.*?)```", t, re.S):
        out[m.group(1).strip()] = list(csv.reader(io.StringIO(m.group(2))))
    return out

def precios(hoja):
    pos = {}
    for r in hoja:
        r = r + [""] * 14
        p = r[0].strip()
        nota = r[8]
        mm = re.search(r"Pos\. (\d+) plano", nota)
        if not p.isdigit() and mm:
            p = mm.group(1)
        if p.isdigit() and r[5].strip():
            try:
                pos[p] = {"desc": r[1], "medida": r[2], "cant": float(r[3]), "unidad": r[4], "precio": float(r[5]), "prov": r[8] if not mm else "Taval", "nota": nota if mm else ""}
            except ValueError:
                pass
    return pos

if __name__ == "__main__":
    h = hojas()
    for k in ("1000623713", "1000623708"):
        print(k, {p: (v["precio"], v["prov"][:20]) for p, v in precios(h[k]).items()})
