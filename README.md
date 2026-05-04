# 🚀 ManttoAI — Plataforma de Monitoreo IoT por Rubro

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB.svg?logo=react&logoColor=black)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg?logo=docker&logoColor=white)
![Machine Learning](https://img.shields.io/badge/ML-Scikit_Learn-F7931E.svg)

**ManttoAI** es una plataforma open-source de monitoreo IoT por rubro (industrial, agrícola, comercial). Captura telemetría en tiempo real desde dispositivos IoT (ESP32) vía MQTT, evalúa umbrales operacionales y ejecuta un modelo de Machine Learning (Random Forest) para predecir fallas en los equipos antes de que ocurran.

---

## ✨ Características Principales

- **📡 Telemetría IoT en Tiempo Real:** Integración nativa con MQTT (Mosquitto) para capturar temperatura, humedad y vibración.
- **🧠 Predicciones con Machine Learning:** Modelo Random Forest integrado (94.1% F1-Score) para evaluar riesgo de falla.
- **🚨 Alertas Inteligentes:** Evaluación automática de umbrales operacionales con notificaciones por email.
- **📊 Dashboard Interactivo:** SPA en React con auto-refresh, tendencias históricas y gestión de equipos.
- **🛠️ Simulador IoT Integrado:** ¿No tenés hardware? Incluye un simulador por software 24/7 que genera datos realistas de sensores.
- **🤖 Asistente de Mantenimiento:** Chat híbrido (reglas + IA con Ollama) para consultas técnicas del operador.

## 🏗️ Stack Tecnológico

- **Backend:** FastAPI, SQLAlchemy, Pydantic, MySQL 8
- **Frontend:** React 18, Vite, Tailwind CSS
- **IoT y Mensajería:** ESP32 (Firmware), Eclipse Mosquitto (MQTT)
- **Machine Learning:** Scikit-learn, Pandas, Numpy
- **Infraestructura:** Docker, Docker Compose, Nginx (compatible con Dokploy)

---

## 🚀 Inicio Rápido (Desarrollo Local)

Podés ejecutar toda la plataforma localmente usando Docker Compose. No requiere dependencias externas.

### Requisitos Previos
- Docker y Docker Compose V2
- GNU Make

### 1. Levantar la plataforma
```bash
# Generar archivos .env locales y credenciales MQTT
make setup-env

# Levantar todo el stack (Backend, Frontend, MySQL, Mosquitto)
make up
```

### 2. Cargar datos y simular
```bash
# Crear usuario admin, equipos de ejemplo y umbrales
make seed

# Iniciar la simulación de telemetría MQTT realista
make simulate
```

### 3. Acceder al Dashboard
- **Frontend:** `http://localhost:5173` (o puerto 80 si está desplegado completo)
- **Documentación API (Swagger):** `http://localhost:8000/docs`
- **Login por defecto:** `admin@manttoai.local` (Contraseña generada en `backend/.env` tras ejecutar `make setup-env`)

---

## 📂 Estructura del Repositorio

```text
├── backend/       # Aplicación FastAPI, modelos ML y lógica de negocio
├── frontend/      # Dashboard SPA en React 18
├── iot/           # Firmware C++ para ESP32 y scripts de simulación MQTT
├── mosquitto/     # Configuración del broker MQTT y autenticación
├── scripts/       # Utilidades operacionales y de despliegue
└── docs/          # Documentación de arquitectura y académica
```

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Si querés colaborar:
1. Revisá la pestaña [Issues](https://github.com/sebitabravo/ManttoAI/issues) para tareas abiertas.
2. Hacé un fork del repositorio y creá una rama feature (`feature/amazing-idea`).
3. Asegurate de que tu código pase todos los checks (`make lint` y `make test`).
4. Abrí un Pull Request.

---

## 🎓 Contexto Académico (PMBOK)

*Este proyecto se originó como Proyecto de Título (Gestión de Proyectos Informáticos) en INACAP. Incluye el plan de negocios de ManttoAI como empresa real (Evaluación 3 — Gestión de Costos).*

Si sos evaluador académico o buscás los artefactos formales de gestión del proyecto bajo PMBOK (Acta de Constitución, EDT, RACI, Matriz de Riesgos, Gestión de Costos, etc.), consultá el índice dedicado:

👉 **[Ver Documentación PMBOK / Evaluación Académica](docs/gestion-proyecto/INDEX.md)**

---
*Mantenido por el equipo ManttoAI. Código abierto para la comunidad.*
