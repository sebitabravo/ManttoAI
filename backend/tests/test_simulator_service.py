"""Tests para el servicio de simulación de sensores IoT."""

import random
from unittest.mock import MagicMock, patch

import pytest

from app.services.simulator_service import (
    _get_equipment_profile,
    _build_reading,
    _resolve_session_factory,
    run_simulator_cycle,
    is_simulator_running,
    start_simulator,
    stop_simulator,
    _simulator_scheduler,
    _simulator_lock,
    _SIMULATOR_JOB_ID,
)
from app.config import Settings, get_settings
from sqlalchemy.orm import Session
from collections.abc import Callable


@pytest.fixture(autouse=True)
def reset_simulator_globals():
    """Resetea el estado global del simulador antes de cada test."""
    with _simulator_lock:
        global _simulator_scheduler
        if _simulator_scheduler:
            _simulator_scheduler.shutdown(wait=False)
        _simulator_scheduler = None
    yield


class TestSimulatorService:
    """Tests para las funciones auxiliares del simulador."""

    def test_get_equipment_profile_valid(self):
        """Verifica que devuelve el perfil correcto para un tipo de equipo válido."""
        profile = _get_equipment_profile("compresor")
        assert "temp_range" in profile
        assert profile["temp_range"] == (40.0, 65.0)

    def test_get_equipment_profile_invalid(self):
        """Verifica que devuelve el perfil por defecto para un tipo de equipo inválido."""
        profile = _get_equipment_profile("inexistente")
        assert "temp_range" in profile
        assert profile["temp_range"] == (35.0, 55.0)  # default

    def test_get_equipment_profile_none(self):
        """Verifica que devuelve el perfil por defecto para tipo de equipo None."""
        profile = _get_equipment_profile(None)
        assert "temp_range" in profile
        assert profile["temp_range"] == (35.0, 55.0)  # default

    def test_get_equipment_profile_whitespace(self):
        """Verifica que maneja espacios en blanco y mayúsculas/minúsculas."""
        profile = _get_equipment_profile(" BOMBA ")
        assert "temp_range" in profile
        assert profile["temp_range"] == (35.0, 50.0)

    @patch("app.services.simulator_service.datetime")
    def test_build_reading(self, mock_datetime):
        """Verifica que _build_reading genera lecturas con el formato y rangos correctos."""
        mock_datetime.now.return_value.isoformat.return_value = (
            "2023-01-01T12:00:00Z"
        )
        rng = random.Random(42)  # Seed para reproducibilidad
        profile = {
            "temp_range": (10.0, 20.0),
            "humidity_range": (30.0, 40.0),
            "vib_base": (0.1, 0.2),
        }
        reading = _build_reading(rng, profile)

        assert "temperatura" in reading
        assert 10.0 <= reading["temperatura"] <= 20.0
        assert "humedad" in reading
        assert 30.0 <= reading["humedad"] <= 40.0
        assert "vib_x" in reading
        assert 0.1 <= reading["vib_x"] <= 0.2
        assert "vib_y" in reading
        assert 0.05 <= reading["vib_y"] <= 0.16  # vib_base * 0.5 y vib_base * 0.8
        assert "vib_z" in reading
        assert 9.5 <= reading["vib_z"] <= 10.1
        assert reading["timestamp"] == "2023-01-01T12:00:00Z"

    def test_resolve_session_factory_provided(self):
        """Verifica que usa la session_factory provista."""
        mock_factory = MagicMock(spec=Callable[[], Session])
        resolved = _resolve_session_factory(mock_factory)
        assert resolved is mock_factory

    @patch("app.services.simulator_service.SessionLocal")
    def test_resolve_session_factory_fallback(self, mock_session_local):
        """Verifica que usa SessionLocal si no se provee session_factory."""
        resolved = _resolve_session_factory(None)
        assert resolved is mock_session_local

    @patch("app.services.simulator_service.get_settings")
    @patch("app.services.equipo_service.list_equipos") # Patch where it's imported
    @patch("app.database.SessionLocal") # Patch where it's imported
    def test_run_simulator_cycle_mqtt_unavailable(
        self, mock_session_local, mock_list_equipos, mock_get_settings
    ):
        """Verifica el comportamiento cuando paho-mqtt no está disponible."""
        mock_get_settings.return_value = Settings(
            mqtt_broker_host="localhost",
            mqtt_broker_port=1883,
            mqtt_telemetry_topic="manttoai/equipo",
        )
        # Asegura que mqtt es None para simular no disponible
        with patch("app.services.simulator_service.mqtt", None):
            result = run_simulator_cycle()
            assert result == {"status": "skipped", "reason": "mqtt_unavailable"}

    @patch("app.services.simulator_service.get_settings")
    @patch("app.services.simulator_service.mqtt.Client")
    @patch("app.services.equipo_service.list_equipos") # Patch where it's imported
    def test_run_simulator_cycle_no_active_equipment(
        self, mock_list_equipos, mock_mqtt_client, mock_get_settings
    ):
        """Verifica el comportamiento cuando no hay equipos activos."""
        mock_get_settings.return_value = Settings(
            mqtt_broker_host="localhost",
            mqtt_broker_port=1883,
            mqtt_telemetry_topic="manttoai/equipo",
            mqtt_enabled=True,
        )
        mock_list_equipos.return_value = []
        mock_session = MagicMock(spec=Session)
        mock_session_factory = MagicMock(return_value=mock_session)

        result = run_simulator_cycle(session_factory=mock_session_factory)

        assert result == {"status": "ok", "equipos": 0, "publicados": 0}
        mock_list_equipos.assert_called_once_with(mock_session)
        mock_session.close.assert_called_once()
        mock_mqtt_client.assert_not_called()

    class MockEquipo:
        def __init__(self, id, mac_address, tipo, estado):
            self.id = id
            self.mac_address = mac_address
            self.tipo = tipo
            self.estado = estado

    @patch("app.services.simulator_service.get_settings")
    @patch("app.services.simulator_service.mqtt.Client")
    @patch("app.services.equipo_service.list_equipos") # Patch where it's imported
    def test_run_simulator_cycle_mqtt_connect_error(
        self, mock_list_equipos, mock_mqtt_client, mock_get_settings
    ):
        """Verifica el manejo de errores de conexión MQTT."""
        mock_get_settings.return_value = Settings(
            mqtt_broker_host="badhost",
            mqtt_broker_port=1883,
            mqtt_telemetry_topic="manttoai/equipo",
            mqtt_enabled=True,
        )
        mock_list_equipos.return_value = [
            self.MockEquipo(1, "mac1", "compresor", "operativo")
        ]
        mock_mqtt_client.return_value.connect.side_effect = Exception("Connect failed")

        mock_session = MagicMock(spec=Session)
        mock_session_factory = MagicMock(return_value=mock_session)

        result = run_simulator_cycle(session_factory=mock_session_factory)

        assert result["status"] == "error"
        assert "Connect failed" in result["reason"]
        mock_mqtt_client.return_value.connect.assert_called_once_with("badhost", 1883)
        mock_session.close.assert_called_once()

    @patch("app.services.simulator_service.get_settings")
    @patch("app.services.simulator_service.mqtt.Client")
    @patch("app.services.equipo_service.list_equipos") # Patch where it's imported
    @patch("app.services.simulator_service.random.Random")
    def test_run_simulator_cycle_success(
        self,
        mock_random,
        mock_list_equipos,
        mock_mqtt_client,
        mock_get_settings,
    ):
        """Verifica un ciclo completo de simulación exitoso."""
        settings = Settings(
            mqtt_broker_host="localhost",
            mqtt_broker_port=1883,
            mqtt_telemetry_topic="manttoai/equipo",
            mqtt_username="user",
            mqtt_password="pass",
            mqtt_enabled=True,
        )
        mock_get_settings.return_value = settings

        mock_equipos = [
            self.MockEquipo(1, "mac1", "compresor", "operativo"),
            self.MockEquipo(2, "mac2", "bomba", "activo"),
        ]
        mock_list_equipos.return_value = mock_equipos

        mock_mqtt_instance = MagicMock()
        mock_mqtt_instance.publish.return_value.rc = 0
        mock_mqtt_client.return_value = mock_mqtt_instance

        mock_random_instance = MagicMock()
        mock_random_instance.uniform.side_effect = [
            50.0,
            60.0,
            0.5,
            0.25,
            9.8,  # for mac1
            40.0,
            50.0,
            0.3,
            0.15,
            9.9,  # for mac2
        ]
        mock_random.return_value = mock_random_instance

        mock_session = MagicMock(spec=Session)
        mock_session_factory = MagicMock(return_value=mock_session)

        result = run_simulator_cycle(session_factory=mock_session_factory)

        assert result["status"] == "ok"
        assert result["equipos"] == 2
        assert result["publicados"] == 2
        mock_mqtt_client.assert_called_once_with(
            mqtt.CallbackAPIVersion.VERSION2
        )
        mock_mqtt_instance.username_pw_set.assert_called_once_with("user", "pass")
        mock_mqtt_instance.connect.assert_called_once_with("localhost", 1883)
        assert mock_mqtt_instance.publish.call_count == 2
        mock_mqtt_instance.disconnect.assert_called_once()
        mock_session.close.assert_called_once()

    @patch("app.services.simulator_service.get_settings")
    @patch("app.services.simulator_service.mqtt.Client")
    @patch("app.services.equipo_service.list_equipos") # Patch where it's imported
    @patch("app.services.simulator_service.random.Random")
    def test_run_simulator_cycle_partial_publish_failure(
        self,
        mock_random,
        mock_list_equipos,
        mock_mqtt_client,
        mock_get_settings,
    ):
        """Verifica el comportamiento cuando algunas publicaciones MQTT fallan."""
        settings = Settings(
            mqtt_broker_host="localhost",
            mqtt_broker_port=1883,
            mqtt_telemetry_topic="manttoai/equipo",
            mqtt_enabled=True,
        )
        mock_get_settings.return_value = settings

        mock_equipos = [
            self.MockEquipo(1, "mac1", "compresor", "operativo"),
            self.MockEquipo(2, "mac2", "bomba", "activo"),
        ]
        mock_list_equipos.return_value = mock_equipos

        mock_mqtt_instance = MagicMock()
        # Primer publish falla (rc=1), segundo exitoso (rc=0)
        mock_mqtt_instance.publish.side_effect = [
            MagicMock(rc=1),
            MagicMock(rc=0),
        ]
        mock_mqtt_client.return_value = mock_mqtt_instance

        mock_random_instance = MagicMock()
        mock_random_instance.uniform.side_effect = [
            50.0,
            60.0,
            0.5,
            0.25,
            9.8,  # for mac1
            40.0,
            50.0,
            0.3,
            0.15,
            9.9,  # for mac2
        ]
        mock_random.return_value = mock_random_instance

        mock_session = MagicMock(spec=Session)
        mock_session_factory = MagicMock(return_value=mock_session)

        result = run_simulator_cycle(session_factory=mock_session_factory)

        assert result["status"] == "ok"
        assert result["equipos"] == 2
        assert result["publicados"] == 1  # Solo uno publicado con éxito
        assert mock_mqtt_instance.publish.call_count == 2
        mock_mqtt_instance.disconnect.assert_called_once()
        mock_session.close.assert_called_once()


    @patch("app.services.simulator_service._simulator_scheduler")
    def test_is_simulator_running_true_from_running(self, mock_scheduler):
        """Verifica que is_simulator_running retorna True si el scheduler está corriendo (atributo 'running')."""
        mock_scheduler.running = True
        assert is_simulator_running() is True

    @patch("app.services.simulator_service._simulator_scheduler")
    def test_is_simulator_running_true_from_started(self, mock_scheduler):
        """Verifica que is_simulator_running retorna True si el scheduler ha sido iniciado (atributo 'started')."""
        del mock_scheduler.running  # Remove 'running' attribute
        mock_scheduler.started = True
        assert is_simulator_running() is True

    @patch("app.services.simulator_service._simulator_scheduler")
    def test_is_simulator_running_false_from_running(self, mock_scheduler):
        """Verifica que is_simulator_running retorna False si el scheduler no está corriendo (atributo 'running')."""
        mock_scheduler.running = False
        assert is_simulator_running() is False

    @patch("app.services.simulator_service._simulator_scheduler")
    def test_is_simulator_running_false_from_started(self, mock_scheduler):
        """Verifica que is_simulator_running retorna False si el scheduler no ha sido iniciado (atributo 'started')."""
        del mock_scheduler.running  # Remove 'running' attribute
        mock_scheduler.started = False
        assert is_simulator_running() is False

    def test_is_simulator_running_false_no_scheduler(self):
        """Verifica que is_simulator_running retorna False si no hay scheduler."""
        assert is_simulator_running() is False


