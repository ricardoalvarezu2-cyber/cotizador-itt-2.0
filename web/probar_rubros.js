// Prueba de rubros.js contra herramientas/ficha_rubros.py. Uso: node web/probar_rubros.js
// 1) Misma clasificación de renglones por rubro en todas las cotizaciones del repositorio.
// 2) Pasar todos los rubros a global con precio y volver a detallado: el motor JS da lo mismo que Python, y al volver queda igual que al principio.
// 3) Transporte: mismos equipos por camión y viajes.
const fs = require("fs");
const { execFileSync } = require("child_process");
const Motor = require("./src/motor.js"), Rubros = require("./src/rubros.js");
const datos = JSON.parse(fs.readFileSync(__dirname + "/datos.json", "utf8"));
const raiz = __dirname + "/..";
const py = (codigo, entrada) => JSON.parse(execFileSync("python3", ["-c", `import json,sys; sys.path.insert(0,"herramientas")
import armar_cotizacion as a, ficha_rubros as f
${codigo}`], { cwd: raiz, input: JSON.stringify(entrada) }).toString());
let ok = true;
const falla = t => { ok = false; console.log("FALLA " + t); };
const carpetas = fs.readdirSync(raiz + "/cotizaciones").filter(c => fs.existsSync(`${raiz}/cotizaciones/${c}/cotizacion.json`) && !c.startsWith("_"));
for (const c of carpetas) {
  const cot = JSON.parse(fs.readFileSync(`${raiz}/cotizaciones/${c}/cotizacion.json`, "utf8"));
  const p = py(`c=json.load(sys.stdin); print(json.dumps([f.rubro_de(i) for i in c["items"]]))`, cot);
  cot.items.forEach((it, i) => { if ((Rubros.rubroDe(it) || null) !== p[i]) falla(`${c} ${it.id}: JS ${Rubros.rubroDe(it)} · Python ${p[i]}`); });
}
const cot = JSON.parse(fs.readFileSync(`${raiz}/cotizaciones/COT26-0330-001_YPF_LIC69343_SKID713/cotizacion.json`, "utf8"));
const antes = JSON.stringify(Motor.calcular(cot, datos.indices).precio_unitario);
const g = JSON.parse(JSON.stringify(cot));
Object.keys(Rubros.RUBROS).forEach((r, i) => { Rubros.pasarAGlobal(g, r, "2026-10-28"); Rubros.globalDe(g, r).fuentes[0].precio = 1000 * (i + 1); });
const gp = py(`c=json.load(sys.stdin)
for i, r in enumerate(f.RUBROS):
    f.pasar_a_global(c, r, "2026-10-28"); next(x for x in c["items"] if x.get("global") and x["rubro"] == r)["fuentes"][0]["precio"] = 1000 * (i + 1)
print(json.dumps(a.calcular(c, a.leer_indices(c))))`, cot);
const gj = Motor.calcular(g, datos.indices);
for (const k of ["costo", "precio_unitario", "total"]) if (Math.abs(gj[k] - gp[k]) > 0.011) falla(`global ${k}: JS ${gj[k]} · Python ${gp[k]}`);
Object.keys(Rubros.RUBROS).forEach(r => Rubros.volverADetallado(g, r));
if (JSON.stringify(Motor.calcular(g, datos.indices).precio_unitario) !== antes) falla("al volver a detallado el precio no es el de antes");
const t = { ...cot, transporte: { largo_m: 6, ancho_m: 2.4, alto_m: 2.2 } };
const tj = Rubros.transporte(t, 9081), tp = py(`c=json.load(sys.stdin); print(json.dumps(f.transporte(c, 9081)))`, t);
if (tj.por_camion !== tp["por_camion"] || tj.viajes !== tp["viajes"] || tj.avisos.length !== tp["avisos"].length) falla(`transporte JS ${tj.por_camion}/${tj.viajes} · Python ${tp.por_camion}/${tp.viajes}`);
console.log(ok ? `Rubros JS OK: clasificación igual a Python en ${carpetas.length} cotizaciones; global y vuelta a detallado iguales; transporte ${tj.por_camion} por camión, ${tj.viajes} viaje(s)` : "Rubros JS distinto de Python");
process.exit(ok ? 0 : 1);
