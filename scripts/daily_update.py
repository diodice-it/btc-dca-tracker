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
        btc_comprados = usd_invertidos / precio_btc
        log_message(f"Compra del día: ${usd_invertidos:.2f} = {btc_comprados:.8f} BTC")

        # Paso 3: Leer datos históricos (si existen)
        if CSV_FILE.exists():
            df = pd.read_csv(CSV_FILE)
            # Normalizar fechas a solo fecha (sin hora) para comparaciones - usar format='mixed' para manejar formatos inconsistentes
            df['fecha'] = pd.to_datetime(df['fecha'], format='mixed').dt.date

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
            'valor_actual_usd': valor_actual_usd
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

def generate_dashboard(df):
    """Genera el dashboard HTML mejorado con todas las nuevas features"""
    from datetime import datetime

    # ===== MÉTRICAS BÁSICAS =====
    total_dias = len(df)
    total_invertido = total_dias * 2.00
    btc_total = df['btc_acumulado'].iloc[-1]
    satoshis = int(btc_total * 100_000_000)
    precio_actual = df['precio_btc_usd'].iloc[-1]
    valor_actual = df['valor_actual_usd'].iloc[-1]
    ganancia = valor_actual - total_invertido
    porcentaje = (ganancia / total_invertido) * 100 if total_invertido > 0 else 0

    # ===== MEJORA 1: PRECIO PROMEDIO DE COMPRA =====
    precio_promedio = total_invertido / btc_total if btc_total > 0 else 0
    diff_vs_promedio = ((precio_actual - precio_promedio) / precio_promedio * 100) if precio_promedio > 0 else 0

    # ===== MEJORA 3: INDICADORES DE TENDENCIA =====
    if len(df) > 1:
        valor_ayer = df['valor_actual_usd'].iloc[-2]
        cambio_valor = valor_actual - valor_ayer
        tendencia_valor = "↗️" if cambio_valor > 0 else "↘️" if cambio_valor < 0 else "→"

        precio_ayer = df['precio_btc_usd'].iloc[-2]
        cambio_precio = precio_actual - precio_ayer
        tendencia_precio = "↗️" if cambio_precio > 0 else "↘️" if cambio_precio < 0 else "→"
    else:
        tendencia_valor = "→"
        tendencia_precio = "→"
        cambio_valor = 0
        cambio_precio = 0

    # ===== MEJORA 4: ESTADÍSTICAS =====
    mejor_dia_idx = df['btc_comprados'].idxmax()
    peor_dia_idx = df['btc_comprados'].idxmin()

    mejor_dia_fecha = str(df.loc[mejor_dia_idx, 'fecha'])
    mejor_dia_btc = df.loc[mejor_dia_idx, 'btc_comprados']
    mejor_dia_precio = df.loc[mejor_dia_idx, 'precio_btc_usd']

    peor_dia_fecha = str(df.loc[peor_dia_idx, 'fecha'])
    peor_dia_btc = df.loc[peor_dia_idx, 'btc_comprados']
    peor_dia_precio = df.loc[peor_dia_idx, 'precio_btc_usd']

    racha_dias = total_dias

    # Formatear racha en meses/años
    if racha_dias < 30:
        racha_formato = f"{racha_dias} día{'s' if racha_dias != 1 else ''}"
    elif racha_dias < 365:
        meses = racha_dias // 30
        racha_formato = f"{meses} mes{'es' if meses != 1 else ''}"
    else:
        años = racha_dias // 365
        meses_restantes = (racha_dias % 365) // 30
        if meses_restantes > 0:
            racha_formato = f"{años} año{'s' if años != 1 else ''} y {meses_restantes} mes{'es' if meses_restantes != 1 else ''}"
        else:
            racha_formato = f"{años} año{'s' if años != 1 else ''}"

    # Colores
    color_ganancia = "#10b981" if ganancia >= 0 else "#ef4444"
    simbolo = "+" if ganancia >= 0 else ""
    emoji_tendencia = "📈" if ganancia >= 0 else "📉"

    # ===== DATOS PARA GRÁFICOS =====
    # Generar labels en formato "14 Feb", "15 Feb", etc.
    import locale
    try:
        locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_TIME, 'es_ES')
        except:
            pass  # Si no está disponible, usar el locale por defecto

    fechas_array = [pd.to_datetime(fecha).strftime("%d %b") for fecha in df['fecha']]
    usd_acumulado_array = [(i + 1) * 2.00 for i in range(len(df))]
    valor_btc_array = df['valor_actual_usd'].tolist()
    precio_btc_array = df['precio_btc_usd'].tolist()

    # Timestamp
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    # ===== GENERAR HTML =====
    html_content = f"""<!DOCTYPE html>
<html lang="es" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes">
    <title>📊 Bitcoin DCA Tracker</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;800&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --bg-gradient-start: #667eea;
            --bg-gradient-end: #764ba2;
            --card-bg: rgba(255, 255, 255, 0.95);
            --card-border: rgba(255, 255, 255, 0.3);
            --text-primary: #1f2937;
            --text-secondary: #6b7280;
            --text-tertiary: #9ca3af;
            --shadow: rgba(0, 0, 0, 0.1);
            --shadow-hover: rgba(0, 0, 0, 0.2);
        }}

        [data-theme="dark"] {{
            --bg-gradient-start: #1a1a2e;
            --bg-gradient-end: #16213e;
            --card-bg: rgba(30, 30, 46, 0.8);
            --card-border: rgba(255, 255, 255, 0.1);
            --text-primary: #f3f4f6;
            --text-secondary: #d1d5db;
            --text-tertiary: #9ca3af;
            --shadow: rgba(0, 0, 0, 0.3);
            --shadow-hover: rgba(0, 0, 0, 0.5);
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        /* Mejoras para experiencia táctil en mobile */
        * {{
            -webkit-tap-highlight-color: transparent;
            -webkit-touch-callout: none;
        }}

        html {{
            -webkit-text-size-adjust: 100%;
            text-size-adjust: 100%;
        }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, var(--bg-gradient-start) 0%, var(--bg-gradient-end) 100%);
            background-attachment: fixed;
            min-height: 100vh;
            padding: 20px;
            transition: background 0.3s ease;
            animation: gradientShift 15s ease infinite;
            background-size: 200% 200%;
        }}

        @keyframes gradientShift {{
            0%, 100% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
        }}

        @keyframes fadeInUp {{
            from {{
                opacity: 0;
                transform: translateY(20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        @keyframes pulse {{
            0%, 100% {{ transform: scale(1); }}
            50% {{ transform: scale(1.05); }}
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            animation: fadeInUp 0.6s ease;
        }}

        .header {{
            text-align: center;
            color: white;
            margin-bottom: 40px;
            position: relative;
        }}

        .header h1 {{
            font-size: 3em;
            margin-bottom: 10px;
            font-weight: 700;
            text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
            animation: fadeInUp 0.6s ease 0.1s both;
        }}

        .header p {{
            opacity: 0.95;
            font-size: 1.1em;
            font-weight: 400;
            animation: fadeInUp 0.6s ease 0.2s both;
        }}

        /* MODO OSCURO - Toggle (Icono SVG minimalista) */
        .theme-toggle {{
            position: absolute;
            top: 0;
            right: 0;
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            backdrop-filter: blur(10px);
            width: 48px;
            height: 48px;
            border-radius: 50%;
            cursor: pointer;
            box-shadow: 0 4px 12px var(--shadow);
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .theme-toggle:hover {{
            transform: translateY(-2px) rotate(20deg);
            box-shadow: 0 6px 16px var(--shadow-hover);
        }}

        .theme-toggle svg {{
            width: 24px;
            height: 24px;
            fill: none;
            stroke: var(--text-primary);
            stroke-width: 2;
            stroke-linecap: round;
            stroke-linejoin: round;
            transition: all 0.3s ease;
            pointer-events: none;
        }}

        .theme-toggle-text {{
            display: none;
        }}

        /* Métricas Grid - Estilo compacto con bordes de color */
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
            gap: 14px;
            margin-bottom: 30px;
        }}

        /* Cards con borde de color y separador */
        .metric-card {{
            background: var(--card-bg);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border-left: 4px solid #667eea;
            padding: 18px 22px;
            border-radius: 12px;
            box-shadow: 0 4px 16px var(--shadow);
            transition: all 0.3s ease;
            position: relative;
            animation: fadeInUp 0.6s ease both;
            display: flex;
            flex-direction: column;
        }}

        /* Colores de borde por card */
        .metric-card:nth-child(1) {{
            animation-delay: 0.1s;
            border-left-color: #667eea;
        }}
        .metric-card:nth-child(2) {{
            animation-delay: 0.15s;
            border-left-color: #f7931a;
        }}
        .metric-card:nth-child(3) {{
            animation-delay: 0.2s;
            border-left-color: #10b981;
        }}
        .metric-card:nth-child(4) {{
            animation-delay: 0.25s;
            border-left-color: #ef4444;
        }}
        .metric-card:nth-child(5) {{
            animation-delay: 0.3s;
            border-left-color: #8b5cf6;
        }}
        .metric-card:nth-child(6) {{
            animation-delay: 0.35s;
            border-left-color: #06b6d4;
        }}
        .metric-card:nth-child(7) {{
            animation-delay: 0.4s;
            border-left-color: #f59e0b;
        }}
        .metric-card:nth-child(8) {{
            animation-delay: 0.45s;
            border-left-color: #ec4899;
        }}

        .metric-card:hover {{
            transform: translateX(4px) translateY(-2px);
            box-shadow: 0 8px 24px var(--shadow-hover);
        }}

        /* Label con separador (border-bottom) */
        .metric-label {{
            font-size: 0.7em;
            color: var(--text-tertiary);
            margin-bottom: 12px;
            padding-bottom: 10px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            border-bottom: 1px solid var(--card-border);
        }}

        /* Tipografía monoespaciada para valores */
        .metric-value {{
            font-size: 2em;
            font-weight: 800;
            color: var(--text-primary);
            margin: 8px 0 6px 0;
            line-height: 1.1;
            font-family: 'JetBrains Mono', 'SF Mono', 'Monaco', 'Consolas', monospace;
        }}

        .metric-subtitle {{
            font-size: 0.75em;
            color: var(--text-secondary);
            font-weight: 500;
        }}

        /* Títulos de secciones */
        .section-title {{
            color: white;
            font-size: 1.8em;
            font-weight: 600;
            margin: 40px 0 20px 0;
            text-align: left;
            opacity: 0.95;
            text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
        }}

        /* Secciones de información */
        .info-section {{
            background: var(--card-bg);
            backdrop-filter: blur(10px);
            border-left: 4px solid #667eea;
            padding: 28px 32px;
            border-radius: 12px;
            box-shadow: 0 4px 16px var(--shadow);
            margin-bottom: 20px;
            animation: fadeInUp 0.6s ease 0.4s both;
            transition: all 0.3s ease;
        }}

        .info-section:hover {{
            transform: translateX(4px) translateY(-2px);
            box-shadow: 0 8px 24px var(--shadow-hover);
        }}

        .info-section:nth-of-type(1) {{
            border-left-color: #8b5cf6;
        }}

        .info-section:nth-of-type(2) {{
            border-left-color: #10b981;
        }}

        .info-section h2 {{
            margin-bottom: 24px;
            padding-bottom: 12px;
            border-bottom: 1px solid var(--card-border);
            color: var(--text-primary);
            font-weight: 600;
            font-size: 1.4em;
        }}


        /* Gráficos */
        .chart-container {{
            position: relative;
            height: 400px;
            margin-bottom: 30px;
        }}

        .chart-container canvas {{
            max-height: 400px;
        }}

        footer {{
            text-align: center;
            color: white;
            opacity: 0.9;
            margin-top: 40px;
            padding: 24px;
            font-weight: 400;
            animation: fadeInUp 0.6s ease 0.5s both;
        }}

        /* ===== MOBILE RESPONSIVE - MEJORES PRÁCTICAS ===== */

        /* Tablet y pantallas medianas */
        @media (max-width: 1024px) {{
            body {{
                padding: 15px;
            }}

            .metrics-grid {{
                grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
                gap: 12px;
            }}

            .section-title {{
                font-size: 1.5em;
                margin: 30px 0 15px 0;
            }}
        }}

        /* Mobile */
        @media (max-width: 768px) {{
            body {{
                padding: 12px;
            }}

            /* Header optimizado para mobile */
            .header {{
                margin-bottom: 30px;
                padding-right: 55px;
            }}

            .header h1 {{
                font-size: 1.75em;
                margin-bottom: 8px;
                line-height: 1.2;
            }}

            /* Botón dark mode - tamaño táctil óptimo */
            .theme-toggle {{
                width: 44px;
                height: 44px;
                top: 0;
                right: 0;
            }}

            .theme-toggle svg {{
                width: 20px;
                height: 20px;
            }}

            /* Grid de 2 columnas en mobile */
            .metrics-grid {{
                grid-template-columns: repeat(2, 1fr);
                gap: 10px;
                margin-bottom: 20px;
            }}

            /* Cards optimizadas para 2 columnas en mobile */
            .metric-card {{
                padding: 14px 12px;
                border-radius: 10px;
                border-left-width: 3px;
            }}

            .metric-label {{
                font-size: 0.6em;
                margin-bottom: 8px;
                padding-bottom: 6px;
                letter-spacing: 0.5px;
            }}

            .metric-value {{
                font-size: 1.4em;
                margin: 5px 0 4px 0;
            }}

            .metric-subtitle {{
                font-size: 0.65em;
                line-height: 1.3;
            }}

            /* Section titles más compactos */
            .section-title {{
                font-size: 1.3em;
                margin: 25px 0 12px 0;
            }}

            /* Info sections optimizadas */
            .info-section {{
                padding: 18px 20px;
                border-radius: 10px;
                margin-bottom: 16px;
            }}

            .info-section h2 {{
                font-size: 1.2em;
                margin-bottom: 18px;
                padding-bottom: 10px;
            }}

            /* Gráficos responsivos */
            .chart-container {{
                height: 280px;
                margin-bottom: 20px;
            }}

            .chart-container canvas {{
                max-height: 280px;
            }}

            /* Footer */
            footer {{
                margin-top: 30px;
                padding: 20px;
                font-size: 0.85em;
            }}
        }}

        /* Mobile pequeño (iPhone SE, etc) */
        @media (max-width: 375px) {{
            body {{
                padding: 10px;
            }}

            .header {{
                padding-right: 50px;
            }}

            .header h1 {{
                font-size: 1.5em;
            }}

            .theme-toggle {{
                width: 40px;
                height: 40px;
                top: 0;
            }}

            .theme-toggle svg {{
                width: 18px;
                height: 18px;
            }}

            .metric-card {{
                padding: 14px 16px;
            }}

            .metric-value {{
                font-size: 1.4em;
            }}

            .section-title {{
                font-size: 1.2em;
            }}

            .info-section {{
                padding: 16px 18px;
            }}

            .chart-container {{
                height: 240px;
            }}

            .chart-container canvas {{
                max-height: 240px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <!-- Toggle de Modo Oscuro -->
            <div class="theme-toggle" onclick="toggleTheme()">
                <svg id="theme-icon" viewBox="0 0 24 24">
                    <!-- Sol (modo dark) -->
                    <g class="sun-icon">
                        <circle cx="12" cy="12" r="4"/>
                        <line x1="12" y1="1" x2="12" y2="3"/>
                        <line x1="12" y1="21" x2="12" y2="23"/>
                        <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
                        <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
                        <line x1="1" y1="12" x2="3" y2="12"/>
                        <line x1="21" y1="12" x2="23" y2="12"/>
                        <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
                        <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
                    </g>
                    <!-- Luna (modo light) -->
                    <path class="moon-icon" d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" style="visibility: hidden;"/>
                </svg>
            </div>

            <h1>₿ Bitcoin DCA Tracker</h1>
        </div>

        <!-- Sección 1: Tu Inversión Actual -->
        <h2 class="section-title">💰 Tu Inversión Actual</h2>
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">💵 Total Invertido</div>
                <div class="metric-value">${total_invertido:.2f}</div>
                <div class="metric-subtitle">{total_dias} día{'s' if total_dias != 1 else ''} × $2 USD</div>
            </div>

            <div class="metric-card">
                <div class="metric-label">₿ BTC Acumulado</div>
                <div class="metric-value">{btc_total:.8f}</div>
                <div class="metric-subtitle">Satoshis: {satoshis:,}</div>
            </div>

            <div class="metric-card">
                <div class="metric-label">📈 Valor Actual</div>
                <div class="metric-value">
                    ${valor_actual:.2f}
                </div>
                <div class="metric-subtitle">BTC @ ${precio_actual:,.2f}</div>
            </div>

            <div class="metric-card">
                <div class="metric-label">{emoji_tendencia} Ganancia/Pérdida</div>
                <div class="metric-value" style="color: {color_ganancia}">{simbolo}${ganancia:.2f}</div>
                <div class="metric-subtitle" style="color: {color_ganancia}">{simbolo}{porcentaje:.2f}%</div>
            </div>
        </div>

        <!-- Sección 2: Análisis Histórico -->
        <h2 class="section-title">📊 Análisis Histórico</h2>
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">📊 Precio Promedio</div>
                <div class="metric-value">${precio_promedio:,.2f}</div>
                <div class="metric-subtitle">
                    {'+' if diff_vs_promedio >= 0 else ''}{diff_vs_promedio:.1f}% vs actual
                </div>
            </div>

            <div class="metric-card">
                <div class="metric-label">🏆 Mejor Día de Compra</div>
                <div class="metric-value">${mejor_dia_precio:,.2f}</div>
                <div class="metric-subtitle">{mejor_dia_fecha} · {mejor_dia_btc:.8f} BTC</div>
            </div>

            <div class="metric-card">
                <div class="metric-label">📉 Peor Día de Compra</div>
                <div class="metric-value">${peor_dia_precio:,.2f}</div>
                <div class="metric-subtitle">{peor_dia_fecha} · {peor_dia_btc:.8f} BTC</div>
            </div>

            <div class="metric-card">
                <div class="metric-label">🔥 Racha Consecutiva</div>
                <div class="metric-value">{racha_formato}</div>
                <div class="metric-subtitle">{racha_dias} día{'s' if racha_dias != 1 else ''} totales</div>
            </div>
        </div>

        <!-- Primer Gráfico - Evolución del DCA -->
        <div class="info-section">
            <h2>📊 Evolución del DCA</h2>
            <div class="chart-container">
                <canvas id="dcaChart"></canvas>
            </div>
        </div>

        <!-- Segundo Gráfico - Precio de Bitcoin -->
        <div class="info-section">
            <h2>💹 Precio de Bitcoin en el Tiempo</h2>
            <div class="chart-container">
                <canvas id="btcPriceChart"></canvas>
            </div>
        </div>

        <footer>
            <p>@ Generado automáticamente · {timestamp}</p>
        </footer>
    </div>

    <script>
        // ===== MODO OSCURO =====
        function toggleTheme() {{
            const html = document.documentElement;
            const currentTheme = html.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

            html.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);

            // Actualizar icono SVG
            updateThemeIcon(newTheme);

            // Actualizar gráficos
            updateChartsTheme(newTheme);
        }}

        function updateThemeIcon(theme) {{
            const svg = document.getElementById('theme-icon');
            const sunIcon = svg.querySelector('.sun-icon');
            const moonIcon = svg.querySelector('.moon-icon');

            if (theme === 'dark') {{
                // Modo dark: mostrar sol (para cambiar a light)
                sunIcon.style.visibility = 'visible';
                moonIcon.style.visibility = 'hidden';
            }} else {{
                // Modo light: mostrar luna (para cambiar a dark)
                sunIcon.style.visibility = 'hidden';
                moonIcon.style.visibility = 'visible';
            }}
        }}

        // Cargar tema guardado
        const savedTheme = localStorage.getItem('theme') || 'dark';
        document.documentElement.setAttribute('data-theme', savedTheme);
        updateThemeIcon(savedTheme);

        // Datos desde Python
        const labels = {fechas_array};
        const dataInvertido = {usd_acumulado_array};
        const dataValorBTC = {valor_btc_array};
        const dataPrecioBTC = {precio_btc_array};

        // Configuración de colores según tema
        function getChartColors() {{
            const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
            return {{
                textColor: isDark ? '#f3f4f6' : '#1f2937',
                gridColor: isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)',
            }};
        }}

        let dcaChart, btcPriceChart;

        // MEJORA 2: Primer Gráfico - Evolución del DCA
        const ctx1 = document.getElementById('dcaChart').getContext('2d');
        dcaChart = new Chart(ctx1, {{
            type: 'line',
            data: {{
                labels: labels,
                datasets: [
                    {{
                        label: '💵 USD Invertidos',
                        data: dataInvertido,
                        borderColor: '#667eea',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        borderWidth: 3,
                        tension: 0.4,
                        fill: true,
                        pointRadius: 4,
                        pointHoverRadius: 6,
                    }},
                    {{
                        label: '₿ Valor en BTC',
                        data: dataValorBTC,
                        borderColor: '#f7931a',
                        backgroundColor: 'rgba(247, 147, 26, 0.1)',
                        borderWidth: 3,
                        tension: 0.4,
                        fill: true,
                        pointRadius: 4,
                        pointHoverRadius: 6,
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                interaction: {{
                    mode: 'index',
                    intersect: false,
                }},
                plugins: {{
                    tooltip: {{
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        padding: 12,
                        titleFont: {{ size: 14, weight: 'bold' }},
                        bodyFont: {{ size: 13 }},
                        borderColor: '#667eea',
                        borderWidth: 1,
                        callbacks: {{
                            label: function(context) {{
                                return context.dataset.label + ': $' + context.parsed.y.toFixed(2);
                            }}
                        }}
                    }},
                    legend: {{
                        position: 'top',
                        labels: {{
                            color: getChartColors().textColor,
                            font: {{ size: 14, weight: '500' }},
                            padding: 20,
                            usePointStyle: true,
                        }}
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        suggestedMax: 10,
                        grace: '5%',
                        grid: {{
                            color: getChartColors().gridColor,
                            drawBorder: true,
                            drawOnChartArea: true,
                            lineWidth: 1,
                        }},
                        ticks: {{
                            color: getChartColors().textColor,
                            stepSize: 2,
                            callback: function(value) {{
                                return '$' + value.toFixed(0);
                            }}
                        }},
                        border: {{
                            color: getChartColors().gridColor,
                            width: 2,
                        }}
                    }},
                    x: {{
                        grid: {{
                            color: getChartColors().gridColor,
                            drawBorder: true,
                            lineWidth: 1,
                        }},
                        ticks: {{
                            color: getChartColors().textColor,
                            maxRotation: 45,
                            minRotation: 45,
                        }},
                        border: {{
                            color: getChartColors().gridColor,
                            width: 2,
                        }}
                    }}
                }}
            }}
        }});

        // MEJORA 2: Segundo Gráfico - Precio de Bitcoin
        const ctx2 = document.getElementById('btcPriceChart').getContext('2d');
        btcPriceChart = new Chart(ctx2, {{
            type: 'line',
            data: {{
                labels: labels,
                datasets: [
                    {{
                        label: '💰 Precio de Bitcoin (USD)',
                        data: dataPrecioBTC,
                        borderColor: '#10b981',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        borderWidth: 3,
                        tension: 0.4,
                        fill: true,
                        pointRadius: 4,
                        pointHoverRadius: 6,
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                interaction: {{
                    mode: 'index',
                    intersect: false,
                }},
                plugins: {{
                    tooltip: {{
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        padding: 12,
                        titleFont: {{ size: 14, weight: 'bold' }},
                        bodyFont: {{ size: 13 }},
                        borderColor: '#10b981',
                        borderWidth: 1,
                        callbacks: {{
                            label: function(context) {{
                                return 'Precio: $' + context.parsed.y.toLocaleString('en-US', {{minimumFractionDigits: 2}});
                            }}
                        }}
                    }},
                    legend: {{
                        position: 'top',
                        labels: {{
                            color: getChartColors().textColor,
                            font: {{ size: 14, weight: '500' }},
                            padding: 20,
                            usePointStyle: true,
                        }}
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: false,
                        grace: '10%',
                        grid: {{
                            color: getChartColors().gridColor,
                            drawBorder: true,
                            drawOnChartArea: true,
                            lineWidth: 1,
                        }},
                        ticks: {{
                            color: getChartColors().textColor,
                            maxTicksLimit: 8,
                            callback: function(value) {{
                                return '$' + value.toLocaleString('en-US', {{maximumFractionDigits: 0}});
                            }}
                        }},
                        border: {{
                            color: getChartColors().gridColor,
                            width: 2,
                        }}
                    }},
                    x: {{
                        grid: {{
                            color: getChartColors().gridColor,
                            drawBorder: true,
                            lineWidth: 1,
                        }},
                        ticks: {{
                            color: getChartColors().textColor,
                            maxRotation: 45,
                            minRotation: 45,
                        }},
                        border: {{
                            color: getChartColors().gridColor,
                            width: 2,
                        }}
                    }}
                }}
            }}
        }});

        // Función para actualizar tema de los gráficos
        function updateChartsTheme(theme) {{
            const colors = getChartColors();

            // Actualizar DCA Chart
            dcaChart.options.plugins.legend.labels.color = colors.textColor;
            dcaChart.options.scales.x.ticks.color = colors.textColor;
            dcaChart.options.scales.y.ticks.color = colors.textColor;
            dcaChart.options.scales.x.grid.color = colors.gridColor;
            dcaChart.options.scales.y.grid.color = colors.gridColor;
            dcaChart.update();

            // Actualizar BTC Price Chart
            btcPriceChart.options.plugins.legend.labels.color = colors.textColor;
            btcPriceChart.options.scales.x.ticks.color = colors.textColor;
            btcPriceChart.options.scales.y.ticks.color = colors.textColor;
            btcPriceChart.options.scales.x.grid.color = colors.gridColor;
            btcPriceChart.options.scales.y.grid.color = colors.gridColor;
            btcPriceChart.update();
        }}

        // Aplicar tema inicial a los gráficos
        updateChartsTheme(savedTheme);
    </script>
</body>
</html>"""

    # Guardar HTML
    with open(DASHBOARD_FILE, 'w', encoding='utf-8') as f:
        f.write(html_content)

    log_message(f"✓ Dashboard generado en {DASHBOARD_FILE}")

if __name__ == "__main__":
    update_btc_data()