@patch("app.services.simulator_service.get_settings")
@patch("app.services.simulator_service.logger")
def test_start_simulator_disabled_by_config(mock_logger, mock_get_settings):
    """Verifica que el simulador no inicia si está deshabilitado por configuración."""
    mock_get_settings.return_value = Settings(simulator_enabled=False)
    assert start_simulator() is False
    mock_logger.info.assert_called_with("Simulador IoT deshabilitado por configuración")


@patch("app.services.simulator_service.get_settings")
@patch("app.services.simulator_service.logger")
def test_start_simulator_mqtt_disabled(mock_logger, mock_get_settings):
    """Verifica que el simulador no inicia si MQTT está deshabilitado."""
    mock_get_settings.return_value = Settings(simulator_enabled=True, mqtt_enabled=False)
    assert start_simulator() is False
    mock_logger.info.assert_called_with("Simulador IoT requiere MQTT habilitado")


@patch("app.services.simulator_service.get_settings")
@patch("app.services.simulator_service.logger")
def test_start_simulator_invalid_interval(mock_logger, mock_get_settings):
    """Verifica que el simulador no inicia con un intervalo inválido."""
    mock_get_settings.return_value = Settings(
        simulator_enabled=True, mqtt_enabled=True, simulator_interval_seconds=0
    )
    assert start_simulator() is False
    mock_logger.warning.assert_called_with("Intervalo inválido para simulador: %s", 0)


