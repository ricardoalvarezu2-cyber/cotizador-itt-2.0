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


A_CONFIRMAR = "DESVÍO A CONFIRMAR · "
SIN_RESOLVER = r"\[|a confirmar|a definir|confirmar con|por confirmar|pendiente|a cotizar"


def firma_p9(cot):
    """Lo que P9 controló de una cotización: la página no deja pasar a revisado ni aprobar si sus renglones de material
    ya no son los que controló el repositorio (sexta auditoría 30-10-2026). La misma cuenta en web/src/busqueda.js."""
    out = []
    for it in cot.get("items", []):
        if it.get("grupo") != "material" or not it.get("fuentes"):
            continue
        f = it["fuentes"][0]
        dv = ";".join(f"{d.get('que', '')}:{d.get('ofrecido', '')}:{d.get('pedido', '')}" for d in (it.get("desvio") or []) if isinstance(d, dict))
        out.append(f"{it.get('id', '')}|{it.get('pos', '')}|{f.get('codigo') or ''}|{f.get('proveedor') or ''}|{float(f.get('precio') or 0):.4f}|{dv}")
    return "\n".join(out)
TIPOS_DESVIO = ("material", "extremos", "schedule", "revestimiento", "costura", "nace", "serie")


def desvios_oferta(c):
    """{pos: [textos]} de aclaraciones y desvíos de la oferta: "(pos. 1, 8, 10 y 11)", "pos. 1 a 5", "pos. 21-23"."""
    import json
    out = {}
    if not (c / "oferta.json").exists():
        return out
    of = json.load(open(c / "oferta.json", encoding="utf-8"))
    for x in (of.get("aclaraciones_y_desvios") or {}).get("items", []):
        x = str(x)
        for m in re.finditer(r"(?i)\bpos(?:ición|iciones|\.)?\s*(\d+[a-z]?(?:\s*(?:,|y|e|a|-|–)\s*\d+[a-z]?)*)", x):
            for a, sep, b in re.findall(r"(\d+[a-z]?)(?:\s*(a|-|–)\s*(\d+)(?![a-z]))?", m.group(1)):
                nums = [str(n) for n in range(int(a), int(b) + 1)] if b and a.isdigit() and int(b) - int(a) < 60 else [a]
                for n in nums:
                    out.setdefault(n, []).append(x)
    return out


def revisar_desvios(pos, it, mots, textos_oferta):
    """Quinta auditoría (30-10-2026): el desvío es un DATO del renglón, no una frase de la oferta. it["desvio"] es una
    lista de {"que": tipo, "ofrecido": "...", "pedido": "..."}; hace falta uno por cada tipo de motivo, sin nada "a
    confirmar", y que la oferta lo muestre: un texto de aclaraciones y desvíos que nombre la posición y lo ofrecido.
    Devuelve (errores, avisos)."""
    err, av = [], []
    lista = [d for d in (it.get("desvio") or []) if isinstance(d, dict)]
    tipos = [str(d.get("que", "")).lower() for d in lista]
    for t in sorted({t for t in tipos if tipos.count(t) > 1}):  # sexta auditoría: el último tapaba al primero
        err.append(f"Pos {pos}: hay más de un desvío de {t} en el renglón: dejar uno solo")
    decl = {str(d.get("que", "")).lower(): d for d in lista}
    for tipo, txt in mots:
        d = decl.get(tipo)
        if not d:
            err.append(f"Pos {pos}: la referencia no sirve según la norma ({tipo}: {txt[:110]}). Cambiarla por una compatible, "
                       f"dejar SIN PRECIO o declarar el desvío en el renglón (\"desvio\": [{{\"que\": \"{tipo}\", \"ofrecido\": …, \"pedido\": …}}]) y en la oferta")
            continue
        ofr, ped = str(d.get("ofrecido", "")).strip(), str(d.get("pedido", "")).strip()
        if not ofr or not ped or re.search(SIN_RESOLVER, f"{ofr} {ped}".lower()):
            err.append(f"{A_CONFIRMAR}Pos {pos}: desvío de {tipo} sin resolver ({ofr or '¿ofrecido?'} por {ped or '¿pedido?'}): "
                       "pedir cotización que cumpla o completar el desvío antes de pasar a revisado")
            continue
        limpio = lambda x: re.sub(r"[^a-z0-9]", "", x.lower())
        if len(limpio(ofr)) < 5 or not re.search(r"[a-z]", limpio(ofr)) or len(limpio(ped)) < 4 or limpio(ofr) == limpio(ped):
            err.append(f"Pos {pos}: el desvío de {tipo} ({ofr} por {ped}) es demasiado genérico: decir qué se ofrece y qué pide el plano")
            continue
        ms = re.match(r"serie (\d+) por (\d+)", txt)
        if tipo == "serie" and ms and not (ms.group(1) in ofr and ms.group(2) in ped):
            # lo declarado tiene que ser lo que encontró el control (sexta auditoría: un desvío invertido pasaba)
            err.append(f"Pos {pos}: el desvío de serie dice {ofr} por {ped}, pero la fuente es serie {ms.group(1)} y el plano pide {ms.group(2)}")
            continue
        en_oferta = [t for t in textos_oferta if limpio(ofr) in limpio(t) and limpio(ped) in limpio(t)]
        if not en_oferta:
            err.append(f"Pos {pos}: el desvío de {tipo} ({ofr} por {ped}) no está en aclaraciones y desvíos de la oferta "
                       "(un texto que nombre la posición, lo que se ofrece y lo que pide el plano): el cliente tiene que enterarse")
            continue
        if any(re.search(SIN_RESOLVER, t.lower()) for t in en_oferta) and not any(not re.search(SIN_RESOLVER, t.lower()) for t in en_oferta):
            err.append(f"{A_CONFIRMAR}Pos {pos}: el desvío de {tipo} figura en la oferta como \"a confirmar\": resolverlo antes de pasar a revisado")
            continue
        av.append(f"Pos {pos}: desvío declarado de {tipo}: {ofr} por {ped}")
    return err, av


