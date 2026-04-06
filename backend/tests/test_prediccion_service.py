"""Tests de servicio para predicciones."""

from collections.abc import Generator
from datetime import datetime, timedelta, timezone

import numpy as np
import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app import models  # noqa: F401
from app.database import Base
from app.models.equipo import Equipo
from app.models.lectura import Lectura
from app.models.prediccion import Prediccion
from app.services import prediccion_service


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    """Entrega sesión SQLite aislada para tests de servicio."""

    engine = create_engine(
        "sqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session_local = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        future=True,
    )

    Base.metadata.create_all(bind=engine)
    session = testing_session_local()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def _create_equipo(db_session: Session, nombre: str = "Equipo Servicio") -> int:
    """Crea un equipo auxiliar para pruebas de predicción."""

    equipo = Equipo(
        nombre=nombre,
        ubicacion="Laboratorio",
        tipo="Motor",
        estado="operativo",
    )
    db_session.add(equipo)
    db_session.commit()
    db_session.refresh(equipo)
    return equipo.id


def _create_lectura(
    db_session: Session,
    equipo_id: int,
    temperatura: float,
    timestamp: datetime,
) -> None:
    """Crea una lectura con timestamp controlado para elegir la última."""

    lectura = Lectura(
        equipo_id=equipo_id,
        temperatura=temperatura,
        humedad=56.0,
        vib_x=0.3,
        vib_y=0.2,
        vib_z=9.8,
        timestamp=timestamp,
    )
    db_session.add(lectura)
    db_session.commit()


class _FakeModel:
    """Mock de modelo con trazabilidad de filas de inferencia."""

    def __init__(self, probability: float):
        self.probability = probability
        self.received_rows: list[list[float]] = []

    def predict_proba(self, rows):
        self.received_rows.extend(rows)
        return [[1.0 - self.probability, self.probability]]


def test_execute_prediction_uses_latest_reading_and_persists(db_session, monkeypatch):
    """Valida inferencia usando última lectura y guardando predicción en DB."""

    equipo_id = _create_equipo(db_session)
    now = datetime.now(timezone.utc)
    _create_lectura(
        db_session,
        equipo_id=equipo_id,
        temperatura=42.0,
        timestamp=now - timedelta(minutes=5),
    )
    _create_lectura(
        db_session,
        equipo_id=equipo_id,
        temperatura=51.0,
        timestamp=now,
    )

    fake_model = _FakeModel(probability=0.67)
    monkeypatch.setattr(
        prediccion_service,
        "load_model_artifact",
        lambda _model_path=None: {
            "model": fake_model,
            "features": ["temperatura", "humedad", "vib_x", "vib_y", "vib_z"],
            "target": "riesgo",
            "model_params": {"n_estimators": 120, "random_state": 42},
        },
    )

    result = prediccion_service.execute_prediction(db_session, equipo_id)

    assert result.equipo_id == equipo_id
    assert result.clasificacion == "alerta"
    assert result.probabilidad == 0.67
    assert fake_model.received_rows[0][0] == 51.0

    persisted = list(
        db_session.scalars(select(Prediccion).where(Prediccion.equipo_id == equipo_id))
    )
    assert len(persisted) == 1
    assert persisted[0].id == result.id


def test_get_prediction_returns_latest_persisted(db_session):
    """Valida que get_prediction entregue la predicción más reciente."""

    equipo_id = _create_equipo(db_session)

    first = Prediccion(
        equipo_id=equipo_id,
        clasificacion="normal",
        probabilidad=0.32,
        modelo_version="rf-v1",
    )
    db_session.add(first)
    db_session.commit()
    db_session.refresh(first)

    second = Prediccion(
        equipo_id=equipo_id,
        clasificacion="falla",
        probabilidad=0.91,
        modelo_version="rf-v1",
    )
    db_session.add(second)
    db_session.commit()
    db_session.refresh(second)

    latest = prediccion_service.get_prediction(db_session, equipo_id)

    assert latest.id == second.id
    assert latest.clasificacion == "falla"
    assert latest.probabilidad == 0.91


def test_execute_prediction_returns_503_when_model_is_unavailable(
    db_session,
    monkeypatch,
):
    """Valida 503 cuando el artefacto del modelo no está disponible."""

    equipo_id = _create_equipo(db_session)
    _create_lectura(
        db_session,
        equipo_id=equipo_id,
        temperatura=47.0,
        timestamp=datetime.now(timezone.utc),
    )

    def failing_loader(_model_path=None):
        raise RuntimeError("artifact missing")

    monkeypatch.setattr(prediccion_service, "load_model_artifact", failing_loader)

    with pytest.raises(HTTPException) as exc_info:
        prediccion_service.execute_prediction(db_session, equipo_id)

    assert exc_info.value.status_code == 503
    assert exc_info.value.detail == "Modelo de predicción no disponible"


