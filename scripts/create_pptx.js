// Genera el PowerPoint ejecutivo del Reporte de Abonos Club Puebla
const pptxgen = require("pptxgenjs");
const fs = require("fs");
const path = require("path");

const REPO_ROOT = path.resolve(__dirname, "..");
const DATA_PATH = process.env.PUEBLA_DATA_JSON || path.join(REPO_ROOT, "data.json");
const OUT       = process.env.PUEBLA_PPTX_OUT  || path.join(REPO_ROOT, "outputs", "Reporte_Puebla_Abonados_2026.pptx");

const data = JSON.parse(fs.readFileSync(DATA_PATH, "utf-8"));

// ===== Branding (dark mode Boletomóvil) =====
const COLOR = {
  bg:        "0B0F14",
  bgCard:    "161D24",
  bgElev:    "1F2830",
  border:    "2A343E",
  text1:     "ECF1F5",
  text2:     "9AA5B0",
  text3:     "6A7682",
  bmGreen:   "00C677",
  bmGreen2:  "1FE39A",
  bmDark:    "253039",
  amber:     "FF6B6B",
  red:       "FF5C61",
  grayDark:  "4A5560",
  graySoft:  "7B8A98",
};
const FONT = "Inter";

// ===== Helpers =====
const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";   // 13.3" × 7.5"
pres.author = "Boletomóvil";
pres.title  = "Reporte de Abonos — Club Puebla";
pres.company = "Boletomóvil";

const SW = 13.3, SH = 7.5;

const fmtMoney = v => v >= 1e6 ? "$"+(v/1e6).toFixed(2)+"M" : "$"+(v/1e3).toFixed(0)+"K";
const fmtMoneyFull = v => "$"+Math.round(v).toLocaleString("es-MX");
const fmtNum = v => v.toLocaleString("es-MX");

const tours = data.tournaments;
const main  = data.main;
const renewal = data.renewal;

// ===== Helper: estandariza fondos y header de cada slide =====
function newSlide(title, subtitle) {
  const s = pres.addSlide();
  s.background = { color: COLOR.bg };
  // accent bar superior (verde)
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: SW, h: 0.05,
    fill: { color: COLOR.bmGreen }, line: { color: COLOR.bmGreen, width: 0 },
  });
  // Branding superior derecho
  s.addText("BOLETOMÓVIL  ·  CLUB PUEBLA", {
    x: SW-4.2, y: 0.18, w: 4.0, h: 0.3,
    align: "right", fontFace: FONT, fontSize: 9,
    color: COLOR.text3, bold: true, charSpacing: 3, margin: 0,
  });
  if (title) {
    s.addText(title, {
      x: 0.6, y: 0.22, w: 8.5, h: 0.55,
      fontFace: FONT, fontSize: 24, bold: true,
      color: COLOR.text1, margin: 0,
    });
  }
  if (subtitle) {
    s.addText(subtitle, {
      x: 0.6, y: 0.78, w: 11, h: 0.32,
      fontFace: FONT, fontSize: 12,
      color: COLOR.text2, margin: 0,
    });
  }
  return s;
}

// ===== KPI card helper (auto-fits value size to card height) =====
function addKpiCard(s, x, y, w, h, label, value, sublabel, opts = {}) {
  const featured = !!opts.featured;
  // Auto fontSize del valor en función de h
  const valueSize = opts.valueSize || (h >= 1.7 ? 36 : (h >= 1.55 ? 30 : 26));
  const labelH = 0.28;
  const sublabelH = 0.28;
  const labelY = y + 0.18;
  const sublabelY = y + h - sublabelH - 0.18;
  // valor centrado entre label (abajo) y sublabel (arriba)
  const valueY = labelY + labelH + 0.05;
  const valueH = sublabelY - valueY - 0.05;

  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x, y, w, h,
    fill: { color: featured ? COLOR.bmGreen : COLOR.bgCard },
    line: { color: featured ? COLOR.bmGreen : COLOR.border, width: 1 },
    rectRadius: 0.1,
  });
  s.addText(label.toUpperCase(), {
    x: x+0.25, y: labelY, w: w-0.5, h: labelH,
    fontFace: FONT, fontSize: 9, bold: true, charSpacing: 3,
    color: featured ? "FFFFFF" : COLOR.text3, margin: 0,
  });
  s.addText(value, {
    x: x+0.25, y: valueY, w: w-0.5, h: valueH,
    fontFace: FONT, fontSize: valueSize, bold: true, valign: "middle",
    color: featured ? "FFFFFF" : COLOR.text1, margin: 0,
  });
  if (sublabel) {
    s.addText(sublabel, {
      x: x+0.25, y: sublabelY, w: w-0.5, h: sublabelH,
      fontFace: FONT, fontSize: 10,
      color: featured ? "FFFFFF" : COLOR.text2, margin: 0,
    });
  }
}

// ===== Card container =====
function addCard(s, x, y, w, h, title, meta) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x, y, w, h,
    fill: { color: COLOR.bgCard },
    line: { color: COLOR.border, width: 1 },
    rectRadius: 0.08,
  });
  if (title) {
    s.addText(title, {
      x: x+0.3, y: y+0.18, w: w*0.6, h: 0.32,
      fontFace: FONT, fontSize: 12, bold: true,
      color: COLOR.text1, margin: 0,
    });
  }
  if (meta) {
    s.addText(meta, {
      x: x+w*0.4, y: y+0.18, w: w*0.55-0.3, h: 0.32,
      fontFace: FONT, fontSize: 9, charSpacing: 2,
      color: COLOR.text3, align: "right", bold: true, margin: 0,
    });
  }
}

