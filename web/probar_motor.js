// Prueba del motor JS contra Python. Uso: node web/probar_motor.js
// 1) CAPEX (caso de control): costo 5.644,88 · unitario 7.620,59 · total 15.241,18 (índices congelados).
// 2) Paridad con armar_cotizacion.py en una cotización con válvulas Taval (factor FTV aparte): COT26-0330-001, FTV 1 y 1,5.
const fs = require("fs");
const { execFileSync } = require("child_process");
const Motor = require("./src/motor.js");
const datos = JSON.parse(fs.readFileSync(__dirname + "/datos.json", "utf8"));
const leer = c => JSON.parse(fs.readFileSync(`${__dirname}/../cotizaciones/${c}/cotizacion.json`, "utf8"));
let ok = true;
const comparar = (nombre, r, esperado) => {
  for (const k of Object.keys(esperado)) {
    const v = Math.round(r[k] * 100) / 100;
    if (Math.abs(v - esperado[k]) > 0.011) { ok = false; console.log(`FALLA ${nombre} ${k}: ${v} (esperado ${esperado[k]})`); }
  }
};
const r = Motor.calcular(leer("COT26-1003-001_CAPEX_OQ8209"), datos.indices);
comparar("CAPEX", r, { costo: 5644.88, precio_unitario: 7620.59, total: 15241.18 });
const ypf = leer("COT26-0330-001_YPF_LIC69343_SKID713");
for (const ftv of [1, 1.5]) {
  const cfg = { ...ypf, parametros: { ...ypf.parametros, FTV: ftv } };
  const py = JSON.parse(execFileSync("python3", ["-c", `import json,sys; sys.path.insert(0,"herramientas"); import armar_cotizacion as a
c=json.load(sys.stdin); print(json.dumps(a.calcular(c, a.leer_indices())))`], { cwd: __dirname + "/..", input: JSON.stringify(cfg) }).toString());
  comparar(`YPF FTV ${ftv}`, Motor.calcular(cfg, datos.indices), py);
}
console.log(ok ? `Motor JS OK: CAPEX costo ${r.costo.toFixed(2)} · unitario ${r.precio_unitario} · total ${r.total}; YPF con válvulas Taval igual a Python` : "Motor JS distinto de Python");
process.exit(ok ? 0 : 1);
