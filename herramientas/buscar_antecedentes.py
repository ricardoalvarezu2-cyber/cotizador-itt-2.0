"""Busca en el índice de proyectos las cotizaciones más parecidas a un pedido nuevo, priorizando las más actuales.

Uso:
  python herramientas/buscar_antecedentes.py --texto "separador vertical coalescente" --cuerpo 55 --serie 600 --cliente CAMUZZI
  python herramientas/buscar_antecedentes.py --familia CO --subtipo colector_campo --texto "colector de campo" --diametro 6 \\
         --serie 300 --material carbono --union bridado --cliente "PAMPA" [--top 8]
  python herramientas/buscar_antecedentes.py --cotizacion cotizaciones/<carpeta>   (arma la consulta desde cotizacion.json)
  python herramientas/buscar_antecedentes.py --familias      (familias y subtipos, con cuántos proyectos hay de cada uno)

Sin --familia ni --subtipo, se deducen del texto (indice_proyectos.clasificar). Sirve para todas las familias.

Criterio (Matías, 29-10-2026: igual para todas las familias y todo el catálogo):
  1. Familia: entran los de la misma familia, los que la tienen como secundaria (×0,85) y los de otra familia con el
     mismo subtipo (un "separador coalescente" SEP y un "filtro coalescente" F).
  2. Parecido (0–100), solo con los datos que tienen los dos (un dato que falta no resta: se avisa "sin dato"):
     subtipo 30 (si el proyecto trae varios equipos y uno es el pedido, 20; otro subtipo 0) · texto hasta 25 (sinónimos unificados) · tamaño 15 (cercano 7) · serie 12 ·
     material 8 · roscado/bridado 5 · mismo cliente 4.
     Tamaño: en recipientes (separadores, filtros, tanques, calentadores) el Ø del CUERPO (igual ±10%, cercano ±30%);
     si falta el del cuerpo, el de las conexiones vale la mitad. En el resto, el Ø de línea.
     Se multiplica por 0,7 + 0,3 × (datos comparados / datos del pedido): con pocos datos no llega a 100.
  3. Utilidad de la carpeta: planilla de costo +5 · proveedores +2 · OC +2 · confianza baja −5.
  4. Antigüedad: ×1,0 este año y −20% por año (mínimo ×0,4). Ante dos parecidos, gana el más nuevo.
  5. Si hay menos de 5 antecedentes del mismo subtipo (o de la familia, sin subtipo), se muestran aparte las carpetas
     sin ficha de 2021–2024 (indice_historico.csv, año estimado, sin precios: solo para comparar diseño y alcance).
     Las carpetas de 2025–2026 que todavía no tienen ficha entran en la lista principal marcadas SIN FICHA.
Revisar los 3–5 primeros (abrir la carpeta de textos y la ficha).
"""
import argparse
import csv
import json
import math
import sys
from collections import Counter
from datetime import date
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent))
from numeros import fmt, fmtg  # noqa: E402
from indice_proyectos import (FAMILIAS, HISTORICO, RECIPIENTES, SALIDA as INDICE, SUBTIPO_FAMILIA, SUBTIPO_NOMBRE,  # noqa: E402
                              canon, clasificar, clasificar_cotizacion, norm, palabras)

TAMANOS = [0.5, 0.75, 1, 1.5, 2, 2.5, 3, 4, 6, 8, 10, 12, 14, 16, 18, 20, 24, 30, 36, 42, 48]
PESOS = {"subtipo": 30, "texto": 25, "tamano": 15, "serie": 12, "material": 8, "union": 5, "cliente": 4}
MINIMO_MISMO_SUBTIPO = 5  # con menos, se muestran las carpetas sin ficha 2021–2024


def vecino(a, b):
    try:
        return abs(TAMANOS.index(a) - TAMANOS.index(b)) == 1
    except ValueError:
        return abs(a - b) / max(a, b) <= 0.25


