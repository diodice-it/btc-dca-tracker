#!/usr/bin/env python3
"""
Script de actualización diaria del tracker de BTC DCA
Ejecuta automáticamente cada día a las 9:00 AM
"""

import pandas as pd
import requests
from datetime import datetime
from pathlib import Path
import time
import sys

# Configuración de rutas
BASE_DIR = Path(__file__).parent.parent
COMISION_PORCENTAJE = 0.003  # 0.3% por transacción (compra)
CSV_FILE = BASE_DIR / "data" / "btc_purchases.csv"
DASHBOARD_FILE = BASE_DIR / "index.html"
LOG_DIR = BASE_DIR / "logs"

# Crear directorio de logs si no existe
LOG_DIR.mkdir(exist_ok=True)

def log_message(message):
    """Registra mensaje con timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] {message}"
    print(log_msg)

    # Guardar en archivo de log
    log_file = LOG_DIR / f"btc_tracker_{datetime.now().strftime('%Y%m')}.log"
    with open(log_file, 'a') as f:
        f.write(log_msg + '\n')

def get_btc_price(max_retries=3):
    """Obtiene precio actual de BTC desde CoinGecko con reintentos"""
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": "bitcoin", "vs_currencies": "usd"}

    for intento in range(max_retries):
        try:
            log_message(f"Consultando precio de BTC (intento {intento + 1}/{max_retries})...")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            precio = response.json()["bitcoin"]["usd"]

            # Validar que el precio sea razonable
            if precio <= 0:
                raise ValueError(f"Precio inválido: {precio}")

            log_message(f"✓ Precio obtenido: ${precio:,.2f} USD")
            return precio

        except requests.exceptions.RequestException as e:
            log_message(f"✗ Error de conexión: {e}")
            if intento < max_retries - 1:
                wait_time = 2 ** intento  # Backoff exponencial: 1s, 2s, 4s
                log_message(f"Esperando {wait_time}s antes de reintentar...")
                time.sleep(wait_time)
            else:
                log_message("✗ Máximo de reintentos alcanzado")
                raise
        except (KeyError, ValueError) as e:
            log_message(f"✗ Error procesando respuesta: {e}")
            raise

    raise Exception("No se pudo obtener el precio de BTC")

def update_btc_data():
    """Registra compra del día y actualiza CSV"""
    try:
        log_message("=" * 60)
        log_message("Iniciando actualización diaria del tracker BTC DCA")

        # Paso 1: Obtener precio actual
        precio_btc = get_btc_price()

        # Paso 2: Calcular compra del día
        usd_invertidos = 2.00
        comision_usd = usd_invertidos * COMISION_PORCENTAJE
        btc_comprados = (usd_invertidos - comision_usd) / precio_btc
        log_message(f"Compra del día: ${usd_invertidos:.2f} = {btc_comprados:.8f} BTC · Comisión: ${comision_usd:.4f}")

        # Paso 3: Leer datos históricos (si existen)
        if CSV_FILE.exists():
            df = pd.read_csv(CSV_FILE)
            # Normalizar fechas a solo fecha (sin hora) para comparaciones - usar format='mixed' para manejar formatos inconsistentes
            df['fecha'] = pd.to_datetime(df['fecha'], format='mixed').dt.date

            # Migrar: agregar columna de comision si no existe (compatibilidad hacia atrás)
            if 'comision_usd' not in df.columns:
                df['comision_usd'] = df['usd_invertidos'] * COMISION_PORCENTAJE
                log_message("✓ Columna comision_usd migrada al CSV existente")

            # Contar duplicados antes de limpiar
            duplicados_antes = len(df)

            # Eliminar duplicados si existen (mantener solo el primero de cada día)
            df = df.drop_duplicates(subset=['fecha'], keep='first')

            duplicados_despues = len(df)
            if duplicados_antes > duplicados_despues:
                log_message(f"⚠ Se encontraron {duplicados_antes - duplicados_despues} registro(s) duplicado(s) - limpiando...")
                # Guardar CSV limpio
                df.to_csv(CSV_FILE, index=False)
                log_message(f"✓ CSV limpio guardado")

            btc_acumulado_previo = df['btc_acumulado'].iloc[-1]
            log_message(f"BTC acumulado previo: {btc_acumulado_previo:.8f}")
        else:
            df = pd.DataFrame()
            btc_acumulado_previo = 0.0
            log_message("Primera ejecución - creando archivo CSV")

        # Paso 4: Verificar si ya existe un registro para hoy
        fecha_hoy = datetime.now().date()

        if not df.empty and fecha_hoy in df['fecha'].values:
            log_message(f"⚠ Ya existe un registro para {fecha_hoy} - regenerando solo el dashboard")
            # Regenerar dashboard con datos existentes
            generate_dashboard(df)
            log_message("✓ Dashboard actualizado (sin agregar nueva compra)")
            log_message("=" * 60)
            return

        # Paso 5: Calcular nuevos acumulados
        btc_acumulado = btc_acumulado_previo + btc_comprados
        valor_actual_usd = btc_acumulado * precio_btc

        # Paso 6: Crear registro del día
        nuevo_registro = {
            'fecha': fecha_hoy,
            'precio_btc_usd': precio_btc,
            'usd_invertidos': usd_invertidos,
            'btc_comprados': btc_comprados,
            'btc_acumulado': btc_acumulado,
            'valor_actual_usd': valor_actual_usd,
            'comision_usd': comision_usd
        }

        # Paso 7: Guardar en CSV
        df = pd.concat([df, pd.DataFrame([nuevo_registro])], ignore_index=True)
        df.to_csv(CSV_FILE, index=False)
        log_message(f"✓ Datos guardados en {CSV_FILE}")

        # Paso 8: Regenerar dashboard HTML
        generate_dashboard(df)

        log_message("✓ Actualización completada exitosamente")
        log_message("=" * 60)

    except Exception as e:
        log_message(f"✗ ERROR CRÍTICO: {e}")
        import traceback
        log_message(traceback.format_exc())
        sys.exit(1)

# ===== ICONOS SVG (stroke, heredan color del label) =====
ICONS = {
    "trend": '<svg viewBox="0 0 24 24"><path d="M3 17l6-6 4 4 8-8"/><path d="M21 7v5h-5"/></svg>',
    "coin": '<svg viewBox="0 0 24 24"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/></svg>',
    "clock": '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>',
    "bars": '<svg viewBox="0 0 24 24"><path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/></svg>',
    "check": '<svg viewBox="0 0 24 24"><path d="M20 6L9 17l-5-5"/></svg>',
    "cross": '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M15 9l-6 6M9 9l6 6"/></svg>',
    "dip": '<svg viewBox="0 0 24 24"><path d="M3 7l5 8 4-4 4 6 5-11"/></svg>',
    "star": '<svg viewBox="0 0 24 24"><path d="M12 3l2.9 5.9 6.6 1-4.8 4.6 1.2 6.5L12 18l-5.9 3 1.2-6.5-4.8-4.6 6.6-1z"/></svg>',
}

# ===== CSS (string plano: no necesita escapar llaves) =====
DASHBOARD_CSS = """
:root{
  --bg:#f4f6fa; --surface:#ffffff; --surface-2:#eef1f7;
  --line:#dde2ec; --line-soft:#e7ebf2;
  --txt:#131824; --txt-2:#5b6779; --txt-3:#8b97a8;
  --btc:#e07c0a; --pos:#18794e; --neg:#c93c37; --accent:#4257b2;
  --pos-bg:rgba(24,121,78,.10); --neg-bg:rgba(201,60,55,.10);
  --shadow:0 1px 2px rgba(16,24,40,.05),0 4px 12px rgba(16,24,40,.05);
}
[data-theme="dark"]{
  --bg:#0d1117; --surface:#161b22; --surface-2:#1c2230;
  --line:#2a3140; --line-soft:#222835;
  --txt:#e6edf3; --txt-2:#9aa7b8; --txt-3:#6b7889;
  --btc:#f7931a; --pos:#3fb950; --neg:#f85149; --accent:#6e8ef7;
  --pos-bg:rgba(63,185,80,.13); --neg-bg:rgba(248,81,73,.13);
  --shadow:0 1px 2px rgba(0,0,0,.3),0 4px 14px rgba(0,0,0,.2);
}
*{margin:0;padding:0;box-sizing:border-box;-webkit-tap-highlight-color:transparent}
html{-webkit-text-size-adjust:100%;text-size-adjust:100%}
body{
  background:var(--bg);color:var(--txt);
  font-family:Inter,-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
  line-height:1.5;padding:28px 20px 40px;min-height:100vh;
  font-feature-settings:'tnum' 1;
}
.wrap{max-width:1240px;margin:0 auto}
.mono{font-family:'JetBrains Mono','SF Mono',Monaco,Consolas,monospace}

