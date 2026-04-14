"""Tests unitarios para parches de esquema y helpers de DB."""

from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace

import pytest
from sqlalchemy.exc import SQLAlchemyError

from app import database


class FakeInspector:
    """Inspector mínimo para simular metadatos de tablas."""

    def __init__(
        self,
        columns: dict[str, list[str]] | None = None,
        indexes: list[dict[str, object]] | None = None,
        constraints: list[dict[str, object]] | None = None,
    ) -> None:
        self._columns = columns or {}
        self._indexes = indexes or []
        self._constraints = constraints or []

    def get_columns(self, table_name: str) -> list[dict[str, str]]:
        return [
            {"name": column_name} for column_name in self._columns.get(table_name, [])
        ]

    def get_indexes(self, _table_name: str) -> list[dict[str, object]]:
        return self._indexes

    def get_unique_constraints(self, _table_name: str) -> list[dict[str, object]]:
        return self._constraints


@dataclass
class FakeResult:
    """Resultado mínimo con rowcount para emular execute()."""

    rowcount: int = 0


class FakeConnection:
    """Context manager de conexión con captura de SQL ejecutado."""

    def __init__(
        self,
        executed_sql: list[str],
        *,
        rowcount: int = 0,
        fail_once_on: str | None = None,
        fail_exception: Exception | None = None,
    ) -> None:
        self.executed_sql = executed_sql
        self.rowcount = rowcount
        self.fail_once_on = fail_once_on
        self.fail_exception = fail_exception or RuntimeError("fallo simulado")
        self._already_failed = False

    def __enter__(self) -> "FakeConnection":
        return self

    def __exit__(self, _exc_type, _exc, _tb) -> bool:
        return False

    def execute(self, statement):
        sql = str(statement)
        self.executed_sql.append(sql)

        if self.fail_once_on and self.fail_once_on in sql and not self._already_failed:
            self._already_failed = True
            raise self.fail_exception

        return FakeResult(rowcount=self.rowcount)


class FakeEngine:
    """Engine fake con dialect configurable y conexión inyectable."""

    def __init__(self, dialect_name: str, connection: FakeConnection) -> None:
        self.dialect = SimpleNamespace(name=dialect_name)
        self._connection = connection

    def begin(self) -> FakeConnection:
        return self._connection

    def connect(self) -> FakeConnection:
        return self._connection


def test_list_table_columns_returns_column_names(monkeypatch):
    """Devuelve set de columnas desde inspector SQLAlchemy."""

    fake_inspector = FakeInspector(columns={"equipos": ["id", "descripcion"]})
    monkeypatch.setattr(database, "inspect", lambda _engine: fake_inspector)

    assert database._list_table_columns("equipos") == {"id", "descripcion"}


def test_add_column_if_missing_runs_alter_table(monkeypatch):
    """Agrega columna cuando no existe en la tabla."""

    executed_sql: list[str] = []
    fake_connection = FakeConnection(executed_sql, rowcount=1)
    fake_engine = FakeEngine("sqlite", fake_connection)

    monkeypatch.setattr(database, "engine", fake_engine)
    monkeypatch.setattr(database, "_list_table_columns", lambda _table_name: {"id"})

    changed = database._add_column_if_missing(
        "equipos",
        "descripcion",
        "descripcion VARCHAR(255) NOT NULL DEFAULT 'Equipo'",
    )

    assert changed is True
    assert any(
        "ALTER TABLE equipos ADD COLUMN descripcion" in sql for sql in executed_sql
    )


def test_add_column_if_missing_is_noop_when_column_exists(monkeypatch):
    """No ejecuta ALTER TABLE cuando la columna ya existe."""

    monkeypatch.setattr(
        database,
        "_list_table_columns",
        lambda _table_name: {"id", "descripcion"},
    )

    assert (
        database._add_column_if_missing(
            "equipos", "descripcion", "descripcion VARCHAR(255)"
        )
        is False
    )


@pytest.mark.parametrize(
    ("dialect_name", "expected_fragment"),
    [
        ("mysql", "DELETE a1"),
        ("sqlite", "DELETE FROM alertas"),
    ],
)
def test_dedupe_alertas_removes_duplicates_for_supported_dialects(
    monkeypatch,
    dialect_name: str,
    expected_fragment: str,
):
    """Deduplicación usa SQL esperado para MySQL y SQLite."""

    executed_sql: list[str] = []
    fake_connection = FakeConnection(executed_sql, rowcount=3)
    fake_engine = FakeEngine(dialect_name, fake_connection)
    monkeypatch.setattr(database, "engine", fake_engine)

    deleted_count = database._dedupe_alertas_by_logical_key()

    assert deleted_count == 3
    assert any(expected_fragment in sql for sql in executed_sql)


