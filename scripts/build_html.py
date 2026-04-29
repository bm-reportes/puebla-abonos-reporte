"""Construye Reporte_Puebla_Abonados_2026.html — v2 dark mode."""
import json, os
from datetime import datetime

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_PATH    = os.environ.get("PUEBLA_DATA_JSON")    or os.path.join(REPO_ROOT, "data.json")
OUT_PATH     = os.environ.get("PUEBLA_HTML_OUT")     or os.path.join(REPO_ROOT, "outputs", "Reporte_Puebla_Abonados_2026.html")
CHARTJS_PATH = os.environ.get("PUEBLA_CHARTJS_PATH") or os.path.join(REPO_ROOT, "node_modules", "chart.js", "dist", "chart.umd.js")

with open(DATA_PATH) as f:
    data = json.load(f)

with open(CHARTJS_PATH) as f:
    chartjs_code = f.read()

tours = data['tournaments']
main = data['main']
renewal = data['renewal']
occ = data.get('occupancy', {})

# ---------- HTML ----------
html = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Reporte de Abonos — Club Puebla | 3 Temporadas</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<script>
""" + chartjs_code + """
</script>
<style>
  :root {
    --bg-page:    #0B0F14;
    --bg-card:    #161D24;
    --bg-card-2:  #11171E;
    --bg-elev:    #1F2830;
    --bg-input:   #232C35;
    --border:     #2A343E;
    --border-2:   #364452;
    --text-1:     #ECF1F5;
    --text-2:     #9AA5B0;
    --text-3:     #6A7682;
    --bm-green:   #00C677;
    --bm-green-2: #1FE39A;
    --bm-green-dim: rgba(0, 198, 119, 0.15);
    --bm-green-glow: rgba(0, 198, 119, 0.35);
    --bm-dark:    #253039;
    --bm-dark-2:  #3A4753;
    /* Cortesías: coral en lugar de amarillo */
    --coral:      #FF6B6B;
    --amber:      #FF6B6B;
    --red:        #FF5C61;
    --blue:       #5B8DEF;
    --purple:     #A993FF;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  html, body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: var(--text-1); background: var(--bg-page);
    -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale;
    line-height: 1.5;
  }

  /* HEADER */
  .header {
    background: linear-gradient(135deg, #0E1620 0%, #14202B 50%, #0E1620 100%);
    padding: 28px 48px 24px;
    border-bottom: 1px solid var(--border);
    position: relative;
    overflow: hidden;
  }
  .header::before {
    content: ""; position: absolute; top: -120px; right: -100px;
    width: 360px; height: 360px; border-radius: 50%;
    background: radial-gradient(circle, var(--bm-green-glow) 0%, transparent 70%);
    pointer-events: none;
  }
  .header::after {
    content: ""; position: absolute; left: 0; bottom: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent 0%, var(--bm-green) 30%, var(--bm-green-2) 70%, transparent 100%);
  }
  .header-inner { max-width: 1400px; margin: 0 auto; display: flex; align-items: center; justify-content: space-between; gap: 24px; position: relative; z-index: 1; }
  .header-title { display: flex; align-items: center; gap: 18px; }
  .bm-logo { width: 56px; height: 56px; flex-shrink: 0; filter: drop-shadow(0 4px 12px rgba(0,198,119,0.35)); }
  .header h1 { font-size: 24px; font-weight: 800; letter-spacing: -0.4px; color: var(--text-1); }
  .header .subtitle { font-size: 13px; color: var(--text-2); margin-top: 4px; font-weight: 500; }
  .header-meta { text-align: right; font-size: 12px; color: var(--text-3); }
  .header-meta strong { color: var(--text-2); }

  /* NAV */
  .nav { background: var(--bg-card); border-bottom: 1px solid var(--border); position: sticky; top: 0; z-index: 100; backdrop-filter: blur(8px); }
  .nav-inner { max-width: 1400px; margin: 0 auto; padding: 0 48px; display: flex; gap: 4px; overflow-x: auto; }
  .nav button {
    background: none; border: none; padding: 16px 22px; font-family: inherit; font-size: 13px; font-weight: 600;
    color: var(--text-2); cursor: pointer; white-space: nowrap;
    border-bottom: 2px solid transparent; transition: all 0.2s;
    letter-spacing: 0.2px;
  }
  .nav button:hover { color: var(--text-1); background: rgba(255,255,255,0.02); }
  .nav button.active { color: var(--bm-green); border-bottom-color: var(--bm-green); }

  /* MAIN */
  main { max-width: 1400px; margin: 0 auto; padding: 32px 48px 64px; }
  section { display: none; animation: fadeIn 0.25s ease; }
  section.active { display: block; }
  @keyframes fadeIn { from {opacity:0; transform: translateY(6px);} to {opacity:1; transform: translateY(0);} }

  h2 { font-size: 22px; font-weight: 800; margin-bottom: 6px; letter-spacing: -0.3px; color: var(--text-1); }
  h3 { font-size: 14px; font-weight: 700; color: var(--text-1); letter-spacing: 0.1px; }
  .section-sub { color: var(--text-2); font-size: 13px; margin-bottom: 28px; }
  .section-header { margin-bottom: 24px; }

  /* KPI CARDS */
  .kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; margin-bottom: 24px; }
  /* dashboard principal: 2 cards lado a lado */
  #dashboard > .kpi-grid:first-child { grid-template-columns: 1fr 1fr; }
  @media (max-width: 760px) { #dashboard > .kpi-grid:first-child { grid-template-columns: 1fr; } }
  .kpi {
    background: linear-gradient(160deg, var(--bg-card) 0%, var(--bg-card-2) 100%);
    border-radius: 14px; padding: 20px 22px;
    border: 1px solid var(--border);
    transition: transform 0.2s, border-color 0.2s, box-shadow 0.2s;
    position: relative; overflow: hidden;
  }
  .kpi:hover { transform: translateY(-2px); border-color: var(--border-2); box-shadow: 0 8px 24px rgba(0,0,0,0.35); }
  .kpi-label { font-size: 10px; color: var(--text-3); text-transform: uppercase; letter-spacing: 0.8px; font-weight: 700; margin-bottom: 6px; }
  .kpi-value { font-size: 28px; font-weight: 800; letter-spacing: -1px; color: var(--text-1); font-feature-settings: "tnum"; }
  .kpi-sub { font-size: 12px; color: var(--text-2); margin-top: 4px; }
  .kpi.featured {
    background: linear-gradient(135deg, var(--bm-green) 0%, #00A864 100%);
    border: none;
  }
  .kpi.featured::after {
    content: ""; position: absolute; top: -50%; right: -20%;
    width: 220px; height: 220px; border-radius: 50%;
    background: radial-gradient(circle, rgba(255,255,255,0.18) 0%, transparent 70%);
    pointer-events: none;
  }
  .kpi.featured .kpi-label { color: rgba(255,255,255,0.85); }
  .kpi.featured .kpi-value { color: white; text-shadow: 0 0 24px rgba(0,198,119,0.55), 0 0 6px rgba(255,255,255,0.3); }
  .kpi.featured .kpi-sub { color: rgba(255,255,255,0.85); }
  .kpi.revenue { background: linear-gradient(160deg, #14202B 0%, #1B2A38 100%); border: 1px solid var(--bm-green-dim); }
  .kpi.revenue .kpi-value { color: var(--bm-green-2); }

  /* CARD */
  .card {
    background: linear-gradient(180deg, var(--bg-card) 0%, var(--bg-card-2) 100%);
    border-radius: 14px; padding: 22px 24px; border: 1px solid var(--border);
  }
  .card-header { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 18px; gap: 12px; }
  .card-header h3 { font-size: 14px; font-weight: 700; }
  .card-header .meta { font-size: 11px; color: var(--text-3); text-transform: uppercase; letter-spacing: 0.6px; font-weight: 600; }

  /* GRID LAYOUTS */
  .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px; }
  .grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 16px; }
  .grid-2-1 { display: grid; grid-template-columns: 2fr 1fr; gap: 16px; margin-bottom: 16px; }
  .grid-1-2 { display: grid; grid-template-columns: 1fr 2fr; gap: 16px; margin-bottom: 16px; }
  @media (max-width: 900px) { .grid-2, .grid-3, .grid-2-1, .grid-1-2 { grid-template-columns: 1fr; } }

  /* CHART containers */
  .chart-wrap { position: relative; height: 280px; }
  .chart-wrap.tall { height: 360px; }
  .chart-wrap.short { height: 220px; }

  /* TABLE */
  table { width: 100%; border-collapse: collapse; font-size: 13px; color: var(--text-1); }
  thead th {
    text-align: left; padding: 10px 8px; font-weight: 700;
    color: var(--text-3); text-transform: uppercase; font-size: 10px; letter-spacing: 0.8px;
    border-bottom: 1px solid var(--border); background: rgba(255,255,255,0.01);
  }
  tbody td { padding: 11px 8px; border-bottom: 1px solid var(--border); font-feature-settings: "tnum"; }
  tbody tr:last-child td { border-bottom: none; }
  tbody tr:hover { background: rgba(255,255,255,0.015); }
  td.num, th.num { text-align: right; }
  td.zone { font-weight: 500; color: var(--text-1); }
  .pct-bar { display: inline-block; height: 6px; background: rgba(255,255,255,0.06); border-radius: 99px; width: 70px; vertical-align: middle; margin-right: 8px; overflow: hidden; }
  .pct-bar > span { display: block; height: 100%; background: linear-gradient(90deg, var(--bm-green) 0%, var(--bm-green-2) 100%); border-radius: 99px; }
  .pct-bar.dark > span { background: linear-gradient(90deg, var(--text-2) 0%, var(--text-1) 100%); }
  .pct-bar.amber > span { background: linear-gradient(90deg, var(--coral) 0%, #FF9696 100%); }

  .tag { display: inline-block; padding: 3px 9px; border-radius: 99px; font-size: 11px; font-weight: 700; letter-spacing: 0.2px; }
  .tag.green { background: var(--bm-green-dim); color: var(--bm-green-2); }
  .tag.gray { background: rgba(255,255,255,0.06); color: var(--text-2); }
  .tag.amber { background: rgba(255,107,107,0.15); color: var(--coral); }

  .small { font-size: 11px; opacity: 0.7; }

  /* FILTER PILLS */
  .filter-group { display: inline-flex; gap: 2px; background: var(--bg-input); border-radius: 99px; padding: 3px; align-self: center; }
  .filter-group button {
    background: transparent; border: none; color: var(--text-2);
    font-family: inherit; font-size: 11px; font-weight: 600;
    padding: 6px 14px; border-radius: 99px; cursor: pointer;
    transition: all 0.18s; letter-spacing: 0.2px;
  }
  .filter-group button:hover { color: var(--text-1); }
  .filter-group button.active { background: var(--bm-green); color: #0B0F14; }

  /* FOOTER */
  footer {
    background: var(--bg-card); border-top: 1px solid var(--border);
    padding: 24px 48px; margin-top: 48px;
  }
  .footer-inner { max-width: 1400px; margin: 0 auto; display: flex; align-items: center; justify-content: space-between; gap: 24px; width: 100%; font-size: 13px; color: var(--text-2); }
  .bm-elephant { display: flex; align-items: center; gap: 12px; color: var(--text-1); font-weight: 600; }
  .bm-elephant .bm-logo-sm { width: 32px; height: 32px; }

  @media print {
    .nav { display: none; }
    section { display: block !important; page-break-after: always; }
    body { background: white; color: black; }
  }
</style>
</head>
<body>

<!-- Reusable elephant SVG (Boletomóvil placeholder) -->
<svg width="0" height="0" style="position:absolute" aria-hidden="true">
  <defs>
    <symbol id="bm-elephant" viewBox="0 0 64 64">
      <defs>
        <linearGradient id="bmg" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stop-color="#1FE39A"/>
          <stop offset="100%" stop-color="#00A864"/>
        </linearGradient>
      </defs>
      <circle cx="32" cy="32" r="30" fill="url(#bmg)"/>
      <!-- Elephant body -->
      <path d="M19 38 C19 28, 26 22, 33 22 C40 22, 46 27, 46 35 L46 42 C46 44, 44.5 45, 43 45 L41 45 C41 47, 39.5 48, 37.5 48 L36 48 C36 46, 34.5 45, 33 45 L25 45 C22 45, 19 43, 19 38 Z" fill="white"/>
      <!-- Trunk -->
      <path d="M44 36 C46 35, 48 36, 49 38 L51 43 C50.2 43.4, 49 43, 48.5 42 L47 39 C46.5 38, 46 38, 45.5 38.5 Z" fill="white"/>
      <!-- Ear -->
      <ellipse cx="26" cy="29" rx="5" ry="6" fill="white" opacity="0.92"/>
      <!-- Eye -->
      <circle cx="38" cy="32" r="1.4" fill="#0B0F14"/>
    </symbol>
  </defs>
</svg>

<!-- HEADER -->
<header class="header">
  <div class="header-inner">
    <div class="header-title">
      <div>
        <h1>Reporte Ejecutivo de Abonos — Club Puebla</h1>
        <div class="subtitle">3 temporadas comparadas · AP23-CL24 · AP24-CL25 · AP25-CL26</div>
      </div>
    </div>
  </div>
</header>

<!-- NAV -->
<nav class="nav">
  <div class="nav-inner">
    <button class="tab-btn active" data-tab="dashboard">Dashboard Principal</button>
    <button class="tab-btn" data-tab="t1">AP23 + CL24</button>
    <button class="tab-btn" data-tab="t2">AP24 + CL25</button>
    <button class="tab-btn" data-tab="t3">AP25 + CL26</button>
  </div>
</nav>

<main>

<!-- ============================================================ -->
<!-- DASHBOARD PRINCIPAL -->
<!-- ============================================================ -->
<section id="dashboard" class="active">

  <!-- KPIs grandes -->
  <div class="kpi-grid">
    <div class="kpi featured">
      <div class="kpi-label">Total vendido (3 torneos)</div>
      <div class="kpi-value">$""" + f"{main['total_revenue']/1000000:,.1f}M" + """</div>
    </div>
    <div class="kpi">
      <div class="kpi-label">Abonos emitidos totales</div>
      <div class="kpi-value">""" + f"{main['total_volumen']:,}" + """</div>
      <div class="kpi-sub">""" + f"{main['total_pagado']:,} pagados · {main['total_cortesias']:,} cortesías" + """</div>
    </div>
  </div>

  <!-- 2 charts grandes lado a lado: REVENUE y VOLUMEN -->
  <div class="grid-2">
    <div class="card">
      <div class="card-header">
        <h3>Revenue vendido por torneo</h3>
        <span class="meta">Taquilla · Online</span>
      </div>
      <div class="chart-wrap"><canvas id="chRevenue"></canvas></div>
    </div>
    <div class="card">
      <div class="card-header">
        <h3>Abonos emitidos por torneo</h3>
        <span class="meta">Taquilla · Online</span>
      </div>
      <div class="chart-wrap"><canvas id="chVolStack"></canvas></div>
    </div>
  </div>

  <!-- Emisión por SEMESTRE (6 barras) + Ticket promedio -->
  <div class="grid-2-1">
    <div class="card">
      <div class="card-header">
        <h3>Emisión por semestre</h3>
        <span class="meta">Anual · Semestral · Cortesía — % y cantidad</span>
      </div>
      <div class="chart-wrap tall"><canvas id="chMix"></canvas></div>
    </div>
    <div class="card">
      <div class="card-header"><h3>Ticket promedio por torneo</h3><span class="meta">Excluyendo cortesías</span></div>
      <div class="chart-wrap"><canvas id="chTicket"></canvas></div>
    </div>
  </div>

  <!-- Tabla resumen comparativa -->
  <div class="card" style="margin-bottom:16px;">
    <div class="card-header"><h3>Resumen comparativo por torneo</h3><span class="meta">Cuánto se vendió, cuánto se emitió</span></div>
    <table>
      <thead>
        <tr>
          <th>Torneo</th>
          <th class="num">Revenue</th>
          <th class="num">Abonos emitidos</th>
          <th class="num">Pagados</th>
          <th class="num">Cortesías</th>
          <th class="num">% Cortesías</th>
          <th class="num">Ticket prom.</th>
        </tr>
      </thead>
      <tbody>
"""
for t in main['tournaments_summary']:
    cort_pct = round(t['cortesias']/t['volumen']*100, 1) if t['volumen'] else 0
    color = "amber" if cort_pct>=20 else ("gray" if cort_pct>=12 else "green")
    html += f'        <tr><td class="zone">{t["torneo"]}</td><td class="num"><strong style="color:var(--bm-green-2)">${t["revenue"]/1e6:,.2f}M</strong></td><td class="num">{t["volumen"]:,}</td><td class="num">{t["pagado"]:,}</td><td class="num">{t["cortesias"]:,}</td><td class="num"><span class="tag {color}">{cort_pct}%</span></td><td class="num">${t["ticket_promedio"]:,.0f}</td></tr>\n'

html += """
      </tbody>
    </table>
  </div>

  <!-- COMPARATIVA POR TIPO DE ABONO ENTRE TORNEOS -->
  <div class="card" style="margin-bottom:16px;">
    <div class="card-header">
      <h3>Revenue por tipo de abono — comparativa entre torneos</h3>
      <span class="meta">Cuánto se vendió de cada tipo en cada temporada</span>
    </div>
    <div class="chart-wrap tall"><canvas id="chCatByTour_Rev"></canvas></div>
  </div>

  <div class="card" style="margin-bottom:16px;">
    <div class="card-header">
      <h3>Abonos emitidos por tipo — comparativa entre torneos</h3>
      <span class="meta">Volumen de cada categoría en cada temporada</span>
    </div>
    <div class="chart-wrap tall"><canvas id="chCatByTour_Vol"></canvas></div>
  </div>

  <!-- Top zonas con barras agrupadas por torneo -->
  <div class="card" style="margin-bottom:16px;">
    <div class="card-header">
      <h3>Top zonas — volumen por torneo</h3>
      <span class="meta">Abonos emitidos · 3 torneos comparados</span>
    </div>
    <div class="chart-wrap" style="height: 460px;"><canvas id="chTopZonesVol"></canvas></div>
  </div>
  <div class="card" style="margin-bottom:16px;">
    <div class="card-header">
      <h3>Top zonas — revenue por torneo</h3>
      <span class="meta">Pesos vendidos · 3 torneos comparados</span>
    </div>
    <div class="chart-wrap" style="height: 460px;"><canvas id="chTopZonesRev"></canvas></div>
  </div>

  <!-- Renovación + Ocupación -->
  <div class="grid-2">
    <div class="card">
      <div class="card-header"><h3>Renovación temporada a temporada</h3><span class="meta">Solo canal Online</span></div>
      <table>
        <thead><tr><th>Transición</th><th class="num">Base prev.</th><th class="num">Renovaron</th><th class="num">Tasa</th><th class="num">Nuevos</th><th class="num">Perdidos</th></tr></thead>
        <tbody>
"""
for r in renewal:
    color = "green" if r['tasa_renovacion_pct']>=25 else ("amber" if r['tasa_renovacion_pct']>=18 else "gray")
    html += f'          <tr><td>{r["from"]} → {r["to"]}</td><td class="num">{r["abonados_prev"]:,}</td><td class="num">{r["renovaron"]:,}</td><td class="num"><span class="tag {color}">{r["tasa_renovacion_pct"]}%</span></td><td class="num" style="color:var(--bm-green-2)">+{r["nuevos"]:,}</td><td class="num" style="color:var(--red)">−{r["perdidos"]:,}</td></tr>\n'

html += """
        </tbody>
      </table>
    </div>
    <div class="card">
      <div class="card-header"><h3>Ocupación de aforo por torneo</h3><span class="meta">Pagados + cortesías cubren el aforo total</span></div>
      <table>
        <thead><tr><th>Torneo</th><th class="num">Aforo</th><th class="num">Pagados</th><th class="num">Cortesías</th><th class="num">Ocupación</th></tr></thead>
        <tbody>
"""
for tour_id in ["AP23-CL24","AP24-CL25","AP25-CL26"]:
    if tour_id in occ:
        tt = occ[tour_id]['totales']
        ocp = tt['ocupacion_pct']
        color = "green" if ocp>=60 else ("amber" if ocp>=40 else "gray")
        html += f'          <tr><td class="zone">{tour_id}</td><td class="num">{tt["aforo_total"]:,}</td><td class="num">{tt["abonos_vendidos"]:,}</td><td class="num" style="color:var(--amber)">{tt["cortesias"]:,}</td><td class="num"><span class="tag {color}">{ocp}%</span></td></tr>\n'
    else:
        html += f'          <tr><td class="zone">{tour_id}</td><td class="num">—</td><td class="num">—</td><td class="num">—</td><td class="num"><span class="tag gray">no data</span></td></tr>\n'

html += """
        </tbody>
      </table>
    </div>
  </div>

  <!-- DESGLOSE DE OCUPACIÓN POR ZONA — un torneo a la vez con filtro -->
  <div class="card" style="margin-bottom:16px;">
    <div class="card-header">
      <h3>Desglose por zona</h3>
      <div class="filter-group" id="filterOcc">
"""
occ_keys_avail = [k for k in ["AP23-CL24","AP24-CL25","AP25-CL26"] if k in occ]
for i, tour_id in enumerate(occ_keys_avail):
    cls = "active" if i == len(occ_keys_avail)-1 else ""
    html += f'        <button class="{cls}" data-tour="{tour_id}">{tour_id}</button>\n'

html += """
      </div>
    </div>
    <div id="occupancyTable"></div>
    <div class="small" style="color:var(--text-3); margin-top:14px;">Aforo y ventas por zona vienen de los reportes de disponibilidad. Pagados + Cortesías = total cubierto. Espacio libre = aforo que NO se vendió.</div>
  </div>
</section>
"""

# ---------- SUB-DASHBOARDS ----------
for idx, t in enumerate(tours):
    tab_id = f"t{idx+1}"
    rev_growth_str = vol_growth_str = ""
    if idx > 0:
        prev = tours[idx-1]
        rg = round((t['revenue']-prev['revenue'])/prev['revenue']*100,1) if prev['revenue'] else 0
        vg = round((t['volumen_total']-prev['volumen_total'])/prev['volumen_total']*100,1) if prev['volumen_total'] else 0
        rev_growth_str = f"{'+' if rg>=0 else ''}{rg}% vs torneo previo"
        vol_growth_str = f"{'+' if vg>=0 else ''}{vg}% vs torneo previo"

    html += f"""
<section id="{tab_id}">
  <div class="section-header">
    <h2>Torneo {t['label']}</h2>
    <div class="section-sub">Cuánto se vendió y qué se emitió en este torneo. Desglose por categoría, zona y canal.</div>
  </div>

  <div class="kpi-grid">
    <div class="kpi featured">
      <div class="kpi-label">Revenue vendido</div>
      <div class="kpi-value">${t['revenue']/1e6:,.2f}M</div>
      <div class="kpi-sub">{rev_growth_str or 'Primer torneo del comparativo'}</div>
    </div>
    <div class="kpi">
      <div class="kpi-label">Abonos emitidos</div>
      <div class="kpi-value">{t['volumen_total']:,}</div>
      <div class="kpi-sub">{vol_growth_str or '—'}</div>
    </div>
    <div class="kpi">
      <div class="kpi-label">Ticket promedio</div>
      <div class="kpi-value">${t['ticket_promedio']:,.0f}</div>
      <div class="kpi-sub">excluyendo cortesías</div>
    </div>
    <div class="kpi">
      <div class="kpi-label">Cortesías</div>
      <div class="kpi-value">{t['cortesias']:,}</div>
      <div class="kpi-sub">{t['cortesias_pct']}% del volumen</div>
    </div>
  </div>

  <!-- Categoría: revenue + volumen -->
  <div class="grid-2">
    <div class="card">
      <div class="card-header"><h3>Revenue por categoría</h3><span class="meta">Pesos vendidos</span></div>
      <div class="chart-wrap tall"><canvas id="chCatRev_{tab_id}"></canvas></div>
    </div>
    <div class="card">
      <div class="card-header"><h3>Abonos emitidos por categoría</h3><span class="meta">Volumen</span></div>
      <div class="chart-wrap tall"><canvas id="chCatVol_{tab_id}"></canvas></div>
    </div>
  </div>

  <!-- Tabla detalle categorías -->
  <div class="card" style="margin-bottom:16px;">
    <div class="card-header"><h3>Detalle por categoría</h3><span class="meta">{t['label']}</span></div>
    <table>
      <thead><tr><th>Categoría</th><th class="num">Abonos</th><th class="num">Cortesías</th><th class="num">Revenue</th><th class="num">Ticket prom.</th></tr></thead>
      <tbody>
"""
    for c in t['categorias']:
        rev_str = f'${c["revenue"]/1e6:,.2f}M' if c["revenue"]>=1e6 else (f'${c["revenue"]/1000:,.0f}K' if c["revenue"]>0 else '—')
        tick_str = f'${c["ticket_promedio"]:,.0f}' if c["ticket_promedio"] else '—'
        html += f'        <tr><td class="zone">{c["categoria"]}</td><td class="num">{c["volumen"]:,}</td><td class="num">{c["cortesias"]:,}</td><td class="num"><strong style="color:var(--bm-green-2)">{rev_str}</strong></td><td class="num">{tick_str}</td></tr>\n'

    html += f"""
      </tbody>
    </table>
  </div>

  <!-- Zonas: revenue + volumen -->
  <div class="grid-2">
    <div class="card">
      <div class="card-header"><h3>Top zonas — revenue</h3><span class="meta">Top 8 por pesos vendidos</span></div>
      <div class="chart-wrap tall"><canvas id="chZoneRev_{tab_id}"></canvas></div>
    </div>
    <div class="card">
      <div class="card-header"><h3>Top zonas — volumen</h3><span class="meta">Top 8 por abonos</span></div>
      <div class="chart-wrap tall"><canvas id="chZoneVol_{tab_id}"></canvas></div>
    </div>
  </div>

  <!-- Canal y Semestre -->
  <div class="grid-2">
    <div class="card">
      <div class="card-header"><h3>Revenue por canal</h3><span class="meta">Taquilla vs Online</span></div>
      <div class="chart-wrap"><canvas id="chCanRev_{tab_id}"></canvas></div>
    </div>
    <div class="card">
      <div class="card-header"><h3>Revenue por semestre</h3><span class="meta">Apertura vs Clausura</span></div>
      <div class="chart-wrap"><canvas id="chSemRev_{tab_id}"></canvas></div>
    </div>
  </div>
</section>
"""

# ---------- FOOTER + JS ----------
html += """
</main>

<script>
const DATA = """ + json.dumps(data, ensure_ascii=False) + """;

// Tabs
document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('section').forEach(s => s.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById(btn.dataset.tab).classList.add('active');
    window.scrollTo({top: 0, behavior: 'smooth'});
  });
});

// Chart.js dark defaults
Chart.defaults.font.family = "'Inter', sans-serif";
Chart.defaults.font.size = 12;
Chart.defaults.color = '#9AA5B0';
Chart.defaults.borderColor = '#2A343E';
Chart.defaults.plugins.legend.labels.usePointStyle = true;
Chart.defaults.plugins.legend.labels.boxWidth = 8;
Chart.defaults.plugins.legend.labels.boxHeight = 8;
Chart.defaults.plugins.legend.labels.color = '#ECF1F5';
Chart.defaults.plugins.tooltip.backgroundColor = '#1F2830';
Chart.defaults.plugins.tooltip.titleColor = '#ECF1F5';
Chart.defaults.plugins.tooltip.bodyColor = '#9AA5B0';
Chart.defaults.plugins.tooltip.borderColor = '#2A343E';
Chart.defaults.plugins.tooltip.borderWidth = 1;
Chart.defaults.plugins.tooltip.padding = 10;
Chart.defaults.plugins.tooltip.cornerRadius = 8;
Chart.defaults.plugins.tooltip.titleFont = { size: 13, weight: '700' };
Chart.defaults.plugins.tooltip.bodyFont = { size: 12 };

const C = {
  green:  '#00C677',
  green2: '#1FE39A',
  greenDim: 'rgba(0, 198, 119, 0.18)',
  dark2:  '#3A4753',
  coral:  '#FF6B6B',   // antes amber/amarillo
  amber:  '#FF6B6B',   // alias para compatibilidad — pero ahora coral
  red:    '#FF5C61',
  blue:   '#5B8DEF',
  purple: '#A993FF',
  gray:   '#6A7682',
};

// Make a vertical green gradient for chart bars
function vGradient(ctx, area, c1, c2) {
  const g = ctx.createLinearGradient(0, area.top, 0, area.bottom);
  g.addColorStop(0, c1);
  g.addColorStop(1, c2);
  return g;
}
function hGradient(ctx, area, c1, c2) {
  const g = ctx.createLinearGradient(area.left, 0, area.right, 0);
  g.addColorStop(0, c1);
  g.addColorStop(1, c2);
  return g;
}

const greenBar = {
  backgroundColor(ctx) {
    const chart = ctx.chart; const {ctx: c, chartArea} = chart;
    if (!chartArea) return C.green;
    return vGradient(c, chartArea, '#1FE39A', '#00A864');
  },
  borderRadius: 8,
  borderSkipped: false,
};
const greenBarH = {
  backgroundColor(ctx) {
    const chart = ctx.chart; const {ctx: c, chartArea} = chart;
    if (!chartArea) return C.green;
    return hGradient(c, chartArea, '#00A864', '#1FE39A');
  },
  borderRadius: 8,
  borderSkipped: false,
};
// Stacked: Taquilla = gris oscuro, Online = verde Boletomóvil
const navyBar = {
  backgroundColor(ctx) {
    const chart = ctx.chart; const {ctx: c, chartArea} = chart;
    if (!chartArea) return C.dark2;
    return vGradient(c, chartArea, '#4A5560', '#2C3742');
  },
  borderSkipped: false,
};
const cyanBar = {
  backgroundColor(ctx) {
    const chart = ctx.chart; const {ctx: c, chartArea} = chart;
    if (!chartArea) return C.green;
    return vGradient(c, chartArea, '#1FE39A', '#00A864');
  },
  borderSkipped: false,
};
const grayBar = { backgroundColor: '#3A4753', borderRadius: 8, borderSkipped: false };
const amberBar = { backgroundColor: C.coral, borderRadius: 8, borderSkipped: false };

const fmtMoney = v => '$' + (v >= 1e6 ? (v/1e6).toFixed(2) + 'M' : (v/1000).toFixed(0) + 'K');
const fmtMoneyFull = v => '$' + Math.round(v).toLocaleString('es-MX');
const fmtNum = v => v.toLocaleString('es-MX');

const gridStyle = { display: false };
const gridStyleSubtle = { display: false };

// Plugin: render values on top of bars
const valueLabelPlugin = {
  id: 'valueLabel',
  afterDatasetsDraw(chart, args, opts) {
    const {ctx} = chart;
    chart.data.datasets.forEach((ds, di) => {
      if (ds.hideLabels) return;
      const meta = chart.getDatasetMeta(di);
      meta.data.forEach((bar, i) => {
        const v = ds.data[i];
        if (v == null || v === 0) return;
        ctx.save();
        ctx.fillStyle = '#ECF1F5';
        ctx.font = '700 11px Inter';
        ctx.textAlign = 'center'; ctx.textBaseline = 'bottom';
        let label = (opts && opts.format) ? opts.format(v) : fmtNum(v);
        if (chart.options.indexAxis === 'y') {
          ctx.textAlign = 'left'; ctx.textBaseline = 'middle';
          ctx.fillText(label, bar.x + 6, bar.y);
        } else {
          ctx.fillText(label, bar.x, bar.y - 6);
        }
        ctx.restore();
      });
    });
  }
};

// === DASHBOARD PRINCIPAL ===

// Helper: obtener valores por canal
function getChan(t, canal, key) {
  const c = (t.canales || []).find(x => x.canal === canal);
  return c ? c[key] : 0;
}

// Plugin: muestra total arriba de barra apilada + valor dentro de cada segmento
const stackTotalPlugin = {
  id: 'stackTotal',
  afterDatasetsDraw(chart, args, opts) {
    const {ctx} = chart;
    const datasets = chart.data.datasets;
    if (!datasets.length) return;
    const fmt = (opts && opts.format) || fmtNum;
    const fmtSeg = (opts && opts.formatSeg) || fmt;
    const minSegPx = (opts && opts.minSegPx) || 28;

    // Para cada categoría: dibuja total arriba
    const lastMeta = chart.getDatasetMeta(datasets.length - 1);
    lastMeta.data.forEach((bar, i) => {
      const total = datasets.reduce((s, d) => s + (d.data[i] || 0), 0);
      if (!total) return;
      ctx.save();
      ctx.fillStyle = '#EDF2F8';
      ctx.font = '800 15px Inter';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'bottom';
      ctx.fillText(fmt(total), bar.x, bar.y - 8);
      ctx.restore();
    });

    // Para cada segmento: dibuja valor dentro si hay espacio
    datasets.forEach((ds, di) => {
      const meta = chart.getDatasetMeta(di);
      meta.data.forEach((bar, i) => {
        const v = ds.data[i];
        if (!v) return;
        const segH = Math.abs(bar.base - bar.y);
        if (segH < minSegPx) return;
        ctx.save();
        ctx.fillStyle = '#FFFFFF';
        ctx.font = '700 11px Inter';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        const cy = (bar.base + bar.y) / 2;
        ctx.fillText(fmtSeg(v), bar.x, cy);
        ctx.restore();
      });
    });
  }
};

// === Revenue stacked: Taquilla + Online ===
const chRevenueObj = new Chart(document.getElementById('chRevenue'), {
  type: 'bar',
  data: {
    labels: DATA.tournaments.map(t => t.label),
    datasets: [
      { label: 'Taquilla', data: DATA.tournaments.map(t => getChan(t,'Taquilla','revenue')), ...navyBar, borderRadius: 0 },
      { label: 'Online',   data: DATA.tournaments.map(t => getChan(t,'Online','revenue')),   ...cyanBar,  borderRadius: { topLeft: 8, topRight: 8 } },
    ]
  },
  options: {
    responsive: true, maintainAspectRatio: false,
    layout: { padding: { top: 36 } },
    plugins: {
      legend: { position: 'bottom' },
      tooltip: {
        mode: 'index',
        callbacks: {
          label: c => {
            const total = c.chart.data.datasets.reduce((s,d) => s + (d.data[c.dataIndex] || 0), 0);
            const pct = total ? (c.parsed.y / total * 100).toFixed(1) : 0;
            return c.dataset.label + ': ' + fmtMoneyFull(c.parsed.y) + '  (' + pct + '%)';
          },
          footer: items => 'Total: ' + fmtMoneyFull(items.reduce((s,x) => s + x.parsed.y, 0))
        }
      },
      stackTotal: { format: fmtMoney, formatSeg: fmtMoney, minSegPx: 30 }
    },
    scales: {
      x: { stacked: true, grid: { display: false }, ticks: { color: '#99A8C0', font: { weight: '600' } } },
      y: { stacked: true, beginAtZero: true, grid: { display: false }, ticks: { callback: v => fmtMoney(v), color: '#6B7C95' } }
    }
  },
  plugins: [stackTotalPlugin]
});

// Desglose de ocupación por zona — render dinámico según torneo
function renderOccupancy(tourId) {
  const data = (DATA.occupancy || {})[tourId];
  const cont = document.getElementById('occupancyTable');
  if (!data) { cont.innerHTML = '<div style="color:var(--text-3); padding: 24px 0;">Sin datos para este torneo.</div>'; return; }
  const rows = [...data.rows].sort((a,b) => b.aforo - a.aforo);
  let html = '<table style="margin-top:8px;"><thead><tr>'
    + '<th>Zona</th>'
    + '<th class="num">Aforo</th>'
    + '<th class="num">Pagados</th>'
    + '<th class="num">Cortesías</th>'
    + '<th class="num">Cubierto</th>'
    + '<th class="num">Libre</th>'
    + '<th>Ocupación</th>'
    + '</tr></thead><tbody>';
  rows.forEach(r => {
    const cubierto = r.abonos_vendidos + r.cortesias;
    const libre = Math.max(0, r.aforo - cubierto);
    const ocp = r.ocupacion_pct;
    // Stacked bar visual: pagado (verde) + cortesía (ámbar) + libre (gris)
    const pPag  = r.aforo > 0 ? (r.abonos_vendidos/r.aforo*100) : 0;
    const pCort = r.aforo > 0 ? (r.cortesias/r.aforo*100) : 0;
    const pLib  = Math.max(0, 100 - pPag - pCort);
    const stackBar = `<div style="display:flex; height:8px; width:160px; border-radius:99px; overflow:hidden; background:rgba(255,255,255,0.06);"><div style="background:var(--bm-green); width:${pPag}%"></div><div style="background:var(--amber); width:${pCort}%"></div><div style="background:transparent; width:${pLib}%"></div></div>`;
    html += `<tr>
      <td class="zone">${r.zona}</td>
      <td class="num">${r.aforo.toLocaleString('es-MX')}</td>
      <td class="num">${r.abonos_vendidos.toLocaleString('es-MX')}</td>
      <td class="num" style="color:var(--amber)">${r.cortesias.toLocaleString('es-MX')}</td>
      <td class="num"><strong>${cubierto.toLocaleString('es-MX')}</strong></td>
      <td class="num" style="color:var(--text-3)">${libre.toLocaleString('es-MX')}</td>
      <td><div style="display:flex; align-items:center; gap:10px;">${stackBar}<span style="font-weight:700; min-width:48px;">${ocp}%</span></div></td>
    </tr>`;
  });
  // Fila total
  const t = data.totales;
  const tCub = t.abonos_vendidos + t.cortesias;
  const tLibre = Math.max(0, t.aforo_total - tCub);
  html += `<tr style="border-top:2px solid var(--border)"><td class="zone" style="color:var(--bm-green-2);font-weight:700">TOTAL</td><td class="num"><strong>${t.aforo_total.toLocaleString('es-MX')}</strong></td><td class="num"><strong>${t.abonos_vendidos.toLocaleString('es-MX')}</strong></td><td class="num" style="color:var(--amber)"><strong>${t.cortesias.toLocaleString('es-MX')}</strong></td><td class="num"><strong>${tCub.toLocaleString('es-MX')}</strong></td><td class="num" style="color:var(--text-3)">${tLibre.toLocaleString('es-MX')}</td><td><span class="tag green">${t.ocupacion_pct}%</span></td></tr>`;
  html += '</tbody></table>';
  cont.innerHTML = html;
}
// Init con el torneo activo
const occActive = document.querySelector('#filterOcc button.active');
if (occActive) renderOccupancy(occActive.dataset.tour);
document.querySelectorAll('#filterOcc button').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('#filterOcc button').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    renderOccupancy(btn.dataset.tour);
  });
});

