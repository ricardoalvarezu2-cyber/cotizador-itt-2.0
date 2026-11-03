// Documentos que descarga la página: planilla del presupuesto (Excel con fórmulas, mismo diseño que armar_cotizacion.py),
// lista para Compras, informe del presupuesto (PDF), ofertas técnica y económica (Word con la plantilla de ITT y PDF) y respaldo.
// Librerías: XLSX (xlsx-js-style), JSZip, html2pdf.
const Documentos = (() => {
  const TIPOS = { cot: "Cotización", lista: "Lista de precios", stock: "Stock / compra", ant: "Planilla interna", est: "Estimado" };
  const COINC = { igual: "Igual", similar: "Similar", sin_ref: "Sin referencia" };
  const W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main";
  const esc = s => String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  // Números a la vista (decisión de Matías, 29-10-2026): punto de miles, coma decimal y 2 decimales, en la página, el
  // informe, las planillas y las ofertas. Igual que numeros.fmt en Python. No depende del idioma del navegador.
  function num(v, d = 2) {
    const n = Number(v || 0), [e, f] = Math.abs(n).toFixed(d).split(".");
    const t = e.replace(/\B(?=(\d{3})+(?!\d))/g, ".") + (f ? "," + f : "");
    return (n < 0 && /[1-9]/.test(t) ? "-" : "") + t;
  }
  const numg = v => num(v).replace(/,?0+$/, ""); // sin ceros de más: 0,5 · 12 · 1.234,57
  const usd = v => "USD " + num(v);
  // Fechas a la vista: siempre DD-MM-AAAA (decisión de Matías, 28/10/2026); adentro se guardan AAAA-MM-DD. Igual que numeros.a_vista.
  const dos = n => String(n).padStart(2, "0");
  function fecha(v) {
    if (v instanceof Date) return `${dos(v.getDate())}-${dos(v.getMonth() + 1)}-${v.getFullYear()}`;
    const s = String(v ?? "").trim(); let m;
    if ((m = s.match(/^(\d{4})-(\d{2})-(\d{2})/))) return `${m[3]}-${m[2]}-${m[1]}`;
    if ((m = s.match(/^(\d{4})-(\d{2})$/))) return `${m[2]}-${m[1]}`;
    if ((m = s.match(/^(\d{1,2})\/(\d{1,2})\/(\d{4})$/))) return `${dos(m[1])}-${dos(m[2])}-${m[3]}`;
    return s;
  }
  const fechaHora = v => { if (!v) return ""; const d = new Date(v); return isNaN(d) ? fecha(v) : `${fecha(d)} ${dos(d.getHours())}:${dos(d.getMinutes())}`; };
  // Número escrito por el usuario (decisión de Matías, 29-10-2026): el punto separa miles y la coma decimales, con 2
  // decimales como máximo. "1.500" = 1500 · "1,5" = 1,5 · "1.234,56" · "1500". Lo que no cumple da null (el campo se marca
  // en rojo, dice por qué y no se guarda): así "1,500" o "1.5" nunca se leen distinto de lo que se quiso escribir.
  function numeroDe(t) {
    const s = String(t ?? "").trim().replace(/\s/g, "").replace(/^(usd|u\$s|\$)/i, "");
    if (!/^-?(\d{1,3}(\.\d{3})+|\d+)(,\d{1,2})?$/.test(s)) return null;
    const n = Number(s.replace(/\./g, "").replace(",", "."));
    return isFinite(n) ? n : null;
  }
  // Por qué no se aceptó lo escrito ("" si está bien o vacío)
  function errorNumero(t) {
    const s = String(t ?? "").trim().replace(/\s/g, "").replace(/^(usd|u\$s|\$)/i, "");
    if (!s || numeroDe(s) != null) return "";
    if (/,\d{3,}$/.test(s)) return "Máximo 2 decimales. Si son miles, van con punto: 1.500";
    if (/\.\d{1,2}$/.test(s) || /\.\d{4,}/.test(s)) return "El punto separa miles; los decimales van con coma: 1,5";
    return "Escribí el número así: 1.234,56 (punto de miles, coma decimal)";
  }
  // Número dentro de un campo editable: mismo formato que a la vista, sin ceros de más
  const NI = v => (v === "" || v == null || isNaN(Number(v))) ? "" : numg(v);
  // Transporte cargado con precio en MO y servicios (ítem global del rubro transporte): va dentro del precio unitario,
  // así que la oferta no puede decir EXW. null si no hay.
  function transporteIncluido(cot) {
    const g = (cot.items || []).find(i => i.global && i.rubro === "transporte" && +(i.fuentes?.[0]?.precio) > 0);
    return g ? { destino: cot.transporte?.destino || "", transportista: cot.transporte?.transportista || "", precio: +g.fuentes[0].precio } : null;
  }
  const notaTransporte = t => `Precio puesto en ${t.destino || "el lugar de entrega acordado"}: el transporte está incluido en el precio unitario.`;
  // La oferta toma de la cotización lo que ya está cargado (auditoría 29-10-2026): el plazo y la revisión siempre salen de
  // la cotización (una sola fuente); cliente, contacto y fecha, si en la oferta siguen vacíos o entre [corchetes]. Igual que
  // generar_oferta.completar en Python.
  function completarOferta(cot, of) {
    const o = JSON.parse(JSON.stringify(of || {}));
    const vacio = v => v == null || !String(v).trim() || /\[[^\]]*\]/.test(String(v)), ok = v => v != null && String(v).trim() && !/\[/.test(String(v));
    o.oferta ??= {}; o.cliente ??= {}; o.item ??= {};
    if (vacio(o.cliente.nombre) && ok(cot.cliente?.nombre)) o.cliente.nombre = cot.cliente.nombre;
    if (vacio(o.cliente.contacto) && ok(cot.cliente?.comprador)) o.cliente.contacto = cot.cliente.comprador;
    if (vacio(o.oferta.fecha) && ok(cot.fecha)) o.oferta.fecha = cot.fecha;
    const rv = String(cot.revision || "").replace(/^rev\.?\s*/i, "").trim();
    if (rv) o.oferta.revision = rv;
    const d = cot.plazo?.dias;
    if (d) {
      o.item.plazo_dias = String(d);
      for (const k of Object.keys(o.condiciones || {}))
        o.condiciones[k] = [].concat(o.condiciones[k]).map(l => String(l).replace(/^(\[d[ií]as\]|\d+)(?= d[ií]as)/i, String(d)).replace(/\[d[ií]as\]/gi, String(d)));
    }
    return o;
  }
  // DD-MM-AAAA (o DD/MM/AAAA) escrita por el usuario → AAAA-MM-DD; "" si no es una fecha válida
  function isoDe(t) {
    const m = String(t || "").trim().match(/^(\d{1,2})[-/.](\d{1,2})[-/.](\d{4})$/); if (!m) return "";
    const d = new Date(+m[3], +m[2] - 1, +m[1]);
    return d.getDate() === +m[1] && d.getMonth() === +m[2] - 1 ? `${m[3]}-${dos(m[2])}-${dos(m[1])}` : "";
  }
  const serial = iso => { const [y, m, d] = String(iso).split("-").map(Number); return (Date.UTC(y, (m || 1) - 1, d || 1) - Date.UTC(1899, 11, 30)) / 86400000; };
  const sinHtml = s => String(s ?? "").replace(/<[^>]+>/g, "");

  // ------------------------------------------------------------------ Excel del presupuesto
  function planilla(cot, idx, datos, of = {}) {
    idx = Motor.indicesDe(cot, idx);
    const X = XLSX;
    const wb = X.utils.book_new();
    const H = { font: { bold: true, color: { rgb: "FFFFFF" } }, fill: { fgColor: { rgb: "1D5F86" } }, alignment: { wrapText: true, vertical: "center" } };
    const INP = { fill: { fgColor: { rgb: "FBEFD6" } } }, TOT = { fill: { fgColor: { rgb: "E8EDF0" } }, font: { bold: true } };
    const GRIS = { font: { italic: true, color: { rgb: "5D6B75" } } }, AZ = { font: { bold: true, color: { rgb: "1D5F86" } } };
    const TF = { cot: "DDF1E4", lista: "DCEBF4", stock: "DCEBF4", ant: "FBEFD6", est: "F8E1DE" };
    const U = "#,##0.00";
    const p = cot.parametros, eq = cot.equipo || { singular: "equipo", plural: "equipos" };
    const mat = cot.items.filter(i => i.grupo === "material"), srv = cot.items.filter(i => i.grupo !== "material");
    const nm = mat.length + 1, ns = srv.length + 1, ni = idx.length + 1;
    const RNG = `'Índices'!$A$2:$E$${ni}`;
    const hoja = () => ({ "!ref": "A1:A1" });
    const put = (ws, a, v, s, z) => {
      const c = typeof v === "object" && v !== null && "f" in v ? { t: "n", f: v.f } : (typeof v === "number" ? { t: "n", v } : { t: "s", v: String(v ?? "") });
      if (s) c.s = s; if (z) c.z = z;
      ws[a] = c;
      const r = X.utils.decode_range(ws["!ref"]), cell = X.utils.decode_cell(a);
      r.e.r = Math.max(r.e.r, cell.r); r.e.c = Math.max(r.e.c, cell.c); ws["!ref"] = X.utils.encode_range(r);
    };
    const A = (c, r) => X.utils.encode_cell({ c: c - 1, r: r - 1 });
    const cabecera = (ws, cols, anchos) => { cols.forEach((t, i) => put(ws, A(i + 1, 1), t, H)); ws["!cols"] = anchos.map(w => ({ wch: w })); };

    const ws = hoja();
    put(ws, "A1", `${cot.codigo} ${cot.revision || ""} · ${cot.titulo || ""}`, { font: { bold: true, sz: 14 } });
    put(ws, "A2", `${cot.subtitulo_planilla || ""} · ${cot.estado} ${fecha(cot.fecha)}`, GRIS);
    put(ws, "A4", "PARÁMETROS (celdas amarillas editables)", { font: { bold: true } });
    [[`Cantidad de ${eq.plural}`, p.N, "0"], ["Factor de materiales (materiales y contingencia)", p.FM, "#,##0.00"], ["Factor de mano de obra y servicios", p.FMO, "#,##0.00"],
     ["Contingencia materiales", p.CONT / 100, "0%"], ["Incluir flete (1 = sí, 0 = no)", p.TRANS, "0"], ["Tipo de cambio ARS/USD (BNA)", p.TC, "#,##0"],
     ["Flete ARS por envío", p.TR_ARS, "#,##0"], ["Embalaje USD por envío (estimado)", p.TR_EMB, U], ["Factor flete", p.TR_F, "#,##0.00"],
     ["Factor de válvulas Taval (con su contingencia)", p.FTV ?? 1, "#,##0.00"]]
      .forEach(([n, v, z], i) => { put(ws, A(1, 5 + i), n); put(ws, A(2, 5 + i), Number(v) || 0, INP, z); });
    put(ws, "G5", "AJUSTE POR INFLACIÓN (desde la fecha de cada precio hasta hoy)", { font: { bold: true } });
    put(ws, "G6", "Aplicar ajuste (1 = sí, 0 = no)"); put(ws, "H6", p.AJ ? 1 : 0, INP, "0");
    put(ws, "G7", "Fecha de hoy (referencia)"); put(ws, "H7", serial(p.fecha_referencia), INP, "dd-mm-yyyy");
    put(ws, "G8", "Variación 12 meses — materiales (CPI EE.UU.)"); put(ws, "H8", { f: `VLOOKUP(H7,${RNG},5,1)/VLOOKUP(EDATE(H7,-12),${RNG},5,1)-1` }, null, "0.0%");
    put(ws, "G9", "Variación 12 meses — MO y servicios (costo local en USD)"); put(ws, "H9", { f: `VLOOKUP(H7,${RNG},4,1)/VLOOKUP(EDATE(H7,-12),${RNG},4,1)-1` }, null, "0.0%");
    ["Factor de cada fila = índice del mes de hoy / índice del mes del precio (hoja Índices).", "Materiales: CPI de EE.UU. (los precios ya están en dólares).",
     "MO y servicios: costo local en dólares = IPC INDEC / dólar BNA vendedor (promedio mensual).", "Todos los precios sin IVA."]
      .forEach((t, i) => put(ws, A(7, 10 + i), t, GRIS));
    put(ws, "A16", "RESUMEN", { font: { bold: true } });
    ["Rubro", `Costo / ${eq.singular}`, "Factor", `Precio / ${eq.singular}`, "Total"].forEach((t, i) => put(ws, A(i + 1, 17), t, H));
    const S = "'MO y servicios'";
    [["Materiales sin válvulas Taval (con ajuste por inflación)", `SUMIF(Materiales!S2:S${nm},"<>sí",Materiales!P2:P${nm})`, "$B$6"], ["Contingencia", "B18*$B$8", "$B$6"],
     ["Válvulas Taval (con ajuste y contingencia)", `SUMIF(Materiales!S2:S${nm},"sí",Materiales!P2:P${nm})*(1+$B$8)`, "$B$14"],
     ["Mano de obra", `SUMIF(${S}!B2:B${ns},"MO",${S}!P2:P${ns})`, "$B$7"], ["Servicios e insumos", `SUMIF(${S}!B2:B${ns},"Servicio",${S}!P2:P${ns})`, "$B$7"]]
      .forEach(([n, f, fa], i) => {
        const r = 18 + i; put(ws, A(1, r), n); put(ws, A(2, r), { f }, null, U); put(ws, A(3, r), { f: fa }, null, "#,##0.00");
        put(ws, A(4, r), { f: `B${r}*C${r}` }, null, U); put(ws, A(5, r), { f: `D${r}*$B$5` }, null, U);
      });
    put(ws, "A23", "Flete + embalaje (por envío)"); put(ws, "C23", { f: "$B$13" }, null, "#,##0.00"); put(ws, "E23", { f: "IF($B$9=1,($B$11/$B$10+$B$12)*$B$13,0)" }, null, U);
    put(ws, "A24", "TOTAL SIN IVA", TOT); put(ws, "B24", { f: "SUM(B18:B22)" }, TOT, U); put(ws, "C24", { f: "D24/B24" }, TOT, "#,##0.00");
    put(ws, "D24", { f: "SUM(D18:D22)" }, TOT, U); put(ws, "E24", { f: "SUM(E18:E23)" }, TOT, U);
    put(ws, "A26", "Margen sobre precio"); put(ws, "D26", { f: "1-B24/D24" }, null, "0.0%");
    put(ws, "A27", "PRECIO UNITARIO DE VENTA (redondeado, va a la oferta)", AZ); put(ws, "D27", { f: "ROUND(D24,2)" }, AZ, U);
    put(ws, "A28", "TOTAL DE LA OFERTA SIN IVA (unitario redondeado × cantidad + flete)", AZ); put(ws, "E28", { f: "D27*B5+E23" }, AZ, U);
    put(ws, "A29", `Costo / ${eq.singular} SIN ajuste por inflación`); put(ws, "B29", { f: `SUM(Materiales!G2:G${nm})*(1+B8)+SUM(${S}!G2:G${ns})` }, null, U);
    put(ws, "A30", "Ajuste por inflación incluido en el costo"); put(ws, "B30", { f: "B24-B29" }, null, U); put(ws, "C30", { f: "B30/B29" }, null, "+0.0%");
    // peso del equipo y USD/kg (pedido de Matías, 29-10-2026), igual que armar_cotizacion.py
    const pe = datos && typeof Ficha !== "undefined" ? Ficha.pesoEquipo(cot, datos) : { kg: 0, sin_peso: [] };
    put(ws, "G16", `PESO Y PRECIO POR KILO (por ${eq.singular})`, { font: { bold: true } });
    put(ws, "G17", `Peso aproximado por ${eq.singular} (kg)`); put(ws, "H17", pe.kg, INP, "#,##0");
    put(ws, "G18", "Costo por kg (USD/kg)"); put(ws, "H18", { f: "IF(H17>0,B24/H17,0)" }, null, U);
    put(ws, "G19", "Precio de venta por kg (USD/kg)"); put(ws, "H19", { f: "IF(H17>0,D27/H17,0)" }, null, U);
    put(ws, "G20", pe.sin_peso.length ? `Sin peso (no suman): pos ${pe.sin_peso.join(", ")}. Corregir el peso a mano si hace falta.`
      : "Piping con tabla, estructura, renglones por kg y piezas con su peso; sin compras extra, repuestos ni instrumentos.", GRIS);
    (cot.planilla_notas || []).forEach((t, k) => put(ws, A(1, 32 + k), sinHtml(t)));
    ws["!cols"] = [{ wch: 52 }, { wch: 16 }, { wch: 16 }, { wch: 16 }, { wch: 16 }, { wch: 4 }, { wch: 58 }, { wch: 13 }];
    X.utils.book_append_sheet(wb, ws, "Cotización");

    // Datos del pedido y del antecedente, columna por columna (Matías, 03-11-2026), como atributos_plano.fila_datos
    const COLS = [["Ø", "diametro"], ["Ø2", "diametro2"], ["Serie", "serie"], ["Sch", "schedule"], ["Espesor mm", "espesor_mm"], ["Material", "material"],
      ["Extremos", "extremos"], ["Cara", "cara"], ["Norma", "norma"], ["Marca", "marca"], ["Modelo", "modelo"], ["Rango", "rango"]];
    const OTROS = ["tipo", "trim", "paso", "costura", "revestimiento", "largo_mm", "medida", "designacion", "conexion"];
    const NOMBRES = { diametro: "Ø", diametro2: "Ø2", espesor_mm: "espesor", largo_mm: "largo", designacion: "designación", conexion: "conexión" };
    const otros = a => OTROS.filter(k => a[k]).map(k => `${k}: ${a[k]}`).join("; ");
    const CATM = new Map(((datos && datos.materiales) || []).map(m => [m.c, m]));
    const filaDatos = it => {
      const at = it.atributos || (it.at ? { familia: it.fam || "", ...it.at } : {});
      let faltan = it.faltan_datos;
      if (!faltan && datos && at.familia && datos.familias?.[at.familia]) {
        const op = Busqueda.opcionales(at.familia, at);
        faltan = Busqueda.campos(datos, at.familia).filter(c => !at[c] && !op.has(c));
      }
      const s = it.fuentes[0], cod = Busqueda.codigoDe(s), m = CATM.get(cod), ra = m ? { ...(m.a || {}) } : {};
      return [[at.familia || "", ...COLS.map(([, k]) => at[k] || ""), otros(at), (faltan || []).map(k => NOMBRES[k] || k).join(", ")],
              [cod, m ? m.d : "", ...COLS.map(([, k]) => ra[k] || ""), otros(ra)]];
    };
    const ENC_P = ["Pedido: familia", ...COLS.map(([n]) => `Pedido: ${n}`), "Pedido: otros datos", "Datos que faltan del pedido"];
    const ENC_A = ["Antecedente: código", "Antecedente: descripción", ...COLS.map(([n]) => `Antecedente: ${n}`), "Antecedente: otros datos"];
    const detalle = (nombre, items, esSrv) => {
      const w = hoja();
      cabecera(w, ["Pos", esSrv ? "Grupo" : "ID", "Descripción", `Cant. / ${eq.singular}`, "Unidad", "USD unit. (a la fecha del precio)", "Subtotal USD (sin ajuste)",
        "Tipo de origen", "Proveedor o criterio", "Carpeta de origen", "Fecha del precio", "ID", "Meses hasta hoy",
        "Factor inflación (" + (esSrv ? "costo local USD" : "CPI EE.UU.") + ")", "USD unit. ajustado", "Subtotal USD ajustado", "Coincidencia con el plano", "Diferencia con lo pedido", ...(esSrv ? [] : ["Válvula Taval (factor aparte)"])],
        [6, 10, 44, 10, 8, 13, 13, 13, 48, 26, 12, 6, 9, 10, 12, 13, 13, 50, ...(esSrv ? [] : [12])]);
      const col = esSrv ? 4 : 5;
      items.forEach((it, k) => {
        const i = k + 2, s = it.fuentes[0];
        const vals = [it.pos, esSrv ? (it.grupo === "mo" ? "MO" : "Servicio") : it.id, it.descripcion, Number(it.cantidad), it.unidad, Number(s.precio), { f: `D${i}*F${i}` },
          TIPOS[s.tipo] || s.tipo, s.proveedor, s.origen, serial(s.fecha), it.id, { f: `MAX(0,('Cotización'!$H$7-K${i})/30.4375)` },
          { f: `IF('Cotización'!$H$6=1,VLOOKUP('Cotización'!$H$7,${RNG},${col},1)/VLOOKUP(MAX(K${i},'Índices'!$A$2),${RNG},${col},1),1)` },
          { f: `F${i}*N${i}` }, { f: `D${i}*O${i}` }, COINC[s.coincide] || "", s.diferencia || "", ...(esSrv ? [] : [Motor.esTaval(it) ? "sí" : ""])];
        vals.forEach((v, j) => {
          const c = j + 1;
          const st = c === 4 || c === 6 ? INP : c === 8 ? { fill: { fgColor: { rgb: TF[s.tipo] || "FFFFFF" } } } :
            c === 17 ? { fill: { fgColor: { rgb: { igual: "DDF1E4", similar: "FBEFD6", sin_ref: "F8E1DE" }[s.coincide] || "FFFFFF" } } } : null;
          const z = [6, 7, 15, 16].includes(c) ? U : c === 4 ? (Number.isInteger(v) ? "#,##0" : "#,##0.0###") : { 11: "dd-mm-yyyy", 13: "#,##0.00", 14: "#,##0.00" }[c];
          put(w, A(c, i), v, st, z);
        });
        if (!esSrv) {
          const [ped, ant] = filaDatos(it);
          [...ped, ...ant].forEach((v, j) => put(w, A(20 + j, i), v, j === ped.length - 1 && v ? { fill: { fgColor: { rgb: "F8E1DE" } } } : null));
        }
      });
      if (!esSrv) {
        [...ENC_P, ...ENC_A].forEach((t, j) => put(w, A(20 + j, 1), t, { ...H, fill: { fgColor: { rgb: j < ENC_P.length ? "2C7A4B" : "6B4E9B" } } }));
        w["!cols"] = [...(w["!cols"] || []), ...[...ENC_P, ...ENC_A].map(t => ({ wch: /descripción|otros datos|faltan del pedido/.test(t) ? 40 : 12 }))];
      }
      const n = items.length + 2;
      put(w, A(3, n), `Subtotal por ${eq.singular}`, TOT);
      put(w, A(7, n), { f: `SUM(G2:G${n - 1})` }, TOT, U); put(w, A(16, n), { f: `SUM(P2:P${n - 1})` }, TOT, U);
      let k = n + 2;
      for (const it of items) for (const a of it.fuentes.slice(1)) put(w, A(3, k++), `Alternativa pos ${it.pos}: USD ${numg(a.precio)} · ${a.proveedor} · ${a.origen} · ${fecha(a.fecha)} (${TIPOS[a.tipo]})`, GRIS);
      w["!autofilter"] = { ref: `A1:${X.utils.encode_col(esSrv ? 17 : 19 + ENC_P.length + ENC_A.length - 1)}${Math.max(2, n - 1)}` };
      X.utils.book_append_sheet(wb, w, nombre);
    };
    detalle("Materiales", mat, false);

    // Materiales por familia (como armar_cotizacion.py): una lista debajo de la otra, precios por fórmula de la hoja Materiales
    {
      const wf = hoja(), filaMat = new Map(mat.map((it, k) => [it, k + 2])), EQ = { igual: "Igual", similar: "Similar", sin_ref: "No encontrado" };
      const HF2 = { font: { bold: true, color: { rgb: "FFFFFF" } }, fill: { fgColor: { rgb: "1D5F86" } } };
      let r = 1; const subt = [];
      put(wf, "A1", `MATERIALES POR FAMILIA · por ${eq.singular} · USD sin IVA (precios ajustados a hoy, de la hoja Materiales)`, { font: { bold: true, sz: 13 } });
      r = 3;
      Busqueda.GRUPOS.forEach(([nombre, , cols], g) => {
        const its = mat.filter(it => Busqueda.grupoDe(it) === g); if (!its.length) return;
        const izq = ["Ítem", /ITT/.test(of?.titulo_materiales || "") ? "Descripción (lista de ITT)" : "Descripción (lista del cliente)", ...cols.map(k => Busqueda.ETIQUETAS[k]), "Cantidad", "Unidad"];
        const der = ["Equivalencia encontrada", "Precio ajustado a hoy USD", "Subtotal USD", "Fecha del último precio", "Antecedente", "Descripción del reemplazo", "Diferencias"];
        for (let j = 1; j <= izq.length + der.length; j++) put(wf, A(j, r), j === 1 ? nombre.toUpperCase() : j === izq.length + 1 ? "DATOS ENCONTRADOS" : "", HF2);
        r++;
        [...izq, ...der].forEach((t, j) => put(wf, A(j + 1, r), t, { font: { bold: true }, alignment: { wrapText: true }, fill: { fgColor: { rgb: j < izq.length ? "DDF1E4" : "E8E1F3" } } }));
        r++; const r0 = r, n = izq.length;
        for (const it of its) {
          const at = Busqueda.atributosDe(it), s = it.fuentes[0], i = filaMat.get(it), [, ant] = filaDatos(it);
          const eqv = !s.precio || s.coincide === "sin_ref" ? "No encontrado" : EQ[s.coincide] || "";
          [it.pos, it.descripcion, ...cols.map(k => at[k] || ""), Number(it.cantidad), it.unidad].forEach((v, j) => put(wf, A(j + 1, r), v));
          put(wf, A(n + 1, r), eqv, { fill: { fgColor: { rgb: { Igual: "DDF1E4", Similar: "FBEFD6" }[eqv] || "F8E1DE" } } });
          put(wf, A(n + 2, r), { f: `Materiales!O${i}` }, null, U); put(wf, A(n + 3, r), { f: `Materiales!P${i}` }, null, U);
          put(wf, A(n + 4, r), serial(s.fecha), null, "dd-mm-yyyy"); put(wf, A(n + 5, r), (ant[0] ? ant[0] + " · " : "") + (s.proveedor || ""));
          put(wf, A(n + 6, r), ant[1]); put(wf, A(n + 7, r), s.diferencia || "");
          r++;
        }
        const col = X.utils.encode_col(n + 2);
        put(wf, A(2, r), `Subtotal ${nombre.split(" (")[0].toLowerCase()}`, TOT); put(wf, A(n + 3, r), { f: `SUM(${col}${r0}:${col}${r - 1})` }, TOT, U);
        subt.push([nombre.split(" (")[0], `'Materiales por familia'!${col}${r}`]);
        r += 3;
      });
      put(wf, A(2, r), `TOTAL MATERIALES por ${eq.singular} (sin contingencia; igual a la hoja Materiales)`, AZ);
      put(wf, A(4, r), subt.length ? { f: subt.map(x => x[1]).join("+") } : 0, AZ, U);
      wf["!cols"] = [{ wch: 6 }, { wch: 46 }, ...Array(23).fill({ wch: 14 })];
      X.utils.book_append_sheet(wb, wf, "Materiales por familia");
      wb.SheetNames.splice(wb.SheetNames.indexOf("Materiales por familia"), 1); wb.SheetNames.splice(1, 0, "Materiales por familia");
      put(ws, "G22", `COSTO DE MATERIALES POR FAMILIA (por ${eq.singular}, ajustado a hoy, sin contingencia)`, { font: { bold: true } });
      subt.forEach(([nombre, ref], k) => { put(ws, A(7, 23 + k), nombre); put(ws, A(8, 23 + k), { f: ref }, null, U); });
    }
    detalle("MO y servicios", srv, true);

    const x = hoja();
    cabecera(x, ["Mes", "IPC Argentina (oct-24=100)", "Dólar BNA vendedor (promedio)", "Costo local en USD (IPC/dólar, oct-24=100)", "CPI EE.UU. (oct-24=100)", "Origen IPC", "Origen dólar", "Origen CPI"],
      [11, 13, 12, 16, 12, 40, 40, 40]);
    idx.forEach((r, k) => {
      const i = k + 2;
      put(x, A(1, i), serial(r.mes + "-01"), null, "mm-yyyy"); put(x, A(2, i), r.ipc, null, "#,##0.0##"); put(x, A(3, i), r.dolar, null, "#,##0.00");
      put(x, A(4, i), r.local, null, "#,##0.0##"); put(x, A(5, i), r.cpi, null, "#,##0.0##"); put(x, A(6, i), r.oi); put(x, A(7, i), r.od); put(x, A(8, i), r.oc);
    });
    X.utils.book_append_sheet(wb, x, "Índices");
    if ((cot.desvios || []).length) {
      const d = hoja(); cabecera(d, ["Pos", "Desvío", "Detalle"], [16, 50, 80]);
      cot.desvios.forEach((dv, k) => { put(d, A(1, k + 2), sinHtml(dv.tag)); put(d, A(2, k + 2), sinHtml(dv.titulo)); put(d, A(3, k + 2), sinHtml(dv.texto)); });
      X.utils.book_append_sheet(wb, d, "Desvíos");
    }
    planillaItt(X, wb, cot, of || {}, mat, srv, { put, A, hoja, serial, U, filaDatos });
    return new Blob([X.write(wb, { type: "array", bookType: "xlsx" })], { type: "application/octet-stream" });
  }

  // ------------------------------------------------------------------ hoja "Planilla ITT" (herramientas/planilla_itt.py)
  // Distribución de la planilla base de ITT que lee la dirección (Matías, 03-11-2026): encabezado, cuadro de rentabilidad,
  // plazo y entrega, alcance SI/NO, material principal y END, y un bloque por rubro. Los números salen por fórmula de las
  // hojas Materiales, "MO y servicios" y Cotización (mismo total que siempre).
  const BLOQUES = ["Recipiente", "Piping", "Skid", "Plataforma / escaleras", "Válvulas manuales", "Instrumental", "Instalación eléctrica",
    "Aislación", "Tracing eléctrico", "Otros materiales", "Mano de obra de 3ros", "Mano de obra ITT", "Granallado y pintura",
    "Ensayos no destructivos", "Embalaje", "Transporte a destino final", "Seguro de Caución", "Otros servicios"];
  const INSTR = /^(sensor|transmisor|presion regulada|temperatura|switch|interruptor|manometro|termometro|termovaina|indicador|toma multiport|regulador y filtro|tubing|conector)|\bdoble virola\b|\binstrumento/;
  const RECIP = /filtro|separador|recipiente|tanque|calentador|trampa|coalesc|depurador|scrubber|slug/;
  function bloqueDe(it, cot) {
    const n = Busqueda.norm, d = n(it.descripcion || "");
    if (it.grupo === "material") {
      if (/aislac/.test(d)) return "Aislación";
      if (/tracing|traceado/.test(d)) return "Tracing eléctrico";
      if (/\bcable|bandeja portacable|conduit|prensacable|caja de paso|luminaria|instalacion electrica/.test(d)) return "Instalación eléctrica";
      if (/escalera|plataforma|baranda|rejilla|guarda ?hombre|pasarela/.test(d)) return "Plataforma / escaleras";
      if (INSTR.test(d)) return "Instrumental";
      if (/^valv/.test(d)) return "Válvulas manuales";
      const g = Busqueda.grupoDe(it), e = cot.equipo || {};
      if (g === 0) return "Válvulas manuales";
      if ([1, 2, 6].includes(g)) return "Piping";
      if (g === 5) return "Instrumental";
      if (g === 3) return "Skid";
      if (RECIP.test(n(`${e.tipo || ""} ${e.singular || ""}`)) && (g === 4 || g === 7) && !/\bskid\b|soporte|pollera|patas/.test(d)) return "Recipiente";
      if (g === 4 || /\bskid\b|soporte|estructura|bastidor|pollera|patas/.test(d)) return "Skid";
      return "Otros materiales";
    }
    const t = n(`${it.descripcion || ""} ${it.fuentes[0].proveedor || ""}`);
    if (/caucion|seguro/.test(t)) return "Seguro de Caución";
    if (/embalaje/.test(t)) return "Embalaje";
    if (/galvaniz/.test(t)) return "Granallado y pintura";
    if (/rolado|cilindrado|plegado/.test(t)) return "Mano de obra de 3ros";
    if (/prueba de fugas|horas de planta/.test(t)) return "Mano de obra ITT";
    const r = typeof Rubros !== "undefined" ? Rubros.rubroDe(it) : null;
    if (r === "procedimientos" && /radiograf|penetrant|\brx\b|\blp\b|ultrason/.test(t)) return "Ensayos no destructivos";
    if (r === "horas" || r === "ph" || (it.grupo === "mo" && /propi|\bitt\b/.test(t))) return "Mano de obra ITT";
    if (r === "pintura") return "Granallado y pintura";
    if (r === "end") return "Ensayos no destructivos";
    if (r === "transporte") return "Transporte a destino final";
    if (r === "mo_piping" || r === "mo_estructura" || it.grupo === "mo") return "Mano de obra de 3ros";
    return "Otros servicios";
  }
  function bloquesDe(cot) {
    const out = new Map(), porPos = new Map();
    for (const it of cot.items) { out.set(it, bloqueDe(it, cot)); if (!porPos.has(String(it.pos ?? ""))) porPos.set(String(it.pos ?? ""), out.get(it)); }
    for (const it of cot.items) {
      const m = String(it.pos ?? "").match(/^(\d+)[a-z]$/);
      if (m && porPos.has(m[1]) && /completar|sobrante|compra minima|tira|barra/.test(Busqueda.norm(it.descripcion || ""))) out.set(it, porPos.get(m[1]));
    }
    return out;
  }
  const ETQ = { diametro: "Ø", diametro2: "Ø2", serie: "serie", schedule: "sch", espesor_mm: "esp. mm", material: "", extremos: "", cara: "", norma: "",
    marca: "marca", modelo: "modelo", rango: "rango", trim: "trim", paso: "paso", costura: "", revestimiento: "", largo_mm: "largo mm", medida: "", designacion: "", conexion: "conexión" };
  const ampliada = it => { const at = it.atributos || {};
    return it.grupo === "material" && Object.keys(at).length ? [...(at.tipo ? [at.tipo] : []), ...Object.keys(ETQ).filter(k => at[k]).map(k => `${ETQ[k]} ${at[k]}`.trim())].join(" · ") : String(it.especificacion || ""); };
  function materialPrincipal(cot, b) {
    const out = [], fam = it => (it.atributos || {}).familia;
    for (const [n, c] of [["Caños", it => Busqueda.grupoDe(it) === 2], ["Accesorios", it => ["ABW", "AFO"].includes(fam(it))], ["Bridas", it => fam(it) === "BRI"],
      ["Válvulas", it => b.get(it) === "Válvulas manuales"], ["Recipiente", it => b.get(it) === "Recipiente"]]) {
      const its = cot.items.filter(it => it.grupo === "material" && c(it) && (it.atributos || {}).material).sort((x, y) => y.cantidad * y.fuentes[0].precio - x.cantidad * x.fuentes[0].precio);
      if (its.length) out.push(`${n} ${its[0].atributos.material}`);
    }
    return out.join(", ");
  }
  function planillaItt(X, wb, cot, of, mat, srv, h) {
    const { put, A, hoja, serial, filaDatos } = h, p = cot.parametros, eq = cot.equipo || { singular: "equipo", plural: "equipos" };
    const ws = hoja(), b = bloquesDe(cot), CONT = '_-* #,##0.00_-;\\-* #,##0.00_-;_-* "-"??_-;_-@_-';
    const fill = c => ({ fill: { fgColor: { rgb: c } } }), BT = { top: { style: "thin" }, bottom: { style: "thin" }, left: { style: "thin" }, right: { style: "thin" } };
    const AN = (o = {}) => ({ font: { name: "Arial Narrow", sz: 11, ...o } });
    const merges = [];
    const datosP = Object.fromEntries((cot.pedido?.datos_html || []).map(x => [x[0], x[1]]));
    const enc = [["CLIENTE", cot.cliente?.nombre], ["PEDIDO DE PRECIOS", of.cliente?.referencia || cot.pedido?.eyebrow], ["REFERENCIA", of.cliente?.proyecto || cot.titulo],
      ["PRESUPUESTO", [`${cot.codigo} ${cot.revision || ""}`.trim(), of.oferta?.numero].filter(Boolean).join(" · ")], ["ÍTEM", of.item?.item], ["NOMBRE", of.item?.descripcion || cot.titulo],
      ["CANTIDAD", `${p.N} ${p.N !== 1 ? eq.plural : eq.singular}`], ["FECHA RECEPCION PED COTIZACION", cot.fecha_recepcion], ["FECHA DE VENCIMIENTO DE COTIZACION", cot.fecha_vencimiento],
      ["PLANO / ER", cot.plano || datosP.Documento || datosP.Documentos]];
    enc.forEach(([k, v], i) => {
      const r = i + 1; v = sinHtml(v ?? "");
      put(ws, A(1, r), k, { font: { name: "Arial", sz: 10 }, alignment: { horizontal: "center", vertical: "center" }, border: BT });
      const f = /^\d{4}-\d{2}-\d{2}$/.test(v);
      put(ws, A(2, r), f ? serial(v) : v, { font: { name: "Arial", sz: 12, bold: true }, alignment: { horizontal: "center", vertical: "center", wrapText: true }, border: BT }, f ? "dd-mm-yyyy" : undefined);
      for (let j = 3; j <= 8; j++) put(ws, A(j, r), "", { border: BT });
      merges.push({ s: { r: r - 1, c: 1 }, e: { r: r - 1, c: 7 } });
    });
    const filaMat = new Map(mat.map((it, k) => [it, k + 2])), filaSrv = new Map(srv.map((it, k) => [it, k + 2]));
    const activos = BLOQUES.filter(n => cot.items.some(it => b.get(it) === n));
    const nFilas = 5 + (p.FM === p.FMO ? 0 : 1) + (p.TRANS ? 1 : 0);
    const rTot = 15 + nFilas, rt = rTot + 2, rp = rt + 3, ra = rp + 4;
    let r = ra + 1 + BLOQUES.length + 5;
    const sub = {}, EQV = { igual: "Igual", similar: "Similar", sin_ref: "No encontrado" };
    for (const nombre of activos) {
      const its = [...mat, ...srv].filter(it => b.get(it) === nombre);
      put(ws, A(1, r), nombre, { font: { name: "Arial", sz: 12, bold: true }, ...fill("BFBFBF") }); put(ws, A(2, r), "SI", { font: { name: "Arial", sz: 10 } });
      r++;
      ["Descripción", "Descripción ampliada", "Cantidad", "Unid", "USD/un", "Subt USD", "Posición", "Proveedor / antecedente", "Equivalencia", "Fecha del precio"]
        .forEach((t, j) => put(ws, A(j + 1, r), t, { font: { name: "Arial", sz: 10 }, ...fill(j < 7 ? "D9D9D9" : "E8E1F3"), alignment: { horizontal: "center" }, border: BT }));
      r++; const r0 = r;
      for (const it of its) {
        const s = it.fuentes[0], esM = it.grupo === "material", hj = esM ? "Materiales" : "'MO y servicios'", i = esM ? filaMat.get(it) : filaSrv.get(it);
        const ant = esM ? filaDatos(it)[1] : ["", ""];
        const eqv = !s.precio || s.coincide === "sin_ref" ? "No encontrado" : EQV[s.coincide] || "";
        const st = { font: { name: "Calibri", sz: 11 }, border: BT, alignment: { vertical: "center", wrapText: true } };
        put(ws, A(1, r), it.descripcion, st); put(ws, A(2, r), ampliada(it), st);
        put(ws, A(3, r), Number(it.cantidad), { ...st, alignment: { horizontal: "center" } }, Number.isInteger(Number(it.cantidad)) ? "#,##0" : "#,##0.00##");
        put(ws, A(4, r), it.unidad, { ...st, alignment: { horizontal: "center" } });
        put(ws, A(5, r), { f: `${hj}!O${i}` }, st, CONT); put(ws, A(6, r), { f: `${hj}!P${i}` }, st, CONT);
        put(ws, A(7, r), String(it.pos ?? ""), { ...st, alignment: { horizontal: "center" } });
        put(ws, A(8, r), (ant[0] ? ant[0] + " · " : "") + (s.proveedor || ""), st);
        put(ws, A(9, r), eqv, { ...st, ...fill({ Igual: "DDF1E4", Similar: "FBEFD6" }[eqv] || "F8E1DE"), alignment: { horizontal: "center" } });
        put(ws, A(10, r), s.fecha ? serial(s.fecha) : "", { ...st, alignment: { horizontal: "center" } }, "dd-mm-yyyy");
        r++;
      }
      put(ws, A(6, r), { f: `SUM(F${r0}:F${r - 1})` }, { font: { name: "Calibri", sz: 11, bold: true }, ...fill("FFFF00"), border: BT }, CONT);
      sub[nombre] = `F${r}`; r += 3;
    }
    const ref = n => sub[n] || "0", C = "'Cotización'!";
    [["Detalle", ""], ["Cantidad", "Unidad"], ["Costo Unitario", "U$S"], ["Factor de Rentabilidad", ""], ["Precio de Venta Unitario", "U$S"], ["Precio de Venta unitario", "U$S"],
      ["Margen de ganancia", "%"], ["Precio de venta total", "U$S"]].forEach(([t1, t2], j) => {
      [[12, t1], [13, t2]].forEach(([rr, t]) => put(ws, A(j + 1, rr), t, { ...fill("FCD5B4"), border: BT, font: { name: "Arial Narrow", sz: j === 0 ? 16 : 11, bold: j === 0 }, alignment: { horizontal: "center", vertical: "center", wrapText: true } }));
    });
    merges.push({ s: { r: 11, c: 0 }, e: { r: 12, c: 0 } });
    const resto = `(${C}B21+${C}B22-${ref("Mano de obra de 3ros")}-${ref("Seguro de Caución")}-${ref("Transporte a destino final")})`;
    const filas = p.FM === p.FMO ? [["Materiales, MO y SVC", `${C}B5`, `${C}B18+${C}B19+${resto}`, `${C}B6`]]
      : [["Materiales (con contingencia)", `${C}B5`, `${C}B18+${C}B19`, `${C}B6`], ["MO ITT y servicios", `${C}B5`, resto, `${C}B7`]];
    filas.push(["Válvulas Taval", `${C}B5`, `${C}B20`, `${C}B14`], ["Mano de obra de terceros", `${C}B5`, ref("Mano de obra de 3ros"), `${C}B7`],
      ["Seguro de caución", `${C}B5`, ref("Seguro de Caución"), `${C}B7`], ["Transporte", `${C}B5`, ref("Transporte a destino final"), `${C}B7`]);
    if (p.TRANS) filas.push(["Flete y embalaje (por envío)", 1, `${C}E23`, 1]);
    filas.forEach(([n, cant, costo, fac], k) => {
      const rr = 15 + k, st = { ...AN(), border: BT };
      put(ws, A(1, rr), n, { ...st, alignment: { horizontal: "right" } });
      put(ws, A(2, rr), typeof cant === "number" ? cant : { f: cant }, { ...st, alignment: { horizontal: "center" } }, "0");
      put(ws, A(3, rr), { f: costo }, st, "#,##0.00");
      put(ws, A(4, rr), typeof fac === "number" ? fac : { f: fac }, { ...st, ...fill("FFFF00"), alignment: { horizontal: "center" } }, "0.00");
      put(ws, A(5, rr), { f: `C${rr}*D${rr}` }, st, CONT); put(ws, A(6, rr), { f: `E${rr}` }, st, CONT);
      put(ws, A(7, rr), { f: `IFERROR((E${rr}-C${rr})/E${rr},0)` }, st, "0.0%"); put(ws, A(8, rr), { f: `F${rr}*B${rr}` }, st, "#,##0.00");
    });
    const kUlt = 14 + filas.length, unit = filas.map((_, k) => 15 + k).filter(k => !(p.TRANS && k === kUlt)), rT = kUlt + 1;
    put(ws, A(2, rT), "Total", { ...AN({ bold: true }), border: BT });
    put(ws, A(3, rT), { f: unit.map(k => `C${k}`).join("+") }, { ...AN({ bold: true }), border: BT, ...fill("DDEBF7") }, "#,##0.00");
    put(ws, A(6, rT), { f: unit.map(k => `F${k}`).join("+") }, { ...AN({ bold: true }), border: BT, ...fill("FFFF00") }, CONT);
    put(ws, A(8, rT), { f: `SUM(H15:H${kUlt})` }, { ...AN({ bold: true }), border: BT, ...fill("FFFF00") }, "#,##0.00");
    put(ws, A(7, rT + 1), { f: `IFERROR((F${rT}-C${rT})/F${rT},0)` }, null, "0.0%");
    const BM = { top: { style: "medium" }, bottom: { style: "medium" }, left: { style: "medium" }, right: { style: "medium" } };
    put(ws, A(6, rT + 2), "Total U$D", { ...AN({ sz: 18, bold: true }), ...fill("FFFF00"), alignment: { horizontal: "center" }, border: BM }); put(ws, A(7, rT + 2), "", { ...fill("FFFF00"), border: BM });
    merges.push({ s: { r: rT + 1, c: 5 }, e: { r: rT + 1, c: 6 } });
    put(ws, A(8, rT + 2), { f: `${C}E28` }, { ...AN({ sz: 18, bold: true }), ...fill("FFFF00"), alignment: { horizontal: "center" }, border: BM }, "#,##0.00");
    put(ws, A(6, rT + 3), "Precio unitario de la oferta (redondeado):", AN({ sz: 10, italic: true })); put(ws, A(8, rT + 3), { f: `${C}D27` }, AN({ sz: 10, italic: true }), "#,##0.00");
    const pz = cot.plazo || {}, entrega = p.TRANS ? cot.flete?.etiqueta || "" : "EXW, ITT SA, Av. 12 de Octubre 4004, Quilmes Oeste, AMBA.";
    [[rp, `Plazo de entrega : ${pz.dias ?? ""} días ${pz.texto || ""}`.trim()], [rp + 1, `Entrega: ${entrega}`]].forEach(([rr, t]) => {
      for (let j = 1; j <= 8; j++) put(ws, A(j, rr), j === 1 ? t : "", { ...AN({ sz: 14, bold: true }), ...fill("FCD5B4") });
      merges.push({ s: { r: rr - 1, c: 0 }, e: { r: rr - 1, c: 7 } });
    });
    put(ws, A(1, ra), "MATERIA PRIMA Y MATERIALES", { font: { name: "Arial", sz: 12, bold: true }, ...fill("BFBFBF") });
    BLOQUES.forEach((n, k) => {
      const rr = ra + 1 + k, si = activos.includes(n);
      put(ws, A(1, rr), n, { font: { name: "Arial", sz: 12 }, alignment: { horizontal: "center" } });
      put(ws, A(2, rr), si ? "SI" : "NO", { font: { name: "Arial", sz: 10 }, ...(si ? fill("FCD5B4") : {}) });
      if (si) { put(ws, A(3, rr), { f: ref(n) }, fill("FCD5B4"), CONT); put(ws, A(4, rr), "", fill("FCD5B4")); }
      if (n === "Mano de obra ITT") put(ws, A(5, rr), "Ingeniería - Calidad - Movimientos internos, PH, armado final", { font: { name: "Arial", sz: 9 } });
    });
    const rm = ra + BLOQUES.length + 2, end = srv.filter(it => b.get(it) === "Ensayos no destructivos").map(it => it.descripcion).join("; ");
    [["Material principal:", materialPrincipal(cot, b)], ["END", end || "Sin ensayos no destructivos"]].forEach(([k, v], i) => {
      put(ws, A(1, rm + i), k, { font: { name: "Calibri", sz: 14 } }); put(ws, A(2, rm + i), v, { font: { name: "Calibri", sz: 14, color: { rgb: "FF0000" } } });
    });
    ws["!merges"] = merges;
    ws["!cols"] = [43.5, 61.2, 13.7, 9, 16.8, 17.3, 13, 30, 16, 14].map(w => ({ wch: w }));
    X.utils.book_append_sheet(wb, ws, "Planilla ITT");
    wb.SheetNames.splice(wb.SheetNames.indexOf("Planilla ITT"), 1); wb.SheetNames.unshift("Planilla ITT");
  }

  // ------------------------------------------------------------------ Excel para Compras
  // Igual que herramientas/lista_compras.py (pedido de Matías, 28-10-2026): la lista TAL CUAL el documento de origen
  // (cot.transcripcion: tablas con sus columnas y su texto), a la derecha la cantidad a comprar calculada (m, kg o un),
  // los kg aproximados y de dónde sale la cantidad; después Proveedor, Precio, Plazo y Anotaciones para Compras.
  // Lo que se compra y no está en el documento va aparte; los precios de referencia, en otra hoja (uso interno).
  function compras(cot) {
    const X = XLSX, wb = X.utils.book_new(), N = Number(cot.parametros.N) || 1;
    const est = (rgb, bold, color) => ({ font: { bold: !!bold, color: { rgb: color || "000000" } }, fill: { fgColor: { rgb } }, alignment: { wrapText: true, vertical: "top" } });
    const AZ = est("1D5F86", true, "FFFFFF"), GR = est("5D6B75", true, "FFFFFF"), OC = est("B7791F", true, "FFFFFF"), CG = est("EEF3F6"), CA = est("FBEFD6");
    const mats = cot.items.filter(i => i.grupo === "material");
    const esTira = it => /^(completar|sobrante)/i.test(String(it.descripcion || "").trim());
    const kgU = cot.kg_compras || {};
    const eqTxt = N === 1 ? (cot.equipo?.singular || "equipo") : (cot.equipo?.plural || "equipos");
    const tr = cot.transcripcion || { fuente: "Cotización de la página (no hay transcripción literal del documento)", tablas: [{
      titulo: "LISTA DE MATERIALES", columnas: ["Pos", "Descripción", "Ø", "Serie / SCH", "Material", "Marca / modelo", "Cant.", "Unidad"],
      filas: mats.filter(i => !esTira(i) && !/[a-z]$/i.test(String(i.pos))).map(i => { const p = i.plano || {};
        return [i.pos, p.descripcion || i.descripcion, p.diametro || "", p.serie_sch || "", p.material || "", p.modelo || "", i.cantidad, i.unidad]; }) }] };
    const enDoc = new Set(tr.tablas.flatMap(t => t.filas.map(f => String(f[0]).trim())));
    const filas = [[`PEDIDO DE COTIZACIÓN DE MATERIALES · ${cot.codigo}`], [`${cot.titulo || ""} · ${N} ${eqTxt}`], ["Origen de la lista", tr.fuente]];
    const estilos = {};
    const marca = (r, c, s) => { estilos[X.utils.encode_cell({ r, c })] = s; };
    // Números como celdas numéricas, nunca texto (Matías, 29-10-2026). Del documento se convierte solo lo que es un
    // número sin ambigüedad (numeroDe: 1.500 · 12,5); Pos/ID/código quedan como texto. Formato según la columna.
    const CLAVE = /^(pos|id|c[oó]d|art)/i;
    const docNum = (v, col) => typeof v === "string" && !CLAVE.test(col) && numeroDe(v) != null ? numeroDe(v) : v;
    const zDe = (col, v) => /precio|usd/i.test(col) ? "#,##0.00" : /serie|sch|clase/i.test(col) && Number.isInteger(v) ? "0" : Number.isInteger(v) ? "#,##0" : "#,##0.0###";
    const formatos = {};
    const fila = (vals, cab, r) => vals.map((v, c) => { const x = c < cab.length ? docNum(v, cab[c]) : v;
      if (typeof x === "number") formatos[X.utils.encode_cell({ r, c })] = zDe(cab[c] || "", x); return x; });
    let kgTot = 0;
    for (const t of tr.tablas) {
      filas.push([], [t.titulo]);
      const cab = [...t.columnas, "Cant. a comprar", "Unidad", "Kg aprox.", "Origen de la cantidad", "Proveedor", "Precio unit. USD", "Plazo", "Anotaciones"];
      const rc = filas.length; filas.push(cab);
      cab.forEach((_, c) => marca(rc, c, c < t.columnas.length ? AZ : c < t.columnas.length + 4 ? GR : OC));
      for (const f of t.filas) {
        const pos = String(f[0]).trim(), its = mats.filter(i => String(i.pos).trim() === pos);
        const extras = mats.filter(i => esTira(i) && new RegExp("^" + pos.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + "[b-z]$").test(String(i.pos).trim()));
        let calc = ["—", "", "", "no se cotiza"];
        if (its.length) {
          const q = its.reduce((a, i) => a + Number(i.cantidad), 0) * N, qe = extras.reduce((a, i) => a + Number(i.cantidad), 0) * N, u = its[0].unidad;
          const k = kgU[pos] != null ? Math.round(kgU[pos] * (q + qe) * 10) / 10 : "—";
          if (typeof k === "number") kgTot += k;
          const desc = its[0].plano?.descripcion || "";
          calc = [Math.round((q + qe) * 1000) / 1000, u, k, qe ? `${numg(q)} ${u} para ${numg(N)} ${eqTxt} + ${numg(qe)} ${u} para completar la tira`
            : /medida del dibujo|no indica/i.test(desc) ? "el documento no da cantidad: medida del dibujo (±20%)" : N === 1 ? "documento" : `documento × ${numg(N)}`];
        }
        const r = filas.length; filas.push(fila([...f, ...calc, "", "", "", ""], cab, r));
        for (let c = t.columnas.length; c < t.columnas.length + 8; c++) marca(r, c, c < t.columnas.length + 4 ? CG : CA);
      }
    }
    if (tr.nota) filas.push(["", "Nota del documento: " + tr.nota]);
    const adic = mats.filter(i => !enDoc.has(String(i.pos).trim()) && !esTira(i));
    if (adic.length) {
      filas.push([], ["ADICIONALES (no figuran en el documento; los agrega ITT)"]);
      const cab = ["Pos", "Descripción", "Especificación", "Cant. a comprar", "Unidad", "Kg aprox.", "Por qué", "Proveedor", "Precio unit. USD", "Plazo", "Anotaciones"];
      const rc = filas.length; filas.push(cab); cab.forEach((_, c) => marca(rc, c, c < 7 ? GR : OC));
      for (const i of adic) { const r = filas.length; filas.push(fila([i.pos, i.descripcion, i.especificacion || "", Number(i.cantidad) * N, i.unidad, "—", "compra mínima o nota del documento", "", "", "", ""], cab, r));
        for (let c = 7; c < 11; c++) marca(r, c, CA); }
    }
    filas.push([], [`Peso aproximado de lo que tiene tabla: ${num(kgTot, 0)} kg`],
      ["Columnas azules: tal cual el documento. Grises: cálculo de ITT. Amarillas: para que Compras complete (proveedor, precio sin IVA, plazo y anotaciones)."]);
    const ws = X.utils.aoa_to_sheet(filas);
    for (const [a, s] of Object.entries(estilos)) { ws[a] = ws[a] || { t: "s", v: "" }; ws[a].s = s; }
    for (const [a, z] of Object.entries(formatos)) if (ws[a]) ws[a].z = z;
    ws.A1.s = { font: { bold: true, sz: 14, color: { rgb: "1D5F86" } } };
    ws["!cols"] = [6, 46, 9, 8, 8, 8, 20, 11, 8, 10, 30, 22, 13, 12, 45].map(w => ({ wch: w }));
    X.utils.book_append_sheet(wb, ws, "Materiales");
    const serv = cot.items.filter(i => i.grupo !== "material");
    const sv = X.utils.aoa_to_sheet([["Servicio", "Aclaraciones", "Proveedor", "Precio unit. USD", "Plazo", "Anotaciones"], ...serv.map(i => [i.descripcion, i.especificacion || "", "", "", "", ""])]);
    sv["!cols"] = [50, 45, 22, 13, 12, 45].map(w => ({ wch: w }));
    X.utils.book_append_sheet(wb, sv, "Servicios");
    const ref = X.utils.aoa_to_sheet([["Pos", "Descripción", "Proveedor de referencia", "Último precio USD", "Fecha", "Tipo", "Coincide", "Diferencia"],
      ...cot.items.map(i => { const s = i.fuentes[0]; return [i.pos, i.descripcion, s.proveedor, Number(s.precio) || "SIN PRECIO", fecha(s.fecha), TIPOS[s.tipo] || s.tipo, COINC[s.coincide] || s.coincide || "", s.diferencia || ""]; }),
      [], ["Uso interno: no mandar al proveedor."]]);
    cot.items.forEach((i, k) => { const c = ref[X.utils.encode_cell({ r: k + 1, c: 3 })]; if (c && c.t === "n") c.z = "#,##0.00"; });
    ref["!cols"] = [7, 45, 40, 13, 11, 12, 12, 50].map(w => ({ wch: w }));
    X.utils.book_append_sheet(wb, ref, "Referencias internas");
    return new Blob([X.write(wb, { type: "array", bookType: "xlsx" })], { type: "application/octet-stream" });
  }

  // ------------------------------------------------------------------ PDF desde HTML (html2pdf)
  async function pdfDeHtml(html) {
    const caja = document.createElement("div");
    caja.style.cssText = "position:fixed;left:-10000px;top:0;width:718px;background:#fff;color:#1b2730";
    caja.innerHTML = html;
    document.body.appendChild(caja);
    try {
      return await html2pdf().set({
        margin: [10, 10, 12, 10], image: { type: "jpeg", quality: 0.95 }, html2canvas: { scale: 2, useCORS: true, backgroundColor: "#ffffff" },
        jsPDF: { unit: "mm", format: "a4", orientation: "portrait" }, pagebreak: { mode: ["css", "legacy"], avoid: ["tr", ".nobreak"] }
      }).from(caja.firstElementChild).outputPdf("blob");
    } finally { caja.remove(); }
  }

  const CSS_PDF = `<style>
    .doc{font:10.5px/1.45 Arial,Helvetica,sans-serif;color:#1b2730;width:718px;box-sizing:border-box}
    .doc h1{font:700 19px Arial;margin:0}.doc h2{font:700 13px Arial;margin:14px 0 6px;border-bottom:1.5px solid #1b2730;padding-bottom:3px}
    .doc table{border-collapse:collapse;width:100%;font-size:9px}.doc th{background:#1d5f86;color:#fff;text-align:left;padding:4px;font-weight:700}
    .doc td{border-bottom:1px solid #d5dde2;padding:3px 4px;vertical-align:top}.doc td.n,.doc th.n{text-align:right;white-space:nowrap}
    .doc .muted{color:#5d6b75}.doc .marca{border:2px solid #a3392f;color:#a3392f;font-weight:700;padding:4px 8px;display:inline-block;letter-spacing:.05em}
    .doc .tot{display:flex;gap:0;border:1px solid #d5dde2;margin:8px 0}.doc .tot div{flex:1;padding:6px 8px;border-right:1px solid #d5dde2}.doc .tot div:last-child{border-right:0}
    .doc .tot b{display:block;font-size:14px}.doc .pill{font-size:8.5px;padding:1px 4px;border-radius:2px}
    .doc .ok{background:#ddf1e4}.doc .warn{background:#fbefd6}.doc .bad{background:#f8e1de}
    .doc .cab{display:flex;justify-content:space-between;align-items:flex-end;border-bottom:3px solid #1b2730;padding-bottom:8px;gap:12px}
    .doc .firma{margin-top:18px;display:flex;flex-direction:column;gap:2px}.doc .firma img{max-height:60px;max-width:180px}
    .doc .of-caja{background:#002060;color:#fff;padding:10px 12px;margin:10px 0}.doc .of-caja b{font-size:15px}
    .doc .of h2{color:#002060;border-color:#002060}.doc .of td,.doc .of p,.doc .of li{color:#002060}.doc .of th{background:#002060}
    .doc ul{margin:4px 0 4px 18px;padding:0}.doc p{margin:4px 0}
  </style>`;

  function informeHtml(ctx) {
    const { cot, calc, avisos, firmante, firmaUrl, logo, plazo } = ctx;
    const eq = cot.equipo || { singular: "equipo", plural: "equipos" };
    const marca = ["revisado", "aprobado", "enviado"].includes(cot.estado) ? "" : `<span class="marca">BORRADOR, SIN REVISAR</span>`;
    const fila = it => {
      const s = it.fuentes[0], f = calc.filas.find(x => x.id === it.id) || { ajustado: it.cantidad * s.precio, factor: 1 };
      const cl = s.coincide === "igual" ? "ok" : s.coincide === "similar" ? "warn" : "bad";
      return `<tr><td>${esc(it.pos)}</td><td><b>${esc(it.descripcion)}</b><br><span class="muted">${esc(it.especificacion || "")}</span></td>
        <td class="n">${num(it.cantidad, it.cantidad % 1 ? 2 : 0)} ${esc(it.unidad)}</td><td class="n">${num(s.precio)}</td><td class="n">${num(f.factor, 2)}</td><td class="n">${num(f.ajustado)}</td>
        <td>${esc(TIPOS[s.tipo] || s.tipo)} · ${esc(s.proveedor)}<br><span class="muted">${esc(s.origen || "")} · ${esc(fecha(s.fecha))}</span></td>
        <td><span class="pill ${cl}">${COINC[s.coincide] || ""}</span>${s.diferencia ? "<br><span class='muted'>" + esc(s.diferencia) + "</span>" : ""}</td></tr>`;
    };
    const tabla = items => `<table><thead><tr><th>Pos</th><th>Ítem</th><th class="n">Cant.</th><th class="n">USD unit.</th><th class="n">Ajuste</th><th class="n">USD ajustado</th><th>Fuente y fecha</th><th>Coincidencia</th></tr></thead><tbody>${items.map(fila).join("")}</tbody></table>`;
    const p = cot.parametros;
    return `<div class="doc">${CSS_PDF}
      <div class="cab"><div><img src="${logo}" style="height:42px"><h1>${esc(cot.codigo)} ${esc(cot.revision || "")}</h1><div>${esc(cot.titulo || "")}</div>
        <div class="muted">Cliente: ${esc(cot.cliente?.nombre || "")} · Comprador: ${esc(cot.cliente?.comprador || "")} · Fecha de referencia: ${esc(fecha(p.fecha_referencia))} · Estado: ${esc(cot.estado)}</div></div><div>${marca}</div></div>
      <h2>Resumen (USD sin IVA)</h2>
      <div class="tot"><div>Costo / ${esc(eq.singular)}<b>${usd(calc.costo)}</b></div><div>Precio unitario<b>${usd(calc.precio_unitario)}</b></div>
        <div>Cantidad<b>${num(p.N, 0)} ${esc(eq.plural)}</b></div><div>Total de la oferta<b>${usd(calc.total)}</b></div></div>
      <table><tbody>
        <tr><td>Materiales (con ajuste por inflación)</td><td class="n">${usd(calc.sub.material)}</td><td class="n">factor ${num(p.FM)}</td></tr>
        <tr><td>Contingencia ${numg(p.CONT)}%</td><td class="n">${usd(calc.cont)}</td><td class="n">factor ${num(p.FM)}</td></tr>
        ${calc.tav ? `<tr><td>Válvulas Taval (con contingencia)</td><td class="n">${usd(calc.tav)}</td><td class="n">factor ${num(calc.ftv)}</td></tr>` : ""}
        <tr><td>Mano de obra</td><td class="n">${usd(calc.sub.mo)}</td><td class="n">factor ${num(p.FMO)}</td></tr>
        <tr><td>Servicios e insumos</td><td class="n">${usd(calc.sub.servicio)}</td><td class="n">factor ${num(p.FMO)}</td></tr>
        ${transporteIncluido(cot) ? `<tr><td>Transporte${cot.transporte?.destino ? " a " + esc(cot.transporte.destino) : ""} (en servicios, por ${esc(eq.singular)})</td><td class="n">${usd(transporteIncluido(cot).precio)}</td><td class="n">incluido en el precio</td></tr>` : ""}
        <tr><td>Flete + embalaje (por envío)</td><td class="n">${usd(calc.flete)}</td><td class="n">${p.TRANS ? "incluido" : transporteIncluido(cot) ? "no se usa" : "no incluido (EXW Quilmes Oeste)"}</td></tr>
        <tr><td>Ajuste por inflación incluido</td><td class="n">${usd(calc.costo - calc.costo0)}</td><td class="n">${p.AJ ? "aplicado hasta " + esc(fecha(p.fecha_referencia)) : "sin ajuste"}</td></tr>
      </tbody></table>
      <h2>Materiales</h2>${tabla(cot.items.filter(i => i.grupo === "material"))}
      <h2>Mano de obra y servicios</h2>${tabla(cot.items.filter(i => i.grupo !== "material"))}
      ${plazo ? `<h2>Plazo</h2><p>Plazo ofrecido: <b>${esc(cot.plazo?.dias ?? "—")} días</b>. ${esc(plazo.texto)}</p>` : ""}
      <h2>Avisos de control</h2>${avisos.length ? "<ul>" + avisos.map(a => `<li>${esc(a.txt)}</li>`).join("") + "</ul>" : "<p>Sin avisos.</p>"}
      <p class="muted">Precios sin IVA. Pesos convertidos con el promedio mensual del dólar oficial BNA venta. Materiales ajustados con el CPI de EE.UU.; mano de obra y servicios con el costo local en dólares (IPC ÷ dólar).</p>
      <div class="firma nobreak">Preparó: <b>${esc(firmante?.nombre || cot.preparo || "")}</b> ${esc(firmante?.cargo || "")}
        ${firmante?.telefono ? "<span>Tel.: " + esc(firmante.telefono) + "</span>" : ""}${firmante?.email ? "<span>" + esc(firmante.email) + "</span>" : ""}
        ${firmaUrl && cot.estado === "aprobado" ? `<img src="${firmaUrl}">` : ""}<span class="muted">Generado el ${fecha(new Date())}</span></div></div>`;
  }

  // ------------------------------------------------------------------ Ofertas (Word con la plantilla de ITT)
  const r_ = (texto, o = {}) => {
    const tam = Math.round((o.tam || 10) * 2), color = o.color || "002060";
    return `<w:r><w:rPr><w:rFonts w:ascii="Aptos" w:hAnsi="Aptos"/>${o.negrita ? "<w:b/>" : ""}${o.italica ? "<w:i/>" : ""}<w:color w:val="${color}"/><w:sz w:val="${tam}"/>${o.resaltar ? '<w:highlight w:val="yellow"/>' : ""}</w:rPr><w:t xml:space="preserve">${esc(texto)}</w:t></w:r>`;
  };
  const marcadores = (texto, o = {}) => String(texto ?? "").split(/(\[[^\]]+\])/).filter(Boolean).map(t => r_(t, { ...o, resaltar: t.startsWith("[") })).join("");
  const cm = v => Math.round(v * 567);

  function cuerpoOferta(tipo, ctx) {
    const { of, cot, calc, tituloXml, plano } = ctx;
    let x = "";
    const p = (runs, o = {}) => `<w:p><w:pPr>${o.keep ? "<w:keepNext/>" : ""}<w:spacing w:after="${o.after ?? 80}"/><w:ind w:left="${cm(o.sangria ?? 0.75)}"${o.colgante ? ` w:hanging="${cm(o.colgante)}"` : ""}/><w:jc w:val="${o.jc || "both"}"/></w:pPr>${runs}</w:p>`;
    const vacio = () => "<w:p/>";
    const titulo = t => {
      let xml = tituloXml.replace(/ w14:(paraId|textId)="[^"]*"/g, "");
      let primero = true;
      xml = xml.replace(/(<w:t(?: [^>]*)?>)([^<]*)(<\/w:t>)/g, (m, a, b, c) => { const v = primero ? esc(t) : ""; primero = false; return `<w:t xml:space="preserve">${v}</w:t>`; });
      xml = xml.replace("</w:pPr>", "<w:keepNext/></w:pPr>");
      return xml + p("", { keep: true, after: 0 });
    };
    const texto = (t, o = {}) => p(marcadores(t, { negrita: o.negrita }), { sangria: o.sangria ?? 0.75 });
    const vinetas = items => items.map(t => p(r_("•  ") + marcadores(t), { sangria: 1.25, colgante: 0.4, jc: "left", after: 40 })).join("");
    const tabla = (cab, filas, anchos, total, tam = 9, alinear) => {
      const borde = ["top", "left", "bottom", "right", "insideH", "insideV"].map(l => `<w:${l} w:val="single" w:sz="4" w:color="002060"/>`).join("");
      const celda = (t, w, o = {}) => `<w:tc><w:tcPr><w:tcW w:w="${cm(w)}" w:type="dxa"/>${o.span ? `<w:gridSpan w:val="${o.span}"/>` : ""}${o.cab ? '<w:shd w:val="clear" w:color="auto" w:fill="002060"/>' : ""}<w:vAlign w:val="center"/></w:tcPr><w:p><w:pPr><w:spacing w:after="0"/><w:jc w:val="${o.jc || "center"}"/></w:pPr>${marcadores(t, { negrita: o.cab || o.negrita, tam, color: o.cab ? "FFFFFF" : "002060" })}</w:p></w:tc>`;
      let t = `<w:tbl><w:tblPr><w:jc w:val="center"/><w:tblBorders>${borde}</w:tblBorders><w:tblLayout w:type="fixed"/></w:tblPr><w:tblGrid>${anchos.map(a => `<w:gridCol w:w="${cm(a)}"/>`).join("")}</w:tblGrid>`;
      t += `<w:tr>${cab.map((h, i) => celda(h, anchos[i], { cab: true })).join("")}</w:tr>`;
      for (const f of filas) t += `<w:tr>${f.map((v, i) => celda(v, anchos[i], { jc: (alinear || [])[i] === 0 ? "left" : "center" })).join("")}</w:tr>`;
      if (total) {
        const n = cab.length, span = n - 2;
        t += `<w:tr>${celda(total[0], anchos.slice(0, span).reduce((a, b) => a + b, 0), { span, negrita: true })}${celda(total[1], anchos[n - 2], { negrita: true })}${celda("", anchos[n - 1])}</w:tr>`;
      }
      return t + "</w:tbl>" + vacio();
    };
    x += `<w:p><w:r><w:br w:type="page"/></w:r></w:p>` + vacio() + vacio();
    const obj = (of.objeto || "").replace("{tipo}", tipo === "tecnica" ? "Técnica" : "Comercial");
    const it = of.item || {};
    const N = Number(cot.parametros.N);
    if (tipo === "economica") {
      x += titulo("OBJETO") + texto(obj) + titulo("PRECIO DE LA PROVISIÓN");
      x += tabla(["ITEM", "CÓDIGO", "DESCRIPCIÓN", "CANTIDAD", "USD UNIDAD", "USD SUBTOTAL", "Plazo de entrega (días)"],
        [[it.item, it.codigo, it.descripcion, String(N), usd(calc.precio_unitario), usd(calc.precio_unitario * N), it.plazo_dias],
         ...(calc.flete ? [["", "", of.descripcion_flete || "Flete y embalaje hasta destino", "1", usd(calc.flete), usd(calc.flete), ""]] : [])],
        [1.3, 3.1, 5.0, 2.1, 2.4, 2.6, 1.9], ["TOTAL (SIN IVA)", usd(calc.total)], 9, [1, 1, 0, 1, 1, 1, 1]);
      if (transporteIncluido(cot)) x += texto(notaTransporte(transporteIncluido(cot)));
      else if (!cot.parametros.TRANS && of.nota_flete) x += texto(of.nota_flete);
      for (const [tit, txt] of Object.entries(of.condiciones || {})) { x += titulo(tit); for (const l of [].concat(txt)) x += texto(l, { sangria: 1.25 }); }
      x += vacio();
    } else {
      x += titulo("OBJETO") + texto(obj) + titulo("ALCANCE");
      x += tabla(["ITEM", "CANTIDAD", "DESCRIPCIÓN", "OBSERVACIÓN / DESVÍO", "Plazo de entrega (días)"], [[it.item, String(N), it.descripcion, it.observacion, it.plazo_dias]],
        [1.4, 2.2, 7.2, 4.2, 2.2], null, 9, [1, 1, 0, 1, 1]);
      x += titulo("EMBALAJE") + texto(of.embalaje || "");
      x += titulo("DOCUMENTOS QUE FORMAN PARTE DE LA PROPUESTA") + vinetas([`${of.oferta.numero} – OFERTA TÉCNICA`, `${of.oferta.numero} – OFERTA ECONÓMICA`, ...(of.documentos_cliente || [])]);
      x += titulo("CARACTERÍSTICAS GENERALES SEGÚN PLANO") + texto(of.caracteristicas || "");
      if (ctx.planoXml) x += ctx.planoXml;
      x += titulo(of.titulo_materiales || `MATERIALES CONSIDERADOS (POR ${(cot.equipo?.singular || "equipo").toUpperCase()})`);
      x += tabla(["POS", "DESCRIPCIÓN", "Ø", "SERIE / SCH", "MATERIAL", "EXT.", "CANT."], plano, [1.0, 7.4, 1.6, 1.6, 3.3, 1.6, 1.1], null, 7.5, [1, 0, 1, 1, 1, 1, 1]);
      if (notaCantidades(cot)) x += texto(notaCantidades(cot));
      for (const k of ["aclaraciones_y_desvios", "exclusiones", "alcance_general"]) if (of[k]) x += titulo(of[k].titulo) + vinetas(of[k].items || []);
      x += titulo("GARANTÍA") + texto(of.garantia || "") + vacio();
    }
    return x;
  }

  function notaCantidades(cot) {
    const ps = cot.items.filter(i => i.grupo === "material" && i.plano?.cantidad_origen && !/b$|c$/.test(String(i.pos))).map(i => i.pos);
    return ps.length ? `(*) Pos. ${ps.join(", ")}: el cliente no indica cantidad; ITT la calculó según el plano / especificación técnica.` : "";
  }

  function filasPlano(cot) {
    return cot.items.filter(i => i.grupo === "material" && !/b$|c$/.test(String(i.pos))).map(i => {
      const pl = i.plano || {};
      // descripción del cliente tal cual (regla crítica, 29-10-2026); la cantidad que el cliente no indicó va con (*)
      return [i.pos, (pl.descripcion || i.descripcion) + (pl.modelo ? ` (${pl.modelo})` : ""), pl.diametro || "", pl.serie_sch || "", pl.material || "", pl.extremos || "", numg(i.cantidad) + (pl.cantidad_origen ? " (*)" : "")];
    });
  }

  function textoParrafo(pEl) { return Array.from(pEl.getElementsByTagNameNS(W, "t")).map(t => t.textContent).join(""); }
  function setTexto(pEl, texto) {
    const ts = Array.from(pEl.getElementsByTagNameNS(W, "t"));
    if (!ts.length) return;
    ts[0].textContent = texto; ts[0].setAttribute("xml:space", "preserve");
    ts.slice(1).forEach(t => (t.textContent = ""));
  }
  function reemplazar(raiz, mapa) {
    for (const pEl of Array.from(raiz.getElementsByTagNameNS(W, "p"))) {
      if (pEl.getElementsByTagNameNS(W, "p").length) continue;
      const txt = textoParrafo(pEl).trim();
      for (const [k, v] of Object.entries(mapa)) if (txt.startsWith(k)) { setTexto(pEl, v); break; }
    }
  }

  async function registrarImagen(zip, img, rid, nombre) {
    const ext = img.tipo === "image/png" ? "png" : "jpeg";
    zip.file(`word/media/${nombre}.${ext}`, img.bytes);
    let rels = await zip.file("word/_rels/document.xml.rels").async("string");
    rels = rels.replace("</Relationships>", `<Relationship Id="${rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/${nombre}.${ext}"/></Relationships>`);
    zip.file("word/_rels/document.xml.rels", rels);
    let ct = await zip.file("[Content_Types].xml").async("string");
    if (!ct.includes(`Extension="${ext}"`)) ct = ct.replace("<Default ", `<Default Extension="${ext}" ContentType="image/${ext}"/><Default `);
    zip.file("[Content_Types].xml", ct);
    return ext;
  }
  const dibujo = (rid, nombre, cx, cy, id) => `<w:r><w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0"><wp:extent cx="${cx}" cy="${cy}"/><wp:docPr id="${id}" name="${nombre}"/><a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:nvPicPr><pic:cNvPr id="${id}" name="${nombre}"/><pic:cNvPicPr/></pic:nvPicPr><pic:blipFill><a:blip r:embed="${rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill><pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="${cx}" cy="${cy}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r>`;

  async function ofertaDocx(tipo, ctx) {
    const { of, firmante, firma, datos } = ctx;
    const zip = await JSZip.loadAsync(datos["docx_" + tipo], { base64: true });
    const xml = await zip.file("word/document.xml").async("string");
    const doc = new DOMParser().parseFromString(xml, "application/xml");
    const body = doc.getElementsByTagNameNS(W, "body")[0];
    const titulo = tipo === "tecnica" ? "OFERTA TÉCNICA" : "OFERTA ECONÓMICA";
    const tbl = body.getElementsByTagNameNS(W, "tbl")[0];
    const celdas = Array.from(tbl.getElementsByTagNameNS(W, "tc"));
    const setCelda = (i, v) => { const pp = celdas[i].getElementsByTagNameNS(W, "p")[0]; if (pp) setTexto(pp, v); };
    setCelda(3, of.oferta.revision); setCelda(4, fecha(of.oferta.fecha)); setCelda(5, of.oferta.descripcion_revision);
    const cli = of.cliente || {};
    reemplazar(body, {
      "OFERTA ECONÓMICA": titulo,
      "Oferta:": `Oferta: ${of.oferta.numero}${" ".repeat(29)}Revisión ${of.oferta.revision}${" ".repeat(19)}Fecha ${fecha(of.oferta.fecha)}`,
      "Cliente:": `Cliente: ${cli.nombre || ""}`, "Contacto:": `Contacto: ${cli.contacto || ""}`, "Referencia:": `Referencia: ${cli.referencia || ""}`,
      "Proyecto:": `Proyecto: ${cli.proyecto || ""}`, "ITT S.A.:": `ITT S.A.: ${firmante?.nombre || ""}`,
      "Agradecemos su pedido": "Agradecemos su pedido y nos complace presentarles nuestra mejor propuesta " + (tipo === "tecnica" ? "Técnica" : "Económica") + " para la provisión de la referencia solicitada.",
      "Lucas Valdez": firmante?.nombre || "", "Representante": firmante?.cargo || ""
    });
    for (const pEl of Array.from(body.getElementsByTagNameNS(W, "p"))) {
      const ts = Array.from(pEl.getElementsByTagNameNS(W, "t")), txt = ts.map(t => t.textContent).join("");
      for (const [emoji, valor] of [["☎", firmante?.telefono], ["📱", firmante?.celular]]) {
        if (txt.startsWith(emoji) && ts.length > 1) {
          const i = ts.findIndex(t => !/[☎📱️]/u.test(t.textContent));
          if (i >= 0) { ts[i].textContent = `: ${valor || "[completar]"}`; ts.slice(i + 1).forEach(t => (t.textContent = "")); }
        }
      }
    }
    if (firma && ctx.aprobado) {
      // imagen de la firma, antes del nombre
      const destino = Array.from(body.getElementsByTagNameNS(W, "p")).find(pp => textoParrafo(pp).trim() === (firmante?.nombre || "").trim());
      if (destino) {
        const ext = await registrarImagen(zip, firma, "rIdFirma", "firma");
        const cx = 1440000, cy = Math.round(cx * firma.alto / firma.ancho);
        const frag = `<w:p xmlns:w="${W}" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">${dibujo("rIdFirma", "firma." + ext, cx, cy, 9001)}</w:p>`;
        const nodo = doc.importNode(new DOMParser().parseFromString(frag, "application/xml").documentElement, true);
        destino.parentNode.insertBefore(nodo, destino);
      }
    }
    let planoXml = "";
    if (tipo === "tecnica" && ctx.planoImg) {
      const ext = await registrarImagen(zip, ctx.planoImg, "rIdPlano", "plano");
      const cx = Math.round(15 * 360000), cy = Math.round(cx * ctx.planoImg.alto / ctx.planoImg.ancho);
      planoXml = `<w:p><w:pPr><w:jc w:val="center"/></w:pPr>${dibujo("rIdPlano", "plano." + ext, cx, cy, 9002)}</w:p>`;
    }
    let salida = new XMLSerializer().serializeToString(doc);
    salida = salida.replace("<w:p><w:r><w:t>{{CUERPO}}</w:t></w:r></w:p>", cuerpoOferta(tipo, { ...ctx, tituloXml: datos.docx_titulo, plano: filasPlano(ctx.cot), planoXml }));
    zip.file("word/document.xml", salida);
    if (!ctx.aprobado) {
      let h = await zip.file("word/header1.xml").async("string");
      h = h.replace("</w:hdr>", `<w:p><w:pPr><w:jc w:val="right"/></w:pPr>${r_("BORRADOR – SIN REVISAR – NO ENVIAR", { negrita: true, tam: 11, color: "C00000" })}</w:p></w:hdr>`);
      zip.file("word/header1.xml", h);
    }
    return zip.generateAsync({ type: "blob" });
  }

  function ofertaHtml(tipo, ctx) {
    const { of, cot, calc, firmante, firmaUrl, logo, aprobado } = ctx, it = of.item || {}, N = Number(cot.parametros.N), cli = of.cliente || {};
    let n = 0;
    const tit = t => `<h2>${++n}. ${esc(t)}</h2>`;
    const lis = a => `<ul>${(a || []).map(t => `<li>${esc(t)}</li>`).join("")}</ul>`;
    const obj = (of.objeto || "").replace("{tipo}", tipo === "tecnica" ? "Técnica" : "Comercial");
    let cuerpo = tit("OBJETO") + `<p>${esc(obj)}</p>`;
    if (tipo === "economica") {
      cuerpo += tit("PRECIO DE LA PROVISIÓN") + `<table><thead><tr><th>ITEM</th><th>CÓDIGO</th><th>DESCRIPCIÓN</th><th class="n">CANT.</th><th class="n">USD UNIDAD</th><th class="n">USD SUBTOTAL</th><th>Plazo (días)</th></tr></thead>
        <tbody><tr><td>${esc(it.item)}</td><td>${esc(it.codigo)}</td><td>${esc(it.descripcion)}</td><td class="n">${N}</td><td class="n">${usd(calc.precio_unitario)}</td><td class="n">${usd(calc.precio_unitario * N)}</td><td>${esc(it.plazo_dias)}</td></tr>
        ${calc.flete ? `<tr><td></td><td></td><td>${esc(of.descripcion_flete || "Flete y embalaje hasta destino")}</td><td class="n">1</td><td class="n">${usd(calc.flete)}</td><td class="n">${usd(calc.flete)}</td><td></td></tr>` : ""}
        <tr><td colspan="5"><b>TOTAL (SIN IVA)</b></td><td class="n"><b>${usd(calc.total)}</b></td><td></td></tr></tbody></table>`;
      if (transporteIncluido(cot)) cuerpo += `<p>${esc(notaTransporte(transporteIncluido(cot)))}</p>`;
      else if (!cot.parametros.TRANS && of.nota_flete) cuerpo += `<p>${esc(of.nota_flete)}</p>`;
      for (const [t, v] of Object.entries(of.condiciones || {})) cuerpo += tit(t) + [].concat(v).map(l => `<p>${esc(l)}</p>`).join("");
    } else {
      cuerpo += tit("ALCANCE") + `<table><thead><tr><th>ITEM</th><th>CANT.</th><th>DESCRIPCIÓN</th><th>OBSERVACIÓN / DESVÍO</th><th>Plazo (días)</th></tr></thead><tbody><tr><td>${esc(it.item)}</td><td>${N}</td><td>${esc(it.descripcion)}</td><td>${esc(it.observacion)}</td><td>${esc(it.plazo_dias)}</td></tr></tbody></table>`;
      cuerpo += tit("EMBALAJE") + `<p>${esc(of.embalaje)}</p>` + tit("DOCUMENTOS QUE FORMAN PARTE DE LA PROPUESTA") + lis([`${of.oferta.numero} – OFERTA TÉCNICA`, `${of.oferta.numero} – OFERTA ECONÓMICA`, ...(of.documentos_cliente || [])]);
      cuerpo += tit("CARACTERÍSTICAS GENERALES SEGÚN PLANO") + `<p>${esc(of.caracteristicas)}</p>` + (ctx.planoUrl ? `<p style="text-align:center"><img src="${ctx.planoUrl}" style="max-width:560px"></p>` : "");
      cuerpo += tit(of.titulo_materiales || "MATERIALES CONSIDERADOS") + `<table><thead><tr><th>POS</th><th>DESCRIPCIÓN</th><th>Ø</th><th>SERIE / SCH</th><th>MATERIAL</th><th>EXT.</th><th>CANT.</th></tr></thead><tbody>${filasPlano(cot).map(f => `<tr>${f.map(v => `<td>${esc(v)}</td>`).join("")}</tr>`).join("")}</tbody></table>`;
      if (notaCantidades(cot)) cuerpo += `<p>${esc(notaCantidades(cot))}</p>`;
      for (const k of ["aclaraciones_y_desvios", "exclusiones", "alcance_general"]) if (of[k]) cuerpo += tit(of[k].titulo) + lis(of[k].items);
      cuerpo += tit("GARANTÍA") + `<p>${esc(of.garantia)}</p>`;
    }
    return `<div class="doc of">${CSS_PDF}
      <div style="display:flex;justify-content:space-between;align-items:center"><img src="${logo}" style="height:46px">${aprobado ? "" : '<span class="marca">BORRADOR – SIN REVISAR – NO ENVIAR</span>'}</div>
      <div class="of-caja"><b>${tipo === "tecnica" ? "OFERTA TÉCNICA" : "OFERTA ECONÓMICA"}</b><br>Oferta: ${esc(of.oferta.numero)} · Revisión ${esc(of.oferta.revision)} · Fecha ${esc(fecha(of.oferta.fecha))}<br>
        Cliente: ${esc(cli.nombre)}<br>Contacto: ${esc(cli.contacto)}<br>Referencia: ${esc(cli.referencia)}<br>Proyecto: ${esc(cli.proyecto)}<br>ITT S.A.: ${esc(firmante?.nombre || "")}</div>
      <p>De nuestra consideración:</p><p>Agradecemos su pedido y nos complace presentarles nuestra mejor propuesta ${tipo === "tecnica" ? "Técnica" : "Económica"} para la provisión de la referencia solicitada.</p>
      <p>Sin otro particular, los saludamos atentamente.</p>${cuerpo}
      <div class="firma nobreak">${firmaUrl && aprobado ? `<img src="${firmaUrl}">` : ""}<b>${esc(firmante?.nombre || "")}</b><span>${esc(firmante?.cargo || "")}</span>
        ${firmante?.telefono ? `<span>☎ ${esc(firmante.telefono)}</span>` : ""}${firmante?.celular ? `<span>📱 ${esc(firmante.celular)}</span>` : ""}${firmante?.email ? `<span>${esc(firmante.email)}</span>` : ""}</div></div>`;
  }

  return { fecha, fechaHora, isoDe, numeroDe, errorNumero, NI, numg, transporteIncluido, completarOferta, planilla, compras, informeHtml, pdfDeHtml, ofertaDocx, ofertaHtml, usd, num, esc, TIPOS, COINC };
})();
if (typeof module !== "undefined") module.exports = Documentos;
