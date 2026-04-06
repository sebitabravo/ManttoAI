"""Tests de concurrencia sobre alertas de predicción usando la BD configurada."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import os

import pytest
from sqlalchemy import delete, select

from app.config import get_settings
from app.database import SessionLocal, initialize_database_schema
from app.models.alerta import Alerta
from app.models.equipo import Equipo
from app.models.lectura import Lectura
from app.models.prediccion import Prediccion
from app.services import alerta_service, email_service, prediccion_service


class _FixedProbabilityModel:
    """Modelo determinista para simular fallas concurrentes."""

    def predict_proba(self, _rows):
        return [[0.08, 0.92]]


@pytest.mark.skipif(
    os.getenv("RUN_DB_CONCURRENCY_TESTS") != "1"
    or "mysql" not in get_settings().database_url,
    reason="La prueba de concurrencia requiere MySQL real y habilitación explícita",
)
def test_concurrent_execute_prediction_creates_single_active_alert(monkeypatch):
    """Valida deduplicación real de alerta activa bajo concurrencia."""

    initialize_database_schema()
    monkeypatch.setattr(
        prediccion_service,
        "load_model_artifact",
        lambda _model_path=None: {
            "model": _FixedProbabilityModel(),
            "features": ["temperatura", "humedad", "vib_x", "vib_y", "vib_z"],
            "target": "riesgo",
            "model_params": {"n_estimators": 120, "random_state": 42},
        },
    )
    # Mockear get_smtp_client para evitar intentos reales de conexión SMTP
    from unittest.mock import MagicMock

    mock_smtp = MagicMock()
    monkeypatch.setattr(
        email_service,
        "get_smtp_client",
        lambda: mock_smtp,
    )

    with SessionLocal() as db:
        db.execute(delete(Prediccion))
        db.execute(delete(Alerta))
        db.execute(delete(Lectura))
        db.execute(delete(Equipo))
        db.commit()

        equipo = Equipo(
            nombre="Equipo Concurrencia",
            ubicacion="Laboratorio",
            tipo="Motor",
            estado="operativo",
        )
        db.add(equipo)
        db.commit()
        db.refresh(equipo)

        db.add(
            Lectura(
                equipo_id=equipo.id,
                temperatura=58.0,
                humedad=61.0,
                vib_x=0.48,
                vib_y=0.31,
                vib_z=10.4,
                timestamp=datetime.now(timezone.utc),
            )
        )
        db.commit()
        equipo_id = equipo.id

    def _execute_prediction_once() -> None:
        with SessionLocal() as db:
            prediccion_service.execute_prediction(db, equipo_id)

    with ThreadPoolExecutor(max_workers=4) as executor:
        list(executor.map(lambda _index: _execute_prediction_once(), range(4)))

    with SessionLocal() as db:
        active_alerts = list(
            db.scalars(
                select(Alerta)
                .where(Alerta.equipo_id == equipo_id)
                .where(Alerta.tipo == alerta_service.PREDICTION_ALERT_TYPE)
                .where(Alerta.leida.is_(False))
            )
        )
        persisted_predictions = list(
            db.scalars(select(Prediccion).where(Prediccion.equipo_id == equipo_id))
        )

        db.execute(delete(Prediccion).where(Prediccion.equipo_id == equipo_id))
        db.execute(delete(Alerta).where(Alerta.equipo_id == equipo_id))
        db.execute(delete(Lectura).where(Lectura.equipo_id == equipo_id))
        db.execute(delete(Equipo).where(Equipo.id == equipo_id))
        db.commit()

    assert len(active_alerts) == 1
    assert len(persisted_predictions) == 4
