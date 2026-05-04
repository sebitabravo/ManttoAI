# Despliegue en Dokploy (ManttoAI)

Guía de despliegue para el MVP con HTTPS y stack verificable, usando [Dokploy](https://docs.dokploy.com/docs/core).

## Arquitectura unificada

Este proyecto usa **un solo `docker-compose.yml`** que funciona tanto en desarrollo local como en Dokploy. Las diferencias entre entornos se manejan con:

- **Variables de entorno** (`.env` en raíz)
- **Docker Compose override** (solo local)
- **Configuración de Traefik** (Dokploy UI)

```
┌─────────────────────────────────────────────────────────────────┐
│                           DOKPLOY                               │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Traefik (HTTPS, Let's Encrypt)                          │   │
│  │   - Configurado desde UI → Domains                      │   │
│  │   - Inyecta labels y red automáticamente                │   │
│  └──────────────────────┬───────────────────────────────────┘   │
│                         │ HTTP :80                              │
│  ┌──────────────────────▼───────────────────────────────────┐   │
│  │ frontend:80 (nginx interno del contenedor)              │   │
│  │   - sirve SPA React                                     │   │
│  │   - proxy /api/* → backend:8000                         │   │
│  └──────────────────────────────────────────────────────────┘   │
│                         │                                       │
│  ┌─────────────┐   ┌────┴────────┐   ┌─────────┐   ┌─────────┐ │
│  │  frontend   │   │   backend   │   │  mysql  │   │mosquitto│ │
│  │   :80       │   │   :8000     │   │  :3306  │   │  :1883  │ │
│  └─────────────┘   └─────────────┘   └─────────┘   └─────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## 1. Crear aplicación en Dokploy

1. En Dokploy: **Projects** → nuevo proyecto → **Docker Compose**
2. **Source**: Git repository (GitHub/GitLab/etc.)
3. **Compose Path**: `docker-compose.yml` (el único archivo)
4. **Branch**: `main` o la rama deseada

## 2. Variables de entorno

En la pestaña **Environment**, pegar las variables. Dokploy las guarda como `.env` junto al compose.

### Variables requeridas

```env
# Base de datos
MYSQL_ROOT_PASSWORD=__GENERA_UNA_SEGURA__
MYSQL_DATABASE=manttoai_db

# MQTT
MQTT_USERNAME=manttoai_mqtt
MQTT_PASSWORD=__GENERA_UNA_SEGURA__

# Backend
APP_NAME=ManttoAI — Monitoreo IoT por Rubro API
APP_ENV=production
API_PREFIX=
DATABASE_URL=mysql+pymysql://root:__USA_MISMO_MYSQL_ROOT_PASSWORD__@mysql:3306/manttoai_db
DATABASE_AUTO_INIT=true
SECRET_KEY=__GENERA_UNA_SEGURA__

# MQTT (backend)
MQTT_BROKER_HOST=mosquitto
MQTT_BROKER_PORT=1883
MQTT_BASE_TOPIC=manttoai/equipo
MQTT_ENABLED=true

# Predicciones (opcional)
ENABLE_PREDICTION_SCHEDULER=true
PREDICTION_INTERVAL_SECONDS=300

# Email (opcional para alertas)
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
SMTP_FROM_EMAIL=
SMTP_TO_EMAIL=

# Frontend (opcional)
# Si desplegás frontend/backend como aplicaciones separadas,
# definir URL absoluta del backend (ej: https://api.tu-dominio.com/api/v1)
VITE_API_URL=

# Seed (opcional, primera ejecución)
SEED_ADMIN_EMAIL=admin@manttoai.local
SEED_ADMIN_PASSWORD=__GENERA_UNA_SEGURA__
```

## 3. Dominio y HTTPS

1. Ir a pestaña **Domains** de la aplicación
2. **Add Domain**:
   - **Service**: `frontend`
   - **Port**: `80`
   - **Domain**: tu dominio (ej: `manttoai.example.com`)
   - **HTTPS**: habilitado (Let's Encrypt automático)
3. Dokploy inyecta automáticamente:
   - Labels de Traefik
   - Red `dokploy-network` al servicio frontend

## 4. Primera ejecución: seed (opcional)

Desde la consola de Dokploy o SSH:

```bash
# Ejecutar seed con datos de ejemplo
docker compose exec -e APP_ENV=development backend python /scripts/seed_db.py
```

Para producción, agregar `SEED_ALLOW_NON_DEV=true` en Environment.

## 5. Verificación

```bash
# Frontend
curl -I "https://tu-dominio/"

# API health
curl -sS "https://tu-dominio/api/health"

# MQTT (desde cliente externo)
mosquitto_pub -h tu-dominio -p 1883 -u manttoai_mqtt -P TU_PASSWORD \
  -t "manttoai/equipo/1/lecturas" \
  -m '{"temperatura":45.2,"humedad":60,"vib_x":0.3,"vib_y":0.1,"vib_z":9.8}'
```

## Notas importantes

### Diferencias local vs Dokploy

| Aspecto | Local | Dokploy |
|---------|-------|---------|
| HTTPS | No (http://localhost) | Sí (Traefik + Let's Encrypt) |
| .env | `./backend/.env` (override) | `.env` raíz (generado por Dokploy) |
| Hot-reload | Sí (override monta volúmenes) | No (imagen fija) |
| Red Traefik | No aplica | Inyectada automáticamente |

### Puertos en Dokploy

- Dokploy **ignora los `ports:`** del compose para servicios internos
- Solo `mosquitto:1883` queda expuesto al host para ESP32
- Restringir con firewall si el servidor es público

### Auto-deploy

Habilitar **Auto Deploy** en Dokploy para que cada push a la rama dispare un nuevo despliegue.