/* ---- header ---- */
.head{display:flex;align-items:flex-start;justify-content:space-between;gap:16px;margin-bottom:30px}
.head h1{font-size:1.6rem;font-weight:700;letter-spacing:-.025em;display:flex;align-items:center;gap:9px}
.head h1 .b{color:var(--btc)}
.head .meta{margin-top:5px;font-size:.83rem;color:var(--txt-2);display:flex;align-items:center;gap:9px;flex-wrap:wrap}
.theme-toggle{
  flex:none;width:40px;height:40px;border-radius:10px;cursor:pointer;
  background:var(--surface);border:1px solid var(--line);
  display:flex;align-items:center;justify-content:center;
  transition:border-color .2s,transform .2s;
}
.theme-toggle:hover{border-color:var(--txt-3);transform:translateY(-1px)}
.theme-toggle svg{width:18px;height:18px;fill:none;stroke:var(--txt-2);stroke-width:1.9;stroke-linecap:round;stroke-linejoin:round;pointer-events:none}

/* ---- primitivas ---- */
.sec{font-size:.72rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--txt-3);margin:30px 0 12px;display:flex;align-items:center;gap:10px}
.sec::after{content:"";flex:1;height:1px;background:var(--line-soft)}
.dot{width:3px;height:3px;border-radius:50%;background:var(--txt-3);flex:none}
.pill{
  font-family:'JetBrains Mono','SF Mono',Monaco,monospace;font-size:.92rem;font-weight:700;
  padding:4px 10px;border-radius:8px;white-space:nowrap;
  background:var(--pos-bg);color:var(--pos);border:1px solid transparent;
}
.pill.neg{background:var(--neg-bg);color:var(--neg)}
.pill.sm{font-size:.76rem;padding:2px 7px}

