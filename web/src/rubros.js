// Modo Detallado / Global por rubro y ficha del rubro (pedido de Matías, 28-10-2026). Mismas reglas que herramientas/ficha_rubros.py.
// Global: un renglón por rubro (cantidad 1, "gl", rubro, global: true) con el precio del tercero; los renglones detallados quedan
// guardados en cot.rubros[r].detalle y vuelven al pasar a detallado. El motor no cambia: suma cot.items como siempre. Todo por equipo.
// La ficha física (soldaduras, kg, m², placas) viene de cot.ficha (la arma ficha_rubros.py con la tabla del plano); si no está, la
// página arma una aproximada con lo cargado. El transporte se recalcula siempre con las medidas de cot.transporte.
const Rubros = (() => {
  const RUBROS = {  // en el orden en que se muestran (un ítem por rubro de fabricación, pedido de Matías 29-10-2026)
    mo_estructura: ["Fabricación del skid (estructura)", "mo"],
    mo_piping: ["Fabricación del piping", "mo"],
    pintura: ["Granallado y pintura", "servicio"],
    end: ["Radiografía y END", "servicio"],
    procedimientos: ["Procedimientos", "servicio"],
    ph: ["Prueba hidráulica", "servicio"],
    horas: ["Horas de ITT (ingeniería, calidad y montaje)", "mo"],
    transporte: ["Transporte", "servicio"],
  };
  const CAMION = { largo: 13.5, ancho: 2.5, piso: 1.2, kg: 27000 }, LIMITE_ANCHO = 2.6, LIMITE_ALTO = 4.1;
  const ESTRUCTURA = /estructura|perfileria|bastidor|\bskid\b|\bupn\b|\bipn\b|\bheb\b|\bhea\b|\bipe\b|angulo|planchuela/;
  const norm = t => String(t || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();

  function rubroDe(it) {
    if (it.rubro) return it.rubro;
    if (it.grupo === "material") return null;
    const t = norm(`${it.pos || ""} ${it.descripcion}`);
    if (/caucion|seguro|repuesto/.test(t)) return null;
    if (String(it.pos || "").toUpperCase() === "PH" || /^prueba hidraul/.test(norm(it.descripcion))) return "ph";
    if (/\bhoras?\b|ingenier|calidad/.test(t)) return "horas";
    if (/procedimiento|\bwps\b|\bpqr\b|\bwpq\b|calificacion de soldador/.test(t)) return "procedimientos";
    if (/granall|pintur|arenad|revestim/.test(t)) return "pintura";
    if (/radiograf|\brx\b|\blp\b|tintas|penetrant|ultrason|particulas|\bend\b|ensayo/.test(t)) return "end";
    if (/hidraul/.test(t)) return "ph";
    if (/flete|transporte|camion/.test(t)) return "transporte";
    if (/estructura|bastidor|perfileria|\bmoe\b/.test(t)) return "mo_estructura";
    if (/soldadur|armado|prefabricad|spool|ledesma|dimensional|piping/.test(t)) return "mo_piping";
    return null;
  }
  const modo = (cot, r) => cot.rubros?.[r]?.modo || "detallado";
  const globalDe = (cot, r) => cot.items.find(i => i.global && i.rubro === r);

  function pasarAGlobal(cot, r, hoy) {
    if (modo(cot, r) === "global") return null;
    const det = cot.items.filter(i => rubroDe(i) === r && !i.global);
    cot.items = cot.items.filter(i => !det.includes(i));
    const [nombre, grupo] = RUBROS[r];
    const it = { id: `G-${r}`, pos: "GL", grupo, rubro: r, global: true, descripcion: `${nombre} (global por equipo)`,
      especificacion: "Precio global del tercero: ver la ficha del rubro", cantidad: 1, unidad: "gl",
      fuentes: [{ tipo: "est", precio: 0, proveedor: "A cotizar: global del tercero", origen: "ficha_rubros.md (pedir con la ficha)", fecha: hoy, coincide: "igual",
        diferencia: "SIN PRECIO: pedir cotización global con la ficha del rubro" }] };
    cot.items.push(it);
    (cot.rubros ??= {})[r] = { ...(cot.rubros?.[r] || {}), modo: "global", detalle: det };
    return it;
  }
  function volverADetallado(cot, r) {
    if (modo(cot, r) !== "global") return;
    const det = cot.rubros[r].detalle || [];
    cot.items = cot.items.filter(i => !(i.global && i.rubro === r)).concat(det);
    cot.rubros[r] = { modo: "detallado", ...(cot.rubros[r].tarifa ? { tarifa: cot.rubros[r].tarifa } : {}) };
  }

  // Ficha aproximada de la página (sin tabla del plano): kg y m² de caños por la tabla ASME, kg de las demás piezas de cot.kg_compras
  function fichaBasica(cot, datos, sold) {
    let kgP = 0, m2C = 0, kgE = 0;
    for (const it of cot.items.filter(i => i.grupo === "material")) {
      const d = norm(it.descripcion + " " + (it.especificacion || ""));
      if (ESTRUCTURA.test(norm(it.descripcion))) { if (norm(it.unidad) === "kg") kgE += it.cantidad; continue; }
      if (/\bcano\b|\bniple|\btubo\b/.test(d)) {
        const dn = parseFloat(String(it.plano?.diametro || "").replace(/"/g, "").replace(" 1/2", ".5")) || null, sch = (String(it.plano?.serie_sch || "").match(/\d+|STD|XS/i) || ["40"])[0].toUpperCase();
        const f = datos.canos.find(c => dn && Math.abs(c.dn - dn) < 1e-6 && (c.sch === sch || c.cl === sch));
        const largo = it.unidad === "m" ? 1 : (parseFloat((d.match(/(\d[\d.]*)\s?mm/) || [])[1]?.replace(".", "")) || 0) / 1000;
        if (f && largo) { kgP += f.kg * largo * it.cantidad; m2C += f.m2 * largo * it.cantidad; continue; }
      }
      const k = cot.kg_compras?.[String(it.pos)];
      if (k) kgP += k * it.cantidad;
    }
    const s = sold && typeof Busqueda !== "undefined" ? Busqueda.soldadura(datos, sold) : null, pct = cot.parametros.rx_pct || 0;
    const m2E = kgE * 0.03;
    return { aproximada: true,
      mo_piping: { juntas_bw: null, pulg_eq: s?.pulg || null, juntas_sw_olet: null, extremos_campo: null, kg_piping: kgP, bridas: cot.items.filter(i => i.grupo === "material" && /^brida/.test(norm(i.descripcion))).reduce((a, i) => a + i.cantidad, 0), diametros: [] },
      mo_estructura: { kg: kgE, m2: m2E },
      pintura: { m2_canos: m2C, m2_piping: m2C, m2_estructura: m2E, m2_total: m2C + m2E, esquema: cot.pintura?.esquema || "" },
      end: { juntas_bw: null, rx_pct: pct, placas_chicas: s ? Math.ceil(s.placas_chicas * pct / 100) : null, placas_grandes: s ? Math.ceil(s.placas_grandes * pct / 100) : null, juntas_lp: null, procedimientos: [] } };
  }

  function transporte(cot, kgEquipo) {
    const t = cot.transporte || {}, L = +t.largo_m || 0, A = +t.ancho_m || 0, H = +t.alto_m || 0;
    const r = { largo_m: L, ancho_m: A, alto_m: H, kg_equipo: kgEquipo, destino: t.destino || "", por_camion: null, viajes: null, avisos: [] };
    if (!(L && A && H)) { r.avisos.push("Faltan las medidas del equipo (largo × ancho × alto): cargarlas del plano de conjunto"); return r; }
    if (A > LIMITE_ANCHO && L > LIMITE_ANCHO) r.avisos.push(`Ancho ${A} m: supera ${LIMITE_ANCHO} m → carga especial (permiso de Vialidad y escolta)`);
    if (H + CAMION.piso > LIMITE_ALTO) r.avisos.push(`Alto cargado ${(H + CAMION.piso).toFixed(2)} m (equipo ${H} m + piso ${CAMION.piso} m): supera ${LIMITE_ALTO} m → carretón o carga especial`);
    if (Math.max(L, A) > CAMION.largo) r.avisos.push(`Largo ${Math.max(L, A)} m: más que la caja de un semi (${CAMION.largo} m) → carretón extensible`);
    const entra = (l, a) => l <= CAMION.largo && a <= CAMION.ancho ? Math.floor(CAMION.largo / l) * Math.floor(CAMION.ancho / a) : 0;
    const porMedida = Math.max(entra(L, A), entra(A, L), 1), porPeso = kgEquipo ? Math.floor(CAMION.kg / kgEquipo) : porMedida;
    const n = Math.max(1, Math.min(porMedida, porPeso));
    Object.assign(r, { por_camion: n, viajes: Math.ceil(cot.parametros.N / n), por_medida: porMedida, por_peso: porPeso });
    return r;
  }

  // Ficha completa: la de Claude Code (cot.ficha) o la aproximada, más transporte y referencias en vivo
  function ficha(cot, datos, sold, motor) {
    // la ficha se calcula en vivo con ficha.js (mismas fórmulas que ficha_rubros.py); sin ficha.js, la guardada o la aproximada
    const base = typeof Ficha !== "undefined" ? Ficha.calcular(cot, datos)
      : cot.ficha && cot.ficha.mo_piping ? JSON.parse(JSON.stringify(cot.ficha)) : fichaBasica(cot, datos, sold);
    base.transporte = transporte(cot, (base.mo_piping.kg_piping || 0) + (base.mo_estructura.kg || 0));
    base.referencias = {};
    const idx = motor.indicesDe(cot, datos.indices), p = cot.parametros, fref = p.fecha_referencia.slice(0, 7);
    const importe = its => its.reduce((a, it) => a + it.cantidad * it.fuentes[0].precio * motor.factorAjuste(it, idx, fref, p.AJ), 0);
    for (const r of Object.keys(RUBROS)) {
      const g = globalDe(cot, r), det = modo(cot, r) === "global" ? cot.rubros[r].detalle || [] : cot.items.filter(i => rubroDe(i) === r);
      base.referencias[r] = { modo: modo(cot, r), detallado_usd: importe(det), renglones_detalle: det.length, global_usd: g ? g.fuentes[0].precio : null };
    }
    return base;
  }

  function unitarios(f, r, usd) {
    const x = f[r];
    const pares = { mo_piping: [["pulgada eq.", x.pulg_eq], ["kg de piping", x.kg_piping], ["junta a tope", x.juntas_bw]], mo_estructura: [["kg", x.kg]],
      pintura: [["m²", x.m2_total]], end: [["junta a tope", x.juntas_bw], ["placa", (x.placas_chicas || 0) + (x.placas_grandes || 0)]],
      transporte: [["viaje", x.por_camion ? 1 / x.por_camion : null]], procedimientos: [["procedimiento", x.cantidad]], ph: [["litro", x.litros]], horas: [] }[r];
    return pares.filter(([, q]) => q).map(([u, q]) => [u, usd / q]);
  }

  // Renglones de datos de la ficha de un rubro: [etiqueta, valor, unidad]
  function datosDe(f, r) {
    const x = f[r];
    return {
      mo_piping: [["Juntas a tope (BW) de taller", x.juntas_bw, ""], ["Juntas SW, cuplas y olets", x.juntas_sw_olet, ""], ["Extremos para soldar en campo", x.extremos_campo, ""],
        ["Pulgadas equivalentes de soldadura", x.pulg_eq, "pulg"], ["kg de piping", x.kg_piping, "kg"], ["Con peso aproximado (sin tabla)", (x.aproximados || []).length ? x.aproximados.join("; ") : null, ""], ["Sin peso", (x.sin_peso || []).length ? x.sin_peso.join("; ") : null, ""], ["Bridas", x.bridas, ""],
        ["Diámetros soldados a tope", (x.diametros || []).map(d => d + '"').join(", ") || null, ""]],
      mo_estructura: [["kg de estructura", x.kg, "kg"], ["m² de estructura", x.m2, "m²"]],
      pintura: [["m² de piping", x.m2_piping, "m²"], ["m² de estructura", x.m2_estructura, "m²"], ["m² total (sin overspray)", x.m2_total, "m²"], ["Esquema", x.esquema || "según pliego", ""]],
      end: [["Juntas a tope", x.juntas_bw, ""], ["RX", x.rx_pct, "%"], ["Placas chicas", x.placas_chicas, ""], ["Placas grandes", x.placas_grandes, ""],
        ["Juntas con LP (SW, cuplas y olets)", x.juntas_lp, ""]],
      procedimientos: (x.lista || []).map(p => [p.nombre + (p.alcance ? ` (${p.alcance})` : ""), p.cantidad, ""]),
      ph: [["Volumen interior de los caños", x.litros, "litros"]],
      horas: [],
      transporte: [["Largo × ancho × alto", x.largo_m && x.ancho_m && x.alto_m ? [x.largo_m, x.ancho_m, x.alto_m].map(d => d.toLocaleString("es-AR")).join(" × ") : null, "m"], ["kg por equipo (piping + estructura)", x.kg_equipo, "kg"],
        ["Destino", x.destino || null, ""], ["Equipos por semirremolque", x.por_camion, ""], ["Viajes para la cantidad", x.viajes, ""]],
    }[r] || [];
  }

  // Texto de la ficha para pedir cotización al tercero (sin precios internos)
  function texto(cot, f, r, num) {
    const eq = cot.equipo?.singular || "equipo";
    const v = x => x == null || x === "" ? "—" : typeof x === "number" ? num(x, Number.isInteger(x) ? 0 : 2) : x;
    return [`Pedido de cotización: ${RUBROS[r][0]}`, `${cot.codigo} · ${cot.titulo || ""}`, `Cliente: ${cot.cliente?.nombre || ""}`,
      `Precio por ${eq} (USD sin IVA). Cantidad: ${cot.parametros.N} ${cot.equipo?.plural || "equipos"}.`, "",
      ...datosDe(f, r).map(([e, x, u]) => `- ${e}: ${v(x)}${u && x != null ? " " + u : ""}`), ...(f[r].avisos || []).map(a => `- Atención: ${a}`)].join("\n");
  }

  // ---------------------------------------------------------------- costo por antecedentes
  // Opciones de tarifa del historial para un rubro (tarifas.csv y catálogo de servicios con tarifa unitaria) y renglones que genera.
  const fechaDia = f => /^\d{4}-\d{2}-\d{2}/.test(f || "") ? f.slice(0, 10) : /^\d{4}-\d{2}$/.test(f || "") ? f + "-01" : /^\d{4}$/.test(f || "") ? f + "-07-01" : "";
  // base de cobro del piping: por pulgada de soldadura o por kg (hay proveedores que cotizan por kilo)
  const basePiping = cot => cot.rubros?.mo_piping?.base === "kg" ? "kg" : "pulg";
  function opcionesTarifa(datos, r, base = "pulg") {
    const tar = (rubro, unidad) => datos.tarifas.filter(t => t.rubro === rubro && t.unidad === unidad && t.tipo !== "precio_venta" && isFinite(+t.valor) && fechaDia(t.fecha))
      .map(t => ({ id: "T:" + t.concepto + t.fecha + t.valor, valor: +t.valor, fecha: fechaDia(t.fecha), etiqueta: `${t.concepto} (${t.tipo.replace(/_/g, " ")})`, origen: t.fuente || "conocimiento/costos/tarifas.csv" }));
    const srv = (ut, rx) => datos.servicios.filter(x => x.ut === ut && x.t && !/ESTIMADO/.test(x.al || "") && (!rx || rx.test(norm(x.s))) && fechaDia(x.fe))
      .map(x => ({ id: "S:" + x.c, valor: x.t, fecha: fechaDia(x.fe), etiqueta: `${x.s} · ${String(x.pr || "").slice(0, 40)} · ${x.c}`, origen: x.o || x.c }));
    const ops = { mo_piping: base === "kg" ? srv("USD/kg", /skid|piping|spool|caner|carretel/).filter(o => !/estructura de skid|bastidor|\bupn\b|\bipn\b|percha|trampa/.test(norm(o.etiqueta))) : [...tar("soldadura", "USD/pulg-diam-eq"), ...srv("USD/pulg-eq")],
      mo_estructura: [...tar("estructura", "USD/kg"), ...srv("USD/kg", /estructura|skid|perfil/)],
      pintura: [...tar("pintura", "USD/m2"), ...srv("USD/m2")],
      ph: srv("USD/hora", /hidr/) }[r] || [];
    return ops.sort((a, b) => b.fecha.localeCompare(a.fecha));
  }
  const UNIDADES = { mo_piping: ["pulg", "pulgadas equivalentes"], mo_estructura: ["kg", "kg de estructura"], pintura: ["m2", "m² a pintar"], ph: ["h", "horas de prueba"] };
  const unidadDe = (cot, r) => r === "mo_piping" && basePiping(cot) === "kg" ? ["kg", "kg de piping"] : UNIDADES[r];
  // Renglones por antecedentes de un rubro: [{descripcion, especificacion, cantidad, unidad, precio, fuente}] y el texto del cálculo.
  // La tarifa sale del historial o es una tarifa propia escrita a mano (cot.rubros[r].propia: valor, proveedor, fecha).
  function antecedentes(cot, datos, f, r) {
    const N = +cot.parametros.N || 1, num = (v, d = 2) => Number(v || 0).toLocaleString("es-AR", { minimumFractionDigits: d, maximumFractionDigits: d });
    const base = basePiping(cot), rb = cot.rubros?.[r] || {}, ops = opcionesTarifa(datos, r, base);
    const propia = rb.tarifa === "PROPIA" ? { id: "PROPIA", valor: +(rb.propia?.valor || 0), fecha: rb.propia?.fecha || "", etiqueta: rb.propia?.proveedor || "Tarifa propia", origen: rb.propia?.origen || "cargada a mano en la página" } : null;
    const elegida = propia || ops.find(o => o.id === rb.tarifa) || ops[0];
    const UNIDAD = unidadDe(cot, r);
    if (UNIDAD) {
      const cant = r === "mo_piping" ? (base === "kg" ? f.mo_piping.kg_piping : f.mo_piping.pulg_eq) : r === "mo_estructura" ? f.mo_estructura.kg : r === "pintura" ? f.pintura.m2_total : +(cot.parametros.ph_horas || 6);
      const res = { opciones: ops, elegida, base, unidad: UNIDAD, renglones: [] };
      if (!elegida) return { ...res, texto: "No hay tarifas del historial para esta base: elegí «Tarifa propia» y cargala." };
      if (!elegida.valor) return { ...res, texto: "Cargá el valor de la tarifa propia." };
      if (propia && !/^\d{4}-\d{2}-\d{2}$/.test(propia.fecha)) return { ...res, texto: "Cargá la fecha de la tarifa propia." };
      if (!cant) return { ...res, texto: `Falta la cantidad (${UNIDAD[1]}): completá los datos del plano y Recalculá.` };
      const desc = { mo_piping: `Soldadura y armado del piping (${num(f.mo_piping.juntas_bw, 0)} juntas a tope + SW y olets${base === "kg" ? ", por kg" : ""})`, mo_estructura: "Fabricación de la estructura del skid",
        pintura: "Granallado y pintura (piping y estructura)", ph: `Prueba hidráulica (horas de planta; ${num(f.ph?.litros || 0, 0)} litros)` }[r];
      return { ...res, texto: `${num(cant)} ${UNIDAD[1]} × USD ${num(elegida.valor)} = USD ${num(cant * elegida.valor)}`,
        renglones: [{ descripcion: desc, especificacion: `${num(cant)} ${UNIDAD[0]} × USD ${num(elegida.valor)} (${elegida.etiqueta})`, cantidad: Math.round(cant * 1000) / 1000, unidad: UNIDAD[0],
          precio: elegida.valor, fuente: { tipo: propia ? "cot" : "ant", precio: elegida.valor, proveedor: elegida.etiqueta.slice(0, 120), origen: elegida.origen, fecha: elegida.fecha, coincide: "igual" } }] };
    }
    if (r === "end") {
      const t = c => datos.tarifas.find(x => x.rubro === "end" && norm(x.concepto).includes(c) && x.tipo === "tercero");
      const tc = t("placa radiografica chica"), tg = t("placa radiografica grande"), ts = t("servicio de radiografia (antonelli)"), tl = t("liquidos penetrantes");
      const e = f.end, ch = e.placas_chicas || 0, gr = e.placas_grandes || 0, sv = ch + gr ? Math.max(1, Math.ceil((ch + gr) / 40)) : 0;
      const ren = [];
      if (ch + gr && tc && ts) {
        const costo = ch * +tc.valor + gr * +(tg?.valor || 0) + sv * +ts.valor;
        ren.push({ descripcion: `Radiografía ${num(e.rx_pct, 0)}% de las juntas a tope`, especificacion: `${ch} placas chicas × ${tc.valor} + ${gr} grandes × ${tg?.valor || 0} + ${sv} servicio(s) × ${ts.valor}`,
          cantidad: 1, unidad: "gl", precio: costo, fuente: { tipo: "cot", precio: costo, proveedor: "NDT Antonelli (tarifas)", origen: ts.fuente || "conocimiento/costos/tarifas.csv", fecha: fechaDia(ts.fecha), coincide: "igual" } });
      }
      if (e.juntas_lp && tl) ren.push({ descripcion: `Líquidos penetrantes en SW, cuplas y olets (${e.juntas_lp} juntas)`, especificacion: `1 servicio × ${tl.valor}`, cantidad: 1, unidad: "servicio",
        precio: +tl.valor, fuente: { tipo: "cot", precio: +tl.valor, proveedor: "NDT Antonelli (tarifas)", origen: tl.fuente || "conocimiento/costos/tarifas.csv", fecha: fechaDia(tl.fecha), coincide: "igual" } });
      return { opciones: [], renglones: ren, texto: ren.length ? ren.map(x => `${x.descripcion}: USD ${num(x.precio)}`).join(" · ") : "Sin juntas a tope ni placas: completá los datos del plano y Recalculá." };
    }
    if (r === "procedimientos") {
      const t = datos.tarifas.find(x => x.rubro === "end" && norm(x.concepto).includes("procedimiento escrito"));
      const end = (f.procedimientos?.lista || []).filter(p => p.tipo === "end");
      const ren = t ? end.map(p => ({ descripcion: p.nombre, especificacion: `USD ${num(+t.valor)} por trabajo ÷ ${N} equipo(s)`, cantidad: 1, unidad: "gl", precio: Math.round(+t.valor / N * 100) / 100,
        fuente: { tipo: "cot", precio: Math.round(+t.valor / N * 100) / 100, proveedor: t.concepto, origen: t.fuente || "conocimiento/costos/tarifas.csv", fecha: fechaDia(t.fecha), coincide: "igual" } })) : [];
      const sin = (f.procedimientos?.lista || []).filter(p => p.tipo !== "end").length;
      return { opciones: [], renglones: ren, texto: (ren.length ? `${ren.length} procedimiento(s) de END × USD ${num(+t.valor)} ÷ ${N} equipo(s)` : "Sin procedimientos de END")
        + (sin ? ` · ${sin} sin costo de antecedente (WPS/PQR, WPQ, PH, pintura): si hacen falta nuevos, pedir cotización` : "") };
    }
    return { opciones: [], renglones: [], texto: r === "horas" ? "Se estiman con el antecedente más parecido (precotización de Claude Code). Los renglones se editan acá." : "" };
  }
  // Reemplaza los renglones por antecedentes del rubro por los que calcula antecedentes()
  function aplicarAntecedentes(cot, datos, f, r) {
    const a = antecedentes(cot, datos, f, r);
    if (!a.renglones.length) return 0;
    const [, grupo] = RUBROS[r];
    cot.items = cot.items.filter(i => !(rubroDe(i) === r && !i.global));
    a.renglones.forEach((x, k) => cot.items.push({ id: `A-${r}-${k + 1}`, pos: "MO", grupo, rubro: r, descripcion: x.descripcion, especificacion: x.especificacion,
      cantidad: x.cantidad, unidad: x.unidad, fuentes: [x.fuente] }));
    return a.renglones.length;
  }

  return { RUBROS, CAMION, rubroDe, basePiping, opcionesTarifa, antecedentes, aplicarAntecedentes, modo, globalDe, pasarAGlobal, volverADetallado, fichaBasica, transporte, ficha, unitarios, datosDe, texto };
})();
if (typeof module !== "undefined") module.exports = Rubros;
