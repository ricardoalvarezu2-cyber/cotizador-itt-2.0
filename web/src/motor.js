// Motor de cálculo del cotizador: mismas fórmulas que herramientas/armar_cotizacion.py (calcular y factor).
// Se prueba contra Python con web/probar_motor.js (la CAPEX tiene que dar costo 5.644,88 · unitario 7.620,59 · total 15.241,18).
const Motor = (() => {
  // idx: [{mes:"2024-01", local, cpi}, ...] ordenado por mes
  function factorAjuste(item, idx, fref, aplicar) {
    if (!aplicar) return 1;
    const col = item.grupo !== "material" ? "local" : "cpi";
    const f = (item.fuentes[0].fecha || "").slice(0, 7);
    let mes = f < fref ? f : fref;            // min(fecha, referencia)
    if (mes < idx[0].mes) mes = idx[0].mes;  // max(…, primer mes de la tabla)
    const en = m => { let v = idx[0]; for (const r of idx) if (r.mes <= m) v = r; return v[col]; };
    return en(fref) / en(mes);
  }

  function redondear(x, d = 2) {
    const k = 10 ** d;
    return Math.round((x + Number.EPSILON) * k) / k;
  }

  // Índices de la cotización: los congelados (al pasar a revisado) o los vigentes de la base
  function indicesDe(cfg, idx) {
    const cg = cfg.indices_congelados;
    return cg && cg.filas && cg.filas.length ? cg.filas : idx;
  }

  const esTaval = it => it.grupo === "material" && !!it.taval;

  function calcular(cfg, idx) {
    idx = indicesDe(cfg, idx);
    const p = cfg.parametros, fref = p.fecha_referencia.slice(0, 7);
    const sub = { material: 0, mo: 0, servicio: 0, taval: 0 }, sub0 = { material: 0, mo: 0, servicio: 0, taval: 0 };
    const ftv = p.FTV ?? 1;  // válvulas Taval (empresa del grupo): factor aparte, por defecto 1
    const filas = cfg.items.map(it => {
      const fa = factorAjuste(it, idx, fref, p.AJ);
      const base = it.cantidad * it.fuentes[0].precio, g = esTaval(it) ? "taval" : it.grupo;
      sub[g] += base * fa;
      sub0[g] += base;
      return { id: it.id, base, factor: fa, ajustado: base * fa };
    });
    const cont = sub.material * p.CONT / 100, tav = sub.taval * (1 + p.CONT / 100);
    const costo = sub.material + cont + tav + sub.mo + sub.servicio;
    const costo0 = (sub0.material + sub0.taval) * (1 + p.CONT / 100) + sub0.mo + sub0.servicio;
    const precio = redondear((sub.material + cont) * p.FM + tav * ftv + (sub.mo + sub.servicio) * p.FMO, 2);
    const flete = p.TRANS ? (p.TR_ARS / p.TC + p.TR_EMB) * p.TR_F : 0;
    return { sub, cont, tav, ftv, costo, costo0, precio_unitario: precio, flete, total: redondear(precio * p.N + flete, 2), filas };
  }

  // Escenarios de factor (el factor lo define la dirección; la herramienta propone 1,35 y muestra alternativas)
  function escenarios(cfg, idx, factores = [1.25, 1.30, 1.35, 1.40, 1.50]) {
    return factores.map(F => {
      const c = calcular({ ...cfg, parametros: { ...cfg.parametros, FM: F, FMO: F } }, idx);
      return { F, unitario: c.precio_unitario, total: c.total, margen: 1 - c.costo / c.precio_unitario };
    });
  }
  return { factorAjuste, calcular, escenarios, redondear, indicesDe, esTaval };
})();
if (typeof module !== "undefined") module.exports = Motor;
