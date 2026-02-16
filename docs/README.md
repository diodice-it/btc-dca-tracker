# 📊 Bitcoin DCA Tracker - Guía Completa

Sistema automático para simular la compra diaria de $2 USD en Bitcoin y visualizar el rendimiento de la estrategia Dollar Cost Averaging (DCA).

---

## 📑 Tabla de Contenidos

1. [¿Qué es este proyecto?](#-qué-es-este-proyecto)
2. [¿Cómo funciona el sistema?](#-cómo-funciona-el-sistema)
3. [Estructura del Proyecto](#-estructura-del-proyecto)
4. [Guía Rápida de Uso](#-guía-rápida-de-uso)
5. [Dashboard Web - Explicación Detallada](#-dashboard-web---explicación-detallada)
6. [Entender el DCA (Dollar Cost Averaging)](#-entender-el-dca-dollar-cost-averaging)
7. [Cómo Funciona Técnicamente](#-cómo-funciona-técnicamente)
8. [Automatización - Configuración y Gestión](#-automatización---configuración-y-gestión)
9. [Datos y Archivos](#-datos-y-archivos)
10. [Troubleshooting (Solución de Problemas)](#-troubleshooting-solución-de-problemas)
11. [Preguntas Frecuentes](#-preguntas-frecuentes)
12. [Seguridad y Privacidad](#-seguridad-y-privacidad)

---

## 🎯 ¿Qué es este proyecto?

Este es un **simulador educativo** que te permite visualizar qué pasaría si compraras **$2 USD en Bitcoin cada día** usando la estrategia de Dollar Cost Averaging (DCA).

### Objetivos del Proyecto

1. **Educativo**: Entender cómo funciona la estrategia DCA en la práctica
2. **Visualización**: Ver gráficamente cómo las compras regulares suavizan la volatilidad
3. **Seguimiento**: Monitorear el rendimiento acumulado día a día
4. **Automático**: El sistema se actualiza solo, sin intervención manual

### ⚠️ Importante

- **Esto es una SIMULACIÓN**: No se compra Bitcoin real
- **Solo con fines educativos**: No es asesoramiento financiero
- **Datos locales**: Todo se guarda en tu computadora, no se envía a ningún servidor

---

## ⚙️ ¿Cómo funciona el sistema?

El sistema funciona completamente de forma automática cada día a las **9:00 AM**:

```
┌─────────────────────────────────────────────────────────┐
│  9:00 AM - Ejecución Automática Diaria                 │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
         ┌────────────────────────────────┐
         │  1. Consultar API CoinGecko    │
         │     Obtener precio real de BTC │
         └────────────────────────────────┘
                          │
                          ▼
         ┌────────────────────────────────┐
         │  2. Calcular Compra del Día    │
         │     $2 USD ÷ Precio BTC        │
         └────────────────────────────────┘
                          │
                          ▼
         ┌────────────────────────────────┐
         │  3. Actualizar Acumulados      │
         │     BTC total + valor USD      │
         └────────────────────────────────┘
                          │
                          ▼
         ┌────────────────────────────────┐
         │  4. Guardar en CSV             │
         │     data/btc_purchases.csv     │
         └────────────────────────────────┘
                          │
                          ▼
         ┌────────────────────────────────┐
         │  5. Regenerar Dashboard        │
         │     dashboard.html             │
         └────────────────────────────────┘
                          │
                          ▼
                    ✅ Listo!
```

---

## 📁 Estructura del Proyecto

```
/Users/diodice/BTC/
│
├── data/
│   └── btc_purchases.csv          # 📊 Base de datos de compras diarias
│                                  #     - Fecha, precio, BTC comprado, acumulados
│                                  #     - Formato CSV para Excel/Numbers
│
├── scripts/
│   └── daily_update.py            # 🤖 Script principal en Python
│                                  #     - Se ejecuta automáticamente a las 9 AM
│                                  #     - Consulta API, calcula, guarda datos
│                                  #     - Genera el dashboard
│
├── logs/                          # 📝 Registro de ejecuciones
│   ├── stdout.log                 #     - Salida estándar del script
│   ├── stderr.log                 #     - Errores si los hay
│   └── btc_tracker_YYYYMM.log     #     - Log detallado por mes
│
├── dashboard.html                 # 📈 Dashboard web interactivo
│                                  #     - Gráfico Chart.js
│                                  #     - Métricas en tiempo real
│                                  #     - ⭐ ESTE ES EL ARCHIVO QUE ABRES
│
└── README.md                      # 📖 Esta guía completa
```

### Archivos Clave

| Archivo | ¿Qué hace? | ¿Cuándo lo uso? |
|---------|-----------|-----------------|
| `dashboard.html` | Muestra los gráficos y métricas | Abrilo para ver el progreso |
| `btc_purchases.csv` | Guarda todas las compras | Abrilo en Excel/Numbers para ver los datos |
| `daily_update.py` | Script que hace la magia | Ejecutalo manualmente si querés |
| Carpeta `logs/` | Registro de lo que pasó | Cuando algo no funciona |

---

## 🚀 Guía Rápida de Uso

### 1️⃣ Ver el Dashboard (Lo Más Común)

**Opción A - Desde el Finder** (más fácil):
1. Abrí el Finder
2. Andá a la carpeta `/Users/diodice/BTC/`
3. Hacé doble click en `dashboard.html`
4. Se abre en tu navegador (Chrome, Safari, etc.)

**Opción B - Desde la Terminal**:
```bash
open /Users/diodice/BTC/dashboard.html
```

**Opción C - Agregar a Favoritos** (recomendado):
1. Abrí `dashboard.html` una vez
2. En tu navegador, agregalo a favoritos (⌘+D)
3. Ahora podés abrirlo desde favoritos siempre

### 2️⃣ Ejecutar Manualmente el Script

Si querés forzar una actualización sin esperar a las 9 AM:

```bash
# Opción 1: Ir a la carpeta y ejecutar
cd /Users/diodice/BTC
python3 scripts/daily_update.py

# Opción 2: Ejecutar directo desde cualquier lado
python3 /Users/diodice/BTC/scripts/daily_update.py
```

**Nota**: Si ya se ejecutó hoy, el script te avisará y no duplicará el registro.

### 3️⃣ Ver los Datos en Formato Tabla

Para ver los datos históricos en Excel o Numbers:

```bash
# Abre el CSV en tu app predeterminada (Excel, Numbers, etc.)
open /Users/diodice/BTC/data/btc_purchases.csv
```

O podés ver los datos en la terminal:

```bash
# Ver todo el archivo
cat /Users/diodice/BTC/data/btc_purchases.csv

# Ver solo las primeras 10 líneas
head -10 /Users/diodice/BTC/data/btc_purchases.csv

# Ver solo las últimas 10 líneas (más recientes)
tail -10 /Users/diodice/BTC/data/btc_purchases.csv
```

---

## 📈 Dashboard Web - Explicación Detallada

### Métricas Principales

El dashboard muestra 4 tarjetas con información clave:

#### 1. 💵 Total Invertido
```
$X.XX
Y días × $2 USD
```
- **Qué significa**: Cuánta plata invertiste en total hasta hoy
- **Cálculo**: Número de días × $2 USD
- **Ejemplo**: Si llevás 30 días, invertiste $60 USD

#### 2. ₿ BTC Acumulado
```
0.XXXXXXXX BTC
Satoshis: XXX,XXX
```
- **Qué significa**: Cuánto Bitcoin acumulaste con tus compras
- **Satoshis**: 1 BTC = 100,000,000 satoshis (es como los centavos del Bitcoin)
- **Ejemplo**: 0.00100000 BTC = 100,000 satoshis

#### 3. 📈 Valor Actual
```
$XXX.XX
BTC @ $XX,XXX
```
- **Qué significa**: Cuánto vale HOY todo tu Bitcoin acumulado
- **Cálculo**: BTC acumulado × Precio actual de BTC
- **Ejemplo**: Si tenés 0.001 BTC y BTC vale $70,000 → Valor = $70

#### 4. 📈/📉 Ganancia/Pérdida
```
+$XX.XX (verde) o -$XX.XX (rojo)
+X.XX% o -X.XX%
```
- **Qué significa**: Cuánto ganaste o perdiste vs lo que invertiste
- **Cálculo**: Valor Actual - Total Invertido
- **Color verde**: Estás ganando 🎉
- **Color rojo**: Estás perdiendo (temporal, es normal en DCA)

### Gráfico Interactivo

El gráfico muestra dos líneas en el tiempo:

**Línea Azul - 💵 USD Invertidos**:
- Es una línea recta que sube de a $2 por día
- Representa tu inversión acumulada
- Siempre sube al mismo ritmo ($2/día)

**Línea Naranja - ₿ Valor en BTC**:
- Representa cuánto vale tu BTC acumulado cada día
- Sube y baja según el precio de Bitcoin
- Si está arriba de la azul = ganando
- Si está abajo de la azul = perdiendo (temporal)

**Cómo usar el gráfico**:
- **Pasa el mouse** sobre cualquier punto para ver los valores exactos
- **Compará las dos líneas**: la distancia entre ellas es tu ganancia/pérdida
- **Observá tendencias**: con DCA, la línea naranja debería tender a subir en el largo plazo

### Ejemplo Visual de Interpretación

```
Escenario A - Mercado Alcista (Bitcoin sube):
    Valor BTC (naranja) ↗️ ↗️ ↗️ ↗️
    Invertido (azul)    ↗️ ↗️ ↗️ ↗️
    → Ganancia creciente ✅

Escenario B - Mercado Bajista (Bitcoin baja):
    Valor BTC (naranja) ↘️ ↘️ ↘️ ↘️
    Invertido (azul)    ↗️ ↗️ ↗️ ↗️
    → Pérdida temporal, PERO comprás más BTC por el mismo dinero 💡

Escenario C - Mercado Lateral (Bitcoin estable):
    Valor BTC (naranja) → → → →
    Invertido (azul)    ↗️ ↗️ ↗️ ↗️
    → Acumulás BTC sin volatilidad
```

---

## 🎓 Entender el DCA (Dollar Cost Averaging)

### ¿Qué es el DCA?

**Dollar Cost Averaging** (Promedio de Costo en Dólares) es una estrategia de inversión donde:
- Invertís una **cantidad fija** ($2 USD en este caso)
- En **intervalos regulares** (cada día)
- **Sin importar el precio** del activo (Bitcoin)

### ¿Por qué funciona?

#### Problema que resuelve: Market Timing

**Sin DCA** (inversión única):
```
Día 1: Invertís $100 cuando BTC = $50,000
       → Comprás 0.002 BTC

¿Qué pasa si al día siguiente BTC baja a $40,000?
       → Tu inversión ahora vale $80 (perdiste $20)
       → Compraste en el "momento equivocado"
```

**Con DCA** (inversión regular):
```
Día 1:  Invertís $10, BTC = $50,000 → Comprás 0.0002 BTC
Día 2:  Invertís $10, BTC = $40,000 → Comprás 0.00025 BTC ⭐
Día 3:  Invertís $10, BTC = $45,000 → Comprás 0.000222 BTC
...
Día 10: Invertís $10, BTC = $55,000 → Comprás 0.000182 BTC

Total invertido: $100
Total BTC: más que en la inversión única porque compraste barato varios días
Precio promedio: mejor que $50,000
```

### Ventajas del DCA

#### 1. ✅ Elimina el riesgo de "market timing"
No tenés que adivinar cuándo es el mejor momento para comprar. Comprás siempre.

#### 2. ✅ Aprovecha las bajas
Cuando el precio baja, tu mismo monto compra MÁS Bitcoin. Es como un descuento automático.

**Ejemplo numérico**:
```
Compra 1: $2 ÷ $60,000/BTC = 0.00003333 BTC
Compra 2: $2 ÷ $30,000/BTC = 0.00006666 BTC (¡el doble!)
Compra 3: $2 ÷ $45,000/BTC = 0.00004444 BTC

Promedio comprado: 0.00004814 BTC por $2 USD
Precio promedio pagado: $41,538 (mejor que $60,000 inicial)
```

#### 3. ✅ Reduce la volatilidad emocional
No comprás cuando estás emocionado (porque el precio sube) ni vendés por miedo (cuando baja). Es automático.

#### 4. ✅ Es disciplinado
Al ser automático, no hay excusas. La disciplina es clave en inversiones a largo plazo.

### Desventajas del DCA (para ser transparentes)

#### ❌ En mercados constantemente alcistas, una inversión única puede rendir más
Si BTC solo sube sin parar, invertir todo al principio hubiera sido mejor. Pero... ¿quién puede predecir eso?

#### ❌ Comisiones de transacción
En el mundo real, cada compra tiene una comisión. Comprar $2 diarios puede ser poco eficiente. (Pero este es solo un simulador 😉)

### Ejemplo Real de DCA

**Escenario**: Invertís $2 diarios durante 90 días

| Semana | Precio BTC | USD Invertidos | BTC Acumulado | Valor Actual |
|--------|-----------|----------------|---------------|--------------|
| 1      | $50,000   | $14            | 0.00028       | $14          |
| 4      | $45,000   | $56            | 0.00126       | $56.70       |
| 8      | $40,000   | $112           | 0.00285       | $114         |
| 12     | $55,000   | $168           | 0.00318       | $174.90      |

Observá cómo en la semana 8 (cuando BTC bajó a $40k) acumulaste MÁS Bitcoin, lo que te benefició cuando subió a $55k en la semana 12.

### Filosofía del DCA

> "El tiempo en el mercado es mejor que intentar timear el mercado"
> — Inversor anónimo

El DCA es para inversores que:
- Creen en el activo a largo plazo
- No tienen tiempo/conocimiento para hacer trading
- Prefieren dormir tranquilos sin estresarse por las fluctuaciones diarias

---

## 🔧 Cómo Funciona Técnicamente

### 1. Consulta de Precio (API CoinGecko)

**¿Qué es CoinGecko?**
- Plataforma que recopila precios de criptomonedas en tiempo real
- Gratuita (no requiere registro ni API key)
- Actualiza precios cada ~60 segundos

**Endpoint usado**:
```
https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd
```

**Respuesta de ejemplo**:
```json
{
  "bitcoin": {
    "usd": 69784
  }
}
```

**Manejo de errores**:
- Si falla la conexión, reintenta 3 veces con backoff exponencial (1s, 2s, 4s)
- Si el precio es inválido (≤0), lanza error
- Todos los errores se registran en los logs

### 2. Cálculo de la Compra

**Fórmula**:
```python
btc_comprados = usd_invertidos / precio_btc_usd

# Ejemplo:
# $2 USD / $69,784 = 0.00002866 BTC
```

**Formato de números**:
- BTC se guarda con 8 decimales (precisión de satoshi)
- USD se guarda con 2 decimales (centavos)

### 3. Actualización de Acumulados

**Variables que se rastrean**:

| Variable | Descripción | Cálculo |
|----------|-------------|---------|
| `btc_comprados` | BTC comprado HOY | $2 / precio_btc |
| `btc_acumulado` | BTC total hasta hoy | suma de todos los `btc_comprados` |
| `usd_invertidos` | USD invertido HOY | Siempre $2 |
| `total_invertido` | USD total hasta hoy | días × $2 |
| `valor_actual_usd` | Valor del BTC acumulado | btc_acumulado × precio_btc_hoy |

### 4. Almacenamiento en CSV

**Formato del archivo `btc_purchases.csv`**:

```csv
fecha,precio_btc_usd,usd_invertidos,btc_comprados,btc_acumulado,valor_actual_usd
2026-02-14,69784.00,2.00,0.00002866,0.00002866,2.00
2026-02-15,70000.00,2.00,0.00002857,0.00005723,4.01
2026-02-16,68500.00,2.00,0.00002920,0.00008643,5.92
```

**Columnas**:
- `fecha`: YYYY-MM-DD
- `precio_btc_usd`: Precio de 1 BTC en USD ese día
- `usd_invertidos`: Siempre 2.00
- `btc_comprados`: BTC comprado ese día (8 decimales)
- `btc_acumulado`: BTC total hasta ese día (running sum)
- `valor_actual_usd`: btc_acumulado × precio del DÍA (no de hoy)

### 5. Generación del Dashboard

**Tecnologías**:
- **HTML5**: Estructura
- **CSS3**: Estilos (gradientes, tarjetas, responsive)
- **Chart.js**: Gráfico interactivo (librería JavaScript)

**Proceso**:
1. Python lee el CSV con pandas
2. Calcula métricas (total invertido, ganancia, etc.)
3. Genera arrays de datos para Chart.js
4. Interpola los datos en plantilla HTML
5. Guarda `dashboard.html`

**¿Por qué Chart.js?**
- Ligera (~65KB)
- Responsive (se adapta a móviles)
- Tooltips interactivos
- Animaciones suaves
- Carga desde CDN (no requiere instalación)

---

## 🤖 Automatización - Configuración y Gestión

### ¿Qué es launchd?

**launchd** es el sistema de automatización nativo de macOS. Es como el cron de Linux pero más moderno.

**Ventajas sobre cron**:
- ✅ Más confiable (reinicia si el script falla)
- ✅ Mejor manejo de logs
- ✅ Integrado con macOS
- ✅ Se ejecuta aunque no hayas iniciado sesión

### Configuración Actual

El servicio está configurado en:
```
~/Library/LaunchAgents/com.dario.btc-dca-tracker.plist
```

**Configuración**:
```xml
<key>StartCalendarInterval</key>
<dict>
    <key>Hour</key>
    <integer>9</integer>      <!-- 9:00 AM -->
    <key>Minute</key>
    <integer>0</integer>      <!-- En punto -->
</dict>
```

### Comandos de Gestión

#### Ver si está activo
```bash
launchctl list | grep btc-dca
```

**Salida esperada**:
```
-    0    com.dario.btc-dca-tracker
```

El `0` indica que la última ejecución fue exitosa (exit code 0).

#### Ver información detallada
```bash
launchctl print user/$(id -u)/com.dario.btc-dca-tracker
```

Esto muestra:
- Próxima ejecución programada
- Última ejecución
- Estado del servicio

#### Ejecutar manualmente (sin esperar a las 9 AM)
```bash
launchctl start com.dario.btc-dca-tracker
```

#### Desactivar la automatización
```bash
launchctl unload ~/Library/LaunchAgents/com.dario.btc-dca-tracker.plist
```

#### Volver a activar
```bash
launchctl load ~/Library/LaunchAgents/com.dario.btc-dca-tracker.plist
```

#### Reiniciar el servicio (si hiciste cambios)
```bash
launchctl unload ~/Library/LaunchAgents/com.dario.btc-dca-tracker.plist
launchctl load ~/Library/LaunchAgents/com.dario.btc-dca-tracker.plist
```

### Cambiar el Horario de Ejecución

Si querés que se ejecute a otra hora (ej: 6:00 PM):

1. **Editar el archivo plist**:
```bash
nano ~/Library/LaunchAgents/com.dario.btc-dca-tracker.plist
```

2. **Cambiar la hora**:
```xml
<key>Hour</key>
<integer>18</integer>     <!-- Cambiá 9 por 18 -->
<key>Minute</key>
<integer>0</integer>
```

3. **Reiniciar el servicio**:
```bash
launchctl unload ~/Library/LaunchAgents/com.dario.btc-dca-tracker.plist
launchctl load ~/Library/LaunchAgents/com.dario.btc-dca-tracker.plist
```

### Logs de Automatización

Los logs se guardan automáticamente:

**Logs del sistema launchd**:
```bash
# Salida estándar (mensajes normales)
tail -f /Users/diodice/BTC/logs/stdout.log

# Errores
tail -f /Users/diodice/BTC/logs/stderr.log
```

**Logs detallados del script**:
```bash
# Log del mes actual
tail -f /Users/diodice/BTC/logs/btc_tracker_$(date +%Y%m).log

# Ver últimas 50 líneas
tail -50 /Users/diodice/BTC/logs/btc_tracker_*.log
```

---

## 📊 Datos y Archivos

### Archivo CSV - Explicación Profunda

#### Ejemplo de Datos Reales

```csv
fecha,precio_btc_usd,usd_invertidos,btc_comprados,btc_acumulado,valor_actual_usd
2026-02-14,69784.00,2.00,0.00002866,0.00002866,2.00
2026-02-15,70500.00,2.00,0.00002837,0.00005703,4.02
2026-02-16,68200.00,2.00,0.00002933,0.00008636,5.89
2026-02-17,71000.00,2.00,0.00002817,0.00011453,8.13
```

#### Análisis Línea por Línea

**Día 1 (2026-02-14)**:
- Precio BTC: $69,784
- Compraste: 0.00002866 BTC (2,866 satoshis)
- Acumulado: 0.00002866 BTC
- Valor: $2.00 (igual a lo invertido)

**Día 2 (2026-02-15)**:
- Precio BTC: $70,500 (subió $716)
- Compraste: 0.00002837 BTC (menos BTC porque el precio subió)
- Acumulado: 0.00005703 BTC
- Valor: $4.02 (ganaste $0.02 por la suba de precio)

**Día 3 (2026-02-16)**:
- Precio BTC: $68,200 (bajó $2,300)
- Compraste: 0.00002933 BTC (MÁS BTC porque el precio bajó!)
- Acumulado: 0.00008636 BTC
- Valor: $5.89 (perdiste $0.11 vs invertido, pero acumulaste más BTC)

**Día 4 (2026-02-17)**:
- Precio BTC: $71,000 (recuperó y subió más)
- Compraste: 0.00002817 BTC
- Acumulado: 0.00011453 BTC
- Valor: $8.13 (ganaste $0.13 vs $8 invertidos)

**Lección**: La baja del día 3 te permitió acumular más BTC, lo que te benefició cuando subió el día 4.

### Abrir y Analizar el CSV

#### En Excel / Numbers

```bash
open /Users/diodice/BTC/data/btc_purchases.csv
```

**Análisis que podés hacer**:

1. **Calcular precio promedio de compra**:
   ```
   = SUMA(usd_invertidos) / SUMA(btc_comprados)
   ```

2. **Encontrar el mejor día de compra** (más BTC comprado):
   ```
   = MAX(btc_comprados)
   ```

3. **Ganancia/Pérdida porcentual**:
   ```
   = (valor_actual - total_invertido) / total_invertido * 100
   ```

#### En la Terminal

**Ver las primeras compras**:
```bash
head -5 /Users/diodice/BTC/data/btc_purchases.csv
```

**Ver las últimas compras**:
```bash
tail -5 /Users/diodice/BTC/data/btc_purchases.csv
```

**Contar cuántos días llevas**:
```bash
wc -l /Users/diodice/BTC/data/btc_purchases.csv
# Restale 1 por el header
```

**Ver solo fechas y precios**:
```bash
awk -F',' '{print $1, $2}' /Users/diodice/BTC/data/btc_purchases.csv
```

### Backup de Datos

**Hacer backup manual**:
```bash
# Copiar CSV a carpeta de backups
cp /Users/diodice/BTC/data/btc_purchases.csv ~/Desktop/btc_backup_$(date +%Y%m%d).csv

# O crear un ZIP con todo
cd /Users/diodice
zip -r ~/Desktop/BTC_backup_$(date +%Y%m%d).zip BTC/
```

**Restaurar un backup**:
```bash
cp ~/Desktop/btc_backup_20260314.csv /Users/diodice/BTC/data/btc_purchases.csv
```

---

## 🔧 Troubleshooting (Solución de Problemas)

### Problema 1: El dashboard no muestra el gráfico

**Síntoma**: Ves las tarjetas de métricas pero el gráfico no aparece.

**Causas posibles**:

1. **Sin conexión a internet la primera vez**
   - Chart.js se descarga desde CDN
   - Solución: Conectate a internet y recargá la página (⌘+R)

2. **Bloqueador de ads/JavaScript deshabilitado**
   - Algunos bloqueadores bloquean Chart.js
   - Solución: Desactiva el bloqueador para ese archivo local

3. **Datos corruptos en el CSV**
   - Solución: Ver los logs y regenerar el dashboard
   ```bash
   python3 /Users/diodice/BTC/scripts/daily_update.py
   ```

### Problema 2: Error "No module named 'pandas'"

**Síntoma**: El script falla con este mensaje.

**Causa**: pandas/requests no están instalados.

**Solución**:
```bash
pip3 install pandas requests
```

Si sigue fallando:
```bash
python3 -m pip install pandas requests
```

### Problema 3: Error "Failed to get BTC price"

**Síntoma**: El script no puede obtener el precio de Bitcoin.

**Causas posibles**:

1. **Sin conexión a internet**
   - Solución: Verificá tu conexión WiFi

2. **API de CoinGecko caída** (raro)
   - Solución: El script reintenta 3 veces. Esperá 10 minutos y probá de nuevo

3. **Firewall bloqueando la conexión**
   - Solución: Verificá configuración de firewall en Preferencias del Sistema

**Verificar conectividad manualmente**:
```bash
curl "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
```

Deberías ver:
```json
{"bitcoin":{"usd":69784}}
```

### Problema 4: La automatización no se ejecuta

**Síntoma**: Llegan las 9 AM y el script no se ejecuta.

**Diagnóstico paso a paso**:

1. **Verificar que el servicio está cargado**:
   ```bash
   launchctl list | grep btc-dca
   ```

   - Si no aparece nada: el servicio no está cargado
   - Solución: `launchctl load ~/Library/LaunchAgents/com.dario.btc-dca-tracker.plist`

2. **Ver detalles del servicio**:
   ```bash
   launchctl print user/$(id -u)/com.dario.btc-dca-tracker
   ```

   Buscá la línea `next scheduled run` para ver cuándo se ejecutará.

3. **Revisar logs**:
   ```bash
   tail -50 /Users/diodice/BTC/logs/stderr.log
   ```

4. **Probar ejecución manual**:
   ```bash
   launchctl start com.dario.btc-dca-tracker
   ```

   Si esto funciona pero la automatización no, puede ser un problema de permisos.

### Problema 5: "Ya existe un registro para hoy"

**Síntoma**: El script se ejecuta pero dice que ya hay un registro.

**Causa**: Ya se ejecutó hoy (esto es intencional para evitar duplicados).

**Solución**: Esto no es un error, es el comportamiento esperado. Si querés forzar una nueva ejecución:

1. Abrí el CSV
2. Borrá la última línea (el registro de hoy)
3. Guardá el archivo
4. Ejecutá el script de nuevo

**CUIDADO**: Solo hacé esto si sabés lo que estás haciendo.

### Problema 6: Registro corrupto o duplicado

**Síntoma**: Hay datos extraños o duplicados en el CSV.

**Solución**:

1. **Hacer backup primero**:
   ```bash
   cp /Users/diodice/BTC/data/btc_purchases.csv ~/Desktop/btc_backup.csv
   ```

2. **Abrir el CSV y corregir manualmente**:
   ```bash
   open /Users/diodice/BTC/data/btc_purchases.csv
   ```

3. **Regenerar el dashboard**:
   ```bash
   python3 /Users/diodice/BTC/scripts/daily_update.py
   ```

### Problema 7: Los logs están muy grandes

**Síntoma**: La carpeta `logs/` ocupa mucho espacio.

**Solución - Limpiar logs antiguos**:
```bash
# Ver tamaño de logs
du -sh /Users/diodice/BTC/logs/

# Borrar logs de más de 30 días
find /Users/diodice/BTC/logs/ -name "*.log" -mtime +30 -delete
```

### Verificación de Salud del Sistema

**Script de diagnóstico completo**:

```bash
#!/bin/bash
echo "=== Diagnóstico BTC DCA Tracker ==="
echo ""

echo "1. ¿Existe la carpeta BTC?"
ls -ld /Users/diodice/BTC && echo "✅ Sí" || echo "❌ No"
echo ""

echo "2. ¿Existe el CSV de datos?"
ls -lh /Users/diodice/BTC/data/btc_purchases.csv && echo "✅ Sí" || echo "❌ No"
echo ""

echo "3. ¿Cuántos registros hay?"
wc -l /Users/diodice/BTC/data/btc_purchases.csv
echo ""

echo "4. ¿Está activa la automatización?"
launchctl list | grep btc-dca && echo "✅ Sí" || echo "❌ No"
echo ""

echo "5. ¿Están instaladas las dependencias?"
python3 -c "import pandas; import requests" && echo "✅ Sí" || echo "❌ No"
echo ""

echo "6. ¿Funciona la API de CoinGecko?"
curl -s "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd" && echo "" && echo "✅ Sí" || echo "❌ No"
echo ""

echo "7. Último log:"
tail -3 /Users/diodice/BTC/logs/btc_tracker_*.log 2>/dev/null || echo "No hay logs aún"
```

Guardá esto en un archivo `diagnose.sh` y ejecutalo:
```bash
chmod +x diagnose.sh
./diagnose.sh
```

---

## ❓ Preguntas Frecuentes

### ¿Puedo cambiar el monto de $2 USD a otra cantidad?

Sí, pero tenés que editar el script:

1. Abrí el script:
   ```bash
   nano /Users/diodice/BTC/scripts/daily_update.py
   ```

2. Buscá la línea (aprox. línea 60):
   ```python
   usd_invertidos = 2.00
   ```

3. Cambiala por el monto que quieras:
   ```python
   usd_invertidos = 5.00  # Por ejemplo, $5 USD
   ```

4. Guardá (Ctrl+O, Enter, Ctrl+X)

5. La próxima ejecución usará el nuevo monto

### ¿Puedo ejecutarlo más de una vez por día?

Técnicamente sí, pero no tiene sentido para un DCA diario. El script detecta si ya hay un registro para hoy y no duplicará.

Si querés cambiar a **cada 12 horas** o **cada semana**:

1. Editar el plist y cambiar `StartCalendarInterval`
2. Ajustar la lógica de detección de duplicados en el script

### ¿Cómo reseteo todo y empiezo de cero?

```bash
# Backup primero (por las dudas)
cp -r /Users/diodice/BTC ~/Desktop/BTC_backup

# Borrar datos
rm /Users/diodice/BTC/data/btc_purchases.csv

# Ejecutar de nuevo
python3 /Users/diodice/BTC/scripts/daily_update.py
```

Esto creará un CSV nuevo empezando desde hoy.

### ¿Puedo comparar con otras criptos (ETH, etc.)?

El sistema actual solo soporta Bitcoin, pero se puede extender:

1. Modificar el script para consultar otros IDs en CoinGecko
2. Crear CSV separados para cada cripto
3. Generar dashboards individuales

(Esto requiere programación adicional)

### ¿Los datos son privados?

**Sí, 100% privados**:
- ✅ Todo se guarda localmente en tu Mac
- ✅ No se envía información a ningún servidor (excepto consultar el precio público de BTC)
- ✅ CoinGecko no recibe información sobre vos ni tu inversión
- ✅ No hay tracking, analytics, ni telemetría

### ¿Puedo usar esto en Windows o Linux?

El script de Python funciona igual, pero:
- **Windows**: Usar Task Scheduler en vez de launchd
- **Linux**: Usar cron en vez de launchd

La lógica del script es la misma, solo cambia la automatización.

### ¿Qué pasa si mi Mac está apagada a las 9 AM?

launchd ejecutará el script la próxima vez que enciendas tu Mac **si configurás**:

```xml
<key>RunAtLoad</key>
<true/>
```

en el archivo plist. Por defecto está en `false`.

### ¿Puedo importar estos datos a una planilla de Google Sheets?

Sí:

1. Abrí Google Sheets
2. Archivo → Importar
3. Subí el archivo `btc_purchases.csv`
4. Configurá: delimitador por comas, primera fila como encabezado

Ahora podés hacer tus propios gráficos y análisis en Sheets.

### ¿El precio es en tiempo real?

El precio se obtiene en el momento de ejecución (9 AM cada día). No es un precio promedio del día, sino el precio en ese momento específico.

Si querés el precio de cierre del día (a las 00:00 UTC), tendrías que:
1. Cambiar el horario de ejecución a medianoche UTC
2. O usar un endpoint diferente de CoinGecko

---

## 🔐 Seguridad y Privacidad

### ¿Qué datos se recopilan?

**Datos que SÍ se guardan** (localmente):
- Fechas de ejecución
- Precios de Bitcoin consultados
- Cálculos de compras simuladas

**Datos que NO se guardan**:
- Información personal
- Dirección IP
- Actividad de navegación
- Cualquier dato sensible

### ¿Se comparte información con terceros?

**NO**. Las únicas conexiones externas son:

1. **CoinGecko API** (para obtener precio de BTC)
   - Datos enviados: ninguno (es una consulta GET pública)
   - Datos recibidos: precio actual de Bitcoin en USD
   - No requiere autenticación ni tracking

2. **CDN de Chart.js** (solo cuando abres el dashboard)
   - Tu navegador descarga la librería Chart.js
   - Esto es estándar para cualquier sitio web
   - No envía datos personales

### ¿Es seguro ejecutar este código?

**Sí**, porque:
- ✅ Todo el código es visible y editable (no hay ofuscación)
- ✅ No requiere permisos de administrador
- ✅ No modifica archivos del sistema
- ✅ Solo lee/escribe en `/Users/diodice/BTC/`
- ✅ No se conecta a servidores desconocidos

Podés revisar todo el código:
```bash
cat /Users/diodice/BTC/scripts/daily_update.py
```

### Protección contra Pérdida de Datos

**Riesgos**:
- Si se borra accidentalmente el CSV, perdés el historial

**Mitigación**:
- Hacer backups periódicos (ver sección "Backup de Datos")
- Opción: versionar con Git

**Setup de Git (opcional)**:
```bash
cd /Users/diodice/BTC
git init
git add .
git commit -m "Initial commit"

# Después de cada actualización automática
git add data/btc_purchases.csv
git commit -m "Update $(date +%Y-%m-%d)"
```

### ¿Qué pasa si CoinGecko cierra o cambia su API?

**Plan de contingencia**:

1. El script dejaría de funcionar (no obtendría precios)
2. Tus datos históricos quedarían intactos
3. Solución:
   - Cambiar a otra API (ej: CoinMarketCap, Binance)
   - Modificar la función `get_btc_price()` en el script

**APIs alternativas**:
- Kraken: `https://api.kraken.com/0/public/Ticker?pair=XBTUSD`
- Binance: `https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT`
- CoinMarketCap: (requiere API key gratuita)

---

## 📞 Soporte y Ayuda

### Recursos

1. **Este README**: Revisá las secciones de Troubleshooting y FAQ
2. **Logs del sistema**: `/Users/diodice/BTC/logs/`
3. **Script de diagnóstico**: Ver sección "Verificación de Salud del Sistema"

### Antes de Pedir Ayuda

Ejecutá este comando y guardá la salida:

```bash
{
  echo "=== Info del Sistema ==="
  sw_vers
  echo ""
  python3 --version
  echo ""
  echo "=== Estado del Servicio ==="
  launchctl list | grep btc-dca
  echo ""
  echo "=== Últimos Logs ==="
  tail -20 /Users/diodice/BTC/logs/btc_tracker_*.log 2>/dev/null
  echo ""
  echo "=== Datos ==="
  wc -l /Users/diodice/BTC/data/btc_purchases.csv
  tail -3 /Users/diodice/BTC/data/btc_purchases.csv
} > ~/Desktop/btc_debug_info.txt

cat ~/Desktop/btc_debug_info.txt
```

Esto genera un archivo con toda la info de diagnóstico.

---

## 📅 Información del Proyecto

- **Fecha de inicio**: 14 de febrero de 2026
- **Versión**: 1.0
- **Lenguaje**: Python 3.9+
- **Plataforma**: macOS (Darwin)
- **Licencia**: Uso personal educativo

---

## 🎓 Aprendizajes Esperados

Después de usar este tracker por unos meses, deberías poder:

1. ✅ Entender qué es el DCA y por qué funciona
2. ✅ Ver cómo la volatilidad del Bitcoin afecta tu inversión
3. ✅ Comprender que las bajas de precio son **oportunidades** de acumular más
4. ✅ Desarrollar disciplina de inversión sistemática
5. ✅ Interpretar gráficos de inversiones
6. ✅ Familiarizarte con conceptos de criptomonedas (satoshis, exchanges, etc.)

---

## ⚠️ Disclaimer

**IMPORTANTE - Leer antes de usar**:

1. **Esto es una SIMULACIÓN educativa**
   - No se compra Bitcoin real
   - No hay transacciones reales
   - Es solo para aprender

2. **No es asesoramiento financiero**
   - No te estoy recomendando invertir en Bitcoin
   - Hacé tu propia investigación (DYOR - Do Your Own Research)
   - Consultá con un asesor financiero antes de invertir dinero real

3. **Inversiones reales conllevan riesgos**
   - Podés perder todo tu dinero
   - La volatilidad de Bitcoin es extrema
   - Solo invertí lo que estés dispuesto a perder

4. **Uso bajo tu propia responsabilidad**
   - Este software se provee "as is" sin garantías
   - No me hago responsable de decisiones financieras basadas en esta simulación

---

## 🚀 Próximos Pasos Sugeridos

### Semana 1-2:
- Familiarizarte con el dashboard
- Ver cómo se actualiza cada día
- Observar la primera volatilidad

### Mes 1:
- Analizar los datos en Excel/Numbers
- Calcular tu precio promedio de compra
- Comparar días de alta vs baja

### Mes 3:
- Evaluar el rendimiento a más largo plazo
- Decidir si querés aumentar/disminuir el monto diario
- Considerar agregar otras cryptos (requiere modificaciones)

### Largo Plazo:
- Después de 6-12 meses, tendrás datos suficientes para ver patrones reales
- Comparar con estrategias de inversión única
- Usar el aprendizaje para decisiones reales (si decidís invertir)

---

## 📖 Recursos Adicionales

### Aprender más sobre Bitcoin:
- https://bitcoin.org/es/
- "Mastering Bitcoin" por Andreas Antonopoulos (libro gratuito)

### Aprender más sobre DCA:
- Investopedia: Dollar-Cost Averaging
- Artículos sobre backtesting de DCA en Bitcoin

### Aprender más sobre Python:
- https://docs.python.org/3/tutorial/
- Curso de pandas para análisis de datos

---

**¡Feliz tracking! 📊₿**

*Última actualización: 14 de febrero de 2026*
