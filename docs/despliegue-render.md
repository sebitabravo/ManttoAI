# Despliegue de demo: Render + Vercel

> **Estado:** configuración preparada y validable localmente. No implica que
> exista un servicio público desplegado ni que las credenciales externas estén
> configuradas.

## Arquitectura elegida

```text
Navegador -> Vercel (React SPA + /api/* rewrite)
                    |
                    v
             Render Web Service (FastAPI + Docker)
                    |
                    v
                 Aiven MySQL
```

- `render.yaml` define el backend como Web Service Docker en Render.
- `backend/Dockerfile.render` usa el repositorio como contexto, incluye el
  seed operativo y genera el artefacto Random Forest durante el build. El
  `modelo.joblib` y su checksum no se versionan. Como Render Free no admite
  `preDeployCommand`, el `CMD` ejecuta `/app/seed_db.py` de forma idempotente
  antes de iniciar Uvicorn. Requiere `SEED_ADMIN_PASSWORD`,
  `SEED_TECNICO_PASSWORD` y `SEED_DEMO_PASSWORD` configuradas como secretos.
  La cuenta `demo@manttoai.local` queda en modo solo lectura para no romper una
  demo compartida. Ver la limitación de [pre-deploy commands de Render](https://render.com/docs/deploys).
- `MQTT_ENABLED=false` evita depender de un broker público; el simulador del
  backend persiste lecturas directamente en MySQL para que la demo siga viva.
- `frontend/vercel.json` reescribe `/api/*` hacia Render. El navegador ve una
  ruta same-origin y las cookies `SameSite=Lax` siguen siendo utilizables.

La sintaxis de `render.yaml` sigue el [Blueprint YAML Reference de Render](https://render.com/docs/blueprint-spec).
La regla `/api/*` usa el mecanismo de [rewrites de Vercel](https://vercel.com/docs/routing/rewrites).

## Límites del free tier que afectan la demo

- **Render Free:** el Web Service se duerme después de 15 minutos sin tráfico,
  puede tardar cerca de un minuto en despertar y consume las horas gratuitas
  mensuales mientras está activo. Render lo orienta a prototipos y previews,
  no a producción; además, el tier Free no puede enviar SMTP por los puertos
  25, 465 o 587. Ver [Deploy for Free](https://render.com/docs/free).
- **Aiven MySQL Free:** ofrece 1 GB de RAM y 1 GB de almacenamiento, un solo
  nodo, sin límite temporal y sin tarjeta según su documentación, pero puede
  apagarse por inactividad. El límite obliga a retener telemetría y no sembrar
  datos sin control. Ver [Aiven MySQL free tier](https://aiven.io/docs/products/mysql/concepts/mysql-free-tier).
- **Vercel Hobby:** es gratuito y adecuado para proyectos personales; la
  vitrina debe mantenerse como portfolio personal/no comercial. Ver [Hobby
  Plan](https://vercel.com/docs/plans/hobby).

## Configuración de Render

1. Crear el servicio desde el Blueprint o importar `render.yaml`.
2. Completar los valores `sync: false` sin pegarlos en el repositorio:
   - `DATABASE_URL`: URL `mysql+pymysql` de Aiven. Si Aiven exige CA, montar el
     certificado como Secret File y referenciar su ruta en la URL.
   - `CORS_ALLOWED_ORIGINS`: origen HTTPS exacto de Vercel, sin wildcard.
   - `SEED_ADMIN_PASSWORD`, `SEED_TECNICO_PASSWORD` y `SEED_DEMO_PASSWORD`:
     contraseñas únicas, largas y no reutilizadas.
3. Mantener `APP_ENV=production`, `MQTT_ENABLED=false`,
   `ML_AUTO_TRAIN_ON_MISSING=false` y `PREDICTION_SCHEDULER_MAX_WORKERS=1`
   para el tier de demo.
   El blueprint deja `SEED_ALLOW_NON_DEV=true` de forma explícita para permitir
   que el arranque del contenedor cree de manera idempotente las cuentas de la demo;
   usá contraseñas únicas configuradas como secretos y no reutilicés esta
   opción para un servicio productivo sin una política de provisioning propia.
   `SIMULATOR_INTERVAL_SECONDS=60` y `TELEMETRY_RETENTION_DAYS=30` limitan el
   crecimiento de telemetría en Aiven; cada ciclo purga lecturas fuera de esa
   ventana. En desarrollo la retención queda deshabilitada por defecto (`0`).
4. `ALLOW_SCHEMA_AUTO_CREATE=true` y `ALLOW_RUNTIME_SCHEMA_CHANGES=true`
   siguen explicitados para el prototipo Render; `Base.metadata.create_all`
   incluye `revoked_tokens`, necesaria para revocar JWT sin Redis. Alembic
   ahora detecta una base completamente vacía, crea el esquema vigente desde
   `Base.metadata`, registra `head` y persiste la revisión; la regresión está
   en `backend/tests/test_alembic_bootstrap.py`. Esto evita el fallo histórico
   `no such table: equipos` de `41d35d73683b`. Una base ya creada con
   `create_all` y sin `alembic_version` solo se estampa si sus tablas y
   columnas coinciden exactamente con el metadata vigente; un esquema parcial
   se rechaza antes de ejecutar migraciones históricas. Igual se requiere
   respaldo e inspección de columnas, datos y constraints antes de retirar
	   los flags runtime en un entorno real.
	   La migración reversible disponible para JWT es
	   `d8e9f0a1b2c3_add_persistent_jwt_revocations.py`.
	   El roundtrip `upgrade head` → `downgrade base` también fue verificado contra
	   MySQL 8.0.41 efímero con `RUN_MYSQL_ALEMBIC_TESTS=1`; esa prueba es
	   destructiva y no debe ejecutarse sobre Aiven ni sobre una base compartida.
5. Verificar que el health check de Render apunte a `/health`; `/ready` además
   debe responder `200` cuando MySQL esté accesible. Render documenta el
   comportamiento de estos checks en [Health Checks](https://render.com/docs/health-checks).

## Configuración de Vercel

1. Crear/importar un proyecto **nuevo de ManttoAI** con root directory
   `frontend/`. No reutilizar un proyecto Vercel genérico enlazado por el nombre
   de la carpeta: el CLI puede seleccionar un proyecto ajeno y sus ajustes
   pueden apuntar a Next.js o a `public/`.
2. `frontend/vercel.json` fija el framework Vite, `npm ci`, `npm run build` y
   la salida `dist`, además del rewrite API/SPA. Esos valores deben mantenerse
   también en el proyecto Vercel si el proveedor los muestra en el dashboard.
3. Mantener `VITE_API_URL` vacío o no definido: el cliente usa `/api/v1`.
4. Revisar `frontend/vercel.json`: el hostname debe coincidir con el servicio
   real de Render. Si el nombre del servicio cambia, actualizar solo ese
   destino y volver a validar el build.
5. Opcionalmente configurar `VITE_DEMO_EMAIL` y `VITE_DEMO_PASSWORD` con la
   misma cuenta `demo@manttoai.local` y contraseña que usa Render. Cuando ambas
   variables existen aparece **Usar cuenta demo** y solo rellena el formulario;
   no hace auto-login. La contraseña queda embebida en el JavaScript público de
   Vercel: usá exclusivamente una cuenta `is_demo` de solo lectura, nunca una
   cuenta admin/técnico, y omití ambas variables si no querés publicar ese
   acceso.
6. Confirmar en el navegador que el login pasa por `/api/v1/auth/login` bajo
   el dominio de Vercel y que la cookie no queda asociada al hostname de Render.

## Verificación antes de anunciar la URL

```bash
# Validación estática local
git diff --check
bash -n scripts/setup_env.sh scripts/demo-defensa.sh

# Backend
cd backend
.venv/bin/python -m compileall -q app
.venv/bin/ruff check app/
.venv/bin/pytest tests/ -q

# Solo contra una base MySQL efímera; no usar una base con datos
RUN_MYSQL_ALEMBIC_TESTS=1 DATABASE_URL='mysql+pymysql://usuario:password@host:3306/base' \
  .venv/bin/pytest tests/test_alembic_bootstrap.py -v

# Frontend
cd ../frontend
npm run lint
npm run test:unit
npm run build
```

La verificación pública es una puerta separada y requiere evidencia real:

```bash
curl --fail https://<render-host>/health
curl --fail https://<render-host>/ready
```

Después, validar desde el dominio Vercel: login, dashboard con lecturas,
alerta, predicción y logout. No considerar el despliegue entregado hasta que
esas respuestas y el flujo de navegador estén comprobados; los tests locales
no prueban DNS, cookies del proveedor ni MySQL remoto.