def leer(ruta):
    return list(csv.DictReader(open(ruta, encoding="utf-8"))) if Path(ruta).exists() else []


def idf_de(filas):
    df = Counter(w for r in filas for w in set(r["palabras"].split()))
    return {w: math.log(len(filas) / n) for w, n in df.items()}


def consulta(texto="", familia=None, subtipo=None, diametro=None, cuerpo=None, serie=None, material=None, union=None, cliente=None):
    """Arma la consulta; familia y subtipo se deducen del texto si no vienen."""
    fam, _, sub = clasificar(texto) if texto else ("", [], "")
    subtipo = subtipo or sub or None
    familia = (familia or "").upper() or (SUBTIPO_FAMILIA.get(subtipo) if subtipo and not texto else None) or (fam if fam != "OT" else None)
    return SimpleNamespace(texto=texto, familia=familia, subtipo=subtipo, diametro=diametro, cuerpo=cuerpo, serie=serie,
                           material=material, union=union, cliente=cliente)


def consulta_de_cotizacion(c, yo=None):
    """Consulta para una cotización del cotizador: familia, subtipo y Ø del cuerpo de clasificar_cotizacion
    (equipo.familia / equipo.subtipo si están); Ø de línea, serie, material y unión del título y los ítems. Es la misma
    que arma la página (web/src/antecedentes.js); yo no se usa (queda por compatibilidad)."""
    from indice_proyectos import atributos, diametros, series
    fam, _, sub, cuerpo = clasificar_cotizacion(c)
    t = canon(norm(" ".join([c.get("titulo", "")] + [i.get("descripcion", "") + " " + i.get("especificacion", "") for i in c.get("items", [])])))
    dias = diametros(t)
    ser = series(t) or [None]
    mat, uni, _ = atributos(t)
    eq = c.get("equipo") or {}
    diam = None if cuerpo else (num(eq.get("diametro_pulg")) or (max(dias) if dias else None))
    return SimpleNamespace(texto=" ".join([eq.get("singular", ""), c.get("titulo", "")]), familia=fam if fam != "OT" else None,
                           subtipo=sub or None, diametro=diam, cuerpo=cuerpo, serie=ser[-1],
                           material=mat[0] if len(mat) == 1 else None, union=uni[0] if len(uni) == 1 else None,
                           cliente=(c.get("cliente") or {}).get("nombre"))


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def puntuar(p, q, idf, hoy):
    """(puntaje, razones, factor de antigüedad) o None si no es de la familia ni del subtipo pedido."""
    razones, falta = [], []
    tags = p["etiquetas"].split()
    psub = p.get("subtipo", "")
    qsub, qfam = getattr(q, "subtipo", None), getattr(q, "familia", None)
    factor_familia = 1.0
    if qfam:
        if p["familia"] == qfam or (qsub and qsub in (p.get("subtipos") or psub).split()):
            pass
        elif qfam in tags:
            factor_familia = 0.85
            razones.append(f"familia {qfam} secundaria")
        else:
            return None
    got = posible = maximo = 0.0

    def criterio(nombre, tiene_q, tiene_p, puntos, etiqueta=None):
        nonlocal got, posible, maximo
        if not tiene_q:
            return
        maximo += PESOS[nombre]
        if not tiene_p:
            falta.append(etiqueta or nombre)
            return
        posible += PESOS[nombre]
        got += puntos

    # subtipo
    psubs = (p.get("subtipos") or psub).split()
    if qsub:
        igual = psub == qsub
        tambien = not igual and qsub in psubs  # proyecto con varios equipos: el pedido es uno de ellos
        criterio("subtipo", True, bool(psub), PESOS["subtipo"] if igual else 20 if tambien else 0)
        if psub:
            razones.append(f"mismo subtipo ({SUBTIPO_NOMBRE.get(qsub, qsub)})" if igual else
                           f"incluye {SUBTIPO_NOMBRE.get(qsub, qsub)}" if tambien else f"otro subtipo: {SUBTIPO_NOMBRE.get(psub, psub)}")
    # texto: palabras del pedido presentes en el proyecto, ponderadas por rareza
    qw = set(palabras(canon(norm(q.texto)))) if q.texto else set()
    if qw:
        pw = set(p["palabras"].split())
        comunes = qw & pw
        tot = sum(idf.get(w, 3) for w in qw)
        criterio("texto", True, True, PESOS["texto"] * sum(idf.get(w, 3) for w in comunes) / tot if tot else 0)
        if comunes:
            razones.append("texto: " + ", ".join(sorted(comunes, key=lambda w: -idf.get(w, 3))[:5]))
    # tamaño: cuerpo en recipientes; si no, línea
    dias = [float(x) for x in p["diametros"].split()]
    pc = num(p.get("diametro_cuerpo"))
    qc = getattr(q, "cuerpo", None)
    recipiente = (qfam in RECIPIENTES) or SUBTIPO_FAMILIA.get(qsub) in RECIPIENTES
    if recipiente and qc:
        if pc:
            r = abs(qc - pc) / max(qc, pc)
            pts = PESOS["tamano"] if r <= 0.10 else 7 if r <= 0.30 else 0
            criterio("tamano", True, True, pts)
            razones.append(f'Ø cuerpo {fmtg(pc)}"' + ("" if pts == PESOS["tamano"] else " (cercano)" if pts else " (otro tamaño)"))
        elif q.diametro and dias:  # sin cuerpo: las conexiones valen la mitad
            pts = 7.5 if q.diametro in dias else 3.5 if any(vecino(q.diametro, d) for d in dias) else 0
            criterio("tamano", True, True, pts)
            falta.append("Ø cuerpo")
        else:
            criterio("tamano", True, False, 0, "Ø cuerpo")
    elif q.diametro:
        if q.diametro in dias:
            criterio("tamano", True, True, PESOS["tamano"]); razones.append(f'Ø{fmtg(q.diametro)}"')
        elif any(vecino(q.diametro, d) for d in dias):
            criterio("tamano", True, True, 7); razones.append(f'Ø cercano ({", ".join(fmtg(d) for d in dias if vecino(q.diametro, d))}")')
        else:
            criterio("tamano", True, bool(dias), 0, "Ø")
    if q.serie:
        ps = p["series"].split()
        criterio("serie", True, bool(ps), PESOS["serie"] if q.serie in ps else 0)
        if q.serie in ps:
            razones.append(f"serie {q.serie}")
    if q.material:
        pm = p["material"].split()
        criterio("material", True, bool(pm), PESOS["material"] if q.material in pm else 0)
        if q.material in pm:
            razones.append(q.material)
    if q.union:
        pu = p["union"].split()
        criterio("union", True, bool(pu), PESOS["union"] if q.union in pu else 0)
        if q.union in pu:
            razones.append(q.union)
    if q.cliente:
        mismo = norm(q.cliente) in norm(p["cliente"] + " " + p.get("cliente_final", "") + " " + p["id"])
        criterio("cliente", True, True, PESOS["cliente"] if mismo else 0)
        if mismo:
            razones.append("mismo cliente")
    s = 100 * got / posible * (0.7 + 0.3 * posible / maximo) if posible else 0.0
    if p.get("tiene_planilla_costo"):
        s += 5; razones.append("PLANILLA DE COSTO")
    if p.get("proveedores") not in (None, "", "0"):
        s += 2
    if p.get("tiene_oc"):
        s += 2; razones.append("ganada (OC)")
    if p.get("confianza") == "baja":
        s -= 5
    if p.get("origen") == "carpeta sin ficha":
        razones.append("SIN FICHA (año estimado)")
    if falta:
        razones.append("sin dato: " + ", ".join(falta))
    anios = max(0.0, (hoy - date.fromisoformat(p["fecha"])).days / 365.25) if p["fecha"] else 3
    factor_edad = max(0.4, 1 - 0.2 * anios)
    return s * factor_familia * factor_edad, razones, factor_edad


