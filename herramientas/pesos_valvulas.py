"""Peso de válvulas Taval (kg) desde la Lista 30 de Taval (fuentes_originales/taval_lista30_2025-09.xlsx).

Uso: python herramientas/pesos_valvulas.py  → conocimiento/tecnico/valvulas_peso.csv

La lista trae, para cada válvula, el código Taval y el peso en kg en la columna "Kg" (o "Peso"). El código se descifra
con las tablas del codificador de Taval (fuentes_originales/codificador_taval_2023-07.xlsx): tipo (3 caracteres),
diámetro (3), serie (1), extremos (1), material (2) y el resto (junta/trim/mando).
Las hojas sin código (esféricas forjadas NPT y API 602) son tablas por diámetro: el peso va en la columna "Kg" de cada
grupo y la serie es el título de la columna siguiente.
También guarda el PRECIO de lista (columna "L30" o "Lista u$s") de cada código en conocimiento/precios/taval_lista30.csv,
con el precio neto = lista × FACTOR_TAVAL (0,52: el que aplican las planillas TAVAL/72 y TAVAL/78 de 2026). El precio es
el número que, dividido por los kg, da el "u$s x kg" de la columna vecina (así se lee igual en todas las hojas, aunque cambie
el orden de las columnas).
Controles: cada peso tiene que crecer con el diámetro dentro del mismo tipo, serie y hoja; lo que no cumple sale marcado.
"""
import csv
import re
import sys
from pathlib import Path

import openpyxl

RAIZ = Path(__file__).resolve().parent.parent
LISTA = RAIZ / "fuentes_originales" / "taval_lista30_2025-09.xlsx"
CODIF = RAIZ / "fuentes_originales" / "codificador_taval_2023-07.xlsx"
SALIDA = RAIZ / "conocimiento" / "tecnico" / "valvulas_peso.csv"
PRECIOS_L30 = RAIZ / "conocimiento" / "precios" / "taval_lista30.csv"
FACTOR_TAVAL = 0.52  # lista 30 × 0,52 = costo de ITT (TAVAL/72 "Valvulas Taval.xlsx" y TAVAL/78 "Valvulas.xlsx", 07/08-2026)
# Tipo según la hoja de la lista (manda sobre el código: hay códigos de otro modelo dentro de una hoja; se anota en tipo_codificador)
TIPO_HOJA = {"Esclusas": "ESCLUSA", "Globo": "GLOBO", "Retencion": "RETENCION A CLAPETA", "PT Flotante": "ESFERICA PT FLOTANTE",
             "PT Guiada": "ESFERICA PT GUIADA", "PR Flotante": "ESFERICA PR FLOTANTE", "PR Guiada": "ESFERICA PR GUIADA",
             "Waffer": "RETENCION WAFER DUAL PLATE", "Filtros Y": "FILTRO Y"}
CODIGO = re.compile(r"^[A-Z0-9]{3}\d{3}[0-9A-Z][A-Z0-9][A-Z0-9]{2}")


def tabla(wb, hoja, col_val=1):
    out = {}
    for r in wb[hoja].iter_rows(min_row=2, values_only=True):
        r = [x for x in r if x is not None]
        if len(r) > col_val and str(r[0]).strip() and str(r[0]).strip() not in out:
            out[str(r[0]).strip()] = r[col_val]
    return out


def pulgadas(v):
    """Título de columna de diámetro: '2"', '2  1/2"', '3/4"', 2, 2.5 → pulgadas; None si no es un diámetro."""
    if isinstance(v, (int, float)) and 0 < v <= 60:
        return float(v)
    m = re.match(r'^\s*(\d+)?\s*(?:(\d+)/(\d+))?\s*["”＂]\s*$', str(v or ""))
    if not m or not (m.group(1) or m.group(2)):
        return None
    return (int(m.group(1)) if m.group(1) else 0) + (int(m.group(2)) / int(m.group(3)) if m.group(2) else 0)