// === Abonos emitidos stacked: Taquilla + Online ===
new Chart(document.getElementById('chVolStack'), {
  type: 'bar',
  data: {
    labels: DATA.tournaments.map(t => t.label),
    datasets: [
      { label: 'Taquilla', data: DATA.tournaments.map(t => getChan(t,'Taquilla','volumen')), ...navyBar, borderRadius: 0 },
      { label: 'Online',   data: DATA.tournaments.map(t => getChan(t,'Online','volumen')),   ...cyanBar,  borderRadius: { topLeft: 8, topRight: 8 } }
    ]
  },
  options: {
    responsive: true, maintainAspectRatio: false,
    layout: { padding: { top: 36 } },
    plugins: {
      legend: { position: 'bottom' },
      tooltip: {
        mode: 'index',
        callbacks: {
          label: c => {
            const total = c.chart.data.datasets.reduce((s,d) => s + (d.data[c.dataIndex] || 0), 0);
            const pct = total ? (c.parsed.y / total * 100).toFixed(1) : 0;
            return c.dataset.label + ': ' + fmtNum(c.parsed.y) + '  (' + pct + '%)';
          },
          footer: items => 'Total: ' + fmtNum(items.reduce((s,x) => s + x.parsed.y, 0))
        }
      },
      stackTotal: { format: fmtNum, formatSeg: fmtNum, minSegPx: 30 }
    },
    scales: {
      x: { stacked: true, grid: { display: false }, ticks: { color: '#99A8C0', font: { weight: '600' } } },
      y: { stacked: true, beginAtZero: true, grid: { display: false }, ticks: { callback: v => fmtNum(v), color: '#6B7C95' } }
    }
  },
  plugins: [stackTotalPlugin]
});

