"""Tests de scheduler periódico de predicciones."""

from collections.abc import Generator
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app import models  # noqa: F401
from app.database import Base
from app.models.equipo import Equipo
from app.models.lectura import Lectura
from app.models.prediccion import Prediccion
from app.services import prediccion_scheduler_service, prediccion_service


@pytest.fixture(autouse=True)
def ensure_scheduler_stopped() -> Generator[None, None, None]:
    """Asegura aislamiento deteniendo el scheduler antes y después de cada test."""

    prediccion_scheduler_service.stop_prediction_scheduler()
    yield
    prediccion_scheduler_service.stop_prediction_scheduler()


@pytest.fixture
def db_context() -> Generator[tuple[Session, sessionmaker], None, None]:
    """Entrega sesión SQLite y su factory para pruebas del scheduler."""

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
        yield session, testing_session_local
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def _create_equipo(
    db_session: Session,
    nombre: str,
    estado: str = "operativo",
) -> int:
    """Crea equipo de prueba con estado controlado."""

    equipo = Equipo(
        nombre=nombre,
        ubicacion="Laboratorio",
        tipo="Motor",
        estado=estado,
    )
    db_session.add(equipo)
    db_session.commit()
    db_session.refresh(equipo)
    return equipo.id


def _create_lectura(
    db_session: Session, equipo_id: int, temperatura: float = 47.0
) -> None:
    """Crea lectura persistida para habilitar inferencia."""

    lectura = Lectura(
        equipo_id=equipo_id,
        temperatura=temperatura,
        humedad=57.0,
        vib_x=0.33,
        vib_y=0.21,
        vib_z=9.8,
        timestamp=datetime.now(timezone.utc),
    )
    db_session.add(lectura)
    db_session.commit()


class _FakeModel:
    """Modelo mock para predecir una probabilidad fija."""

    def __init__(self, probability: float):
        self.probability = probability

    def predict_proba(self, _rows):
        return [[1.0 - self.probability, self.probability]]


def _mock_model_loader(probability: float):
    """Entrega un loader mockeado con modelo determinista."""

    model = _FakeModel(probability)
    return lambda _model_path=None: {
        "model": model,
        "features": ["temperatura", "humedad", "vib_x", "vib_y", "vib_z"],
        "target": "riesgo",
        "model_params": {"n_estimators": 120, "random_state": 42},
    }


def test_run_periodic_predictions_processes_only_active_equipos(
    db_context,
    monkeypatch,
):
    """Valida que el job periódico procese solo equipos activos."""

    db_session, session_factory = db_context
    equipo_operativo = _create_equipo(db_session, "Compresor A", estado="operativo")
    equipo_activo = _create_equipo(db_session, "Compresor B", estado="activo")
    _create_equipo(db_session, "Compresor C", estado="inactivo")

    _create_lectura(db_session, equipo_operativo, temperatura=46.0)
    _create_lectura(db_session, equipo_activo, temperatura=48.0)

    monkeypatch.setattr(
        prediccion_service,
        "load_model_artifact",
        _mock_model_loader(0.73),
    )

    summary = prediccion_scheduler_service.run_periodic_predictions(
        session_factory=session_factory,
    )

    assert summary["equipos_activos"] == 2
    assert summary["predicciones_ok"] == 2
    assert summary["predicciones_error"] == 0

    verification_db = session_factory()
    try:
        predicciones = list(verification_db.scalars(select(Prediccion)))
    finally:
        verification_db.close()

    assert len(predicciones) == 2
    assert {pred.equipo_id for pred in predicciones} == {
        equipo_operativo,
        equipo_activo,
    }


def test_run_periodic_predictions_continues_when_one_equipo_fails(
    db_context,
    monkeypatch,
):
    """Valida que un error por equipo no detenga la ejecución completa."""

    db_session, session_factory = db_context
    equipo_sin_lectura = _create_equipo(
        db_session, "Bomba sin lectura", estado="operativo"
    )
    equipo_con_lectura = _create_equipo(
        db_session, "Bomba con lectura", estado="operativo"
    )
    _create_lectura(db_session, equipo_con_lectura, temperatura=50.0)

    monkeypatch.setattr(
        prediccion_service,
        "load_model_artifact",
        _mock_model_loader(0.61),
    )

    summary = prediccion_scheduler_service.run_periodic_predictions(
        session_factory=session_factory,
    )

    assert summary["equipos_activos"] == 2
    assert summary["predicciones_ok"] == 1
    assert summary["predicciones_error"] == 1

    verification_db = session_factory()
    try:
        predicciones = list(verification_db.scalars(select(Prediccion)))
    finally:
        verification_db.close()

    assert len(predicciones) == 1
    assert predicciones[0].equipo_id == equipo_con_lectura
    assert predicciones[0].equipo_id != equipo_sin_lectura


