# 06. Enunciado del Alcance

## Descripción del Producto
ManttoAI — Plataforma de Monitoreo IoT por Rubro: plataforma web para la monitorización de telemetría IoT organizada por rubro económico (industrial, agrícola, comercial). Evalúa datos de temperatura, humedad y vibración capturados vía MQTT para predecir fallas mediante Machine Learning.

## Entregables Incluidos
1. **E1 Módulo IoT:** Firmware ESP32 y simulador backend 24/7.
2. **E2 Pipeline de Datos:** FastAPI, SQLAlchemy y base de datos relacional.
3. **E3 Modelo IA:** Scikit-learn Random Forest (Accuracy ≥ 80%, F1-score ≥ 80%).
4. **E4 Dashboard:** React SPA con Tailwind, visualización de historial y alertas.
5. **E5 Manuales:** README.md, `manual-usuario.md`, `despliegue-dokploy.md`.
6. **E6 QA:** Reporte de pruebas Pytest y Playwright.

## Exclusiones Explícitas (Fuera de Alcance)
- ❌ Integraciones ERP o SCADA corporativos.
- ❌ Protocolos industriales como Modbus o LoRa.
- ❌ Aplicación móvil nativa (Android/iOS).
- ❌ Arquitecturas complejas (Kubernetes, Serverless).
- ❌ Deep Learning (Neural Networks).
