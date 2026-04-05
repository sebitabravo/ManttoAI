"""Simulador MQTT para generar lecturas demo sin ESP32 físico."""

from __future__ import annotations

import argparse
import json
import random
import time

try:
    import paho.mqtt.client as mqtt
except (
    ImportError
):  # pragma: no cover - ruta útil para ejecutar sin dependencia instalada
    mqtt = None


def build_payload() -> dict[str, float]:
    """Construye una lectura aleatoria razonable para el prototipo."""

    return {
        "temperatura": round(random.uniform(35.0, 55.0), 2),
        "humedad": round(random.uniform(45.0, 70.0), 2),
        "vib_x": round(random.uniform(0.2, 0.6), 3),
        "vib_y": round(random.uniform(0.1, 0.4), 3),
        "vib_z": round(random.uniform(9.5, 10.1), 3),
    }


def parse_args() -> argparse.Namespace:
    """Parsea argumentos de línea de comandos."""

    parser = argparse.ArgumentParser(description="Simulador MQTT de ManttoAI")
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=1883)
    parser.add_argument("--equipo-id", type=int, default=1)
    parser.add_argument("--count", type=int, default=5)
    parser.add_argument("--interval", type=float, default=1.5)
    return parser.parse_args()


def main() -> int:
    """Publica lecturas MQTT demo si paho-mqtt está disponible."""

    args = parse_args()
    topic = f"manttoai/equipo/{args.equipo_id}/lecturas"

    if mqtt is None:
        print("paho-mqtt no está instalado. Instalalo para usar el simulador real.")
        return 1

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.connect(args.host, args.port)

    for _ in range(args.count):
        payload = build_payload()
        client.publish(topic, json.dumps(payload))
        print(f"Publicado en {topic}: {payload}")
        time.sleep(args.interval)

    client.disconnect()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
