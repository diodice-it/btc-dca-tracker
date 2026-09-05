# ₿ Bitcoin DCA Tracker

Dashboard interactivo para trackear una estrategia de Dollar Cost Averaging (DCA) en Bitcoin.
Se actualiza solo todos los días: registra la compra, recalcula las métricas y regenera el HTML.

## 🚀 Vista rápida

[Ver Dashboard](https://diodice-it.github.io/btc-dca-tracker/)

## 📊 Qué muestra

**Posición** — resultado neto en USD y %, variación de 24 h, valor del portafolio, BTC y satoshis acumulados, precio promedio de compra.

**Tu estrategia** — precio promedio vs. precio actual, aporte diario y racha, comisiones pagadas, y comparación **DCA vs. comprar todo el primer día** (lump sum, con la misma comisión para que sea justo).

**Rendimiento histórico** — mejor y peor compra (en sats por dólar), caída máxima del portafolio desde un pico, y días en verde sobre el total.

**Gráficos** (Apache ECharts, con zoom por rango de fechas):
1. Invertido vs. valor del portafolio
2. Resultado acumulado, coloreado por signo
3. Precio de Bitcoin con tu precio promedio marcado y los puntos de mejor/peor compra

Modo claro/oscuro con la preferencia guardada en `localStorage`.

## ⚡ Quick start

```bash
pip install -r requirements.txt
python scripts/daily_update.py   # trae el precio, registra la compra y regenera index.html
open index.html
```

Para regenerar solo el dashboard sin consultar la API ni agregar una compra:

```bash
python -c "import sys,pandas as pd; sys.path.insert(0,'scripts'); \
import daily_update as d; df=pd.read_csv(d.CSV_FILE); \
df['fecha']=pd.to_datetime(df['fecha'],format='mixed').dt.date; d.generate_dashboard(df)"
```

## 🗂️ Estructura

| Ruta | Qué es |
|---|---|
| `scripts/daily_update.py` | Todo: fetch del precio, escritura del CSV y generación del HTML |
| `data/btc_purchases.csv` | Histórico de compras (una fila por día) |
| `index.html` | **Generado.** No editar a mano: se pisa en cada corrida |

El HTML sale de `generate_dashboard()`. El CSS y el JS viven en las constantes
`DASHBOARD_CSS` y `DASHBOARD_JS` (strings planos, sin llaves escapadas); los datos
de los gráficos entran por un único bloque `const DATA = {...}` en JSON.
**Cualquier cambio visual va ahí**, no en `index.html`.

## 📖 Documentación completa

Ver [docs/README.md](docs/README.md).

---

Generado automáticamente • Actualizado diariamente
