"""Tests de parsing y persistencia del servicio MQTT."""

import json
from collections.abc import Generator

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models  # noqa: F401
from app.database import Base
from app.models.equipo import Equipo
from app.models.lectura import Lectura
from app.services.mqtt_service import (
    extract_equipo_id,
    parse_message,
    process_mqtt_message,
)


@pytest.fixture
def session_factory() -> Generator[sessionmaker, None, None]:
    """Entrega un session factory aislado para pruebas de servicio MQTT."""

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
    yield testing_session_local
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def _create_equipo(session_factory: sessionmaker, nombre: str = "Equipo MQTT") -> int:
    """Crea un equipo auxiliar para validar FK de lecturas."""

    db = session_factory()
    try:
        equipo = Equipo(
            nombre=nombre,
            ubicacion="Laboratorio",
            tipo="Motor",
            estado="operativo",
        )
        db.add(equipo)
        db.commit()
        db.refresh(equipo)
        return equipo.id
    finally:
        db.close()


def test_extract_equipo_id_from_valid_topic():
    """Valida extracción de equipo_id cuando el topic es válido."""

    equipo_id = extract_equipo_id("manttoai/equipo/7/lecturas")
    assert equipo_id == 7


def test_extract_equipo_id_rejects_invalid_topic():
    """Valida rechazo cuando el topic no cumple formato esperado."""

    with pytest.raises(ValueError, match="Topic MQTT inválido"):
        extract_equipo_id("manttoai/equipo/x/lecturas")


def test_parse_message_rejects_invalid_json():
    """Valida que parse_message rechace JSON inválido."""

    with pytest.raises(ValueError, match="Payload MQTT no es JSON válido"):
        parse_message("{invalido")


def test_process_mqtt_message_persists_lectura(session_factory: sessionmaker):
    """Valida persistencia en DB cuando llega mensaje MQTT válido."""

    equipo_id = _create_equipo(session_factory)
    payload = {
        "temperatura": 44.2,
        "humedad": 57.4,
        "vib_x": 0.33,
        "vib_y": 0.22,
        "vib_z": 9.81,
    }

    processed = process_mqtt_message(
        topic=f"manttoai/equipo/{equipo_id}/lecturas",
        payload=json.dumps(payload).encode("utf-8"),
        session_factory=session_factory,
    )

    assert processed is True

    db = session_factory()
    try:
        lectura = db.scalars(select(Lectura)).first()
        assert lectura is not None
        assert lectura.equipo_id == equipo_id
        assert lectura.temperatura == 44.2
    finally:
        db.close()


def test_process_mqtt_message_invalid_payload_does_not_break_loop(
    session_factory: sessionmaker,
):
    """Valida que payload inválido no rompa el proceso de ingesta."""

    equipo_id = _create_equipo(session_factory)

    processed = process_mqtt_message(
        topic=f"manttoai/equipo/{equipo_id}/lecturas",
        payload=b"{json_invalido",
        session_factory=session_factory,
    )

    assert processed is False

    db = session_factory()
    try:
        total_lecturas = len(list(db.scalars(select(Lectura))))
        assert total_lecturas == 0
    finally:
        db.close()