def test_dedupe_alertas_returns_zero_for_unsupported_dialect(monkeypatch):
    """Si el dialecto no es MySQL/SQLite, no deduplica."""

    executed_sql: list[str] = []
    fake_connection = FakeConnection(executed_sql, rowcount=3)
    fake_engine = FakeEngine("postgresql", fake_connection)
    monkeypatch.setattr(database, "engine", fake_engine)

    assert database._dedupe_alertas_by_logical_key() == 0
    assert executed_sql == []


def test_ensure_alerta_unique_index_is_noop_when_index_is_absent(monkeypatch):
    """No ejecuta cambios si el índice legacy ya no existe."""

    fake_inspector = FakeInspector(indexes=[])
    monkeypatch.setattr(database, "inspect", lambda _engine: fake_inspector)

    assert database._ensure_alerta_unique_index() is False


def test_ensure_alerta_unique_index_drops_legacy_index(monkeypatch):
    """Elimina el índice único legacy cuando todavía existe."""

    executed_sql: list[str] = []
    fake_connection = FakeConnection(executed_sql)
    fake_engine = FakeEngine("sqlite", fake_connection)
    fake_inspector = FakeInspector(
        indexes=[
            {
                "name": "uq_alerta_activa_por_equipo_tipo_mensaje",
                "column_names": ["equipo_id", "tipo", "mensaje"],
            }
        ]
    )

    monkeypatch.setattr(database, "engine", fake_engine)
    monkeypatch.setattr(database, "inspect", lambda _engine: fake_inspector)

    changed = database._ensure_alerta_unique_index()

    assert changed is True
    assert any(
        "DROP INDEX IF EXISTS uq_alerta_activa_por_equipo_tipo_mensaje" in sql
        for sql in executed_sql
    )


def test_apply_runtime_schema_fixes_logs_info_when_any_patch_applies(
    monkeypatch, caplog
):
    """Reporta por log cuando al menos un parche cambia el esquema."""

    add_column_calls: list[tuple[str, str]] = []

    def fake_add_column(table_name: str, column_name: str, _ddl: str) -> bool:
        add_column_calls.append((table_name, column_name))
        return column_name == "descripcion"

    monkeypatch.setattr(database, "_add_column_if_missing", fake_add_column)
    monkeypatch.setattr(database, "_ensure_alerta_unique_index", lambda: False)

    with caplog.at_level("INFO"):
        database.apply_runtime_schema_fixes()

    assert add_column_calls == [
        ("equipos", "descripcion"),
        ("mantenciones", "fecha_programada"),
        ("mantenciones", "fecha_ejecucion"),
        ("usuarios", "is_active"),
        ("usuarios", "password_changed_at"),
    ]
    assert "Se aplicaron parches de compatibilidad de esquema" in caplog.text


def test_apply_runtime_schema_fixes_handles_exceptions(monkeypatch, caplog):
    """No propaga excepción si falla un parche de compatibilidad."""

    def failing_add_column(_table_name: str, _column_name: str, _ddl: str) -> bool:
        raise RuntimeError("boom")

    monkeypatch.setattr(database, "_add_column_if_missing", failing_add_column)

    with caplog.at_level("ERROR"):
        database.apply_runtime_schema_fixes()

    assert "Falló la aplicación de parches de compatibilidad de esquema" in caplog.text


def test_initialize_database_schema_calls_create_all_and_runtime_fixes(monkeypatch):
    """Inicialización crea tablas y luego aplica parches idempotentes."""

    create_all_calls: list[object] = []
    runtime_fix_calls: list[bool] = []

    monkeypatch.setattr(
        database.Base.metadata,
        "create_all",
        lambda bind: create_all_calls.append(bind),
    )
    monkeypatch.setattr(
        database,
        "apply_runtime_schema_fixes",
        lambda: runtime_fix_calls.append(True),
    )
    monkeypatch.setattr(database, "should_auto_create_schema", lambda: True)
    monkeypatch.setattr(database, "should_apply_runtime_schema_fixes", lambda: True)

    database.initialize_database_schema()

    assert create_all_calls == [database.engine]
    assert runtime_fix_calls == [True]


