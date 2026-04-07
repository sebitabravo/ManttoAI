# Backend ManttoAI

Backend FastAPI organizado con el patrón **router → service → model**.

## Objetivo del scaffold

- exponer `GET /health`
- verificar conectividad DB desde `GET /health`
- entregar endpoints base para el dashboard
- dejar la estructura lista para crecer sin mezclar capas

## Ejecutar local (desde directorio backend/)

```bash
# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt

# Generar archivos .env (desde la raíz del repo)
cd ..
bash scripts/setup_env.sh
cd backend

# Iniciar servidor
uvicorn app.main:app --reload --port 8000
```

## Flujo mínimo con MySQL (Docker Compose)

Desde la raíz del repo:

```bash
bash scripts/setup_env.sh
docker compose up -d mysql backend
curl http://localhost:8000/health
```

El backend toma `DATABASE_URL` desde `backend/.env`, crea tablas faltantes al arrancar con `Base.metadata.create_all(...)` y expone en `/health` la señal `database.connected`.

> **Nota MVP**: el bootstrap automático de esquema (`create_all`) es suficiente para el prototipo. En un entorno productivo se reemplazaría por migraciones explícitas con Alembic.

## Tests

Los tests usan SQLite en memoria por defecto. Solo los tests de integración requieren MySQL.

### Tests unitarios (no requiere MySQL)

```bash
# Desde el directorio backend/
pytest tests/ -v -m "not integration"
```

### Verificación rápida (sin cobertura)

```bash
pytest tests/ -v
```

### Verificación completa (con cobertura)

```bash
pytest tests/ -v --cov=app --cov-report=term-missing --cov-fail-under=60
```

**Umbral de cobertura**: 60% — configurado en `--cov-fail-under=60`. Si la cobertura baja del umbral, pytest fallará indicando qué líneas no están cubiertas.

### Tests de integración (requiere MySQL)

```bash
# Desde la raíz del repo, iniciar MySQL
docker compose up -d mysql

# Desde backend/, ejecutar solo tests de integración
pytest tests/ -v -m "integration"
```

### Dependencias de test

Las dependencias necesarias están en `requirements-dev.txt`:
- `pytest==8.3.5` — framework de testing
- `pytest-cov==6.0.0` — plugin de cobertura
- `httpx==0.28.1` — cliente HTTP para tests de integración

### Notas

- Los tests de integración que requieren servicios externos (SMTP) están marcados con `@pytest.mark.integration` y se pueden skippear con `pytest -m "not integration"`.
- La base de datos de test usa SQLite en memoria para velocidad; los tests de integración reales con MySQL requieren `docker compose up -d mysql`.