@patch("app.services.simulator_service.get_settings")
@patch("app.services.simulator_service.logger")
@patch("app.services.simulator_service.BackgroundScheduler", new=None)
def test_start_simulator_apscheduler_unavailable(mock_logger, mock_get_settings):
    """Verifica que el simulador no inicia si APScheduler no está disponible."""
    mock_get_settings.return_value = Settings(
        simulator_enabled=True, mqtt_enabled=True, simulator_interval_seconds=10
    )
    assert start_simulator() is False
    mock_logger.warning.assert_called_with("APScheduler no disponible para simulador")


@patch("app.services.simulator_service.get_settings")
@patch("app.services.simulator_service.logger")
def test_start_simulator_invalid_session_factory(mock_logger, mock_get_settings):
    """Verifica que el simulador no inicia con una SessionFactory inválida."""
    mock_get_settings.return_value = Settings(
        simulator_enabled=True, mqtt_enabled=True, simulator_interval_seconds=10
    )
    # Simula una SessionFactory que no es callable
    assert start_simulator(session_factory="not_callable") is False
    mock_logger.error.assert_called_with("SessionFactory inválido para simulador")


@patch("app.services.simulator_service.get_settings")
@patch("app.services.simulator_service.BackgroundScheduler")
@patch("app.services.simulator_service.logger")
def test_start_simulator_success(
    mock_logger, mock_background_scheduler, mock_get_settings
):
    """Verifica que el simulador inicia correctamente."""
    settings = Settings(
        simulator_enabled=True, mqtt_enabled=True, simulator_interval_seconds=10
    )
    mock_get_settings.return_value = settings

    mock_scheduler_instance = MagicMock()
    mock_background_scheduler.return_value = mock_scheduler_instance

    mock_session_factory = MagicMock(spec=Callable[[], Session])

    assert start_simulator(session_factory=mock_session_factory) is True
    mock_background_scheduler.assert_called_once_with(timezone="UTC")
    mock_scheduler_instance.add_job.assert_called_once()
    mock_scheduler_instance.start.assert_called_once()
    mock_logger.info.assert_called_with(
        "Simulador IoT iniciado job_id=%s (intervalo=%s segundos)",
        _SIMULATOR_JOB_ID,
        settings.simulator_interval_seconds,
    )

    # Verificar que el simulador no se inicia dos veces
    assert start_simulator(session_factory=mock_session_factory) is True