/* ---- hero ---- */
.hero{
  background:var(--surface);border:1px solid var(--line);border-radius:16px;
  padding:26px 28px;box-shadow:var(--shadow);
  display:grid;grid-template-columns:1.15fr 1fr;gap:32px;
}
.hero .lbl{font-size:.72rem;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:var(--txt-3);margin-bottom:10px}
.pnl{display:flex;align-items:baseline;gap:14px;flex-wrap:wrap}
.pnl .big{font-size:3rem;font-weight:700;letter-spacing:-.03em;line-height:1}
.hero-meta{margin-top:15px;display:flex;gap:9px;align-items:center;flex-wrap:wrap;font-size:.82rem;color:var(--txt-2)}
.bar{margin-top:20px;height:8px;border-radius:6px;background:var(--surface-2);overflow:hidden;display:flex}
.bar i{display:block;height:100%}
.barleg{display:flex;gap:18px;margin-top:9px;font-size:.75rem;color:var(--txt-2);flex-wrap:wrap}
.barleg span{display:flex;align-items:center;gap:6px}
.sw{width:9px;height:9px;border-radius:3px;flex:none}
.hero-r{border-left:1px solid var(--line);padding-left:32px;display:flex;flex-direction:column;justify-content:center;gap:13px}
.kv{display:flex;justify-content:space-between;align-items:baseline;gap:12px}
.kv .k{font-size:.82rem;color:var(--txt-2)}
.kv .v{font-size:1.05rem;font-weight:600;display:flex;align-items:baseline;gap:7px}
.kv .v.btc{color:var(--btc)}

/* ---- cards ---- */
.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}
.card{
  background:var(--surface);border:1px solid var(--line-soft);border-radius:12px;
  padding:16px 18px;box-shadow:var(--shadow);
  transition:border-color .2s,transform .2s;
}
.card:hover{border-color:var(--line);transform:translateY(-2px)}
.card .top{display:flex;align-items:center;gap:8px;margin-bottom:12px}
.card svg{width:14px;height:14px;stroke:var(--txt-3);fill:none;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round;flex:none}
.card .lb{font-size:.68rem;font-weight:600;letter-spacing:.07em;text-transform:uppercase;color:var(--txt-3)}
.card .val{font-size:1.45rem;font-weight:600;letter-spacing:-.015em;line-height:1.15}
.card .val .of{font-size:.85rem;color:var(--txt-3);font-weight:400}
.card .val.o{color:var(--btc)}
.card .val.pos{color:var(--pos)}
.card .val.neg{color:var(--neg)}
.card .sub{font-size:.75rem;color:var(--txt-2);margin-top:6px}
.card .sub b{color:var(--txt);font-weight:600}

/* ---- charts ---- */
.panel{
  background:var(--surface);border:1px solid var(--line);border-radius:14px;
  padding:20px 22px 14px;box-shadow:var(--shadow);margin-bottom:14px;
}
.panel h2{font-size:.95rem;font-weight:600;letter-spacing:-.01em;margin-bottom:2px}
.panel .hint{font-size:.78rem;color:var(--txt-3);margin-bottom:12px}
.chart{width:100%;height:340px}

footer{margin-top:34px;padding-top:20px;border-top:1px solid var(--line-soft);text-align:center;font-size:.78rem;color:var(--txt-3)}
footer a{color:var(--txt-2)}

/* ---- responsive ---- */
@media(max-width:1000px){
  .hero{grid-template-columns:1fr;gap:22px;padding:22px}
  .hero-r{border-left:none;border-top:1px solid var(--line);padding-left:0;padding-top:20px}
  .grid{grid-template-columns:repeat(2,1fr)}
}
@media(max-width:640px){
  body{padding:18px 14px 30px}
  .head h1{font-size:1.25rem}
  .pnl .big{font-size:2.3rem}
  .card .val{font-size:1.25rem}
  .chart{height:280px}
  .panel{padding:16px 14px 10px}
}
@media(max-width:380px){
  .grid{grid-template-columns:1fr}
}
@media(prefers-reduced-motion:reduce){
  *{transition:none!important;animation:none!important}
}
"""

# ===== JS (string plano: los datos entran por un unico bloque JSON) =====
DASHBOARD_JS = """
// ---- tema ----
function themeIcon(t){
  var s=document.getElementById('theme-icon');
  s.querySelector('.i-sun').style.display   = t==='dark' ? '' : 'none';
  s.querySelector('.i-moon').style.display  = t==='dark' ? 'none' : '';
}
function toggleTheme(){
  var h=document.documentElement;
  var next = h.getAttribute('data-theme')==='dark' ? 'light' : 'dark';
  h.setAttribute('data-theme',next);
  try{ localStorage.setItem('theme',next); }catch(e){}
  themeIcon(next);
  renderCharts();
}
themeIcon(document.documentElement.getAttribute('data-theme'));