def buscar(q, filas=None, historico=None, hoy=None, excluir=(), con_precio=False):
    """Lista principal (índice 2025–2026 + carpetas 2025–2026 sin ficha) y, si hay pocos del mismo subtipo, las
    carpetas sin ficha anteriores. Cada resultado: (puntaje, razones, factor de antigüedad, fila)."""
    filas = leer(INDICE) if filas is None else filas
    historico = leer(HISTORICO) if historico is None else historico
    hoy = hoy or date.today()
    nuevas = [r for r in historico if r["fecha"] >= "2025-01-01"]
    viejas = [r for r in historico if r["fecha"] < "2025-01-01"]
    idf = idf_de(filas)  # solo el índice: igual que la página

    def correr(lista):
        res = []
        for p in lista:
            if any(x and x.lower() in (p["id"] + " " + p.get("origen", "")).lower() for x in excluir):
                continue
            if con_precio and not p.get("precio_unitario_principal"):
                continue
            r = puntuar(p, q, idf, hoy)
            if r:
                res.append((r[0], r[1], r[2], p))
        res.sort(key=lambda x: (round(x[0], 1), x[3]["fecha"]), reverse=True)  # empate: el más nuevo primero
        return res

    principal = correr(filas + ([] if con_precio else nuevas))
    if q.subtipo:
        mismos = sum(1 for r in principal if q.subtipo in (r[3].get("subtipos") or r[3].get("subtipo", "")).split())
    else:
        mismos = sum(1 for r in principal if r[3]["familia"] == q.familia) if q.familia else len(principal)
    anteriores = correr(viejas) if mismos < MINIMO_MISMO_SUBTIPO and not con_precio else []
    if q.subtipo:
        anteriores = [r for r in anteriores if q.subtipo in (r[3].get("subtipos") or r[3].get("subtipo", "")).split()] or anteriores
    return principal, anteriores, mismos


