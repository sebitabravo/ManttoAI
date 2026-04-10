# API Endpoints — ManttoAI

Todos los endpoints (excepto `/health` y `/legal/*`) están bajo el prefijo `/api/v1/`.
Los paths legacy sin prefijo también funcionan pero están ocultos del schema OpenAPI.

**Autenticación:** Los endpoints marcados con 🔒 requieren header `Authorization: Bearer <JWT>`.
Los marcados con 🔑 requieren header `X-API-Key`.
Los marcados con 👑 requieren rol `admin`.

---

## System

| Método | Path | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/health` | Estado de API y conectividad de base de datos | No |

---

## Auth (`/api/v1/auth`)

| Método | Path | Descripción | Auth |
|--------|------|-------------|------|
| POST | `/api/v1/auth/register` | Registra un usuario persistido | No |
| POST | `/api/v1/auth/login` | Retorna token JWT para credenciales válidas | No |
| GET | `/api/v1/auth/me` | Retorna el usuario autenticado | 🔒 |
| POST | `/api/v1/auth/logout` | Limpia cookie de autenticación | No |

---

## Equipos (`/api/v1/equipos`)

| Método | Path | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/api/v1/equipos` | Lista equipos disponibles | 🔒 |
| GET | `/api/v1/equipos/{equipo_id}` | Obtiene un equipo por ID | 🔒 |
| POST | `/api/v1/equipos` | Crea un equipo | 🔒 admin/técnico |
| PUT | `/api/v1/equipos/{equipo_id}` | Actualiza un equipo | 🔒 admin/técnico |
| DELETE | `/api/v1/equipos/{equipo_id}` | Elimina un equipo | 👑 |

---

## Lecturas (`/api/v1/lecturas`)

| Método | Path | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/api/v1/lecturas` | Historial de lecturas con límite por defecto | 🔒 |
| GET | `/api/v1/lecturas/latest/{equipo_id}` | Última lectura de un equipo | 🔒 |
| POST | `/api/v1/lecturas` | Crea una lectura persistida | 🔒 admin/técnico |

---

## Alertas (`/api/v1/alertas`)

| Método | Path | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/api/v1/alertas` | Lista alertas con filtros | 🔒 |
| GET | `/api/v1/alertas/count` | Conteo total y no leído | 🔒 |
| PATCH | `/api/v1/alertas/{alerta_id}/leer` | Marca alerta como leída | 🔒 admin/técnico |

---

## Predicciones (`/api/v1/predicciones`)

| Método | Path | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/api/v1/predicciones/{equipo_id}` | Última predicción de un equipo | 🔒 |
| POST | `/api/v1/predicciones/ejecutar/{equipo_id}` | Ejecuta predicción y la persiste | 🔒 |

---

## Dashboard (`/api/v1/dashboard`)

| Método | Path | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/api/v1/dashboard/resumen` | Resumen agregado para el frontend | 🔒 |

### GET `/api/v1/dashboard/resumen` — Detalle

Entrega un contrato compacto y estable para la vista principal del dashboard,
pensado para polling periódico sin payload gigante.

**Response `200 OK`:**

- `total_equipos` (`int`): total de equipos persistidos.
- `alertas_activas` (`int`): total de alertas no leídas.
- `equipos_en_riesgo` (`int`): cantidad de equipos con última probabilidad `>= 0.5`.
- `ultima_clasificacion` (`string`): clasificación de la última predicción global.
- `probabilidad_falla` (`float`): probabilidad de la última predicción global.
- `equipos` (`array`): resumen mínimo por equipo.

Ejemplo:

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
    }
  ]
}
```

**Rate limiting:** admin `10/min`, tecnico `6/min`, visualizador `3/min`. Respuesta: `429 Too Many Requests`.

---

## Umbrales (`/api/v1/umbrales`)

| Método | Path | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/api/v1/umbrales` | Lista umbrales con filtro opcional por equipo | 🔒 |
| GET | `/api/v1/umbrales/equipo/{equipo_id}` | Umbrales de un equipo específico | 🔒 |
| GET | `/api/v1/umbrales/{umbral_id}` | Obtiene un umbral por ID | 🔒 |
| POST | `/api/v1/umbrales` | Crea un umbral | 👑 |
| POST | `/api/v1/umbrales/equipo/{equipo_id}` | Crea umbral asociado al equipo de la ruta | 👑 |
| PUT | `/api/v1/umbrales/{umbral_id}` | Actualiza un umbral | 🔒 admin/técnico |
| DELETE | `/api/v1/umbrales/{umbral_id}` | Elimina un umbral | 👑 |

