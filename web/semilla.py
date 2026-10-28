"""Prepara la carga inicial de la base de la página (web/semilla.json): el firmante y una cotización de la carpeta
cotizaciones/, con los datos del plano (diámetro, serie, material, extremos) en cada renglón de material para la
tabla de la oferta técnica. Claude la carga con ArtifactData (batch de "set").

Uso: python web/semilla.py cotizaciones/<carpeta> [id] [--salida <carpeta>]
  Sin --salida: deja web/semilla.json (firmante + cotización + resumen) para la carga inicial.
  Con --salida: deja un JSON por documento (cotizaciones__<id>.json y resumenes__<id>.json) para subir con ArtifactData
  (batch de "set" con file_path); es lo que usa Claude Code al terminar un pedido de la página (web/LEEME.md).
"""
import csv
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def main(carpeta, ident="capex-oq8209", salida=None):
    c = Path(carpeta)
    cot = json.load(open(c / "cotizacion.json", encoding="utf-8"))
    of = json.load(open(c / "oferta.json", encoding="utf-8"))
    plano = {r["pos"]: r for r in csv.DictReader(open(c / "pedido" / "lista_materiales_plano.csv", encoding="utf-8"))}
    for it in cot["items"]:
        r = plano.get(str(it.get("pos")))
        if it["grupo"] == "material" and r:
            it["plano"] = {k: r[k] for k in ("descripcion", "diametro", "serie_sch", "material", "extremos", "modelo_fabricante") if r.get(k)}
            if "modelo_fabricante" in it["plano"]:
                it["plano"]["modelo"] = it["plano"].pop("modelo_fabricante")
    # transcripción literal del documento y kilos por unidad, para el Excel de Compras de la página (igual que lista_compras.py)
    sys.path.insert(0, str(RAIZ / "herramientas"))
    import lista_compras
    if (c / "pedido" / "transcripcion.json").exists():
        cot["transcripcion"] = json.load(open(c / "pedido" / "transcripcion.json", encoding="utf-8"))
    kg = {}
    for it in cot["items"]:
        if it["grupo"] == "material" and str(it.get("pos")) not in kg:
            k, _ = lista_compras.kg_por_unidad(plano.get(str(it.get("pos")), {"descripcion": it["descripcion"]}), it)
            if k is not None:
                kg[str(it["pos"])] = round(k, 3)
    cot["kg_compras"] = kg
    cot["firmante_id"] = "matias-russo"
    of.pop("firma", None)  # la firma sale del firmante elegido
    ahora = datetime.now().isoformat(timespec="seconds")
    calc = json.loads(subprocess.run(["node", "-e", f"""
const M=require('{RAIZ}/web/src/motor.js'),d=require('{RAIZ}/web/datos.json'),c=require('{c.resolve()}/cotizacion.json');
const r=M.calcular(c,d.indices);console.log(JSON.stringify({{u:r.precio_unitario,t:r.total}}))"""], capture_output=True, text=True, check=True).stdout)
    ops = [
        {"op": "set", "path": "firmantes/matias-russo", "data": {"nombre": "Matías Russo", "cargo": "Representante Comercial", "telefono": "", "celular": "", "email": ""}},
        {"op": "set", "path": f"cotizaciones/{ident}", "data": {"cot": cot, "oferta": of, "creado": ahora, "guardado": ahora}},
        {"op": "set", "path": f"resumenes/{ident}", "data": {"codigo": cot["codigo"], "titulo": cot["titulo"], "cliente": cot["cliente"]["nombre"],
                                                           "estado": cot["estado"], "unitario": calc["u"], "total": calc["t"], "actualizado": ahora}},
    ]
    if salida:
        ops[1]["data"]["editor"] = "claude-code"  # la página avisa que la actualizó Claude Code
        Path(salida).mkdir(parents=True, exist_ok=True)
        for o in ops[1:]:
            f = Path(salida) / (o["path"].replace("/", "__") + ".json")
            f.write_text(json.dumps(o["data"], ensure_ascii=False), encoding="utf-8")
            print(f"{o['path']} → {f}")
        print(f"unitario USD {calc['u']} · total USD {calc['t']}")
        return
    archivo = RAIZ / "web" / "semilla.json"
    archivo.write_text(json.dumps(ops, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{archivo.relative_to(RAIZ)}: {len(ops)} documentos · unitario USD {calc['u']} · {len(json.dumps(ops[1]['data'])) / 1024:.0f} KiB la cotización")


if __name__ == "__main__":
    a = sys.argv[1:]
    sal = None
    if "--salida" in a:
        i = a.index("--salida")
        sal = a[i + 1]
        del a[i:i + 2]
    main(*a, salida=sal)