// Emisión por SEMESTRE (6 barras: AP23, CL24, AP24, CL25, AP25, CL26)
// Stacked horizontal con % (Anual / Semestral / Cortesía), tooltip muestra % + cantidad
const semData = DATA.main.mix_emision_semestre;
new Chart(document.getElementById('chMix'), {
  type: 'bar',
  data: {
    labels: semData.map(m => m.semestre),
    datasets: [
      { label: 'Anual',     data: semData.map(m => m.Anual_pct),     nData: semData.map(m => m.Anual_n),     backgroundColor: C.green,  borderRadius: 6, borderSkipped: false },
      { label: 'Semestral', data: semData.map(m => m.Semestral_pct), nData: semData.map(m => m.Semestral_n), backgroundColor: C.dark2,  borderRadius: 0, borderSkipped: false },
      { label: 'Cortesía',  data: semData.map(m => m.Cortesía_pct),  nData: semData.map(m => m.Cortesía_n),  backgroundColor: C.amber,  borderRadius: 6, borderSkipped: false },
    ]
  },
  options: {
    indexAxis: 'y',
    responsive: true, maintainAspectRatio: false,
    plugins: {
      legend: { position: 'bottom' },
      tooltip: {
        callbacks: {
          title: items => items[0].label + ' — ' + fmtNum(semData[items[0].dataIndex].total) + ' abonos',
          label: c => {
            const n = c.dataset.nData[c.dataIndex];
            return c.dataset.label + ': ' + c.parsed.x + '%  (' + fmtNum(n) + ')';
          }
        }
      }
    },
    scales: {
      x: { stacked: true, max: 100, grid: gridStyle, ticks: { callback: v => v + '%' } },
      y: { stacked: true, grid: { display: false }, ticks: { color: '#ECF1F5', font: { weight: '700', size: 12 } } }
    }
  },
  // plugin custom para mostrar cantidad dentro de cada segmento si es ancho suficiente
  plugins: [{
    id: 'segLabels',
    afterDatasetsDraw(chart) {
      const {ctx} = chart;
      chart.data.datasets.forEach((ds, di) => {
        const meta = chart.getDatasetMeta(di);
        meta.data.forEach((bar, i) => {
          const pct = ds.data[i];
          const n = ds.nData[i];
          if (pct < 6) return; // skip if too narrow
          const cx = (bar.base + bar.x) / 2;
          const cy = bar.y;
          ctx.save();
          ctx.fillStyle = ds.backgroundColor === C.dark2 ? '#ECF1F5' : '#0B0F14';
          ctx.font = '700 11px Inter';
          ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
          ctx.fillText(pct + '% · ' + fmtNum(n), cx, cy);
          ctx.restore();
        });
      });
    }
  }]
});