// ---- paleta segun tema ----
function palette(){
  var dark = document.documentElement.getAttribute('data-theme')==='dark';
  return dark
    ? {txt:'#9aa7b8', faint:'#6b7889', grid:'#222835', tipBg:'#161b22', tipBorder:'#2a3140', tipTxt:'#e6edf3',
       accent:'#6e8ef7', btc:'#f7931a', pos:'#3fb950', neg:'#f85149', zoomFill:'rgba(110,142,247,.12)'}
    : {txt:'#5b6779', faint:'#8b97a8', grid:'#e7ebf2', tipBg:'#ffffff', tipBorder:'#dde2ec', tipTxt:'#131824',
       accent:'#4257b2', btc:'#e07c0a', pos:'#18794e', neg:'#c93c37', zoomFill:'rgba(66,87,178,.10)'};
}
var usd0 = function(v){ return '$' + Math.round(v).toLocaleString('en-US'); };
var usd2 = function(v){ return '$' + v.toLocaleString('en-US',{minimumFractionDigits:2,maximumFractionDigits:2}); };
function fade(hex,a){
  var r=parseInt(hex.slice(1,3),16),g=parseInt(hex.slice(3,5),16),b=parseInt(hex.slice(5,7),16);
  return 'rgba('+r+','+g+','+b+','+a+')';
}
function area(hex){
  return {type:'linear',x:0,y:0,x2:0,y2:1,colorStops:[{offset:0,color:fade(hex,.28)},{offset:1,color:fade(hex,.02)}]};
}

// ---- base comun de los 3 graficos ----
function base(p, zoomStart){
  return {
    animationDuration: 700,
    textStyle:{fontFamily:'Inter,-apple-system,sans-serif'},
    grid:{left:8,right:16,top:44,bottom:58,containLabel:true},
    tooltip:{
      trigger:'axis',
      backgroundColor:p.tipBg, borderColor:p.tipBorder, borderWidth:1,
      padding:[9,12],
      textStyle:{color:p.tipTxt,fontSize:12},
      axisPointer:{type:'line',lineStyle:{color:p.faint,width:1,type:'dashed'}},
      extraCssText:'box-shadow:0 6px 20px rgba(0,0,0,.18);border-radius:8px'
    },
    legend:{top:2,left:0,icon:'roundRect',itemWidth:9,itemHeight:9,itemGap:16,
            textStyle:{color:p.txt,fontSize:12}},
    xAxis:{
      type:'category', data:DATA.labels, boundaryGap:false,
      axisLine:{lineStyle:{color:p.grid}},
      axisTick:{show:false},
      axisLabel:{color:p.faint,fontSize:11,hideOverlap:true,margin:12},
      splitLine:{show:false}
    },
    dataZoom:[
      {type:'inside', start:zoomStart, end:100, zoomOnMouseWheel:'shift'},
      {type:'slider', start:zoomStart, end:100, height:26, bottom:8,
       borderColor:'transparent', backgroundColor:'transparent',
       fillerColor:p.zoomFill, showDetail:false,
       moveHandleSize:0, brushSelect:false,
       handleSize:'80%', handleStyle:{color:p.tipBg,borderColor:p.accent,borderWidth:1.5,shadowBlur:0},
       dataBackground:{lineStyle:{color:p.faint,width:1,opacity:.5},areaStyle:{color:p.faint,opacity:.12}},
       selectedDataBackground:{lineStyle:{color:p.accent,width:1},areaStyle:{color:p.accent,opacity:.2}}}
    ]
  };
}
function yAxis(p, fmt){
  return {
    type:'value', scale:true,
    axisLine:{show:false}, axisTick:{show:false},
    axisLabel:{color:p.faint,fontSize:11,formatter:fmt},
    splitLine:{lineStyle:{color:p.grid,type:'dashed'}}
  };
}

