"""Verifica que Alembic pueda inicializar una base de datos vacía."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys

import pytest
from sqlalchemy import create_engine, inspect, text

from app import models  # noqa: F401
from app.database import Base


BACKEND_DIR = Path(__file__).resolve().parents[1]


def _run_alembic(
    database_url: str, *arguments: str
) -> subprocess.CompletedProcess[str]:
    """Ejecuta Alembic con una base aislada y la configuración del test."""

    env = os.environ.copy()
    env.update(
        {
            "APP_ENV": "development",
            "DATABASE_URL": database_url,
            "SECRET_KEY": "alembic-bootstrap-test",
            "PYTHONPATH": str(BACKEND_DIR),
        }
    )
    return subprocess.run(
        [sys.executable, "-m", "alembic", *arguments],
        cwd=BACKEND_DIR,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def test_alembic_upgrade_head_crea_esquema_desde_cero(tmp_path):
    """El bootstrap de una base vacía registra el esquema vigente en head."""

    database_url = f"sqlite:///{tmp_path / 'fresh.db'}"
    result = _run_alembic(database_url, "upgrade", "head")
    assert result.returncode == 0, result.stdout + result.stderr

    engine = create_engine(database_url)
    tables = set(inspect(engine).get_table_names())
    assert {
        "alertas",
        "api_keys",
        "audit_logs",
        "equipos",
        "lecturas",
        "mantenciones",
        "mensajes_chat",
        "organizaciones",
        "predicciones",
        "provisioning_tokens",
        "revoked_tokens",
        "umbrales",
        "usuarios",
    }.issubset(tables)

    with engine.connect() as connection:
        revision = connection.execute(
            text("SELECT version_num FROM alembic_version")
        ).scalar_one()

    assert revision == "d8e9f0a1b2c3"

    repeated = _run_alembic(database_url, "upgrade", "head")
    assert repeated.returncode == 0, repeated.stdout + repeated.stderr


def test_alembic_bootstrap_downgrade_persiste_la_reversion(tmp_path):
    """La cadena puede revertirse después del bootstrap sin perder la versión."""

    database_url = f"sqlite:///{tmp_path / 'downgrade.db'}"
    upgraded = _run_alembic(database_url, "upgrade", "head")
    assert upgraded.returncode == 0, upgraded.stdout + upgraded.stderr

    downgraded = _run_alembic(database_url, "downgrade", "base")
    assert downgraded.returncode == 0, downgraded.stdout + downgraded.stderr

    engine = create_engine(database_url)
    tables = set(inspect(engine).get_table_names())
    assert "equipos" in tables
    assert "api_keys" not in tables
    assert "revoked_tokens" not in tables
    with engine.connect() as connection:
        assert (
            connection.execute(text("SELECT version_num FROM alembic_version")).all()
            == []
        )


def test_alembic_upgrade_head_estampa_esquema_create_all_completo(tmp_path):
    """Una base actual sin versionar se transiciona sin repetir migraciones."""

    database_url = f"sqlite:///{tmp_path / 'existing-schema.db'}"
    engine = create_engine(database_url)
    Base.metadata.create_all(bind=engine)

    result = _run_alembic(database_url, "upgrade", "head")
    assert result.returncode == 0, result.stdout + result.stderr

    with engine.connect() as connection:
        revision = connection.execute(
            text("SELECT version_num FROM alembic_version")
        ).scalar_one()

    assert revision == "d8e9f0a1b2c3"


def test_alembic_upgrade_head_rechaza_esquema_no_versionado_parcial(tmp_path):
    """No ejecuta migraciones históricas sobre un esquema parcial."""

    database_url = f"sqlite:///{tmp_path / 'partial-schema.db'}"
    engine = create_engine(database_url)
    Base.metadata.tables["usuarios"].create(bind=engine)

    result = _run_alembic(database_url, "upgrade", "head")
    output = result.stdout + result.stderr

    assert result.returncode != 0
    assert "esquema existente no coincide" in output

    assert "alembic_version" not in inspect(engine).get_table_names()


@pytest.mark.skipif(
    os.getenv("RUN_MYSQL_ALEMBIC_TESTS") != "1"
    or "mysql" not in os.getenv("DATABASE_URL", ""),
    reason="La prueba MySQL de Alembic requiere una base efímera y habilitación explícita",
)
def test_alembic_mysql_upgrade_downgrade():
    """El downgrade debe respetar las FKs del dialecto MySQL."""

    database_url = os.environ["DATABASE_URL"]

    upgraded = _run_alembic(database_url, "upgrade", "head")
    assert upgraded.returncode == 0, upgraded.stdout + upgraded.stderr

    downgraded = _run_alembic(database_url, "downgrade", "base")
    assert downgraded.returncode == 0, downgraded.stdout + downgraded.stderr

    engine = create_engine(database_url)
    with engine.connect() as connection:
        versions = connection.execute(
            text("SELECT version_num FROM alembic_version")
        ).all()
    assert versions == []

    foreign_keys = inspect(engine).get_foreign_keys("equipos")
    assert any(
        fk.get("constrained_columns") == ["organizacion_id"]
        and fk.get("referred_table") == "organizaciones"
        for fk in foreign_keys
    )
    assert any(
        index.get("name") == "ix_equipos_organizacion_id"
        for index in inspect(engine).get_indexes("equipos")
    )
