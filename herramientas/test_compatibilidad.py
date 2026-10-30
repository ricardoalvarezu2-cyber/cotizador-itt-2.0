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
    ("VAL", {"material": "A216 WCB"}, {"material": "A216 WCC"}, SI),   # WCC (1.2) reemplaza a WCB (1.1): revisión 30-10-2026
    ("VAL", {"material": "A216 WCC"}, {"material": "A216 WCB"}, NO),
    ("VAL", {"material": "AISI 316"}, {"material": "A182 F304"}, NO),
    ("VAL", {"material": "AISI 316"}, {"material": "316L"}, NO),       # 316L (2.3) tiene menos rating que 316 (2.2)
    ("VAL", {"material": "CF8M"}, {"material": "CF3M"}, SI),           # CF3M está en el grupo 2.2
    ("VAL", {"material": "316/316L"}, {"material": "316L"}, NO),
    ("VAL", {"material": "316"}, {"material": "316/316L"}, SI),
    ("VAL", {"material": "A403 WP316"}, {"material": "A403 WP304"}, NO),
    ("VAL", {"material": "CF8M"}, {"material": "CF8"}, NO),
    ("VAL", {"material": "A105"}, {"material": "A352 LCB"}, NO),
    ("VAL", {"material": "A105"}, {"material": ""}, NO),               # sin material no se puede comparar
    ("VAL", {"material": "A105"}, {"material": "SA-105"}, SI),
    ("VAL", {"material": "A182 F11"}, {"material": "A105"}, NO),
    ("VAL", {"material": "A216 WC6"}, {"material": "A216 WCB"}, NO),
    ("CAN", {"material": "A106 B"}, {"material": "A53"}, NO),
    ("CAN", {"material": "A53"}, {"material": "A106 B"}, SI),
    ("CAN", {"material": "API 5L X-52"}, {"material": "API 5L B"}, NO),
    ("CAN", {"material": "A53 galvanizado"}, {"material": "A106 B"}, NO),
    ("ABW", {"material": "A420 WPL6"}, {"material": "A234 WPB"}, NO),
    ("JUN", {"material": "A193 B7"}, {"material": "A193 B7M"}, NO),
    ("JUN", {"material": "A193 B7"}, {"material": "A320 L7"}, SI),
    ("PER", {"material": "A36"}, {"material": "A516 Gr 60"}, NO),
    ("BRI", {"extremos": "RF"}, {"extremos": "NPT"}, NO),              # bridada no es referencia de roscada
    ("VAL", {"extremos": "NPT"}, {"extremos": "BW"}, NO),
    ("CAN", {"schedule": "STD", "diametro": "DN 300"}, {"schedule": "40"}, NO),
    ("VAL", {"material": "316L"}, {"material": "AISI 316"}, NO),
    ("BRI", {"material": "A350 LF2"}, {"material": "A105"}, NO),
    ("BRI", {"material": "A105"}, {"material": "A350 LF2"}, SI),
    ("CAN", {"material": "API 5L X52"}, {"material": "API 5L X60"}, NO),
    ("ABW", {"material": "A234 WPB"}, {"material": "A403 (inox)"}, NO),
    ("JUN", {"material": "A-193 B7 / A-194 2H"}, {"material": "A193 B7"}, SI),   # sin dato de tuerca: se compara el bulón
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
chk("MR0175 no se cubre con MR0103", incompatible("VAL", {}, {}, "NACE MR0175", "NACE MR0103") != "")
chk("'source' no es servicio ácido", incompatible("VAL", {}, {}, "source water", "x") == "")

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
