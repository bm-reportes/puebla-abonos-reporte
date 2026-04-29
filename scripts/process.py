"""
Pipeline de procesamiento — Reporte de Abonos Club Puebla.
Lee todos los Excels de transacciones de las subcarpetas (AP23..CL26),
limpia, normaliza y agrega métricas. Lee archivos de disponibilidad
por zona desde la raíz para % de ocupación.
Salida: data.json (consumido por el HTML).
"""
import pandas as pd
import os, re, json, unicodedata
from datetime import datetime
from collections import defaultdict, Counter

# Configuración por env var con fallback al layout estándar (data en ../Puebla relativo al repo)
ROOT = os.environ.get("PUEBLA_DATA_DIR") or os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "Puebla")
)
OUT_JSON = os.environ.get("PUEBLA_DATA_JSON") or os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "data.json")
)

# ---------- helpers ----------
def norm(s):
    if s is None or (isinstance(s, float) and pd.isna(s)):
        return ""
    s = str(s).strip()
    return s

def lower_no_accents(s):
    s = norm(s).lower()
    s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
    return s

def to_num(v):
    if v is None: return 0.0
    if isinstance(v,(int,float)) and not pd.isna(v): return float(v)
    s = str(v).strip()
    if s in ("","-","nan","NaN","NAN","None"): return 0.0
    s = s.replace("$","").replace(",","")
    try: return float(s)
    except: return 0.0

def is_junk_evento(s):
    s = norm(s)
    if s == "" or s == "-" or s.lower() == "nan": return True
    if s.startswith("[Deshaib"): return True
    if s in ("ADMINISTRADORES","Venta en Línea","Venta en linea","TOTAL"): return True
    return False

# ---------- categorización ----------
TOURNAMENTS = {
    "AP23": "AP23-CL24",
    "CL24": "AP23-CL24",
    "AP24": "AP24-CL25",
    "CL25": "AP24-CL25",
    "AP25": "AP25-CL26",
    "CL26": "AP25-CL26",
}
TOURNAMENT_LABEL = {
    "AP23-CL24": "AP23 + CL24",
    "AP24-CL25": "AP24 + CL25",
    "AP25-CL26": "AP25 + CL26",
}
TOURNAMENT_ORDER = ["AP23-CL24", "AP24-CL25", "AP25-CL26"]

def categorize(filename, evento, tipo, semester):
    """Devuelve (categoria, formato, duracion)."""
    fn = lower_no_accents(filename)
    ev = lower_no_accents(evento)
    tp = lower_no_accents(tipo)

    # categoría
    if "kids" in fn or "kids" in ev:
        cat = "Kids"
    elif "universitario" in fn or "universitario" in ev:
        cat = "Universitarios"
    elif "socio" in fn or "socio" in ev:
        cat = "Socio Puebla"
    elif "referido" in fn or "referido" in ev:
        cat = "Referidos"
    elif "palco" in fn or "platea" in fn or "palco" in ev or "plateas" in ev:
        cat = "Palcos y Plateas"
    elif "ex-abonado" in fn or "ex abonado" in fn or "ex-abonado" in ev:
        cat = "Ex-abonado"
    elif "renovacion" in fn:
        cat = "Renovación"
    elif "nuevo abonado" in fn:
        cat = "Nuevo abonado"
    elif "cortesia" in fn or "cortesia" in tp:
        cat = "Cortesía"
    else:
        cat = "Franjabono regular"

    # formato (digital / fisico)
    is_cortesia_tipo = "cortesia" in tp
    if is_cortesia_tipo:
        formato = "Cortesía"
    elif "digital" in ev or "digital" in fn:
        formato = "Digital"
    elif "fisico" in ev or "fisico" in fn:
        formato = "Físico"
    elif "palco" in ev:
        formato = "Físico"  # palco es físico por defecto
    else:
        formato = "Físico"  # default histórico

    # duración
    if "anual" in ev or "anual" in fn:
        duracion = "Anual"
    elif "semestral" in ev or "semestral" in fn:
        duracion = "Semestral"
    else:
        # Por torneo: AP23/CL24/AP24/CL25 todo era semestral
        # AP25-CL26 introdujo modalidad anual, pero los archivos no anuales son semestrales
        duracion = "Semestral"

    return cat, formato, duracion

