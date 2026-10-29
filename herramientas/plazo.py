"""Plazo calculado de una cotización (camino crítico), con la regla de conocimiento/plazos.md §4.

Uso: python herramientas/plazo.py cotizaciones/<carpeta>   (lo corre también armar_cotizacion.py)

Trabaja solo con datos internos de cotizacion.json; no cambia el plazo ofrecido: lo controla y propone.
1. Acopio = el material que llega último. Se toman, en este orden:
   - las tareas de material de `plazo.tareas` (las que no son de taller), que se cargan con el plazo de cada proveedor;
   - si no hay tareas, el campo `plazo_dias` de cada ítem (0 si `"stock": true`);
   - si tampoco, el plazo típico sin stock del rubro en comercial/plazos_proveedores.csv (marcado como SUPUESTO).
2. Taller = suma de las tareas de taller (`"tal"`) de `plazo.tareas`, o `plazo.taller_dias`, o la referencia de la familia
   (plazos.md §3) marcada como SUPUESTO.
3. Plazo calculado = acopio + taller, sin superponer (el taller empieza cuando llega el material más largo), y con el
   margen de 15–20% de la regla.
4. Avisa si el plazo ofrecido es menor que el calculado, si no tiene margen, o si queda muy por debajo del plazo real
   histórico de la familia (plazos.md §1).
Genera <carpeta>/plazo_calculado.md.
"""
import csv
import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from numeros import fmt, fmtg  # noqa: E402
from catalogo_materiales import atributos, expandir, familia_de  # noqa: E402
from controles_tablas import RUBRO_PLAZO, rubro  # noqa: E402
from indice_proyectos import clasificar_cotizacion, norm  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
# plazos.md §3: días de taller con el material completo (cronogramas AESA 2023) y §1: plazo real histórico (mediana)
TALLER_FAMILIA = {"P": 40, "SEP": 38, "F": 42, "SK": 42, "M": 42, "CO": 42, "C": 60, "T": 42, "TS": 42, "CA": 30}
REAL_FAMILIA = {"CO": 51, "M": 58, "P": 121, "SK": 162, "T": 124, "C": 431, "SEP": 370, "TS": 222}


def tipicos():
    filas = list(csv.DictReader(open(RAIZ / "conocimiento" / "comercial" / "plazos_proveedores.csv", encoding="utf-8")))
    out = {}
    for rp in {r["rubro"] for r in filas}:
        v = [(float(r["plazo_dias_min"] or 0) + float(r["plazo_dias_max"])) / 2 for r in filas
             if r["rubro"] == rp and r["plazo_dias_max"] and float(r["plazo_dias_max"]) > 7]
        if v:
            out[rp] = statistics.median(v)
    return out


