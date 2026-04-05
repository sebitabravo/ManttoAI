# Backend ManttoAI

Backend FastAPI organizado con el patrón **router → service → model**.

## Objetivo del scaffold

- exponer `GET /health`
- entregar endpoints base para el dashboard
- dejar la estructura lista para crecer sin mezclar capas

## Ejecutar local

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
uvicorn app.main:app --reload --port 8000
```

## Tests

```bash
pytest tests/ -v --cov=app --cov-report=term-missing
```