# ---------- canal ----------
def channel(medio_compra, vendido_por):
    m = lower_no_accents(medio_compra)
    v = lower_no_accents(vendido_por)
    if "taquilla" in m or m == "" or m == "-":
        return "Taquilla"
    if "venta en linea" in v or "venta en línea" in v:
        return "Online"
    # Frame V3, IOS, Android, etc.
    return "Online"

# ---------- leer transacciones ----------
# Archivos a excluir del análisis (decisión del cliente)
EXCLUDE_FILES = {
    ("AP25", "Anual Palcos y Plaetas.xlsx"),  # Palcos y Plateas AP25-CL26 — fuera del comparativo
}

records = []
read_log = []
for sem in ["AP23","CL24","AP24","CL25","AP25","CL26"]:
    folder = os.path.join(ROOT, sem)
    if not os.path.isdir(folder): continue
    for fname in sorted(os.listdir(folder)):
        if not fname.endswith(".xlsx"): continue
        if (sem, fname) in EXCLUDE_FILES:
            read_log.append({"file": f"{sem}/{fname}", "skipped": "excluido por configuración"})
            continue
        full = os.path.join(folder, fname)
        try:
            df = pd.read_excel(full, header=2)
        except Exception as e:
            read_log.append({"file":f"{sem}/{fname}", "error": str(e)})
            continue
        # filter junk rows
        df = df[df['NÚMERO DE ORDEN'].notna()].copy()
        df = df[~df['EVENTO'].astype(str).map(is_junk_evento)].copy()
        n = len(df)
        if n == 0:
            read_log.append({"file":f"{sem}/{fname}", "rows":0})
            continue

        for _, r in df.iterrows():
            evento  = norm(r.get('EVENTO'))
            tipo    = norm(r.get('TIPO'))
            zona    = norm(r.get('ZONA')) or "(sin zona)"
            medio   = norm(r.get('MEDIO DE COMPRA'))
            vend_por= norm(r.get('VENDIDO POR'))
            precio  = to_num(r.get('PRECIO'))
            descuento = to_num(r.get('DESCUENTO'))
            subtotal = to_num(r.get('SUBTOTAL'))
            email = lower_no_accents(r.get('CORREO ELECTRÓNICO')) if 'CORREO ELECTRÓNICO' in df.columns else ""
            email_alt = lower_no_accents(r.get('CORREO USUARIO')) if 'CORREO USUARIO' in df.columns else ""
            email_use = email or email_alt
            fecha = norm(r.get('FECHA'))
            n_orden = norm(r.get('NÚMERO DE ORDEN'))
            asiento = norm(r.get('ASIENTO'))

            cat, formato, duracion = categorize(fname, evento, tipo, sem)
            chan = channel(medio, vend_por)

            # Cortesía: cualquier orden con SUBTOTAL = 0 (sin importar tipo o archivo)
            # incluye también las cortesías explícitas (TIPO='Cortesia')
            subtotal_raw = norm(r.get('SUBTOTAL'))
            is_zero_subtotal = (subtotal_raw == "-") or (subtotal == 0)
            es_cortesia = (lower_no_accents(tipo) == "cortesia") or is_zero_subtotal
            if es_cortesia:
                cat_emision = "Cortesía"
                revenue = 0.0
            else:
                cat_emision = formato  # Digital/Físico
                revenue = subtotal

            records.append({
                "torneo": TOURNAMENTS[sem],
                "semestre": sem,
                "archivo": fname,
                "evento": evento,
                "tipo": tipo,
                "zona": zona,
                "medio_compra": medio,
                "vendido_por": vend_por,
                "canal": chan,
                "precio": precio,
                "descuento": descuento,
                "subtotal": subtotal,
                "revenue": revenue,
                "es_cortesia": es_cortesia,
                "categoria": cat,
                "formato": formato,
                "cat_emision": cat_emision,
                "duracion": duracion,
                "email": email_use,
                "fecha": fecha,
                "n_orden": n_orden,
                "asiento": asiento,
            })
        read_log.append({"file":f"{sem}/{fname}", "rows":n, "kept": sum(1 for x in records[-n:] if x is not None)})

print(f"\nTotal transacciones cargadas: {len(records)}")
df_all = pd.DataFrame(records)

# ---------- métricas ----------
def safe_div(a,b):
    return (a/b) if b else 0.0

def round_money(v):
    return round(v, 0)

result = {
    "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    "tournaments": [],
    "main": {},
    "renewal": {},
    "occupancy": {},
    "notes": [],
}

