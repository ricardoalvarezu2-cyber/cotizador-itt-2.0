"""Pruebas del buscador de antecedentes (criterio del 29-10-2026, igual para todas las familias).

Uso: python herramientas/test_antecedentes.py   (lo corre verificar_todo.py)

1. Clasificación: sinónimos, familia por la primera palabra clave, subtipo, Ø del cuerpo.
2. Cada caso de control (cotizaciones/CTRL-*, uno por familia) encuentra primero el proyecto del que salió.
3. Casos de la COT26-0135 (Camuzzi): el separador coalescente compara contra coalescentes y no contra manifolds; el
   skid de regulación encuentra el CAMUZZI/23; las carpetas sin ficha anteriores aparecen cuando hay pocos del subtipo.
4. Un dato que falta en el antecedente no le resta puntos.
5. La página (web/src/antecedentes.js) da los mismos 5 que Python en todas las cotizaciones.
"""
import json
import subprocess
import sys
from datetime import date
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent))
from buscar_antecedentes import buscar, consulta, consulta_de_cotizacion, idf_de, leer, puntuar  # noqa: E402
from indice_proyectos import SALIDA, canon, clasificar, diametro_cuerpo, norm  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
fallas = []


def chk(nombre, cond, detalle=""):
    if not cond:
        fallas.append(nombre)
        print("FALLA", nombre, detalle)


# 1. clasificación
chk("sinónimos coalescedor = coalescente", canon(norm("filtros coalescedores")) == canon(norm("filtros coalescentes")))
chk("FM06 = FM6", canon(norm("filtro FM06")) == canon(norm("filtro FM-6")) == "filtro fm6")
for texto, fam, sub in [("2 separadores verticales coalescentes", "SEP", "coalescente"),
                        ("Filtro coalescente FM06", "F", "coalescente"),
                        ("Filtro FM y skid salto de regulación", "F", "filtro_fm"),
                        ("Tramo de medición UFM", "P", "puente_medicion"),
                        ("Skid de gas combustible PAD #900", "SK", "skid_gas_combustible"),
                        ("Trampa lanzadora 16x20 serie 900", "TS", "trampa_scraper"),
                        ("Tanque de choque horizontal 36\"", "T", "tanque_choque"),
                        ("Calentador indirecto 500.000 BTU/h", "C", "calentador_indirecto"),
                        ("2 puentes armados BBO MEC 1500", "P", "puente_produccion"),
                        ("Estructuras - soporte línea flare", "EST", "plataforma")]:
    f, _, s = clasificar(texto)
    chk(f"clasificar «{texto}»", (f, s) == (fam, sub), f"→ {f} {s}")
for texto, v in [('Filtro Coalescente 48”#600', 48), ("cuerpo Ø1740 x 4400 mm", 68.5), ("2.286 mm diám. x 8.100 mm", 90),
                 ("filtro canasto 12\" #150", None), ("elemento D 400 x H 800 mm", None)]:
    chk(f"Ø cuerpo «{texto}»", diametro_cuerpo(texto) == v, f"→ {diametro_cuerpo(texto)}")

# 2 y 3. cotizaciones
ORIGEN = {"CTRL-C01": "PAMPA ENERGIA/7", "CTRL-CA01": "Sacde/18", "CTRL-F01": "TAVAL/40", "CTRL-M01": "TECPETROL/9",
          "CTRL-P01": "TAVAL/70", "CTRL-P02": "PAMPA ENERGIA/5", "CTRL-SK01": "YPF/28", "CTRL-T01": "Sacde/20", "CTRL-TS01": "TECPETROL/13"}
filas = leer(SALIDA)
carpetas = sorted(d for d in (RAIZ / "cotizaciones").iterdir() if (d / "cotizacion.json").exists() and not d.name.startswith("_"))
python = {}
for d in carpetas:
    c = json.load(open(d / "cotizacion.json", encoding="utf-8"))
    q = consulta_de_cotizacion(c)
    res = buscar(q, filas, hoy=date.today(), excluir=[d.name], con_precio=True)[0]
    python[str(d.relative_to(RAIZ))] = [p["id"] for _, _, _, p in res[:5]]
    pref = next((k for k in ORIGEN if d.name.startswith(k + "_")), None)
    if pref:
        chk(f"{d.name}: primero {ORIGEN[pref]}", res and res[0][3]["id"].startswith(ORIGEN[pref]), f"→ {res[0][3]['id'] if res else '-'}")
