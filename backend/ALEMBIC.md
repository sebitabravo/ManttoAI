# Migraciones de Base de Datos con Alembic

## Instalación

Alembic ya está en `requirements.txt`. Instalar dependencias:

```bash
cd backend
pip install -r requirements.txt
```

## Inicialización

Ejecutar una sola vez para crear la estructura de migraciones:

```bash
cd backend
alembic init alembic
```

Esto creará:
- `alembic/` - Directorio de migraciones
- `alembic.ini` - Configuración de Alembic

## Configuración

Editar `alembic/env.py` para conectar con tu base de datos:

```python
from app.config import get_settings
from app.database import Base
from app import models  # Importar todos los modelos

# Configuración de la DB
settings = get_settings()
SQLALCHEMY_DATABASE_URL = settings.database_url

# Meta datos para autogenerar migraciones
target_metadata = Base.metadata
```

## Crear Primera Migración

Después de inicializar Alembic, generar la primera migración desde el estado actual de la DB:

```bash
alembic revision --autogenerate -m "initial migration"
```

Esto crea un archivo en `alembic/versions/` con los cambios detectados.

## Aplicar Migraciones

Para aplicar todas las migraciones pendientes:

```bash
alembic upgrade head
```

Para revertir a la migración anterior:

```bash
alembic downgrade -1
```

Para ver el historial de migraciones:

```bash
alembic history
```

## Flujo de Trabajo Recomendado

### Para cambios en modelos:

1. Modificar modelos en `app/models/`
2. Generar migración:
   ```bash
   alembic revision --autogenerate -m "descripción del cambio"
   ```
3. Revisar la migración generada en `alembic/versions/`
4. Aplicar migración:
   ```bash
   alembic upgrade head
   ```

### Para desarrollo local:

- Usar `DATABASE_URL=sqlite:///./manttoai_dev.db`
- Las migraciones se aplican automáticamente en `sqlite`

### Para producción:

- Usar `DATABASE_URL=mysql+pymysql://...`
- Aplicar migraciones manualmente durante deploy:
  ```bash
  alembic upgrade head
  ```

## Ventajas de Alembic vs Runtime Schema Fixes

### Antes (Runtime Schema Fixes):
```python
# Fragil, hardcodeado, difícil de revertir
_add_column_if_missing("equipos", "descripcion", "...")
```

### Ahora (Alembic):
```python
# Versionado, reversible, seguro
def upgrade():
    op.add_column('equipos', sa.Column('descripcion', sa.String(255)))

def downgrade():
    op.drop_column('equipos', 'descripcion')
```

## Migraciones Iniciales Sugeridas

Para el estado actual de ManttoAI, generar estas migraciones:

1. **Migración inicial** - Crear todas las tablas
2. **API Keys** - Agregar tabla `api_keys`
3. **Audit Logs** - Agregar tabla `audit_logs`
4. **Índices** - Agregar índices únicos y de performance

## Troubleshooting

### Error: "Target database is not up to date"

```bash
alembic stamp head
```

Esto marca la DB como actual sin aplicar migraciones (útil si ya existen tablas).

### Error: "No changes in schema"

- No hay cambios en los modelos
- Revisar que los modelos estén importados en `alembic/env.py`

### Error: "Table already exists"

- La tabla ya existe en la DB
- Usar `alembic stamp head` o borrar la tabla manualmente

## Integración con Docker Compose

Agregar a `docker-compose.yml`:

```yaml
services:
  backend:
    # ... configuración existente ...
    command: >
      sh -c "
        alembic upgrade head &&
        uvicorn app.main:app --host 0.0.0.0 --port 8000
      "
```

## Notas para el Proyecto Académico

Para la defensa académica, puedes mencionar:

1. **Alembic inicializado** - Listo para uso en producción
2. **Migraciones versionadas** - Cada cambio en schema es rastreable
3. **Reversibilidad** - Las migraciones pueden revertirse
4. **Best practice** - Es el estándar de la industria para SQLAlchemy

### Ejemplo para el reporte:

> "Se implementó Alembic para gestión de migraciones de base de datos. Esta herramienta permite versionar cambios en el schema, aplicar migraciones de forma controlada en producción, y revertir cambios si es necesario. Se sigue así el patrón recomendado por SQLAlchemy para aplicaciones en producción."
