# ManttoAI Predictivo — Arquitectura de Archivos

> Este documento describe la **estructura objetivo** del proyecto. No implica que todos los archivos existan hoy; sirve como guía para implementar el repo de forma consistente y AI-friendly.

## Principios de diseño

1. **Un archivo = una responsabilidad.** Si el nombre del archivo no explica qué hace, está mal nombrado.
2. **Archivos cortos (< 200 líneas).** La IA trabaja mejor con archivos pequeños y enfocados. Si un archivo crece mucho, hay que dividirlo.
3. **Cada carpeta importante debería tener su README.** El agente lo lee para entender el contexto antes de tocar código.
4. **Cero lógica en `main.py`.** Solo registra routers, middleware y startup hooks. La lógica vive en `services/`.
5. **Los modelos de DB, schemas y routers siguen correspondencia 1:1.** Si existe `models/equipo.py`, debería existir `schemas/equipo.py` y `routers/equipos.py`.

---

## Árbol completo

```text
manttoai/
│
│── AGENTS.md                        # Contexto del proyecto para agentes IA (fuente de verdad)
│── CLAUDE.md                        # Symlink a AGENTS.md
│── README.md                        # Descripción general, cómo levantar el proyecto
│── docker-compose.yml               # Orquestación de servicios
│── .env.example                     # Variables de entorno documentadas (sin secretos)
│── .gitignore                       # Archivos ignorados por Git
│── Makefile                         # Atajos de comandos frecuentes
│── skills-lock.json                 # Lock de skills instaladas a nivel proyecto
│
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   └── work-item.md            # Template liviano para issues del equipo
│   ├── workflows/
│   │   ├── ci.yml                   # Lint + test en PRs y pushes a ramas principales
│   │   ├── docker-check.yml         # Validar Dockerfiles y compose si cambian
│   │   └── frontend-e2e.yml         # Playwright E2E para frontend cuando exista configuración
│   └── PULL_REQUEST_TEMPLATE.md     # Template para que cada PR tenga estructura
│
├── backend/
│   ├── README.md                    # Cómo levantar el backend local, endpoints principales
│   ├── Dockerfile                   # Imagen Docker del backend
│   ├── requirements.txt             # Dependencias Python (pinned versions)
│   ├── requirements-dev.txt         # Dependencias de desarrollo y testing
│   ├── .env.example                 # Variables de entorno del backend
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                  # Entry point FastAPI — solo monta routers y middleware
│   │   ├── config.py                # Carga de variables de entorno con pydantic-settings
│   │   ├── database.py              # Engine SQLAlchemy, SessionLocal, Base declarativa
│   │   ├── dependencies.py          # Dependencias compartidas (get_db, get_current_user)
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── usuario.py
│   │   │   ├── equipo.py
│   │   │   ├── lectura.py
│   │   │   ├── alerta.py
│   │   │   ├── prediccion.py
│   │   │   ├── mantencion.py
│   │   │   └── umbral.py
│   │   │
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── usuario.py
│   │   │   ├── equipo.py
│   │   │   ├── lectura.py
│   │   │   ├── alerta.py
│   │   │   ├── prediccion.py
│   │   │   ├── mantencion.py
│   │   │   └── umbral.py
│   │   │
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── equipos.py
│   │   │   ├── lecturas.py
│   │   │   ├── alertas.py
│   │   │   ├── predicciones.py
│   │   │   ├── mantenciones.py
│   │   │   ├── umbrales.py
│   │   │   └── dashboard.py
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── equipo_service.py
│   │   │   ├── lectura_service.py
│   │   │   ├── alerta_service.py
│   │   │   ├── prediccion_service.py
│   │   │   ├── email_service.py
│   │   │   ├── mqtt_service.py
│   │   │   └── dashboard_service.py
│   │   │
│   │   ├── ml/
│   │   │   ├── README.md
│   │   │   ├── generate_dataset.py
│   │   │   ├── train.py
│   │   │   ├── evaluate.py
│   │   │   ├── predict.py
│   │   │   ├── modelo.joblib        # Debe ir ignorado por Git
│   │   │   └── data/
│   │   │       ├── .gitkeep
│   │   │       └── README.md
│   │   │
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── datetime_utils.py
│   │       └── validators.py
│   │
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py
│       ├── test_auth.py
│       ├── test_equipos.py
│       ├── test_lecturas.py
│       ├── test_alertas.py
│       ├── test_predicciones.py
│       └── test_email.py
│
├── frontend/
│   ├── README.md
│   ├── Dockerfile
│   ├── .env.example
│   ├── package.json
│   ├── package-lock.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── index.html
│   ├── eslint.config.js
│   │
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       │
│       ├── api/
│       │   ├── client.js
│       │   ├── auth.js
│       │   ├── equipos.js
│       │   ├── lecturas.js
│       │   ├── alertas.js
│       │   ├── predicciones.js
│       │   ├── mantenciones.js
│       │   └── dashboard.js
│       │
│       ├── context/
│       │   └── AuthContext.jsx
│       │
│       ├── hooks/
│       │   ├── useAuth.js
│       │   ├── usePolling.js
│       │   └── useFetch.js
│       │
│       ├── pages/
│       │   ├── LoginPage.jsx
│       │   ├── DashboardPage.jsx
│       │   ├── EquiposPage.jsx
│       │   ├── EquipoDetallePage.jsx
│       │   ├── AlertasPage.jsx
│       │   ├── HistorialPage.jsx
│       │   └── NotFoundPage.jsx
│       │
│       ├── components/
│       │   ├── layout/
│       │   │   ├── Layout.jsx
│       │   │   ├── Sidebar.jsx
│       │   │   └── Header.jsx
│       │   │
│       │   ├── dashboard/
│       │   │   ├── ResumenCards.jsx
│       │   │   ├── GraficoTemperatura.jsx
│       │   │   ├── GraficoVibracion.jsx
│       │   │   └── TablaUltimasLecturas.jsx
│       │   │
│       │   ├── equipos/
│       │   │   ├── EquipoCard.jsx
│       │   │   └── EquipoForm.jsx
│       │   │
│       │   ├── alertas/
│       │   │   ├── AlertaItem.jsx
│       │   │   └── AlertaBadge.jsx
│       │   │
│       │   └── ui/
│       │       ├── Button.jsx
│       │       ├── Input.jsx
│       │       ├── LoadingSpinner.jsx
│       │       ├── EmptyState.jsx
│       │       └── Modal.jsx
│       │
│       └── utils/
│           ├── formatDate.js
│           ├── constants.js
│           └── classNames.js
│
├── iot/
│   ├── README.md
│   ├── firmware/
│   │   ├── manttoai_sensor/
│   │   │   ├── manttoai_sensor.ino
│   │   │   ├── config.h
│   │   │   ├── sensors.h
│   │   │   ├── sensors.cpp
│   │   │   ├── mqtt_client.h
│   │   │   └── mqtt_client.cpp
│   │   └── libraries.txt
│   │
│   ├── wiring/
│   │   ├── diagrama_conexion.png
│   │   └── pinout.md
│   │
│   └── simulator/
│       └── mqtt_simulator.py
│
├── mosquitto/
│   ├── mosquitto.conf
│   └── passwd                       # Debe ir ignorado por Git
│
├── nginx/
│   └── default.conf
│
├── scripts/
│   ├── backup_db.sh
│   ├── seed_db.py
│   ├── install_skills.sh
│   └── setup_vps.sh
│
├── docs/
│   ├── arquitectura-manttoai.md
│   ├── api-endpoints.md
│   ├── flujo-trabajo-ia.md
│   ├── modelo-ml.md
│   ├── manual-usuario.md
│   └── decisiones/
│       ├── 001-usar-fastapi.md
│       ├── 002-random-forest.md
│       └── 003-mqtt-sobre-http.md
│
└── data/
    ├── .gitkeep
    └── README.md
```