// ---- graficos ----
var charts = {};
function renderCharts(){
  try{
    var p = palette();
    Object.keys(charts).forEach(function(k){ if(charts[k]) charts[k].dispose(); });
    charts = {};

    // 1. DCA: invertido vs valor
    charts.dca = echarts.init(document.getElementById('chart-dca'));
    charts.dca.setOption(Object.assign(base(p,0),{
      yAxis: yAxis(p, function(v){ return usd0(v); }),
      tooltip: Object.assign(base(p,0).tooltip,{
        formatter:function(ps){
          var i=ps[0].dataIndex, d=DATA.pnl[i], pct=DATA.pnlPct[i];
          var c = d>=0 ? p.pos : p.neg;
          var out = '<b>'+DATA.fechas[i]+'</b>';
          ps.forEach(function(s){ out += '<br/>'+s.marker+' '+s.seriesName+': <b>'+usd2(s.value)+'</b>'; });
          out += '<br/><span style="color:'+c+'">&#9679; Resultado: <b>'+(d>=0?'+':'-')+usd2(Math.abs(d))
               + ' ('+(d>=0?'+':'')+pct.toFixed(2)+'%)</b></span>';
          return out;
        }
      }),
      series:[
        {name:'Invertido', type:'line', data:DATA.invertido, smooth:true, symbol:'none',
         lineStyle:{width:2, color:p.accent, type:'dashed'}, itemStyle:{color:p.accent}},
        {name:'Valor del portafolio', type:'line', data:DATA.valor, smooth:true, symbol:'none',
         lineStyle:{width:2.5, color:p.btc}, itemStyle:{color:p.btc}, areaStyle:{color:area(p.btc)},
         emphasis:{focus:'series'}}
      ]
    }));

    // 2. Resultado acumulado (P&L), partido en tramos por signo para colorearlo
    var pnlPos = DATA.pnl.map(function(v){ return v >= 0 ? v : null; });
    var pnlNeg = DATA.pnl.map(function(v){ return v <= 0 ? v : null; });
    charts.pnl = echarts.init(document.getElementById('chart-pnl'));
    charts.pnl.setOption(Object.assign(base(p,0),{
      legend:{show:false},
      grid:{left:8,right:16,top:20,bottom:58,containLabel:true},
      yAxis: yAxis(p, function(v){ return (v>=0?'+':'-') + '$' + Math.abs(Math.round(v)).toLocaleString('en-US'); }),
      tooltip: Object.assign(base(p,0).tooltip,{
        formatter:function(ps){
          var i=ps[0].dataIndex, d=DATA.pnl[i], pct=DATA.pnlPct[i];
          var c = d>=0 ? p.pos : p.neg;
          return '<b>'+DATA.fechas[i]+'</b><br/><span style="color:'+c+'">&#9679; '
               + (d>=0?'+':'-')+usd2(Math.abs(d))+' <b>('+(d>=0?'+':'')+pct.toFixed(2)+'%)</b></span>';
        }
      }),
      series:[
        {
          name:'Ganancia', type:'line', data:pnlPos, smooth:true, symbol:'none',
          connectNulls:false,
          itemStyle:{color:p.pos}, lineStyle:{width:2.5, color:p.pos},
          areaStyle:{color:area(p.pos), origin:0},
          markLine:{
            silent:true, symbol:'none',
            data:[{yAxis:0}],
            lineStyle:{color:p.faint,type:'solid',width:1},
            label:{show:false}
          }
        },
        {
          name:'Pérdida', type:'line', data:pnlNeg, smooth:true, symbol:'none',
          connectNulls:false,
          itemStyle:{color:p.neg}, lineStyle:{width:2.5, color:p.neg},
          areaStyle:{color:area(p.neg), origin:0}
        }
      ]
    }));

    // 3. Precio de BTC + precio promedio + mejor/peor compra
    charts.price = echarts.init(document.getElementById('chart-price'));
    charts.price.setOption(Object.assign(base(p,0),{
      legend:{show:false},
      grid:{left:8,right:16,top:20,bottom:58,containLabel:true},
      yAxis: yAxis(p, function(v){ return usd0(v); }),
      tooltip: Object.assign(base(p,0).tooltip,{
        formatter:function(ps){
          var i=ps[0].dataIndex;
          var diff = (ps[0].value/DATA.precioPromedio - 1)*100;
          var c = diff>=0 ? p.pos : p.neg;
          return '<b>'+DATA.fechas[i]+'</b><br/>&#9679; BTC: <b>'+usd2(ps[0].value)+'</b>'
               + '<br/><span style="color:'+c+'">'+(diff>=0?'+':'')+diff.toFixed(1)+'% vs tu promedio</span>'
               + '<br/><span style="color:'+p.faint+'">Compraste '+DATA.sats[i].toLocaleString('en-US')+' sats</span>';
        }
      }),
      series:[{
        name:'BTC/USD', type:'line', data:DATA.precio, smooth:true, symbol:'none',
        lineStyle:{width:2.5,color:p.btc}, itemStyle:{color:p.btc}, areaStyle:{color:area(p.btc)},
        markLine:{
          silent:true, symbol:'none',
          data:[{yAxis:DATA.precioPromedio, name:'Promedio'}],
          lineStyle:{color:p.accent,type:'dashed',width:1.5},
          label:{formatter:'Tu promedio  '+usd0(DATA.precioPromedio), position:'insideEndTop',
                 color:p.accent, fontSize:11, fontWeight:600}
        },
        markPoint:{
          symbol:'circle', symbolSize:10,
          data:[
            {name:'Mejor compra', coord:[DATA.mejorIdx, DATA.mejorPrecio],
             itemStyle:{color:p.pos, borderColor:p.tipBg, borderWidth:2},
             label:{show:true, formatter:'Mejor', position:'bottom', distance:6,
                    color:p.pos, fontSize:10, fontWeight:600}},
            {name:'Peor compra', coord:[DATA.peorIdx, DATA.peorPrecio],
             itemStyle:{color:p.neg, borderColor:p.tipBg, borderWidth:2},
             label:{show:true, formatter:'Peor', position:'top', distance:6,
                    color:p.neg, fontSize:10, fontWeight:600}}
          ]
        },
        emphasis:{focus:'series'}
      }]
    }));
  }catch(e){
    console.error('Error al renderizar graficos:', e);
  }
}

var rt;
window.addEventListener('resize', function(){
  clearTimeout(rt);
  rt = setTimeout(function(){
    Object.keys(charts).forEach(function(k){ if(charts[k]) charts[k].resize(); });
  }, 120);
});

