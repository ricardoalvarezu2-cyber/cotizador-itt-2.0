// Búsqueda en los catálogos y controles de una cotización. Misma lógica que herramientas/buscar_material.py
// (igual / similar con diferencias) y que herramientas/verificar_computo.py (avisos), pero con filtros elegidos en pantalla.
const Busqueda = (() => {
  const CON_TIPO = ["VAL", "AFO", "ABW", "BRI", "JUN", "INS"];
  const TIPO_FUENTE = { "lista": "lista", "compra": "stock", "stock (precio maestro)": "stock", "cotización": "cot", "planilla interna": "ant", "estimado (cepo)": "est" };
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
        res.push({ r, estado: "lista", difs: [], orden: [0, 0, 0, r.p ? 1 : 0, 0, r.fe || ""] });
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
      const oblig = cs.filter(c => !op.has(c));
      const igual = !difs.length && oblig.every(c => f[c]);
      const misma = !!f.marca && norm(r.a.marca) === norm(f.marca);
      res.push({ r, estado: igual ? "igual" : "similar", difs, misma, orden: [igual ? 1 : 0, misma ? 1 : 0, -difs.length, r.p ? 1 : 0, coinc, r.fe || ""] });
    }
    res.sort((x, y) => { for (let i = 0; i < 6; i++) { if (x.orden[i] < y.orden[i]) return 1; if (x.orden[i] > y.orden[i]) return -1; } return 0; });
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
    const f = { tipo: TIPO_FUENTE[r.tp] || "ant", precio: r.p || 0, proveedor: `${(r.pr || "").slice(0, 70)} · ${r.c}`, origen: r.o || "", fecha: r.fe || hoy(), coincide };
    if (coincide === "similar") f.diferencia = resultado.difs.join("; ") || "Pieza similar: completar en qué difiere";
    if (!r.p) { f.tipo = "est"; f.proveedor = "SIN PRECIO CONFIABLE: pedir cotización · " + r.c; f.coincide = "sin_ref"; f.diferencia = "Sin precio confiable en el catálogo"; }
    return { id, pos: "", grupo: "material", descripcion: r.d.slice(0, 120), especificacion: describirAtributos(r.a), cantidad, unidad: r.u || "un", fuentes: [f] };
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
  function soldadura(datos, filas) {
    let pulg = 0, pch = 0, pgr = 0; const detalle = [];
    for (const f of filas) {
      const dn = parseFloat(f.dn); if (!dn) continue;
      const t = datos.soldadura.find(r => Math.abs(r.dn - dn) < 1e-6 && (r.sch === f.sch || r.cl === f.sch)) || { fe: 1, pch: 0, pgr: 0 };
      const bw = +f.bw || 0, sw = +f.sw || 0, ol = +f.olet || 0;
      const fo = f.tipoOlet === "weldolet" ? 2.5 : 1.75;
      const v = (bw + sw) * dn * t.fe + ol * dn * fo;
      pulg += v; pch += bw * (t.pch || 0); pgr += bw * (t.pgr || 0);
      detalle.push(`${bw + sw} junta(s) ${dn}" sch ${f.sch || "40"} × ${t.fe}` + (ol ? ` + ${ol} olet/cupla × ${dn}" × ${fo}` : "") + ` = ${v.toFixed(2)}`);
    }
    return { pulg: Motor.redondear(pulg, 3), placas_chicas: pch, placas_grandes: pgr, detalle };
  }

  function tarifa(datos, rubro, texto, tipos = ["costo_propio"]) {
    return datos.tarifas.find(r => r.rubro === rubro && norm(r.concepto).includes(texto) && tipos.includes(r.tipo));
  }

  // Avisos de una cotización (verificar_computo + control de carga)
  function avisos(cfg) {
    const out = []; const h = hoy();
    for (const it of cfg.items) {
      const s = it.fuentes[0], tag = `${it.pos || it.id} ${it.descripcion.slice(0, 40)}`, n0 = out.length;
      if (!s.precio) out.push({ nivel: "bad", txt: `${tag}: SIN PRECIO, pedir cotización antes de presentar` });
      if (!s.proveedor || !s.fecha) out.push({ nivel: "bad", txt: `${tag}: precio sin fuente o sin fecha` });
      if (s.fecha && (!/^\d{4}-\d{2}-\d{2}$/.test(s.fecha) || s.fecha > h)) out.push({ nivel: "bad", txt: `${tag}: fecha inválida o futura (${s.fecha})` });
      if (s.coincide === "similar" && !s.diferencia) out.push({ nivel: "bad", txt: `${tag}: similar sin decir en qué difiere` });
      if (s.coincide === "similar") out.push({ nivel: "warn", txt: `${tag}: pieza SIMILAR (${(s.diferencia || "").slice(0, 80)})` });
      if (s.tipo === "est" && s.precio) out.push({ nivel: "warn", txt: `${tag}: precio ESTIMADO (USD ${(it.cantidad * s.precio).toFixed(2)})` });
      if (/con iva|iva incluido|c\/ ?iva/.test(norm(s.proveedor + " " + (s.diferencia || "")))) out.push({ nivel: "warn", txt: `${tag}: la fuente dice "con IVA": cargar el precio sin IVA` });
      if (s.fecha && s.fecha < "2025-04-14" && !/tc |tipo de cambio/.test(norm(s.proveedor))) out.push({ nivel: "warn", txt: `${tag}: precio del período con cepo (${s.fecha}) sin tipo de cambio explícito` });
      if (s.fecha && /^\d{4}-\d{2}/.test(s.fecha)) {
        const [y, m] = s.fecha.split("-").map(Number), [Y, M] = h.split("-").map(Number);
        const meses = (Y - y) * 12 + M - m;
        if (meses > 6 && s.tipo !== "est") out.push({ nivel: "warn", txt: `${tag}: precio de hace ${meses} meses (${s.fecha}), actualizar` });
      }
      for (const x of out.slice(n0)) { x.id = it.id; x.corto = x.txt.slice(tag.length + 2); }
    }
    return out;
  }
  return { norm, coincide, campos, opcionales, valores, materiales, servicios, itemDeMaterial, itemDeServicio, soldadura, tarifa, avisos, TIPO_FUENTE, CON_TIPO };
})();
if (typeof module !== "undefined") module.exports = Busqueda;