// ===== SLIDE 1: PORTADA =====
{
  const s = pres.addSlide();
  s.background = { color: COLOR.bg };
  // verde radial top right (simulada con un círculo grande con baja opacidad)
  s.addShape(pres.shapes.OVAL, {
    x: SW-4.5, y: -3, w: 8, h: 8,
    fill: { color: COLOR.bmGreen, transparency: 80 },
    line: { color: COLOR.bmGreen, width: 0 },
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: SH-0.05, w: SW, h: 0.05,
    fill: { color: COLOR.bmGreen }, line: { color: COLOR.bmGreen, width: 0 },
  });

  s.addText("REPORTE EJECUTIVO", {
    x: 0.8, y: 1.6, w: 11, h: 0.4,
    fontFace: FONT, fontSize: 12, bold: true, charSpacing: 6,
    color: COLOR.bmGreen2, margin: 0,
  });
  s.addText("Análisis de Abonos", {
    x: 0.8, y: 2.1, w: 11, h: 0.95,
    fontFace: FONT, fontSize: 56, bold: true,
    color: COLOR.text1, margin: 0,
  });
  s.addText("Club Puebla", {
    x: 0.8, y: 3.05, w: 11, h: 0.95,
    fontFace: FONT, fontSize: 56, bold: true,
    color: COLOR.bmGreen2, margin: 0,
  });
  s.addText("3 temporadas comparadas  ·  AP23-CL24  ·  AP24-CL25  ·  AP25-CL26", {
    x: 0.8, y: 4.3, w: 11, h: 0.4,
    fontFace: FONT, fontSize: 16,
    color: COLOR.text2, margin: 0,
  });
  s.addText("BOLETOMÓVIL", {
    x: 0.8, y: SH-0.7, w: 6, h: 0.3,
    fontFace: FONT, fontSize: 10, bold: true, charSpacing: 4,
    color: COLOR.text3, margin: 0,
  });
}

// ===== SLIDE 2: KPIs PRINCIPALES =====
{
  const s = newSlide("Resumen ejecutivo", "Lo más relevante de los últimos 3 torneos");

  const kpiY = 1.5, kpiH = 1.7;
  // 2 cards principales
  addKpiCard(s, 0.6, kpiY, 6.0, kpiH,
    "Total vendido (3 torneos)",
    "$"+(main.total_revenue/1e6).toFixed(1)+"M",
    "Suma del SUBTOTAL pagado",
    { featured: true });

  addKpiCard(s, 6.7, kpiY, 6.0, kpiH,
    "Abonos emitidos totales",
    fmtNum(main.total_volumen),
    fmtNum(main.total_pagado)+" pagados  ·  "+fmtNum(main.total_cortesias)+" cortesías");

  // 3 KPIs secundarios por torneo
  const subY = 3.5, subH = 1.7, subW = 4.0, gap = 0.15;
  tours.forEach((t,i) => {
    const x = 0.6 + i*(subW+gap);
    addKpiCard(s, x, subY, subW, subH,
      t.label,
      "$"+(t.revenue/1e6).toFixed(2)+"M",
      fmtNum(t.volumen_total)+" abonos  ·  "+t.cortesias_pct+"% cortesías");
  });

  // Footer note
  s.addText("Cortesías = órdenes con SUBTOTAL=0 (explícitas + descuentos 100%). Palcos y Plateas AP25-CL26 quedan fuera del comparativo.", {
    x: 0.6, y: SH-0.55, w: 12, h: 0.3,
    fontFace: FONT, fontSize: 9, italic: true,
    color: COLOR.text3, margin: 0,
  });
}