---

## docker-compose.yml — Servicios

```yaml
services:
  backend:
    build: ./backend
    ports: ["8000:8000"]
    depends_on: [mysql, mosquitto]
    env_file: ./backend/.env
    volumes:
      - ./backend/app:/app/app

  frontend:
    build: ./frontend
    ports: ["5173:80"]
    depends_on: [backend]

  mysql:
    image: mysql:8.0
    ports: ["3306:3306"]
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: manttoai_db
    volumes:
      - mysql_data:/var/lib/mysql

  mosquitto:
    image: eclipse-mosquitto:2
    ports: ["1883:1883"]
    volumes:
      - ./mosquitto/mosquitto.conf:/mosquitto/config/mosquitto.conf

  nginx:
    image: nginx:alpine
    ports: ["80:80", "443:443"]
    volumes:
      - ./nginx/default.conf:/etc/nginx/conf.d/default.conf
    depends_on: [backend, frontend]

volumes:
  mysql_data:
```

---

## Por qué esta estructura es AI-friendly

### 1. Nombres autodescriptivos
La IA no necesita leer el contenido de `email_service.py` para saber qué hace. El nombre ya lo dice. Compará eso con `utils.py` o `helpers.py`, que no dicen nada.

### 2. Archivos cortos y enfocados
Cada archivo idealmente tiene menos de 200 líneas. Cuando la IA lee `alerta_service.py`, el archivo entero cabe en contexto. Si fuera un `services.py` de 1500 líneas, pierde precisión.

