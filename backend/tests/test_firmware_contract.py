"""Regresiones estáticas mínimas del contrato MQTT del firmware ESP32."""

from pathlib import Path


FIRMWARE_PATH = (
    Path(__file__).resolve().parents[2]
    / "iot"
    / "firmware"
    / "manttoai_sensor"
    / "mqtt_client.cpp"
)


def test_firmware_client_id_formatea_la_mac_como_string():
    """El client ID debe usar la MAC con el especificador de formato correcto."""

    source = FIRMWARE_PATH.read_text(encoding="utf-8")

    assert '"manttoai-esp32-%s", WiFi.macAddress().c_str()' in source