if(document.readyState === 'loading'){
  document.addEventListener('DOMContentLoaded', renderCharts);
}else{
  renderCharts();
}
"""


def generate_dashboard(df):
    """Genera el dashboard HTML estatico a partir del historico de compras"""
    import json
    from datetime import datetime

    # ===== METRICAS BASICAS =====
    total_dias = len(df)
    total_invertido = total_dias * 2.00
    btc_total = df['btc_acumulado'].iloc[-1]
    satoshis = int(round(btc_total * 100_000_000))
    precio_actual = df['precio_btc_usd'].iloc[-1]
    valor_actual = df['valor_actual_usd'].iloc[-1]
    ganancia = valor_actual - total_invertido
    porcentaje = (ganancia / total_invertido) * 100 if total_invertido > 0 else 0

    # ===== COMISIONES =====
    if 'comision_usd' in df.columns:
        total_comisiones = df['comision_usd'].sum()
    else:
        total_comisiones = total_invertido * COMISION_PORCENTAJE
    pct_comisiones = (total_comisiones / total_invertido) * 100 if total_invertido > 0 else 0

    # El BTC acumulado ya se compra neto de comision (btc = (usd - fee) / precio),
    # asi que `ganancia` es el resultado real: restarle los fees otra vez seria
    # contarlos dos veces. La bruta se reconstruye comprando sin comision cada dia
    # -- los fees cuestan mas que su valor nominal porque ese BTC que no se compro
    # tambien se habria revalorizado.
    ganancia_neta = ganancia
    porcentaje_neto = porcentaje
    btc_sin_fees = float(sum(2.00 / precio for precio in df['precio_btc_usd'] if precio > 0))
    ganancia_bruta = btc_sin_fees * precio_actual - total_invertido
    costo_real_fees = ganancia_bruta - ganancia_neta

    # ===== PRECIO PROMEDIO DE COMPRA =====
    precio_promedio = total_invertido / btc_total if btc_total > 0 else 0
    diff_vs_promedio = ((precio_actual - precio_promedio) / precio_promedio * 100) if precio_promedio > 0 else 0

    # ===== VARIACION 24 H =====
    if total_dias > 1:
        valor_ayer = df['valor_actual_usd'].iloc[-2]
        precio_ayer = df['precio_btc_usd'].iloc[-2]
        # el valor de ayer no incluye el aporte de hoy: se descuenta para comparar manzanas con manzanas
        cambio_valor = (valor_actual - 2.00) - valor_ayer
        cambio_valor_pct = (cambio_valor / valor_ayer * 100) if valor_ayer > 0 else 0
        cambio_precio_pct = ((precio_actual - precio_ayer) / precio_ayer * 100) if precio_ayer > 0 else 0
    else:
        cambio_valor = cambio_valor_pct = cambio_precio_pct = 0.0

    # ===== MEJOR / PEOR COMPRA =====
    mejor_idx = int(df['btc_comprados'].values.argmax())
    peor_idx = int(df['btc_comprados'].values.argmin())
    mejor_precio = float(df['precio_btc_usd'].iloc[mejor_idx])
    peor_precio = float(df['precio_btc_usd'].iloc[peor_idx])
    mejor_sats = int(round(df['btc_comprados'].iloc[mejor_idx] * 100_000_000))
    peor_sats = int(round(df['btc_comprados'].iloc[peor_idx] * 100_000_000))
    mejor_fecha = pd.to_datetime(df['fecha'].iloc[mejor_idx]).strftime("%d/%m/%Y")
    peor_fecha = pd.to_datetime(df['fecha'].iloc[peor_idx]).strftime("%d/%m/%Y")

    # ===== DCA VS COMPRAR TODO EL PRIMER DIA (LUMP SUM) =====
    # misma comision que paga el DCA, para que la comparacion sea justa
    precio_inicial = float(df['precio_btc_usd'].iloc[0])
    btc_lump = (total_invertido * (1 - COMISION_PORCENTAJE)) / precio_inicial if precio_inicial > 0 else 0
    valor_lump = btc_lump * precio_actual
    dca_ventaja = valor_actual - valor_lump
    dca_ventaja_pct = (dca_ventaja / valor_lump * 100) if valor_lump > 0 else 0

    # ===== CAIDA MAXIMA (peor bajon del portafolio desde un pico) =====
    equity = df['valor_actual_usd'].astype(float)
    pico = equity.cummax()
    caidas = (equity / pico - 1) * 100
    drawdown_max = float(caidas.min())
    drawdown_fecha = pd.to_datetime(df['fecha'].iloc[int(caidas.values.argmin())]).strftime("%d/%m/%Y")

    # ===== DIAS EN VERDE =====
    invertido_serie = [(i + 1) * 2.00 for i in range(total_dias)]
    dias_verde = int(sum(1 for v, inv in zip(equity, invertido_serie) if v > inv))
    pct_verde = (dias_verde / total_dias * 100) if total_dias > 0 else 0

    fecha_inicio = pd.to_datetime(df['fecha'].iloc[0]).strftime("%d/%m/%Y")

    # ===== SERIES PARA LOS GRAFICOS =====
    chart_data = {
        "labels": [pd.to_datetime(f).strftime("%d/%m") for f in df['fecha']],
        "fechas": [pd.to_datetime(f).strftime("%d/%m/%Y") for f in df['fecha']],
        "invertido": [round(v, 2) for v in invertido_serie],
        "valor": [round(float(v), 2) for v in equity],
        "precio": [float(v) for v in df['precio_btc_usd']],
        "pnl": [round(float(v) - inv, 2) for v, inv in zip(equity, invertido_serie)],
        "pnlPct": [round((float(v) - inv) / inv * 100, 2) for v, inv in zip(equity, invertido_serie)],
        "sats": [int(round(v * 100_000_000)) for v in df['btc_comprados']],
        "precioPromedio": round(precio_promedio, 2),
        "mejorIdx": mejor_idx, "mejorPrecio": mejor_precio,
        "peorIdx": peor_idx, "peorPrecio": peor_precio,
    }

    # ===== HELPERS DE FORMATO =====
    def signo(v):
        return "+" if v >= 0 else "−"

    def money(v, dec=2):
        return f"${abs(v):,.{dec}f}"

    def signed_money(v, dec=2):
        return f"{signo(v)}{money(v, dec)}"

    def signed_pct(v, dec=2):
        return f"{signo(v)}{abs(v):.{dec}f}%"

    cls_pnl = "" if ganancia_neta >= 0 else " neg"
    cls_24h = "" if cambio_valor >= 0 else " neg"
    cls_precio24 = "" if cambio_precio_pct >= 0 else " neg"
    pct_invertido_barra = min(100.0, (total_invertido / valor_actual * 100)) if valor_actual > 0 else 100.0
    pct_pnl_barra = max(0.0, 100.0 - pct_invertido_barra)
    color_pnl_barra = "var(--pos)" if ganancia_neta >= 0 else "var(--neg)"
    cls_promedio = "pos" if diff_vs_promedio >= 0 else "neg"
    txt_promedio = "arriba de" if diff_vs_promedio >= 0 else "abajo de"
    cls_lump = "pos" if dca_ventaja >= 0 else "neg"
    txt_lump = ("Ganás" if dca_ventaja >= 0 else "Perdés") + f" {abs(dca_ventaja_pct):.1f}% " + \
               ("más" if dca_ventaja >= 0 else "menos") + " que comprando todo el primer día"

    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")

    # ===== HTML =====
    html_content = f"""<!DOCTYPE html>
