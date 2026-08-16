# Auditoría de despliegue — Backend ManttoAI en Render free tier + Aiven MySQL

Fecha: 2026-08-16
Alcance: solo backend (FastAPI). Frontend en Vercel Hobby ya está decidido, fuera de este análisis.

> **Nota de vigencia:** este informe conserva la medición y el análisis de la
> línea base. Después de la auditoría se endureció el workflow, se preparó el
> `Dockerfile.render` con seed idempotente y se verificó una imagen `linux/amd64`
> con límite cgroup de **512 MiB**: `/health` y `/ready` respondieron `200`,
> con **204,3 MiB** reportados por `docker stats` y `220736 kB` de `VmRSS`.
> Aiven, DNS y Render siguen siendo gates externos pendientes.

## Veredicto: GO-WITH-MITIGATION

El proceso mide **~164-166 MB RSS** en reposo (single worker, tras servir requests), muy por debajo del límite duro de 512 MB de Render free. El plan es viable, pero requiere las mitigaciones descritas en la sección 6 antes de desplegar, porque hay un factor de riesgo real (el scheduler de predicción con thread pool) que no se ve en una medición de reposo.

## 1. Medición de memoria (el número que decide todo)

Build: `docker build -t manttoai-backend-audit backend/` — build limpio, sin errores, 26.6s de instalación de deps.

Run aislado (sin MySQL/Redis/MQTT reales, `DATABASE_URL=sqlite:///./manttoai.db`, `MQTT_ENABLED=false`, `ENABLE_PREDICTION_SCHEDULER=false`):

```
docker stats manttoai-audit-run --no-stream
NAME                 MEM USAGE / LIMIT     MEM %
manttoai-audit-run   164.1MiB / 5.853GiB   2.74%
```

Confirmado con `/proc/1/status` del proceso uvicorn real dentro del container:

```
VmRSS: 165560 kB   (≈ 161.7 MiB)
```

Esto es **después** de dos requests a `/health` (200 OK ambas), o sea que no es memoria de arranque en frío sin uso.

**Detalle importante:** `app/ml/train.py` importa `pandas`, `sklearn` y `joblib` a nivel de módulo, y ese módulo se carga en el arranque de FastAPI porque `main.py` incluye el router de `predicciones` que importa `predict.py` → `train.py`. Es decir, **el costo de pandas+numpy+scikit-learn ya está pagado en el baseline de 164 MB**, no es un salto adicional que aparezca recién al primer request de predicción. Verifiqué esto cargando el modelo (`modelo.joblib`, 6.4 MB, ya embebido en la imagen porque `SKIP_TRAIN=true` no lo borra, solo evita reentrenar en build) desde un proceso Python separado dentro del container: el interprete completo con todas las libs cargadas más el modelo en memoria totaliza ~178 MB, consistente con el baseline medido — no hay un segundo salto grande al usar el modelo.

**Headroom real:** 512 MB − 166 MB ≈ 346 MB libres para picos de request concurrente, buffers de SQLAlchemy connection pool, y el propio runtime de Docker/cgroup overhead. Suficiente para una demo de portafolio con tráfico bajo.

La validación posterior de la imagen destinada a Render se ejecutó con
`docker build --platform linux/amd64 -f backend/Dockerfile.render` y luego con
`docker run --memory=512m --memory-swap=512m`. El seed arrancó sobre SQLite
aislado para no tocar el Compose del demo; por eso esta evidencia valida el
footprint y el arranque de la imagen, no la conexión a Aiven.

**Riesgo no capturado por esta medición:** el `Dockerfile` no pasa `--workers` a uvicorn (default = 1 proceso), lo cual es correcto para 0.1 vCPU — no hay multiplicación de footprint por workers. Pero `PREDICTION_SCHEDULER_MAX_WORKERS` (default `4` en `docker-compose.yml`, no seteado en `config.py` cuyo default real es también `4`) crea un `ThreadPoolExecutor` de 4 hilos que corre RandomForest inference cada `PREDICTION_INTERVAL_SECONDS` (default 30s). Cuatro hilos ejecutando `predict()` de scikit-learn en paralelo sobre 0.1 vCPU no van a explotar memoria (los threads comparten el mismo espacio de proceso, no duplican el modelo), pero sí pueden generar contención de CPU y colas de request lentas en un tier con CPU compartido/throttled. Ver mitigación en sección 6.

## 2. Servicios de `docker-compose.yml` — qué se lleva a Render

