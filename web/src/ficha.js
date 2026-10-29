// Ficha por rubro calculada en la página (botón "Recalcular"): soldaduras, kg, m², placas de RX y procedimientos, sin IA.
// Espejo de herramientas/precotizar.py (soldaduras, superficie_pintura), herramientas/controles_tablas.py (peso_item) y
// herramientas/ficha_rubros.py (armar). Usa los datos del plano de cada renglón (it.plano) y la familia y atributos del
// catálogo (it.fam, it.at). Se prueba contra Python con web/probar_ficha.js.
const Ficha = (() => {
  const FRAC = { "½": " 1/2", "¼": " 1/4", "¾": " 3/4", "⅛": " 1/8", "⅜": " 3/8", "⅝": " 5/8", "⅞": " 7/8", "⁄": "/", "ø": " diam ", "Ø": " diam ", "⌀": " diam ", "°": " grados ", "º": " grados " };
  function norm(t) {
    let s = String(t ?? "");
    for (const [a, b] of Object.entries(FRAC)) s = s.split(a).join(b);
    return s.normalize("NFKD").replace(/[\u0300-\u036f]/g, "").replace(/[^\x00-\x7f]/g, "").toLowerCase().replace(/\s+/g, " ");
  }
  const SCHEDULES = new Set(["5", "10", "20", "30", "40", "60", "80", "100", "120", "140", "160", "STD", "XS", "XXS"]);
  const OLETS = /cupla|sockolet|threadolet|thredolet|weldolet|elbowlet|latrolet|nipolet|\bolet/;
  const AJUSTE_DIRECTAS = 0.75, M2_POR_KG_ESTRUCTURA = 0.030;
  const INTERNOS = /bafle|deflector|separador de niebla|interno|elemento filtrante|placa apoyo|viruta|refuerzo/;
  const LARGO_EQ_D = [[/valvula|\bvalv\b/, 6.0], [/\btee\b|\bte\b/, 3.0], [/codo 45|curva 45/, 1.2], [/\bcodo|\bcurva/, 2.4], [/reduc/, 1.5], [/brida/, 1.5], [/casquete|\bcap\b|tapa/, 1.0]];
  const ESTRUCTURA = /estructura|perfileria|bastidor|\bskid\b|\bupn\b|\bipn\b|\bheb\b|\bhea\b|\bipe\b|angulo|planchuela/;
  const OD_NPS = [[21.3, 0.5], [26.7, 0.75], [33.4, 1], [42.2, 1.25], [48.3, 1.5], [60.3, 2], [73.0, 2.5], [88.9, 3], [101.6, 3.5], [114.3, 4], [141.3, 5],
    [168.3, 6], [219.1, 8], [273.0, 10], [323.8, 12], [323.9, 12], [355.6, 14], [406.4, 16], [457.0, 18], [457.2, 18], [508.0, 20], [609.6, 24], [610.0, 24]];

  function frac(s) { let t = 0; for (const p of String(s).trim().split(/\s+/)) { if (p.includes("/")) { const [a, b] = p.split("/"); t += +a / +b; } else t += +p; } return t; }
  function dnDe(txt) {
    const m = String(txt ?? "").replace(/"/g, " ").match(/(\d+\s\d\/\d|\d+\/\d+|\d+(?:[.,]\d+)?)/);
    if (!m) return null;
    const v = frac(m[1].replace(",", "."));
    return isFinite(v) ? v : null;
  }
  const partesSch = v => String(v ?? "").toUpperCase().split(/\s+X\s+|[/ ]|(?<=\d)X(?=\d)/).filter(p => p.replace(/^#+|#+$/g, "")).map(p => p.replace(/^#+|#+$/g, "").replace("SCH", ""));
  const schDe = v => partesSch(v).find(p => SCHEDULES.has(p)) || "";
  const largoM = d => { const m = norm(d).match(/(\d[\d.]*)\s?mm/); return m ? parseFloat(m[1].replace(/\./g, "")) / 1000 : null; };
  const barraM = d => (dnDe(d) || 0) >= 3 ? 12.0 : 6.0;
  function espesorMm(r) {
    const m = (String(r.descripcion || "") + " " + String(r.serie_sch || "")).match(/\b(?:esp|e)\s*[.=:]?\s*(\d+(?:[.,]\d+)?(?:\s*\d+\/\d+|\/\d+)?)\s*("|mm|pulg)/i);
    if (!m) return null;
    const v = m[1].includes("/") ? frac(m[1].replace(",", ".")) : parseFloat(m[1].replace(",", "."));
    return m[2].toLowerCase() !== "mm" ? v * 25.4 : v;
  }
  function factorEspesor(dn, sch, tabla, esp) {
    if (esp && dn != null) {
      const fs = tabla.filter(r => Math.abs(r.dn - dn) < 1e-6 && r.e);
      if (fs.length) { const r = fs.reduce((a, b) => Math.abs(b.e - esp) < Math.abs(a.e - esp) ? b : a); return [r.fe, r.pch || 0, r.pgr || 0]; }
    }
    sch = sch || "40";
    const r = tabla.find(r => dn != null && Math.abs(r.dn - dn) < 1e-6 && (r.sch === sch || r.cl === sch));
    return r ? [r.fe, r.pch || 0, r.pgr || 0] : [1.0, 0, 0];
  }
  const odM = dn => { const o = OD_NPS.find(([, n]) => Math.abs(n - dn) < 1e-6); return o ? o[0] / 1000 : dn * 0.0254; };
  const diams = d => String(d || "").toLowerCase().split(/\s*x\s*/).map(dnDe).filter(Boolean);

  // Renglones del plano a partir de los ítems (los que tienen columna de extremos)
  function filasDe(cot) {
    return cot.items.filter(i => i.grupo === "material" && i.plano && (i.plano.extremos || i.plano.diametro)).map(i => ({
      pos: String(i.pos), descripcion: i.plano.descripcion || i.descripcion, diametro: i.plano.diametro || "", serie_sch: i.plano.serie_sch || "",
      material: i.plano.material || "", extremos: i.plano.extremos || "", cantidad: i.plano.cantidad ?? i.cantidad, unidad: i.plano.unidad ?? i.unidad,
      ...(i.plano.extremos_campo !== undefined ? { extremos_campo: i.plano.extremos_campo } : {}) }));
  }

  // Pulgadas equivalentes de soldadura (precotizar.soldaduras)
  function soldaduras(filas, datos, facAcc = 1.75) {
    const tabla = datos.soldadura;
    let bwEq = 0, juntasOlet = 0, juntasSw = 0, extremosBw = 0, nSwOlet = 0; const placas = [0, 0], detalle = [];
    const hayCampo = filas.some(r => "extremos_campo" in r);
    const esCanoM = r => /\bcano\b|\bcanos\b|\btubo\b/.test(norm(r.descripcion)) && norm(r.unidad).startsWith("m");
    const porMetro = filas.filter(r => esCanoM(r) && String(r.extremos).toUpperCase().includes("BW"));
    const diamCano = new Set(porMetro.flatMap(r => diams(r.diametro)));
    const mult = porMetro.length ? 2 * AJUSTE_DIRECTAS : 1;
    for (const r of porMetro) {
      const dn = dnDe(r.diametro), q = +r.cantidad || 0, emp = Math.max(0, Math.ceil(q / barraM(r.diametro) - 1e-9) - 1);
      if (emp && dn) {
        const [f, pch, pgr] = factorEspesor(dn, schDe(r.serie_sch), tabla, espesorMm(r));
        bwEq += 2 * emp * dn * f; extremosBw += 2 * emp; placas[0] += emp * pch; placas[1] += emp * pgr;
      }
    }
    for (const r of filas) {
      if (porMetro.includes(r)) continue;
      const ext = String(r.extremos).toUpperCase().replace(/-M/g, "").replace(/-H/g, "");
      let toks = ext.split("/").map(t => t.trim()).filter(Boolean);
      const d = norm(r.descripcion);
      if (toks.length === 1) {
        const n = /\btee\b|\bte\b/.test(d) ? 3 : (new RegExp("casquete|\\bcap\\b|brida|\\btapa\\b|cierre rapido|" + OLETS.source).test(d) ? 1 : 2);
        toks = Array(n).fill(toks[0]);
      }
      const nBw = toks.filter(t => t === "BW").length, nSw = toks.filter(t => t === "SW").length;
      if (!(nBw || nSw)) continue;
      const q = +r.cantidad || 0;
      let dn = dnDe(r.diametro); const sch = schDe(r.serie_sch);
      let [f, pch, pgr] = factorEspesor(dn, sch, tabla, espesorMm(r));
      if (OLETS.test(d)) {
        const fa = d.includes("weldolet") ? 2.5 : facAcc;
        const ds = diams(r.diametro); dn = ds.length ? Math.min(...ds) : dn;
        juntasOlet += (nBw + nSw) * q * (dn || 0) * fa; nSwOlet += (nBw + nSw) * q;
        continue;
      }
      const campo = +(r.extremos_campo || 0), dims = diams(r.diametro);
      const mR = (!diamCano.size || dims.some(x => diamCano.has(x))) ? mult : 1;
      const bwTaller = Math.max(0, nBw - campo) * q * mR;
      extremosBw += bwTaller;
      if (nBw && !campo && dims.length === 2 && dims[0] !== dims[1]) {
        const schs = [...String(r.serie_sch).split(/\s*x\s*/).map(x => schDe(x) || sch), sch];
        const f2 = factorEspesor(dims[1], schs.length > 2 ? schs[1] : sch, tabla)[0];
        const prom = ((nBw - 1) * dims[0] * f + 1 * dims[1] * f2) / nBw;
        bwEq += bwTaller * prom; dn = prom; f = 1.0;
      } else bwEq += bwTaller * (dn || 0) * f;
      juntasSw += nSw * q * (dn || 0) * f; nSwOlet += nSw * q;
      placas[0] += bwTaller / 2 * pch; placas[1] += bwTaller / 2 * pgr;
      if (/\bvirola/.test(d) && largoM(r.descripcion)) bwEq += 2 * (q * largoM(r.descripcion) * 1000 / (Math.PI * 25.4)) * f;
    }
    const avisos = [];
    if (extremosBw % 2 && !porMetro.length) avisos.push(`Quedan ${extremosBw} extremos BW de taller (número impar): falta marcar algún extremo de campo o una pieza`);
    if (!hayCampo && extremosBw) avisos.push("La tabla no tiene la columna extremos_campo: se supuso que TODOS los extremos BW se sueldan en taller. Confirmar en el dibujo cuáles quedan para campo");
    return { juntas_bw: Math.ceil(extremosBw / 2 - 1e-9), pulg_eq: Math.round((bwEq / 2 + juntasSw + juntasOlet) * 1000) / 1000, placas, juntas_sw_olet: nSwOlet, avisos };
  }

  // ---------------------------------------------------------------- pesos (controles_tablas.peso_item)
  const pulg = d => { const v = parseFloat(String(d ?? "").replace(/"/g, "")); return isFinite(v) && /^\s*[\d.]+"?\s*$/.test(String(d ?? "")) ? v : null; };
  function schTabla(sch, dn) {
    const s = String(sch || "").toUpperCase();
    if ((s === "40" || s === "STD") && (dn || 0) <= 10) return "STD";
    if ((s === "80" || s === "XS") && (dn || 0) <= 8) return "XS";
    return s;
  }
  function fracPulg(t) {
    t = String(t).trim().replace(/"/g, "");
    if (t.includes(" ")) { const [a, ...b] = t.split(" "); const x = fracPulg(b.join(" ")); return x == null ? null : +a + x; }
    if (t.includes("/")) { const [a, b] = t.split("/"); return +b ? +a / +b : null; }
    const v = parseFloat(t); return isFinite(v) ? v : null;
  }
  function pesoValvula(it, at, P) {
    const dn = pulg(at.diametro), serie = String(at.serie || "").replace(/\D/g, "");
    const t = norm(`${it.descripcion} ${it.especificacion || ""} ${at.tipo || ""}`), mat = norm((at.material || "") + " " + t), ext = norm((at.extremos || "") + " " + t);
    const roscada = /\bnpt\b|\bsw\b|rosca|socket/.test(ext) && !/\brf\b|\brtj\b|brid/.test(ext);
    if (!dn || !serie) return [null, null, "válvula sin diámetro o serie"];
    const inox = /316|304|cf8m|inox/.test(mat) && !/a ?216|wcb|a ?105|carbono/.test(mat);
    const buscar = (tipos, mats) => P.valv.filter(r => tipos.includes(r[0]) && r[2] === serie && Math.abs(r[1] - dn) < 0.01 && (!mats || mats.includes(r[3])) && !r[5]);
    let cand = [];
    if (t.includes("esferica")) {
      if (roscada) {
        const forjada = /a ?105|f ?316|f ?304|forjad/.test(mat) && !/a ?216|wcb|cf8m|fundid/.test(mat);
        const tipo = "ESFERICA PT FLOTANTE " + (forjada ? "FORJADA" : "FUNDIDA") + " NPT (API 608)";
        const mats = forjada ? (inox ? ["F316"] : ["A105"]) : (inox ? ["CF8M"] : ["WCB"]);
        cand = buscar([tipo], mats); if (!cand.length) cand = buscar([tipo]);
      } else {
        const base = /paso reducido|\bpr\b/.test(t) ? "ESFERICA PR" : "ESFERICA PT";
        cand = buscar([base + " FLOTANTE"]); if (!cand.length) cand = buscar([base + " GUIADA"]);
      }
    } else if (t.includes("retencion")) {
      if (/wafer|dual/.test(t)) cand = buscar(["RETENCION WAFER DUAL PLATE"]);
      else if (roscada && dn <= 2) return [null, null, "retención roscada: sin tabla"];
      else cand = buscar(["RETENCION A CLAPETA"]);
    } else if (/esclusa|compuerta|\bgate\b/.test(t)) cand = buscar([roscada && dn <= 2 ? "ESCLUSA API 602" : "ESCLUSA"]);
    else if (t.includes("globo")) cand = buscar([roscada && dn <= 2 ? "GLOBO API 602" : "GLOBO"]);
    else if (t.includes("filtro") && /\by\b|tipo y/.test(t)) cand = buscar(["FILTRO Y"]);
    else return [null, null, "válvula de otro tipo: sin tabla"];
    if (!cand.length) return [null, null, `sin peso en la lista Taval para ${dn}" #${serie}`];
    return [cand[0][4], null, `${cand[0][0].toLowerCase()} ${dn}" #${serie} (Taval Lista 30)`];
  }
  function pesoOlet(it, at, P) {
    const d = norm(it.descripcion + " " + (it.especificacion || ""));
    const tipo = ["weldolet", "sockolet", "thredolet"].find(t => d.includes(t) || (t === "thredolet" && d.includes("threadolet")));
    if (!tipo) return [null, null, "olet de otro tipo: sin tabla"];
    let ms = [...(it.descripcion + " " + (it.especificacion || "")).matchAll(/(\d+(?: \d+\/\d+)?|\d+\/\d+)"/g)].map(m => fracPulg(m[1])).filter(Boolean);
    if (!ms.length) ms = [pulg(at.diametro)].filter(Boolean);
    const salida = ms.length ? Math.min(...ms) : null;
    if (!salida) return [null, null, "olet sin medida de salida"];
    const clase = tipo !== "weldolet" ? (at.serie || "3000") : schTabla(at.schedule || "STD", 1);
    const c = P.olets.find(r => r[0] === tipo && r[1] === salida && r[2].startsWith(clase));
    return c ? [c[3], null, `${tipo} salida ${salida}" ${clase} (Bonney Forge)`] : [null, null, `sin tabla para ${tipo} ${salida}" ${clase}`];
  }
  function pesoEsparrago(it, at, P) {
    const d = pulg(at.diametro);
    const m = String(at.medida || "").match(/x\s*(\d+(?: \d+\/\d+)?|\d+\/\d+)/);
    let largo = m ? fracPulg(m[1]) : null;
    if (!largo) { const mm = norm(it.descripcion).match(/[\d.]+\s*x\s*(\d{2,3})\b/); largo = mm ? +mm[1] / 25.4 : null; }
    if (!d || !largo) return [null, null, "espárrago sin diámetro o largo"];
    const k = Object.keys(P.esp.var).find(x => Math.abs(+x - d) < 1e-6), var_ = k != null ? P.esp.var[k] : null;
    const kt = Object.keys(P.esp.tue).find(x => Math.abs(+x - d) < 1e-6), tue = kt != null ? P.esp.tue[kt] : null;
    if (var_ == null || tue == null) return [null, null, `sin tabla para espárrago ${d}"`];
    const con = norm(it.descripcion).includes("tuerca");
    return [var_ * largo + (con ? 2 * tue : 0), null, `espárrago ${d}" × ${largo.toFixed(2)}"${con ? " + 2 tuercas" : ""} (calculado)`];
  }
  // Peso APROXIMADO por volumen × densidad cuando ninguna tabla lo tiene (herramientas/peso_aproximado.estimar)
  const MAPA_ACC = { "codo 90": "codo_90_radio_largo", "codo radio corto 90": "codo_90_radio_corto", "codo 45": "codo_45", tee: "tee_recta",
    "reduccion concentrica": "reduccion_concentrica_excentrica", "reduccion excentrica": "reduccion_concentrica_excentrica", reduccion: "reduccion_concentrica_excentrica",
    casquete: "casquete", cupla: "cupla", "media cupla": "media_cupla", tapon: "tapon_hexagonal", buje: "buje_hexagonal" };
  function tipoAccesorio(at, fam, dn) {
    const t = at.tipo || "", tipo = fam === "AFO" && t === "codo 90" ? "codo_90" : MAPA_ACC[t] || "";
    const d2 = at.diametro2 ? pulg(at.diametro2) : null;
    return tipo === "tee_recta" && d2 && d2 !== dn ? "tee_reduccion" : tipo;
  }
  const kgmOd = (datos, dn, clase) => { const r = clase && datos.canos.find(r => Math.abs(r.dn - dn) < 1e-6 && (r.sch === clase || r.cl === clase)); return r ? [r.kg, r.od / 1000] : null; };
  const claseNum = c => { const m = String(c).match(/\d+/); return m ? +m[0] : 0; };
  const minPor = (arr, key) => arr.reduce((a, b) => { const ka = key(a), kb = key(b); return (kb[0] < ka[0] || (kb[0] === ka[0] && kb[1] < ka[1])) ? b : a; });
  function scheduleDe(it, at) {
    for (const c of [at.schedule || "", it.plano?.serie_sch || "", ...String(it.especificacion || "").split("·")]) { const s = schDe(String(c).trim()); if (s) return s; }
    return "";
  }
  function estimar(it, at, fam, tipo, datos) {
    const P = datos.pesos, dn = pulg(at.diametro), d = norm(`${it.descripcion} ${it.especificacion || ""}`);
    const bw = fam === "ABW" || (fam === "AFO" && String(at.extremos || "").toUpperCase().includes("BW"));
    const tipoBw = tipo === "codo_90" ? "codo_90_radio_largo" : tipo;
    if (bw && dn && P.aprox[tipoBw] != null) {
      const sch = scheduleDe(it, at) || "STD", k = kgmOd(datos, dn, sch) || (sch === "40" ? kgmOd(datos, dn, "STD") : null);
      if (k) return [k[0] * k[1] * P.aprox[tipoBw], null, `APROXIMADO: ${tipoBw} ${dn}" sch ${sch}`];
    }
    if (fam === "AFO" && dn && tipo && !bw) {
      const ext = String(at.extremos || "").includes("SW") ? "SW" : "NPT", cl = claseNum(at.serie || "3000");
      const cand = P.acc.filter(r => r[0] === tipo && Math.abs(r[1] - dn) < 1e-6 && r[4] === ext && r[5] && r[2] == null);
      if (cand.length) { const r = minPor(cand, r => [Math.abs(claseNum(r[3]) - cl), r[6]]); return [r[5], null, `APROXIMADO: ${tipo} ${dn}" ${ext} con el peso de la clase ${r[3]}`]; }
    }
    if (fam === "VAL" && dn) {
      const t0 = d.includes("esferica") ? "ESFERICA" : d.includes("retencion") ? "RETENCION" : d.includes("globo") ? "GLOBO" : /esclusa|compuerta/.test(d) ? "ESCLUSA" : "";
      if (t0) {
        const cl = claseNum(at.serie || ""), cand = P.valv.filter(r => r[0].startsWith(t0) && Math.abs(r[1] - dn) < 0.01 && !r[5]);
        if (cand.length) { const r = minPor(cand, r => [Math.abs(claseNum(r[2]) - cl), 0]); return [r[4], null, `APROXIMADO: ${r[0].toLowerCase()} ${dn}" con el peso de la serie ${r[2]}`]; }
      }
    }
    if (fam === "JUN" && dn && /junta/.test(d)) {
      const k = kgmOd(datos, dn, "STD") || kgmOd(datos, dn, "40");
      if (k) {
        const m = d.match(/esp\.?\s*(\d+(?:[.,]\d+)?)\s*mm/), e = m ? parseFloat(m[1].replace(",", ".")) / 1000 : 0.0045;
        const rho = /dielectr|aramid|fibra|nbr/.test(d) ? 1800 : 7900, di = k[1], de = k[1] + 0.05;
        return [3.14159265 / 4 * (de ** 2 - di ** 2) * e * rho, null, `APROXIMADO: junta anillo × ${rho} kg/m³`];
      }
    }
    if (/termovaina|vaina|termopozo/.test(d) && /brid/.test(d)) {
      const m = (it.descripcion + " " + (it.especificacion || "")).match(/(\d+(?: \d\/\d)?)"/), sm = d.match(/(150|300|600|900|1500|2500)\s*(?:lb|#)/);
      const dnv = (m ? fracPulg(m[1]) : null) || 1.5, serie = sm ? sm[1] : "300";
      const r = P.bridas.find(r => r[0] === "ciega" && Math.abs(r[1] - dnv) < 1e-6 && r[2] === serie);
      if (r) return [r[3], null, `APROXIMADO: termovaina con el peso de una brida ciega ${dnv}" #${serie}`];
    }
    return [null, null, ""];
  }
  function pesoItem(it, at, fam, datos) {
    const r = pesoTabla(it, at, fam, datos);
    if (r[0] != null) return r;
    const e = estimar(it, at, fam, fam === "ABW" || fam === "AFO" ? tipoAccesorio(at, fam, pulg(at.diametro)) : "", datos);
    return e[0] != null ? e : r;
  }
  function pesoTabla(it, at, fam, datos) {
    const P = datos.pesos, dn = pulg(at.diametro), sch = at.schedule || "";
    if ((fam === "CAN" || fam === "NIP") && dn) {
      const f = datos.canos.find(r => r.dn === dn && (r.sch === sch || r.cl === String(sch).toUpperCase()));
      if (!f) return [null, null, `caño ${dn}" sin schedule reconocido`];
      let kg = f.kg; const m2 = f.m2;
      if (/inox|316|304/.test(norm(at.material || ""))) kg = f.kg * 1.0141;
      if (fam === "NIP" || it.unidad !== "m") {
        const l = norm(it.descripcion + " " + (it.especificacion || "")).match(/(\d[\d.]*)\s?mm/);
        if (!l) return [null, null, "niple sin largo"];
        const L = parseFloat(l[1].replace(/\./g, "")) / 1000;
        return [kg * L, m2 * L, `caño ${dn}" sch ${sch} × ${L} m`];
      }
      return [kg, m2, `caño ${dn}" sch ${sch} por metro`];
    }
    if (fam === "BRI" && dn && at.serie) {
      const tipo = { wn: "WN", so: "SO", ciega: "ciega", sw: "SW", roscada: "roscada", lj: "LJ" }[at.tipo || ""] || "";
      const f = P.bridas.find(r => r[0] === tipo && r[1] === dn && r[2] === at.serie);
      if (f) return [f[3], null, `brida ${tipo} ${dn}" #${at.serie}`];
    }
    if (String(at.tipo || "").includes("olet") || /olet\b/.test(norm(it.descripcion))) return pesoOlet(it, at, P);
    if (fam === "JUN" && ["esparrago", "bulon"].includes(at.tipo)) return pesoEsparrago(it, at, P);
    if ((fam === "ABW" || fam === "AFO") && dn) {
      const t = at.tipo || "";
      const mapa = { "codo 90": fam === "AFO" ? "codo_90" : "codo_90_radio_largo", "codo radio corto 90": "codo_90_radio_corto", "codo 45": "codo_45", tee: "tee_recta",
        "reduccion concentrica": "reduccion_concentrica_excentrica", "reduccion excentrica": "reduccion_concentrica_excentrica", reduccion: "reduccion_concentrica_excentrica",
        casquete: "casquete", cupla: "cupla", "media cupla": "media_cupla", tapon: "tapon_hexagonal", buje: "buje_hexagonal" };
      let tipo = mapa[t] || "";
      const d2 = at.diametro2 ? pulg(at.diametro2) : null;
      if (tipo === "tee_recta" && d2 && d2 !== dn) tipo = "tee_reduccion";
      const [clase, ext] = fam === "ABW" ? [schTabla(sch, dn), "BW"] : [at.serie || "3000", String(at.extremos || "").includes("SW") ? "SW" : "NPT"];
      const cand = P.acc.filter(r => r[0] === tipo && r[1] === dn && r[4] === ext && (r[3] === clase || (/^(tapon|buje)/.test(tipo) && r[3] === "3000/6000")) && (d2 == null || r[2] === d2))
        .sort((a, b) => a[6] - b[6]);
      if (cand.length) return [cand[0][5], null, `${tipo} ${dn}" ${clase} ${ext}`];
      return [null, null, `sin tabla para ${t} ${dn}" ${clase}`];
    }
    if (fam === "VAL") return pesoValvula(it, at, P);
    return [null, null, "sin tabla (instrumento, junta u otro)"];
  }
  const perfil = (datos, desc) => { const m = norm(desc).match(/\b(upn|ipn|heb|hea|ipe|upe)\s*(\d+)/); return m ? datos.pesos.perfiles[m[1] + m[2]] || null : null; };

  function pesos(cot, datos) {
    let kgP = 0, m2C = 0, kgE = 0; const sin = [], faltan = [], aprox = [];
    for (const it of cot.items.filter(i => i.grupo === "material")) {
      if (ESTRUCTURA.test(norm(it.descripcion))) {
        const u = norm(it.unidad);
        if (u === "kg") kgE += it.cantidad;
        else { const pf = perfil(datos, it.descripcion); if (pf && u.startsWith("m")) kgE += pf[0] * it.cantidad; else sin.push(`${it.pos} ${it.descripcion.slice(0, 40)}`); }
        continue;
      }
      if (!it.at) { if (!/completar barra|sobrante|manga|junta|repuesto/.test(norm(it.descripcion))) faltan.push(`${it.pos} ${it.descripcion.slice(0, 40)}`); continue; }
      const [kg, m2, fuente] = pesoItem(it, it.at, it.fam, datos);
      if (kg != null && String(fuente).startsWith("APROXIMADO")) aprox.push(`${it.pos} ${it.descripcion.slice(0, 40)}`);
      if (kg == null) { if (!/junta|termometro|manometro|instrumento|transmisor|bloqueo y purga|repuesto|completar barra/.test(norm(it.descripcion))) sin.push(`${it.pos} ${it.descripcion.slice(0, 40)}`); continue; }
      kgP += kg * it.cantidad; m2C += (m2 || 0) * it.cantidad;
    }
    return { kgP, m2C, kgE, sin, faltan, aprox };
  }

  // m² a pintar (precotizar.superficie_pintura)
  function superficie(filas, m2Canos, datos) {
    let piezas = 0, env = 0, est = 0;
    for (const r of filas) {
      const d = norm(r.descripcion), q = +r.cantidad || 0, u = norm(r.unidad), D = (dnDe(r.diametro) || 0) * 0.0254;
      if (/\bvirola/.test(d) && D && largoM(r.descripcion)) env += Math.PI * D * largoM(r.descripcion) * q;
      else if (/casquete|cabezal/.test(d) && D) env += 1.09 * D * D * q;
      else if (INTERNOS.test(d)) continue;
      else if (perfil(datos, r.descripcion) && u.startsWith("m") && !u.startsWith("m2")) est += perfil(datos, r.descripcion)[1] * q;
      else if (u === "kg" && /perfil|upn|ipn|heb|bastidor|estructura|pata|cuna|soporte|skid|chapa|cancamo|angulo|planchuela/.test(d)) est += q * M2_POR_KG_ESTRUCTURA;
      else if (!u.startsWith("m") && !new RegExp("\\bcano\\b|\\bniple|\\btubo\\b|" + OLETS.source).test(d)) {
        const k = (LARGO_EQ_D.find(([rx]) => rx.test(d)) || [])[1], dn = dnDe(r.diametro);
        if (k && dn) piezas += q * k * odM(dn) * Math.PI * odM(dn);
      }
    }
    return { piezas, env, est, canos: m2Canos };
  }

  // Ficha completa (ficha_rubros.armar, sin referencias ni transporte: los agrega Rubros.ficha)
  function calcular(cot, datos) {
    const filas = filasDe(cot);
    const sol = filas.length ? soldaduras(filas, datos) : { juntas_bw: 0, pulg_eq: 0, placas: [0, 0], juntas_sw_olet: 0, avisos: [] };
    const p = pesos(cot, datos), sup = filas.length ? superficie(filas, p.m2C, datos) : { piezas: 0, env: 0, est: 0 };
    const m2Est = sup.est || p.kgE * M2_POR_KG_ESTRUCTURA, m2Pip = p.m2C + sup.piezas + sup.env;
    const rx = cot.parametros.rx_pct || 0, [ch, gr] = sol.placas.map(x => Math.ceil(x * rx / 100));
    const campo = filas.reduce((a, f) => a + (+(f.extremos_campo || 0)) * (+f.cantidad || 0), 0);
    const bw = filas.filter(f => String(f.extremos).toUpperCase().includes("BW"));
    const dns = [...new Set(bw.map(f => dnDe(f.diametro)).filter(Boolean))].sort((a, b) => b - a);
    const mats = [...new Set(bw.map(f => f.material).filter(Boolean))].sort();
    let esp = 0;
    for (const f of bw) { const dn = dnDe(f.diametro), s = schDe(f.serie_sch); if (!dn || !s) continue; for (const r of datos.soldadura) if (Math.abs(r.dn - dn) < 1e-6 && (r.sch === s || r.cl === s) && r.e) esp = Math.max(esp, r.e); }
    const r2 = x => Math.round(x * 100) / 100, r1 = x => Math.round(x * 10) / 10;
    const avisos = [...sol.avisos];
    if (p.faltan.length) avisos.push(`Sin familia ni atributos (no suman kg): ${p.faltan.join("; ")}. Recalcular los busca en el catálogo`);
    if (!filas.length) avisos.push("Ningún renglón tiene los datos del plano (Ø, serie y extremos): no se pueden contar soldaduras");
    const espTxt = esp ? esp.toLocaleString("es-AR", { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : "";
    const out = {
      generada: new Date().toISOString().slice(0, 10), origen: "pagina",
      mo_piping: { juntas_bw: sol.juntas_bw, pulg_eq: sol.pulg_eq, juntas_sw_olet: sol.juntas_sw_olet, extremos_campo: campo, kg_piping: r1(p.kgP),
        bridas: cot.items.filter(i => i.grupo === "material" && /^brida/.test(norm(i.descripcion))).reduce((a, i) => a + i.cantidad, 0), diametros: dns, sin_peso: p.sin, aproximados: p.aprox, avisos },
      mo_estructura: { kg: r1(p.kgE), m2: r2(m2Est) },
      pintura: { m2_canos: r2(p.m2C), m2_piping: r2(m2Pip), m2_estructura: r2(m2Est), m2_total: r2(m2Pip + m2Est), esquema: cot.pintura?.esquema || "" },
      end: { juntas_bw: sol.juntas_bw, rx_pct: rx, placas_chicas: ch, placas_grandes: gr, juntas_lp: sol.juntas_sw_olet, materiales: mats, espesor_max_mm: esp,
        procedimientos: [esp ? `WPS/PQR de soldadura a tope para ${mats.join(", ") || "el material del plano"} hasta ${espTxt} mm de espesor` : "WPS/PQR de soldadura",
          "Calificación de soldadores (WPQ) para esos WPS", "Procedimiento de RX y de LP (escrito, nivel 3 ISO 9712)",
          "Confirmar con el pliego: si exige procedimientos nuevos o alcanzan los vigentes de ITT"] },
    };
    const lista = procedimientos(filas, esp, sol.juntas_bw, sol.juntas_sw_olet, rx, m2Pip + m2Est);
    out.procedimientos = { lista, cantidad: lista.reduce((a, p) => a + p.cantidad, 0) };
    out.ph = { litros: litros(cot, datos) };
    out.horas = {};
    return out;
  }

  // Procedimientos que lleva el equipo (ficha_rubros.procedimientos)
  function procedimientos(filas, esp, bw, sw, rx, m2) {
    const grupos = [...new Set(filas.filter(f => f.material && /BW|SW/.test(String(f.extremos || "").toUpperCase()))
      .map(f => /304|316|inox|cf8m/.test(norm(f.material)) ? "inoxidable" : "acero al carbono"))].sort();
    const espTxt = esp ? `hasta ${esp.toLocaleString("es-AR", { minimumFractionDigits: 2, maximumFractionDigits: 2 })} mm de espesor` : "";
    const l = [];
    for (const g of grupos) {
      if (bw) l.push({ codigo: "WPS-BW", nombre: `WPS/PQR de soldadura a tope, ${g}`, alcance: espTxt, cantidad: 1, tipo: "soldadura" });
      if (sw) l.push({ codigo: "WPS-SW", nombre: `WPS/PQR de soldadura socket y filete, ${g}`, alcance: "", cantidad: 1, tipo: "soldadura" });
    }
    if (l.length) l.push({ codigo: "WPQ", nombre: "Calificación de soldadores (WPQ)", alcance: "una por WPS y soldador asignado", cantidad: l.length, tipo: "soldadura" });
    if (rx && bw) l.push({ codigo: "END-RX", nombre: "Procedimiento de radiografía (nivel 3, ISO 9712)", alcance: "", cantidad: 1, tipo: "end" });
    if (sw) l.push({ codigo: "END-LP", nombre: "Procedimiento de líquidos penetrantes (nivel 3, ISO 9712)", alcance: "", cantidad: 1, tipo: "end" });
    if (bw || sw) l.push({ codigo: "PH", nombre: "Procedimiento de prueba hidráulica", alcance: "", cantidad: 1, tipo: "calidad" });
    if (m2) l.push({ codigo: "PIN", nombre: "Procedimiento de granallado y pintura", alcance: "esquema del pliego", cantidad: 1, tipo: "calidad" });
    return l;
  }
  // Volumen interior de los caños, en litros por equipo (ficha_rubros.litros)
  function litros(cot, datos) {
    let t = 0;
    for (const it of cot.items.filter(i => i.grupo === "material" && norm(i.unidad) === "m" && i.fam === "CAN" && i.at)) {
      const dn = dnDe(it.at.diametro || ""), sch = it.at.schedule || "";
      const r = dn && sch && datos.canos.find(r => Math.abs(r.dn - dn) < 1e-6 && (r.sch === sch || r.cl === String(sch).toUpperCase()));
      if (r) t += r.l * it.cantidad;
    }
    return Math.round(t * 10) / 10;
  }

  // Completa familia y atributos de los renglones que no los tienen, con el código de catálogo de su fuente
  function completarAtributos(cot, datos) {
    let n = 0;
    for (const it of cot.items.filter(i => i.grupo === "material" && !i.at)) {
      const cod = (String(it.fuentes?.[0]?.proveedor || "").match(/\b[A-Z]{3}-\d{5}\b/) || [])[0];
      const r = cod && datos.materiales.find(m => m.c === cod);
      if (r) { it.fam = r.f; it.at = { ...r.a }; n++; }
    }
    return n;
  }

  return { calcular, completarAtributos, soldaduras, pesoItem, filasDe, norm, dnDe, schDe };
})();
if (typeof module !== "undefined") module.exports = Ficha;
