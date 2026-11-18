"""Errores sembrados: cada error ya cometido se mete a propósito en una copia de la CAPEX y algún control tiene que frenarlo
(validación del proceso unificado, Matías, 30-10-2026). Si un control deja de detectar su error, esta prueba falla.

Uso: python herramientas/test_errores_sembrados.py   (lo corre verificar_todo.py)

Base: copia de cotizaciones/COT26-1003-001_CAPEX_OQ8209 con los frenos levantados (justificaciones escritas y consultas
cerradas), para que cada siembra muestre solo su propio freno. La tabla error → control está en
conocimiento/procedimiento_cotizacion.md ("Errores sembrados").
"""
import contextlib
import csv
import io
import json
import shutil
import sys
import tempfile
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import frenos  # noqa: E402
import verificar_computo  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
CAPEX = RAIZ / "cotizaciones" / "COT26-1003-001_CAPEX_OQ8209"
fallas = []
HOY = date(2026, 10, 30)  # fecha fija: los frenos de vencimiento no cambian con el día en que se corre
JUST = "Justificación de prueba con más de veinte letras."


def leer_csv(p):
    filas = list(csv.DictReader(open(p, encoding="utf-8")))
    return filas, list(filas[0].keys())


def escribir_csv(p, filas, cols):
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(filas)


