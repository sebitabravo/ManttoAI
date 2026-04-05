"""Simulador MQTT para generar lecturas demo sin ESP32 físico."""

from __future__ import annotations

import argparse
import json
import random
import time
from datetime import datetime, timezone

try:
    import paho.mqtt.client as mqtt
except (
    ImportError
):  # pragma: no cover - ruta útil para ejecutar sin dependencia instalada
    mqtt = None


def positive_int(value: str) -> int:
    """Valida que un argumento entero sea mayor a cero."""

    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"'{value}' no es un entero válido") from exc

    if parsed <= 0:
        raise argparse.ArgumentTypeError("el valor debe ser mayor a 0")
    return parsed


def positive_float(value: str) -> float:
    """Valida que un argumento decimal sea mayor a cero."""

    try:
        parsed = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"'{value}' no es un decimal válido") from exc

    if parsed <= 0:
        raise argparse.ArgumentTypeError("el valor debe ser mayor a 0")
    return parsed


def utc_timestamp() -> str:
    """Entrega un timestamp ISO8601 en UTC terminado en Z."""

    return (
        datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    )


def build_payload(rng: random.Random) -> dict[str, float | str]:
    """Construye una lectura aleatoria razonable para el prototipo."""

    return {
        "temperatura": round(rng.uniform(35.0, 55.0), 2),
        "humedad": round(rng.uniform(45.0, 70.0), 2),
        "vib_x": round(rng.uniform(0.2, 0.6), 3),
        "vib_y": round(rng.uniform(0.1, 0.4), 3),
        "vib_z": round(rng.uniform(9.5, 10.1), 3),
        "timestamp": utc_timestamp(),
    }


def build_topic(topic_prefix: str, equipo_id: int) -> str:
    """Construye el topic MQTT para un equipo."""

    return f"{topic_prefix.rstrip('/')}/{equipo_id}/lecturas"


def publish_reading(
    client: mqtt.Client, topic: str, payload: dict[str, float | str]
) -> mqtt.MQTTMessageInfo:
    """Publica una lectura serializando el payload en JSON."""

    return client.publish(topic, json.dumps(payload))


def parse_args() -> argparse.Namespace:
    """Parsea argumentos de línea de comandos."""

    parser = argparse.ArgumentParser(description="Simulador MQTT de ManttoAI")
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=positive_int, default=1883)
    parser.add_argument("--username", default="")
    parser.add_argument("--password", default="")
    parser.add_argument("--devices", type=positive_int, default=1)
    parser.add_argument("--start-id", type=positive_int, default=1)
    parser.add_argument(
        "--equipo-id",
        type=positive_int,
        default=None,
        help="Compatibilidad hacia atrás: publica solo para un equipo específico.",
    )
    parser.add_argument("--count", type=positive_int, default=5)
    parser.add_argument("--interval", type=positive_float, default=1.5)
    parser.add_argument("--topic-prefix", default="manttoai/equipo")
    parser.add_argument("--seed", type=int, default=None)
    return parser.parse_args()


def main() -> int:
    """Publica lecturas MQTT demo si paho-mqtt está disponible."""

    args = parse_args()

    if args.equipo_id is not None:
        args.start_id = args.equipo_id
        args.devices = 1

    rng = random.Random(args.seed)
    equipo_ids = [args.start_id + idx for idx in range(args.devices)]
    topics = {
        equipo_id: build_topic(args.topic_prefix, equipo_id) for equipo_id in equipo_ids
    }

    if mqtt is None:
        print("paho-mqtt no está instalado. Instalalo para usar el simulador real.")
        return 1

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    if args.username:
        client.username_pw_set(args.username, args.password)
    client.connect(args.host, args.port)

    for ciclo in range(args.count):
        for equipo_id in equipo_ids:
            topic = topics[equipo_id]
            payload = build_payload(rng)
            message_info = publish_reading(client, topic, payload)
            if message_info.rc != mqtt.MQTT_ERR_SUCCESS:
                print(
                    f"[{ciclo + 1}/{args.count}] Error publicando en {topic}: rc={message_info.rc}"
                )
                continue

            print(f"[{ciclo + 1}/{args.count}] Publicado en {topic}: {payload}")

        if ciclo < args.count - 1:
            time.sleep(args.interval)

    client.disconnect()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