// ===== SLIDE 3: COMPARATIVO POR TORNEO (TABLA) =====
{
  const s = newSlide("Comparativo por torneo", "Cuánto se vendió y cuántos abonos se emitieron en cada temporada");

  const tableY = 1.5;
  const headerFill = { color: COLOR.bgElev };
  const cellFont = { fontFace: FONT, fontSize: 12, color: COLOR.text1, valign: "middle" };

  const header = [
    { text: "TORNEO", options: { bold: true, color: COLOR.text3, fontSize: 10, fill: headerFill, charSpacing: 2 } },
    { text: "REVENUE", options: { bold: true, color: COLOR.text3, fontSize: 10, fill: headerFill, charSpacing: 2, align: "right" } },
    { text: "ABONOS", options: { bold: true, color: COLOR.text3, fontSize: 10, fill: headerFill, charSpacing: 2, align: "right" } },
    { text: "PAGADOS", options: { bold: true, color: COLOR.text3, fontSize: 10, fill: headerFill, charSpacing: 2, align: "right" } },
    { text: "CORTESÍAS", options: { bold: true, color: COLOR.text3, fontSize: 10, fill: headerFill, charSpacing: 2, align: "right" } },
    { text: "% CORT.", options: { bold: true, color: COLOR.text3, fontSize: 10, fill: headerFill, charSpacing: 2, align: "right" } },
    { text: "TICKET PROM.", options: { bold: true, color: COLOR.text3, fontSize: 10, fill: headerFill, charSpacing: 2, align: "right" } },
  ];
  const rows = [header];
  tours.forEach(t => {
    rows.push([
      { text: t.label, options: { ...cellFont, bold: true, fill: { color: COLOR.bgCard } } },
      { text: "$"+(t.revenue/1e6).toFixed(2)+"M", options: { ...cellFont, bold: true, color: COLOR.bmGreen2, align: "right", fill: { color: COLOR.bgCard } } },
      { text: fmtNum(t.volumen_total), options: { ...cellFont, align: "right", fill: { color: COLOR.bgCard } } },
      { text: fmtNum(t.volumen_pagado), options: { ...cellFont, align: "right", fill: { color: COLOR.bgCard } } },
      { text: fmtNum(t.cortesias), options: { ...cellFont, align: "right", color: COLOR.amber, fill: { color: COLOR.bgCard } } },
      { text: t.cortesias_pct+"%", options: { ...cellFont, align: "right", fill: { color: COLOR.bgCard } } },
      { text: "$"+t.ticket_promedio.toLocaleString("es-MX"), options: { ...cellFont, align: "right", fill: { color: COLOR.bgCard } } },
    ]);
  });

  s.addTable(rows, {
    x: 0.6, y: tableY, w: 12.1, h: 3.2,
    colW: [2.3, 1.8, 1.5, 1.5, 1.7, 1.4, 1.9],
    rowH: 0.6,
    border: { type: "solid", pt: 1, color: COLOR.border },
    margin: 0.15,
  });

  // Insight callout below
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 0.6, y: 5.2, w: 12.1, h: 1.7,
    fill: { color: COLOR.bgCard },
    line: { color: COLOR.bmGreen, width: 1 },
    rectRadius: 0.08,
  });
  s.addText("LECTURA EJECUTIVA", {
    x: 0.85, y: 5.35, w: 6, h: 0.3,
    fontFace: FONT, fontSize: 9, bold: true, charSpacing: 3,
    color: COLOR.bmGreen2, margin: 0,
  });
  // Cálculos dinámicos desde data
  const t1 = tours[0], t3 = tours[2];
  const volChg = Math.round((t3.volumen_total - t1.volumen_total)/t1.volumen_total*1000)/10;
  const revChg = Math.round((t3.revenue - t1.revenue)/t1.revenue*1000)/10;
  const tickChg = Math.round((t3.ticket_promedio - t1.ticket_promedio)/t1.ticket_promedio*1000)/10;
  const cortPct = t3.cortesias_pct;
  const sign = v => v >= 0 ? "+" : "";

  s.addText([
    { text: `Volumen ${volChg<0?'cayó':'creció'} ${sign(volChg)}${volChg}% (${fmtNum(t1.volumen_total)} → ${fmtNum(t3.volumen_total)}) `, options: { color: COLOR.text1, bold: true } },
    { text: `y revenue ${revChg<0?'cayó':'creció'} ${sign(revChg)}${revChg}% ($${(t1.revenue/1e6).toFixed(2)}M → $${(t3.revenue/1e6).toFixed(2)}M) `, options: { color: revChg<0?COLOR.amber:COLOR.bmGreen2, bold: true } },
    { text: `entre AP23-CL24 y AP25-CL26. `, options: { color: COLOR.text1, bold: true, breakLine: true } },
    { text: "", options: { breakLine: true } },
    { text: `Ticket promedio ${tickChg>=0?'subió':'bajó'} a $${t3.ticket_promedio.toLocaleString('es-MX')} (${sign(tickChg)}${tickChg}%) `, options: { color: COLOR.text2 } },
    { text: `y las cortesías ya representan ${cortPct}% del volumen del último torneo`, options: { color: cortPct>=30?COLOR.amber:COLOR.text2 } },
    { text: " — el club está vendiendo menos pero a precio mayor; el reto es recuperar volumen pagado.", options: { color: COLOR.text2 } },
  ], {
    x: 0.85, y: 5.7, w: 11.6, h: 1.1,
    fontFace: FONT, fontSize: 13, valign: "top", margin: 0,
  });
}

// ===== SLIDE 4: REVENUE POR TORNEO (BAR CHART) =====
{
  const s = newSlide("Revenue por torneo", "Pesos vendidos en cada temporada — suma del SUBTOTAL");

  s.addChart(pres.charts.BAR, [{
    name: "Revenue",
    labels: tours.map(t => t.label),
    values: tours.map(t => Math.round(t.revenue)),
  }], {
    x: 0.6, y: 1.4, w: 12.1, h: 5.5,
    barDir: "col",
    chartColors: [COLOR.bmGreen],
    chartArea: { fill: { color: COLOR.bg } },
    plotArea: { fill: { color: COLOR.bg } },
    catAxisLabelColor: COLOR.text2, catAxisLabelFontSize: 14, catAxisLabelFontFace: FONT,
    valAxisLabelColor: COLOR.text2, valAxisLabelFontSize: 11, valAxisLabelFontFace: FONT,
    valAxisLabelFormatCode: "$#,##0,,\"M\"",
    valGridLine: { color: COLOR.border, size: 0.5 },
    catGridLine: { style: "none" },
    showValue: true,
    dataLabelPosition: "outEnd",
    dataLabelColor: COLOR.text1,
    dataLabelFontSize: 14,
    dataLabelFontBold: true,
    dataLabelFontFace: FONT,
    dataLabelFormatCode: "$#,##0",
    showLegend: false,
    barGapWidthPct: 60,
  });
}

// ===== SLIDE 5: ABONOS EMITIDOS POR TORNEO (STACKED) =====
{
  const s = newSlide("Abonos emitidos por torneo", "Anuales pagados · Semestrales pagados · Cortesías");

  function getDur(t, dur, key) {
    const ds = (t.duracion_split || []).find(x => x.duracion === dur);
    return ds ? ds[key] : 0;
  }

  const stackData = [
    { name: "Anuales pagados",     labels: tours.map(t=>t.label), values: tours.map(t=>getDur(t,"Anual","pagado")) },
    { name: "Semestrales pagados", labels: tours.map(t=>t.label), values: tours.map(t=>getDur(t,"Semestral","pagado")) },
    { name: "Cortesías",           labels: tours.map(t=>t.label), values: tours.map(t=>t.cortesias) },
  ];

  s.addChart(pres.charts.BAR, stackData, {
    x: 0.6, y: 1.4, w: 12.1, h: 5.5,
    barDir: "col",
    barGrouping: "stacked",
    chartColors: [COLOR.bmGreen, COLOR.grayDark, COLOR.amber],
    chartArea: { fill: { color: COLOR.bg } },
    plotArea: { fill: { color: COLOR.bg } },
    catAxisLabelColor: COLOR.text2, catAxisLabelFontSize: 14, catAxisLabelFontFace: FONT,
    valAxisLabelColor: COLOR.text2, valAxisLabelFontSize: 11, valAxisLabelFontFace: FONT,
    valGridLine: { color: COLOR.border, size: 0.5 },
    catGridLine: { style: "none" },
    showValue: true,
    dataLabelColor: "FFFFFF",
    dataLabelFontSize: 11,
    dataLabelFontBold: true,
    dataLabelFontFace: FONT,
    showLegend: true,
    legendPos: "b",
    legendColor: COLOR.text2,
    legendFontSize: 12,
    legendFontFace: FONT,
    barGapWidthPct: 60,
  });
}