# Por torneo
totals_by_tournament = {}
for tour in TOURNAMENT_ORDER:
    sub = df_all[df_all['torneo']==tour].copy()
    if len(sub)==0:
        continue

    n_total = len(sub)
    n_cortesias = int(sub['es_cortesia'].sum())
    n_pagados  = n_total - n_cortesias
    revenue_total = float(sub['revenue'].sum())

    # mix emisión
    mix_em = sub.groupby('cat_emision').size().to_dict()
    # mix duración
    mix_dur = sub.groupby('duracion').size().to_dict()
    # mix categoría
    mix_cat = sub.groupby('categoria').size().to_dict()

    # por categoría: volumen y revenue
    cat_breakdown = []
    for cat, grp in sub.groupby('categoria'):
        vol = len(grp)
        rev = float(grp['revenue'].sum())
        cort = int(grp['es_cortesia'].sum())
        cat_breakdown.append({
            "categoria": cat,
            "volumen": vol,
            "revenue": round_money(rev),
            "cortesias": cort,
            "ticket_promedio": round_money(safe_div(rev, vol-cort)) if (vol-cort)>0 else 0,
        })
    cat_breakdown.sort(key=lambda x: -x['volumen'])

    # por zona (excluye filas sin zona — ruido)
    zone_breakdown = []
    for zona, grp in sub.groupby('zona'):
        if zona == "(sin zona)": continue
        vol = len(grp)
        rev = float(grp['revenue'].sum())
        zone_breakdown.append({
            "zona": zona,
            "volumen": vol,
            "revenue": round_money(rev),
        })
    zone_breakdown.sort(key=lambda x: -x['volumen'])

    # por canal
    chan_breakdown = sub.groupby('canal').agg(
        vol=('canal','size'),
        rev=('revenue','sum'),
        cort=('es_cortesia','sum'),
    ).reset_index().to_dict(orient='records')

    # por semestre (AP vs CL)
    sem_breakdown = sub.groupby('semestre').agg(
        vol=('semestre','size'),
        rev=('revenue','sum'),
        cort=('es_cortesia','sum'),
    ).reset_index().to_dict(orient='records')

    # por duración
    dur_breakdown = sub.groupby('duracion').agg(
        vol=('duracion','size'),
        rev=('revenue','sum'),
        cort=('es_cortesia','sum'),
    ).reset_index().to_dict(orient='records')

    # por duración con split pagado vs cortesia (para chart sin negativos)
    dur_split = []
    for dur, grp in sub.groupby('duracion'):
        cort_cnt = int(grp['es_cortesia'].sum())
        dur_split.append({
            "duracion": dur,
            "pagado": int(len(grp) - cort_cnt),
            "cortesia": cort_cnt,
            "total": int(len(grp)),
        })

    # por tipo (digital/fisico/cortesia)
    em_breakdown = sub.groupby('cat_emision').agg(
        vol=('cat_emision','size'),
        rev=('revenue','sum'),
    ).reset_index().to_dict(orient='records')

    # ticket promedio (excluyendo cortesías)
    pagados = sub[~sub['es_cortesia']]
    ticket_avg = round_money(safe_div(float(pagados['revenue'].sum()), len(pagados))) if len(pagados)>0 else 0

    totals_by_tournament[tour] = {
        "torneo": tour,
        "label": TOURNAMENT_LABEL[tour],
        "volumen_total": n_total,
        "volumen_pagado": n_pagados,
        "cortesias": n_cortesias,
        "cortesias_pct": round(safe_div(n_cortesias, n_total)*100, 1),
        "revenue": round_money(revenue_total),
        "ticket_promedio": ticket_avg,
        "categorias": cat_breakdown,
        "zonas": zone_breakdown,
        "canales": [
            {"canal": x['canal'], "volumen": int(x['vol']), "revenue": round_money(float(x['rev'])), "cortesias": int(x['cort'])}
            for x in chan_breakdown
        ],
        "semestres": [
            {"semestre": x['semestre'], "volumen": int(x['vol']), "revenue": round_money(float(x['rev'])), "cortesias": int(x['cort'])}
            for x in sem_breakdown
        ],
        "duracion": [
            {"duracion": x['duracion'], "volumen": int(x['vol']), "revenue": round_money(float(x['rev'])), "cortesias": int(x['cort'])}
            for x in dur_breakdown
        ],
        "duracion_split": dur_split,
        "emision": [
            {"emision": x['cat_emision'], "volumen": int(x['vol']), "revenue": round_money(float(x['rev']))}
            for x in em_breakdown
        ],
    }
    result["tournaments"].append(totals_by_tournament[tour])