### 3. Correspondencia 1:1 entre capas
Si la IA necesita agregar un campo a `equipos`, sabe exactamente qué archivos tocar:

- `models/equipo.py`
- `schemas/equipo.py`
- `routers/equipos.py`
- `tests/test_equipos.py`

### 4. READMEs por carpeta
Cuando la IA entra a `backend/app/ml/`, primero puede leer su README y entender:

- qué modelo se usa
- cómo entrenar
- qué dataset usar
- qué métricas se esperan

### 5. API layer separada en el frontend
En vez de tener llamadas a `axios.get(...)` dispersas, todo vive en `src/api/`. Eso reduce acoplamiento y hace más fácil agregar componentes nuevos sin repetir URLs ni headers.

### 6. Custom hooks reutilizables
`usePolling.js` y `useFetch.js` encapsulan patrones repetitivos. La IA no tiene que reescribir loading, error handling y polling en cada pantalla.

### 7. Componentes por dominio
Agrupar `components/dashboard/`, `components/equipos/` y `components/ui/` facilita que la IA encuentre rápido dónde modificar algo sin revisar todo el frontend.

### 8. IoT con simulador
`iot/simulator/mqtt_simulator.py` permite desarrollar backend y frontend sin depender del ESP32 físico. Eso desacopla al equipo y también simplifica debugging.

### 9. ADRs (Architecture Decision Records)
Los archivos en `docs/decisiones/` explican **por qué** se tomó cada decisión. Eso evita sugerencias fuera de contexto como migrar a Django o usar TensorFlow cuando ya se definió otro camino.

---

## Reglas para mantener la estructura

1. **Nunca crear archivos catch-all.** Nada de `utils.py`, `helpers.py` o `misc.py` para mezclar cosas sin criterio.
2. **Máximo 200 líneas por archivo** como guía práctica. Si crece demasiado, dividir por responsabilidad.
3. **Cada nuevo recurso sigue el patrón:** model → schema → router → service → test.
4. **Frontend: una página por ruta, componentes por dominio.**
5. **Imports explícitos, nunca `*`.**

---

## Notas de ajuste para este repo

- El workflow de deploy **no está incluido** a propósito. Se descartó para evitar fricción operativa temprana.
- El workflow `frontend-e2e.yml` está pensado para activarse recién cuando exista configuración real de Playwright.
- `AGENTS.md` es la fuente de verdad del contexto del proyecto; `CLAUDE.md` solo apunta a ese archivo.