// ===== SLIDE 6: EMISIÓN POR SEMESTRE (Anual/Semestral/Cortesía) =====
{
  const s = newSlide("Emisión por semestre", "Anual · Semestral · Cortesía — % del volumen de cada semestre");

  const sem = main.mix_emision_semestre;
  // Reemplaza 0 con null para que no muestre "0.0%" en las barras
  const nz = v => (v === 0 ? null : v);
  s.addChart(pres.charts.BAR, [
    { name: "Anual",     labels: sem.map(m=>m.semestre), values: sem.map(m=>nz(m.Anual_pct)) },
    { name: "Semestral", labels: sem.map(m=>m.semestre), values: sem.map(m=>nz(m.Semestral_pct)) },
    { name: "Cortesía",  labels: sem.map(m=>m.semestre), values: sem.map(m=>nz(m.Cortesía_pct)) },
  ], {
    x: 0.6, y: 1.4, w: 9, h: 5.5,
    barDir: "bar",
    barGrouping: "percentStacked",
    chartColors: [COLOR.bmGreen, COLOR.grayDark, COLOR.amber],
    chartArea: { fill: { color: COLOR.bg } },
    plotArea: { fill: { color: COLOR.bg } },
    catAxisLabelColor: COLOR.text1, catAxisLabelFontSize: 13, catAxisLabelFontFace: FONT, catAxisLabelBold: true,
    valAxisLabelColor: COLOR.text2, valAxisLabelFontSize: 10, valAxisLabelFontFace: FONT,
    valAxisLabelFormatCode: "0%",  // formato % de Excel: multiplica por 100
    valGridLine: { color: COLOR.border, size: 0.5 },
    catGridLine: { style: "none" },
    showValue: true,
    dataLabelColor: "FFFFFF",
    dataLabelFontSize: 10,
    dataLabelFontBold: true,
    dataLabelFontFace: FONT,
    dataLabelFormatCode: "0.0\"%\"",
    showLegend: true,
    legendPos: "b",
    legendColor: COLOR.text2,
    legendFontSize: 12,
    legendFontFace: FONT,
  });

  // Tabla de cantidad al lado derecho
  const cardX = 9.8, cardY = 1.4, cardW = 2.9, cardH = 5.5;
  addCard(s, cardX, cardY, cardW, cardH, "Cantidad", "");
  let yy = cardY + 0.65;
  s.addText([
    { text: "SEMESTRE", options: { bold: true, color: COLOR.text3, fontSize: 9, charSpacing: 2 } },
  ], { x: cardX+0.2, y: yy, w: cardW-0.4, h: 0.25, fontFace: FONT, margin: 0 });
  yy += 0.32;
  sem.forEach(m => {
    s.addText(m.semestre, { x: cardX+0.2, y: yy, w: 1.0, h: 0.32, fontFace: FONT, fontSize: 12, bold: true, color: COLOR.text1, margin: 0 });
    s.addText(fmtNum(m.total), { x: cardX+1.2, y: yy, w: cardW-1.4, h: 0.32, fontFace: FONT, fontSize: 12, color: COLOR.bmGreen2, align: "right", bold: true, margin: 0 });
    yy += 0.42;
  });
  // Nota
  s.addText("Cortesía = SUBTOTAL=0", {
    x: cardX+0.2, y: cardH+cardY-0.45, w: cardW-0.4, h: 0.3,
    fontFace: FONT, fontSize: 9, italic: true,
    color: COLOR.text3, margin: 0,
  });
}

// ===== SLIDE 7: COMPARATIVA POR TIPO DE ABONO ENTRE TORNEOS (REVENUE) =====
{
  const s = newSlide("Revenue por tipo de abono", "Comparativa entre torneos — cuánto se vendió de cada tipo");

  // Recoger todas las categorías y ordenar por revenue total
  const allCats = new Set();
  tours.forEach(t => t.categorias.forEach(c => allCats.add(c.categoria)));
  const catList = Array.from(allCats).map(cat => {
    const totalRev = tours.reduce((s,t) => {
      const c = t.categorias.find(x => x.categoria === cat);
      return s + (c ? c.revenue : 0);
    }, 0);
    return { cat, totalRev };
  }).sort((a,b) => b.totalRev - a.totalRev);

  const catLabels = catList.map(x => x.cat);
  const datasets = tours.map((t, i) => ({
    name: t.label,
    labels: catLabels,
    values: catLabels.map(cat => {
      const c = t.categorias.find(x => x.categoria === cat);
      return (c && c.revenue > 0) ? Math.round(c.revenue) : null;
    })
  }));

  s.addChart(pres.charts.BAR, datasets, {
    x: 0.6, y: 1.4, w: 12.1, h: 5.5,
    barDir: "col",
    barGrouping: "clustered",
    chartColors: [COLOR.grayDark, COLOR.graySoft, COLOR.bmGreen],
    chartArea: { fill: { color: COLOR.bg } },
    plotArea: { fill: { color: COLOR.bg } },
    catAxisLabelColor: COLOR.text2, catAxisLabelFontSize: 10, catAxisLabelFontFace: FONT,
    catAxisLabelRotate: -25,
    valAxisLabelColor: COLOR.text2, valAxisLabelFontSize: 10, valAxisLabelFontFace: FONT,
    valAxisLabelFormatCode: "$#,##0,,\"M\"",
    valGridLine: { color: COLOR.border, size: 0.5 },
    catGridLine: { style: "none" },
    showValue: false,
    showLegend: true,
    legendPos: "t",
    legendColor: COLOR.text2,
    legendFontSize: 11,
    legendFontFace: FONT,
    barGapWidthPct: 40,
  });
}