<html lang="es" data-theme="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<title>Bitcoin DCA Tracker</title>
<meta name="description" content="Seguimiento diario de una estrategia DCA en Bitcoin: {total_dias} días, {money(total_invertido)} invertidos, resultado {signed_money(ganancia_neta)}.">
<meta name="color-scheme" content="dark light">
<meta name="theme-color" content="#0d1117" media="(prefers-color-scheme: dark)">
<meta name="theme-color" content="#f4f6fa" media="(prefers-color-scheme: light)">
<link rel="manifest" href="manifest.json">
<link rel="icon" type="image/svg+xml" href="icon.svg">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta property="og:title" content="Bitcoin DCA Tracker">
<meta property="og:description" content="{total_dias} días de DCA · {money(total_invertido)} invertidos · {signed_money(ganancia_neta)} ({signed_pct(porcentaje_neto)})">
<meta property="og:type" content="website">
<script>
  // Aplica el tema guardado antes del primer pintado para evitar el flash
  (function(){{
    try{{
      var t = localStorage.getItem('theme');
      if(t) document.documentElement.setAttribute('data-theme', t);
    }}catch(e){{}}
  }})();
</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>{DASHBOARD_CSS}</style>
</head>
<body>
<div class="wrap">

  <header class="head">
    <div>
      <h1><span class="b">&#8383;</span> Bitcoin DCA Tracker</h1>
      <div class="meta">
        <span>BTC <b class="mono">{money(precio_actual, 0)}</b></span>
        <span class="pill sm{cls_precio24}">{signed_pct(cambio_precio_pct, 2)}</span>
        <span class="dot"></span>
        <span>Actualizado {timestamp}</span>
      </div>
    </div>
    <button class="theme-toggle" onclick="toggleTheme()" aria-label="Cambiar tema" title="Cambiar tema">
      <svg id="theme-icon" viewBox="0 0 24 24">
        <g class="i-sun">
          <circle cx="12" cy="12" r="4"/>
          <path d="M12 1v2M12 21v2M4.2 4.2l1.4 1.4M18.4 18.4l1.4 1.4M1 12h2M21 12h2M4.2 19.8l1.4-1.4M18.4 5.6l1.4-1.4"/>
        </g>
        <path class="i-moon" d="M21 12.8A9 9 0 1 1 11.2 3 7 7 0 0 0 21 12.8z"/>
      </svg>
    </button>
  </header>

  <p class="sec">Posición</p>
  <div class="hero">
    <div class="hero-l">
      <div class="lbl">Resultado neto · después de comisiones</div>
      <div class="pnl">
        <span class="big mono" style="color:{color_pnl_barra}">{signed_money(ganancia_neta)}</span>
        <span class="pill{cls_pnl}">{signed_pct(porcentaje_neto)}</span>
      </div>
      <div class="hero-meta">
        <span>Últimas 24 h</span>
        <span class="pill sm{cls_24h}">{signed_money(cambio_valor)} · {signed_pct(cambio_valor_pct)}</span>
        <span class="dot"></span>
        <span>Bruta {signed_money(ganancia_bruta)} · las comisiones te costaron {money(costo_real_fees, 2)}</span>
      </div>
      <div class="bar">
        <i style="background:var(--accent);width:{pct_invertido_barra:.1f}%"></i>
        <i style="background:{color_pnl_barra};width:{pct_pnl_barra:.1f}%"></i>
      </div>
      <div class="barleg">
        <span><i class="sw" style="background:var(--accent)"></i>Invertido {money(total_invertido)}</span>
        <span><i class="sw" style="background:{color_pnl_barra}"></i>Resultado {signed_money(ganancia_neta)}</span>
      </div>
    </div>
    <div class="hero-r">
      <div class="kv"><span class="k">Valor actual</span><span class="v mono">{money(valor_actual)}</span></div>
      <div class="kv"><span class="k">BTC acumulado</span><span class="v mono btc">{btc_total:.8f}</span></div>
      <div class="kv"><span class="k">Satoshis</span><span class="v mono">{satoshis:,}</span></div>
      <div class="kv"><span class="k">Precio promedio</span><span class="v mono">{money(precio_promedio, 0)}</span></div>
    </div>
  </div>

  <p class="sec">Tu estrategia</p>
  <div class="grid">
    <div class="card">
      <div class="top">{ICONS['trend']}<span class="lb">Precio promedio</span></div>
      <div class="val mono">{money(precio_promedio, 0)}</div>
      <div class="sub">BTC hoy está <b class="{cls_promedio}">{abs(diff_vs_promedio):.1f}% {txt_promedio}</b> tu promedio</div>
    </div>
    <div class="card">
      <div class="top">{ICONS['coin']}<span class="lb">Aporte diario</span></div>
      <div class="val mono">$2.00</div>
      <div class="sub">{total_dias} días sin interrumpir · desde {fecha_inicio}</div>
    </div>
    <div class="card">
      <div class="top">{ICONS['clock']}<span class="lb">Comisiones</span></div>
      <div class="val mono">{money(total_comisiones, 2)}</div>
      <div class="sub">{pct_comisiones:.1f}% del capital · {total_dias} transacciones</div>
    </div>
    <div class="card">
      <div class="top">{ICONS['bars']}<span class="lb">DCA vs todo de una</span></div>
      <div class="val mono {cls_lump}">{signed_money(dca_ventaja)}</div>
      <div class="sub">{txt_lump}</div>
    </div>
  </div>

  <p class="sec">Rendimiento histórico</p>
  <div class="grid">
    <div class="card">
      <div class="top">{ICONS['check']}<span class="lb">Mejor compra</span></div>
      <div class="val mono o">{money(mejor_precio, 0)}</div>
      <div class="sub">{mejor_fecha} · {mejor_sats:,} sats por $2</div>
    </div>
    <div class="card">
      <div class="top">{ICONS['cross']}<span class="lb">Peor compra</span></div>
      <div class="val mono o">{money(peor_precio, 0)}</div>
      <div class="sub">{peor_fecha} · {peor_sats:,} sats por $2</div>
    </div>
    <div class="card">
      <div class="top">{ICONS['dip']}<span class="lb">Caída máxima</span></div>
      <div class="val mono neg">&minus;{abs(drawdown_max):.1f}%</div>
      <div class="sub">Peor bajón desde un pico · {drawdown_fecha}</div>
    </div>
    <div class="card">
      <div class="top">{ICONS['star']}<span class="lb">Días en verde</span></div>
      <div class="val mono">{dias_verde} <span class="of">/ {total_dias}</span></div>
      <div class="sub">{pct_verde:.0f}% del tiempo por encima de lo invertido</div>
    </div>
  </div>

  <p class="sec">Evolución</p>

  <div class="panel">
    <h2>Invertido vs. valor del portafolio</h2>
    <p class="hint">Arrastrá la barra inferior para acotar el período · shift + rueda para hacer zoom</p>
    <div id="chart-dca" class="chart"></div>
  </div>

  <div class="panel">
    <h2>Resultado acumulado</h2>
    <p class="hint">Ganancia o pérdida sobre el total invertido hasta cada día</p>
    <div id="chart-pnl" class="chart"></div>
  </div>

  <div class="panel">
    <h2>Precio de Bitcoin</h2>
    <p class="hint">La línea punteada es tu precio promedio de compra</p>
    <div id="chart-price" class="chart"></div>
  </div>

  <footer>
    <p>Generado automáticamente · {timestamp} · datos de CoinGecko</p>
  </footer>
</div>

<script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>
<script>
const DATA = {json.dumps(chart_data)};
{DASHBOARD_JS}
</script>
</body>
</html>"""

    # Guardar HTML
    with open(DASHBOARD_FILE, 'w', encoding='utf-8') as f:
        f.write(html_content)

    log_message(f"✓ Dashboard generado en {DASHBOARD_FILE}")


if __name__ == "__main__":
    update_btc_data()
