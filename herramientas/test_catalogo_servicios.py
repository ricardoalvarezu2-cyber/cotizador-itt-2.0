"""Test de regresión del catálogo de servicios (etapa 1). Correr después de tocar catalogo_servicios.py, buscar_servicio.py,
numeros.py o servicios_extraidos.csv:

  python herramientas/test_catalogo_servicios.py

Cubre casos reales del catálogo (Antonelli, Ledesma, Quesada, Suan, planilla de costo de planta, MO Master), la regla del cepo
(28/10/2026), IVA, pesos, tarifa unitaria, números ambiguos, fechas parciales, códigos estables, determinismo y que cada cita de la
extracción siga estando en el documento original.
"""
import csv
import hashlib
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import catalogo_servicios as cs  # noqa: E402
from buscar_servicio import buscar, tokens  # noqa: E402
from catalogo_materiales import tabla_dolar, en_mes  # noqa: E402
from numeros import fecha_iso  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
PRECIOS = RAIZ / "conocimiento" / "precios"
fallas = []


def igual(nombre, obtenido, esperado, tol=None):
    ok = abs(obtenido - esperado) <= tol if tol is not None and isinstance(obtenido, (int, float)) and isinstance(esperado, (int, float)) else obtenido == esperado
    if not ok:
        fallas.append(f"{nombre}: dio {obtenido!r}, se esperaba {esperado!r}")


def leer(ruta):
    return list(csv.DictReader(open(ruta, encoding="utf-8")))


def hashes():
    return {n: hashlib.md5((PRECIOS / n).read_bytes()).hexdigest() for n in
            ("catalogo_servicios.csv", "catalogo_servicios_historial.csv", "catalogo_servicios_codigos.csv")}


# armado determinístico: dos corridas, mismo CSV
cs.main.__globals__["print"] = lambda *a, **k: None  # silencia el resumen
cs.main()
h1 = hashes()
cs.main()
igual("dos corridas dan el mismo CSV", hashes(), h1)
cs.main.__globals__.pop("print", None)

cat = leer(PRECIOS / "catalogo_servicios.csv")
hist = leer(PRECIOS / "catalogo_servicios_historial.csv")
ext = leer(PRECIOS / "servicios_extraidos.csv")
por_serv = {}
for r in cat:
    por_serv.setdefault(r["servicio"], []).append(r)


def uno(servicio, **filtro):
    xs = [r for r in por_serv[servicio] if all(r[k] == v for k, v in filtro.items())]
    assert len(xs) == 1, (servicio, filtro, len(xs))
    return xs[0]


