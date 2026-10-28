// Prueba del motor JS contra Python con la CAPEX (caso de control). Uso: node web/probar_motor.js
const fs = require("fs");
const Motor = require("./src/motor.js");
const datos = JSON.parse(fs.readFileSync(__dirname + "/datos.json", "utf8"));
const cfg = JSON.parse(fs.readFileSync(__dirname + "/../cotizaciones/COT26-1003-001_CAPEX_OQ8209/cotizacion.json", "utf8"));
const r = Motor.calcular(cfg, datos.indices);
const esperado = { costo: 5644.88, precio_unitario: 7620.59, total: 15241.18 };
let ok = true;
for (const k of Object.keys(esperado)) {
  const v = Math.round(r[k] * 100) / 100;
  if (Math.abs(v - esperado[k]) > 0.005) { ok = false; console.log(`FALLA ${k}: ${v} (esperado ${esperado[k]})`); }
}
console.log(ok ? `Motor JS OK: costo ${r.costo.toFixed(2)} · unitario ${r.precio_unitario} · total ${r.total}` : "Motor JS distinto de Python");
process.exit(ok ? 0 : 1);
