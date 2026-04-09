# Endpoints iniciales

## System

- `GET /health`

## Auth

- `POST /auth/login`
- `POST /auth/register`

## Equipos

- `GET /equipos`
- `GET /equipos/{equipo_id}`
- `POST /equipos`
- `PUT /equipos/{equipo_id}`

## Lecturas

- `GET /lecturas`
- `GET /lecturas/latest/{equipo_id}`
- `POST /lecturas`

## Alertas

- `GET /alertas`
- `GET /alertas/count`
- `PATCH /alertas/{alerta_id}/leer`

## Predicciones

- `GET /predicciones/{equipo_id}`
- `POST /predicciones/ejecutar/{equipo_id}`

## Dashboard

- `GET /dashboard/resumen`

### GET `/dashboard/resumen`

Entrega un contrato compacto y estable para la vista principal del dashboard,
pensado para polling periódico sin payload gigante.

#### Request

No requiere body.

#### Response `200 OK`

Campos principales:

- `total_equipos` (`int`): total de equipos persistidos.
- `alertas_activas` (`int`): total de alertas no leídas.
- `equipos_en_riesgo` (`int`): cantidad de equipos con última probabilidad `>= 0.5`.
- `ultima_clasificacion` (`string`): clasificación de la última predicción global.
- `probabilidad_falla` (`float`): probabilidad de la última predicción global.
- `equipos` (`array`): resumen mínimo por equipo para cards/listado.

Campos por item en `equipos`:

- `id` (`int`)
- `nombre` (`string`)
- `ultima_temperatura` (`float | null`)
- `ultima_probabilidad` (`float | null`)
- `alertas_activas` (`int`)

Ejemplo de respuesta:

```json
{
  "total_equipos": 3,
  "alertas_activas": 1,
  "equipos_en_riesgo": 1,
  "ultima_clasificacion": "alerta",
  "probabilidad_falla": 0.68,
  "equipos": [
    {
      "id": 1,
      "nombre": "Compresor principal",
      "ultima_temperatura": 51.2,
      "ultima_probabilidad": 0.68,
      "alertas_activas": 1
    },
    {
      "id": 2,
      "nombre": "Bomba respaldo",
      "ultima_temperatura": 35.4,
      "ultima_probabilidad": 0.22,
      "alertas_activas": 0
    }
  ]
}
```

Notas:

- Si no existe lectura/predicción para un equipo, `ultima_temperatura` y/o `ultima_probabilidad` se retornan en `null`.
- Si no existen predicciones globales, se retorna `ultima_clasificacion: "normal"` y `probabilidad_falla: 0.0`.
- El endpoint prioriza datos operativos del MVP y evita agregaciones históricas pesadas.

#### Rate limiting por rol

`GET /dashboard/resumen` aplica cuota diferenciada por usuario autenticado:

- `admin`: `10/minute`
- `tecnico`: `6/minute`
- `visualizador`: `3/minute`

Al exceder la cuota, la API responde `429 Too Many Requests`.

## Reportes

- `GET /reportes/lecturas.csv`
- `GET /reportes/alertas.csv`
- `GET /reportes/mantenciones.csv`
- `GET /reportes/ejecutivo.pdf`

Rate limiting por rol para endpoints de reportes:

- CSV (`lecturas`, `alertas`, `mantenciones`):
  - `admin`: `80/hour`
  - `tecnico`: `60/hour`
  - `visualizador`: `40/hour`
- PDF (`ejecutivo`):
  - `admin`: `40/hour`
  - `tecnico`: `30/hour`
  - `visualizador`: `20/hour`

## Contrato MQTT (ingesta de lecturas)

### Topic esperado

- `manttoai/equipo/{equipo_id}/lecturas`

### Payload JSON esperado

```json
{
  "temperatura": 45.2,
  "humedad": 60.0,
  "vib_x": 0.3,
  "vib_y": 0.1,
  "vib_z": 9.8,
  "timestamp": "2026-04-04T22:00:00Z"
}
```

Notas:

- `equipo_id` se obtiene desde el topic.
- `timestamp` puede ser opcional para compatibilidad con fuentes legacy.

## Umbrales

- `GET /umbrales`
- `GET /umbrales?equipo_id={equipo_id}`
- `GET /umbrales/equipo/{equipo_id}`
- `GET /umbrales/{umbral_id}`
- `POST /umbrales`
- `POST /umbrales/equipo/{equipo_id}`
- `PUT /umbrales/{umbral_id}`
- `DELETE /umbrales/{umbral_id}`