# 1. Antonelli (NDT, 03/11/2025): radiografía USD 490 sin IVA, con TC explícito
r = uno("Radiografía (servicio)")
igual("Antonelli RX precio", float(r["ultimo_precio_usd"]), 490)
igual("Antonelli RX fecha", r["fecha_ultimo_precio"], "2025-11-03")
igual("Antonelli RX unidad", r["unidad_tarifa"], "USD/servicio")
igual("Antonelli RX proveedor", "Antonelli" in r["proveedor"], True)
# 2. Cepo: el modelo MO Master (28 USD/pulg, 28/05/2024) no dice TC -> sin precio confiable, solo referencia
r = uno("Soldadura piping (valor del modelo MO Master)")
igual("MO Master sin último precio", r["ultimo_precio_usd"], "")
igual("MO Master alerta", "sin precio confiable: pedir cotización" in r["alerta"], True)
igual("MO Master referencia descartada", float(r["referencia_descartada_usd"]), 28)
# 3. La planilla de costo de planta oct-2024 SÍ es confiable (hoja Sueldos con TC 997)
r = uno("Hora hombre soldador (costo empresa)")
igual("soldador hh se usa", float(r["ultimo_precio_usd"]), 61.1609, 0.001)
igual("soldador hh no descartado", "cepo" in r["nota"] and "descartado" in r["nota"] and "pero con tipo de cambio" not in r["nota"], False)
# 4. Ledesma 2024 (4,60 / 6 / 16,31 por pulgada, sin TC) quedan en el historial como descartados; el último es posterior a abr-2025
r = uno("MO soldadura y armado de piping por pulgada (tercero)")
igual("piping tercero último es de 2026", r["fecha_ultimo_precio"] >= "2025-07", True)
desc = [h for h in hist if h["codigo"] == r["codigo"] and h["estado"] == "descartado (cepo)"]
igual("piping: 3 descartados de Ledesma 2024", sorted(float(h["precio_origen"]) for h in desc), [4.6, 6.0, 16.31])
igual("piping: nota del descarte", all("descartado: período con cepo, dólar sin aclarar" in h["nota"] for h in desc), True)
igual("piping: el descartado no entra en el mínimo", float(r["precio_min_usd"]) >= 12, True)
# 5. Pesos a USD con el dólar BNA del mes: Suan, 3.200.000 ARS por semirremolque (31/07/2025)
r = uno("Flete de equipo en semirremolque (camión)")
tc, _ = en_mes(tabla_dolar(), "2025-07-31", 0)
igual("Suan ARS -> USD", float(r["ultimo_precio_usd"]), 3200000 / tc, 0.01)
igual("Suan unidad", r["unidad_tarifa"], "USD/viaje")
# 6. IVA: con IVA se divide; si no dice, sin IVA; "más IVA" es sin IVA
base = {"precio": 1210.0, "iva_origen": "con IVA 21%", "texto_original": "USD 1.210 con IVA 21%"}
igual("IVA 21%", round(cs.precio_sin_iva(base)[0], 2), 1000.0)
igual("IVA 10,5%", round(cs.precio_sin_iva({**base, "precio": 1105.0, "iva_origen": "con IVA 10,5%"})[0], 2), 1000.0)
igual("IVA no dice", cs.precio_sin_iva({**base, "iva_origen": "no dice", "texto_original": "USD 1.210"})[0], 1210.0)
igual("IVA más IVA", cs.precio_sin_iva({**base, "iva_origen": "más IVA (lo dice)", "texto_original": "USD 3.400 Más IVA C/U"})[0], 1210.0)
# 7. Tarifa unitaria = precio ÷ magnitud
r = uno("MO fabricación skid y estructura por kg (tercero)")
igual("Quesada calentador 370: 3234 ÷ 770", [float(h["valor_usd"]) for h in hist if h["codigo"] == r["codigo"] and h["fecha"] == "2026-04-22"], [4.2])
r = uno("MO fabricación de manifold (tercero)", unidad_tarifa="USD/pulg-eq")
igual("Ledesma manifold 3590 ÷ 224 pulgadas", float(r["tarifa_unitaria_usd"]), 3590 / 224, 0.001)
igual("manifold: alcance comparable", r["alcance_comparable"], "sí")
r = uno("MO fabricación de antorcha (tercero)")
igual("antorcha 81000 ÷ 24500 kg", float(r["tarifa_unitaria_usd"]), 81000 / 24500, 0.001)
# 8. Un global sin magnitud no tiene tarifa ni alcance comparable
r = uno("MO fabricación de equipo completo (tercero)", equipo_referencia="Desgasificador SB-211")
igual("global sin tarifa", (r["tarifa_unitaria_usd"], r["alcance_comparable"], r["unidad"]), ("", "no", "global"))
# 9. Los globales de distinto equipo no se juntan (6 presupuestos de Ledesma para AESA = 6 códigos)
igual("AESA: 6 equipos, 6 códigos", len(por_serv["MO fabricación de equipo completo (tercero)"]), 6)
# ... pero el mismo equipo cotizado por varios proveedores sí (filtro FM8 S600 lado derecho: Ledesma 2.100 y Finder 3.900)
r = uno("MO fabricación de filtro (tercero)", equipo_referencia="Filtro FM8 S600 lado derecho Inarteco Lic 9333")
igual("FM8: 2 precios en el historial", int(r["precios_en_historial"]), 2)
igual("FM8: último = Finder 3.900 (02/03/2026)", (float(r["ultimo_precio_usd"]), r["fecha_ultimo_precio"]), (3900.0, "2026-03-02"))
# 10. Número ambiguo ('27,200' puede ser 27,2 o 27.200)
igual("ambiguo 27,200", "27,200" in cs.numero_ambiguo({"precio": 27200.0, "texto_original": "Precio USD 27,200 Más IVA"}), True)
igual("no ambiguo 4,5", cs.numero_ambiguo({"precio": 4.5, "texto_original": "U$S 4,5"}), "")
igual("alerta en el catálogo del 200256", "número ambiguo" in uno("MO skids con piping y soportería, por pulgada (tercero)")["alerta"], True)
# 11. Fechas: nunca una fecha por defecto
igual("fecha mes", cs.fecha_valida("2024-09"), "2024-09")
igual("fecha año", cs.fecha_valida("2024"), "2024")
igual("fecha completa", cs.fecha_valida("25/03/2026"), "2026-03-25")
igual("fecha futura", cs.fecha_valida("2099-01-01"), "")
igual("fecha vacía", cs.fecha_valida(""), "")
igual("fecha mes 13", cs.fecha_valida("2024-13"), "")
igual("numeros.fecha_iso sin mes no inventa", fecha_iso("2024-09"), "")
# 12. Valores de un año solo (planilla base 2024) entran por el corte del cepo: no son confiables
r = uno("Hora hombre ingeniería (valor de la planilla base)")
igual("planilla base 2024: sin precio confiable", r["ultimo_precio_usd"], "")
# 13. Sueldos de octubre 2024 por persona (hoja Reparto): armado y prearmado 10.603,92 ÷ 10
r = uno("Sueldo mensual por persona, centro Armado Y Prearmado")
igual("sueldo armado por persona", float(r["ultimo_precio_usd"]), 1060.39, 0.01)
# 14. Ajuste a hoy con indice_local_usd (no con el CPI de EE.UU.)
tabla = cs.tabla_ajuste()
ref = tabla[max(tabla)][1]
r = uno("Hora hombre soldador (costo empresa)")
igual("ajuste con indice_local_usd", float(r["precio_ajustado_hoy_usd"]), 61.1609 * ref / tabla["2024-10"][1], 0.01)
# 15. Magnitud
igual("magnitud kg decimal", cs.magnitud_de("1287.3 kg"), (1287.3, "kg"))
igual("magnitud pulgadas", cs.magnitud_de("1250 pulg-eq"), (1250.0, "pulg-eq"))
igual("magnitud vacía", cs.magnitud_de(""), (None, ""))
# 16. Códigos estables y únicos; el historial usa los mismos códigos
cods = [r["codigo"] for r in cat]
igual("códigos únicos", len(cods), len(set(cods)))
igual("códigos del historial existen", {h["codigo"] for h in hist} <= set(cods), True)
reg = leer(PRECIOS / "catalogo_servicios_codigos.csv")
igual("registro de códigos cubre el catálogo", set(cods) <= {x["codigo"] for x in reg}, True)
# 17. Buscador
igual("buscar radiografía -> END", buscar("radiografia", "ensayos", 1)[0][1]["hoja"], "Ensayos y END")
igual("buscar soldadura piping pulgada -> Soldadura y piping", buscar("soldadura piping por pulgada", "", 1)[0][1]["hoja"], "Soldadura y piping")
igual("buscar flete camión -> Transporte", buscar("flete camion", "", 1)[0][1]["hoja"], "Transporte e izaje")
igual("sinónimo rx", "radiografia" in tokens("RX 100%"), True)
# 18. Las 8 hojas más "Todos" en el Excel
from openpyxl import load_workbook  # noqa: E402

