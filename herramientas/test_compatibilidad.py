"""Pruebas de las reglas de compatibilidad del buscador de materiales (Matías, 30-10-2026).

Uso: python herramientas/test_compatibilidad.py   (lo corre verificar_todo.py)
1. Casos conocidos: lo que la norma permite reemplazar y lo que no.
2. La página (web/src/busqueda.js) da el mismo resultado que Python en los renglones reales de todas las cotizaciones contra
   candidatos del catálogo de su familia.
"""
import csv
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from compatibilidad import incompatible  # noqa: E402
import buscar_material as bm  # noqa: E402
import precotizar as pc  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
fallas = []


def chk(nombre, cond, det=""):
    if not cond:
        fallas.append(nombre)
        print("FALLA", nombre, det)


SI, NO = True, False
CASOS = [  # (familia, pedido, candidato, ¿compatible?)
    ("VAL", {"material": "A105"}, {"material": "A216 WCB"}, SI),
    ("VAL", {"material": "A216 WCB"}, {"material": "A216 WCC"}, NO),
    ("VAL", {"material": "AISI 316"}, {"material": "A182 F304"}, NO),
    ("VAL", {"material": "AISI 316"}, {"material": "316L"}, SI),
    ("VAL", {"material": "316L"}, {"material": "AISI 316"}, NO),
    ("BRI", {"material": "A350 LF2"}, {"material": "A105"}, NO),
    ("BRI", {"material": "A105"}, {"material": "A350 LF2"}, SI),
    ("CAN", {"material": "API 5L X52"}, {"material": "API 5L X60"}, NO),
    ("ABW", {"material": "A234 WPB"}, {"material": "A403 (inox)"}, NO),
    ("JUN", {"material": "A-193 B7 / A-194 2H"}, {"material": "A193 B7"}, SI),
    ("JUN", {"material": "A-193 B7 / A-194 2H"}, {"material": "A193 B8M"}, NO),
    ("BRI", {"cara": "RF", "extremos": "RF/BW"}, {"cara": "RF", "extremos": "RF"}, SI),
    ("BRI", {"cara": "RF"}, {"cara": "RTJ"}, NO),
    ("AFO", {"extremos": "NPT"}, {"extremos": "BSPT"}, NO),
    ("AFO", {"extremos": "SW"}, {"extremos": "NPT"}, NO),
    ("AFO", {"extremos": "BW/SW"}, {"extremos": "SW"}, SI),
    ("CAN", {"schedule": "STD", "diametro": "4"}, {"schedule": "40"}, SI),
    ("CAN", {"schedule": "XS", "diametro": "12"}, {"schedule": "80"}, NO),
    ("ABW", {"schedule": "120"}, {"schedule": "160"}, NO),
]
for fam, a, b, ok in CASOS:
    m = incompatible(fam, a, b)
    chk(f"{fam} {a} ← {b}", (m == "") == ok, m)
chk("NACE", incompatible("VAL", {}, {}, "valvula esferica NACE MR0175", "valvula esferica 2 600") != "")

# 2. página = Python
bm.buscar("brida")  # carga el catálogo
filas = bm._FILAS
casos = []
for f in sorted((RAIZ / "cotizaciones").glob("*/pedido/lista_materiales_plano.csv")):
    for r in pc.leer(f):
        texto = pc.texto_busqueda(r)
        fam, at, *_ = bm.buscar(texto)
        cands = [c for c in filas if bm.NOMBRE_A_COD.get(c["familia"]) == fam][:60]
        for c in cands:
            casos.append({"fam": fam, "ped": {k: at.get(k, "") for k in ("material", "extremos", "cara", "schedule", "diametro")}, "texto": texto,
                          "cand": {k: c.get(k, "") for k in ("material", "extremos", "cara", "schedule", "diametro")}, "d": c["descripcion"],
                          "py": incompatible(fam, at, c, texto, c["descripcion"]) != ""})
js = r"""const fs=require('fs');const B=require('./web/src/busqueda.js');const D=JSON.parse(fs.readFileSync('web/datos.json','utf8'));
const cs=JSON.parse(fs.readFileSync(0,'utf8'));console.log(JSON.stringify(cs.map(c=>B.incompatible(D.compat,c.fam,c.ped,c.cand,c.texto,c.d)!=="")));"""
r = subprocess.run(["node", "-e", js], cwd=RAIZ, input=json.dumps(casos), capture_output=True, text=True)
if r.returncode:
    chk("node", False, r.stderr[-600:])
else:
    res = json.loads(r.stdout)
    dif = [c for c, j in zip(casos, res) if c["py"] != j]
    chk(f"página = Python en {len(casos)} pares", not dif, json.dumps(dif[:3], ensure_ascii=False))
    print(f"{len(casos)} pares comparados, {sum(c['py'] for c in casos)} incompatibles")
print("Compatibilidad: todo OK" if not fallas else f"Compatibilidad: {len(fallas)} fallas")
sys.exit(1 if fallas else 0)