// ===== SLIDE 8: TOP ZONAS POR TORNEO (VOLUMEN) =====
{
  const s = newSlide("Top zonas — volumen por torneo", "Cómo se comportó cada zona en cada temporada");

  const zones = main.top_zonas_by_tour_vol;
  const datasets = tours.map((t, i) => ({
    name: t.label,
    labels: zones.map(z => z.zona),
    values: zones.map(z => (z[t.torneo] && z[t.torneo] > 0) ? z[t.torneo] : null),
  }));

  s.addChart(pres.charts.BAR, datasets, {
    x: 0.6, y: 1.4, w: 12.1, h: 5.5,
    barDir: "bar",
    barGrouping: "clustered",
    chartColors: [COLOR.grayDark, COLOR.graySoft, COLOR.bmGreen],
    chartArea: { fill: { color: COLOR.bg } },
    plotArea: { fill: { color: COLOR.bg } },
    catAxisLabelColor: COLOR.text1, catAxisLabelFontSize: 11, catAxisLabelFontFace: FONT, catAxisLabelBold: true,
    valAxisLabelColor: COLOR.text2, valAxisLabelFontSize: 10, valAxisLabelFontFace: FONT,
    valGridLine: { color: COLOR.border, size: 0.5 },
    catGridLine: { style: "none" },
    showValue: true,
    dataLabelColor: COLOR.text1,
    dataLabelFontSize: 9,
    dataLabelFontFace: FONT,
    showLegend: true,
    legendPos: "t",
    legendColor: COLOR.text2,
    legendFontSize: 11,
    legendFontFace: FONT,
    barGapWidthPct: 40,
  });
}

// ===== SLIDE 9: TOP ZONAS POR TORNEO (REVENUE) =====
{
  const s = newSlide("Top zonas — revenue por torneo", "Cuánto vendió cada zona en cada temporada");

  const zones = main.top_zonas_by_tour_rev;
  const datasets = tours.map((t, i) => ({
    name: t.label,
    labels: zones.map(z => z.zona),
    values: zones.map(z => (z[t.torneo+"_rev"] && z[t.torneo+"_rev"] > 0) ? Math.round(z[t.torneo+"_rev"]) : null),
  }));

  s.addChart(pres.charts.BAR, datasets, {
    x: 0.6, y: 1.4, w: 12.1, h: 5.5,
    barDir: "bar",
    barGrouping: "clustered",
    chartColors: [COLOR.grayDark, COLOR.graySoft, COLOR.bmGreen],
    chartArea: { fill: { color: COLOR.bg } },
    plotArea: { fill: { color: COLOR.bg } },
    catAxisLabelColor: COLOR.text1, catAxisLabelFontSize: 11, catAxisLabelFontFace: FONT, catAxisLabelBold: true,
    valAxisLabelColor: COLOR.text2, valAxisLabelFontSize: 10, valAxisLabelFontFace: FONT,
    valAxisLabelFormatCode: "$#,##0,,\"M\"",
    valGridLine: { color: COLOR.border, size: 0.5 },
    catGridLine: { style: "none" },
    showValue: false,
    showLegend: true,
    legendPos: "t",
    legendColor: COLOR.text2,
    legendFontSize: 11,
    legendFontFace: FONT,
    barGapWidthPct: 40,
  });
}

