from logging.config import fileConfig

from sqlalchemy import engine_from_config, inspect, text
from sqlalchemy import pool

from alembic import context
from alembic.script import ScriptDirectory

from app import models  # noqa: F401
from app.config import get_settings
from app.database import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.database_url)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata


def _schema_matches_metadata(connection) -> bool:
    """Comprueba tablas y columnas antes de estampar una BD no versionada."""

    inspector = inspect(connection)
    actual_tables = set(inspector.get_table_names()) - {"alembic_version"}
    expected_tables = set(target_metadata.tables)
    if actual_tables != expected_tables:
        return False

    for table_name, table in target_metadata.tables.items():
        actual_columns = {
            str(column["name"]) for column in inspector.get_columns(table_name)
        }
        expected_columns = {str(column.name) for column in table.columns}
        if actual_columns != expected_columns:
            return False

    return True


def _stamp_head(connection) -> None:
    """Registra head y confirma la transacción en el dialecto configurado."""

    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.get_context().stamp(ScriptDirectory.from_config(config), "head")
    connection.commit()


def _bootstrap_empty_database(connection) -> bool:
    """Crea el esquema actual y registra head cuando la BD está vacía.

    La primera migración histórica fue generada contra una base que ya tenía
    las tablas del MVP. Mantenerla como raíz es necesario para no invalidar
    bases que ya registraron esa revisión, pero impide arrancar una base nueva.
    Este camino explícito funciona como baseline para bases completamente
    vacías sin alterar la cadena histórica de migraciones.
    """

    inspector = inspect(connection)
    tables = set(inspector.get_table_names())
    application_tables = tables - {"alembic_version"}
    if "alembic_version" in tables:
        version = connection.execute(
            text("SELECT version_num FROM alembic_version LIMIT 1")
        ).scalar_one_or_none()
        if version is not None:
            return False

    if application_tables:
        # Solo se estampa una base existente cuando coincide exactamente con
        # el metadata actual; un esquema parcial debe fallar cerrado.
        if not _schema_matches_metadata(connection):
            raise RuntimeError(
                "El esquema existente no coincide con el metadata actual; "
                "respaldá e inspeccioná la base antes de ejecutar Alembic."
            )
        _stamp_head(connection)
        return True

    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.get_context().stamp(ScriptDirectory.from_config(config), "head")
        Base.metadata.create_all(bind=connection)
    connection.commit()
    return True


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        if _bootstrap_empty_database(connection):
            return

        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()
        connection.commit()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