sep = python.get("cotizaciones/COT26-0135-003_CAMUZZI_CP24578_SEPARADOR", [])
sub_de = {r["id"]: r["subtipo"] for r in filas}
chk("separador coalescente: los 3 primeros son coalescentes", len(sep) >= 3 and all(sub_de.get(x) == "coalescente" for x in sep[:3]), sep)
chk("separador coalescente: ningún manifold en los 5", not any("anifold" in x.lower() for x in sep), sep)
reg = python.get("cotizaciones/COT26-0135-001_CAMUZZI_CP24578_SKIDREG", [])
chk("skid de regulación Camuzzi: CAMUZZI/23 entre los 5", any(x.startswith("CAMUZZI/23") for x in reg), reg)
q = consulta("separador vertical coalescente", cuerpo=55, serie="600", cliente="CAMUZZI")
principal, anteriores, mismos = buscar(q, filas)
chk("coalescente: TAVAL/37 entre los 5 (ficha hecha el 29-10-2026)", any(p["id"].startswith("TAVAL/37") for _, _, _, p in principal[:5]))
chk("coalescente: carpetas anteriores con CAMUZZI/13", any(p["id"].startswith("CAMUZZI/13") for _, _, _, p in anteriores[:5]))

# 4. dato faltante no resta
base = {"id": "X", "origen": "", "fecha": date.today().isoformat(), "cliente": "", "cliente_final": "", "familia": "F", "etiquetas": "F",
        "subtipo": "coalescente", "subtipos": "coalescente", "diametros": "", "diametro_cuerpo": "", "series": "", "material": "", "union": "",
        "palabras": "coalescent"}
q = SimpleNamespace(texto="coalescente", familia="F", subtipo="coalescente", diametro=None, cuerpo=55, serie="600", material=None, union=None, cliente=None)
idf = idf_de(filas)
sin_dato = puntuar(base, q, idf, date.today())[0]
otra_serie = puntuar({**base, "series": "150"}, q, idf, date.today())[0]
misma = puntuar({**base, "series": "600"}, q, idf, date.today())[0]
chk("sin serie puntúa más que con otra serie", sin_dato > otra_serie, (sin_dato, otra_serie))
chk("con la misma serie puntúa más que sin dato", misma > sin_dato, (misma, sin_dato))

# 5. página = Python
r = subprocess.run(["node", str(RAIZ / "web" / "probar_antecedentes.js")] + list(python), cwd=RAIZ, capture_output=True, text=True)
if r.returncode:
    chk("node web/probar_antecedentes.js", False, r.stderr[-800:])
else:
    js = json.loads(r.stdout)
    for k, ids in python.items():
        jids = [x[0] for x in js[k]["top"]]
        chk(f"página = Python en {k}", jids == ids, f"\n  py {ids}\n  js {jids}\n  consulta js {js[k]}")

# 6. costo contra costo (30-10-2026): la página toma el mismo costo por equipo que Python
from comparar_antecedentes import costo_antecedente  # noqa: E402
por_id = {r["id"]: r for r in filas}
datos = json.load(open(RAIZ / "web" / "datos.json", encoding="utf-8"))
cu_pag = {p["id"]: p.get("cu") for p in datos["antecedentes"]["proyectos"]}
for i, r in por_id.items():
    cu = costo_antecedente(r)["cu"]
    if (round(cu, 2) if cu else None) != cu_pag.get(i):
        chk(f"costo por equipo página = Python en {i[:40]}", False, (cu, cu_pag.get(i)))
        break
chk("TAVAL/37 tiene costo por equipo (planilla de costo)", costo_antecedente(next(r for k, r in por_id.items() if k.startswith("TAVAL/37")))["cu"])

print("Antecedentes: todo OK" if not fallas else f"Antecedentes: {len(fallas)} fallas")
sys.exit(1 if fallas else 0)
