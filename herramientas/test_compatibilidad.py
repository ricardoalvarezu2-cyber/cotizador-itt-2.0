"""Pruebas de las reglas de compatibilidad del buscador de materiales (Matías, 30-10-2026).

Uso: python herramientas/test_compatibilidad.py   (lo corre verificar_todo.py)
1. Casos conocidos: lo que la norma permite reemplazar y lo que no.
2. La página (web/src/busqueda.js) da el mismo resultado que Python en los renglones reales de todas las cotizaciones contra
   candidatos del catálogo de su familia.
"""
import csv
import json
import random
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

# 1b. por el buscador completo (auditoría 30-10-2026: el atributo "material" del buscador pierde el grado, y las reglas
# probadas solo con atributos dejaban pasar WC6 → WCB y WPL6 → WPB). Cada pedido: el primer resultado no puede tener
# en la descripción lo que se prohíbe.
POR_BUSCADOR = [
    ('Válvula esférica 2" #600 RF ASTM A216 WC6', r"\bwcb\b"),
    ('Codo 90 2" sch 80 ASTM A420 WPL6 BW', r"\bwpb\b|a ?234"),
    ('Brida WN 2" #150 RF A182 F316L', r"^(?!.*316 ?l)"),
    ('Caño 6" sch 40 ASTM A106 Gr C BE', r"^(?!.*gr(?:ado)?\.? ?c\b)"),
    ('Espárrago 5/8" A193 B7M c/2 tuercas A194 2HM', r"^(?!.*b ?7 ?m)"),
]
import re  # noqa: E402
from compatibilidad import clases, regla_material  # noqa: E402
# 1c. segunda auditoría (30-10-2026): cuerpo contra internos, negaciones, "GR°", guiones, A53 sin grado, medidas "x"
POR_TEXTO = [  # (familia, pedido, candidato, ¿compatible?)
    ("VAL", 'Válvula esférica 2" #150 RF cuerpo AISI 316', "ESF 2 150 RF WCB INT 316", NO),
    ("VAL", "Válvula cuerpo A351 CF8M", "cuerpo WCB, internos 316", NO),
    ("VAL", "Válvula cuerpo A182 F316", "cuerpo A105 trim 316", NO),
    ("VAL", "Válvula esférica A105", "valvula esferica 0.5 #2000 NPT F316 Taval A105 forjada", NO),  # no se sabe el cuerpo
    ("VAL", "Válvula esférica, cuerpo WCB, internos 316 ASTM A-216 WCB", "VALV ESF G 12 S900 RF WCB INT 316 ASTO RPTFE", SI),
    ("VAL", "Válvula esférica, cuerpo WCB, internos 316 ASTM A-216 WCB", "valvula esferica WCB Taval", NO),  # no dice internos
    ("VAL", "Válvula retención, cuerpo ASTM A-216, clapeta AISI-316", "S600 A216 WCB, internos TRIM 8 (13Cr, NO AISI 316)", NO),
    ("VAL", "Válvula retención, cuerpo ASTM A-216, clapeta AISI-316", "retención A216 WCB internos AISI 316", SI),
    ("VAL", "Válvula esférica WCB", "valvula esferica WCB Taval", SI),
    ("ACC", "Tapón A105", "inoxidable AISI 304, NO A105", NO),
    ("CAN", "Caño ASTM A-53 GR°B", "Caño ASTM A-53 GR°A", NO),
    ("CAN", "Caño ASTM A-53 GR°B", "Caño c/c 168,3 x 7,11 mm A53/135", NO),      # A53 sin grado
    ("CAN", "Caño ASTM A-53 GR°B", "Tubo s/costura 168,3 x 7,11 mm A53/A106/API 5L B", SI),
    ("CAN", "Caño A106 GR°C", "Caño A106 Gr B", NO),
    ("CHA", "Chapa SA-516-70", "Chapa SA-516-60", NO),
    ("CHA", "Chapa SA-516 GR°70", "Chapa SA-516 GR°60", NO),
    ("CHA", "Chapa SA-516-60", "Chapa A516 Gr 70", SI),
    # tercera auditoría (30-10-2026)
    ("CAN", 'Caño API 5L PSL2 12" sch 40 X52', "Caño API 5L B", NO),
    ("CAN", 'Caño 36" API 5L e=19,05 X65', "Caño API 5L B", NO),
    ("VAL", 'Válvula esférica cuerpo bipartido, bola flotante, Ø 2", #150, ASTM A351 CF8M, RF', "ESF 2 150 RF WCB INT 316", NO),
    ("VAL", "Válvula esférica cuerpo tripartito, AISI 316", "ESF 2 150 RF WCB INT 316", NO),
    ("VAL", "Válvula esférica bola AISI 316", "A216 WCB bola AISI 316", NO),
    ("VAL", "Válvula mariposa disco AISI 316 cuerpo WCB", "cuerpo AISI 316 disco WCB", NO),
    ("CAN", "Caño A53 Tipo E Gr B", "Caño A53 Tipo E Gr B", SI),
    ("CAN", "caño A106 no galvanizado", "caño A106", SI),
]
for fam, a, b, ok in POR_TEXTO:
    m = regla_material(fam, a, b, b)
    chk(f"texto {fam}: {a} ← {b}", (m == "") == ok, m)