def main(carpeta):
    carpeta = Path(carpeta)
    c = json.load(open(carpeta / "cotizacion.json", encoding="utf-8"))
    pl = c.get("plazo", {})
    tareas = pl.get("tareas", [])
    ofrecido = pl.get("dias")
    fam = clasificar_cotizacion(c)[0]  # familia del equipo (equipo.familia o el título), no de los ítems
    lineas, avisos, supuestos = [f"# Plazo calculado — {c['codigo']}", "", "Generado por `herramientas/plazo.py` (regla de `conocimiento/plazos.md` §4). Propone y controla; no cambia el plazo ofrecido.", ""], [], []
    tip = tipicos()
    mat = [t for t in tareas if t[3] != "tal"]
    tal = [t for t in tareas if t[3] == "tal"]
    # 1. acopio
    if mat:
        acopio = max(t[2] for t in mat)
        critico = max(mat, key=lambda t: t[2])[0]
        lineas += ["## 1. Acopio (tareas de material cargadas)", ""] + [f"- {t[0]}: día {t[1]} a {t[2]}" for t in mat]
    else:
        filas = []
        for it in c["items"]:
            if it["grupo"] != "material":
                continue
            if it.get("stock"):
                d, origen = 0, "stock"
            elif it.get("plazo_dias") is not None:
                d, origen = float(it["plazo_dias"]), "plazo cargado del proveedor"
            else:
                t = expandir(norm(it["descripcion"]))
                f = familia_de(t)
                rp = rubro(RUBRO_PLAZO, f, atributos(t, f).get("tipo", "") or t)
                d, origen = tip.get(rp, 0), f"SUPUESTO: típico sin stock de '{rp}'" if rp in tip else "sin dato"
                if rp in tip:
                    supuestos.append(it["pos"])
            filas.append((d, it["pos"], it["descripcion"][:50], origen))
        acopio, pos_c, critico, _ = max(filas) if filas else (0, "", "", "")
        lineas += ["## 1. Acopio (plazo por ítem)", "", "| Pos | Ítem | Días | Origen |", "|---|---|---|---|"] + \
                  [f"| {p} | {d_} | {fmt(x, 0)} | {o} |" for x, p, d_, o in sorted(filas, reverse=True)]
        if supuestos:
            avisos.append(f"Plazo de acopio con valores SUPUESTOS (típico del rubro) en las posiciones {', '.join(supuestos)}: cargar el plazo cotizado por el proveedor")
    # 2. taller
    if tal:
        taller = sum(t[2] - t[1] for t in tal)
        origen_t = "tareas de taller cargadas"
        sup = [t for t in tal if t[1] < acopio]
        if sup:
            avisos.append(f"Superposición: la tarea de taller '{sup[0][0]}' empieza el día {sup[0][1]}, antes de que llegue el material más largo (día {fmtg(acopio)})")
    elif pl.get("taller_dias"):
        taller, origen_t = float(pl["taller_dias"]), "plazo.taller_dias"
    else:
        taller, origen_t = TALLER_FAMILIA.get(fam, 42), f"SUPUESTO: referencia de la familia {fam} (plazos.md §3)"
        avisos.append(f"Días de taller supuestos ({taller} para la familia {fam}): cargar las tareas de taller")
    calc = acopio + taller
    con_margen = (round(calc * 1.15), round(calc * 1.20))
    real = REAL_FAMILIA.get(fam)
    lineas += ["", "## 2. Resultado", "",
               f"- Material más largo: **{critico}** → acopio **{fmtg(acopio)} días**.",
               f"- Taller, ensayos, pintura y despacho: **{fmtg(taller)} días** ({origen_t}).",
               f"- **Plazo calculado sin superponer: {fmtg(calc)} días**; con el margen de 15–20% de la regla: **{con_margen[0]}–{con_margen[1]} días**.",
               f"- Plazo ofrecido: **{ofrecido} días**." if ofrecido else "- Sin plazo ofrecido cargado.",
               f"- Plazo real histórico de la familia {fam}: {real} días (mediana, plazos.md §1)." if real else ""]
    if ofrecido:
        if ofrecido < calc:
            avisos.append(f"El plazo ofrecido ({ofrecido} d) es MENOR que el calculado ({fmtg(calc)} d)")
        elif ofrecido < con_margen[0]:
            avisos.append(f"El plazo ofrecido ({ofrecido} d) no tiene el margen de 15–20% (sugerido {con_margen[0]}–{con_margen[1]} d)")
        if real and ofrecido < 0.6 * real:
            avisos.append(f"El plazo ofrecido es mucho menor que el real histórico de la familia {fam} ({real} d): confirmar antes de comprometerlo")
    lineas += ["", "## 3. Avisos", ""] + ([f"- ⚠ {a}" for a in avisos] or ["- Ninguno."])
    (carpeta / "plazo_calculado.md").write_text("\n".join(x for x in lineas if x is not None) + "\n", encoding="utf-8")
    print(f"Plazo: calculado {fmtg(calc)} días ({con_margen[0]}–{con_margen[1]} con margen) · ofrecido {ofrecido} → {carpeta / 'plazo_calculado.md'}")
    for a in avisos:
        print("  ! " + a)
    global ultimo
    ultimo = {"calculado": calc, "ofrecido": ofrecido, "justificacion": str(pl.get("justificacion") or "").strip()}
    return avisos


ultimo = {}


def bloquea_oferta():
    """Texto del bloqueo si el plazo ofrecido es menor que el calculado y no hay justificación escrita ("" si no bloquea).
    Un plazo menor no llega al cliente sin que alguien lo justifique (auditoría 29-10-2026; igual que la página)."""
    o, c = ultimo.get("ofrecido"), ultimo.get("calculado")
    if not o or not c or o >= c or ultimo.get("justificacion"):
        return ""
    return f"plazo ofrecido {o} días, menor que el calculado ({fmtg(c)} días): corregir plazo.dias o escribir plazo.justificacion"


if __name__ == "__main__":
    main(sys.argv[1])
