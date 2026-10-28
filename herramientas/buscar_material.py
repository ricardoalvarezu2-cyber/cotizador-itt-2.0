"""Busca un material en el catálogo: primero los IGUALES, después los SIMILARES (diciendo en qué difieren),
con el último precio, su fecha y la ruta de dónde salió.

Uso:
  python herramientas/buscar_material.py "valvula retencion 2\\" serie 600 A216 WCB trim 316 NPT"
  python herramientas/buscar_material.py "brida WN 4\\" 600# RF sch 80 A105" --top 10
  python herramientas/buscar_material.py --familia CAN "caño 2\\" sch 80 A106"   (forzar familia)
  python herramientas/buscar_material.py "valvula retencion 2\\" serie 600 A216 WCB NPT" --marca Danco

Igual = coinciden todas las características que definen el material en su familia (ver catalogo_materiales.py).
Similar = misma familia y tipo, con alguna diferencia: se lista cuál. Un precio de un similar sirve de referencia,
pero en la cotización va con "coincide": "similar" y la diferencia.

Marca (válvulas e instrumentos): la marca NO cuenta para igual/similar. Con --marca (o si la descripción nombra una
marca), primero salen los iguales de esa marca y después los "IGUAL (otra marca)", para poder elegir. Sin marca pedida,
los iguales se ordenan por fecha y se muestra la marca de cada uno. Cotizar una marca distinta de la que pide el cliente
(o de la lista de marcas aprobadas del pliego) es un desvío: va con "coincide": "similar" y la diferencia "marca".
"""
import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from catalogo_materiales import FAMILIAS, MARCAS, PRECIOS, atributos, expandir, familia_de  # noqa: E402
from indice_proyectos import norm  # noqa: E402

NOMBRE_A_COD = {v[0]: k for k, v in FAMILIAS.items()}
CON_TIPO = ("VAL", "AFO", "ABW", "BRI", "JUN", "INS")


_FILAS = None