def test_execute_prediction_returns_500_when_artifact_requires_missing_feature(
    db_session,
    monkeypatch,
):
    """Valida error cuando el artefacto pide features no disponibles."""

    equipo_id = _create_equipo(db_session)
    _create_lectura(
        db_session,
        equipo_id=equipo_id,
        temperatura=47.0,
        timestamp=datetime.now(timezone.utc),
    )

    fake_model = _FakeModel(probability=0.7)
    monkeypatch.setattr(
        prediccion_service,
        "load_model_artifact",
        lambda _model_path=None: {
            "model": fake_model,
            "features": ["temperatura", "humedad", "vib_inexistente"],
            "target": "riesgo",
            "model_params": {"n_estimators": 120, "random_state": 42},
        },
    )

    with pytest.raises(HTTPException) as exc_info:
        prediccion_service.execute_prediction(db_session, equipo_id)

    assert exc_info.value.status_code == 500
    assert "features no disponibles" in str(exc_info.value.detail)


def test_execute_prediction_supports_single_class_numpy_classes(
    db_session, monkeypatch
):
    """Valida fallback cuando el modelo reporta una sola clase en numpy."""

    equipo_id = _create_equipo(db_session)
    _create_lectura(
        db_session,
        equipo_id=equipo_id,
        temperatura=49.0,
        timestamp=datetime.now(timezone.utc),
    )

    class _SingleClassNumpyModel:
        classes_ = np.array([1])

        def predict_proba(self, _rows):
            return [[object()]]

    monkeypatch.setattr(
        prediccion_service,
        "load_model_artifact",
        lambda _model_path=None: {
            "model": _SingleClassNumpyModel(),
            "features": ["temperatura", "humedad", "vib_x", "vib_y", "vib_z"],
            "target": "riesgo",
            "model_params": {"n_estimators": 120, "random_state": 42},
        },
    )

    result = prediccion_service.execute_prediction(db_session, equipo_id)

    assert result.probabilidad == 1.0
    assert result.clasificacion == "falla"


def test_execute_prediction_rejects_multiclass_models(db_session, monkeypatch):
    """Valida 500 cuando el modelo devuelve probabilidades no binarias."""

    equipo_id = _create_equipo(db_session)
    _create_lectura(
        db_session,
        equipo_id=equipo_id,
        temperatura=49.0,
        timestamp=datetime.now(timezone.utc),
    )

    class _MultiClassModel:
        classes_ = np.array([0, 1, 2])

        def predict_proba(self, _rows):
            return [[0.2, 0.3, 0.5]]

    monkeypatch.setattr(
        prediccion_service,
        "load_model_artifact",
        lambda _model_path=None: {
            "model": _MultiClassModel(),
            "features": ["temperatura", "humedad", "vib_x", "vib_y", "vib_z"],
            "target": "riesgo",
            "model_params": {"n_estimators": 120, "random_state": 42},
        },
    )

    with pytest.raises(HTTPException) as exc_info:
        prediccion_service.execute_prediction(db_session, equipo_id)

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Modelo de inferencia no binario no soportado"


def test_execute_prediction_falls_back_to_predict_when_model_has_no_predict_proba(
    db_session, monkeypatch
):
    """Valida compatibilidad con modelos que sólo implementan predict."""

    equipo_id = _create_equipo(db_session)
    _create_lectura(
        db_session,
        equipo_id=equipo_id,
        temperatura=49.0,
        timestamp=datetime.now(timezone.utc),
    )

    class _PredictOnlyModel:
        def predict(self, _rows):
            return np.array([1])

    monkeypatch.setattr(
        prediccion_service,
        "load_model_artifact_cached",
        lambda _model_path=None: {
            "model": _PredictOnlyModel(),
            "features": ["temperatura", "humedad", "vib_x", "vib_y", "vib_z"],
            "target": "riesgo",
            "model_params": {"n_estimators": 120, "random_state": 42},
        },
    )

    result = prediccion_service.execute_prediction(db_session, equipo_id)

    assert result.probabilidad == 1.0
    assert result.clasificacion == "falla"