---

## Mantenciones (`/api/v1/mantenciones`)

| Método | Path | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/api/v1/mantenciones` | Lista mantenciones | 🔒 |
| GET | `/api/v1/mantenciones/{mantencion_id}` | Obtiene una mantención por ID | 🔒 |
| POST | `/api/v1/mantenciones` | Crea una mantención | 🔒 admin/técnico |
| PUT | `/api/v1/mantenciones/{mantencion_id}` | Actualiza una mantención | 🔒 admin/técnico |
| DELETE | `/api/v1/mantenciones/{mantencion_id}` | Elimina una mantención | 👑 |

---

## Reportes (`/api/v1/reportes`)

| Método | Path | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/api/v1/reportes/lecturas.csv` | Descarga lecturas en CSV | 🔒 |
| GET | `/api/v1/reportes/alertas.csv` | Descarga alertas en CSV | 🔒 |
| GET | `/api/v1/reportes/mantenciones.csv` | Descarga mantenciones en CSV | 🔒 |
| GET | `/api/v1/reportes/ejecutivo.pdf` | Descarga informe ejecutivo en PDF | 🔒 |

**Rate limiting CSV:** admin `80/h`, tecnico `60/h`, visualizador `40/h`.
**Rate limiting PDF:** admin `40/h`, tecnico `30/h`, visualizador `20/h`.

---

## Usuarios (`/api/v1/usuarios`) — solo admin

| Método | Path | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/api/v1/usuarios` | Lista todos los usuarios | 👑 |
| GET | `/api/v1/usuarios/{usuario_id}` | Obtiene un usuario por ID | 👑 |
| POST | `/api/v1/usuarios` | Crea un nuevo usuario | 👑 |
| PUT | `/api/v1/usuarios/{usuario_id}` | Actualiza un usuario | 👑 |
| DELETE | `/api/v1/usuarios/{usuario_id}` | Elimina un usuario | 👑 |

---

## API Keys (`/api/v1/api-keys`) — solo admin

| Método | Path | Descripción | Auth |
|--------|------|-------------|------|
| POST | `/api/v1/api-keys` | Crea una nueva API Key para dispositivo IoT | 👑 |
| GET | `/api/v1/api-keys` | Lista todas las API Keys | 👑 |
| GET | `/api/v1/api-keys/{api_key_id}` | Obtiene una API Key por ID | 👑 |
| DELETE | `/api/v1/api-keys/{api_key_id}` | Revoca una API Key | 👑 |

---

## IoT (`/api/v1/iot`)

| Método | Path | Descripción | Auth |
|--------|------|-------------|------|
| POST | `/api/v1/iot/lecturas` | Crea lectura desde dispositivo IoT autenticado | 🔑 |

---

## Audit Logs (`/api/v1/audit-logs`) — solo admin

| Método | Path | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/api/v1/audit-logs` | Lista logs de auditoría con filtros y paginación | 👑 |
| GET | `/api/v1/audit-logs/{log_id}` | Obtiene un log de auditoría por ID | 👑 |

---

## Metrics (`/api/v1/metrics`)

| Método | Path | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/api/v1/metrics/summary` | Resumen de métricas del sistema | 🔒 |
| GET | `/api/v1/metrics/health-detailed` | Health check detallado con múltiples componentes | 🔒 |
| POST | `/api/v1/metrics/reset` | Resetea métricas acumuladas | 👑 |

---

## Legal (sin prefijo `/api/v1`)

| Método | Path | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/legal/terms-of-service` | Términos de Servicio | No |
| GET | `/legal/privacy-policy` | Política de Privacidad | No |
| GET | `/legal/dpa` | Data Processing Agreement | No |

---

## Contrato MQTT (ingesta de lecturas)

### Topic esperado

`manttoai/equipo/{equipo_id}/lecturas`

### Payload JSON esperado

```json
{
  "temperatura": 45.2,
  "humedad": 60.0,
  "vib_x": 0.3,
  "vib_y": 0.1,
  "vib_z": 9.8
}
```

Notas:

- `equipo_id` se obtiene desde el topic.
- `timestamp` es opcional; si no se envía, el backend lo genera.