// Ticket promedio por torneo
new Chart(document.getElementById('chTicket'), {
  type: 'bar',
  data: {
    labels: DATA.tournaments.map(t => t.label),
    datasets: [{ data: DATA.tournaments.map(t => t.ticket_promedio), ...greenBar }]
  },
  options: {
    responsive: true, maintainAspectRatio: false,
    layout: { padding: { top: 24 } },
    plugins: {
      legend: { display: false },
      tooltip: { callbacks: { label: c => fmtMoneyFull(c.parsed.y) } },
      valueLabel: { format: v => '$' + Math.round(v).toLocaleString('es-MX') }
    },
    scales: {
      x: { grid: { display: false }, ticks: { color: '#9AA5B0', font: { weight: '600' } } },
      y: { beginAtZero: true, grid: gridStyle, ticks: { callback: v => '$' + Math.round(v).toLocaleString('es-MX') } }
    }
  },
  plugins: [valueLabelPlugin]
});

// Top zonas — volumen agrupado por torneo (3 barras por zona)
const tourLabels = DATA.tournaments.map(t => t.label);
const tourIds = DATA.tournaments.map(t => t.torneo);
// Verde brillante para el último torneo, grises para los previos
const tourBarColors = ['#4A5560', '#8A99A8', '#00E089'];

