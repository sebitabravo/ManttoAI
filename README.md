# ManttoAI Predictivo

Prototipo académico de mantenimiento predictivo con ESP32, MQTT, FastAPI, React y un pipeline ML liviano.

## Estado actual

Este repositorio tiene un MVP funcional para demo académica, respetando la arquitectura definida en `docs/arquitectura-manttoai.md`.

## Módulos principales

- `backend/`: API FastAPI y lógica de negocio
- `frontend/`: dashboard React con Vite
- `iot/`: firmware y simulador MQTT
- `docs/`: arquitectura, ADRs y documentación funcional
- `scripts/`: utilidades operativas

## Flujo local reproducible (stack + seed + simulador)

### Requisitos previos

- Docker + Docker Compose
- Docker Compose V2 (`docker compose`)
- GNU Make
- `curl` (opcional, para verificación rápida)

> ⚠️ Este flujo es **solo para desarrollo local/demo**. No uses `make seed` contra bases productivas.

### Paso a paso

```bash
# 1) Preparar archivos .env locales (idempotente)
make setup-env

# 2) Validar compose
make config

# 3) Levantar stack completo
make up

# 4) Poblar datos demo (usuario admin + equipos + umbrales)
make seed

# 5) Enviar lecturas demo por MQTT
make simulate

# 5b) (Opcional) validar escenario de 3 nodos en paralelo
make verify-3-nodes

# (Opcional) modo no interactivo para CI/scripts
# export VERIFY_ADMIN_PASSWORD="<password_admin>"
# make verify-3-nodes

# 6) Verificar resumen del dashboard
curl http://localhost:8000/dashboard/resumen

# 7) (Opcional recomendado) validar flujo completo de smoke
bash scripts/smoke_test.sh
```

> El smoke test modifica datos. Ejecutalo en local; para forzar API remota usá `SMOKE_ALLOW_REMOTE=true` de forma explícita.

> `make setup-env` también genera `mosquitto/passwd` (archivo local no versionado) usando `MQTT_USERNAME`/`MQTT_PASSWORD` de `.env` o defaults demo.
> Si cambiás credenciales MQTT después, regenerá con `make setup-mqtt-creds` y reiniciá `mosquitto`.

### Credenciales demo del seed

- Email: `admin@manttoai.local`
- Password: definida en `backend/.env.example` (default de desarrollo — no reutilizar en producción).

> Si querés cambiar estas credenciales, modificá `SEED_ADMIN_*` en `backend/.env` antes de ejecutar `make seed`.
> `make verify-3-nodes` usa prompt oculto para password de login. Para modo no interactivo, exportá `VERIFY_ADMIN_PASSWORD` o `VERIFY_ADMIN_TOKEN` en el entorno.
> El seed valida `APP_ENV=development` por seguridad. Solo se puede forzar fuera de dev con `SEED_ALLOW_NON_DEV=true`.
> No subas `.env` reales al repositorio; mantené credenciales sensibles fuera de git.

### Nota de red para desarrollo local

- MySQL y Mosquitto están ligados a `127.0.0.1` por defecto para reducir exposición accidental.
- Si necesitás recibir MQTT desde dispositivos externos (ej. ESP32 fuera del host), ajustá el puerto de `mosquitto` en `docker-compose.yml` y restringí acceso con firewall/autenticación.

## Comandos útiles

```bash
# Infra
make config
make up
make down
make logs

# Seed / simulación
make seed
make simulate
make verify-3-nodes
make smoke-test

# Backend
make test
make lint

# Frontend
make lint-front
make build-front
make e2e-front
```

## Convenciones

- `AGENTS.md` es la fuente de verdad para contexto de IA
- `CLAUDE.md` apunta a `AGENTS.md`
- comentarios de código en español
- cambios chicos y reversibles

## Documentación clave

- Arquitectura objetivo: `docs/arquitectura-manttoai.md`
- Flujo del equipo con IA: `docs/flujo-trabajo-ia.md`
- Endpoints: `docs/api-endpoints.md`
- Modelo ML: `docs/modelo-ml.md`
- Guía de demo: `docs/demo.md`
- Manual de usuario: `docs/manual-usuario.md`
- Checklist final de entrega: `docs/checklist-entrega.md`