// ===== SLIDE 10: RENOVACIÓN =====
{
  const s = newSlide("Renovación temporada a temporada", "Solo canal Online — abonados identificados por correo electrónico");

  const headerFill = { color: COLOR.bgElev };
  const cellFont = { fontFace: FONT, fontSize: 13, color: COLOR.text1, valign: "middle" };

  const rows = [[
    { text: "TRANSICIÓN", options: { bold: true, color: COLOR.text3, fontSize: 10, fill: headerFill, charSpacing: 2 } },
    { text: "BASE PREVIA", options: { bold: true, color: COLOR.text3, fontSize: 10, fill: headerFill, charSpacing: 2, align: "right" } },
    { text: "RENOVARON", options: { bold: true, color: COLOR.text3, fontSize: 10, fill: headerFill, charSpacing: 2, align: "right" } },
    { text: "TASA", options: { bold: true, color: COLOR.text3, fontSize: 10, fill: headerFill, charSpacing: 2, align: "right" } },
    { text: "NUEVOS", options: { bold: true, color: COLOR.text3, fontSize: 10, fill: headerFill, charSpacing: 2, align: "right" } },
    { text: "PERDIDOS", options: { bold: true, color: COLOR.text3, fontSize: 10, fill: headerFill, charSpacing: 2, align: "right" } },
  ]];
  renewal.forEach(r => {
    const tasaColor = r.tasa_renovacion_pct >= 25 ? COLOR.bmGreen2 : (r.tasa_renovacion_pct >= 18 ? COLOR.amber : COLOR.text2);
    rows.push([
      { text: r.from + "  →  " + r.to, options: { ...cellFont, bold: true, fill: { color: COLOR.bgCard } } },
      { text: fmtNum(r.abonados_prev), options: { ...cellFont, align: "right", fill: { color: COLOR.bgCard } } },
      { text: fmtNum(r.renovaron), options: { ...cellFont, align: "right", fill: { color: COLOR.bgCard } } },
      { text: r.tasa_renovacion_pct + "%", options: { ...cellFont, align: "right", color: tasaColor, bold: true, fill: { color: COLOR.bgCard } } },
      { text: "+"+fmtNum(r.nuevos), options: { ...cellFont, align: "right", color: COLOR.bmGreen2, fill: { color: COLOR.bgCard } } },
      { text: "−"+fmtNum(r.perdidos), options: { ...cellFont, align: "right", color: COLOR.red, fill: { color: COLOR.bgCard } } },
    ]);
  });

  s.addTable(rows, {
    x: 0.6, y: 1.5, w: 12.1, h: 1.8,
    colW: [3.0, 1.8, 1.8, 1.5, 2.0, 2.0],
    rowH: 0.65,
    border: { type: "solid", pt: 1, color: COLOR.border },
    margin: 0.15,
  });

  // Insight callout
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 0.6, y: 4.0, w: 12.1, h: 2.6,
    fill: { color: COLOR.bgCard },
    line: { color: COLOR.amber, width: 1 },
    rectRadius: 0.08,
  });
  s.addText("ALERTA — RETENCIÓN ONLINE EN BAJA", {
    x: 0.85, y: 4.18, w: 9, h: 0.32,
    fontFace: FONT, fontSize: 10, bold: true, charSpacing: 3,
    color: COLOR.amber, margin: 0,
  });
  s.addText([
    { text: "La tasa de renovación cayó de 24.3% a 17.2% entre torneos. ", options: { color: COLOR.text1, bold: true, breakLine: true } },
    { text: "En el último ciclo perdimos 442 abonados online que sí compraron el ciclo previo. ", options: { color: COLOR.amber, breakLine: true } },
    { text: "", options: { breakLine: true } },
    { text: "Recomendación: contactar directamente a esos 442 antes del próximo Apertura con beneficio personalizado. Costo bajo, retorno medible.", options: { color: COLOR.text2 } },
  ], {
    x: 0.85, y: 4.55, w: 11.6, h: 1.9,
    fontFace: FONT, fontSize: 14, valign: "top", margin: 0,
  });

  s.addText("Métrica calculada solo con abonados que compraron por canal Online (Frame, IOS, Android). Compras en Taquilla quedan fuera porque históricamente no se trackeaban contra correo.", {
    x: 0.6, y: SH-0.6, w: 12.1, h: 0.4,
    fontFace: FONT, fontSize: 9, italic: true,
    color: COLOR.text3, margin: 0,
  });
}

// ===== SLIDE 11: OCUPACIÓN GENERAL POR TORNEO =====
{
  const s = newSlide("Ocupación de aforo del estadio", "Cómo se llenó el estadio en cada torneo · pagados + cortesías");

  const occ = data.occupancy || {};
  const tourOrder = ["AP23-CL24","AP24-CL25","AP25-CL26"];

  // 3 KPI cards de ocupación
  tourOrder.forEach((tid, i) => {
    const o = occ[tid];
    const x = 0.6 + i*4.13, y = 1.5, w = 4.0, h = 1.7;
    if (!o) {
      addKpiCard(s, x, y, w, h, tid, "—", "Sin reporte de disponibilidad");
      return;
    }
    const tt = o.totales;
    const featured = i === 2;  // último torneo destacado
    addKpiCard(s, x, y, w, h, tid + " — Ocupación",
      tt.ocupacion_pct + "%",
      `${(tt.abonos_vendidos+tt.cortesias).toLocaleString('es-MX')} de ${tt.aforo_total.toLocaleString('es-MX')} cubiertos`,
      { featured });
  });

  // Tabla detallada
  const headerFill = { color: COLOR.bgElev };
  const cellFont = { fontFace: FONT, fontSize: 12, color: COLOR.text1, valign: "middle" };

  const rows = [[
    { text: "TORNEO", options: { bold: true, color: COLOR.text3, fontSize: 10, fill: headerFill, charSpacing: 2 } },
    { text: "AFORO", options: { bold: true, color: COLOR.text3, fontSize: 10, fill: headerFill, charSpacing: 2, align: "right" } },
    { text: "PAGADOS", options: { bold: true, color: COLOR.text3, fontSize: 10, fill: headerFill, charSpacing: 2, align: "right" } },
    { text: "CORTESÍAS", options: { bold: true, color: COLOR.text3, fontSize: 10, fill: headerFill, charSpacing: 2, align: "right" } },
    { text: "CUBIERTO", options: { bold: true, color: COLOR.text3, fontSize: 10, fill: headerFill, charSpacing: 2, align: "right" } },
    { text: "LIBRE", options: { bold: true, color: COLOR.text3, fontSize: 10, fill: headerFill, charSpacing: 2, align: "right" } },
    { text: "OCUPACIÓN", options: { bold: true, color: COLOR.text3, fontSize: 10, fill: headerFill, charSpacing: 2, align: "right" } },
  ]];
  tourOrder.forEach(tid => {
    const o = occ[tid];
    if (!o) {
      rows.push([
        { text: tid, options: { ...cellFont, bold: true, fill: { color: COLOR.bgCard } } },
        { text: "—", options: { ...cellFont, align: "right", fill: { color: COLOR.bgCard } } },
        { text: "—", options: { ...cellFont, align: "right", fill: { color: COLOR.bgCard } } },
        { text: "—", options: { ...cellFont, align: "right", fill: { color: COLOR.bgCard } } },
        { text: "—", options: { ...cellFont, align: "right", fill: { color: COLOR.bgCard } } },
        { text: "—", options: { ...cellFont, align: "right", fill: { color: COLOR.bgCard } } },
        { text: "no data", options: { ...cellFont, align: "right", color: COLOR.text3, fill: { color: COLOR.bgCard } } },
      ]);
    } else {
      const tt = o.totales;
      const cubierto = tt.abonos_vendidos + tt.cortesias;
      const libre = Math.max(0, tt.aforo_total - cubierto);
      const ocpColor = tt.ocupacion_pct >= 60 ? COLOR.bmGreen2 : (tt.ocupacion_pct >= 40 ? COLOR.amber : COLOR.text2);
      rows.push([
        { text: tid, options: { ...cellFont, bold: true, fill: { color: COLOR.bgCard } } },
        { text: tt.aforo_total.toLocaleString('es-MX'), options: { ...cellFont, align: "right", fill: { color: COLOR.bgCard } } },
        { text: tt.abonos_vendidos.toLocaleString('es-MX'), options: { ...cellFont, align: "right", fill: { color: COLOR.bgCard } } },
        { text: tt.cortesias.toLocaleString('es-MX'), options: { ...cellFont, align: "right", color: COLOR.amber, fill: { color: COLOR.bgCard } } },
        { text: cubierto.toLocaleString('es-MX'), options: { ...cellFont, align: "right", bold: true, fill: { color: COLOR.bgCard } } },
        { text: libre.toLocaleString('es-MX'), options: { ...cellFont, align: "right", color: COLOR.text3, fill: { color: COLOR.bgCard } } },
        { text: tt.ocupacion_pct + "%", options: { ...cellFont, align: "right", bold: true, color: ocpColor, fill: { color: COLOR.bgCard } } },
      ]);
    }
  });

  s.addTable(rows, {
    x: 0.6, y: 3.5, w: 12.1, h: 2.0,
    colW: [2.0, 1.6, 1.6, 1.7, 1.6, 1.5, 2.1],
    rowH: 0.55,
    border: { type: "solid", pt: 1, color: COLOR.border },
    margin: 0.15,
  });

  s.addText("Aforo y ventas por zona vienen de los reportes de disponibilidad. Pagados + Cortesías = total cubierto. Espacio libre = aforo NO vendido (oportunidad).", {
    x: 0.6, y: SH-0.55, w: 12.1, h: 0.4,
    fontFace: FONT, fontSize: 9, italic: true,
    color: COLOR.text3, margin: 0,
  });
}

