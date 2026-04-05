# ManttoAI Predictivo

Prototipo académico de mantenimiento predictivo con ESP32, MQTT, FastAPI, React y un pipeline ML liviano.

## Estado actual

Este repositorio ya tiene un **scaffold funcional inicial** que respeta la arquitectura definida en `docs/arquitectura-manttoai.md`.

## Módulos principales

- `backend/`: API FastAPI y lógica de negocio
- `frontend/`: dashboard React con Vite
- `iot/`: firmware y simulador MQTT
- `docs/`: arquitectura, ADRs y documentación funcional
- `scripts/`: utilidades operativas

## Primeros pasos

```bash
cp backend/.env.example backend/.env
docker compose up --build -d
```

## Comandos útiles

```bash
make test
make lint
make build-front
make e2e-front
make simulate
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
