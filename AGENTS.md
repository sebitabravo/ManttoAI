# ManttoAI — Plataforma de Monitoreo IoT por Rubro

> Source of truth for AI/project instructions. `CLAUDE.md` should point to this file via symlink.

## Project summary
**ManttoAI** es una plataforma de monitoreo IoT organizada por rubro económico (industrial, agrícola, comercial). Captura telemetría en tiempo real desde dispositivos ESP32 vía MQTT, evalúa umbrales, ejecuta un modelo ML (Random Forest), y expone datos en un dashboard React con alertas.

El repositorio contiene el **prototipo académico** funcional desarrollado para INACAP bajo metodología PMBOK. Adicionalmente, los documentos de gestión de costos presentan el **plan de negocios** para ManttoAI como empresa real, con capital de $3.000.000 CLP (3 socios), costos operacionales mensuales de $187.100 CLP y proyección a 3 años. El prototipo técnico actual es la base sobre la cual se construye dicho plan.

This is **not** a production industrial system. It is a low-cost student prototype for INACAP, aligned with PMBOK and validated in a controlled environment. The business plan in `docs/costos/` projects the path to a real company.

## Team
- Sebastián Bravo: backend, MQTT/IoT integration, CI/CD, deployment, Director de Proyecto
- Luis Loyola: frontend, database, API integration, scope documentation, CEO/Comercial (plan de negocios)
- Ángel Rubilar: architecture, ESP32 hardware, ML model

## Main goals
- Capture near-real-time telemetry from low-cost IoT devices
- Estimate equipment risk/failure with a simple scikit-learn model
- Show status, trends, history, and alerts in a web dashboard
- Keep enough technical traceability for the academic report and final demo

## Hard constraints
- Simplicity over enterprise architecture
- Single VPS with Docker Compose
- Free/open-source tools only
- No Kubernetes, microservices, serverless, AWS IoT, Azure IoT Hub, or real ERP/SCADA integrations
- No deep learning; use scikit-learn only
- Web dashboard only; no mobile app
- ESP32 over Wi-Fi only; no LoRa, 4G, Modbus, or OPC-UA
- Feasible for 3 students with limited time and budget
- Generated code comments should be in Spanish for the academic report

## Preferred stack
- IoT: ESP32 DevKit v1, DHT22, MPU-6050, MQTT over Wi-Fi, Mosquitto
- Backend: Python 3.11+, FastAPI, SQLAlchemy, MySQL 8, Pydantic v2, JWT auth
- ML: pandas, numpy, scikit-learn, joblib; prefer Random Forest for MVP
- Frontend: React 18 + Vite + Tailwind CSS + Axios + React Router + Chart.js
- Infra: Ubuntu 22.04 VPS, Docker Compose, Nginx, Let's Encrypt
- Testing: pytest for backend; frontend testing can be manual unless the repo already includes automation

## Product scope
- **Rubros objetivo:** industrial, agrícola, comercial (monitoreo sectorizado por tipo de equipo y entorno)
- Telemetry: temperature, humidity, vibration (x/y/z), and optionally runtime hours if the implementation needs it
- Core modules: auth, equipment, readings, alerts, predictions, maintenance history, thresholds
- First notification channel: email alerts are enough for MVP
- Expected dashboard: equipment status, active alerts, trends, history

## ML guidance
- MVP model: Random Forest
- Allowed data sources: synthetic data and/or NASA C-MAPSS for reference/bootstrapping
- Minimum acceptable prototype target: >= 80% validation performance
- Stretch goal: >= 85%
- Prefer explainable, reproducible results over fancy models

## Expected data flow
1. ESP32 publishes to `manttoai/equipo/{id}/lecturas`
2. Mosquitto receives the message
3. Backend subscriber stores the reading in MySQL
4. Backend evaluates thresholds and creates alerts
5. Backend runs prediction periodically or after enough readings
6. Frontend displays charts, history, and active alerts

## Working rules for AI agents
- Read related files before editing
- Make small, reversible, easy-to-verify changes
- Do not invent architecture that is not present in the repo
- If something is undefined, choose the simplest viable option and state the assumption
- Prefer practical solutions over “enterprise-ready” complexity
- Keep docs/instructions concise; English is fine for repo guidance, but code comments should stay in Spanish
- Do not add dependencies without a clear reason
- Prefer simple scheduling (APScheduler/cron-style) over Celery/Redis unless there is a proven need
- Keep `.env`, secrets, credentials, and model artifacts out of git unless explicitly required
- Treat auth, DB migrations, deployment config, MQTT credentials, and external integrations as sensitive areas

## Coding conventions

### Backend
- black + isort + ruff
- snake_case for functions/variables, PascalCase for classes
- routers for HTTP, services for business logic
- Public functions should have concise docstrings

### Frontend
- Functional components with hooks
- PascalCase for components, camelCase for functions/variables
- Tailwind-first styling; avoid custom CSS unless justified

### Git
- Branches: `main`, `develop`, `feature/*`, `fix/*`
- Conventional Commits, e.g. `feat(api): add prediction endpoint`
- `.env` must stay ignored

## Useful commands
- Backend dev: `uvicorn app.main:app --reload --port 8000`
- Frontend dev: `npm run dev`
- Full stack: `docker compose up --build -d`
- Backend tests: `pytest tests/ -v --cov=app`
- MQTT test publish: `mosquitto_pub -h localhost -t "manttoai/equipo/1/lecturas" -m '{"temperatura":45.2,"humedad":60,"vib_x":0.3,"vib_y":0.1,"vib_z":9.8}'`
- MQTT test subscribe: `mosquitto_sub -h localhost -t "manttoai/#" -v`

## Business plan context (Evaluación 3 — Gestión de Costos)
- **Producto:** ManttoAI — Plataforma de Monitoreo IoT por Rubro
- **Rubros:** industrial, agrícola, comercial (2 kits ESP32 por rubro)
- **Capital inicial:** $3.000.000 CLP (3 socios fundadores, $1.000.000 c/u)
- **Costos operacionales:** $187.100 CLP/mes (infraestructura DO, contador, abogado, domicilio virtual)
- **Infraestructura proyectada:** Digital Ocean (Droplet 2GB + PostgreSQL gestionada + Spaces 250GB, São Paulo)
- **Proveedores:** contadoresenlinea.cl, OficinVirtual.cl, NIC Chile
- **Autonomía financiera:** ~16 meses sin ingresos
- **Proyección:** Año 1 Validación → Año 2 Crecimiento → Año 3 Consolidación
- **Control:** EVM mensual con CPI ≥ 0,95; Luis Loyola como CEO/Comercial a cargo
- **Precio suscripción:** $88.000 CLP/mes por rubro
- Ver `docs/costos/12-plan-gestion-costos.md` para el detalle completo.

> El stack técnico del prototipo (MySQL 8, single VPS Docker Compose) difiere del stack proyectado en el plan de negocios (PostgreSQL gestionada, Digital Ocean). El plan de negocios representa la evolución esperada; el prototipo actual es la base funcional.

## Academic context
- Institution: INACAP
- Course: Gestión de Proyectos Informáticos
- Methodology: PMBOK 6ta Edición
- Deliverables: functional prototype, public repository, demo video, formal report, final presentation, Evaluación 3 (Gestión de Costos)
- This project must remain realistic for a student team and a low budget

## Before closing a task
- Explain what changed
- Explain risks and trade-offs
- Verify related areas were not obviously broken
- List next steps if something is still pending