// Estilo común de leyenda — cuadros más grandes y centrada para que los 3 items se vean
const groupedLegend = {
  position: 'top', align: 'center',
  labels: {
    usePointStyle: false,
    boxWidth: 16, boxHeight: 12,
    padding: 18,
    color: '#ECF1F5',
    font: { size: 12, weight: '600' }
  }
};

const zonesVol = DATA.main.top_zonas_by_tour_vol;
new Chart(document.getElementById('chTopZonesVol'), {
  type: 'bar',
  data: {
    labels: zonesVol.map(z => z.zona),
    datasets: tourIds.map((tid, i) => ({
      label: tourLabels[i],
      data: zonesVol.map(z => z[tid] || 0),
      backgroundColor: tourBarColors[i],
      borderRadius: 6,
      borderSkipped: false,
    }))
  },
  options: {
    indexAxis: 'y',
    responsive: true, maintainAspectRatio: false,
    layout: { padding: { right: 16, top: 8 } },
    plugins: {
      legend: groupedLegend,
      tooltip: {
        mode: 'index',
        callbacks: { label: c => c.dataset.label + ': ' + fmtNum(c.parsed.x) + ' abonos' }
      }
    },
    scales: {
      x: { beginAtZero: true, grid: gridStyle, ticks: { callback: v => fmtNum(v) } },
      y: { grid: { display: false }, ticks: { color: '#ECF1F5', font: { size: 11, weight: '600' } } }
    }
  }
});