chk("reducción 80x40 contra STD x STD", incompatible("ABW", {"diametro": '2 1/2"x2"'}, {}, 'Reducción concéntrica 2 1/2"x2" 80x40 A234', "reduccion conc std x std A234") != "")
chk("reducción 80x40 contra XS x STD", incompatible("ABW", {"diametro": '2 1/2"x2"'}, {}, "Reducción 80x40 A234", "reduccion XS x STD A234") == "")
chk("revestimiento PE por PP", incompatible("CAN", {}, {}, "caño revestido polipropileno", "caño tricapa de polietileno") != "")
chk("revestimiento PP por PE", incompatible("CAN", {}, {}, "caño tricapa polietileno", "caño tricapa polipropileno") == "")
for t, esperado in [("largo 4,8m", {}), ("L=8m", {}), ("espárrago 5/8 x70 B7", {"bulon_b7"}), ("bolsa 45 x60", {}),
                    ("caño A53 a 6 m", {"cano_a53_sin_grado"}), ("dsaw sch20 x65", {"carbono_alta_resistencia"}),
                    ("tuerca A194 8M", {"bulon_inox"}), ("SA-516-60", {"carbono_516_60"})]:
    chk(f"clases {t}", set(clases(t)) == set(esperado), clases(t))
for t, prohibido in POR_BUSCADOR:
    *_, res = bm.buscar(t)
    d = bm.norm(res[0][-1]["descripcion"]) if res else ""
    chk(f"buscador: {t}", not (d and re.search(prohibido, d)), d[:80])

# 2. página = Python
bm.buscar("brida")  # carga el catálogo
filas = bm._FILAS
casos = []
for f in sorted((RAIZ / "cotizaciones").glob("*/pedido/lista_materiales_plano.csv")):
    for r in pc.leer(f):
        texto = pc.texto_busqueda(r)
        fam, at, *_ = bm.buscar(texto)
        todos = [c for c in filas if bm.NOMBRE_A_COD.get(c["familia"]) == fam]
        cands = todos[:60] + random.Random(f"{f.parent.parent.name}{r.get('pos')}").sample(todos[60:], min(90, len(todos[60:])))
        for c in cands:
            casos.append({"fam": fam, "ped": {k: at.get(k, "") for k in ("material", "extremos", "cara", "schedule", "diametro")}, "texto": texto,
                          "cand": {k: c.get(k, "") for k in ("material", "extremos", "cara", "schedule", "diametro")}, "d": c["descripcion"],
                          "py": incompatible(fam, at, c, texto, c["descripcion"]) != ""})
for fam, a, b, _ in POR_TEXTO:  # los casos de texto también en la página
    casos.append({"fam": fam, "ped": {"material": a}, "texto": a, "cand": {"material": b}, "d": b,
                  "py": incompatible(fam, {"material": a}, {"material": b}, a, b) != ""})
for fam, d, a, b in [("ABW", '2 1/2"x2"', 'Reducción 2 1/2"x2" 80x40 A234', "reduccion std x std A234"), ("ABW", '2 1/2"x2"', "Reducción 80x40 A234", "reduccion XS x STD A234"),
                     ("CAN", "", "caño revestido polipropileno A106", "caño tricapa de polietileno A106"), ("CAN", "", "caño A106 no galvanizado", "caño A106")]:
    casos.append({"fam": fam, "ped": {"diametro": d}, "texto": a, "cand": {}, "d": b, "py": incompatible(fam, {"diametro": d}, {}, a, b) != ""})
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
