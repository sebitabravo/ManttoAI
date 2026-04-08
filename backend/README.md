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

El backend toma `DATABASE_URL` desde `backend/.env` y expone en `/health` la señal `database.connected`.

`Base.metadata.create_all(...)` queda habilitado automáticamente sólo en `development`.
Fuera de desarrollo se activa únicamente con `ALLOW_SCHEMA_AUTO_CREATE=true`.

Los parches runtime idempotentes de compatibilidad de esquema (columnas nuevas y constraint de alertas)
se aplican automáticamente en `development`.
Fuera de desarrollo se ejecutan sólo si `ALLOW_RUNTIME_SCHEMA_CHANGES=true` para evitar cambios
destructivos no intencionales en bases productivas.

## Modelo ML en runtime

- Por defecto el build Docker instala solo dependencias runtime (`INSTALL_DEV_REQS=false`) y
  no entrena modelo (`SKIP_TRAIN=true`) para mantener imágenes livianas y builds reproducibles.
- En desarrollo local, `docker-compose.override.yml` activa `INSTALL_DEV_REQS=true`.
- Si se requiere artefacto embebido en imagen: `docker compose build --build-arg SKIP_TRAIN=false backend`.
- Si falta en runtime y `ML_AUTO_TRAIN_ON_MISSING=true`, el backend auto-entrena y continúa.

## SMTP de demo

- El stack local incluye Mailpit (`mailpit:1025` SMTP, `http://localhost:8025` UI).
- Permite validar alertas email sin depender de un proveedor externo.

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
pytest tests/ -v --cov=app --cov-report=term-missing --cov-fail-under=80
```

**Umbral de cobertura**: 80% — configurado en `--cov-fail-under=80`. Si la cobertura baja del umbral, pytest fallará indicando qué líneas no están cubiertas.

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