| Servicio | Veredicto | Nota |
|---|---|---|
| `backend` | **KEEP** | Es el único servicio que va a Render. |
| `frontend` | **DROP** (de este compose) | Ya resuelto: Vercel Hobby sirve la SPA, fuera de este audit. |
| `mysql` | **REPLACE** → Aiven MySQL externo | No se despliega contenedor; `DATABASE_URL` apunta al endpoint gestionado de Aiven. |
| `mosquitto` | **DROP** | Sin ESP32 físicos conectados a Render (no hay red local para que los dispositivos IoT lo alcancen), MQTT real no aplica en este despliegue. Ver mitigación: setear `MQTT_ENABLED=false` para evitar el `ValueError` de validación en `config.py` que exige credenciales MQTT fuera de dev. |
| `mailpit` | **DROP** | Es un SMTP de prueba local (captura correos, no los envía). Si se quiere email real en producción hay que apuntar `SMTP_HOST` a un proveedor real (no cubierto por este audit) o dejar `SMTP_HOST` vacío para desactivar el envío. |
| `redis` | **DROP** | La ausencia de Redis deja el rate limiting en memoria para el demo; la revocación JWT ya persiste `jti` en MySQL y no depende de este servicio. Con un solo proceso Render (no hay múltiples instancias) el rate limiting en memoria es funcionalmente equivalente, aunque se reinicia en cada cold start. |
| `ollama` | **DROP** | 800 MB de límite de memoria él solo ya excede el tier completo de Render free. No hay endpoint crítico documentado que dependa de él para el flujo core (telemetría → alerta → predicción → dashboard); si algún endpoint IA-asistida lo usa, quedará inactivo — no es parte de este audit revisarlo. |
| `ollama-pull` | **DROP** | Job de inicialización de Ollama, mismo motivo. |

## 3. Compatibilidad con Aiven MySQL (TLS)

**No se necesitan cambios en `requirements.txt`.** Verificado en código, no adivinado:

- `pymysql==1.1.1` (ya en requirements) soporta SSL nativamente vía `pymysql.connect(ssl=...)`.
- SQLAlchemy 2.0.40 con el dialecto `mysql+pymysql` reenvía automáticamente los parámetros de query string de la URL como kwargs de conexión. Lo probé directo contra el dialecto instalado en el venv del proyecto:

  ```python
  from sqlalchemy.dialects.mysql.pymysql import MySQLDialect_pymysql
  from sqlalchemy.engine import make_url
  url = make_url("mysql+pymysql://user:pass@host:3306/db?ssl_ca=/path/ca.pem&ssl_verify_cert=true")
  MySQLDialect_pymysql().create_connect_args(url)
  # -> kwargs incluye: {'ssl_verify_cert': 'true', 'ssl': {'ca': '/path/ca.pem'}}
  ```

- `app/database.py` no pasa `connect_args` propios para MySQL (`connect_args = {} if not sqlite`), así que no hay conflicto: todo el TLS se resuelve pasando los parámetros directo en `DATABASE_URL`.

**Acción requerida (config, no código):** el `DATABASE_URL` de Render debe incluir el CA cert de Aiven, típicamente:
```
mysql+pymysql://<user>:<pass>@<aiven-host>:<port>/<db>?ssl_ca=/etc/secrets/aiven-ca.pem
```
Render soporta "Secret Files" para montar el `.pem` de Aiven en una ruta como `/etc/secrets/aiven-ca.pem` sin que el certificado quede en el repo ni en variables de entorno planas.

## 4. `.github/workflows/deploy.yml` — reusabilidad para Render

**No es reusable tal cual.** Este workflow está diseñado para desplegar por SSH a un VPS con Docker Compose (`appleboy/ssh-action`, `docker compose pull && up -d --build`). Render no se despliega por SSH — se dispara vía Git push a un repo conectado o vía Render CLI/API (`render deploy` / webhook de deploy hook). **Se necesita un workflow nuevo** (o ninguno, si se usa el auto-deploy nativo de Render on push a `main`, que no requiere GitHub Actions en absoluto).

**Riesgo histórico detectado, independiente del destino de deploy:**
- Línea 67: `cp .env.example .env || true` — si `.env` no existe en el VPS, lo crea copiando el template de ejemplo. El `|| true` silencia cualquier error de esa copia. Combinado con la validación de `config.py` (`validate_security_settings`), en teoría un `.env` mal poblado con valores de ejemplo debería fallar el arranque de la app (SECRET_KEY vacío se autogenera pero con warning, no error; DATABASE_URL sqlite sí truena en prod; MQTT con password `manttoai_mqtt_dev` también truena). O sea, el fallback es peligroso en potencia pero `config.py` actúa como red de seguridad para varios de los casos más graves. Aun así, el patrón es frágil: un despliegue nuevo sin `.env` real generaría un `.env` de plantilla que probablemente falle igual, solo que en el arranque del container en vez de en el step de CI — deploy "exitoso" según el step 5 (que solo hace `echo`, no valida nada), pero el servicio real caído.
- Step "Verify deployment" (líneas 90-94): **no verifica nada**, solo imprime texto (`echo "✅ Deployment completed"`). No hace un `curl` a `/health`, no revisa el exit code de `docker compose up`. Esto es un gate cosmético, no funcional — un fallo silencioso en el arranque del backend pasaría el pipeline como verde.

