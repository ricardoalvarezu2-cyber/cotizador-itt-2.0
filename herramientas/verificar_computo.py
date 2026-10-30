"""Control automático de una cotización contra la tabla de materiales del plano.

Uso: python herramientas/verificar_computo.py cotizaciones/<carpeta>

Necesita en la carpeta:
  pedido/lista_materiales_plano.csv  (pos, descripcion, diametro, serie_sch, material, extremos, modelo_fabricante, cantidad, unidad)
  computo.csv                        (id, pos, descripcion, cant_por_puente, unidad, precio_unit_usd, subtotal_usd,
                                      tipo_origen, proveedor_o_criterio, carpeta_origen, fecha_precio)

ERRORES (impiden pasar a "revisado"):
  - posición del plano que falta en el cómputo, o con otra cantidad
  - posición del cómputo que no está en el plano (salvo filas de compra extra con sufijo, ej. 14b)
  - precio sin proveedor, origen o fecha
  - subtotal distinto de cantidad × precio
  - descripción distinta de la del cliente, o cantidad que el cliente no indica sin aclarar (con pedido/transcripcion.json)
AVISOS (revisar uno por uno):
  - extremos BW/SW: soldaduras que tienen que estar contadas en la MO
  - modelo o fabricante exigido por el plano
  - precios estimados y su peso en el costo
  - precios con más de 6 meses
Ver conocimiento/procedimiento_cotizacion.md.
"""
import csv
import re
import sys
from datetime import date
from pathlib import Path
from numeros import fmt, fmtg, cantidad_plano


def num(v):
    v = str(v or "").strip().replace(" ", "")
    if "," in v and "." in v:
        v = v.replace(".", "").replace(",", ".")
    return float(v.replace(",", ".")) if v else None


