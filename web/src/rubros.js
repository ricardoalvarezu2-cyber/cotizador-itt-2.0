// Modo Detallado / Global por rubro y ficha del rubro (pedido de Matías, 28-10-2026). Mismas reglas que herramientas/ficha_rubros.py.
// Global: un renglón por rubro (cantidad 1, "gl", rubro, global: true) con el precio del tercero; los renglones detallados quedan
// guardados en cot.rubros[r].detalle y vuelven al pasar a detallado. El motor no cambia: suma cot.items como siempre. Todo por equipo.
// La ficha física (soldaduras, kg, m², placas) viene de cot.ficha (la arma ficha_rubros.py con la tabla del plano); si no está, la
// página arma una aproximada con lo cargado. El transporte se recalcula siempre con las medidas de cot.transporte.
const Rubros = (() => {
  const RUBROS = {
    mo_piping: ["MO de armado y soldadura del piping", "mo"],
    mo_estructura: ["MO de fabricación de la estructura", "mo"],
    pintura: ["Granallado y pintura", "servicio"],
    end: ["RX, END y procedimientos", "servicio"],
    transporte: ["Transporte", "servicio"],
  };
  const CAMION = { largo: 13.5, ancho: 2.5, piso: 1.2, kg: 27000 }, LIMITE_ANCHO = 2.6, LIMITE_ALTO = 4.1;
  const ESTRUCTURA = /estructura|perfileria|bastidor|\bskid\b|\bupn\b|\bipn\b|\bheb\b|\bhea\b|\bipe\b|angulo|planchuela/;
  const norm = t => String(t || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();

  function rubroDe(it) {
    if (it.rubro) return it.rubro;
    if (it.grupo === "material") return null;
    const t = norm(`${it.pos || ""} ${it.descripcion}`);
    if (/\bhoras?\b|ingenier|calidad|hidraul|caucion|seguro|repuesto/.test(t)) return null;
    if (/granall|pintur|arenad|revestim/.test(t)) return "pintura";
    if (/radiograf|\brx\b|\blp\b|tintas|penetrant|ultrason|particulas|\bend\b|ensayo|procedimiento|\bwps\b|\bpqr\b/.test(t)) return "end";
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
    (cot.rubros ??= {})[r] = { modo: "global", detalle: det };
    return it;
  }
  function volverADetallado(cot, r) {
    if (modo(cot, r) !== "global") return;
    const det = cot.rubros[r].detalle || [];
    cot.items = cot.items.filter(i => !(i.global && i.rubro === r)).concat(det);
    cot.rubros[r] = { modo: "detallado" };
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
    const base = cot.ficha && cot.ficha.mo_piping ? JSON.parse(JSON.stringify(cot.ficha)) : fichaBasica(cot, datos, sold);
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
      transporte: [["viaje", x.por_camion ? 1 / x.por_camion : null]] }[r];
    return pares.filter(([, q]) => q).map(([u, q]) => [u, usd / q]);
  }

  // Renglones de datos de la ficha de un rubro: [etiqueta, valor, unidad]
  function datosDe(f, r) {
    const x = f[r];
    return {
      mo_piping: [["Juntas a tope (BW) de taller", x.juntas_bw, ""], ["Juntas SW, cuplas y olets", x.juntas_sw_olet, ""], ["Extremos para soldar en campo", x.extremos_campo, ""],
        ["Pulgadas equivalentes de soldadura", x.pulg_eq, "pulg"], ["kg de piping (con tabla)", x.kg_piping, "kg"], ["Bridas", x.bridas, ""],
        ["Diámetros soldados a tope", (x.diametros || []).map(d => d + '"').join(", ") || null, ""]],
      mo_estructura: [["kg de estructura", x.kg, "kg"], ["m² de estructura", x.m2, "m²"]],
      pintura: [["m² de piping", x.m2_piping, "m²"], ["m² de estructura", x.m2_estructura, "m²"], ["m² total (sin overspray)", x.m2_total, "m²"], ["Esquema", x.esquema || "según pliego", ""]],
      end: [["Juntas a tope", x.juntas_bw, ""], ["RX", x.rx_pct, "%"], ["Placas chicas", x.placas_chicas, ""], ["Placas grandes", x.placas_grandes, ""],
        ["Juntas con LP (SW, cuplas y olets)", x.juntas_lp, ""], ...(x.procedimientos || []).map(t => ["Procedimiento", t, ""])],
      transporte: [["Largo × ancho × alto", x.largo_m && x.ancho_m && x.alto_m ? [x.largo_m, x.ancho_m, x.alto_m].map(d => d.toLocaleString("es-AR")).join(" × ") : null, "m"], ["kg por equipo (piping + estructura)", x.kg_equipo, "kg"],
        ["Destino", x.destino || null, ""], ["Equipos por semirremolque", x.por_camion, ""], ["Viajes para la cantidad", x.viajes, ""]],
    }[r];
  }

  // Texto de la ficha para pedir cotización al tercero (sin precios internos)
  function texto(cot, f, r, num) {
    const eq = cot.equipo?.singular || "equipo";
    const v = x => x == null || x === "" ? "—" : typeof x === "number" ? num(x, Number.isInteger(x) ? 0 : 2) : x;
    return [`Pedido de cotización: ${RUBROS[r][0]}`, `${cot.codigo} · ${cot.titulo || ""}`, `Cliente: ${cot.cliente?.nombre || ""}`,
      `Precio por ${eq} (USD sin IVA). Cantidad: ${cot.parametros.N} ${cot.equipo?.plural || "equipos"}.`, "",
      ...datosDe(f, r).map(([e, x, u]) => `- ${e}: ${v(x)}${u && x != null ? " " + u : ""}`), ...(f[r].avisos || []).map(a => `- Atención: ${a}`)].join("\n");
  }

  return { RUBROS, CAMION, rubroDe, modo, globalDe, pasarAGlobal, volverADetallado, fichaBasica, transporte, ficha, unitarios, datosDe, texto };
})();
if (typeof module !== "undefined") module.exports = Rubros;