def main():
    import warnings
    warnings.filterwarnings("ignore")
    cw = openpyxl.load_workbook(CODIF, data_only=True)
    tipos = {}
    for r in cw["VALVULA"].iter_rows(min_row=2, values_only=True):
        r = [x for x in r if x is not None]
        if len(r) >= 3:
            tipos[str(r[1]).strip()] = str(r[2]).strip()
    diam = {k.zfill(3): float(v) for k, v in tabla(cw, "DIAMETRO").items() if isinstance(v, (int, float))}
    serie = {k: v for k, v in tabla(cw, "SERIE").items()}
    extremos = {k: v for k, v in tabla(cw, "EXTREMOS").items()}
    material = {k.zfill(2) if k.isdigit() else k: v for k, v in tabla(cw, "MATERIAL").items()}

    wb = openpyxl.load_workbook(LISTA, data_only=True)
    filas = []
    for ws in wb.worksheets:
        celdas = list(ws.iter_rows())
        # columnas de peso: título "Kg" o "Peso ..." en alguna fila de encabezado
        col_kg = {c.column for fila in celdas for c in fila if isinstance(c.value, str) and re.match(r"^\s*(kg|peso)\b", c.value.strip(), re.I)}
        dn_col = {}  # títulos de diámetro vigentes por columna (una fila con 2 o más diámetros es una fila de títulos)
        nuevas = []
        for fila in celdas:
            if nuevas:
                # si en una fila contradicen la columna casi todos los códigos, los títulos no son de esa sección: mandan los códigos;
                # si contradice uno solo, es un código mal cargado en la lista: manda la columna
                malos = [f for f in nuevas if f["_titulo"] is not None and f["_codigo"] != "" and abs(f["_titulo"] - f["_codigo"]) > 0.01]
                con_titulo = [f for f in nuevas if f["_titulo"] is not None]
                for f in malos:
                    f["_mayoria_columna"] = len(malos) * 2 <= len(con_titulo)
                filas.extend(nuevas)
                nuevas = []
            dns = {c.column: pulgadas(c.value) for c in fila if pulgadas(c.value) is not None and not CODIGO.match(str(c.value or ""))}
            if len(dns) >= 2 and not any(isinstance(c.value, str) and CODIGO.match(c.value.strip()) for c in fila):
                dn_col = dns
                continue
            trim = fila[1].value if len(fila) > 1 and isinstance(fila[1].value, (int, float)) else None
            for i, c in enumerate(fila):
                v = c.value.strip() if isinstance(c.value, str) else ""
                if not CODIGO.match(v):
                    continue
                kg = None
                for j in range(i + 1, min(i + 4, len(fila))):
                    if fila[j].column in col_kg and isinstance(fila[j].value, (int, float)) and fila[j].value > 0:
                        kg, celda = fila[j].value, fila[j].coordinate
                        break
                if kg is None:
                    continue
                num = lambda c: c.value if isinstance(c.value, (int, float)) and not isinstance(c.value, bool) else None
                precio = None
                jk = next(k for k in range(i + 1, min(i + 4, len(fila))) if fila[k].coordinate == celda)
                for a in range(jk + 1, min(jk + 7, len(fila) - 1)):  # precio y "u$s x kg" después del peso
                    pa, pb = num(fila[a]), num(fila[a + 1])
                    if pa and pb and pa > 20 and abs(pa / kg - pb) <= 0.02 * pb:
                        precio = pa
                        break
                if precio is None and jk >= 2:  # Waffer: precio, kg y u$s x kg
                    pa, pb = num(fila[jk - 1]), num(fila[jk + 1]) if jk + 1 < len(fila) else None
                    if pa and pb and pa > 20 and abs(pa / kg - pb) <= 0.02 * pb:
                        precio = pa
                t, d, s, e, m = v[:3], v[3:6], v[6], v[7], v[8:10]
                dn_codigo = diam.get(d, "")
                cerca = [x for x in dn_col if i - 1 <= x - 1 <= i + 3]  # título del grupo de columnas del código
                dn_titulo = dn_col[min(cerca, key=lambda x: abs(x - 1 - i))] if cerca else None
                nuevas.append({"_titulo": dn_titulo, "_codigo": dn_codigo,"tipo": TIPO_HOJA.get(ws.title, ws.title.upper()), "tipo_codificador": tipos.get(t, ""), "codigo_tipo": t, "dn_pulg": dn_codigo, "serie": serie.get(s, s),
                              "extremos": extremos.get(e, e), "material": material.get(m, m), "trim": trim if trim is not None else "",
                              "kg": round(float(kg), 3), "codigo_taval": v, "hoja": ws.title, "celda": celda, "nota": "",
                              "_precio": round(float(precio), 2) if precio else None})
        filas.extend(nuevas)  # la última fila de la hoja
    # Código y columna en desacuerdo: manda la medida cuyo peso se confirma en otra parte de la lista (mismo tipo, serie,
    # material y extremos); si no se puede confirmar, la regla de la fila (un código solo contra la columna: vale la columna).
    def clave(f, dn):
        return (f["hoja"], f["tipo"], str(f["serie"]), str(f["material"]), str(f["extremos"]), round(float(dn), 4))
    conocidos = {}
    for f in filas:
        if "_titulo" in f and not ("_mayoria_columna" in f):
            conocidos.setdefault(clave(f, f["_codigo"]), set()).add(f["kg"])
    for f in filas:
        if "_titulo" not in f:
            continue
        if "_mayoria_columna" in f:
            cod, tit = f["_codigo"], f["_titulo"]
            if f["kg"] in conocidos.get(clave(f, cod), ()):
                f["dn_pulg"], f["nota"] = cod, f"está en la columna de {tit:g}\" pero el código ({cod:g}\") y el peso coinciden con otra fila de la lista: vale el código"
            elif f["kg"] in conocidos.get(clave(f, tit), ()):
                f["dn_pulg"], f["nota"] = tit, f"el código dice {cod:g}\" pero está en la columna de {tit:g}\" y el peso coincide con esa medida: vale la columna (código mal cargado en la lista)"
            elif f["_mayoria_columna"]:
                f["dn_pulg"], f["nota"] = tit, f"el código dice {cod:g}\" pero está en la columna de {tit:g}\": se tomó la columna sin poder confirmarlo (revisar)"
            else:
                f["dn_pulg"] = cod
            del f["_mayoria_columna"]
        del f["_titulo"], f["_codigo"]
    # tablas por diámetro (sin código): esféricas roscadas NPT (forjadas y fundidas) y API 602. Cada sección empieza en una
    # fila con títulos "Kg"; el material o el tipo es el título más cercano a la izquierda en la fila de arriba de esa sección.
    for hoja in ("PT Flot-NPT FORJADAS", "API 602"):
        ws = wb[hoja]
        filas_ws = list(ws.iter_rows())
        encabezados = [k for k, f in enumerate(filas_ws) if any(isinstance(c.value, str) and c.value.strip().lower() == "kg" for c in f)]
        for n, k in enumerate(encabezados):
            enc = filas_ws[k]
            fin = encabezados[n + 1] if n + 1 < len(encabezados) else len(filas_ws)
            titulos = {}
            for f in filas_ws[k - 1:k]:  # la fila de títulos justo arriba del encabezado (material o tipo)
                for c in f:
                    if isinstance(c.value, str) and c.value.strip():
                        titulos[c.column] = c.value.strip()
            for fila in filas_ws[k + 1:fin]:
                dn = fila[0].value
                if not isinstance(dn, (int, float)):
                    continue
                for c in enc:
                    if not (isinstance(c.value, str) and c.value.strip().lower() == "kg"):
                        continue
                    kg = fila[c.column - 1].value
                    if not isinstance(kg, (int, float)) or kg <= 0:
                        continue
                    ser = str(enc[c.column].value or "").replace("PSI", "").strip()  # la columna siguiente dice la serie
                    izq = [titulos[x] for x in sorted(titulos) if x <= c.column and not re.match(r"^\d+ ?psi$", titulos[x], re.I)]
                    grupo = izq[-1] if izq else ""
                    if hoja == "API 602":
                        tipo, mat = ("ESCLUSA API 602" if "ESCLUSA" in grupo.upper() else "GLOBO API 602"), "A 105"
                    else:
                        mat = grupo
                        tipo = "ESFERICA PT FLOTANTE " + ("FUNDIDA" if mat.upper() in ("WCB", "CF8M") else "FORJADA") + " NPT (API 608)"
                    pr, uk = (fila[c.column].value if c.column < len(fila) else None), (fila[c.column + 1].value if c.column + 1 < len(fila) else None)
                    precio = pr if isinstance(pr, (int, float)) and isinstance(uk, (int, float)) and pr > 20 and abs(pr / kg - uk) <= 0.02 * uk else None
                    filas.append({"tipo": tipo, "tipo_codificador": "", "codigo_tipo": "", "dn_pulg": float(dn), "serie": ser,
                                  "extremos": "NPT" if hoja != "API 602" else "SW/NPT", "material": mat, "trim": "", "kg": round(float(kg), 3),
                                  "codigo_taval": "", "hoja": hoja, "celda": fila[c.column - 1].coordinate, "nota": "", "_precio": precio})
    # precios de lista (una fila por código)
    con_precio, vistos = [], set()
    for f in filas:
        clave_p = f["codigo_taval"] or f"{f['hoja']}|{f['tipo']}|{f['dn_pulg']}|{f['serie']}|{f['material']}"
        if f.get("_precio") and clave_p not in vistos and f["dn_pulg"] != "":
            vistos.add(clave_p)
            con_precio.append({"codigo_taval": f["codigo_taval"], "tipo": f["tipo"], "dn_pulg": f["dn_pulg"], "serie": f["serie"], "extremos": f["extremos"],
                               "material": f["material"], "trim": f["trim"], "kg": f["kg"], "precio_lista30_usd": round(f["_precio"], 2),
                               "factor": FACTOR_TAVAL, "precio_neto_usd": round(f["_precio"] * FACTOR_TAVAL, 2), "hoja": f["hoja"], "nota": f["nota"]})
    for f in filas:
        f.pop("_precio", None)
    with open(PRECIOS_L30, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(con_precio[0].keys()) + ["fecha", "fuente"])
        w.writeheader()
        for f in sorted(con_precio, key=lambda f: (f["tipo"], str(f["serie"]), f["dn_pulg"], str(f["trim"]))):
            w.writerow({**f, "fecha": "2025-09-01", "fuente": "Taval Lista 30 (09-2025), fuentes_originales/taval_lista30_2025-09.xlsx"})
    print(f"{PRECIOS_L30.relative_to(RAIZ)}: {len(con_precio)} precios de lista (neto = lista × {FACTOR_TAVAL:g})")
    # control: el peso crece con el diámetro (mismo tipo, serie, hoja y material)
    grupos = {}
    for f in filas:
        grupos.setdefault((f["hoja"], f["tipo"], str(f["serie"]), str(f["material"])), {}).setdefault(f["dn_pulg"], set()).add(f["kg"])
    raros = 0
    for (hoja, tipo, ser, mat), por_dn in grupos.items():
        dns = sorted(d for d in por_dn if d != "")
        for a, b in zip(dns, dns[1:]):
            if min(por_dn[b]) < max(por_dn[a]):
                raros += 1
                for f in filas:
                    if (f["hoja"], f["tipo"], str(f["serie"]), str(f["material"])) == (hoja, tipo, ser, mat) and f["dn_pulg"] == b:
                        f["nota"] = (f["nota"] + "; " if f["nota"] else "") + f"pesa menos que la de {a:g}\" (revisar)"
    # una fila por válvula: mismo tipo, Ø, serie, extremos y material con el mismo peso (los trims no cambian el peso)
    vistas, unicas = set(), []
    for f in filas:
        k = (f["tipo"], f["dn_pulg"], str(f["serie"]), f["extremos"], f["material"], f["kg"])
        if k not in vistas:
            vistas.add(k)
            unicas.append(f)
    unicas.sort(key=lambda f: (f["tipo"], str(f["serie"]), f["dn_pulg"] if f["dn_pulg"] != "" else 0))
    with open(SALIDA, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(unicas[0].keys()) + ["fuente"])
        w.writeheader()
        for f in unicas:
            w.writerow({**f, "fuente": "Taval Lista 30 (09-2025), fuentes_originales/taval_lista30_2025-09.xlsx"})
    print(f"{SALIDA.relative_to(RAIZ)}: {len(unicas)} pesos ({len(filas)} leídos) · tipos: {len({f['tipo'] for f in unicas})} · "
          f"sin diámetro descifrado: {sum(1 for f in unicas if f['dn_pulg'] == '')} · para revisar: {raros}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