wb = load_workbook(PRECIOS / "catalogo_servicios.xlsx", read_only=True)
igual("hojas del Excel", wb.sheetnames, ["Todos"] + [n for _, n in cs.HOJAS])
# 19. Toda cita de la extracción está en su documento original
sys.path.insert(0, str(RAIZ / "herramientas"))
TEXTOS = RAIZ / "fuentes_originales" / "ofertas_texto"
col = lambda s: re.sub(r"\s+", " ", s or "").strip()  # noqa: E731
cache = {}


def texto_original(c, a):
    if c in ("FUENTE", "REPO"):
        p = RAIZ / ("fuentes_originales" if c == "FUENTE" else "") / a
        if p.suffix == ".xlsx":
            import warnings
            warnings.simplefilter("ignore")
            from datetime import datetime
            out = []
            for ws in load_workbook(p, data_only=True):
                for row in ws.iter_rows():
                    cs_ = []
                    for cell in row:
                        v = cell.value
                        if v is None:
                            continue
                        v = f"{v:.4f}".rstrip("0").rstrip(".") if isinstance(v, float) else (v.strftime("%Y-%m-%d") if isinstance(v, datetime) else str(v).strip())
                        cs_.append(v)
                    if cs_:
                        out.append(" | ".join(cs_))
            return "\n".join(out)
        if p.suffix == ".pdf":
            return subprocess.run(["pdftotext", "-layout", str(p), "-"], capture_output=True, text=True).stdout
        return p.read_text(encoding="utf-8", errors="replace")
    return (TEXTOS / c / (a + ".txt")).read_text(encoding="utf-8", errors="replace")


malas = 0
for r in ext:
    k = (r["carpeta_origen"], r["archivo_origen"])
    try:
        if k not in cache:
            cache[k] = col(texto_original(*k))
        if col(r["texto_original"]) not in cache[k]:
            malas += 1
            fallas.append(f"cita que no está en el original: {k[1][:60]} | {r['texto_original'][:60]}")
    except FileNotFoundError:
        malas += 1
        fallas.append(f"original inexistente: {k}")
igual("citas verificadas", malas, 0)
igual("cada precio de la extracción llega al historial", len(hist), len([r for r in ext if r["precio"].strip()]))

if fallas:
    print(f"FALLAN {len(fallas)}:")
    for f in fallas:
        print("  -", f)
    sys.exit(1)
print("Catálogo de servicios: todos los casos de regresión OK")
