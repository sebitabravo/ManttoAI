#!/usr/bin/env bash
set -euo pipefail

# Genera archivo de credenciales para Mosquitto usando variables del entorno.
# Prioriza valores exportados y usa defaults de demo si no están definidos.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PASSWD_FILE="$ROOT_DIR/mosquitto/passwd"

MQTT_USERNAME="${MQTT_USERNAME:-manttoai_mqtt}"
MQTT_PASSWORD="${MQTT_PASSWORD:-manttoai_mqtt_dev}"

if [[ -f "$ROOT_DIR/.env" ]]; then
  # Carga variables de .env solo para esta ejecución.
  set -a
  # shellcheck source=/dev/null
  source "$ROOT_DIR/.env"
  set +a

  MQTT_USERNAME="${MQTT_USERNAME:-manttoai_mqtt}"
  MQTT_PASSWORD="${MQTT_PASSWORD:-manttoai_mqtt_dev}"
fi

docker run --rm \
  -v "$ROOT_DIR/mosquitto:/mosquitto/config" \
  eclipse-mosquitto:2 \
  mosquitto_passwd -b -c /mosquitto/config/passwd "$MQTT_USERNAME" "$MQTT_PASSWORD"

chmod 600 "$PASSWD_FILE"
echo "Archivo de credenciales generado en: $PASSWD_FILE"
