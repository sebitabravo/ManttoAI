# Backend ManttoAI

Backend FastAPI organizado con el patrón **router → service → model**.

## Objetivo del scaffold

- exponer `GET /health`
- verificar conectividad DB desde `GET /health`
- entregar endpoints base para el dashboard
- dejar la estructura lista para crecer sin mezclar capas

## Ejecutar local

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

## Flujo mínimo con MySQL (Docker Compose)

Desde la raíz del repo:

```bash
cp backend/.env.example backend/.env
docker compose up -d mysql backend
curl http://localhost:8000/health
```

El backend toma `DATABASE_URL` desde `backend/.env`, crea tablas faltantes al arrancar con `Base.metadata.create_all(...)` y expone en `/health` la señal `database.connected`.

> **Nota MVP**: el bootstrap automático de esquema (`create_all`) es suficiente para el prototipo. En un entorno productivo se reemplazaría por migraciones explícitas con Alembic.

## Tests

```bash
pytest tests/ -v --cov=app --cov-report=term-missing
```