@patch("app.services.simulator_service.get_settings")
@patch("app.services.simulator_service.BackgroundScheduler")
@patch("app.services.simulator_service.logger")
def test_start_simulator_exception_during_init(
    mock_logger, mock_background_scheduler, mock_get_settings
):
    """Verifica el manejo de excepciones durante la inicialización del simulador."""
    mock_get_settings.return_value = Settings(
        simulator_enabled=True, mqtt_enabled=True, simulator_interval_seconds=10
    )
    mock_background_scheduler.side_effect = Exception("Scheduler init failed")

    mock_session_factory = MagicMock(spec=Callable[[], Session])

    assert start_simulator(session_factory=mock_session_factory) is False
    mock_logger.exception.assert_called_with("No se pudo iniciar el simulador")


@patch("app.services.simulator_service.logger")
def test_stop_simulator_not_running(mock_logger):
    """Verifica que detener el simulador cuando no está corriendo no causa error."""
    # Asegurarse de que _simulator_scheduler es None
    global _simulator_scheduler
    _simulator_scheduler = None

    stop_simulator()
    mock_logger.info.assert_not_called()  # No debería loggear "detenido"


@patch("app.services.simulator_service._simulator_scheduler")
@patch("app.services.simulator_service.logger")
def test_stop_simulator_success(mock_logger, mock_scheduler):
    """Verifica que el simulador se detiene correctamente."""
    # Simular que el simulador está corriendo
    global _simulator_scheduler
    _simulator_scheduler = mock_scheduler

    stop_simulator()
    mock_scheduler.shutdown.assert_called_once_with(wait=False)
    mock_logger.info.assert_called_with("Simulador IoT detenido")
    assert _simulator_scheduler is None
