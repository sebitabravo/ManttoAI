"""Tests del simulador MQTT usado en demo académica."""

from __future__ import annotations

import importlib.util
import json
import random
from pathlib import Path
from types import SimpleNamespace


def _load_mqtt_simulator_module():
    module_path = (
        Path(__file__).resolve().parents[2] / "iot" / "simulator" / "mqtt_simulator.py"
    )
    spec = importlib.util.spec_from_file_location(
        "manttoai_mqtt_simulator", module_path
    )
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module


mqtt_simulator = _load_mqtt_simulator_module()


def test_build_topic_supports_prefix_with_trailing_slash():
    """Valida construcción estable del topic por equipo."""

    assert (
        mqtt_simulator.build_topic("manttoai/telemetria", 7)
        == "manttoai/telemetria/7"
    )


def test_build_payload_is_reproducible_with_seed():
    """Valida payload determinista usando semilla fija."""

    payload = mqtt_simulator.build_payload(random.Random(42))

    assert payload == {
        "temperatura": 47.79,
        "humedad": 45.63,
        "vib_x": 0.31,
        "vib_y": 0.167,
        "vib_z": 9.942,
        "timestamp": payload["timestamp"],
    }
    assert payload["timestamp"].endswith("Z")


def test_main_publishes_expected_messages_with_mocked_client(monkeypatch):
    """Valida loop principal del simulador con cliente MQTT fake."""

    published_messages = []

    class _FakeClient:
        def username_pw_set(self, username, password):
            self.username = username
            self.password = password

        def connect(self, host, port):
            self.host = host
            self.port = port

        def publish(self, topic, payload):
            published_messages.append((topic, json.loads(payload)))
            return SimpleNamespace(rc=0)

        def disconnect(self):
            return None

    monkeypatch.setattr(
        mqtt_simulator,
        "parse_args",
        lambda: SimpleNamespace(
            host="localhost",
            port=1883,
            username="demo-user",
            password="demo-pass",
            devices=2,
            start_id=10,
            equipo_id=None,
            count=2,
            interval=0.0,
            topic_prefix="manttoai/telemetria",
            seed=123,
        ),
    )
    monkeypatch.setattr(mqtt_simulator.time, "sleep", lambda _seconds: None)
    monkeypatch.setattr(
        mqtt_simulator,
        "mqtt",
        SimpleNamespace(
            Client=lambda *_args, **_kwargs: _FakeClient(),
            CallbackAPIVersion=SimpleNamespace(VERSION2="v2"),
            MQTT_ERR_SUCCESS=0,
        ),
    )

    result = mqtt_simulator.main()

    assert result == 0
    assert len(published_messages) == 4
    assert {topic for topic, _payload in published_messages} == {
        "manttoai/telemetria/10",
        "manttoai/telemetria/11",
    }
    assert all(
        payload["timestamp"].endswith("Z") for _topic, payload in published_messages
    )