# ---------- renovación (online-only, email match torneo N -> N+1) ----------
renewal_data = []
prev_emails = None
prev_tour = None
for tour in TOURNAMENT_ORDER:
    sub = df_all[(df_all['torneo']==tour) & (df_all['canal']=='Online') & (~df_all['es_cortesia'])]
    emails = set(e for e in sub['email'].unique() if e and "@" in e)
    if prev_emails is not None:
        intersect = emails & prev_emails
        renew_pct = round(safe_div(len(intersect), len(prev_emails))*100, 1)
        renewal_data.append({
            "from": prev_tour,
            "to": tour,
            "from_label": TOURNAMENT_LABEL[prev_tour],
            "to_label": TOURNAMENT_LABEL[tour],
            "abonados_prev": len(prev_emails),
            "abonados_curr": len(emails),
            "renovaron": len(intersect),
            "nuevos": len(emails - prev_emails),
            "perdidos": len(prev_emails - emails),
            "tasa_renovacion_pct": renew_pct,
        })
    prev_emails = emails
    prev_tour = tour
result["renewal"] = renewal_data

# ---------- aforo / ocupación por zona (de archivos de disponibilidad en raíz) ----------
# Buscar archivos de disponibilidad: en raíz Y en subcarpeta "Disponibilidad/"
disp_files = []
EXCLUDE_DISP = {"Palcos y plateas AP25-CL26.xlsx"}  # mismo criterio que las transacciones
disp_search_paths = [ROOT, os.path.join(ROOT, "Disponibilidad")]
for path in disp_search_paths:
    if not os.path.isdir(path): continue
    for f in os.listdir(path):
        full = os.path.join(path,f)
        if os.path.isfile(full) and f.endswith(".xlsx") and f not in EXCLUDE_DISP:
            disp_files.append((path, f))

# Mapeo de archivos de disponibilidad a torneo
def map_disp_to_tour(fname):
    f = lower_no_accents(fname)
    if "ap25-cl26" in f or "ap25" in f or "cl26" in f:
        return "AP25-CL26"
    if "cl25" in f or "ap24" in f:
        return "AP24-CL25"
    if "ap23" in f or "cl24" in f:
        return "AP23-CL24"
    return None

afo_by_tour_zone = defaultdict(lambda: defaultdict(lambda: {"aforo":0, "vendidos":0, "abonos_vendidos":0, "cortesias":0}))
for path, f in disp_files:
    tour = map_disp_to_tour(f)
    if not tour: continue
    full = os.path.join(path, f)
    try:
        # leer con header=4 (basado en exploración)
        df = pd.read_excel(full, header=4)
    except: continue
    if 'ZONA' not in df.columns: continue
    df = df[df['ZONA'].notna()].copy()
    df = df[~df['ZONA'].astype(str).str.upper().str.strip().isin(['TOTAL','TOTALES','-','NAN'])].copy()
    for _, r in df.iterrows():
        zona = norm(r.get('ZONA')).upper()
        if not zona or zona == "-": continue
        aforo = to_num(r.get('AFORO'))
        vendidos = to_num(r.get('VENDIDOS'))
        abonos_vendidos = to_num(r.get('ABONOS VENDIDOS'))
        cortesias = to_num(r.get('CORTESÍAS'))
        afo_by_tour_zone[tour][zona]['aforo'] = max(afo_by_tour_zone[tour][zona]['aforo'], aforo)
        afo_by_tour_zone[tour][zona]['vendidos'] += vendidos
        afo_by_tour_zone[tour][zona]['abonos_vendidos'] += abonos_vendidos
        afo_by_tour_zone[tour][zona]['cortesias'] += cortesias

occupancy = {}
for tour, z in afo_by_tour_zone.items():
    rows = []
    total_aforo = 0; total_abonos = 0; total_cortesias = 0
    for zona, vals in z.items():
        af = vals['aforo']
        ab = vals['abonos_vendidos']
        cort = vals['cortesias']
        rows.append({
            "zona": zona,
            "aforo": int(af),
            "abonos_vendidos": int(ab),
            "cortesias": int(cort),
            "ocupacion_pct": round(safe_div(ab+cort, af)*100, 1) if af>0 else 0,
        })
        total_aforo += af; total_abonos += ab; total_cortesias += cort
    rows.sort(key=lambda x: -x['ocupacion_pct'])
    occupancy[tour] = {
        "rows": rows,
        "totales": {
            "aforo_total": int(total_aforo),
            "abonos_vendidos": int(total_abonos),
            "cortesias": int(total_cortesias),
            "ocupacion_pct": round(safe_div(total_abonos+total_cortesias, total_aforo)*100, 1) if total_aforo>0 else 0,
        }
    }