def editar_json(p, fn):
    d = json.load(open(p, encoding="utf-8"))
    fn(d)
    json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def base(tmp):
    c = Path(tmp) / CAPEX.name
    if c.exists():
        shutil.rmtree(c)
    shutil.copytree(CAPEX, c, ignore=shutil.ignore_patterns("*.xlsx", "*.html", "*.pdf", "*.docx", "*.png", "antecedentes", "oferta", "compras"))

    def levantar(d):
        d["justificaciones"] = {"estimado": JUST, "vencidas": JUST, "antecedentes": JUST}
        for it in d["items"]:
            if not it["fuentes"][0].get("precio"):
                it["sin_precio_motivo"] = JUST
    editar_json(c / "cotizacion.json", levantar)
    import re
    pend = re.compile(r"\[|\]|,? ?a confirmar|,? ?a definir|confirmar con|por confirmar|pendiente|a cotizar", re.I)

    def sin_corchetes(x):  # la base no tiene datos pendientes ni desvíos "a confirmar" (oferta y renglones)
        if isinstance(x, str):
            return pend.sub("", x)
        if isinstance(x, list):
            return [sin_corchetes(v) for v in x]
        if isinstance(x, dict):
            return {k: sin_corchetes(v) for k, v in x.items()}
        return x
    o = sin_corchetes(json.load(open(c / "oferta.json", encoding="utf-8")))
    json.dump(o, open(c / "oferta.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    editar_json(c / "cotizacion.json", lambda d: [it.update(desvio=sin_corchetes(it["desvio"])) for it in d["items"] if it.get("desvio")])
    cot = json.load(open(c / "cotizacion.json", encoding="utf-8"))
    o["aclaraciones_y_desvios"]["items"] += [f"Pos. {it['pos']}: se ofrece {d['ofrecido']} por {d['pedido']}." for it in cot["items"]
                                             for d in it.get("desvio") or [] if isinstance(d, dict)]  # cada desvío, declarado
    json.dump(o, open(c / "oferta.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    req, cols = leer_csv(c / "pedido" / "requisitos.csv")
    for r in req:
        r["referencia"] = pend.sub("", r["referencia"])
        if r["destino"] == "consulta":
            r["destino"] = "cumple"
    escribir_csv(c / "pedido" / "requisitos.csv", req, cols)
    return c


def frenos_de(c):
    with contextlib.redirect_stdout(io.StringIO()):
        return frenos.frenos(c, hoy=HOY)


def computo_errores(c):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        rc = verificar_computo.main(c)
    return rc, out.getvalue()


def esperar_error(nombre, c, texto, donde=""):
    """El error tiene que aparecer en la línea de la posición o renglón sembrado (donde), no en cualquier lado."""
    rc, out = computo_errores(c)
    if rc == 0 or not any(texto in ln and donde in ln for ln in out.splitlines() if "✗" in ln):
        fallas.append(nombre)
        print(f"FALLA {nombre}: verificar_computo no dio el error «{texto}»")
    else:
        print(f"OK   {nombre}")


def esperar_freno(nombre, c, clave):
    claves = [k for k, _ in frenos_de(c)]
    if clave not in claves:
        fallas.append(nombre)
        print(f"FALLA {nombre}: no frenó la oferta con [{clave}] (frenos: {claves})")
    else:
        print(f"OK   {nombre}")


def siembra_lista(c, pos, campo, fn):
    filas, cols = leer_csv(c / "pedido" / "lista_materiales_plano.csv")
    for r in filas:
        if r["pos"] == pos:
            r[campo] = fn(r[campo])
    escribir_csv(c / "pedido" / "lista_materiales_plano.csv", filas, cols)


def siembra_computo(c, fn):
    filas, cols = leer_csv(c / "computo.csv")
    filas = fn(filas)
    escribir_csv(c / "computo.csv", filas, cols)


def paridad_pagina():
    """La página (web/src/busqueda.js) frena igual que Python en cada cotización del repositorio (web/probar_frenos.js)."""
    import subprocess
    casos = []
    for c in sorted((RAIZ / "cotizaciones").glob("COT*")):
        if not (c / "cotizacion.json").exists():  # carpeta recién abierta (alcance y lista, sin precios): nada que frenar
            continue
        with contextlib.redirect_stdout(io.StringIO()):
            cot = json.load(open(c / "cotizacion.json", encoding="utf-8"))
            cot["frenos_repo"] = [{"clave": k, "texto": t} for k, t in frenos.frenos_repo(c)]
            claves = [k for k, _ in frenos.frenos(c, hoy=HOY)]
        of = json.load(open(c / "oferta.json", encoding="utf-8")) if (c / "oferta.json").exists() else {}
        casos.append({"nombre": c.name, "cot": cot, "oferta": of, "hoy": HOY.isoformat(), "claves": claves})
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(casos, f, ensure_ascii=False)
    r = subprocess.run(["node", str(RAIZ / "web" / "probar_frenos.js"), f.name], capture_output=True, text=True)
    Path(f.name).unlink()
    print(("OK   " if r.returncode == 0 else "FALLA ") + "frenos de la página iguales a Python: " + r.stdout.strip()[-300:])
    if r.returncode:
        fallas.append("frenos de la página distintos de Python")


def main():
    with tempfile.TemporaryDirectory() as tmp:
        c = base(tmp)
        rc, out = computo_errores(c)
        if rc:
            fallas.append("base sin errores")
            print("FALLA base: la copia de la CAPEX ya tiene errores de cómputo\n" + out[-1500:])
        fr = frenos_de(c)
        if fr:
            fallas.append("base sin frenos")
            print(f"FALLA base: la copia con justificaciones sigue con frenos {fr}")

        # 1. Descripción del cliente con palabras agregadas (regla crítica, 29-10-2026: "RF", "radio largo")
        c = base(tmp)
        siembra_lista(c, "15", "descripcion", lambda d: d + " RADIO LARGO")
        esperar_error("descripción con palabras agregadas", c, "la descripción no es la del cliente", "Pos 15")
        # 2. Cantidad distinta de la del cliente (errores 6 y 14: caño 6 m por 1.900 mm; lista ≠ plano en Camuzzi)
        c = base(tmp)
        siembra_lista(c, "3", "cantidad", lambda q: "7")
        esperar_error("cantidad distinta de la del cliente", c, "el cliente pide", "Pos 3")
        # 3. Posición del plano que falta en el cómputo
        c = base(tmp)
        siembra_computo(c, lambda f: [r for r in f if r["pos"] != "19"])
        esperar_error("posición faltante en el cómputo", c, "no está en el cómputo", "Pos 19")
        # 4. Fecha de precio supuesta o futura (PC0 de YPF con fecha supuesta)
        c = base(tmp)
        siembra_computo(c, lambda f: [dict(r, fecha_precio="2027-01-01") if r["id"] == "M03" else r for r in f])
        esperar_error("fecha de precio futura", c, "fecha de precio inválida o futura", "M03")
        # 5. Precio adivinado sin referencia (P4 ter)
        c = base(tmp)
        siembra_computo(c, lambda f: [dict(r, coincidencia="sin_ref") if r["id"] == "M03" else r for r in f])
        esperar_error("precio sin referencia", c, "sin referencia ni pieza parecida", "M03")
        # 6. Subtotal que no es cantidad × precio (totales hechos a mano)
        c = base(tmp)
        siembra_computo(c, lambda f: [dict(r, subtotal_usd="999") if r["id"] == "M03" else r for r in f])
        esperar_error("subtotal distinto", c, "subtotal", "M03")
        # 7. Precio sin fuente o sin fecha
        c = base(tmp)
        siembra_computo(c, lambda f: [dict(r, proveedor_o_criterio="") if r["id"] == "M03" else r for r in f])
        esperar_error("precio sin fuente", c, "precio sin fuente o sin fecha", "M03")
        # 8. Referencia que la norma no permite (BSPT por NPT, 30-10-2026)
        c = base(tmp)
        import buscar_material as bm
        bm.buscar("tapon")
        cand = next((r for r in bm._FILAS if "TAP" in r["descripcion"].upper() and "BSP" in r["descripcion"].upper()), None)
        if cand is None:
            fallas.append("referencia incompatible (sin candidato BSPT en el catálogo)")
            print("FALLA referencia incompatible: no hay tapón BSPT en el catálogo para sembrar")
        else:
            editar_json(c / "cotizacion.json", lambda d: [it["fuentes"][0].update(codigo=cand["codigo"]) for it in d["items"] if it["id"] == "M17"])
            esperar_error("referencia incompatible", c, "no sirve según la norma", "Pos 17")

        # 9. Atributo distinto del cliente: NPT-M por NPT-H (error #7), otro material, modelo exigido borrado
        c = base(tmp)
        siembra_lista(c, "20", "extremos", lambda v: "NPT-M")
        esperar_error("extremos distintos del cliente (NPT-M por NPT-H, #7)", c, "extremos", "Pos 20")
        c = base(tmp)
        siembra_lista(c, "1", "material", lambda v: "ASTM A-182 F316")
        esperar_error("material distinto del cliente", c, "material", "Pos 1")
        c = base(tmp)
        siembra_lista(c, "19", "modelo_fabricante", lambda v: "")
        esperar_error("modelo exigido por el cliente borrado", c, "modelo_fabricante", "Pos 19")
        # 10. Dato agregado por ITT donde el cliente no lo da, sin nota
        c = base(tmp)
        siembra_lista(c, "2", "nota", lambda v: "")
        esperar_error("dato agregado por ITT sin nota", c, "explicarlo en la columna nota", "Pos 2")

        # Frenos de la oferta
        c = base(tmp)
        (c / "pedido" / "transcripcion.json").unlink()
        esperar_freno("sin transcripción literal del cliente", c, "transcripcion")
        c = base(tmp)
        (c / "pedido" / "transcripcion_b.json").unlink()
        esperar_freno("sin segunda lectura", c, "doble_lectura")
        c = base(tmp)
        editar_json(c / "pedido" / "transcripcion_b.json", lambda d: d["tablas"][0]["filas"][2].__setitem__(5, "NPT-H"))
        esperar_freno("lecturas distintas (NPT-M por NPT-H, errores 7 y 14)", c, "doble_lectura")
        c = base(tmp)
        editar_json(c / "pedido" / "transcripcion_b.json", lambda d: d.update(lector=json.load(open(c / "pedido" / "transcripcion.json", encoding="utf-8"))["lector"]))
        esperar_freno("las dos lecturas del mismo lector", c, "doble_lectura")
        c = base(tmp)
        editar_json(c / "pedido" / "transcripcion.json", lambda d: [t.update(columnas=t["columnas"][:-2] + t["columnas"][-1:], filas=[f[:-2] + f[-1:] for f in t["filas"]]) for t in d["tablas"]])
        esperar_freno("columna que solo leyó B", c, "doble_lectura")
        c = base(tmp)
        (c / "pedido" / "requisitos.csv").unlink()
        esperar_freno("sin matriz de requisitos", c, "requisitos")
        c = base(tmp)
        req, cols = leer_csv(c / "pedido" / "requisitos.csv")
        req[2]["destino"] = ""
        escribir_csv(c / "pedido" / "requisitos.csv", req, cols)
        esperar_freno("requisito sin destino (separador Camuzzi, ET sin leer)", c, "requisitos")
        c = base(tmp)
        req, cols = leer_csv(c / "pedido" / "requisitos.csv")
        req[0]["destino"] = "consulta"
        escribir_csv(c / "pedido" / "requisitos.csv", req, cols)
        esperar_freno("consulta al cliente sin respuesta", c, "requisitos")
        c = base(tmp)
        req, cols = leer_csv(c / "pedido" / "requisitos.csv")
        req[5]["destino"], req[5]["referencia"] = "renglon", "NADA"
        escribir_csv(c / "pedido" / "requisitos.csv", req, cols)
        esperar_freno("requisito a un renglón que no existe", c, "requisitos")
        c = base(tmp)
        req, cols = leer_csv(c / "pedido" / "requisitos.csv")
        req[5]["destino"], req[5]["referencia"] = "desvio", "un desvío que la oferta no dice"
        escribir_csv(c / "pedido" / "requisitos.csv", req, cols)
        esperar_freno("desvío que no figura en la oferta", c, "requisitos")
        c = base(tmp)
        editar_json(c / "cotizacion.json", lambda d: [it.pop("sin_precio_motivo", None) for it in d["items"]])
        esperar_freno("renglón en 0 sin motivo (lo que falta frena)", c, "sin_precio")
        c = base(tmp)
        editar_json(c / "cotizacion.json", lambda d: [it.update(sin_precio_motivo="Pedir cotización a Compras con la especificación del plano")
                                                      for it in d["items"] if not it["fuentes"][0].get("precio")])
        esperar_freno("renglón en 0 con motivo 'pedir cotización' (Camuzzi 003)", c, "sin_precio")
        c = base(tmp)
        editar_json(c / "cotizacion.json", lambda d: [it["fuentes"][0].update(precio=0) for it in d["items"] if it["id"] == "M03"])
        esperar_freno("precio puesto en 0 para bajar lo estimado", c, "sin_precio")
        c = base(tmp)
        o = json.load(open(c / "oferta.json", encoding="utf-8"))
        o["exclusiones"]["items"].append("[dato a completar]")
        json.dump(o, open(c / "oferta.json", "w", encoding="utf-8"), ensure_ascii=False)
        esperar_freno("oferta con datos entre corchetes", c, "pendientes_oferta")
        c = base(tmp)
        editar_json(c / "cotizacion.json", lambda d: d["justificaciones"].update(estimado="ok"))
        esperar_freno("justificación vacía de contenido", c, "estimado")
        c = base(tmp)
        editar_json(c / "cotizacion.json", lambda d: (d["justificaciones"].pop("vencidas"), [it["fuentes"][0].update(reconfirmado="2099-01-01") for it in d["items"] if it["fuentes"][0]["tipo"] == "cot"]))
        esperar_freno("reconfirmación con fecha futura", c, "vencidas")
        c = base(tmp)
        siembra_lista(c, "3", "cantidad", lambda q: "7")
        esperar_freno("generar_oferta sola con errores de cómputo", c, "computo")
        c = base(tmp)
        editar_json(c / "cotizacion.json", lambda d: d["justificaciones"].pop("estimado"))
        esperar_freno("estimado de más del 15% (error 17: 33% informado como 7%)", c, "estimado")
        c = base(tmp)
        editar_json(c / "cotizacion.json", lambda d: d["justificaciones"].pop("vencidas"))
        esperar_freno("cotización de proveedor vencida (error 18)", c, "vencidas")
        c = base(tmp)
        editar_json(c / "cotizacion.json", lambda d: d["justificaciones"].pop("antecedentes"))
        esperar_freno("diferencia con antecedentes sin explicar (error 19)", c, "antecedentes")
        c = base(tmp)
        editar_json(c / "cotizacion.json", lambda d: d["plazo"].update(dias=10))
        esperar_freno("plazo menor que el calculado (YPF 120 contra 180)", c, "plazo")
        # Lista de diseño ITT desde una hoja de datos (filtros AESA, 18-11-2026): la posición es de ITT y la descripción y el
        # material tienen que estar tal cual en la transcripción del documento del cliente
        aesa = RAIZ / "cotizaciones" / "COT26-0010-001_AESA_C5297_FILTROS_GAS"
        if (aesa / "computo.csv").exists():
            c = Path(tmp) / aesa.name
            shutil.copytree(aesa, c, ignore=shutil.ignore_patterns("*.xlsx", "*.html", "*.pdf", "*.docx", "*.png", "*.svg", "oferta", "compras", "ANEXO*"))
            siembra_lista(c, "1", "descripcion", lambda d: d + " RF")
            esperar_error("diseño ITT: descripción con palabras agregadas", c, "la descripción no es la del cliente", "Pos 1")
            shutil.rmtree(c)
            shutil.copytree(aesa, c, ignore=shutil.ignore_patterns("*.xlsx", "*.html", "*.pdf", "*.docx", "*.png", "*.svg", "oferta", "compras", "ANEXO*"))
            siembra_lista(c, "10", "material", lambda m: "SA 106 Gr.B sin costura")
            esperar_error("diseño ITT: material que no es el del cliente", c, "no figura tal cual en el documento del cliente", "Pos 10")
        # Oferta con varias posiciones (RCP, RDO y equipo, 18-11-2026): la suma tiene que dar el total del cálculo; un renglón
        # contado en dos posiciones tiene que frenar
        if (aesa / "computo.csv").exists():
            import armar_cotizacion
            import posiciones_oferta
            c = Path(tmp) / aesa.name
            shutil.rmtree(c, ignore_errors=True)
            shutil.copytree(aesa, c, ignore=shutil.ignore_patterns("*.xlsx", "*.html", "*.pdf", "*.docx", "*.png", "*.svg", "oferta", "compras", "ANEXO*"))
            cot = json.load(open(c / "cotizacion.json", encoding="utf-8"))
            tot = armar_cotizacion.calcular(cot, armar_cotizacion.leer_indices(cot))["total"]
            with contextlib.redirect_stdout(io.StringIO()):
                r = posiciones_oferta.main(c, tot)
            print("OK   posiciones de la oferta suman el total" if r else "FALLA posiciones de la oferta: sin posiciones")
            if not r:
                fallas.append("posiciones de la oferta")
            editar_json(c / "oferta.json", lambda d: d["posiciones"][1]["pos_cotizacion"].append("RCP"))
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    posiciones_oferta.main(c, tot)
                fallas.append("renglón en dos posiciones de la oferta")
                print("FALLA renglón en dos posiciones de la oferta: no frenó")
            except SystemExit:
                print("OK   renglón en dos posiciones de la oferta")
    paridad_pagina()
    print("\nTODO OK" if not fallas else f"\nFALLAN {len(fallas)}: {', '.join(fallas)}")
    return 1 if fallas else 0


if __name__ == "__main__":
    sys.exit(main())