// Top zonas — revenue agrupado por torneo
const zonesRev = DATA.main.top_zonas_by_tour_rev;
new Chart(document.getElementById('chTopZonesRev'), {
  type: 'bar',
  data: {
    labels: zonesRev.map(z => z.zona),
    datasets: tourIds.map((tid, i) => ({
      label: tourLabels[i],
      data: zonesRev.map(z => z[tid+'_rev'] || 0),
      backgroundColor: tourBarColors[i],
      borderRadius: 6,
      borderSkipped: false,
    }))
  },
  options: {
    indexAxis: 'y',
    responsive: true, maintainAspectRatio: false,
    layout: { padding: { right: 16, top: 8 } },
    plugins: {
      legend: groupedLegend,
      tooltip: {
        mode: 'index',
        callbacks: { label: c => c.dataset.label + ': ' + fmtMoneyFull(c.parsed.x) }
      }
    },
    scales: {
      x: { beginAtZero: true, grid: gridStyle, ticks: { callback: v => fmtMoney(v) } },
      y: { grid: { display: false }, ticks: { color: '#ECF1F5', font: { size: 11, weight: '600' } } }
    }
  }
});

// === COMPARATIVA POR TIPO DE ABONO ENTRE TORNEOS ===
// Reúne todas las categorías que aparecen en los 3 torneos y muestra
// barras agrupadas (una por torneo) por categoría
(function() {
  const allCats = new Set();
  DATA.tournaments.forEach(t => t.categorias.forEach(c => allCats.add(c.categoria)));
  // Orden: por revenue máximo a través de los torneos
  const catList = Array.from(allCats).map(cat => {
    const totalRev = DATA.tournaments.reduce((s,t) => {
      const c = t.categorias.find(x => x.categoria === cat);
      return s + (c ? c.revenue : 0);
    }, 0);
    const totalVol = DATA.tournaments.reduce((s,t) => {
      const c = t.categorias.find(x => x.categoria === cat);
      return s + (c ? c.volumen : 0);
    }, 0);
    return { cat, totalRev, totalVol };
  }).sort((a,b) => b.totalRev - a.totalRev);

  const catLabels = catList.map(x => x.cat);

  const tourColors = ['#4A5560', '#8A99A8', '#00E089'];  // gris oscuro · gris claro · verde brillante
  const tourBorderColors = tourColors;

  function tourDataset(tour, idx, valueKey) {
    return {
      label: tour.label,
      data: catLabels.map(cat => {
        const c = tour.categorias.find(x => x.categoria === cat);
        return c ? c[valueKey] : 0;
      }),
      backgroundColor: tourColors[idx],
      borderColor: tourBorderColors[idx],
      borderWidth: idx===2 ? 0 : 0,
      borderRadius: 6,
      borderSkipped: false,
      hideLabels: true,
    };
  }

  // Revenue por tipo entre torneos
  new Chart(document.getElementById('chCatByTour_Rev'), {
    type: 'bar',
    data: {
      labels: catLabels,
      datasets: DATA.tournaments.map((t, i) => tourDataset(t, i, 'revenue'))
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      layout: { padding: { top: 12 } },
      plugins: {
        legend: groupedLegend,
        tooltip: {
          mode: 'index',
          callbacks: { label: c => c.dataset.label + ': ' + fmtMoneyFull(c.parsed.y) }
        }
      },
      scales: {
        x: { grid: { display: false }, ticks: { color: '#9AA5B0', font: { size: 11, weight: '600' }, maxRotation: 35, minRotation: 0 } },
        y: { beginAtZero: true, grid: gridStyle, ticks: { callback: v => fmtMoney(v) } }
      }
    }
  });

  // Volumen por tipo entre torneos
  new Chart(document.getElementById('chCatByTour_Vol'), {
    type: 'bar',
    data: {
      labels: catLabels,
      datasets: DATA.tournaments.map((t, i) => tourDataset(t, i, 'volumen'))
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      layout: { padding: { top: 12 } },
      plugins: {
        legend: groupedLegend,
        tooltip: {
          mode: 'index',
          callbacks: { label: c => c.dataset.label + ': ' + fmtNum(c.parsed.y) + ' abonos' }
        }
      },
      scales: {
        x: { grid: { display: false }, ticks: { color: '#9AA5B0', font: { size: 11, weight: '600' }, maxRotation: 35, minRotation: 0 } },
        y: { beginAtZero: true, grid: gridStyle, ticks: { callback: v => fmtNum(v) } }
      }
    }
  });
})();

