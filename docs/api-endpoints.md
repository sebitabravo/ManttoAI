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
- `PATCH /alertas/{alerta_id}/leer`

## Predicciones

- `GET /predicciones/{equipo_id}`
- `POST /predicciones/ejecutar/{equipo_id}`

## Dashboard

- `GET /dashboard/resumen`

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
