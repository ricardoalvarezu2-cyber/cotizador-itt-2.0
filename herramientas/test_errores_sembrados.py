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
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import frenos  # noqa: E402
import verificar_computo  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
CAPEX = RAIZ / "cotizaciones" / "COT26-1003-001_CAPEX_OQ8209"
fallas = []


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
        d["justificaciones"] = {"estimado": "prueba", "vencidas": "prueba", "antecedentes": "prueba"}
    editar_json(c / "cotizacion.json", levantar)
    req, cols = leer_csv(c / "pedido" / "requisitos.csv")
    for r in req:
        if r["destino"] == "consulta":
            r["destino"] = "desvio"
    escribir_csv(c / "pedido" / "requisitos.csv", req, cols)
    return c


def computo_errores(c):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        rc = verificar_computo.main(c)
    return rc, out.getvalue()


def esperar_error(nombre, c, texto):
    rc, out = computo_errores(c)
    if rc == 0 or texto not in out:
        fallas.append(nombre)
        print(f"FALLA {nombre}: verificar_computo no dio el error «{texto}»")
    else:
        print(f"OK   {nombre}")


def esperar_freno(nombre, c, clave):
    with contextlib.redirect_stdout(io.StringIO()):
        claves = [k for k, _ in frenos.frenos(c)]
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


def main():
    with tempfile.TemporaryDirectory() as tmp:
        c = base(tmp)
        rc, out = computo_errores(c)
        if rc:
            fallas.append("base sin errores")
            print("FALLA base: la copia de la CAPEX ya tiene errores de cómputo\n" + out[-1500:])
        with contextlib.redirect_stdout(io.StringIO()):
            fr = frenos.frenos(c)
        if fr:
            fallas.append("base sin frenos")
            print(f"FALLA base: la copia con justificaciones sigue con frenos {fr}")

        # 1. Descripción del cliente con palabras agregadas (regla crítica, 29-10-2026: "RF", "radio largo")
        c = base(tmp)
        siembra_lista(c, "15", "descripcion", lambda d: d + " RADIO LARGO")
        esperar_error("descripción con palabras agregadas", c, "la descripción no es la del cliente")
        # 2. Cantidad distinta de la del cliente (errores 6 y 14: caño 6 m por 1.900 mm; lista ≠ plano en Camuzzi)
        c = base(tmp)
        siembra_lista(c, "3", "cantidad", lambda q: "7")
        esperar_error("cantidad distinta de la del cliente", c, "el cliente pide")
        # 3. Posición del plano que falta en el cómputo
        c = base(tmp)
        siembra_computo(c, lambda f: [r for r in f if r["pos"] != "19"])
        esperar_error("posición faltante en el cómputo", c, "no está en el cómputo")
        # 4. Fecha de precio supuesta o futura (PC0 de YPF con fecha supuesta)
        c = base(tmp)
        siembra_computo(c, lambda f: [dict(r, fecha_precio="2027-01-01") if r["id"] == "M03" else r for r in f])
        esperar_error("fecha de precio futura", c, "fecha de precio inválida o futura")
        # 5. Precio adivinado sin referencia (P4 ter)
        c = base(tmp)
        siembra_computo(c, lambda f: [dict(r, coincidencia="sin_ref") if r["id"] == "M03" else r for r in f])
        esperar_error("precio sin referencia", c, "sin referencia ni pieza parecida")
        # 6. Subtotal que no es cantidad × precio (totales hechos a mano)
        c = base(tmp)
        siembra_computo(c, lambda f: [dict(r, subtotal_usd="999") if r["id"] == "M03" else r for r in f])
        esperar_error("subtotal distinto", c, "subtotal")
        # 7. Precio sin fuente o sin fecha
        c = base(tmp)
        siembra_computo(c, lambda f: [dict(r, proveedor_o_criterio="") if r["id"] == "M03" else r for r in f])
        esperar_error("precio sin fuente", c, "precio sin fuente o sin fecha")
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
            esperar_error("referencia incompatible", c, "no sirve según la norma")

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
    print("\nTODO OK" if not fallas else f"\nFALLAN {len(fallas)}: {', '.join(fallas)}")
    return 1 if fallas else 0


if __name__ == "__main__":
    sys.exit(main())