// ===== SLIDE 12: DESGLOSE DE OCUPACIÓN POR ZONA — AP25-CL26 =====
{
  const s = newSlide("Desglose por zona · AP25-CL26", "Pagados + cortesías + espacio libre por zona del torneo más reciente");

  const o = (data.occupancy || {})["AP25-CL26"];
  if (o) {
    const rowsRaw = [...o.rows].sort((a,b) => b.aforo - a.aforo);
    const headerFill = { color: COLOR.bgElev };
    const cellFont = { fontFace: FONT, fontSize: 11, color: COLOR.text1, valign: "middle" };

    const tableRows = [[
      { text: "ZONA", options: { bold: true, color: COLOR.text3, fontSize: 9, fill: headerFill, charSpacing: 2 } },
      { text: "AFORO", options: { bold: true, color: COLOR.text3, fontSize: 9, fill: headerFill, charSpacing: 2, align: "right" } },
      { text: "PAGADOS", options: { bold: true, color: COLOR.text3, fontSize: 9, fill: headerFill, charSpacing: 2, align: "right" } },
      { text: "CORTESÍAS", options: { bold: true, color: COLOR.text3, fontSize: 9, fill: headerFill, charSpacing: 2, align: "right" } },
      { text: "CUBIERTO", options: { bold: true, color: COLOR.text3, fontSize: 9, fill: headerFill, charSpacing: 2, align: "right" } },
      { text: "LIBRE", options: { bold: true, color: COLOR.text3, fontSize: 9, fill: headerFill, charSpacing: 2, align: "right" } },
      { text: "OCUPACIÓN", options: { bold: true, color: COLOR.text3, fontSize: 9, fill: headerFill, charSpacing: 2, align: "right" } },
    ]];

    rowsRaw.forEach(r => {
      const cubierto = r.abonos_vendidos + r.cortesias;
      const libre = Math.max(0, r.aforo - cubierto);
      const ocpColor = r.ocupacion_pct >= 60 ? COLOR.bmGreen2 : (r.ocupacion_pct >= 30 ? COLOR.amber : COLOR.red);
      tableRows.push([
        { text: r.zona, options: { ...cellFont, bold: true, fill: { color: COLOR.bgCard } } },
        { text: r.aforo.toLocaleString('es-MX'), options: { ...cellFont, align: "right", fill: { color: COLOR.bgCard } } },
        { text: r.abonos_vendidos.toLocaleString('es-MX'), options: { ...cellFont, align: "right", fill: { color: COLOR.bgCard } } },
        { text: r.cortesias.toLocaleString('es-MX'), options: { ...cellFont, align: "right", color: COLOR.amber, fill: { color: COLOR.bgCard } } },
        { text: cubierto.toLocaleString('es-MX'), options: { ...cellFont, align: "right", bold: true, fill: { color: COLOR.bgCard } } },
        { text: libre.toLocaleString('es-MX'), options: { ...cellFont, align: "right", color: COLOR.text3, fill: { color: COLOR.bgCard } } },
        { text: r.ocupacion_pct + "%", options: { ...cellFont, align: "right", bold: true, color: ocpColor, fill: { color: COLOR.bgCard } } },
      ]);
    });
    // Total
    const tt = o.totales;
    const tCub = tt.abonos_vendidos + tt.cortesias;
    const tLibre = Math.max(0, tt.aforo_total - tCub);
    tableRows.push([
      { text: "TOTAL", options: { ...cellFont, bold: true, color: COLOR.bmGreen2, fill: { color: COLOR.bgElev } } },
      { text: tt.aforo_total.toLocaleString('es-MX'), options: { ...cellFont, align: "right", bold: true, fill: { color: COLOR.bgElev } } },
      { text: tt.abonos_vendidos.toLocaleString('es-MX'), options: { ...cellFont, align: "right", bold: true, fill: { color: COLOR.bgElev } } },
      { text: tt.cortesias.toLocaleString('es-MX'), options: { ...cellFont, align: "right", bold: true, color: COLOR.amber, fill: { color: COLOR.bgElev } } },
      { text: tCub.toLocaleString('es-MX'), options: { ...cellFont, align: "right", bold: true, fill: { color: COLOR.bgElev } } },
      { text: tLibre.toLocaleString('es-MX'), options: { ...cellFont, align: "right", bold: true, color: COLOR.text2, fill: { color: COLOR.bgElev } } },
      { text: tt.ocupacion_pct + "%", options: { ...cellFont, align: "right", bold: true, color: COLOR.bmGreen2, fill: { color: COLOR.bgElev } } },
    ]);

    const rowH = 0.36;
    const tableH = rowH * tableRows.length;
    s.addTable(tableRows, {
      x: 0.6, y: 1.4, w: 12.1, h: tableH,
      colW: [3.4, 1.4, 1.4, 1.5, 1.4, 1.3, 1.7],
      rowH,
      border: { type: "solid", pt: 1, color: COLOR.border },
      margin: 0.1,
    });
  }
}

