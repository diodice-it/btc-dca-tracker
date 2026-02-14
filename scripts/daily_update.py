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
DASHBOARD_FILE = BASE_DIR / "dashboard.html"
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
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📊 Bitcoin DCA Tracker</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
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

        /* MEJORA 5: MODO OSCURO - Toggle */
        .theme-toggle {{
            position: fixed;
            top: 30px;
            right: 30px;
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            backdrop-filter: blur(10px);
            padding: 12px 20px;
            border-radius: 50px;
            cursor: pointer;
            font-size: 1.2em;
            box-shadow: 0 4px 12px var(--shadow);
            transition: all 0.3s ease;
            z-index: 1000;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .theme-toggle:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 16px var(--shadow-hover);
        }}

        .theme-toggle-text {{
            font-size: 0.85em;
            color: var(--text-secondary);
            font-weight: 500;
        }}

        /* Métricas Grid - Ahora con 5 tarjetas */
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 24px;
            margin-bottom: 30px;
        }}

        /* Glassmorphism en tarjetas */
        .metric-card {{
            background: var(--card-bg);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid var(--card-border);
            padding: 28px;
            border-radius: 20px;
            box-shadow: 0 8px 32px var(--shadow);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
            animation: fadeInUp 0.6s ease both;
        }}

        .metric-card:nth-child(1) {{ animation-delay: 0.1s; }}
        .metric-card:nth-child(2) {{ animation-delay: 0.15s; }}
        .metric-card:nth-child(3) {{ animation-delay: 0.2s; }}
        .metric-card:nth-child(4) {{ animation-delay: 0.25s; }}
        .metric-card:nth-child(5) {{ animation-delay: 0.3s; }}
        .metric-card:nth-child(6) {{ animation-delay: 0.35s; }}
        .metric-card:nth-child(7) {{ animation-delay: 0.4s; }}
        .metric-card:nth-child(8) {{ animation-delay: 0.45s; }}

        .metric-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #667eea, #764ba2);
            opacity: 0;
            transition: opacity 0.3s ease;
        }}

        .metric-card:hover::before {{
            opacity: 1;
        }}

        .metric-card:hover {{
            transform: translateY(-8px) scale(1.02);
            box-shadow: 0 16px 48px var(--shadow-hover);
        }}

        .metric-label {{
            font-size: 0.95em;
            color: var(--text-secondary);
            margin-bottom: 12px;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .metric-value {{
            font-size: 2.2em;
            font-weight: 700;
            color: var(--text-primary);
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .metric-subtitle {{
            font-size: 0.9em;
            color: var(--text-tertiary);
            font-weight: 400;
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
            border: 1px solid var(--card-border);
            padding: 35px;
            border-radius: 20px;
            box-shadow: 0 8px 32px var(--shadow);
            margin-bottom: 24px;
            animation: fadeInUp 0.6s ease 0.4s both;
        }}

        .info-section h2 {{
            margin-bottom: 24px;
            color: var(--text-primary);
            font-weight: 600;
            font-size: 1.5em;
        }}


        /* Gráficos */
        .chart-container {{
            position: relative;
            margin-bottom: 30px;
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

        @media (max-width: 768px) {{
            .header h1 {{ font-size: 2em; }}
            .metric-value {{ font-size: 1.6em; }}
            .theme-toggle {{
                top: 20px;
                right: 20px;
                padding: 10px 16px;
            }}
            .info-section {{ padding: 24px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- MEJORA 5: Toggle de Modo Oscuro -->
        <div class="theme-toggle" onclick="toggleTheme()">
            <span id="theme-icon">☀️</span>
            <span class="theme-toggle-text" id="theme-text">Modo Claro</span>
        </div>

        <!-- Header -->
        <div class="header">
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

        <!-- MEJORA 2: Primer Gráfico - Evolución del DCA -->
        <div class="info-section">
            <h2>📊 Evolución del DCA</h2>
            <div class="chart-container">
                <canvas id="dcaChart" height="80"></canvas>
            </div>
        </div>

        <!-- MEJORA 2: Segundo Gráfico - Precio de Bitcoin -->
        <div class="info-section">
            <h2>💹 Precio de Bitcoin en el Tiempo</h2>
            <div class="chart-container">
                <canvas id="btcPriceChart" height="80"></canvas>
            </div>
        </div>

        <footer>
            <p>@ Generado automáticamente · {timestamp}</p>
        </footer>
    </div>

    <script>
        // ===== MEJORA 5: MODO OSCURO =====
        function toggleTheme() {{
            const html = document.documentElement;
            const currentTheme = html.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

            html.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);

            // Actualizar icono y texto
            const icon = document.getElementById('theme-icon');
            const text = document.getElementById('theme-text');

            if (newTheme === 'dark') {{
                icon.textContent = '☀️';
                text.textContent = 'Modo Claro';
            }} else {{
                icon.textContent = '🌙';
                text.textContent = 'Modo Oscuro';
            }}

            // Actualizar gráficos
            updateChartsTheme(newTheme);
        }}

        // Cargar tema guardado
        const savedTheme = localStorage.getItem('theme') || 'dark';
        document.documentElement.setAttribute('data-theme', savedTheme);
        if (savedTheme === 'dark') {{
            document.getElementById('theme-icon').textContent = '☀️';
            document.getElementById('theme-text').textContent = 'Modo Claro';
        }}

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
