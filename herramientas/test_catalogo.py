"""Test de regresión del catálogo de materiales: los casos reales que encontraron las revisiones y la auditoría del
27/10/2026 (control C11). Correr después de tocar catalogo_materiales.py, numeros.py o indice_proyectos.py:

  python herramientas/test_catalogo.py

Si algo falla, el catálogo volvería a leer mal un precio que ya se corrigió.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from catalogo_materiales import atributos, desambiguar, expandir, familia_de, iva_de, tramo, unidad_norm  # noqa: E402
from indice_proyectos import norm, pulgadas  # noqa: E402
from numeros import fecha_iso, leer_numero  # noqa: E402

fallas = []


def igual(nombre, obtenido, esperado):
    if obtenido != esperado:
        fallas.append(f"{nombre}: dio {obtenido!r}, se esperaba {esperado!r}")


def at(texto):
    t = expandir(norm(texto))
    f = familia_de(t)
    return f, atributos(t, f)


# números (4.500 / 4,500 / 4500)
for x, v in [("4,413.92", 4413.92), ("4.413,92", 4413.92), ("28.500", 28500), ("4.550 + IVA", 4550), ("1.096.71", 1096.71),
             ("0,904", 0.904), ("12,87", 12.87), ("1.250.000", 1250000), ("$16.114,07 + IVA", 16114.07), ("4500", 4500)]:
    igual(f"número {x}", leer_numero(x)[0], v)
igual("4,500 es ambiguo", leer_numero("4,500")[1], True)
igual("26,338 c/u con total 52.676 y 2 unidades", desambiguar(26.338, "2 válvulas de control, USD 26,338 c/u", 52676)[0], 26338)
igual("6,010 c/u con total 60,10 por 10", desambiguar(6.01, "10 juntas 6,010 c/u", 60.1)[0], 6.01)
# fechas
for x, v in [("Cot 25/03/26", "2026-03-25"), ("16/19/2025", ""), ("02/07/025", ""), ("12/09/2025", "2025-09-12"), ("2099-01-01", "")]:
    igual(f"fecha {x}", fecha_iso(x), v)
# IVA
igual("IVA: sin IVA al lado del precio", iva_de("78 c/u, total 8.502 sin IVA (10.287,42 con IVA 21%)", 6)[1], 1.0)
igual("IVA: iva incluido", iva_de("121 c/u iva incluido", 6)[1], 1.21)
igual("IVA: 10,5%", iva_de("110,5 c/u con IVA 10,5%", 9)[1], 1.105)
igual("IVA: no dice", iva_de("100 c/u", 6)[1], 1.0)
# fracciones y diámetros
igual("½ no es 12", norm("1½"), "1 1/2")
igual("2,5\"", pulgadas(norm('2,5"')), [2.5])
igual("pulg-eq no es diámetro", pulgadas(norm("13,09 pulg-diam-eq")), [])
igual("codo 45° 1/2\" es 1/2\"", at('Codo Radio Largo 45° 1/2" Std ASTM A234 WPB')[1].get("diametro"), '0.5"')
# un renglón, un ítem
igual("tramo Simat", tramo('Tapón hexagonal 2" NPT (6.66) y 2 tees 2" #6000 (126.36 c/u)'), '2 tees 2" #6000 (126.36 c/u)')
igual("tramo MS Juntas", tramo('Juntas anillo RTJ BX153 (6,01 c/u), kit aislante 3" #600 (167,31)'), "Juntas anillo RTJ BX153 (6,01 c/u)")
# atributos
igual("stock ESF PT 1½ 150 RF", {k: at("ESF PT A/FUEGO 1½ 150 RF WCB JTA TR INT 316 ASTO TR PALANCA")[1].get(k) for k in ("diametro", "serie")},
      {"diametro": '1.5"', "serie": "150"})
igual("4#150RF", at("Valv de control 4#150RF AN667")[1].get("serie"), "150")
igual("A694 F60", at("brida WN 10000 RJ 2 9/16 ASTM A694 F60")[1].get("material"), "A694 F60")
igual("B8M no es B7", at("ESPARRAGO 7/8 x 7 ASTM A 193 B8M")[1].get("material"), "A193 B8M")
igual("FF de factura", "FF" in at('24 juntas RTJ R45 6" #900, 60 días FF')[1].get("extremos", ""), False)
igual("SW en junta espiralada", at('JUNTA ESPIRALADA SW AC 316 LFG 4" #600')[1].get("extremos", ""), "")
igual("casquete 36\" x 3/8\" sin diametro2", at('Casquetes SE 36" x 3/8"')[1].get("diametro2"), None)
igual("XS 10\" no es Sch 80", at('Casquete Semieliptico 10" XS ASTM A234 WPB')[1].get("schedule"), "XS")
igual("caño 48,3 x 3,68", {k: at("Tubo s/costura 48,3 x 3,68 mm A53/A106")[1].get(k) for k in ("diametro", "schedule", "costura")},
      {"diametro": '1.5"', "schedule": "40", "costura": "sin costura"})
igual("manguera R13 no es junta", at("mangueras SAE 100 R13")[0], "OTR")
igual("té en caja no es accesorio", at("TE EN CAJA x 100 UNIDADES")[0], "OTR")
igual("codo forjado 3000 es AFO", at("CODO RADIO CORTO 90° 2 3000 SW ASTM A105")[0], "AFO")
igual("unidad 6mts", unidad_norm("6mts"), "tira de 6 m")

# valores del cepo llevados a su valor verosímil (decisión 28/10/2026)
from catalogo_materiales import factor_cepo  # noqa: E402
igual("cepo: precio maestro del stock × 0,64", factor_cepo("2024-11-01", "stock (precio maestro)")[0], 0.64)
igual("cepo: compra del stock sigue descartada", factor_cepo("2023-06-13", "compra")[0], None)
igual("cepo: otros × oficial/blue del mes", round(factor_cepo("2024-05-20", "cotización")[0], 3), round(904.79 / 1125.48, 3))

if fallas:
    print(f"FALLAN {len(fallas)}:")
    for f in fallas:
        print("  -", f)
    sys.exit(1)
print("Catálogo: todos los casos de regresión OK")
