// Búsqueda en los catálogos y controles de una cotización. Misma lógica que herramientas/buscar_material.py
// (igual / similar con diferencias) y que herramientas/verificar_computo.py (avisos), pero con filtros elegidos en pantalla.
const Busqueda = (() => {
  const CON_TIPO = ["VAL", "AFO", "ABW", "BRI", "JUN", "INS"];
  const TIPO_FUENTE = { "lista": "lista", "compra": "stock", "stock (precio maestro)": "stock", "cotización": "cot", "planilla interna": "ant", "estimado (cepo)": "est", "estimado (fecha supuesta)": "est" };
  const FRAC = { "½": " 1/2", "¼": " 1/4", "¾": " 3/4", "⅛": " 1/8", "°": " grados ", "º": " grados ", "ø": " diam ", "Ø": " diam " };

  function norm(t) {
    let s = String(t ?? "");
    for (const [a, b] of Object.entries(FRAC)) s = s.split(a).join(b);
    return s.normalize("NFKD").replace(/[\u0300-\u036f]/g, "").toLowerCase().replace(/\s+/g, " ").trim();
  }

  // Palabras de búsqueda: un número se busca como número entero ("4" no encuentra "3/4" ni "1/4"; "150" no encuentra "1500")
  function coincide(texto) {
    const tokens = norm(texto).split(" ").filter(Boolean).map(t => /^\d+([.,]\d+)?$/.test(t)
      ? new RegExp(`(?<![\\d/.,])${t.replace(/[.,]/, "[.,]")}(?![\\d/.,])`) : t);
    return tokens.length ? s => tokens.every(t => typeof t === "string" ? s.includes(t) : t.test(s)) : null;
  }

  function campos(datos, fam) {
    return (datos.familias[fam].clave.length ? datos.familias[fam].clave : ["tipo"]).filter(c => c !== "marca" && c !== "modelo");
  }

  function opcionales(fam, f) {
    const o = new Set(["diametro2", "trim", "schedule", "cara", "medida", "extremos"]);
    if (fam === "CAN") { o.add("revestimiento"); if (f.schedule) o.add("espesor_mm"); else if (f.espesor_mm) o.add("schedule"); }
    if (fam === "JUN") {
      if (["esparrago", "bulon", "tuerca", "arandela"].includes(f.tipo)) o.add("serie"); else o.add("material");
      if (["esparrago", "bulon"].includes(f.tipo)) o.delete("medida");
    }
    if (fam === "VAL" && !String(f.tipo || "").startsWith("esferica")) o.add("paso");  // el paso solo distingue esféricas
    return o;
  }

  // Valores existentes de un atributo dentro de la familia (para los desplegables), filtrados por lo ya elegido
  function valores(datos, fam, campo, f) {
    const cuenta = new Map();
    for (const r of datos.materiales) {
      if (r.f !== fam) continue;
      if (f.tipo && campo !== "tipo" && r.a.tipo !== f.tipo) continue;
      const v = r.a[campo];
      if (v) cuenta.set(v, (cuenta.get(v) || 0) + 1);
    }
    return [...cuenta.entries()].sort((a, b) => {
      const na = parseFloat(a[0]), nb = parseFloat(b[0]);
      return (!isNaN(na) && !isNaN(nb)) ? na - nb : String(a[0]).localeCompare(String(b[0]));
    });
  }

  // ------------------------------------------------------------------ compatibilidad (espejo de herramientas/compatibilidad.py)
  // igual que indice_proyectos.norm: las fracciones antes de NFKD ("½" no queda "12")
  const FRACCIONES = { "½": " 1/2", "¼": " 1/4", "¾": " 3/4", "⅛": " 1/8", "⅜": " 3/8", "⅝": " 5/8", "⅞": " 7/8", "\u2044": "/", "ø": " diam ", "Ø": " diam ", "⌀": " diam ", "°": " grados ", "º": " grados " };
  const normP = t => Object.entries(FRACCIONES).reduce((s, [a, b]) => s.split(a).join(b), String(t ?? "")).normalize("NFKD").replace(/[^\x00-\x7f]/g, "").toLowerCase().replace(/\s+/g, " ");
  const RX = new WeakMap();
  const mats = C => { if (!RX.has(C)) RX.set(C, C.materiales.map(m => ({ ...m, rx: new RegExp(m.patron) }))); return RX.get(C); };
  // igual que compatibilidad.prep: sin lo negado ("NO AISI 316"), "GR°B" → "gr b", medidas "5/8 x 60" → "5/8 por 60"
  const prep = (C, t) => normP(t).replace(new RegExp(C.negacion, "g"), " ").replace(new RegExp(C.grados, "g"), "$1 ")
    .replace(new RegExp(new RegExp(C.api5l).test(normP(t)) ? C.medida_x_api : C.medida_x, "g"), "$1 por ").replace(new RegExp(C.prep, "g"), "a$1");
  function clases(C, texto, preparado = false) {
    const t = preparado ? texto : prep(C, texto), hits = [];
    for (const m of mats(C)) {
      const x = t.match(m.rx); if (!x) continue;
      const a = x.index, b = x.index + x[0].length;
      if (!hits.some(h => h[1] <= a && b <= h[2])) hits.push([m, a, b]);
    }
    const out = new Map();
    for (const [m] of hits) if (!out.has(m.clase)) out.set(m.clase, m.grupo_b16_5);
    if (out.size > 1) for (const g of Object.keys(C.genericos)) out.delete(g);
    return out;
  }
  const grado = t => (normP(t).match(/\b(?:x|wphy|f)[- ]?(\d{2})\b/) || [])[1] || "";
  const limpio = x => normP(x).replace(/[^a-z0-9]/g, "");
  const esInox = c => c.startsWith("inox") || c === "duplex" || c === "superduplex";
  function reemplaza(C, ca, ga, cb, gb, pedido, cand) {
    if (!(cb === ca || (C.reemplaza[ca] || []).includes(cb) || (C.genericos[ca] || []).includes(cb))) return false;
    if (ga && gb && !(C.grupos[ga] || [ga]).includes(gb)) return false;
    if (cb === ca && ca === "carbono_alta_resistencia" && grado(pedido) && grado(cand) && grado(pedido) !== grado(cand)) return false;
    return true;
  }
  // válvulas: clases del cuerpo (compatibilidad.cuerpo); null si nombra carbono e inoxidable sin decir cuál es el cuerpo
  function cuerpo(C, texto) {
    const sinInt = prep(C, texto).replace(new RegExp(C.internos, "g"), " ");
    let expl = (sinInt.match(new RegExp(C.cuerpo, "g")) || []).join(" ");
    if (!clases(C, expl, true).size) expl = "";  // "cuerpo bipartido": no dice el material
    const c = new Map([...clases(C, expl || sinInt, true)].filter(([k]) => !C.no_metal.includes(k) && !/^(bulon|tuerca)/.test(k)));
    if ([...c.keys()].some(esInox) && [...c.keys()].some(k => !esInox(k))) return null;
    return c;
  }
  function reglaCuerpo(C, pedido, cand) {
    const pb = cuerpo(C, pedido), cb = cuerpo(C, cand);
    if (pb && !pb.size) return [...clases(C, pedido).keys()].some(k => !C.no_metal.includes(k) && !/^(bulon|tuerca)/.test(k))
      ? "el pedido no dice el material del cuerpo (solo el de los internos): no se puede comparar" : "";
    if (!cb || !cb.size) return `no se sabe el material del cuerpo del candidato (${String(cand).slice(0, 40)}): no se puede comparar`;
    if (!pb) {
      const a = clases(C, pedido);
      for (const [k, g] of cb) if (![...a].some(([ca, ga]) => reemplaza(C, ca, ga, k, g, pedido, cand))) return `cuerpo ${k} del candidato: el pedido no lo nombra`;
      return "";
    }
    for (const [ca, ga] of pb) if (![...cb].some(([k, g]) => reemplaza(C, ca, ga, k, g, pedido, cand))) return `cuerpo del candidato no reemplaza al cuerpo pedido (${ca})`;
    return "";
  }
  function reglaMaterial(C, fam, pedido, cand, descCand) {
    if (!String(pedido || "").trim()) return "";
    const gv = new RegExp(C.galv);
    if (gv.test(prep(C, pedido)) !== gv.test(prep(C, `${cand || ""} ${descCand || ""}`))) return "galvanizado y negro no se reemplazan";
    const a = clases(C, pedido);
    let b = String(cand || "").trim() ? clases(C, cand) : new Map();
    if (!b.size) b = clases(C, descCand || "");
    if (!a.size) return limpio(pedido) && limpio(pedido) === limpio(cand) ? "" : `material ${pedido} sin regla: solo vale el mismo material`;
    if (!b.size) return `el candidato no dice el material (el pedido es ${pedido}): no se puede comparar`;
    for (const [ca, ga] of a) {
      const tipo = /^(bulon|tuerca)/.test(ca) ? ca.split("_")[0] : "";
      if (tipo && ![...b.keys()].some(c => c.startsWith(tipo))) {
        if ([...b.keys()].some(c => /^(bulon|tuerca)/.test(c))) continue;
        return `el candidato no dice el grado del ${tipo.replace("bulon", "bulón")} (el pedido es ${String(pedido).slice(0, 40)}): no se puede comparar`;
      }
      if (![...b].some(([cb, gb]) => reemplaza(C, ca, ga, cb, gb, pedido, cand || descCand))) return `material ${cand || String(descCand).slice(0, 30)} no reemplaza a ${pedido}`;
    }
    if (fam === "VAL") return reglaCuerpo(C, pedido, clases(C, cand || "").size ? cand : descCand);
    return "";
  }
  const CARAS = ["rf", "ff", "rtj"], ROSCAS = ["npt", "bspt", "bspp"];
  function conexiones(...ts) {
    const out = new Set();
    for (let t of ts) {
      t = normP(t).replace(/\br\.?\s?f\.?(?=\s|\/|$)|\brfwn\b/g, " rf ").replace(/\br\.?\s?j\.?(?=\s|\/|$)|\brj\b/g, " rtj ")
        .replace(/\b[fm]npt\b|\bnptf\b|\bnpt-?[hm]\b/g, " npt ").replace(/\bsocket ?weld\b|\bsocket\b/g, " sw ")
        .replace(/\bbspp\b|\bbsp\b(?!t)/g, " bspp ").replace(/\bbe\b|\bbisel/g, " bw ");
      for (const k of [...CARAS, ...ROSCAS, "sw", "bw"]) if (new RegExp(`\\b${k}\\b`).test(t)) out.add(k);
      if (/\bbridad|\bbrida\b/.test(t) && !CARAS.some(k => out.has(k))) out.add("brida");
      if (/\brosca|\broscad/.test(t) && !ROSCAS.some(k => out.has(k))) out.add("rosca");
    }
    return out;
  }
  const tipos = c => new Set([...c].map(x => CARAS.includes(x) || x === "brida" ? "brida" : ROSCAS.includes(x) || x === "rosca" ? "rosca" : x));
  function reglaConexion(a, b) {
    if (!a.size || !b.size) return "";
    const inter = (s, ks) => new Set([...s].filter(x => ks.includes(x))), igual = (x, y) => x.size === y.size && [...x].every(v => y.has(v));
    const txt = `extremos o cara distintos (${[...b].sort().join("/").toUpperCase()} por ${[...a].sort().join("/").toUpperCase()})`;
    const ta = tipos(a), tb = tipos(b);
    if (![...ta].some(x => tb.has(x))) return txt;
    const ca = inter(a, CARAS), cb = inter(b, CARAS);
    if (ca.size && cb.size && !igual(ca, cb)) return txt;
    const ra = inter(a, ROSCAS), rb = inter(b, ROSCAS);
    if (ra.size && rb.size && !igual(ra, rb)) return txt;
    return "";
  }
  function schCanonico(sch, dn) {
    let s = String(sch || "").toUpperCase().replace(/[^A-Z0-9]/g, "").replace(/^(SCH|S)(?=\d)/, "");
    s = { "40S": "STD", "80S": "XS" }[s] || s;
    if (dn != null) { if (s === "STD" && dn <= 10) return "40"; if (s === "XS" && dn <= 8) return "80"; }
    return s;
  }
  function dnDe(C, v) {
    const t = normP(v), m = t.match(/\bdn ?(\d{2,3})\b|(\d{2,3}) ?mm\b/);
    if (m) return C.dn_nps[String(+(m[1] || m[2]))] ?? null;
    const n = t.match(/^\s*(\d+(?:[.,]\d+)?)/); return n ? parseFloat(n[1].replace(",", ".")) : null;
  }
  // el atributo "material" viene simplificado (pierde el grado): se usa el texto si nombra un material (compatibilidad.material_texto)
  const materialTexto = (C, atrib, texto) => clases(C, texto).size ? texto : (atrib || "");
  // revestimientos y schedule de cada extremo (compatibilidad.regla_revestimiento / regla_sch_doble)
  function reglaRevestimiento(C, tp, tc) {
    const a = Object.keys(C.revest).filter(k => new RegExp(C.revest[k]).test(tp));
    if (!a.length) return "";
    const b = Object.keys(C.revest).filter(k => new RegExp(C.revest[k]).test(tc));
    for (const k of a) if (!b.some(x => C.revest_ok[k].includes(x))) return `revestimiento ${b.sort().join("/") || "sin dato"} por ${k} (no lo reemplaza)`;
    return "";
  }
  function reglaSchDoble(C, tp, tc, diametro) {
    const mp = tp.match(new RegExp(C.sch_doble)); if (!mp) return "";
    const mc = tc.match(new RegExp(C.sch_doble));
    if (!mc) return `el pedido es schedule ${mp[1]} × ${mp[2]} y el candidato no dice el de cada extremo`;
    const ds = normP(diametro).split(/\s*x\s*/).map(x => dnDe(C, x)).filter(x => x).concat([null, null]);
    for (const [i, dn] of [[1, ds[0]], [2, ds[1]]]) if (schCanonico(mp[i], dn) !== schCanonico(mc[i], dn)) return `schedule ${mc[1]} × ${mc[2]} por ${mp[1]} × ${mp[2]} (otro espesor en un extremo)`;
    return "";
  }
  function incompatible(C, fam, ped, cand, textoPed, textoCand) {
    const m = reglaMaterial(C, fam, materialTexto(C, ped.material, textoPed || ""), materialTexto(C, cand.material, textoCand || ""), textoCand || ""); if (m) return m;
    const c = reglaConexion(conexiones(ped.extremos || "", ped.cara || ""), conexiones(cand.extremos || "", cand.cara || "")); if (c) return c;
    if (C.familias_sch.includes(fam) && ped.schedule && cand.schedule) {
      const dn = dnDe(C, ped.diametro || "");
      if (schCanonico(ped.schedule, dn) !== schCanonico(cand.schedule, dn)) return `schedule ${cand.schedule} por ${ped.schedule} (otro espesor)`;
    }
    const tp = normP(textoPed), tc = normP(textoCand);
    const r = reglaRevestimiento(C, prep(C, textoPed), prep(C, textoCand)); if (r) return r;
    if (C.familias_sch.includes(fam)) { const r2 = reglaSchDoble(C, tp, tc, ped.diametro || ""); if (r2) return r2; }
    if (new RegExp(C.nace_estricto).test(tp) && !new RegExp(C.nace_estricto).test(tc)) return "el pedido es MR0175 / ISO 15156 y el candidato no lo dice";
    if (new RegExp(C.nace_pedido).test(tp) && !new RegExp(C.nace_cand).test(tc)) return "el pedido es para servicio ácido (NACE) y el candidato no lo dice";
    return "";
  }

  function materiales(datos, f, limite = 60) {
    const fam = f.fam;
    const ok = coincide(f.texto);
    const cs = fam ? campos(datos, fam) : [];
    const op = fam ? opcionales(fam, f) : new Set();
    const elegidos = cs.filter(c => f[c]);
    const clasifica = fam && (!CON_TIPO.includes(fam) || f.tipo) && elegidos.length > 0;
    const res = [];
    for (const r of datos.materiales) {
      if (fam && r.f !== fam) continue;
      if (ok && !ok(norm(r.d + " " + Object.values(r.a).join(" ") + " " + r.pr))) continue;
      if (f.marca && norm(r.a.marca) !== norm(f.marca) && f.soloMarca) continue;
      if (!clasifica) {
        if (elegidos.some(c => r.a[c] && norm(r.a[c]) !== norm(f[c]))) continue;
        res.push({ r, estado: "lista", difs: [], orden: [0, 0, 0, 0, r.p ? 1 : 0, 0, r.fe || ""] });
        continue;
      }
      if (f.tipo && r.a.tipo && norm(f.tipo) !== norm(r.a.tipo)) continue;
      if (CON_TIPO.includes(fam) && !!f.tipo !== !!r.a.tipo) continue;
      let coinc = 0; const difs = [];
      for (const c of cs) {
        if (fam === "CAN" && c === "espesor_mm" && f.schedule && r.a.schedule) continue;
        const a = norm(f[c]), b = norm(r.a[c]);
        if (a === b) coinc += a ? 1 : 0;
        else if (a && b) difs.push(`${c}: ${r.a[c]} (pedido ${f[c]})`);
        else if (a) difs.push(`${c}: sin dato (pedido ${f[c]})`);
        else difs.push(`${c}: ${r.a[c]} (no pedido)`);
      }
      if (coinc === 0) continue;
      // similar solo de la misma serie y la misma norma, igual que buscar_material.py (Matías, 29-10-2026)
      if (cs.includes("serie") && !op.has("serie") && f.serie && norm(r.a.serie) !== norm(f.serie)) continue;
      if (cs.includes("norma") && f.norma && r.a.norma && norm(r.a.norma) !== norm(f.norma)) continue;
      // compatibilidad que pide la norma (material, cara, roscas, schedule, NACE), igual que compatibilidad.py (Matías, 30-10-2026)
      if (datos.compat && incompatible(datos.compat, fam, f, r.a, f.texto || "", r.d || "")) continue;
      const oblig = cs.filter(c => !op.has(c));
      const igual = !difs.length && oblig.every(c => f[c]);
      const misma = !!f.marca && norm(r.a.marca) === norm(f.marca);
      // la marca no le gana al tamaño (Ø, serie, schedule, medida), igual que buscar_material.py (CTRL-TS01)
      const crit = difs.filter(d => ["diametro", "diametro2", "serie", "schedule", "medida", "espesor_mm"].includes(d.split(":")[0]) && !d.includes("(no pedido)")).length;
      res.push({ r, estado: igual ? "igual" : "similar", difs, misma, orden: [igual ? 1 : 0, -crit, misma ? 1 : 0, -difs.length, r.p ? 1 : 0, coinc, r.fe || ""] });
    }
    res.sort((x, y) => { for (let i = 0; i < 7; i++) { if (x.orden[i] < y.orden[i]) return 1; if (x.orden[i] > y.orden[i]) return -1; } return 0; });
    const faltan = fam ? cs.filter(c => !f[c] && !op.has(c)) : [];
    return { res: res.slice(0, limite), total: res.length, clasifica, faltan };
  }

  function servicios(datos, f, limite = 60) {
    const ok = coincide(f.texto);
    const res = datos.servicios.filter(r => (!f.hoja || r.h === f.hoja) && (!ok || ok(norm(r.s + " " + r.d + " " + r.pr + " " + r.eq + " " + r.h))));
    res.sort((a, b) => (b.p ? 1 : 0) - (a.p ? 1 : 0) || (b.t ? 1 : 0) - (a.t ? 1 : 0) || String(b.fe).localeCompare(String(a.fe)));
    return { res: res.slice(0, limite), total: res.length };
  }

  // Ítem de cotizacion.json a partir de un renglón del catálogo de materiales
  function itemDeMaterial(r, resultado, cantidad, id) {
    const coincide = resultado.estado === "igual" ? "igual" : "similar";
    const f = { tipo: TIPO_FUENTE[r.tp] || "ant", precio: r.p || 0, proveedor: `${(r.pr || "").slice(0, 70)} · ${r.c}`, codigo: r.c, origen: r.o || "", fecha: r.fe || hoy(), coincide };
    if (coincide === "similar") f.diferencia = resultado.difs.join("; ") || "Pieza similar: completar en qué difiere";
    if (!r.p) { f.tipo = "est"; f.proveedor = "SIN PRECIO CONFIABLE: pedir cotización · " + r.c; f.coincide = "sin_ref"; f.diferencia = "Sin precio confiable en el catálogo"; }
    const it = { id, pos: "", grupo: "material", descripcion: r.d.slice(0, 120), especificacion: describirAtributos(r.a), cantidad, unidad: r.u || "un", fuentes: [f] };
    if (r.f === "VAL" && /taval/i.test(`${r.a?.marca || ""} ${r.pr || ""}`)) it.taval = true;  // va con el factor de válvulas Taval
    it.fam = r.f; it.at = { ...(r.a || {}) };  // familia y atributos del catálogo: los usa la ficha (kg y soldaduras)
    return it;
  }

  function itemDeServicio(r, cantidad, id) {
    const unit = !!r.t;
    const grupo = ["MO propia", "Fabricación y armado (terceros)", "Soldadura y piping"].includes(r.h) ? "mo" : "servicio";
    return {
      id, pos: grupo === "mo" ? "MO" : "SRV", grupo, descripcion: r.s.slice(0, 120), especificacion: [r.inc && "Incluye: " + r.inc, r.ninc && "No incluye: " + r.ninc].filter(Boolean).join(" · "),
      cantidad, unidad: unit ? r.ut.replace("USD/", "") : "gl",
      fuentes: [{ tipo: "ant", precio: unit ? r.t : r.p, proveedor: `${(r.pr || "").slice(0, 70)} · ${r.c}`, origen: r.o || "", fecha: r.fe || hoy(),
                  coincide: unit ? "igual" : "similar", ...(unit ? {} : { diferencia: `Global de otro trabajo (${r.eq || "sin dato"}): verificar que el alcance sea el mismo` }) }]
    };
  }

  function describirAtributos(a) {
    return ["tipo", "diametro", "diametro2", "serie", "schedule", "material", "trim", "extremos", "marca", "modelo"].filter(k => a[k])
      .map(k => (k === "serie" ? "#" : k === "schedule" ? "sch " : "") + a[k]).join(" · ");
  }

  function hoy() { return new Date().toISOString().slice(0, 10); }

  // Soldaduras: juntas por diámetro y espesor → pulgadas equivalentes (factores_soldadura.csv y factores_accesorios.csv)
  const n2 = v => typeof Documentos !== "undefined" ? Documentos.num(v) : v.toFixed(2); // en las pruebas con node no hay Documentos
  function soldadura(datos, filas) {
    let pulg = 0, pch = 0, pgr = 0; const detalle = [];
    for (const f of filas) {
      const dn = parseFloat(f.dn); if (!dn) continue;
      const t = datos.soldadura.find(r => Math.abs(r.dn - dn) < 1e-6 && (r.sch === f.sch || r.cl === f.sch)) || { fe: 1, pch: 0, pgr: 0 };
      const bw = +f.bw || 0, sw = +f.sw || 0, ol = +f.olet || 0;
      const fo = f.tipoOlet === "weldolet" ? 2.5 : 1.75;
      const v = (bw + sw) * dn * t.fe + ol * dn * fo;
      pulg += v; pch += bw * (t.pch || 0); pgr += bw * (t.pgr || 0);
      detalle.push(`${bw + sw} junta(s) ${dn}" sch ${f.sch || "40"} × ${n2(t.fe)}` + (ol ? ` + ${ol} olet/cupla × ${dn}" × ${n2(fo)}` : "") + ` = ${n2(v)}`);
    }
    return { pulg: Motor.redondear(pulg, 3), placas_chicas: pch, placas_grandes: pgr, detalle };
  }

  function tarifa(datos, rubro, texto, tipos = ["costo_propio"]) {
    return datos.tarifas.find(r => r.rubro === rubro && norm(r.concepto).includes(texto) && tipos.includes(r.tipo));
  }

  // Avisos de una cotización (verificar_computo + control de carga)
  // Código de catálogo de una fuente (auditoría 29-10-2026): el campo codigo, o el que quedó escrito en el proveedor
  // ("Renard · CAN-01435") en las cotizaciones anteriores. Con él se avisa si el catálogo cambió después de cargarlo.
  const codigoDe = s => s.codigo || (String(s.proveedor || "").match(/\b[A-Z]{3}-\d{5}\b/) || [])[0] || "";
  let CAT = null;
  function catalogo(datos) { CAT = new Map([...(datos.materiales || []), ...(datos.servicios || [])].map(m => [m.c, m])); }
  function avisos(cfg) {
    const out = []; const h = hoy();
    for (const it of cfg.items) {
      const s = it.fuentes[0], d = it.descripcion, tag = `${it.pos || it.id} ${d.length > 44 ? d.slice(0, 44).replace(/\s+\S*$/, "") + "…" : d}`, n0 = out.length; // sin cortar palabras
      if (!s.precio) out.push({ nivel: "bad", txt: `${tag}: SIN PRECIO, pedir cotización antes de presentar` });
      if (!s.proveedor || !s.fecha) out.push({ nivel: "bad", txt: `${tag}: precio sin fuente o sin fecha` });
      if (s.fecha && (!/^\d{4}-\d{2}-\d{2}$/.test(s.fecha) || s.fecha > h)) out.push({ nivel: "bad", txt: `${tag}: fecha inválida o futura (${s.fecha.split("-").reverse().join("-")})` });
      if (s.coincide === "similar" && !s.diferencia) out.push({ nivel: "bad", txt: `${tag}: similar sin decir en qué difiere` });
      if (s.coincide === "similar") out.push({ nivel: "warn", txt: `${tag}: pieza SIMILAR (${(s.diferencia || "").slice(0, 80)})` });
      if (s.tipo === "est" && s.precio) out.push({ nivel: "warn", txt: `${tag}: precio ESTIMADO (USD ${n2(it.cantidad * s.precio)})` });
      if (/con iva|iva incluido|c\/ ?iva/.test(norm(s.proveedor + " " + (s.diferencia || "")))) out.push({ nivel: "warn", txt: `${tag}: la fuente dice "con IVA": cargar el precio sin IVA` });
      if (s.fecha && s.fecha < "2025-04-14" && !/tc |tipo de cambio/.test(norm(s.proveedor))) out.push({ nivel: "warn", txt: `${tag}: precio del período con cepo (${s.fecha.split("-").reverse().join("-")}) sin tipo de cambio explícito` });
      if (s.fecha && /^\d{4}-\d{2}/.test(s.fecha)) {
        const [y, m] = s.fecha.split("-").map(Number), [Y, M] = h.split("-").map(Number);
        const meses = (Y - y) * 12 + M - m;
        if (meses > 6 && s.tipo !== "est") out.push({ nivel: "warn", txt: `${tag}: precio de hace ${meses} meses (${s.fecha.split("-").reverse().join("-")}), actualizar` });
      }
      const cc = CAT && !it.global && codigoDe(s), m = cc && CAT.get(cc);
      if (m && m.p && s.precio && Math.abs(m.p - s.precio) >= 0.01 && (m.fe || "") > (s.fecha || ""))
        out.push({ nivel: "warn", txt: `${tag}: el catálogo (${cc}) tiene un precio más nuevo: USD ${n2(m.p)} del ${String(m.fe).split("-").reverse().join("-")} (acá USD ${n2(s.precio)}); actualizalo si corresponde` });
      for (const x of out.slice(n0)) { x.id = it.id; x.corto = x.txt.slice(tag.length + 2); }
    }
    const pz = plazoBloquea(cfg);
    if (pz) out.push({ nivel: "bad", txt: pz });
    return out;
  }
  // Plazo calculado con las tareas de la pestaña Plazo: acopio (material más largo) + taller, sin superponer.
  function plazoCalculado(cfg) {
    const t = cfg.plazo?.tareas || [], mat = t.filter(x => x[3] !== "tal"), tal = t.filter(x => x[3] === "tal");
    const acopio = Math.max(0, ...mat.map(x => +x[2] || 0)), taller = tal.reduce((a, x) => a + ((+x[2] || 0) - (+x[1] || 0)), 0);
    return { acopio, taller, calc: acopio + taller };
  }
  // Un plazo ofrecido menor que el calculado no sale en la oferta sin una justificación escrita (auditoría 29-10-2026).
  function plazoBloquea(cfg) {
    const d = +cfg.plazo?.dias || 0, { calc } = plazoCalculado(cfg);
    if (!d || !calc || d >= calc || String(cfg.plazo?.justificacion || "").trim()) return "";
    return `Plazo ofrecido ${d} días, menor que el calculado (${calc} días): corregilo o escribí la justificación en Plazo. Hasta entonces no se generan las ofertas.`;
  }
  return { norm, coincide, incompatible, campos, opcionales, valores, materiales, servicios, itemDeMaterial, itemDeServicio, soldadura, tarifa, avisos, catalogo, codigoDe, plazoCalculado, plazoBloquea, TIPO_FUENTE, CON_TIPO };
})();
if (typeof module !== "undefined") module.exports = Busqueda;