result["occupancy"] = occupancy

# ---------- main dashboard agregados ----------
total_volumen = sum(t['volumen_total'] for t in result['tournaments'])
total_pagado = sum(t['volumen_pagado'] for t in result['tournaments'])
total_cortesias = sum(t['cortesias'] for t in result['tournaments'])
total_revenue = sum(t['revenue'] for t in result['tournaments'])

# Crecimiento promedio de revenue/volumen
def growth(prev, curr):
    return round(safe_div(curr-prev, prev)*100, 1) if prev else 0
revenues = [t['revenue'] for t in result['tournaments']]
vols = [t['volumen_total'] for t in result['tournaments']]
rev_growths = [growth(revenues[i-1], revenues[i]) for i in range(1, len(revenues))]
vol_growths = [growth(vols[i-1], vols[i]) for i in range(1, len(vols))]
avg_rev_growth = round(sum(rev_growths)/len(rev_growths), 1) if rev_growths else 0
avg_vol_growth = round(sum(vol_growths)/len(vol_growths), 1) if vol_growths else 0

# Mix emisión por torneo
mix_by_tour = []
for t in result['tournaments']:
    em = {x['emision']: x['volumen'] for x in t['emision']}
    total = sum(em.values()) or 1
    mix_by_tour.append({
        "torneo": t['label'],
        "Digital": round(em.get('Digital',0)/total*100,1),
        "Físico": round(em.get('Físico',0)/total*100,1),
        "Cortesía": round(em.get('Cortesía',0)/total*100,1),
        "Digital_n": em.get('Digital',0),
        "Físico_n": em.get('Físico',0),
        "Cortesía_n": em.get('Cortesía',0),
    })

# Top zonas a través de todos los torneos (excluyendo entradas sin zona — ruido en data)
zone_totals = defaultdict(lambda: {"vol":0, "rev":0})
for t in result['tournaments']:
    for z in t['zonas']:
        if z['zona'] == "(sin zona)": continue
        zone_totals[z['zona']]['vol'] += z['volumen']
        zone_totals[z['zona']]['rev'] += z['revenue']
top_zones = sorted([
    {"zona":k, "volumen":v['vol'], "revenue":round_money(v['rev'])}
    for k,v in zone_totals.items()
], key=lambda x: -x['volumen'])[:8]

# Top zonas con desglose por torneo (para chart agrupado)
top_zone_names_vol = [z['zona'] for z in top_zones]
top_zones_by_tour_vol = []
for zona in top_zone_names_vol:
    row = {"zona": zona}
    for t in result['tournaments']:
        z = next((x for x in t['zonas'] if x['zona']==zona), None)
        row[t['torneo']] = z['volumen'] if z else 0
        row[t['torneo']+'_rev'] = z['revenue'] if z else 0
    top_zones_by_tour_vol.append(row)

# Top zonas por revenue (orden distinto)
top_zones_rev_sorted = sorted([
    {"zona":k, "volumen":v['vol'], "revenue":round_money(v['rev'])}
    for k,v in zone_totals.items()
], key=lambda x: -x['revenue'])[:8]
top_zones_by_tour_rev = []
for z_info in top_zones_rev_sorted:
    zona = z_info['zona']
    row = {"zona": zona}
    for t in result['tournaments']:
        z = next((x for x in t['zonas'] if x['zona']==zona), None)
        row[t['torneo']] = z['volumen'] if z else 0
        row[t['torneo']+'_rev'] = z['revenue'] if z else 0
    top_zones_by_tour_rev.append(row)