// ===== SLIDES 13-15: DETALLE POR TORNEO =====
tours.forEach((t, idx) => {
  const s = newSlide("Torneo "+t.label, "Detalle por categoría · revenue, volumen y ticket promedio");

  // 4 KPI cards
  const kpiY = 1.5, kpiH = 1.6, kpiW = 2.96, gap = 0.18;
  let prevRev = idx > 0 ? tours[idx-1].revenue : 0;
  let prevVol = idx > 0 ? tours[idx-1].volumen_total : 0;
  let revGr = prevRev ? Math.round((t.revenue-prevRev)/prevRev*1000)/10 : null;
  let volGr = prevVol ? Math.round((t.volumen_total-prevVol)/prevVol*1000)/10 : null;

  addKpiCard(s, 0.6, kpiY, kpiW, kpiH,
    "Revenue", "$"+(t.revenue/1e6).toFixed(2)+"M",
    revGr !== null ? (revGr>=0?"+":"")+revGr+"% vs torneo previo" : "Primer torneo",
    { featured: true });
  addKpiCard(s, 0.6+kpiW+gap, kpiY, kpiW, kpiH,
    "Abonos emitidos", fmtNum(t.volumen_total),
    volGr !== null ? (volGr>=0?"+":"")+volGr+"% vs torneo previo" : "—");
  addKpiCard(s, 0.6+(kpiW+gap)*2, kpiY, kpiW, kpiH,
    "Ticket promedio", "$"+t.ticket_promedio.toLocaleString("es-MX"),
    "Excluye cortesías");
  addKpiCard(s, 0.6+(kpiW+gap)*3, kpiY, kpiW, kpiH,
    "Cortesías", fmtNum(t.cortesias),
    t.cortesias_pct+"% del volumen");

  // Tabla detalle por categoría
  const tableY = 3.4;
  const headerFill = { color: COLOR.bgElev };
  const cellFont = { fontFace: FONT, fontSize: 11, color: COLOR.text1, valign: "middle" };

  const header = [
    { text: "CATEGORÍA", options: { bold: true, color: COLOR.text3, fontSize: 9, fill: headerFill, charSpacing: 2 } },
    { text: "ABONOS", options: { bold: true, color: COLOR.text3, fontSize: 9, fill: headerFill, charSpacing: 2, align: "right" } },
    { text: "CORTESÍAS", options: { bold: true, color: COLOR.text3, fontSize: 9, fill: headerFill, charSpacing: 2, align: "right" } },
    { text: "REVENUE", options: { bold: true, color: COLOR.text3, fontSize: 9, fill: headerFill, charSpacing: 2, align: "right" } },
    { text: "TICKET PROM.", options: { bold: true, color: COLOR.text3, fontSize: 9, fill: headerFill, charSpacing: 2, align: "right" } },
  ];
  const rows = [header];
  t.categorias.forEach(c => {
    const revStr = c.revenue >= 1e6 ? "$"+(c.revenue/1e6).toFixed(2)+"M" : (c.revenue > 0 ? "$"+(c.revenue/1e3).toFixed(0)+"K" : "—");
    rows.push([
      { text: c.categoria, options: { ...cellFont, bold: true, fill: { color: COLOR.bgCard } } },
      { text: fmtNum(c.volumen), options: { ...cellFont, align: "right", fill: { color: COLOR.bgCard } } },
      { text: fmtNum(c.cortesias), options: { ...cellFont, align: "right", color: COLOR.amber, fill: { color: COLOR.bgCard } } },
      { text: revStr, options: { ...cellFont, align: "right", bold: true, color: COLOR.bmGreen2, fill: { color: COLOR.bgCard } } },
      { text: c.ticket_promedio ? "$"+c.ticket_promedio.toLocaleString("es-MX") : "—", options: { ...cellFont, align: "right", fill: { color: COLOR.bgCard } } },
    ]);
  });

  s.addTable(rows, {
    x: 0.6, y: tableY, w: 12.1, h: SH-tableY-0.6,
    colW: [3.5, 2.0, 2.0, 2.4, 2.2],
    rowH: 0.45,
    border: { type: "solid", pt: 1, color: COLOR.border },
    margin: 0.12,
  });
});

// ===== EXPORT =====
pres.writeFile({ fileName: OUT }).then(f => console.log("Saved:", f));
