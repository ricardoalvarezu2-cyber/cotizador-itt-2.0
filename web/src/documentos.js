// Documentos que descarga la página: planilla del presupuesto (Excel con fórmulas, mismo diseño que armar_cotizacion.py),
// lista para Compras, informe del presupuesto (PDF), ofertas técnica y económica (Word con la plantilla de ITT y PDF) y respaldo.
// Librerías: XLSX (xlsx-js-style), JSZip, html2pdf.
const Documentos = (() => {
  const TIPOS = { cot: "Cotización", lista: "Lista de precios", stock: "Stock / compra", ant: "Planilla interna", est: "Estimado" };
  const COINC = { igual: "Igual", similar: "Similar", sin_ref: "Sin referencia" };
  const W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main";
  const esc = s => String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  const usd = v => "USD " + Number(v || 0).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  const num = (v, d = 2) => Number(v || 0).toLocaleString("es-AR", { minimumFractionDigits: d, maximumFractionDigits: d });
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
  // DD-MM-AAAA (o DD/MM/AAAA) escrita por el usuario → AAAA-MM-DD; "" si no es una fecha válida
  function isoDe(t) {
    const m = String(t || "").trim().match(/^(\d{1,2})[-/.](\d{1,2})[-/.](\d{4})$/); if (!m) return "";
    const d = new Date(+m[3], +m[2] - 1, +m[1]);
    return d.getDate() === +m[1] && d.getMonth() === +m[2] - 1 ? `${m[3]}-${dos(m[2])}-${dos(m[1])}` : "";
  }
  const serial = iso => { const [y, m, d] = String(iso).split("-").map(Number); return (Date.UTC(y, (m || 1) - 1, d || 1) - Date.UTC(1899, 11, 30)) / 86400000; };
  const sinHtml = s => String(s ?? "").replace(/<[^>]+>/g, "");

  // ------------------------------------------------------------------ Excel del presupuesto
  function planilla(cot, idx) {
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
    [[`Cantidad de ${eq.plural}`, p.N, "0"], ["Factor de materiales (materiales y contingencia)", p.FM, "0.00"], ["Factor de mano de obra y servicios", p.FMO, "0.00"],
     ["Contingencia materiales", p.CONT / 100, "0%"], ["Incluir flete (1 = sí, 0 = no)", p.TRANS, "0"], ["Tipo de cambio ARS/USD (BNA)", p.TC, "#,##0"],
     ["Flete ARS por envío", p.TR_ARS, "#,##0"], ["Embalaje USD por envío (estimado)", p.TR_EMB, U], ["Factor flete", p.TR_F, "0.00"]]
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
    [["Materiales (con ajuste por inflación)", `SUM(Materiales!P2:P${nm})`, "$B$6"], ["Contingencia", "B18*$B$8", "$B$6"],
     ["Mano de obra", `SUMIF(${S}!B2:B${ns},"MO",${S}!P2:P${ns})`, "$B$7"], ["Servicios e insumos", `SUMIF(${S}!B2:B${ns},"Servicio",${S}!P2:P${ns})`, "$B$7"]]
      .forEach(([n, f, fa], i) => {
        const r = 18 + i; put(ws, A(1, r), n); put(ws, A(2, r), { f }, null, U); put(ws, A(3, r), { f: fa }, null, "0.00");
        put(ws, A(4, r), { f: `B${r}*C${r}` }, null, U); put(ws, A(5, r), { f: `D${r}*$B$5` }, null, U);
      });
    put(ws, "A22", "Flete + embalaje (por envío)"); put(ws, "C22", { f: "$B$13" }, null, "0.00"); put(ws, "E22", { f: "IF($B$9=1,($B$11/$B$10+$B$12)*$B$13,0)" }, null, U);
    put(ws, "A23", "TOTAL SIN IVA", TOT); put(ws, "B23", { f: "SUM(B18:B21)" }, TOT, U); put(ws, "C23", { f: "D23/B23" }, TOT, "0.00");
    put(ws, "D23", { f: "SUM(D18:D21)" }, TOT, U); put(ws, "E23", { f: "SUM(E18:E22)" }, TOT, U);
    put(ws, "A26", "Margen sobre precio"); put(ws, "D26", { f: "1-B23/D23" }, null, "0.0%");
    put(ws, "A27", "PRECIO UNITARIO DE VENTA (redondeado, va a la oferta)", AZ); put(ws, "D27", { f: "ROUND(D23,2)" }, AZ, U);
    put(ws, "A28", "TOTAL DE LA OFERTA SIN IVA (unitario redondeado × cantidad + flete)", AZ); put(ws, "E28", { f: "D27*B5+E22" }, AZ, U);
    put(ws, "A29", `Costo / ${eq.singular} SIN ajuste por inflación`); put(ws, "B29", { f: `SUM(Materiales!G2:G${nm})*(1+B8)+SUM(${S}!G2:G${ns})` }, null, U);
    put(ws, "A30", "Ajuste por inflación incluido en el costo"); put(ws, "B30", { f: "B23-B29" }, null, U); put(ws, "C30", { f: "B30/B29" }, null, "+0.0%");
    (cot.planilla_notas || []).forEach((t, k) => put(ws, A(1, 32 + k), sinHtml(t)));
    ws["!cols"] = [{ wch: 52 }, { wch: 16 }, { wch: 16 }, { wch: 16 }, { wch: 16 }, { wch: 4 }, { wch: 58 }, { wch: 13 }];
    X.utils.book_append_sheet(wb, ws, "Cotización");

    const detalle = (nombre, items, esSrv) => {
      const w = hoja();
      cabecera(w, ["Pos", esSrv ? "Grupo" : "ID", "Descripción", `Cant. / ${eq.singular}`, "Unidad", "USD unit. (a la fecha del precio)", "Subtotal USD (sin ajuste)",
        "Tipo de origen", "Proveedor o criterio", "Carpeta de origen", "Fecha del precio", "ID", "Meses hasta hoy",
        "Factor inflación (" + (esSrv ? "costo local USD" : "CPI EE.UU.") + ")", "USD unit. ajustado", "Subtotal USD ajustado", "Coincidencia con el plano", "Diferencia con lo pedido"],
        [6, 10, 44, 10, 8, 13, 13, 13, 48, 26, 12, 6, 9, 10, 12, 13, 13, 50]);
      const col = esSrv ? 4 : 5;
      items.forEach((it, k) => {
        const i = k + 2, s = it.fuentes[0];
        const vals = [it.pos, esSrv ? (it.grupo === "mo" ? "MO" : "Servicio") : it.id, it.descripcion, Number(it.cantidad), it.unidad, Number(s.precio), { f: `D${i}*F${i}` },
          TIPOS[s.tipo] || s.tipo, s.proveedor, s.origen, serial(s.fecha), it.id, { f: `MAX(0,('Cotización'!$H$7-K${i})/30.4375)` },
          { f: `IF('Cotización'!$H$6=1,VLOOKUP('Cotización'!$H$7,${RNG},${col},1)/VLOOKUP(MAX(K${i},'Índices'!$A$2),${RNG},${col},1),1)` },
          { f: `F${i}*N${i}` }, { f: `D${i}*O${i}` }, COINC[s.coincide] || "", s.diferencia || ""];
        vals.forEach((v, j) => {
          const c = j + 1;
          const st = c === 4 || c === 6 ? INP : c === 8 ? { fill: { fgColor: { rgb: TF[s.tipo] || "FFFFFF" } } } :
            c === 17 ? { fill: { fgColor: { rgb: { igual: "DDF1E4", similar: "FBEFD6", sin_ref: "F8E1DE" }[s.coincide] || "FFFFFF" } } } : null;
          const z = [6, 7, 15, 16].includes(c) ? U : { 11: "dd-mm-yyyy", 13: "0.0", 14: "0.000" }[c];
          put(w, A(c, i), v, st, z);
        });
      });
      const n = items.length + 2;
      put(w, A(3, n), `Subtotal por ${eq.singular}`, TOT);
      put(w, A(7, n), { f: `SUM(G2:G${n - 1})` }, TOT, U); put(w, A(16, n), { f: `SUM(P2:P${n - 1})` }, TOT, U);
      let k = n + 2;
      for (const it of items) for (const a of it.fuentes.slice(1)) put(w, A(3, k++), `Alternativa pos ${it.pos}: USD ${a.precio} · ${a.proveedor} · ${a.origen} · ${fecha(a.fecha)} (${TIPOS[a.tipo]})`, GRIS);
      w["!autofilter"] = { ref: `A1:R${Math.max(2, n - 1)}` };
      X.utils.book_append_sheet(wb, w, nombre);
    };
    detalle("Materiales", mat, false);
    detalle("MO y servicios", srv, true);

    const x = hoja();
    cabecera(x, ["Mes", "IPC Argentina (oct-24=100)", "Dólar BNA vendedor (promedio)", "Costo local en USD (IPC/dólar, oct-24=100)", "CPI EE.UU. (oct-24=100)", "Origen IPC", "Origen dólar", "Origen CPI"],
      [11, 13, 12, 16, 12, 40, 40, 40]);
    idx.forEach((r, k) => {
      const i = k + 2;
      put(x, A(1, i), serial(r.mes + "-01"), null, "mm-yyyy"); put(x, A(2, i), r.ipc, null, "0.00"); put(x, A(3, i), r.dolar, null, "#,##0.00");
      put(x, A(4, i), r.local, null, "0.00"); put(x, A(5, i), r.cpi, null, "0.00"); put(x, A(6, i), r.oi); put(x, A(7, i), r.od); put(x, A(8, i), r.oc);
    });
    X.utils.book_append_sheet(wb, x, "Índices");
    if ((cot.desvios || []).length) {
      const d = hoja(); cabecera(d, ["Pos", "Desvío", "Detalle"], [16, 50, 80]);
      cot.desvios.forEach((dv, k) => { put(d, A(1, k + 2), sinHtml(dv.tag)); put(d, A(2, k + 2), sinHtml(dv.titulo)); put(d, A(3, k + 2), sinHtml(dv.texto)); });
      X.utils.book_append_sheet(wb, d, "Desvíos");
    }
    return new Blob([X.write(wb, { type: "array", bookType: "xlsx" })], { type: "application/octet-stream" });
  }

  // ------------------------------------------------------------------ Excel para Compras
  function compras(cot) {
    const X = XLSX, wb = X.utils.book_new(), N = Number(cot.parametros.N) || 1;
    const H = { font: { bold: true, color: { rgb: "FFFFFF" } }, fill: { fgColor: { rgb: "1D5F86" } }, alignment: { wrapText: true, vertical: "center" } };
    const AM = { font: { bold: true }, fill: { fgColor: { rgb: "FFE699" } }, alignment: { wrapText: true, vertical: "center" } };
    const hojaDe = (items, titulo, conPlano) => {
      const cols = ["Pos", "Descripción", "Especificación del plano", `Cantidad por ${cot.equipo?.singular || "equipo"}`, `Cantidad a comprar (× ${N})`, "Unidad",
        "Precio de referencia interno USD (sin IVA)", "Fuente de la referencia", "Notas",
        "Proveedor", "Precio unitario", "Moneda", "¿Incluye IVA?", "Plazo de entrega", "Validez de la oferta", "Observaciones del comprador"];
      const filas = items.map(it => {
        const s = it.fuentes[0];
        return [it.pos, it.descripcion, it.especificacion || "", Number(it.cantidad), it.cantidad_compra ?? Number(it.cantidad) * N, it.unidad, Number(s.precio) || "",
          `${TIPOS[s.tipo] || ""} · ${s.proveedor} · ${fecha(s.fecha)}`, s.coincide === "similar" ? "Referencia de una pieza similar: " + (s.diferencia || "") : "", "", "", "", "", "", "", ""];
      });
      const ws = X.utils.aoa_to_sheet([[titulo], [], cols, ...filas]);
      cols.forEach((c, i) => { const a = X.utils.encode_cell({ r: 2, c: i }); ws[a].s = i >= 9 ? AM : H; });
      ws.A1.s = { font: { bold: true, sz: 13 } };
      ws["!cols"] = [6, 40, 46, 10, 12, 8, 14, 46, 36, 22, 12, 9, 10, 14, 14, 30].map(w => ({ wch: w }));
      for (let r = 3; r < 3 + filas.length; r++) for (let c = 9; c < 16; c++) { const a = X.utils.encode_cell({ r, c }); ws[a] = ws[a] || { t: "s", v: "" }; ws[a].s = { fill: { fgColor: { rgb: "FFF7D6" } } }; }
      return ws;
    };
    X.utils.book_append_sheet(wb, hojaDe(cot.items.filter(i => i.grupo === "material"), `${cot.codigo} · ${cot.titulo || ""} · Pedido de cotización a Compras (precios sin IVA)`), "Materiales");
    X.utils.book_append_sheet(wb, hojaDe(cot.items.filter(i => i.grupo !== "material"), `${cot.codigo} · Servicios a cotizar`), "Servicios");
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
        <td class="n">${num(it.cantidad, it.cantidad % 1 ? 2 : 0)} ${esc(it.unidad)}</td><td class="n">${num(s.precio)}</td><td class="n">${num(f.factor, 3)}</td><td class="n">${num(f.ajustado)}</td>
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
        <tr><td>Materiales (con ajuste por inflación)</td><td class="n">${usd(calc.sub.material)}</td><td class="n">factor ${p.FM}</td></tr>
        <tr><td>Contingencia ${p.CONT}%</td><td class="n">${usd(calc.cont)}</td><td class="n">factor ${p.FM}</td></tr>
        <tr><td>Mano de obra</td><td class="n">${usd(calc.sub.mo)}</td><td class="n">factor ${p.FMO}</td></tr>
        <tr><td>Servicios e insumos</td><td class="n">${usd(calc.sub.servicio)}</td><td class="n">factor ${p.FMO}</td></tr>
        <tr><td>Flete + embalaje</td><td class="n">${usd(calc.flete)}</td><td class="n">${p.TRANS ? "incluido" : "no incluido (EXW Quilmes Oeste)"}</td></tr>
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
        [[it.item, it.codigo, it.descripcion, String(N), usd(calc.precio_unitario), usd(calc.precio_unitario * N), it.plazo_dias]],
        [1.3, 3.1, 5.0, 2.1, 2.4, 2.6, 1.9], ["TOTAL (SIN IVA)", usd(calc.total)], 9, [1, 1, 0, 1, 1, 1, 1]);
      if (!cot.parametros.TRANS && of.nota_flete) x += texto(of.nota_flete);
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
      x += titulo(`MATERIALES CONSIDERADOS (POR ${(cot.equipo?.singular || "equipo").toUpperCase()})`);
      x += tabla(["POS", "DESCRIPCIÓN", "Ø", "SERIE / SCH", "MATERIAL", "EXT.", "CANT."], plano, [1.0, 7.4, 1.6, 1.6, 3.3, 1.6, 1.1], null, 7.5, [1, 0, 1, 1, 1, 1, 1]);
      for (const k of ["aclaraciones_y_desvios", "exclusiones", "alcance_general"]) if (of[k]) x += titulo(of[k].titulo) + vinetas(of[k].items || []);
      x += titulo("GARANTÍA") + texto(of.garantia || "") + vacio();
    }
    return x;
  }

  function filasPlano(cot) {
    return cot.items.filter(i => i.grupo === "material" && !/b$|c$/.test(String(i.pos))).map(i => {
      const pl = i.plano || {};
      return [i.pos, i.descripcion + (pl.modelo ? ` (${pl.modelo})` : ""), pl.diametro || "", pl.serie_sch || "", pl.material || "", pl.extremos || "", String(i.cantidad)];
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
        <tr><td colspan="5"><b>TOTAL (SIN IVA)</b></td><td class="n"><b>${usd(calc.total)}</b></td><td></td></tr></tbody></table>`;
      if (!cot.parametros.TRANS && of.nota_flete) cuerpo += `<p>${esc(of.nota_flete)}</p>`;
      for (const [t, v] of Object.entries(of.condiciones || {})) cuerpo += tit(t) + [].concat(v).map(l => `<p>${esc(l)}</p>`).join("");
    } else {
      cuerpo += tit("ALCANCE") + `<table><thead><tr><th>ITEM</th><th>CANT.</th><th>DESCRIPCIÓN</th><th>OBSERVACIÓN / DESVÍO</th><th>Plazo (días)</th></tr></thead><tbody><tr><td>${esc(it.item)}</td><td>${N}</td><td>${esc(it.descripcion)}</td><td>${esc(it.observacion)}</td><td>${esc(it.plazo_dias)}</td></tr></tbody></table>`;
      cuerpo += tit("EMBALAJE") + `<p>${esc(of.embalaje)}</p>` + tit("DOCUMENTOS QUE FORMAN PARTE DE LA PROPUESTA") + lis([`${of.oferta.numero} – OFERTA TÉCNICA`, `${of.oferta.numero} – OFERTA ECONÓMICA`, ...(of.documentos_cliente || [])]);
      cuerpo += tit("CARACTERÍSTICAS GENERALES SEGÚN PLANO") + `<p>${esc(of.caracteristicas)}</p>` + (ctx.planoUrl ? `<p style="text-align:center"><img src="${ctx.planoUrl}" style="max-width:560px"></p>` : "");
      cuerpo += tit("MATERIALES CONSIDERADOS") + `<table><thead><tr><th>POS</th><th>DESCRIPCIÓN</th><th>Ø</th><th>SERIE / SCH</th><th>MATERIAL</th><th>EXT.</th><th>CANT.</th></tr></thead><tbody>${filasPlano(cot).map(f => `<tr>${f.map(v => `<td>${esc(v)}</td>`).join("")}</tr>`).join("")}</tbody></table>`;
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

  return { fecha, fechaHora, isoDe, planilla, compras, informeHtml, pdfDeHtml, ofertaDocx, ofertaHtml, usd, num, esc, TIPOS, COINC };
})();
if (typeof module !== "undefined") module.exports = Documentos;
