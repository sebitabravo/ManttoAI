"""Tests de parsing y persistencia del servicio MQTT."""

import json
from types import SimpleNamespace
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
    extract_mac_address,
    parse_message,
    process_mqtt_message,
    start_mqtt_subscriber,
    stop_mqtt_subscriber,
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


def _create_equipo(session_factory: sessionmaker, nombre: str = "Equipo MQTT", mac_address: str = "00:1A:2B:3C:4D:5E") -> int:
    """Crea un equipo auxiliar para validar FK de lecturas."""

    db = session_factory()
    try:
        equipo = Equipo(
            nombre=nombre,
            ubicacion="Laboratorio",
            tipo="Motor",
            estado="operativo",
            mac_address=mac_address,
        )
        db.add(equipo)
        db.commit()
        db.refresh(equipo)
        return equipo.id
    finally:
        db.close()


def test_extract_mac_address_from_valid_topic():
    """Valida extracción de equipo_id cuando el topic es válido."""

    mac_address = extract_mac_address("manttoai/telemetria/00:1A:2B:3C:4D:5E")
    assert mac_address == "00:1A:2B:3C:4D:5E"


def test_extract_mac_address_rejects_invalid_topic():
    """Valida rechazo cuando el topic no cumple formato esperado."""

    with pytest.raises(ValueError, match="Topic MQTT inválido"):
        extract_mac_address("manttoai/equipo/x/lecturas")


def test_parse_message_rejects_invalid_json():
    """Valida que parse_message rechace JSON inválido."""

    with pytest.raises(ValueError, match="Payload MQTT no es JSON válido"):
        parse_message("{invalido")


def test_process_mqtt_message_persists_lectura(session_factory: sessionmaker):
    """Valida persistencia en DB cuando llega mensaje MQTT válido."""

    equipo_id = _create_equipo(session_factory, mac_address="00:1A:2B:3C:4D:5E")
    payload = {
        "temperatura": 44.2,
        "humedad": 57.4,
        "vib_x": 0.33,
        "vib_y": 0.22,
        "vib_z": 9.81,
    }

    processed = process_mqtt_message(
        topic=f"manttoai/telemetria/00:1A:2B:3C:4D:5E",
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

    equipo_id = _create_equipo(session_factory, mac_address="00:1A:2B:3C:4D:5E")

    processed = process_mqtt_message(
        topic=f"manttoai/telemetria/00:1A:2B:3C:4D:5E",
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


class _DummyMqttClient:
    """Cliente MQTT de prueba para validar autenticación configurada."""

    def __init__(self, *_args, **_kwargs):
        self.auth_calls: list[tuple[str, str]] = []
        self.userdata = None
        self.on_connect = None
        self.on_message = None
        self.loop_started = False

    def username_pw_set(self, username: str, password: str) -> None:
        self.auth_calls.append((username, password))

    def user_data_set(self, userdata) -> None:
        self.userdata = userdata

    def connect(self, _host: str, _port: int) -> None:
        return None

    def loop_start(self) -> None:
        self.loop_started = True

    def loop_stop(self) -> None:
        self.loop_started = False

    def disconnect(self) -> None:
        return None


def test_start_mqtt_subscriber_sets_auth_when_username_is_configured(monkeypatch):
    """Valida que el subscriber configure auth MQTT cuando hay usuario."""

    dummy_client = _DummyMqttClient()
    mqtt_stub = SimpleNamespace(
        CallbackAPIVersion=SimpleNamespace(VERSION2=object()),
        Client=lambda *_args, **_kwargs: dummy_client,
    )
    settings_stub = SimpleNamespace(
        mqtt_broker_host="mosquitto",
        mqtt_broker_port=1883,
        mqtt_username="manttoai_mqtt",
        mqtt_password="manttoai_mqtt_dev",
    )

    import app.services.mqtt_service as mqtt_service

    stop_mqtt_subscriber()
    monkeypatch.setattr(mqtt_service, "mqtt", mqtt_stub)
    monkeypatch.setattr(mqtt_service, "get_settings", lambda: settings_stub)

    started = start_mqtt_subscriber()
    assert started is True
    assert dummy_client.auth_calls == [("manttoai_mqtt", "manttoai_mqtt_dev")]
    assert dummy_client.loop_started is True

    stop_mqtt_subscriber()


def test_start_mqtt_subscriber_skips_auth_when_username_is_empty(monkeypatch):
    """Valida que el subscriber no configure auth si no hay usuario."""

    dummy_client = _DummyMqttClient()
    mqtt_stub = SimpleNamespace(
        CallbackAPIVersion=SimpleNamespace(VERSION2=object()),
        Client=lambda *_args, **_kwargs: dummy_client,
    )
    settings_stub = SimpleNamespace(
        mqtt_broker_host="mosquitto",
        mqtt_broker_port=1883,
        mqtt_username="",
        mqtt_password="",
    )

    import app.services.mqtt_service as mqtt_service

    stop_mqtt_subscriber()
    monkeypatch.setattr(mqtt_service, "mqtt", mqtt_stub)
    monkeypatch.setattr(mqtt_service, "get_settings", lambda: settings_stub)

    started = start_mqtt_subscriber()
    assert started is True
    assert dummy_client.auth_calls == []

    stop_mqtt_subscriber()
