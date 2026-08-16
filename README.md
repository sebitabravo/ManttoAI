# 🚀 ManttoAI — Plataforma de Monitoreo IoT por Rubro

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB.svg?logo=react&logoColor=black)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg?logo=docker&logoColor=white)
![Machine Learning](https://img.shields.io/badge/ML-Scikit_Learn-F7931E.svg)

**ManttoAI** es un prototipo académico open-source de monitoreo IoT por rubro
(industrial, agrícola, comercial). Captura telemetría desde ESP32 vía MQTT,
evalúa umbrales operacionales y ejecuta un Random Forest para estimar riesgo de
falla. No es un sistema industrial certificado ni reemplaza un SCADA.

---

## ✨ Características Principales

- **📡 Telemetría IoT en Tiempo Real:** Integración nativa con MQTT (Mosquitto) para capturar temperatura, humedad y vibración.
- **🧠 Predicciones con Machine Learning:** Random Forest integrado, con 94.13% de accuracy y 93.04% de F1 en el dataset sintético de validación del MVP.
- **🚨 Alertas Inteligentes:** Evaluación automática de umbrales operacionales con notificaciones por email.
- **📊 Dashboard Interactivo:** SPA en React con auto-refresh, tendencias históricas y gestión de equipos.
- **🛠️ Simulador IoT Integrado:** ¿No tenés hardware? El backend puede generar telemetría y persistirla directamente cuando MQTT no está disponible.
- **🤖 Asistente de Mantenimiento:** Chat híbrido (reglas + IA con Ollama) para consultas técnicas del operador.

## 🏗️ Stack Tecnológico

- **Backend:** FastAPI, SQLAlchemy, Pydantic, MySQL 8
- **Frontend:** React 18, Vite, Tailwind CSS
- **IoT y Mensajería:** ESP32 (Firmware), Eclipse Mosquitto (MQTT)
- **Machine Learning:** Scikit-learn, Pandas, Numpy
- **Infraestructura:** Docker, Docker Compose, Nginx (compatible con Dokploy)
- **Demo pública:** Vercel (SPA) + Render Free (API FastAPI) + Neon Free (PostgreSQL)

---

## 🚀 Inicio Rápido (Desarrollo Local)

Podés ejecutar toda la plataforma localmente usando Docker Compose. La primera
ejecución necesita descargar imágenes y dependencias.

### Requisitos Previos
- Docker y Docker Compose V2
- GNU Make

### 1. Levantar la plataforma
```bash
# Generar archivos .env locales y credenciales aleatorias
make setup-env

# Levantar todo el stack (Backend, Frontend, MySQL, Mosquitto)
make up
```

### 2. Cargar datos y simular
```bash
# Crear usuario admin, equipos de ejemplo y umbrales
make seed

# Publicar una tanda de telemetría MQTT realista
make simulate
```

### 3. Verificar cambios

```bash
# Runner raíz usado también por el gate Codex QA
./test.sh

# Suite completa con cobertura
make test
```

### 4. Acceder al Dashboard
- **Frontend:** `http://localhost:5173` (o puerto 80 si está desplegado completo)
- **Documentación API (Swagger):** `http://localhost:8000/docs`
- **Login local:** `admin@manttoai.local`; la contraseña se genera en
  `backend/.env` (ignorado por Git) al ejecutar `make setup-env`. No hay una
  contraseña publicada en el repositorio.
- **Cuenta demo lectura:** `demo@manttoai.local`; su contraseña se genera en
  `backend/.env` como `SEED_DEMO_PASSWORD` y no puede modificar perfil ni
  contraseña.
- En una vitrina pública, el botón **Usar cuenta demo** aparece solo si Vercel
  configura `VITE_DEMO_EMAIL` y `VITE_DEMO_PASSWORD` con esa cuenta de solo
  lectura. La contraseña queda pública en el bundle, por lo que no se deben
  usar credenciales administrativas.

Para una demo sin broker MQTT, configurá `MQTT_ENABLED=false` y
`SIMULATOR_ENABLED=true` en `backend/.env`; el simulador persiste lecturas
directamente en la base de datos.

## 🌐 Demo pública verificada

- **Aplicación:** [manttoai.vercel.app](https://manttoai.vercel.app)
- **API health:** [health](https://manttoai-api.onrender.com/health)
- **API readiness:** [ready](https://manttoai-api.onrender.com/ready)
- **Acceso demo:** abrí la aplicación y presioná **Usar cuenta demo**. La
  cuenta es de solo lectura y no se publica su contraseña en el repositorio.

La vitrina pública usa Vercel para servir la SPA y el rewrite same-origin de
`/api/*`; Render ejecuta FastAPI en un Web Service Free y Neon mantiene la base
PostgreSQL persistente. El backend mantiene `MQTT_ENABLED=false` y
`SIMULATOR_ENABLED=true`, por lo que el dashboard conserva datos vivos sin
exigir hardware físico ni un broker público.

## Qué demuestra el prototipo

ManttoAI conecta sensores IoT de bajo costo con una API operativa y una SPA
para que un operador pueda pasar de una lectura a una decisión de
mantenimiento:

1. Un ESP32 o el simulador publica temperatura, humedad y vibración.
2. FastAPI valida y persiste la lectura en MySQL.
3. Los umbrales crean alertas y el Random Forest calcula riesgo por equipo.
4. React muestra estado, tendencias, historial, alertas y mantenenciones.

El alcance es deliberadamente académico: no reemplaza un SCADA, no usa
Kubernetes ni microservicios, y el modelo ML es liviano y explicable.

## Arquitectura

```text
ESP32 / simulador ── MQTT ──▶ Mosquitto ──▶ FastAPI
                                             ├─ MySQL
                                             ├─ Alertas + email
                                             └─ Random Forest

React + Vite + Tailwind ── /api/v1 ─────────┘
```

En local todo corre con Docker Compose y MySQL. La vitrina pública separa la
SPA en Vercel, el backend Docker en Render y la base PostgreSQL en Neon; Redis,
Ollama, Mailpit y MQTT quedan fuera del servicio público. El simulador integrado
mantiene la telemetría de demo sin hardware ni broker MQTT externo.

## Evidencia técnica

- **Backend:** el runner raíz (`./test.sh`) recolecta 375 tests, con **372
  passed y 3 skipped**; `make test` reporta **86%** de cobertura. Los skips son
  explícitos: SMTP real, concurrencia MySQL y el roundtrip MySQL de Alembic
  requieren habilitación/servicios locales. Esto no sustituye una integración
  contra providers públicos.
- **Frontend:** 59 tests unitarios, lint/build Vite y 22/22 Playwright en
  Chromium y Firefox.
- **Runtime local:** smoke MQTT/SMTP con lecturas persistidas, alertas,
  predicción y dashboard operativo.
- **Runtime público:** Render API y Neon PostgreSQL online; `/health`, `/ready`,
  login demo, equipos, alertas, dashboard y mantenciones verificados contra la
  URL pública. El smoke de navegador en Vercel se repite después de cada cambio
  de rewrite o variables de producción.
- **Render:** el servicio Free se construye desde `backend/Dockerfile`, arranca
  en `0.0.0.0:8000` y usa Neon como base remota. La imagen `linux/amd64` fue
  construida localmente y la API respondió `200` en `/health` y `/ready`.
- **ML:** 94,13% de accuracy y 93,04% de F1 en la evaluación reproducible del
  dataset sintético; ver [`backend/reports/ml-evaluation-latest.md`](backend/reports/ml-evaluation-latest.md).

Ejecutá la evidencia principal con:

```bash
./test.sh       # runner raíz detectado por el gate QA
make test       # suite backend con cobertura
make lint
make smoke-test # Compose + MQTT + alertas + predicción + SMTP local
```

## Capturas

Las capturas de portfolio viven en una sola ruta canónica:

![Login](screenshots/01-login-page.png)

![Dashboard](screenshots/02-dashboard.png)

![Alertas](screenshots/04-alertas.png)

Más detalle operativo en [`docs/manual-usuario.md`](docs/manual-usuario.md).

## 🚀 Configuración de despliegue

La configuración preparada para portfolio está separada del stack local:

- `backend/Dockerfile.render`: imagen del backend FastAPI para el Blueprint de
  Render, con seed idempotente y artefacto ML generado durante el build.
- `Dockerfile`: variante de contexto raíz para crear el Web Service desde
  Render CLI sin depender de la importación interactiva del Blueprint.
- `frontend/vercel.json`: SPA en Vercel con rewrite same-origin de `/api/*`
  hacia `https://manttoai-api.onrender.com`.
- `render.yaml` y `docs/despliegue-render.md`: configuración reproducible del
  backend Render y la base Neon usada por la demo pública.

Los secretos permanecen configurados en Render y Vercel, fuera del repositorio.
La contraseña de la cuenta demo es pública por diseño a través del bundle
Vite, pero corresponde únicamente a un usuario `visualizador` de solo lectura.

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