def test_start_prediction_scheduler_returns_false_when_disabled(monkeypatch):
    """Valida que el scheduler pueda desactivarse por configuración."""

    monkeypatch.setattr(
        prediccion_scheduler_service,
        "get_settings",
        lambda: SimpleNamespace(
            enable_prediction_scheduler=False,
            prediction_interval_seconds=30,
        ),
    )

    started = prediccion_scheduler_service.start_prediction_scheduler()

    assert started is False
    assert prediccion_scheduler_service.is_prediction_scheduler_running() is False


def test_start_prediction_scheduler_registers_interval_job(monkeypatch):
    """Valida creación de job interval y apagado controlado del scheduler."""

    created_schedulers = []

    class _FakeBackgroundScheduler:
        def __init__(self, timezone):
            self.timezone = timezone
            self.jobs = []
            self.started = False
            self.running = False
            self.stopped = False
            created_schedulers.append(self)

        def add_job(self, func, trigger, **kwargs):
            self.jobs.append({"func": func, "trigger": trigger, **kwargs})

        def start(self):
            self.started = True
            self.running = True

        def shutdown(self, wait=False):
            self.stopped = True
            self.running = False

    class _FakeSession:
        def close(self):
            return None

    monkeypatch.setattr(
        prediccion_scheduler_service,
        "BackgroundScheduler",
        _FakeBackgroundScheduler,
    )
    monkeypatch.setattr(
        prediccion_scheduler_service,
        "get_settings",
        lambda: SimpleNamespace(
            enable_prediction_scheduler=True,
            prediction_interval_seconds=45,
        ),
    )

    def session_factory():
        return _FakeSession()

    started = prediccion_scheduler_service.start_prediction_scheduler(
        session_factory=session_factory,
    )

    assert started is True
    assert prediccion_scheduler_service.is_prediction_scheduler_running() is True
    assert len(created_schedulers) == 1
    assert created_schedulers[0].started is True
    assert len(created_schedulers[0].jobs) == 1
    assert created_schedulers[0].jobs[0]["trigger"] == "interval"
    assert created_schedulers[0].jobs[0]["seconds"] == 45
    assert created_schedulers[0].jobs[0]["kwargs"]["session_factory"] is session_factory

    prediccion_scheduler_service.stop_prediction_scheduler()

    assert created_schedulers[0].stopped is True
    assert prediccion_scheduler_service.is_prediction_scheduler_running() is False


def test_start_prediction_scheduler_returns_false_with_invalid_session_factory(
    monkeypatch,
):
    """Valida que el scheduler no arranque con SessionFactory inválido."""

    class _FakeBackgroundScheduler:
        def __init__(self, _timezone):
            self.started = False

        def add_job(self, _func, _trigger, **_kwargs):
            return None

        def start(self):
            self.started = True

        def shutdown(self, wait=False):
            return None

    monkeypatch.setattr(
        prediccion_scheduler_service,
        "BackgroundScheduler",
        _FakeBackgroundScheduler,
    )
    monkeypatch.setattr(
        prediccion_scheduler_service,
        "get_settings",
        lambda: SimpleNamespace(
            enable_prediction_scheduler=True,
            prediction_interval_seconds=45,
        ),
    )

    def invalid_session_factory():
        return None

    started = prediccion_scheduler_service.start_prediction_scheduler(
        session_factory=invalid_session_factory,
    )

    assert started is False
    assert prediccion_scheduler_service.is_prediction_scheduler_running() is False


def test_start_prediction_scheduler_returns_false_when_apscheduler_missing(
    monkeypatch,
):
    """Valida fallback cuando APScheduler no está disponible."""

    monkeypatch.setattr(
        prediccion_scheduler_service,
        "BackgroundScheduler",
        None,
    )
    monkeypatch.setattr(
        prediccion_scheduler_service,
        "get_settings",
        lambda: SimpleNamespace(
            enable_prediction_scheduler=True,
            prediction_interval_seconds=45,
        ),
    )

    started = prediccion_scheduler_service.start_prediction_scheduler()

    assert started is False
    assert prediccion_scheduler_service.is_prediction_scheduler_running() is False