def control_compatibilidad(c, plano, avisos=None):
    """P9 (Matías, 30-10-2026): cada renglón de material con precio se compara con lo que pide el plano con las reglas de
    compatibilidad (compatibilidad.py). Si la norma no permite el reemplazo, es ERROR: la cotización no pasa a revisado
    hasta cambiar la referencia o dejarla SIN PRECIO. Se controla la fuente vigente.
    Auditoría 30-10-2026: también las filas que no están en el plano (5c, 14b: se comparan con su fila madre si usan la
    misma pieza, o con su propia descripción), las fuentes sin código del catálogo (con el texto de la fuente) y el tipo
    y la serie de la pieza (ERROR si difieren); otro Ø es AVISO."""
    ruta = c / "cotizacion.json"
    if not ruta.exists():
        return []
    import json
    import buscar_material as bm
    from compatibilidad import (incompatible, regla_material, clases, dn_de, regla_conexion, conexiones, regla_revestimiento,
                                regla_sch_doble, prep, FAMILIAS_SCH, SCH_DOBLE)
    from precotizar import texto_busqueda
    bm.buscar("brida")
    cat = {r["codigo"]: r for r in bm._FILAS}
    por_lista = {m.group(1): r["codigo"] for r in bm._FILAS if (m := re.search(r"^Renard \(cód\. (\d+)\)", r.get("proveedor", "")))}
    por_pos = {p["pos"].strip(): p for p in plano}
    items = json.load(open(ruta, encoding="utf-8"))["items"]
    # códigos de las listas de Renard que no están en el catálogo (tercera auditoría: CAPEX pos 8 y 17)
    lista_renard = {}
    for lr in sorted((Path(__file__).resolve().parent.parent / "conocimiento" / "precios").glob("lista_renar_*.csv")):
        lista_renard.update({x["codigo"]: x["producto"] for x in csv.DictReader(open(lr, encoding="utf-8"))})
    # desvíos declarados en la oferta, por posición ("Accesorios forjados (pos. 1, 8, 10): serie 3000…")
    desvios = {}
    if (c / "oferta.json").exists():
        of = json.load(open(c / "oferta.json", encoding="utf-8"))
        for x in (of.get("aclaraciones_y_desvios") or {}).get("items", []):
            for grupo in re.findall(r"(?i)\bpos(?:ición|iciones|\.)?\s*((?:[\w]+(?:\s*(?:,|y)\s*)?)+)", str(x)):
                for n in re.findall(r"\b\d+[a-z]?\b", grupo):
                    desvios.setdefault(n, str(x))
    cod_de = lambda f: f.get("codigo") or (re.search(r"\b[A-Z]{3}-\d{5}\b", str(f.get("proveedor") or "")) or [None])[0]
    cod_pos = {str(it.get("pos", "")).strip(): cod_de(it["fuentes"][0]) for it in items if it.get("fuentes")}
    out = []
    for it in items:
        if it.get("grupo") != "material" or not it.get("fuentes"):
            continue
        f = it["fuentes"][0]
        if not f.get("precio"):
            continue
        cod = cod_de(f)
        if not cod:  # "Renard · cód. 5979": la pieza del catálogo de esa lista (segunda auditoría 30-10-2026)
            m = re.search(r"(?i)\b(renard|renar)\b.*?c[óo]d\.? ?(\d+)", str(f.get("proveedor") or ""))
            cod = por_lista.get(m.group(2)) if m else None
        pos = str(it.get("pos", "")).strip()
        madre = re.match(r"\d+", pos)
        p = por_pos.get(pos)
        desc_it = f"{it.get('descripcion', '')} {it.get('especificacion', '')}"
        if str(it.get("descripcion", "")).startswith("["):
            continue  # renglón de la plantilla (casos de control: cotizacion.json solo trae parámetros)
        if not p and madre and madre.group(0) != pos and madre.group(0) in por_pos and (
                (cod and cod_pos.get(madre.group(0)) == cod) or re.search(rf"\bpos\.? ?{madre.group(0)}\b", desc_it.lower())
                or not clases(desc_it)):
            # compra extra de la pieza de la fila madre (14b) o fila sin material propio: se compara con lo que pide el
            # plano en la fila madre (segunda auditoría 30-10-2026: una 21b con otra pieza pasaba sin control)
            p = por_pos.get(madre.group(0))
        texto = texto_busqueda(p) if p else desc_it
        if not p and not clases(texto):
            # fila agregada por ITT (EST, INS…) sin material en su descripción: no hay con qué comparar
            if avisos is not None:
                avisos.append(f"Pos {pos}: fila agregada sin material en la descripción ({desc_it[:45]}): controlar a mano la referencia")
            continue
        fam, at, *_ = bm.buscar(texto)
        documentado = f.get("coincide") == "similar" and str(f.get("diferencia") or "").strip()

        def serie_mal(serie_cand):
            """Otra serie (rating) no es similar (Matías, 29-10-2026). Una serie mayor solo pasa como desvío declarado en
            la oferta (abajo), nunca escrita solo en la fuente: el cliente tiene que enterarse (tercera auditoría)."""
            sp, sc = re.sub(r"\D", "", str(at.get("serie") or "")), re.sub(r"\D", "", str(serie_cand or ""))
            if not sp or not sc or sp == sc:
                return ""
            return f"serie {sc} por {sp} (otro rating)"
        if cod in cat:
            r = cat[cod]
            motivo = incompatible(fam, at, r, texto, r["descripcion"])
            if not motivo:
                motivo = serie_mal(r.get("serie"))
            if not motivo and avisos is not None and at.get("tipo") and r.get("tipo") and bm.norm(at["tipo"]) != bm.norm(r["tipo"]) and not documentado:
                # el tipo del pedido se lee del texto y puede estar mal leído ("manómetros" en una nota): AVISO, no ERROR
                avisos.append(f"Pos {pos}: la referencia {cod} es de otro tipo ({r['tipo']} por {at['tipo']}): confirmar que sea la misma pieza")
            if not motivo and avisos is not None and at.get("diametro") and r.get("diametro") and dn_de(at["diametro"]) != dn_de(r["diametro"]):
                avisos.append(f"Pos {pos}: la referencia {cod} es de otro Ø ({r['diametro']} por {at['diametro']}): justificar")
            desc = r["descripcion"]
        else:
            # fuente sin pieza del catálogo (planilla, cotización): se compara el material con el texto de la fuente
            # (sin lo que la fuente dice del pedido: "el plano pide NPT", "(pedido #150)"); también conexión y serie
            desc = f"{f.get('proveedor', '')} {f.get('diferencia', '')}"
            mr = re.search(r"(?i)\b(renard|renar)\b.*?c[óo]d\.? ?(\d+)", str(f.get("proveedor") or ""))
            if mr and mr.group(2) in lista_renard:  # la descripción de la lista, no la nota de quien cargó
                desc = f"{lista_renard[mr.group(2)]} {f.get('diferencia', '')}"
            limpio = re.sub(r"(?i)\(?\b(?:el plano pide|plano pide|pedid[oa]s?|se pide|pide)\b[^)\];]*\)?", " ", desc)
            motivo = ""
            if clases(texto):
                if clases(limpio):
                    motivo = regla_material(fam, texto, limpio, limpio)
                elif avisos is not None:
                    avisos.append(f"Pos {pos}: la fuente ({desc[:50]}) no dice el material: verificar en el original que sea el que pide el plano")
            if not motivo:
                motivo = regla_conexion(conexiones(at.get("extremos", ""), at.get("cara", "")), conexiones(limpio))
            # revestimiento y schedule por extremo: solo si la fuente los menciona (una planilla sin descripción no los dice:
            # aviso, como con el material)
            if not motivo and re.search(r"(?i)revest|tricapa|polipropileno|polietileno|\bfbe\b|epoxi", limpio):
                motivo = regla_revestimiento(prep(texto), prep(limpio))
            if not motivo and fam in FAMILIAS_SCH:
                if re.search(r"(?i)\bsch|\bstd\b|\bxs\b", limpio):
                    motivo = regla_sch_doble(bm.norm(texto), bm.norm(limpio), at.get("diametro"))
                elif avisos is not None and re.search(SCH_DOBLE, bm.norm(texto)):
                    avisos.append(f"Pos {pos}: la fuente ({desc[:50]}) no dice el schedule de cada extremo: verificarlo en el original")
            if not motivo:
                ms = re.search(r"#\s?(\d{3,4})\b|\b(\d{3,4})\s?(?:#|lbs?\b)|\bserie\s?(\d{3,4})\b|\bs(\d{3,4})\b|\bwog\s?(\d{3,4})\b"
                               r"|\b(?:clase|class|cl\.?|ansi)\s?(\d{3,4})\b", limpio.lower())
                motivo = serie_mal(next(g for g in ms.groups() if g)) if ms else ""
        madre_n = madre.group(0) if madre else pos
        if motivo and (pos in desvios or madre_n in desvios):
            # la oferta declara el desvío en esa posición (el cliente se entera): AVISO; si el desvío sigue entre
            # [corchetes] ("a confirmar"), hay que resolverlo antes de enviar (tercera auditoría 30-10-2026)
            d = desvios.get(pos) or desvios[madre_n]
            if avisos is not None:
                avisos.append(f"Pos {pos}: desvío declarado en la oferta ({motivo[:80]})" +
                              (": SIGUE A CONFIRMAR en la oferta, resolverlo antes de enviar" if "[" in d else ""))
            continue
        if motivo and f.get("tipo") == "est":
            # un ESTIMADO armado sobre otra pieza no se salva por ser estimado: sin desvío declarado en la oferta la oferta
            # afirmaría cumplimiento (tercera auditoría 30-10-2026; lección 12)
            out.append(f"Pos {pos}: ESTIMADO sobre una pieza que la norma no admite ({motivo[:90]}) y la oferta no declara el "
                       "desvío en esa posición: declararlo en aclaraciones y desvíos o pedir cotización")
            continue
        if motivo:
            out.append(f"Pos {pos}: la referencia {cod or ''} ({desc[:45]}) no sirve según la norma: {motivo}. "
                       "Cambiarla por una compatible o dejar SIN PRECIO (compatibilidades_LEEME.md)")
    return out


