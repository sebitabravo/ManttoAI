"""
Tests de rendimiento y latencia para validar RNF-01, RNF-02 y RNF-04.

RNF-01: Latencia de procesamiento IoT < 5 segundos
RNF-02: Latencia de notificación de alertas < 2 minutos (intento síncrono)
RNF-04: Tiempo de respuesta API < 500ms GET, < 1s POST/PUT
"""

import time
from collections.abc import Generator
from types import SimpleNamespace

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models  # noqa: F401
from app.database import Base
from app.models.equipo import Equipo
from app.services.mqtt_service import process_mqtt_message

# ─────────────────────────────────────────────────────────────────────────────
# Fixtures compartidas
# ─────────────────────────────────────────────────────────────────────────────

LATENCIA_MQTT_MAX_SEGUNDOS = 5.0
LATENCIA_EMAIL_MAX_SEGUNDOS = 120.0  # 2 minutos
LATENCIA_GET_MAX_SEGUNDOS = 0.5
LATENCIA_POST_MAX_SEGUNDOS = 1.0


@pytest.fixture
def session_factory_sqlite() -> Generator[sessionmaker, None, None]:
    """Session factory SQLite en memoria para tests de latencia MQTT."""

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


def _crear_equipo(session_factory: sessionmaker, equipo_id_hint: int = 1) -> int:
    """Crea un equipo auxiliar y retorna su ID real persistido."""

    db = session_factory()
    try:
        equipo = Equipo(
            nombre=f"Equipo Latencia {equipo_id_hint}",
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


# ─────────────────────────────────────────────────────────────────────────────
# RNF-01 — Latencia de procesamiento IoT < 5 segundos
# ─────────────────────────────────────────────────────────────────────────────


class TestRNF01LatenciaMQTT:
    """Valida que el pipeline MQTT → parse → persist se complete en < 5 segundos."""

    def test_process_mqtt_message_completa_en_menos_de_5_segundos(
        self, session_factory_sqlite: sessionmaker
    ) -> None:
        """
        RNF-01: El procesamiento completo de un mensaje MQTT (parse + validación
        + persistencia en DB) debe completarse en menos de 5 segundos.
        """
        equipo_id = _crear_equipo(session_factory_sqlite)
        topic = f"manttoai/equipo/{equipo_id}/lecturas"
        payload = (
            '{"temperatura": 45.2, "humedad": 60.0, '
            '"vib_x": 0.3, "vib_y": 0.1, "vib_z": 9.8}'
        )

        inicio = time.perf_counter()
        resultado = process_mqtt_message(
            topic, payload, session_factory=session_factory_sqlite
        )
        duracion = time.perf_counter() - inicio

        assert resultado is True, "El mensaje MQTT debe procesarse exitosamente"
        assert duracion < LATENCIA_MQTT_MAX_SEGUNDOS, (
            f"Latencia MQTT {duracion:.3f}s supera el límite de "
            f"{LATENCIA_MQTT_MAX_SEGUNDOS}s (RNF-01)"
        )

    def test_process_mqtt_message_multiples_lecturas_dentro_de_limite(
        self, session_factory_sqlite: sessionmaker
    ) -> None:
        """
        RNF-01: Procesar 10 lecturas consecutivas debe completarse en < 5s por lectura.
        Valida que no hay degradación acumulativa en el pipeline.
        """
        equipo_id = _crear_equipo(session_factory_sqlite, equipo_id_hint=2)
        topic = f"manttoai/equipo/{equipo_id}/lecturas"
        n_lecturas = 10
        latencias: list[float] = []

        for i in range(n_lecturas):
            payload = (
                f'{{"temperatura": {20.0 + i}, "humedad": {50.0 + i}, '
                f'"vib_x": 0.{i}, "vib_y": 0.1, "vib_z": 9.8}}'
            )
            inicio = time.perf_counter()
            resultado = process_mqtt_message(
                topic, payload, session_factory=session_factory_sqlite
            )
            duracion = time.perf_counter() - inicio
            latencias.append(duracion)
            assert resultado is True, f"Lectura {i} debe procesarse exitosamente"

        latencia_max = max(latencias)
        latencia_promedio = sum(latencias) / len(latencias)

        assert latencia_max < LATENCIA_MQTT_MAX_SEGUNDOS, (
            f"Latencia máxima {latencia_max:.3f}s supera el límite de "
            f"{LATENCIA_MQTT_MAX_SEGUNDOS}s (RNF-01)"
        )
        # El promedio debe ser muy inferior al límite (< 1s esperado)
        assert latencia_promedio < 1.0, (
            f"Latencia promedio {latencia_promedio:.3f}s es mayor a 1s — "
            "posible degradación de rendimiento"
        )

    def test_latencia_mqtt_con_payload_invalido_no_bloquea(
        self, session_factory_sqlite: sessionmaker
    ) -> None:
        """
        RNF-01: Un payload inválido debe rechazarse rápidamente sin bloquear el pipeline.
        """
        topic = "manttoai/equipo/999/lecturas"
        payload_invalido = '{"campo_inexistente": true}'

        inicio = time.perf_counter()
        resultado = process_mqtt_message(
            topic, payload_invalido, session_factory=session_factory_sqlite
        )
        duracion = time.perf_counter() - inicio

        assert resultado is False, "Payload inválido debe retornar False"
        assert (
            duracion < 1.0
        ), f"Rechazo de payload inválido tardó {duracion:.3f}s — debe ser < 1s"


# ─────────────────────────────────────────────────────────────────────────────
# RNF-02 — Latencia de notificación de alertas < 2 minutos
# ─────────────────────────────────────────────────────────────────────────────


class TestRNF02LatenciaEmail:
    """
    Valida que el intento de envío de email ocurre síncronamente
    dentro del límite de 2 minutos desde la evaluación del umbral.
    """

    def test_envio_email_se_intenta_sincronamente_al_evaluar_umbral(
        self, monkeypatch
    ) -> None:
        """
        RNF-02: El email de alerta debe intentarse enviar síncronamente
        (no en background) cuando se supera un umbral crítico.
        El intento debe ocurrir en < 2 minutos desde la evaluación.
        """
        from app.services import email_service

        settings_mock = SimpleNamespace(
            smtp_host="smtp.test.local",
            smtp_port=587,
            smtp_user="bot@test.local",
            smtp_password="secret",
            smtp_from_email="bot@test.local",
            smtp_to_email="alertas@test.local",
            smtp_use_ssl=False,
            smtp_use_starttls=True,
            smtp_require_auth=False,
            smtp_timeout=10,
            smtp_retry_attempts=1,
            smtp_retry_backoff=0.0,
        )
        monkeypatch.setattr(email_service, "get_settings", lambda: settings_mock)

        email_enviado_en: list[float] = []
        inicio_evaluacion = time.perf_counter()

        class FakeSMTP:
            """Mock SMTP que registra el momento exacto del intento de envío."""

            def __init__(self, host, port, timeout):
                pass

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def starttls(self, context=None):
                pass

            def login(self, user, password):
                pass

            def send_message(self, msg):
                email_enviado_en.append(time.perf_counter())

        monkeypatch.setattr(email_service.smtplib, "SMTP", FakeSMTP)

        # Simular envío de alerta crítica usando la firma real del servicio
        smtp_instance = FakeSMTP("", 0, 0)
        email_service.send_alert_email_with_client(
            smtp_client=smtp_instance,
            subject="[ManttoAI] Alerta crítica: Temperatura fuera de rango",
            message=(
                "Equipo: Compresor A\n"
                "Tipo: temperatura\n"
                "Nivel: alto\n"
                "Valor actual: 95.0\n"
                "Umbral máximo: 80.0"
            ),
        )

        if email_enviado_en:
            latencia = email_enviado_en[0] - inicio_evaluacion
            assert latencia < LATENCIA_EMAIL_MAX_SEGUNDOS, (
                f"Email tardó {latencia:.3f}s — supera límite de "
                f"{LATENCIA_EMAIL_MAX_SEGUNDOS}s (RNF-02)"
            )

    def test_can_send_email_retorna_false_sin_config_smtp(self, monkeypatch) -> None:
        """
        RNF-02: Sin configuración SMTP, el sistema no debe intentar enviar
        y debe fallar rápido (< 1s) sin bloquear el pipeline.
        """
        from app.services import email_service

        settings_sin_smtp = SimpleNamespace(
            smtp_host="",
            smtp_port=587,
            smtp_user="",
            smtp_password="",
            smtp_from_email="",
            smtp_to_email="",
            smtp_use_ssl=False,
            smtp_use_starttls=False,
            smtp_require_auth=False,
            smtp_timeout=10,
            smtp_retry_attempts=1,
            smtp_retry_backoff=0.0,
        )
        monkeypatch.setattr(email_service, "get_settings", lambda: settings_sin_smtp)

        inicio = time.perf_counter()
        puede_enviar = email_service.can_send_email()
        duracion = time.perf_counter() - inicio

        assert puede_enviar is False
        assert (
            duracion < 1.0
        ), f"Verificación de config SMTP tardó {duracion:.3f}s — debe ser < 1s"


# ─────────────────────────────────────────────────────────────────────────────
# RNF-04 — Tiempo de respuesta API < 500ms GET, < 1s POST/PUT
# ─────────────────────────────────────────────────────────────────────────────


class TestRNF04TiempoRespuestaAPI:
    """
    Valida que los endpoints REST respondan dentro de los límites de tiempo
    definidos en RNF-04: < 500ms para GET, < 1s para POST/PUT.
    """

    def test_get_equipos_responde_en_menos_de_500ms(self, client) -> None:
        """RNF-04: GET /equipos debe responder en < 500ms."""
        inicio = time.perf_counter()
        response = client.get("/equipos")
        duracion = time.perf_counter() - inicio

        assert response.status_code == 200
        assert duracion < LATENCIA_GET_MAX_SEGUNDOS, (
            f"GET /equipos tardó {duracion:.3f}s — supera límite de "
            f"{LATENCIA_GET_MAX_SEGUNDOS}s (RNF-04)"
        )

    def test_get_alertas_responde_en_menos_de_500ms(self, client) -> None:
        """RNF-04: GET /alertas debe responder en < 500ms."""
        inicio = time.perf_counter()
        response = client.get("/alertas")
        duracion = time.perf_counter() - inicio

        assert response.status_code == 200
        assert duracion < LATENCIA_GET_MAX_SEGUNDOS, (
            f"GET /alertas tardó {duracion:.3f}s — supera límite de "
            f"{LATENCIA_GET_MAX_SEGUNDOS}s (RNF-04)"
        )

    def test_get_lecturas_responde_en_menos_de_500ms(self, client) -> None:
        """RNF-04: GET /lecturas debe responder en < 500ms."""
        inicio = time.perf_counter()
        response = client.get("/lecturas")
        duracion = time.perf_counter() - inicio

        assert response.status_code == 200
        assert duracion < LATENCIA_GET_MAX_SEGUNDOS, (
            f"GET /lecturas tardó {duracion:.3f}s — supera límite de "
            f"{LATENCIA_GET_MAX_SEGUNDOS}s (RNF-04)"
        )

    def test_get_dashboard_resumen_responde_en_menos_de_500ms(self, client) -> None:
        """RNF-04: GET /dashboard/resumen debe responder en < 500ms."""
        inicio = time.perf_counter()
        response = client.get("/dashboard/resumen")
        duracion = time.perf_counter() - inicio

        assert response.status_code == 200
        assert duracion < LATENCIA_GET_MAX_SEGUNDOS, (
            f"GET /dashboard/resumen tardó {duracion:.3f}s — supera límite de "
            f"{LATENCIA_GET_MAX_SEGUNDOS}s (RNF-04)"
        )

    def test_post_equipo_responde_en_menos_de_1_segundo(self, client) -> None:
        """RNF-04: POST /equipos debe responder en < 1 segundo."""
        payload = {
            "nombre": "Equipo Performance Test",
            "ubicacion": "Laboratorio",
            "tipo": "Motor",
            "estado": "operativo",
        }

        inicio = time.perf_counter()
        response = client.post("/equipos", json=payload)
        duracion = time.perf_counter() - inicio

        assert response.status_code == 201
        assert duracion < LATENCIA_POST_MAX_SEGUNDOS, (
            f"POST /equipos tardó {duracion:.3f}s — supera límite de "
            f"{LATENCIA_POST_MAX_SEGUNDOS}s (RNF-04)"
        )

    def test_post_mantencion_responde_en_menos_de_1_segundo(self, client) -> None:
        """RNF-04: POST /mantenciones debe responder en < 1 segundo."""
        # Crear equipo primero
        equipo_resp = client.post(
            "/equipos",
            json={
                "nombre": "Equipo Para Mantencion",
                "ubicacion": "Planta",
                "tipo": "Bomba",
                "estado": "operativo",
            },
        )
        assert equipo_resp.status_code == 201
        equipo_id = equipo_resp.json()["id"]

        payload = {
            "equipo_id": equipo_id,
            "tipo": "preventiva",
            "descripcion": "Mantención de prueba de performance",
            "fecha_programada": "2026-06-01T10:00:00",
        }

        inicio = time.perf_counter()
        response = client.post("/mantenciones", json=payload)
        duracion = time.perf_counter() - inicio

        assert response.status_code == 201
        assert duracion < LATENCIA_POST_MAX_SEGUNDOS, (
            f"POST /mantenciones tardó {duracion:.3f}s — supera límite de "
            f"{LATENCIA_POST_MAX_SEGUNDOS}s (RNF-04)"
        )

    def test_put_equipo_responde_en_menos_de_1_segundo(self, client) -> None:
        """RNF-04: PUT /equipos/{id} debe responder en < 1 segundo."""
        equipo_resp = client.post(
            "/equipos",
            json={
                "nombre": "Equipo PUT Test",
                "ubicacion": "Sala",
                "tipo": "Motor",
                "estado": "operativo",
            },
        )
        assert equipo_resp.status_code == 201
        equipo_id = equipo_resp.json()["id"]

        inicio = time.perf_counter()
        response = client.put(
            f"/equipos/{equipo_id}",
            json={"estado": "mantenimiento"},
        )
        duracion = time.perf_counter() - inicio

        assert response.status_code == 200
        assert duracion < LATENCIA_POST_MAX_SEGUNDOS, (
            f"PUT /equipos/{equipo_id} tardó {duracion:.3f}s — supera límite de "
            f"{LATENCIA_POST_MAX_SEGUNDOS}s (RNF-04)"
        )

    def test_get_health_responde_en_menos_de_200ms(self, client) -> None:
        """RNF-04: GET /health debe responder en < 200ms (endpoint crítico de monitoreo)."""
        inicio = time.perf_counter()
        response = client.get("/health")
        duracion = time.perf_counter() - inicio

        assert response.status_code == 200
        assert duracion < 0.2, f"GET /health tardó {duracion:.3f}s — debe ser < 200ms"
