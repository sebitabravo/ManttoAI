#!/usr/bin/env bash
set -euo pipefail

# Genera archivo de credenciales para Mosquitto usando variables del entorno.
# Prioriza valores exportados y usa defaults de demo si no están definidos.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PASSWD_FILE="$ROOT_DIR/mosquitto/config/passwd"
TEMP_PASSWORD_FILE="$(mktemp)"

cleanup_password_file() {
  rm -f "$TEMP_PASSWORD_FILE"
}

trap cleanup_password_file EXIT

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

chmod 600 "$TEMP_PASSWORD_FILE"
printf '%s\n%s\n' "$MQTT_PASSWORD" "$MQTT_PASSWORD" > "$TEMP_PASSWORD_FILE"

docker run --rm \
  -v "$ROOT_DIR/mosquitto:/mosquitto/config" \
  -v "$TEMP_PASSWORD_FILE:/tmp/mqtt_password:ro" \
  eclipse-mosquitto:2 \
  sh -c 'mosquitto_passwd -c /mosquitto/config/passwd "$1" < /tmp/mqtt_password' sh "$MQTT_USERNAME"

chmod 600 "$PASSWD_FILE"
echo "Archivo de credenciales generado en: $PASSWD_FILE"
