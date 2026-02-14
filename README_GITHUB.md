# 📊 Bitcoin DCA Tracker

Sistema automático para simular y visualizar la estrategia de **Dollar Cost Averaging (DCA)** en Bitcoin.

[![Live Demo](https://img.shields.io/badge/Live-Demo-blue)](https://tu-usuario.github.io/btc-dca-tracker)

![Dashboard Preview](https://img.shields.io/badge/Dashboard-Modern-purple)
![Python](https://img.shields.io/badge/Python-3.9+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 🎯 ¿Qué hace?

Simula la compra diaria de **$2 USD en Bitcoin** y muestra:
- ✅ Evolución de tu inversión vs valor del BTC
- ✅ Precio promedio de compra
- ✅ Gráficos interactivos con Chart.js
- ✅ Estadísticas (mejor/peor día de compra)
- ✅ Modo oscuro/claro

## 🚀 Demo en Vivo

👉 **[Ver Dashboard en Vivo](https://tu-usuario.github.io/btc-dca-tracker)**

## 📸 Preview

El dashboard muestra:
- 5 métricas principales (inversión, BTC acumulado, valor actual, ganancia/pérdida, precio promedio)
- 2 gráficos interactivos (evolución DCA + precio BTC)
- Estadísticas detalladas
- Modo oscuro por defecto

## 🛠 Instalación Local

### Requisitos
- Python 3.9+
- pandas
- requests

### Setup

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/btc-dca-tracker.git
cd btc-dca-tracker

# 2. Instalar dependencias
pip3 install pandas requests

# 3. Ejecutar primera vez
python3 scripts/daily_update.py

# 4. Abrir el dashboard
open dashboard.html
```

## ⚙️ Automatización (macOS)

Para que se actualice automáticamente cada día a las 9 AM:

```bash
# Copiar el plist a LaunchAgents
cp ~/Library/LaunchAgents/com.dario.btc-dca-tracker.plist ~/Library/LaunchAgents/

# Activar
launchctl load ~/Library/LaunchAgents/com.dario.btc-dca-tracker.plist
```

## 📁 Estructura del Proyecto

```
BTC/
├── index.html              # Dashboard (GitHub Pages)
├── dashboard.html          # Dashboard (local)
├── data/
│   ├── btc_purchases.csv   # Tus datos (NO en Git)
│   └── btc_purchases.example.csv
├── scripts/
│   └── daily_update.py     # Script principal
├── logs/                   # Logs (NO en Git)
└── README.md
```

## 🎨 Features

### Visualización
- **Glassmorphism**: Tarjetas con efecto de vidrio esmerilado
- **Gradientes animados**: Background dinámico
- **Chart.js**: Gráficos interactivos y responsive
- **Google Fonts**: Tipografía Inter

### Métricas
1. **Total Invertido**: Días × $2 USD
2. **BTC Acumulado**: Total de BTC comprado
3. **Valor Actual**: BTC × Precio actual
4. **Ganancia/Pérdida**: Diferencia vs invertido
5. **Precio Promedio**: Tu precio promedio de compra

### Estadísticas
- 🏆 Mejor día de compra (precio BTC más bajo)
- 📉 Peor día de compra (precio BTC más alto)
- 🔥 Racha de días consecutivos

## 🌐 GitHub Pages

Este proyecto está configurado para usar GitHub Pages:
- El archivo `index.html` se sirve automáticamente
- Actualiza tu dashboard localmente y haz push
- GitHub Pages se actualiza automáticamente

## 🔐 Privacidad

- ✅ Datos almacenados localmente
- ✅ No se sube tu CSV personal a GitHub (`.gitignore`)
- ✅ API de CoinGecko pública (sin autenticación)
- ✅ Sin tracking ni analytics

## 📚 Documentación Completa

Para documentación detallada, ver [README.md](README.md) completo.

## 🤝 Contribuciones

Las contribuciones son bienvenidas! Si tenés ideas para mejorar el proyecto:
1. Fork el proyecto
2. Crea tu feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la branch (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto es de uso personal y educativo. No constituye asesoramiento financiero.

## 🙏 Agradecimientos

- [CoinGecko API](https://www.coingecko.com/en/api) - Precios de Bitcoin
- [Chart.js](https://www.chartjs.org/) - Gráficos interactivos
- [Google Fonts (Inter)](https://fonts.google.com/specimen/Inter) - Tipografía

---

**⚠️ Disclaimer**: Esto es una simulación educativa. No se compra Bitcoin real. No es asesoramiento financiero.

