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
