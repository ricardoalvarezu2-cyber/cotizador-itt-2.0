// Prueba de la planilla Excel de la página (Documentos.planilla) contra la de Python (herramientas/planilla_excel.py).
// Uso: node web/probar_planilla.js   (necesita LibreOffice)
// Para cada cotización del repositorio arma las dos planillas con los mismos datos, las recalcula con LibreOffice y compara
// hoja por hoja y celda por celda los valores (precios, subtotales, totales, textos).
const fs = require("fs"), path = require("path"), os = require("os");
const { execFileSync } = require("child_process");
const raiz = path.join(__dirname, "..");
// la misma librería que carga la página (cdn.jsdelivr.net/npm/xlsx-js-style@1.2.0/dist/xlsx.bundle.js), copiada en web/vendor
// para no depender de la red; se carga como en el navegador (sin require, que pediría cpexcel.js)
const vm = require("vm"), caja = {};
vm.createContext(caja); vm.runInContext(fs.readFileSync(path.join(__dirname, "vendor", "xlsx-js-style-1.2.0.bundle.js"), "utf8"), caja);
const XLSX = caja.XLSX;
global.XLSX = XLSX;
global.Busqueda = require("./src/busqueda.js"); global.Motor = require("./src/motor.js"); global.Ficha = require("./src/ficha.js"); global.Rubros = require("./src/rubros.js");
global.Blob = class { constructor(p) { this.buf = Buffer.from(p[0]); } };
const Documentos = require("./src/documentos.js");
const datos = JSON.parse(fs.readFileSync(path.join(__dirname, "datos.json"), "utf8"));
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "planilla-"));
const carpetas = fs.readdirSync(path.join(raiz, "cotizaciones")).filter(c => /^COT/.test(c));
let ok = true;
for (const c of carpetas) {
  const d = path.join(tmp, c); fs.mkdirSync(d);
  // Python arma su planilla y deja la cotización con los atributos que usó (atributos_plano.atributos_items)
  const cot = JSON.parse(execFileSync("python3", ["-c", `import json,sys; sys.path.insert(0,"herramientas")
import armar_cotizacion as a, planilla_excel as p
from pathlib import Path
c=Path("cotizaciones/${c}"); cfg=json.load(open(c/"cotizacion.json")); p.escribir(cfg,c,a.filas_indices(cfg),"${d}/py.xlsx")
import csv, ficha_rubros as f  # renglones como los arma semilla.py para la página (familia, datos y plano), como probar_ficha.js
pl=c/"pedido"/"lista_materiales_plano.csv"
plano={r["pos"]:r for r in csv.DictReader(open(pl))} if pl.exists() else {}
for it in cfg["items"]:
    if it["grupo"]=="material":
        it["fam"],it["at"]=f.fam_at(it)
        q=plano.get(str(it.get("pos")))
        if q:
            it["plano"]={k:q[k] for k in ("descripcion","diametro","serie_sch","material","extremos") if q.get(k)}
            if q.get("extremos_campo"): it["plano"]["extremos_campo"]=q["extremos_campo"]
            it["plano"]["cantidad"],it["plano"]["unidad"]=q["cantidad"],q["unidad"]
print(json.dumps(cfg))`], { cwd: raiz, maxBuffer: 1 << 28 }).toString());
  let of = {}; try { of = JSON.parse(fs.readFileSync(path.join(raiz, "cotizaciones", c, "oferta.json"), "utf8")); } catch (e) { /* sin oferta */ }
  // índices como los da la página (Motor.indicesDe toma los congelados si están)
  const idx = datos.indices;
  fs.writeFileSync(path.join(d, "js.xlsx"), Documentos.planilla(cot, idx, datos, of).buf);
  execFileSync("soffice", ["--headless", "--convert-to", "xlsx", "--outdir", path.join(d, "r"), path.join(d, "py.xlsx"), path.join(d, "js.xlsx")], { stdio: "ignore" });
  const out = execFileSync("python3", ["-c", `import sys, datetime
from openpyxl import load_workbook
a=load_workbook("${d}/r/py.xlsx",data_only=True); b=load_workbook("${d}/r/js.xlsx",data_only=True)
dif=[]
if a.sheetnames!=b.sheetnames: dif.append(f"hojas {a.sheetnames} / {b.sheetnames}")
def v(x):
    if isinstance(x,(int,float)) and not isinstance(x,bool): return round(float(x),2)
    if isinstance(x,datetime.datetime): return x.date().isoformat()
    return "" if x is None else str(x).strip()
# datos.json no lleva paso ni norma del catálogo (web/construir_datos.py): esas columnas del antecedente no se comparan
SALTEAR=("Antecedente: Paso","Antecedente: Norma","Antecedente: otros datos")
for n in a.sheetnames:
    if n not in b.sheetnames or n=="Índices": continue
    A,B=a[n],b[n]
    enc={}
    for r in range(1,max(A.max_row,B.max_row)+1):
        if A.cell(r,1).value=="Pos": enc={k:str(A.cell(r,k).value or "") for k in range(1,A.max_column+1)}
        for k in range(1,max(A.max_column,B.max_column)+1):
            if n=="Materiales" and enc.get(k,"") in SALTEAR: continue
            x,y=v(A.cell(r,k).value),v(B.cell(r,k).value)
            if x!=y and not (isinstance(x,float) and isinstance(y,float) and abs(x-y)<=0.011): dif.append(f"{n}!{A.cell(r,k).coordinate}: py={x!r} js={y!r}")
for n in ("PrecioUnitario","TotalOferta","CostoUnitario","Cantidad","Flete","IncluirFlete"):
    for w,t in ((a,"py"),(b,"js")):
        if n not in w.defined_names: dif.append(f"falta el nombre {n} en {t}")
print("\\n".join(dif[:25])+(f"\\n… y {len(dif)-25} más" if len(dif)>25 else ""))
print(len(dif))`]).toString().trim().split("\n");
  const n = +out.pop();
  if (n) { ok = false; console.log(`FALLA ${c}: ${n} diferencias\n  ` + out.join("\n  ")); } else console.log(`OK ${c}`);
}
fs.rmSync(tmp, { recursive: true, force: true });
console.log(ok ? "Planilla de la página igual a la de Python" : "Planilla de la página distinta de la de Python");
process.exit(ok ? 0 : 1);