# Mix de emisión por SEMESTRE (6 entradas) — por DURACIÓN (Anual / Semestral / Cortesía)
SEM_ORDER = ["AP23","CL24","AP24","CL25","AP25","CL26"]
mix_by_sem = []
for sem in SEM_ORDER:
    grp = df_all[df_all['semestre']==sem]
    if len(grp)==0: continue
    pagados = grp[~grp['es_cortesia']]
    anual_n     = int(len(pagados[pagados['duracion']=='Anual']))
    semestral_n = int(len(pagados[pagados['duracion']=='Semestral']))
    cort_n      = int(grp['es_cortesia'].sum())
    total = anual_n + semestral_n + cort_n or 1
    mix_by_sem.append({
        "semestre": sem,
        "Anual_pct":     round(anual_n/total*100, 1),
        "Semestral_pct": round(semestral_n/total*100, 1),
        "Cortesía_pct":  round(cort_n/total*100, 1),
        "Anual_n":     anual_n,
        "Semestral_n": semestral_n,
        "Cortesía_n":  cort_n,
        "total": total,
    })

result["main"] = {
    "total_volumen": total_volumen,
    "total_pagado": total_pagado,
    "total_cortesias": total_cortesias,
    "total_revenue": round_money(total_revenue),
    "rev_growths": rev_growths,
    "vol_growths": vol_growths,
    "avg_rev_growth": avg_rev_growth,
    "avg_vol_growth": avg_vol_growth,
    "tournaments_summary": [
        {
            "torneo": t['label'],
            "tour_id": t['torneo'],
            "volumen": t['volumen_total'],
            "pagado": t['volumen_pagado'],
            "cortesias": t['cortesias'],
            "revenue": t['revenue'],
            "ticket_promedio": t['ticket_promedio'],
        } for t in result['tournaments']
    ],
    "mix_emision": mix_by_tour,
    "mix_emision_semestre": mix_by_sem,
    "top_zonas": top_zones,
    "top_zonas_by_tour_vol": top_zones_by_tour_vol,
    "top_zonas_by_tour_rev": top_zones_by_tour_rev,
}

result["notes"] = [
    "Cada fila del archivo fuente representa un asiento individual; órdenes con múltiples asientos se cuentan tantas veces como asientos.",
    "Se filtraron filas sin NÚMERO DE ORDEN o con EVENTO en {[Deshabilitado:T108], '-', NaN, ADMINISTRADORES, Venta en Línea} (basura/totales del reporte original).",
    "Cortesías: TIPO='Cortesia' → revenue=0, contadas separadas en el conteo total.",
    "Categorías: Franjabono Adulto, Cortesía, Renovación, Nuevo abonado, Ex-abonado, Palcos y Plateas, Kids, Universitarios, Socio Puebla, Referidos. Todas cuentan como abonos emitidos (asiento en estadio) según indicación del cliente.",
    "Renovación temporada-a-temporada: solo considera abonados que compraron por canal Online (Frame, IOS, Android) en ambos torneos. Compras en Taquilla quedan excluidas porque históricamente no se trackeaban contra email.",
    "Modalidad Anual recién apareció en AP25-CL26 — torneos previos eran 100% semestrales.",
    "Datos de aforo/ocupación por zona disponibles solo para torneos AP24-CL25 y AP25-CL26 (no hay reporte de disponibilidad para AP23-CL24).",
    "CL26 al cierre del reporte (29-abr-2026): la temporada está casi cerrada; la venta de abonos se concentra al inicio (jun-feb), por lo que se considera comparable.",
]

# ---------- guardar ----------
with open(OUT_JSON, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2, default=str)

print(f"\n=== RESUMEN ===")
for t in result['tournaments']:
    print(f"  {t['label']:<14} | vol: {t['volumen_total']:>6,} | pagado: {t['volumen_pagado']:>6,} | cort: {t['cortesias']:>5,} | rev: ${t['revenue']:>14,.0f}")
print(f"\nTotal: {total_volumen:,} abonos | ${total_revenue:,.0f} revenue | {total_cortesias:,} cortesías")
print(f"Avg growth revenue: {avg_rev_growth}% | Avg growth volumen: {avg_vol_growth}%")
print(f"\nRenovación:")
for r in renewal_data:
    print(f"  {r['from']} → {r['to']}: {r['renovaron']:,} de {r['abonados_prev']:,} ({r['tasa_renovacion_pct']}%) renovaron. Nuevos: {r['nuevos']:,} | Perdidos: {r['perdidos']:,}")
print(f"\nOcupación por torneo:")
for tour, occ in occupancy.items():
    tt = occ['totales']
    print(f"  {tour}: aforo {tt['aforo_total']:,} | abonos {tt['abonos_vendidos']:,} ({tt['ocupacion_pct']}%)")

print(f"\nJSON guardado: {OUT_JSON}")
