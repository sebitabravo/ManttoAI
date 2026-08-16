# Despliegue de demo: Render + Neon + Vercel

> **Estado:** desplegado y verificado el 16-08-2026. La API pública es
> `https://manttoai-api.onrender.com` y la SPA pública es
> `https://manttoai.vercel.app`. El proyecto Railway histórico dejó de usarse y
> su eliminación quedó programada para `2026-08-18T22:05:05.978Z`.

## Arquitectura pública

```text
Navegador -> Vercel (React SPA + /api/* rewrite)
                    |
                    v
             Render Free Web Service (FastAPI + Docker)
                    |
                    v
             Neon Free PostgreSQL
```

- **Vercel** sirve la SPA desde `frontend/` y mantiene el tráfico API bajo el
  mismo origen mediante `frontend/vercel.json`.
- **Render** ejecuta `manttoai-api` en Oregon, plan Free, rama `main`, con
  `backend/` como root directory y `backend/Dockerfile` como imagen.
- **Neon** mantiene la base PostgreSQL persistente para la demo. El proyecto
  contiene el esquema y datos de vitrina; la connection string nunca se guarda
  en el repositorio.
- **MQTT** está deshabilitado en producción. `SIMULATOR_ENABLED=true` persiste
  telemetría de demo directamente en la base para que el dashboard no dependa
  de hardware ni de un broker público.

El archivo `render.yaml` conserva un Blueprint reproducible alternativo. Ese
Blueprint usa `backend/Dockerfile.render`, que ejecuta el seed idempotente
durante el arranque y requiere los secretos `SEED_*_PASSWORD`. El archivo
`Dockerfile` de la raíz permite crear el mismo servicio desde Render CLI sin
importar el Blueprint. El servicio actual fue creado con Render CLI usando
`backend/Dockerfile`; la base Neon ya estaba poblada y el smoke confirmó 6
equipos, alertas y mantenciones.

## Límites aceptados del free tier

- **Render Free:** el Web Service puede dormir tras un periodo sin tráfico; el
  primer request puede tardar mientras despierta. Esto es aceptable para una
  demo de portfolio, no para producción industrial.
- **Neon Free:** la base puede escalar a cero y tiene límites de almacenamiento
  y cómputo mensuales. La retención de telemetría está limitada a 30 días y el
  simulador usa un intervalo de 60 segundos.
- **Vercel Hobby:** se usa para una vitrina personal; las variables `VITE_*`
  quedan visibles en el bundle. Por eso el botón de demo sólo usa una cuenta
  `visualizador` de solo lectura.

## Variables de Render

Configurar en el dashboard o con la CLI, sin imprimir valores secretos:

```text
APP_ENV=production
PORT=8000
DATABASE_URL=postgresql://...        # Neon; no commitear
DATABASE_AUTO_INIT=true
ALLOW_SCHEMA_AUTO_CREATE=true
ALLOW_RUNTIME_SCHEMA_CHANGES=true
SECRET_KEY=<valor aleatorio largo>
CORS_ALLOWED_ORIGINS=https://manttoai.vercel.app
MQTT_ENABLED=false
SIMULATOR_ENABLED=true
SIMULATOR_INTERVAL_SECONDS=60
TELEMETRY_RETENTION_DAYS=30
ENABLE_PREDICTION_SCHEDULER=true
PREDICTION_INTERVAL_SECONDS=120
PREDICTION_SCHEDULER_MAX_WORKERS=1
ML_AUTO_TRAIN_ON_MISSING=false
```

Si se importa el Blueprint en vez de usar el servicio actual, completar
también `SEED_ADMIN_PASSWORD`, `SEED_TECNICO_PASSWORD` y
`SEED_DEMO_PASSWORD` con contraseñas únicas. Nunca reutilizar esas contraseñas
en una cuenta personal ni publicarlas en README.

## Variables de Vercel

El proyecto debe estar linkeado con root directory `frontend/` y usar estas
variables de **Production**:

```text
VITE_API_URL=/api/v1
VITE_API_TIMEOUT_MS=60000
VITE_DEMO_EMAIL=demo@manttoai.local
VITE_DEMO_PASSWORD=<contraseña de la cuenta visualizador; pública por diseño>
```

`frontend/vercel.json` debe apuntar al host Render actual:

```json
"destination": "https://manttoai-api.onrender.com/api/:path*"
```

No se debe configurar `VITE_API_URL` con el hostname Railway: eso evita el
rewrite same-origin y puede romper cookies y CORS.

## Flujo reproducible de configuración

```bash
# CLIs instaladas localmente
brew install render neonctl

# Autenticación interactiva (abre el navegador)
render login
neon auth

# Validar el Blueprint sin aplicar infraestructura
render blueprints validate render.yaml --workspace <workspace-id>

# Revisar servicios antes de modificar o borrar algo
render services -o json
render postgres list -o json
```

El servicio actual se puede inspeccionar con:

```bash
render services -o json
render deploys list srv-da12q73l550s73en0tv0 -o json
```

No usar `render services delete` mientras Railway no haya sido reemplazado y
el smoke público no esté registrado.

## Verificación antes de anunciar la URL

### API pública

```bash
curl --fail https://manttoai-api.onrender.com/health
curl --fail https://manttoai-api.onrender.com/ready
```

Ambas rutas deben responder `200`. Después validar con la cuenta demo:

1. `POST /api/v1/auth/login` devuelve `200`.
2. `/api/v1/auth/me`, `/equipos`, `/alertas`, `/dashboard/resumen` y
   `/mantenciones` devuelven `200` y datos no vacíos.
3. La cuenta devuelve `rol=visualizador` e `is_demo=true`.

### SPA pública

```bash
cd frontend
npm run lint
npm run test:unit
npm run build
vercel --prod --yes
```

Desde `https://manttoai.vercel.app` comprobar en un navegador real:

1. **Usar cuenta demo** completa el formulario.
2. El login redirige al dashboard.
3. Equipos, alertas, tendencias y mantenciones muestran datos.
4. La cuenta demo no intenta abrir onboarding ni crear equipos.
5. Logout devuelve a `/login` y una nueva sesión funciona.

El estado de despliegue no se considera entregado si sólo pasan los tests
locales: también se necesitan `/health`, `/ready`, login y smoke de navegador
contra los dominios públicos.

## Cutover y retiro de Railway

1. Render, Neon y Vercel pasaron health, readiness y smoke público antes de
   solicitar el retiro de Railway.
2. El proyecto Railway `manttoai-demo` ya no es parte del tráfico público. La
   CLI aceptó la solicitud de eliminación y muestra el `deletedAt` indicado
   arriba; Railway puede seguir apareciendo en la cuenta hasta que se cumpla la
   fecha programada.
3. La base de vitrina quedó disponible en Neon y el rewrite productivo apunta a
   Render. No restaurar Railway como rollback sin revisar primero si la
   eliminación programada sigue siendo cancelable.
4. Después de `deletedAt`, comprobar una vez más la lista de proyectos Railway
   y conservar Render + Neon como el único runtime público.

## Evidencia local relacionada

```bash
git diff --check
./test.sh
cd frontend && npm run lint && npm run test:unit && npm run build
```

La prueba local no reemplaza la verificación DNS, cookies, cold start y base
remota descrita arriba.
