"""Tests unitarios para lógica de negocio de lectura_service."""

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from fastapi import BackgroundTasks

from app.models.equipo import Equipo
from app.models.lectura import Lectura
from app.schemas.lectura import LecturaCreate, LecturaMqttPayload
from app.services import lectura_service


def _crear_equipo(db, nombre: str = "Equipo Servicio Lecturas") -> Equipo:
    """Crea y persiste un equipo auxiliar para pruebas unitarias."""

    equipo = Equipo(
        nombre=nombre,
        ubicacion="Laboratorio",
        tipo="Motor",
        estado="operativo",
        rubro="industrial",
    )
    db.add(equipo)
    db.commit()
    db.refresh(equipo)
    return equipo


def test_list_lecturas_returns_all_when_limit_is_none(db):
    """Valida que list_lecturas retorne todos los registros cuando limit=None."""

    equipo = _crear_equipo(db)
    now = datetime.now(timezone.utc)

    lecturas = [
        Lectura(
            equipo_id=equipo.id,
            temperatura=40.0 + idx,
            humedad=55.0,
            vib_x=0.3,
            vib_y=0.2,
            vib_z=9.8,
            timestamp=now + timedelta(minutes=idx),
        )
        for idx in range(3)
    ]
    db.add_all(lecturas)
    db.commit()

    resultado = lectura_service.list_lecturas(db, equipo_id=equipo.id, limit=None)

    assert len(resultado) == 3
    assert [item.temperatura for item in resultado] == [42.0, 41.0, 40.0]


def test_create_lectura_enqueues_background_notification_for_critical_alerts(
    db, monkeypatch
):
    """Valida encolado de notificaciones cuando hay alertas críticas."""

    equipo = _crear_equipo(db)
    payload = LecturaCreate(
        equipo_id=equipo.id,
        temperatura=65.0,
        humedad=58.0,
        vib_x=0.4,
        vib_y=0.2,
        vib_z=9.7,
    )
    background_tasks = BackgroundTasks()

    monkeypatch.setattr(
        lectura_service,
        "evaluate_thresholds",
        lambda _db, _lectura: [SimpleNamespace(id=101, nivel="alto")],
    )

    lectura = lectura_service.create_lectura(
        db,
        payload,
        background_tasks=background_tasks,
        session_factory=lambda: None,
    )

    assert lectura.id is not None
    assert len(background_tasks.tasks) == 1
    task = background_tasks.tasks[0]
    assert task.args[0] == [101]


def test_create_lectura_logs_error_when_sync_notification_dispatch_fails(
    db, monkeypatch
):
    """Valida fallback robusto cuando falla el despacho SMTP sin BackgroundTasks."""

    import smtplib

    equipo = _crear_equipo(db)
    payload = LecturaCreate(
        equipo_id=equipo.id,
        temperatura=62.0,
        humedad=60.0,
        vib_x=0.3,
        vib_y=0.2,
        vib_z=9.8,
    )
    log_calls: list[str] = []

    monkeypatch.setattr(
        lectura_service,
        "evaluate_thresholds",
        lambda _db, _lectura: [SimpleNamespace(id=202, nivel="alto")],
    )

    def _raise_dispatch_error(_db, _alertas):
        raise smtplib.SMTPException("smtp down")

    monkeypatch.setattr(
        lectura_service,
        "dispatch_critical_email_notifications",
        _raise_dispatch_error,
    )
    monkeypatch.setattr(
        lectura_service.logger,
        "exception",
        lambda message, *_args: log_calls.append(message),
    )

    lectura = lectura_service.create_lectura(db, payload)

    assert lectura.id is not None
    assert any("No se pudo despachar notificación crítica" in msg for msg in log_calls)


def test_create_lectura_from_mqtt_payload_transforms_payload_before_persisting(
    db, monkeypatch
):
    """Valida mapeo de payload MQTT a LecturaCreate antes de persistencia."""

    captured: dict[str, object] = {}
    mqtt_payload = LecturaMqttPayload(
        temperatura=48.2,
        humedad=51.0,
        vib_x=0.22,
        vib_y=0.18,
        vib_z=9.6,
    )

    def _fake_create_lectura(
        _db,
        payload,
        background_tasks=None,
        session_factory=None,
    ):
        captured["payload"] = payload
        captured["background_tasks"] = background_tasks
        captured["session_factory"] = session_factory
        return "lectura-persistida"

    monkeypatch.setattr(lectura_service, "create_lectura", _fake_create_lectura)

    result = lectura_service.create_lectura_from_mqtt_payload(
        db,
        equipo_id=99,
        payload=mqtt_payload,
    )

    assert result == "lectura-persistida"
    assert captured["payload"].equipo_id == 99
    assert captured["payload"].temperatura == 48.2