def control_compatibilidad(c, plano, avisos=None):
    """P9 (Matías, 30-10-2026): cada renglón de material con precio se compara con lo que pide el plano con las reglas de
    compatibilidad (compatibilidad.py). Cada diferencia que la norma no admite (material, extremos, schedule,
    revestimiento, costura, NACE, serie) es ERROR, salvo que el renglón la declare como desvío y la oferta la muestre
    (revisar_desvios). Se controla la fuente vigente, todas las filas con precio (las b/c sin material propio contra su
    fila madre) y las fuentes sin código (con el texto de la fuente, leído como una pieza). Otro Ø u otro tipo: AVISO."""
    ruta = c / "cotizacion.json"
    if not ruta.exists():
        return []
    import json
    import buscar_material as bm
    from compatibilidad import motivos, clases, dn_de, SCH_DOBLE
    from precotizar import texto_busqueda
    bm.buscar("brida")
    cat = {r["codigo"]: r for r in bm._FILAS}
    por_lista = {m.group(1): r["codigo"] for r in bm._FILAS if (m := re.search(r"^Renard \(cód\. (\d+)\)", r.get("proveedor", "")))}
    por_pos = {p["pos"].strip(): p for p in plano}
    items = json.load(open(ruta, encoding="utf-8"))["items"]
    lista_renard = {}  # códigos de las listas de Renard que no están en el catálogo (tercera auditoría)
    for lr in sorted((Path(__file__).resolve().parent.parent / "conocimiento" / "precios").glob("lista_renar_*.csv")):
        lista_renard.update({x["codigo"]: x["producto"] for x in csv.DictReader(open(lr, encoding="utf-8"))})
    desvios = desvios_oferta(c)
    cod_de = lambda f: f.get("codigo") or (re.search(r"\b[A-Z]{3}-\d{5}\b", str(f.get("proveedor") or "")) or [None])[0]
    cod_pos = {str(it.get("pos", "")).strip(): cod_de(it["fuentes"][0]) for it in items if it.get("fuentes")}
    out = []
    if (c / "oferta.json").exists() and not c.name.startswith("CTRL-"):  # textos de la oferta sin resolver: frenan el paso a revisado (como en la página)
        of = json.load(open(c / "oferta.json", encoding="utf-8"))
        for x in (of.get("aclaraciones_y_desvios") or {}).get("items", []):
            if re.search(SIN_RESOLVER, str(x).lower()):
                out.append(f"{A_CONFIRMAR}Oferta: aclaración o desvío sin resolver: {str(x)[:120]}")
    for it in items:
        if it.get("grupo") != "material" or not it.get("fuentes"):
            continue
        f = it["fuentes"][0]
        if not f.get("precio"):
            continue
        if str(it.get("descripcion", "")).startswith("[") and c.name.startswith("CTRL-"):
            continue  # renglón de la plantilla (casos de control: cotizacion.json solo trae parámetros)
        cod = cod_de(f)
        if f.get("codigo") and f["codigo"] not in cat:
            out.append(f"Pos {it.get('pos')}: el código {f['codigo']} no está en el catálogo: corregirlo")
            continue
        if not cod:  # "Renard · cód. 5979": la pieza del catálogo de esa lista
            m = re.search(r"(?i)\b(renard|renar)\b.*?c[óo]d\.? ?(\d+)", str(f.get("proveedor") or ""))
            cod = por_lista.get(m.group(2)) if m else None
        pos = str(it.get("pos", "")).strip()
        madre = re.match(r"\d+", pos)
        p = por_pos.get(pos)
        desc_it = f"{it.get('descripcion', '')} {it.get('especificacion', '')}"
        if not p and madre and madre.group(0) != pos and madre.group(0) in por_pos and (
                (cod and cod_pos.get(madre.group(0)) == cod) or re.search(rf"\bpos\.? ?{madre.group(0)}\b", desc_it.lower())
                or not clases(desc_it)):
            p = por_pos.get(madre.group(0))  # compra extra (14b) o fila sin material propio: contra la fila madre del plano
        texto = texto_busqueda(p) if p else desc_it
        if not p and not clases(texto):
            if avisos is not None:
                avisos.append(f"Pos {pos}: fila agregada sin material en la descripción ({desc_it[:45]}): controlar a mano la referencia")
            continue
        fam, at, *_ = bm.buscar(texto)
        if cod in cat:
            r = cat[cod]
            desc = r["descripcion"]
            mots = motivos(fam, at, r, texto, desc)
            serie_c = r.get("serie")
            if not mots and avisos is not None:
                if at.get("tipo") and r.get("tipo") and bm.norm(at["tipo"]) != bm.norm(r["tipo"]):
                    avisos.append(f"Pos {pos}: la referencia {cod} es de otro tipo ({r['tipo']} por {at['tipo']}): confirmar que sea la misma pieza")
                if at.get("diametro") and r.get("diametro") and dn_de(at["diametro"]) != dn_de(r["diametro"]):
                    avisos.append(f"Pos {pos}: la referencia {cod} es de otro Ø ({r['diametro']} por {at['diametro']}): justificar")
        else:
            # fuente sin pieza del catálogo: su texto (sin lo que dice del pedido) se lee como una pieza con el buscador y
            # se compara con todas las reglas (quinta auditoría: antes faltaban schedule, NACE y costura en esta ruta)
            desc = f"{f.get('proveedor', '')} {f.get('diferencia', '')}"
            mr = re.search(r"(?i)\b(renard|renar)\b.*?c[óo]d\.? ?(\d+)", str(f.get("proveedor") or ""))
            if mr and mr.group(2) in lista_renard:
                desc = f"{lista_renard[mr.group(2)]} {f.get('diferencia', '')}"
            limpio = re.sub(r"(?i)\(?\b(?:el plano pide|plano pide|pedid[oa]s?|se pide|pide)\b[^)\];]*\)?", " ", desc)
            _, at_f, *_ = bm.buscar(limpio)
            # el material sale del texto de la fuente, no del atributo que deduce el buscador ("Futura 36\"" no es A36)
            mots = motivos(fam, at, {**at_f, "material": ""}, texto, limpio)
            # lo que la fuente NO dice (material, sin costura, NACE, schedule por extremo) no se puede comparar: AVISO
            # lo que la fuente no dice: del material es aviso (las planillas casi nunca lo escriben); revestimiento,
            # costura, NACE o schedule de cada extremo que pide el plano son ERROR (sexta auditoría 30-10-2026)
            no_dice = [m for m in mots if re.search(r"no (?:lo )?dice|no se sabe|sin dato", m[1])]
            mots = [m for m in mots if m not in no_dice]
            for m in [m for m in no_dice if m[0] != "material"]:
                # lo que pide el plano y la fuente no dice: verificarlo en el original y escribirlo en la fuente; frena el
                # paso a revisado como un desvío a confirmar
                out.append(f"{A_CONFIRMAR}Pos {pos}: la fuente ({desc[:45]}) no dice {m[0]} ({m[1][:70]}): verificarlo en el original y escribirlo en la fuente")
            no_dice = [m for m in no_dice if m[0] == "material"]
            for m in no_dice:
                if avisos is not None:
                    avisos.append(f"Pos {pos}: la fuente ({desc[:50]}) no lo dice ({m[1][:70]}): verificarlo en el original")
            ms = re.search(r"#\s?(\d{3,4})\b|\b(\d{3,4})\s?(?:#|lbs?\b)|\bserie\s?(\d{3,4})\b|\bs(\d{3,4})\b|\bwog\s?(\d{3,4})\b"
                           r"|\b(?:clase|class|cl\.?|ansi)\s?(\d{3,4})\b", limpio.lower())
            serie_c = next(g for g in ms.groups() if g) if ms else ""
            if not serie_c and at.get("serie") and avisos is not None:
                avisos.append(f"Pos {pos}: la fuente ({desc[:50]}) no dice la serie (el plano pide {at['serie']}): verificarla en el original")
        sp, sc = re.sub(r"\D", "", str(at.get("serie") or "")), re.sub(r"\D", "", str(serie_c or ""))
        if sp and sc and sp != sc:  # otra serie no es similar (Matías, 29-10-2026)
            mots.append(("serie", f"serie {sc} por {sp} (otro rating)"))
        if not mots:
            continue
        madre_n = madre.group(0) if madre else pos
        textos = desvios.get(pos, []) + (desvios.get(madre_n, []) if madre_n != pos else [])
        e, a = revisar_desvios(pos, it, mots, textos)
        out += e
        if avisos is not None:
            avisos += a
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
    # un desvío "a confirmar" frena el paso a revisado (está en ERRORES) pero no el armado de un borrador: devuelve 2
    pendientes = [e for e in errores if e.startswith(A_CONFIRMAR)]
    if errores and len(pendientes) == len(errores):
        import json
        if json.load(open(c / "cotizacion.json", encoding="utf-8")).get("estado", "borrador") == "borrador":
            print(f"\n{len(pendientes)} desvíos a confirmar: el borrador se arma, pero NO pasa a revisado hasta resolverlos")
            return 2
    return 1 if errores else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1]))