def test_initialize_database_schema_skips_runtime_fixes_when_not_allowed(monkeypatch):
    """Si no está habilitado, no ejecuta parches runtime de esquema."""

    create_all_calls: list[object] = []
    runtime_fix_calls: list[bool] = []

    monkeypatch.setattr(
        database.Base.metadata,
        "create_all",
        lambda bind: create_all_calls.append(bind),
    )
    monkeypatch.setattr(
        database,
        "apply_runtime_schema_fixes",
        lambda: runtime_fix_calls.append(True),
    )
    monkeypatch.setattr(database, "should_auto_create_schema", lambda: True)
    monkeypatch.setattr(database, "should_apply_runtime_schema_fixes", lambda: False)

    database.initialize_database_schema()

    assert create_all_calls == [database.engine]
    assert runtime_fix_calls == []


def test_initialize_database_schema_skips_create_all_when_not_allowed(monkeypatch):
    """Fuera de desarrollo no ejecuta create_all sin flag explícita."""

    create_all_calls: list[object] = []
    runtime_fix_calls: list[bool] = []

    monkeypatch.setattr(
        database.Base.metadata,
        "create_all",
        lambda bind: create_all_calls.append(bind),
    )
    monkeypatch.setattr(database, "should_auto_create_schema", lambda: False)
    monkeypatch.setattr(database, "should_apply_runtime_schema_fixes", lambda: True)
    monkeypatch.setattr(
        database,
        "apply_runtime_schema_fixes",
        lambda: runtime_fix_calls.append(True),
    )

    database.initialize_database_schema()

    assert create_all_calls == []
    assert runtime_fix_calls == [True]


def test_should_auto_create_schema_true_in_development(monkeypatch):
    """En development habilita create_all automáticamente."""

    monkeypatch.setattr(database.settings, "app_env", "development")

    assert database.should_auto_create_schema() is True


def test_should_auto_create_schema_requires_explicit_env_outside_dev(monkeypatch):
    """Fuera de development solo habilita con ALLOW_SCHEMA_AUTO_CREATE=true."""

    monkeypatch.setattr(database.settings, "app_env", "production")
    monkeypatch.setattr(database, "getenv", lambda _key, _default="": "false")
    assert database.should_auto_create_schema() is False

    monkeypatch.setattr(database, "getenv", lambda _key, _default="": "true")
    assert database.should_auto_create_schema() is True


def test_should_auto_create_schema_respects_database_auto_init_flag(monkeypatch):
    """Si database_auto_init=false, no ejecuta create_all en ningún entorno."""

    monkeypatch.setattr(database.settings, "database_auto_init", False)
    monkeypatch.setattr(database.settings, "app_env", "development")

    assert database.should_auto_create_schema() is False


def test_should_apply_runtime_schema_fixes_true_in_development(monkeypatch):
    """En development, los parches runtime quedan habilitados."""

    monkeypatch.setattr(database.settings, "app_env", "development")

    assert database.should_apply_runtime_schema_fixes() is True


def test_should_apply_runtime_schema_fixes_requires_explicit_env_outside_dev(
    monkeypatch,
):
    """Fuera de development solo habilita con variable explícita."""

    monkeypatch.setattr(database.settings, "app_env", "production")
    monkeypatch.setattr(database, "getenv", lambda _key, _default="": "false")
    assert database.should_apply_runtime_schema_fixes() is False

    monkeypatch.setattr(database, "getenv", lambda _key, _default="": "true")
    assert database.should_apply_runtime_schema_fixes() is True


def test_should_apply_runtime_schema_fixes_respects_database_auto_init_flag(
    monkeypatch,
):
    """Si database_auto_init=false, no aplica runtime fixes en ningún entorno."""

    monkeypatch.setattr(database.settings, "database_auto_init", False)
    monkeypatch.setattr(database.settings, "app_env", "development")

    assert database.should_apply_runtime_schema_fixes() is False


def test_check_database_connection_success(monkeypatch):
    """Retorna True cuando SELECT 1 funciona."""

    executed_sql: list[str] = []
    fake_connection = FakeConnection(executed_sql)
    fake_engine = FakeEngine("sqlite", fake_connection)
    monkeypatch.setattr(database, "engine", fake_engine)

    assert database.check_database_connection() is True
    assert any("SELECT 1" in sql for sql in executed_sql)


def test_check_database_connection_failure(monkeypatch, caplog):
    """Retorna False y loguea warning cuando falla la conexión."""

    executed_sql: list[str] = []
    fake_connection = FakeConnection(
        executed_sql,
        fail_once_on="SELECT 1",
        fail_exception=SQLAlchemyError("db down"),
    )
    fake_engine = FakeEngine("sqlite", fake_connection)
    monkeypatch.setattr(database, "engine", fake_engine)

    with caplog.at_level("WARNING"):
        assert database.check_database_connection() is False

    assert "No se pudo conectar a la base de datos" in caplog.text
