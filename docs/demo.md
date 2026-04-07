# Guía de demo MVP

Esta guía permite repetir el flujo completo del MVP para defensa académica y grabación de video.

## Objetivo

Validar de punta a punta:

1. simulador MQTT publicando lecturas,
2. persistencia en backend,
3. generación de alertas y predicción de riesgo,
4. visualización en dashboard.

## Precondiciones

- Docker + Docker Compose V2 (`docker compose`)
- GNU Make
- `curl`
- Puerto `8000` disponible en host local

## Opción A (recomendada): smoke automático

```bash
bash scripts/smoke_test.sh
```

> Seguridad: este smoke modifica datos (crea lecturas, alertas y predicciones). Ejecutarlo solo contra `localhost`. Para forzar un entorno remoto, usar explícitamente `SMOKE_ALLOW_REMOTE=true`.

El script ejecuta:

- `make setup-env`
- `make config`
- `make up`
- `make seed`
- `make simulate`
- lectura de endpoints críticos (`/lecturas`, `/alertas`, `/predicciones`, `/dashboard/resumen`)
- verificación de disponibilidad frontend (`http://localhost:5173`)

Si el modelo no está disponible, lo entrena automáticamente antes de reintentar predicción.

Variables opcionales del script:

- `API_URL` (default `http://localhost:8000`)
- `FRONTEND_URL` (default `http://localhost:5173`)
- `EQUIPO_ID` (default `1`)

## Opción B: demo guiada paso a paso

### 1) Levantar stack y seed

```bash
make setup-env
make config
make up
make seed
```

### 2) Escenario de operación normal (simulador -> persistencia)

```bash
make simulate
curl "http://localhost:8000/lecturas?equipo_id=1"
```

Resultado esperado: lista de lecturas no vacía.

### 2b) Escenario multi-equipo (3 nodos en paralelo)

```bash
make verify-3-nodes
```

Resultado esperado:

- validación en verde para equipos `1`, `2`, `3`,
- desfase dentro del umbral de simultaneidad,
- dashboard mostrando telemetría para los 3 equipos.

### 3) Escenario de breach de umbral con alerta

```bash
curl -X POST "http://localhost:8000/lecturas" \
  -H "Content-Type: application/json" \
  -d '{"equipo_id":1,"temperatura":95.0,"humedad":30.0,"vib_x":2.5,"vib_y":2.5,"vib_z":25.0}'

curl "http://localhost:8000/alertas?equipo_id=1&solo_no_leidas=true&limite=100"
```

Resultado esperado: al menos una alerta activa (`tipo` temperatura o vibración).

### 4) Escenario de predicción de riesgo visible en dashboard

```bash
curl -X POST "http://localhost:8000/predicciones/ejecutar/1"
curl "http://localhost:8000/dashboard/resumen"
```

Si `/predicciones/ejecutar/1` responde `503` por artefacto ausente:

```bash
docker compose exec backend python /app/app/ml/train.py
curl -X POST "http://localhost:8000/predicciones/ejecutar/1"
```

Resultado esperado en dashboard:

- `equipos_en_riesgo >= 1`
- `equipos[].ultima_probabilidad` no nulo para el equipo probado.

## Apoyo visual para la defensa

Durante la demo del frontend (`http://localhost:5173`), mostrar en este orden:

1. Dashboard (cards + tendencia)
2. Equipos (estado actual)
3. Alertas (nuevas y marcar leída)
4. Historial (lecturas y mantenciones)

### 5) Escenario de email SMTP (si configurado)

```bash
python scripts/test_smtp_real.py
```

Resultado esperado: `SUCCESS: Email enviado correctamente.`

> Si `SMTP_HOST` no está en `backend/.env`, este escenario se omite sin error.
> El smoke automático (`bash scripts/smoke_test.sh`) detecta y ejecuta este paso automáticamente.

## Evidencia para defensa

Completar `docs/evidencia-qa-e2e.md` con los resultados reales de cada criterio.
Guardar capturas en `evidencia/` con nombre `captura-YYYYMMDD-HHMM.png`.

## Troubleshooting rápido

- **`make config` falla por env:** ejecutar `make setup-env`.
- **No aparecen lecturas:** verificar contenedor backend/mosquitto con `make logs`.
- **Predicción 503:** entrenar modelo con `docker compose exec backend python /app/app/ml/train.py`.
- **Sin alertas tras breach:** revisar que `make seed` haya creado umbrales y reintentar POST extremo.
- **Email SMTP falla:** verificar `SMTP_HOST`, `SMTP_USER`, `SMTP_PASSWORD` en `backend/.env`; probar con `python scripts/test_smtp_real.py`.
