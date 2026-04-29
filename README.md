# Reporte Ejecutivo de Abonos — Club Puebla

Análisis comparativo de 3 temporadas (AP23-CL24, AP24-CL25, AP25-CL26) con dashboard HTML interactivo y presentación PowerPoint ejecutiva.

Generado por **Boletomóvil** para la directiva del Club Puebla.

## Estructura

```
.
├── scripts/
│   ├── process.py        # Pipeline: lee Excels, normaliza, agrega métricas → data.json
│   ├── build_html.py     # Genera el HTML interactivo con Chart.js embebido
│   └── create_pptx.js    # Genera el PowerPoint con pptxgenjs
└── outputs/
    ├── Reporte_Puebla_Abonados_2026.html
    └── Reporte_Puebla_Abonados_2026.pptx
```

## Cómo regenerar el reporte

### Requisitos

- Python 3.9+ con `pandas` y `openpyxl`
- Node.js 18+ con `pptxgenjs` y `chart.js`

```bash
pip install pandas openpyxl
npm install pptxgenjs chart.js
```

### Inputs esperados

Carpeta raíz con esta estructura (los Excels contienen data sensible y **no se incluyen en este repo**):

```
Puebla/
├── AP23/
├── CL24/
├── AP24/
├── CL25/
├── AP25/
├── CL26/
└── Disponibilidad/   # reportes de aforo por zona
```

Cada subcarpeta de torneo contiene los Excels de transacciones (Franjabono, Cortesías, etc.). Cada archivo tiene el header en la fila 3 con columnas `NÚMERO DE ORDEN`, `EVENTO`, `FECHA`, `TIPO`, `ZONA`, `MEDIO DE COMPRA`, `PRECIO`, `DESCUENTO`, `SUBTOTAL`, `CORREO ELECTRÓNICO`, etc.

### Pasos para regenerar

```bash
python scripts/process.py        # genera data.json
python scripts/build_html.py     # genera el HTML
node scripts/create_pptx.js      # genera el PPTX
```

## Decisiones metodológicas

- **Revenue** = suma de la columna `SUBTOTAL` (no `TOTAL`); excluye cortesías (que tienen SUBTOTAL = 0).
- **Cortesías** = cualquier orden con SUBTOTAL = 0 (incluye cortesías explícitas + descuentos del 100%).
- **Renovación entre temporadas** = solo abonados que compraron por canal **Online** en ambos torneos (Taquilla queda fuera porque históricamente no se trackeaba contra correo).
- **Palcos y Plateas AP25-CL26** quedan excluidos del comparativo por convención del cliente.
- **Aforo y ocupación**: vienen de los reportes de disponibilidad por zona en `Disponibilidad/`.

## Características del reporte

- Dark mode con branding Boletomóvil (verde `#00C677`).
- Dashboard principal con 2 KPIs (revenue total + abonos emitidos).
- Comparativos entre torneos por revenue, volumen, categoría y zona.
- Stacked bars Taquilla/Online en revenue y volumen.
- Tabla de ocupación de aforo por torneo con desglose por zona.
- Sub-dashboards detallados para cada uno de los 3 torneos.
- HTML 100% autocontenido (Chart.js embebido inline) — funciona offline.

## Licencia

Uso interno Boletomóvil / Club Puebla.
