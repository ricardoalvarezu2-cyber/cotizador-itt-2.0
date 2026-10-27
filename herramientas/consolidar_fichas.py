"""Consolida las fichas JSON de cotizaciones (una por carpeta) en tablas de la base de conocimiento.

Uso: python herramientas/consolidar_fichas.py CARPETA_FICHAS SUFIJO   (ej.: ... fichas 2026)

Genera:
  conocimiento/fichas_<SUFIJO>/*.json                    fichas completas (sin emails)
  conocimiento/comercial/cotizaciones_<SUFIJO>.csv        una fila por cotización
  conocimiento/comercial/cotizaciones_<SUFIJO>_items.csv  ítems ofertados
  conocimiento/precios/proveedores_<SUFIJO>.csv           cotizaciones de proveedores
  conocimiento/aprendizajes_<SUFIJO>.md                   aprendizajes por familia
"""
import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DESTINO = RAIZ / "conocimiento"
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
FAMILIAS = {"C": "Calentadores", "SEP": "Separadores", "F": "Filtros", "SK": "Skids", "M": "Manifolds",
            "CO": "Colectores", "P": "Puentes y tramos de medición", "CA": "Cañería / piping", "T": "Tanques",
            "TS": "Trampas scraper", "V": "Válvulas", "S": "Servicios / mano de obra", "OT": "Otros"}


def limpiar(valor):
    if isinstance(valor, str):
        return EMAIL.sub("[email]", valor)
    if isinstance(valor, list):
        return [limpiar(v) for v in valor]
    if isinstance(valor, dict):
        return {k: limpiar(v) for k, v in valor.items()}
    return valor


def codigo_familia(texto) -> str:
    t = str(texto or "").strip().upper()
    return next((c for c in sorted(FAMILIAS, key=len, reverse=True) if t.startswith(c)), "OT")


def escribir(ruta: Path, columnas, filas):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with ruta.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(columnas)
        w.writerows([["" if v is None else v for v in fila] for fila in filas])
    print(f"  {ruta.relative_to(RAIZ)}: {len(filas)} filas")


def main():
    origen, sufijo = Path(sys.argv[1]), sys.argv[2]
    fichas = []
    for archivo in sorted(origen.glob("*.json")):
        if archivo.name.startswith("asignacion"):
            continue
        fichas.append(limpiar(json.loads(archivo.read_text(encoding="utf-8"))))
    carpeta_fichas = DESTINO / f"fichas_{sufijo}"
    carpeta_fichas.mkdir(parents=True, exist_ok=True)
    cot, items, prov = [], [], []
    aprendizajes = defaultdict(list)
    for n, f in enumerate(sorted(fichas, key=lambda f: f.get("carpeta", "")), 1):
        nombre = re.sub(r"[^\w-]+", "_", f.get("carpeta", f"ficha_{n}"))[:90]
        (carpeta_fichas / f"{nombre}.json").write_text(json.dumps(f, ensure_ascii=False, indent=1), encoding="utf-8")
        fam = codigo_familia(f.get("familia"))
        oc = f.get("orden_compra") or {}
        cond = f.get("condiciones") or {}
        cot.append([f.get("carpeta"), f.get("cliente"), f.get("cliente_final"), f.get("numero_oferta"),
                    f.get("fecha_oferta"), f.get("fecha_ultima_modificacion"), fam, f.get("descripcion_corta"),
                    f.get("monto_total_ofertado"), f.get("moneda"), f.get("costo_total"), f.get("factor_venta"),
                    f.get("plazo_ofrecido"), f.get("plazo_dias"), cond.get("pago"), cond.get("validez"),
                    f.get("resultado"), oc.get("numero"), oc.get("fecha"), oc.get("monto"), f.get("confianza")])
        for it in f.get("items") or []:
            items.append([f.get("carpeta"), f.get("cliente"), f.get("fecha_oferta"), fam, it.get("descripcion"),
                          it.get("cantidad"), it.get("unidad"), it.get("precio_unitario"), it.get("precio_total"),
                          it.get("moneda"), it.get("datos_tecnicos")])
        for p in f.get("proveedores") or []:
            prov.append([p.get("fecha") or f.get("fecha_oferta") or f.get("fecha_ultima_modificacion"),
                         p.get("proveedor"), p.get("que"), p.get("precio"), p.get("moneda"), p.get("plazo_entrega"),
                         f.get("carpeta")])
        for a in f.get("aprendizajes") or []:
            aprendizajes[fam].append((f.get("carpeta"), a))
    escribir(DESTINO / f"comercial/cotizaciones_{sufijo}.csv",
             ["carpeta", "cliente", "cliente_final", "numero_oferta", "fecha_oferta", "ultima_modificacion",
              "familia", "descripcion", "monto_ofertado", "moneda", "costo_total", "factor_venta",
              "plazo_ofrecido", "plazo_dias", "pago", "validez", "resultado", "oc_numero", "oc_fecha", "oc_monto",
              "confianza"], cot)
    escribir(DESTINO / f"comercial/cotizaciones_{sufijo}_items.csv",
             ["carpeta", "cliente", "fecha_oferta", "familia", "descripcion", "cantidad", "unidad",
              "precio_unitario", "precio_total", "moneda", "datos_tecnicos"], items)
    escribir(DESTINO / f"precios/proveedores_{sufijo}.csv",
             ["fecha", "proveedor", "detalle", "precio", "moneda", "plazo_entrega", "carpeta_cotizacion"], prov)
    lineas = [f"# Aprendizajes de las cotizaciones {sufijo}", "",
              "Observaciones que dejó el análisis de cada carpeta, agrupadas por familia. Sirven como lista de "
              "control al cotizar un pedido parecido. Fuente: `fichas_" + sufijo + "/`.", ""]
    for fam in sorted(aprendizajes, key=lambda c: list(FAMILIAS).index(c)):
        lineas += [f"## {FAMILIAS[fam]}", ""]
        for carpeta, texto in aprendizajes[fam]:
            lineas.append(f"- {texto} *({carpeta})*")
        lineas.append("")
    (DESTINO / f"aprendizajes_{sufijo}.md").write_text("\n".join(lineas), encoding="utf-8")
    print(f"  conocimiento/aprendizajes_{sufijo}.md: {sum(len(v) for v in aprendizajes.values())} aprendizajes")


if __name__ == "__main__":
    main()