**Estado posterior de esos riesgos en el workspace:** ya no se materializa
`.env` desde `.env.example`, el workflow aborta si faltan secretos y ejecuta
`curl --fail` real contra `/health` y `/ready` después del reinicio remoto. El
workflow sigue siendo para VPS; no prueba ni despliega Render.

Para Render, ninguno de los dos problemas de este archivo se hereda directamente (Render maneja su propio healthcheck y build), pero si se construye un workflow nuevo para Render, no copiar el patrón `|| true` en la config de env ni el "verify" que solo hace echo.

## 5. Variables de entorno recomendadas para Render

Basado en los campos reales de `app/config.py` (no inventado):

| Variable | Valor / origen |
|---|---|
| `APP_ENV` | `production` |
| `DATABASE_URL` | Connection string de Aiven MySQL con `?ssl_ca=/etc/secrets/aiven-ca.pem` (ver sección 3) |
| `DATABASE_AUTO_INIT` | `true` (o `false` + `ALLOW_SCHEMA_AUTO_CREATE=true` si se prefiere control explícito de migraciones — ver `should_auto_create_schema()` en `database.py`) |
| `SECRET_KEY` | Secret generado con `python -c "import secrets; print(secrets.token_hex(32))"`, nunca el default `manttoai-dev-secret` (bloqueado por validación en prod) |
| `MQTT_ENABLED` | `false` — sin broker Mosquitto accesible en este despliegue, evita el `ValueError` de credenciales MQTT obligatorias fuera de dev |
| `ENABLE_PREDICTION_SCHEDULER` | `true` si se quiere la demo de predicciones automáticas; considerar `PREDICTION_INTERVAL_SECONDS` más alto (ver mitigación abajo) |
| `PREDICTION_SCHEDULER_MAX_WORKERS` | `1` en vez del default 4 (mitigación de CPU, ver sección 6) |
| `ML_AUTO_TRAIN_ON_MISSING` | `false` — el `modelo.joblib` ya viaja embebido en la imagen si el build usa `SKIP_TRAIN=false`; entrenar en runtime en 0.1 vCPU es indeseable |
| `SMTP_HOST` | dejar vacío si no hay proveedor SMTP real todavía (el envío de alertas por correo queda deshabilitado sin error, según `validate_security_settings`) |
| `REDIS_URL` / `REDIS_PASSWORD` | dejar sin setear — fallback a memoria confirmado funcional (sección 2) |
| `CORS_ALLOWED_ORIGINS` | dominio real de Vercel, ej. `https://manttoai.vercel.app` |
| `SEED_ALLOW_NON_DEV` | dejar en `false` (default) salvo que se quiera sembrar usuarios demo en prod explícitamente |

## 6. Mitigaciones antes de desplegar (bloqueantes del GO limpio)

1. **`PREDICTION_SCHEDULER_MAX_WORKERS=1`** (o deshabilitar el scheduler y disparar predicciones on-demand desde el endpoint): 4 hilos concurrentes de inferencia sklearn sobre 0.1 vCPU es el escenario más probable de latencia/timeout observable en la demo, aunque no de OOM.
2. **`ML_AUTO_TRAIN_ON_MISSING=false`** y confirmar que la imagen que se sube a Render incluye `modelo.joblib` (build con `SKIP_TRAIN=false`, o copiar el artefacto ya generado). Entrenar un RandomForest en cold start sobre 0.1 vCPU es lento y puede disparar el health check timeout de Render antes de que el servicio quede listo.
3. **Confirmar el `ssl_ca` de Aiven vía Render Secret Files**, no como variable de entorno plana con el path del cert hardcodeado en el repo.
4. **`MQTT_ENABLED=false` explícito** — sin este flag, `validate_security_settings()` en `config.py` va a tirar `ValueError` en el arranque (`APP_ENV=production` + `mqtt_enabled=True` default exige `MQTT_USERNAME`/`MQTT_PASSWORD`), y el servicio no levanta.
5. **No reusar `deploy.yml` tal cual** — construir un workflow (o usar el auto-deploy nativo de Render) que sí valide el healthcheck con un `curl` real a `/health` antes de reportar éxito.

## Notas de método

- La medición histórica se corrió en Docker Desktop sobre Apple Silicon (imagen `linux/arm64`); la validación posterior sí construyó y arrancó `linux/amd64` con el límite de 512 MiB mediante emulación QEMU.
- No se instaló ni configuró ninguna cuenta de Render/Aiven; todo lo anterior es inspección de código + medición local aislada.
- No se revisó calidad de código ni seguridad en profundidad (fuera de alcance de este audit, cubierto por otros agentes en paralelo).