def buscar(texto, familia=None, marca_pedida=""):
    """Búsqueda en el catálogo (la usan este comando y precotizar.py).
    Devuelve (familia, atributos leídos, marca, faltan, resultados). Cada resultado: (igual, misma_marca, -n_difs,
    tiene_precio, coincidencias, fecha, difs, renglón del catálogo), ordenados del mejor al peor."""
    global _FILAS
    if _FILAS is None:
        _FILAS = list(csv.DictReader(open(PRECIOS / "catalogo_materiales.csv", encoding="utf-8")))
    t = expandir(norm(texto))
    fam = familia or familia_de(t)
    at = atributos(t, fam)
    marca = MARCAS.get(norm(marca_pedida), marca_pedida.strip()) if marca_pedida else at.get("marca", "")
    campos = [c for c in (FAMILIAS[fam][2] or ["tipo"]) if c not in ("marca", "modelo")]
    opcionales = {"diametro2", "trim", "schedule", "cara", "medida", "extremos"}
    if fam == "CAN":  # alcanza con schedule o espesor
        opcionales |= {"revestimiento"} | ({"espesor_mm"} if at.get("schedule") else {"schedule"} if at.get("espesor_mm") else set())
    if fam == "JUN":  # bulonería: Ø, material y largo; juntas: Ø y serie
        opcionales |= {"serie"} if at.get("tipo") in ("esparrago", "bulon", "tuerca", "arandela") else {"material"}
        if at.get("tipo") in ("esparrago", "bulon"):
            opcionales.discard("medida")
    if fam == "VAL" and not str(at.get("tipo", "")).startswith("esferica"):
        opcionales.add("paso")  # el paso (total/reducido) solo distingue esféricas
    faltan = [c for c in campos if not at.get(c) and c not in opcionales]
    filas = [r for r in _FILAS if NOMBRE_A_COD.get(r["familia"]) == fam]
    res = []
    for r in filas:
        coinc, difs = 0, []
        for c in campos:
            if fam == "CAN" and c == "espesor_mm" and at.get("schedule") and r.get("schedule"):
                continue
            a, b = norm(at.get(c, "")), norm(r.get(c, ""))
            if a == b:
                coinc += 1 if a else 0
            elif a and b:
                difs.append(f"{c}: {r[c]} (pedido {at[c]})")
            elif a:
                difs.append(f"{c}: sin dato (pedido {at[c]})")
            else:
                difs.append(f"{c}: {r[c]} (no pedido)")
        if at.get("tipo") and r.get("tipo") and norm(at["tipo"]) != norm(r["tipo"]):
            continue  # otro tipo de pieza: no es ni similar
        if fam in CON_TIPO and bool(at.get("tipo")) != bool(r.get("tipo")):
            continue  # sin tipo de un lado no se sabe qué pieza es: no se compara (ej. junta monolítica vs junta sin tipo)
        if coinc == 0:
            continue
        oblig = [c for c in campos if c not in opcionales]
        igual = not difs and all(at.get(c) for c in oblig)
        misma_marca = bool(marca) and norm(r.get("marca", "")) == norm(marca)
        res.append((igual, misma_marca, -len(difs), bool(r["ultimo_precio_usd"]), coinc, r["fecha_ultimo_precio"], difs, r))
    res.sort(key=lambda x: x[:6], reverse=True)  # a igual parecido, primero el que tiene precio confiable
    return fam, at, marca, faltan, res


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("texto")
    ap.add_argument("--familia", choices=list(FAMILIAS))
    ap.add_argument("--top", type=int, default=8)
    ap.add_argument("--marca", default="", help="marca pedida (válvulas e instrumentos): sale primero, el resto como 'otra marca'")
    q = ap.parse_args()
    fam, at, marca, faltan, res = buscar(q.texto, q.familia, q.marca)
    print(f"Familia: {FAMILIAS[fam][0]} · características leídas: " + ", ".join(f"{k}={v}" for k, v in at.items() if k != "marca")
          + (f" · marca pedida: {marca}" if marca else ""))
    if faltan:
        print(f"Faltan en la búsqueda: {', '.join(faltan)}. Agregalas para distinguir igual de similar.")
    if not res:
        print("No hay precios de esa familia y tipo en el catálogo. Pedir cotización a Compras.")
        return
    if marca and fam in ("VAL", "INS") and not any(x[1] for x in res):
        print(f"No hay precios de la marca {marca} para esta pieza: se listan otras marcas.")
    for i, (igual, misma, _, _, coinc, _, difs, r) in enumerate(res[:q.top], 1):
        estado = "IGUAL" if igual else "SIMILAR"
        if marca and fam in ("VAL", "INS") and not misma:
            estado += " (otra marca)"
        mm = ""
        if fam in ("VAL", "INS"):
            mm = f" · marca: {r.get('marca') or 'sin identificar'}" + (f" · modelo {r['modelo']}" if r.get("modelo") else "")
        print(f"\n{i}. {estado} · {r['codigo']}{mm} · {r['descripcion'][:110]}")
        if not r["ultimo_precio_usd"]:
            print(f"   SIN PRECIO CONFIABLE: solo hay valores del período con cepo (referencia descartada USD "
                  f"{float(r['referencia_descartada_usd']):,.2f} del {r['fecha_referencia_descartada']}, {r['proveedor']}). Pedir cotización.")
        else:
            print(f"   Último precio: USD {float(r['ultimo_precio_usd']):,.2f} / {r['unidad'] or 'unidad s/d'} · {r['fecha_ultimo_precio']} · {r['tipo_precio']} · {r['proveedor']}")
            print(f"   Ajustado a hoy: USD {float(r['precio_ajustado_hoy_usd']):,.2f} · {r['precios_en_historial']} precio(s) en el historial"
                  + (f" (entre {float(r['precio_min_usd']):,.2f} y {float(r['precio_max_usd']):,.2f})" if int(r["precios_en_historial"]) > 1 else ""))
        if r.get("alerta") and r["ultimo_precio_usd"]:
            print(f"   ALERTA: {r['alerta']}")
        if difs:
            print(f"   Difiere en: {'; '.join(difs)}")
        print(f"   Origen: {r['ruta_origen']}" + (f" · {r['archivo_origen']}" if r["archivo_origen"] else ""))
        if r["ruta_repo"]:
            print(f"   En el repo: {r['ruta_repo']}")


if __name__ == "__main__":
    main()
