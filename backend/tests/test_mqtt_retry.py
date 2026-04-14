"""
Tests de tolerancia a fallos del MQTT service con reintentos automáticos (RNF-17).

Valida que _persist_lectura_with_retry reintenta ante OperationalError de DB
y descarta correctamente ante errores de negocio o agotamiento de reintentos.
"""

from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models  # noqa: F401
from app.database import Base
from app.models.equipo import Equipo
from app.schemas.lectura import LecturaMqttPayload
from app.services.mqtt_service import (
    _persist_lectura_with_retry,
    process_mqtt_message,
)


@pytest.fixture
def session_factory_sqlite() -> Generator[sessionmaker, None, None]:
    """Session factory SQLite en memoria para tests de retry MQTT."""

    engine = create_engine(
        "sqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    Base.metadata.create_all(bind=engine)
    yield factory
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def _crear_equipo(session_factory: sessionmaker) -> int:
    """Crea un equipo auxiliar y retorna su ID."""

    db = session_factory()
    try:
        equipo = Equipo(
            nombre="Equipo Retry Test",
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


def _build_lectura_payload(temperatura: float = 45.0) -> LecturaMqttPayload:
    """Construye un payload de lectura válido para tests."""

    return LecturaMqttPayload(
        temperatura=temperatura,
        humedad=60.0,
        vib_x=0.3,
        vib_y=0.1,
        vib_z=9.8,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Tests de _persist_lectura_with_retry
# ─────────────────────────────────────────────────────────────────────────────


class TestPersistLecturaWithRetry:
    """Valida la lógica de reintentos ante fallos de DB (RNF-17)."""

    def test_persiste_exitosamente_en_primer_intento(
        self, session_factory_sqlite: sessionmaker
    ) -> None:
        """RNF-17: Sin errores de DB, persiste en el primer intento."""
        equipo_id = _crear_equipo(session_factory_sqlite)
        payload = _build_lectura_payload()

        resultado = _persist_lectura_with_retry(
            topic=f"manttoai/equipo/{equipo_id}/lecturas",
            equipo_id=equipo_id,
            lectura_payload=payload,
            session_factory=session_factory_sqlite,
            max_attempts=3,
            backoff_seconds=0.0,
        )

        assert resultado is True

    def test_reintenta_ante_operational_error_y_tiene_exito(
        self, session_factory_sqlite: sessionmaker
    ) -> None:
        """
        RNF-17: Si la DB falla con OperationalError en el primer intento
        pero se recupera en el segundo, debe persistir exitosamente.
        """
        equipo_id = _crear_equipo(session_factory_sqlite)
        payload = _build_lectura_payload()
        topic = f"manttoai/equipo/{equipo_id}/lecturas"

        llamadas = {"count": 0}
        original_factory = session_factory_sqlite

        def factory_con_fallo_inicial():
            """Falla en el primer intento, funciona en los siguientes."""
            llamadas["count"] += 1
            if llamadas["count"] == 1:
                raise OperationalError("DB no disponible", None, None)
            return original_factory()

        with patch(
            "app.services.mqtt_service.create_lectura_from_mqtt_payload"
        ) as mock_create:
            # Primer intento: OperationalError; segundo: éxito
            mock_create.side_effect = [
                OperationalError("DB no disponible", None, None),
                MagicMock(id=1, timestamp="2026-04-13T00:00:00"),
            ]

            resultado = _persist_lectura_with_retry(
                topic=topic,
                equipo_id=equipo_id,
                lectura_payload=payload,
                session_factory=session_factory_sqlite,
                max_attempts=3,
                backoff_seconds=0.0,  # Sin espera en tests
            )

        assert resultado is True
        assert mock_create.call_count == 2

    def test_descarta_tras_agotar_reintentos(
        self, session_factory_sqlite: sessionmaker
    ) -> None:
        """
        RNF-17: Si la DB falla en todos los intentos, debe retornar False
        y no propagar la excepción.
        """
        equipo_id = _crear_equipo(session_factory_sqlite)
        payload = _build_lectura_payload()
        topic = f"manttoai/equipo/{equipo_id}/lecturas"

        with patch(
            "app.services.mqtt_service.create_lectura_from_mqtt_payload"
        ) as mock_create:
            mock_create.side_effect = OperationalError("DB caída", None, None)

            resultado = _persist_lectura_with_retry(
                topic=topic,
                equipo_id=equipo_id,
                lectura_payload=payload,
                session_factory=session_factory_sqlite,
                max_attempts=3,
                backoff_seconds=0.0,
            )

        assert resultado is False
        assert mock_create.call_count == 3  # Intentó 3 veces

    def test_no_reintenta_ante_http_exception(
        self, session_factory_sqlite: sessionmaker
    ) -> None:
        """
        RNF-17: HTTPException (equipo no existe, etc.) no debe reintentarse —
        es un error de negocio, no un fallo transitorio de DB.
        """
        from fastapi import HTTPException

        payload = _build_lectura_payload()
        topic = "manttoai/equipo/99999/lecturas"

        with patch(
            "app.services.mqtt_service.create_lectura_from_mqtt_payload"
        ) as mock_create:
            mock_create.side_effect = HTTPException(
                status_code=404, detail="Equipo no encontrado"
            )

            resultado = _persist_lectura_with_retry(
                topic=topic,
                equipo_id=99999,
                lectura_payload=payload,
                session_factory=session_factory_sqlite,
                max_attempts=3,
                backoff_seconds=0.0,
            )

        assert resultado is False
        assert mock_create.call_count == 1  # Solo intentó una vez

    def test_process_mqtt_message_usa_retry_internamente(
        self, session_factory_sqlite: sessionmaker
    ) -> None:
        """
        RNF-17: process_mqtt_message debe delegar en _persist_lectura_with_retry,
        garantizando que el retry está activo en el pipeline completo.
        """
        equipo_id = _crear_equipo(session_factory_sqlite)
        topic = f"manttoai/equipo/{equipo_id}/lecturas"
        payload = (
            '{"temperatura": 50.0, "humedad": 55.0, '
            '"vib_x": 0.2, "vib_y": 0.1, "vib_z": 9.7}'
        )

        with patch(
            "app.services.mqtt_service._persist_lectura_with_retry"
        ) as mock_retry:
            mock_retry.return_value = True

            resultado = process_mqtt_message(
                topic, payload, session_factory=session_factory_sqlite
            )

        assert resultado is True
        assert mock_retry.call_count == 1
        # Verificar que se pasaron los argumentos correctos
        call_kwargs = mock_retry.call_args
        assert call_kwargs.kwargs["equipo_id"] == equipo_id