def imprimir(i, s, razones, fe, p):
    pu = p.get("precio_unitario_principal")
    datos = " · ".join(x for x in [
        f"{fmt(float(p['monto']), 0)} {p['moneda']}" if p.get("monto") else "",
        f"unit. {fmt(float(pu), 0)}" if pu else "", f"factor {fmt(float(p['factor']), 2)}" if p.get("factor") else "",
        f"{fmt(float(p['plazo_dias']), 0)} días" if p.get("plazo_dias") else "", p.get("resultado", "")] if x)
    sub = SUBTIPO_NOMBRE.get(p.get("subtipo", ""), "")
    print(f"{i}. [{fmt(s, 0)}] {p['fecha'][:4] if p.get('fecha_estimada') else p['fecha']} · {p['id']}")
    print(f"   {p['familia']}{' · ' + sub if sub else ''}{' · Ø cuerpo ' + fmtg(float(p['diametro_cuerpo'])) + chr(34) if p.get('diametro_cuerpo') else ''} · {p['descripcion'][:150]}")
    if datos:
        print(f"   {datos}")
    print(f"   Por qué: {'; '.join(razones) or '—'} · antigüedad ×{fmt(fe, 2)}")
    print(f"   Abrir: {p['carpeta_textos']}" + (f"  |  ficha: {p['ficha']}" if p.get("ficha") else "") + "\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--familia", help="código de familia (CO, P, SK, F, ...); si no, se deduce del texto")
    ap.add_argument("--subtipo", help="subtipo (coalescente, filtro_canasto, bifasico, puente_medicion…; ver --familias)")
    ap.add_argument("--texto", default="", help="qué es: tipo de equipo, servicio, norma…")
    ap.add_argument("--diametro", type=float, help='Ø de línea principal en pulgadas (ej. 6 o 2.5)')
    ap.add_argument("--cuerpo", type=float, help='Ø del cuerpo en pulgadas (recipientes: separadores, filtros, tanques, calentadores)')
    ap.add_argument("--serie", help="serie o rating: 150, 300, 600, 900, 1500, 2000, 3000…")
    ap.add_argument("--material", choices=["carbono", "inoxidable"])
    ap.add_argument("--union", choices=["roscado", "bridado"])
    ap.add_argument("--cliente")
    ap.add_argument("--cotizacion", help="carpeta de una cotización: arma la consulta desde su cotizacion.json")
    ap.add_argument("--top", type=int, default=8)
    ap.add_argument("--excluir", action="append", default=[], help="texto del id a excluir (ej. la propia cotización); repetible")
    ap.add_argument("--hoy", default=date.today().isoformat())
    ap.add_argument("--familias", action="store_true", help="listar familias y subtipos")
    a = ap.parse_args()
    filas = leer(INDICE)
    if a.familias:
        c = Counter(t for r in filas for t in r["etiquetas"].split())
        cs = Counter(r.get("subtipo", "") for r in filas)
        ch = Counter(r.get("subtipo", "") for r in leer(HISTORICO))
        for k, v in FAMILIAS.items():
            print(f"{k:4} {v:32} {c.get(k, 0):3} proyectos ({sum(1 for r in filas if r['familia'] == k)} como familia principal)")
            for s, f in SUBTIPO_FAMILIA.items():
                if f == k:
                    print(f"       {s:22} {SUBTIPO_NOMBRE[s]:42} {cs.get(s, 0):3} (+{ch.get(s, 0)} sin ficha)")
        return
    if a.cotizacion:
        carpeta = Path(a.cotizacion)
        c = json.load(open(carpeta / "cotizacion.json", encoding="utf-8"))
        q = consulta_de_cotizacion(c, next((r for r in filas if r["id"] == carpeta.name), None))
        a.excluir.append(carpeta.name)
    else:
        if a.familia and a.familia.upper() not in FAMILIAS:
            sys.exit(f"Familia desconocida: {a.familia}. Opciones: {', '.join(FAMILIAS)}")
        if a.subtipo and a.subtipo not in SUBTIPO_FAMILIA:
            sys.exit(f"Subtipo desconocido: {a.subtipo}. Opciones: {', '.join(SUBTIPO_FAMILIA)}")
        q = consulta(a.texto, a.familia, a.subtipo, a.diametro, a.cuerpo, a.serie, a.material, a.union, a.cliente)
    principal, anteriores, mismos = buscar(q, filas, hoy=date.fromisoformat(a.hoy), excluir=a.excluir)
    print(f"Consulta: familia {q.familia or '(todas)'}" + (f" · subtipo {SUBTIPO_NOMBRE.get(q.subtipo, q.subtipo)}" if q.subtipo else " · sin subtipo")
          + (f' · Ø cuerpo {fmtg(q.cuerpo)}"' if q.cuerpo else "") + (f' · Ø {fmtg(q.diametro)}"' if q.diametro else "")
          + (f" · serie {q.serie}" if q.serie else "") + (f" · {q.cliente}" if q.cliente else ""))
    print(f"{len(principal)} proyectos en el índice (2025–2026); {mismos} del mismo {'subtipo' if q.subtipo else 'grupo'}. "
          f"Los {min(a.top, len(principal))} más parecidos:\n")
    for i, (s, razones, fe, p) in enumerate(principal[:a.top], 1):
        imprimir(i, s, razones, fe, p)
    if anteriores:
        print(f"Hay menos de {MINIMO_MISMO_SUBTIPO} del mismo {'subtipo' if q.subtipo else 'grupo'} en 2025–2026. "
              "Carpetas anteriores sin ficha (año estimado, sin precios: solo para comparar diseño y alcance):\n")
        for i, (s, razones, fe, p) in enumerate(anteriores[:5], 1):
            imprimir(i, s, razones, fe, p)


if __name__ == "__main__":
    main()