// === SUB-DASHBOARDS ===
DATA.tournaments.forEach((t, idx) => {
  const tabId = 't' + (idx+1);

  const cats = t.categorias.slice(0, 8);
  // Revenue por categoría
  new Chart(document.getElementById('chCatRev_'+tabId), {
    type: 'bar',
    data: {
      labels: cats.map(c => c.categoria),
      datasets: [{ data: cats.map(c => c.revenue), ...greenBarH }]
    },
    options: {
      indexAxis: 'y',
      responsive: true, maintainAspectRatio: false,
      layout: { padding: { right: 70 } },
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { label: c => fmtMoneyFull(c.parsed.x) } },
        valueLabel: { format: v => v >= 1e6 ? '$'+(v/1e6).toFixed(2)+'M' : (v>0 ? '$'+(v/1000).toFixed(0)+'K' : '—') }
      },
      scales: {
        x: { beginAtZero: true, grid: gridStyle, ticks: { callback: v => fmtMoney(v) } },
        y: { grid: { display: false }, ticks: { color: '#ECF1F5', font: { size: 11 } } }
      }
    },
    plugins: [valueLabelPlugin]
  });

  // Volumen por categoría (gris)
  new Chart(document.getElementById('chCatVol_'+tabId), {
    type: 'bar',
    data: {
      labels: cats.map(c => c.categoria),
      datasets: [{ data: cats.map(c => c.volumen), backgroundColor: C.dark2, borderRadius: 8, borderSkipped: false }]
    },
    options: {
      indexAxis: 'y',
      responsive: true, maintainAspectRatio: false,
      layout: { padding: { right: 60 } },
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { label: c => fmtNum(c.parsed.x) + ' abonos' } },
        valueLabel: { format: fmtNum }
      },
      scales: {
        x: { beginAtZero: true, grid: gridStyle, ticks: { callback: v => fmtNum(v) } },
        y: { grid: { display: false }, ticks: { color: '#ECF1F5', font: { size: 11 } } }
      }
    },
    plugins: [valueLabelPlugin]
  });

  // Top zonas — revenue
  const zonasRev = [...t.zonas].sort((a,b)=>b.revenue-a.revenue).slice(0,8);
  new Chart(document.getElementById('chZoneRev_'+tabId), {
    type: 'bar',
    data: {
      labels: zonasRev.map(z => z.zona),
      datasets: [{ data: zonasRev.map(z => z.revenue), ...greenBarH }]
    },
    options: {
      indexAxis: 'y',
      responsive: true, maintainAspectRatio: false,
      layout: { padding: { right: 70 } },
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { label: c => fmtMoneyFull(c.parsed.x) } },
        valueLabel: { format: fmtMoney }
      },
      scales: {
        x: { beginAtZero: true, grid: gridStyle, ticks: { callback: v => fmtMoney(v) } },
        y: { grid: { display: false }, ticks: { color: '#ECF1F5', font: { size: 11 } } }
      }
    },
    plugins: [valueLabelPlugin]
  });

  // Top zonas — volumen
  const zonasVol = t.zonas.slice(0, 8);
  new Chart(document.getElementById('chZoneVol_'+tabId), {
    type: 'bar',
    data: {
      labels: zonasVol.map(z => z.zona),
      datasets: [{ data: zonasVol.map(z => z.volumen), backgroundColor: C.dark2, borderRadius: 8, borderSkipped: false }]
    },
    options: {
      indexAxis: 'y',
      responsive: true, maintainAspectRatio: false,
      layout: { padding: { right: 60 } },
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { label: c => fmtNum(c.parsed.x) + ' abonos' } },
        valueLabel: { format: fmtNum }
      },
      scales: {
        x: { beginAtZero: true, grid: gridStyle, ticks: { callback: v => fmtNum(v) } },
        y: { grid: { display: false }, ticks: { color: '#ECF1F5', font: { size: 11 } } }
      }
    },
    plugins: [valueLabelPlugin]
  });

  // Revenue por canal
  new Chart(document.getElementById('chCanRev_'+tabId), {
    type: 'bar',
    data: {
      labels: t.canales.map(c => c.canal),
      datasets: [{ data: t.canales.map(c => c.revenue), ...greenBar }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      layout: { padding: { top: 28 } },
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { label: c => fmtMoneyFull(c.parsed.y) } },
        valueLabel: { format: fmtMoney }
      },
      scales: {
        x: { grid: { display: false }, ticks: { color: '#9AA5B0', font: { weight: '600' } } },
        y: { beginAtZero: true, grid: gridStyle, ticks: { callback: v => fmtMoney(v) } }
      }
    },
    plugins: [valueLabelPlugin]
  });

  // Revenue por semestre
  new Chart(document.getElementById('chSemRev_'+tabId), {
    type: 'bar',
    data: {
      labels: t.semestres.map(s => s.semestre),
      datasets: [{ data: t.semestres.map(s => s.revenue), ...greenBar }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      layout: { padding: { top: 28 } },
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { label: c => fmtMoneyFull(c.parsed.y) } },
        valueLabel: { format: fmtMoney }
      },
      scales: {
        x: { grid: { display: false }, ticks: { color: '#9AA5B0', font: { weight: '600' } } },
        y: { beginAtZero: true, grid: gridStyle, ticks: { callback: v => fmtMoney(v) } }
      }
    },
    plugins: [valueLabelPlugin]
  });
});
</script>

</body>
</html>
"""

os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
with open(OUT_PATH, "w", encoding="utf-8") as f:
    f.write(html)

print(f"HTML guardado: {OUT_PATH}")
print(f"Tamaño: {os.path.getsize(OUT_PATH):,} bytes")