def main(carpeta):
    c = Path(carpeta)
    plano = list(csv.DictReader(open(c / "pedido" / "lista_materiales_plano.csv", encoding="utf-8")))
    comp = list(csv.DictReader(open(c / "computo.csv", encoding="utf-8")))
    errores, avisos = [], []

    por_pos = {}
    for r in comp:
        por_pos.setdefault(r["pos"].strip(), []).append(r)
    pos_plano = {p["pos"].strip() for p in plano}

    for p in plano:
        filas = por_pos.get(p["pos"].strip())
        if not filas:
            errores.append(f"Pos {p['pos']} ({p['descripcion'][:40]}) no está en el cómputo")
            continue
        cant = sum(num(f["cant_por_puente"]) or 0 for f in filas)
        largo = re.search(r"(\d+)\s*mm", p["descripcion"])
        if p.get("unidad", "un") == "un" and filas[0]["unidad"] == "m" and largo:
            esperado = int(largo.group(1)) / 1000 * cantidad_plano(p["cantidad"])
            if abs(cant - esperado) > 1e-6:
                errores.append(f"Pos {p['pos']}: el plano pide {p['cantidad']} × {largo.group(1)} mm = {fmtg(esperado)} m y el cómputo tiene {fmtg(cant)} m")
        elif p.get("unidad", "un") == "un" and filas[0]["unidad"] != "un":
            errores.append(f"Pos {p['pos']}: el plano pide {p['cantidad']} un y el cómputo usa '{filas[0]['unidad']}'. "
                           "Si se compra por metro, la cantidad tiene que dar el largo del plano y el sobrante va en fila aparte")
        elif abs(cant - cantidad_plano(p["cantidad"])) > 1e-6:
            errores.append(f"Pos {p['pos']}: plano {p['cantidad']} / cómputo {fmtg(cant)}")
        ext = p.get("extremos", "").upper()
        if "BW" in ext or "SW" in ext:
            avisos.append(f"Pos {p['pos']} extremos {ext} × {p['cantidad']}: confirmar que la soldadura está contada (taller o campo)")
        if p.get("modelo_fabricante", "").strip():
            avisos.append(f"Pos {p['pos']}: el plano exige {p['modelo_fabricante']}. Confirmar que el precio es de ese modelo o declarar desvío")

    # REGLA CRÍTICA (Matías, 29-10-2026): la descripción es la del cliente, exacta; si el cliente no indica cantidad,
    # la calculada lleva la aclaración. Se controla contra pedido/transcripcion.json (copia textual del documento).
    ruta_tr = c / "pedido" / "transcripcion.json"
    if ruta_tr.exists():
        import json
        cliente = {}
        for t in json.load(open(ruta_tr, encoding="utf-8"))["tablas"]:
            cols = t["columnas"]
            iq = next((i for i, x in enumerate(cols) if x.upper().startswith("CANT")), None)
            for f in t["filas"]:
                cliente[str(f[0]).strip()] = (f[1], f[iq] if iq is not None else "")
        for p in plano:
            pos = p["pos"].strip()
            if pos not in cliente:
                errores.append(f"Pos {pos}: no está en la transcripción del documento del cliente")
                continue
            desc, q = cliente[pos]
            if " ".join(p["descripcion"].split()) != " ".join(str(desc).split()):
                errores.append(f"Pos {pos}: la descripción no es la del cliente. Cliente: «{desc}» · cómputo: «{p['descripcion']}»")
            if str(q).strip() in ("", "_", "-", "—") and "no indica cantidad" not in p.get("cantidad_origen", "").lower():
                errores.append(f"Pos {pos}: el cliente no indica cantidad; aclarar en cantidad_origen que la calculó ITT (según plano o ET)")
        for r in comp:
            base_pos = r["pos"].strip()
            if base_pos in cliente and not r["descripcion"].startswith(" ".join(str(cliente[base_pos][0]).split())):
                errores.append(f"{r['id']}: la descripción del cómputo no empieza con la del cliente («{cliente[base_pos][0]}»)")

    for pos, filas in por_pos.items():
        if pos in pos_plano:
            continue
        base = re.match(r"^(\d+)[a-z]$", pos)
        if base and base.group(1) in pos_plano:
            avisos.append(f"Pos {pos}: fila de compra extra (sobrante) de la pos {base.group(1)}")
        elif not re.match(r"^[A-Z]{2,4}$", pos):  # MO, PH, PIN, CAL, INS
            errores.append(f"Pos {pos} del cómputo no está en el plano")

    total = estimado = 0.0
    hoy = date.today()
    for r in comp:
        cant, precio, sub = num(r["cant_por_puente"]), num(r["precio_unit_usd"]), num(r["subtotal_usd"])
        if cant is None or precio is None:
            errores.append(f"{r['id']}: falta cantidad o precio")
            continue
        if sub is not None and abs(sub - cant * precio) > 0.05:
            errores.append(f"{r['id']}: subtotal {sub} distinto de {fmtg(cant)} × {precio}")
        total += cant * precio
        if not r.get("proveedor_o_criterio", "").strip() or not r.get("fecha_precio", "").strip():
            errores.append(f"{r['id']}: precio sin fuente o sin fecha")
        if r.get("coincidencia") == "similar":
            avisos.append(f"{r['id']}: precio de una pieza SIMILAR, no igual: {r.get('diferencia', '')}")
        f_ok = re.fullmatch(r"\d{4}-\d{2}-\d{2}", r.get("fecha_precio", "").strip() or "")
        if r.get("fecha_precio", "").strip() and (not f_ok or r["fecha_precio"] > hoy.isoformat()):
            errores.append(f"{r['id']}: fecha de precio inválida o futura ({r['fecha_precio']}): usar AAAA-MM-DD real del documento")
        if re.search(r"con iva|iva incluido|c/ ?iva", (r.get("proveedor_o_criterio", "") + " " + r.get("diferencia", "")).lower()):
            avisos.append(f"{r['id']}: la fuente menciona 'con IVA': el precio tiene que estar SIN IVA (dividir por 1,21 o 1,105)")
        if precio and r.get("coincidencia", "").strip() == "sin_ref":
            errores.append(f"{r['id']}: precio {fmtg(precio)} sin referencia ni pieza parecida ({r['descripcion'][:45]}): no se adivina, va en 0 y se pide cotización (P4 ter)")
        if precio == 0:
            avisos.append(f"{r['id']}: SIN PRECIO ({r['descripcion'][:45]}): pedir cotización antes de presentar")
        if r.get("tipo_origen", "").strip().lower() == "estimado":
            estimado += cant * precio
            avisos.append(f"{r['id']}: precio ESTIMADO ({r['descripcion'][:45]}) USD {fmt(cant * precio, 2)}")
        m = re.match(r"(\d{4})-(\d{2})", r.get("fecha_precio", ""))
        if m:
            meses = (hoy.year - int(m.group(1))) * 12 + hoy.month - int(m.group(2))
            if meses > 6 and r.get("tipo_origen", "").lower() != "estimado":
                avisos.append(f"{r['id']}: precio de hace {meses} meses ({r['fecha_precio']}), actualizar")
            # decisión de Matías (28/10/2026): valores de antes del fin del cepo sin tipo de cambio explícito no son confiables
            if r.get("fecha_precio", "") < "2025-04-14" and not re.search(r"tc |tipo de cambio|tc explícito|tc explicito", (r.get("proveedor_o_criterio", "") + " " + r.get("nota", "")).lower()):
                avisos.append(f"{r['id']}: precio del período con cepo ({r['fecha_precio']}) sin tipo de cambio explícito: reemplazar por un valor confiable o justificar (por ejemplo, costo de planta oct-2024: TC 997 en la hoja Sueldos)")

    errores += control_compatibilidad(c, plano, avisos)

    print(f"Plano: {len(plano)} posiciones · Cómputo: {len(comp)} filas · Costo directo por unidad USD {fmt(total, 2)}")
    if total:
        print(f"Estimado sin fuente: USD {fmt(estimado, 2)} ({estimado / total:.0%} del costo directo)"
              + ("  ← más del 15%, justificar" if estimado / total > 0.15 else ""))
    print(f"\nERRORES ({len(errores)})")
    for e in errores:
        print("  ✗", e)
    print(f"\nAVISOS ({len(avisos)})")
    for a in avisos:
        print("  !", a)
    return 1 if errores else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1]))
