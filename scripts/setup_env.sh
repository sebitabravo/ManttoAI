#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ROOT_ENV_FILE="$ROOT_DIR/.env"
BACKEND_ENV_FILE="$ROOT_DIR/backend/.env"

ensure_env_key() {
  local file_path="$1"
  local key="$2"
  local value="$3"

  if ! grep -qE "^${key}=" "$file_path"; then
    printf '%s=%s\n' "$key" "$value" >> "$file_path"
  fi
}

create_root_env() {
  cat > "$ROOT_ENV_FILE" <<EOF
# Entorno local/demo generado automáticamente.
MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD:-manttoai_root}
MYSQL_DATABASE=${MYSQL_DATABASE:-manttoai_db}
MQTT_USERNAME=${MQTT_USERNAME:-manttoai_mqtt}
MQTT_PASSWORD=${MQTT_PASSWORD:-manttoai_mqtt_dev}
COMPOSE_PROJECT_NAME=${COMPOSE_PROJECT_NAME:-manttoai}
EOF
}

create_backend_env() {
  cat > "$BACKEND_ENV_FILE" <<EOF
APP_NAME=ManttoAI Predictive Maintenance API
APP_ENV=${APP_ENV:-development}
API_PREFIX=
DATABASE_URL=${DATABASE_URL:-mysql+pymysql://root:${MYSQL_ROOT_PASSWORD:-manttoai_root}@mysql:3306/${MYSQL_DATABASE:-manttoai_db}}
DATABASE_AUTO_INIT=${DATABASE_AUTO_INIT:-true}
SECRET_KEY=${SECRET_KEY:-manttoai-dev-secret}
MQTT_BROKER_HOST=${MQTT_BROKER_HOST:-mosquitto}
MQTT_BROKER_PORT=${MQTT_BROKER_PORT:-1883}
MQTT_USERNAME=${MQTT_USERNAME:-manttoai_mqtt}
MQTT_PASSWORD=${MQTT_PASSWORD:-manttoai_mqtt_dev}
MQTT_BASE_TOPIC=${MQTT_BASE_TOPIC:-manttoai/equipo}
MQTT_ENABLED=${MQTT_ENABLED:-true}
SMTP_HOST=${SMTP_HOST:-}
SMTP_PORT=${SMTP_PORT:-587}
SMTP_USER=${SMTP_USER:-}
SMTP_PASSWORD=${SMTP_PASSWORD:-}
SMTP_FROM_EMAIL=${SMTP_FROM_EMAIL:-}
SMTP_TO_EMAIL=${SMTP_TO_EMAIL:-}
ENABLE_PREDICTION_SCHEDULER=${ENABLE_PREDICTION_SCHEDULER:-true}
PREDICTION_INTERVAL_SECONDS=${PREDICTION_INTERVAL_SECONDS:-300}
PREDICTION_SCHEDULER_MAX_WORKERS=${PREDICTION_SCHEDULER_MAX_WORKERS:-4}
SEED_ADMIN_NAME=${SEED_ADMIN_NAME:-Admin ManttoAI}
SEED_ADMIN_EMAIL=${SEED_ADMIN_EMAIL:-admin@manttoai.local}
SEED_ADMIN_PASSWORD=${SEED_ADMIN_PASSWORD:-Admin123!}
SEED_RESET_ADMIN_PASSWORD=${SEED_RESET_ADMIN_PASSWORD:-false}
SEED_ALLOW_NON_DEV=${SEED_ALLOW_NON_DEV:-false}
EOF
}

if [ ! -f "$ROOT_ENV_FILE" ]; then
  create_root_env
fi

if [ ! -f "$BACKEND_ENV_FILE" ]; then
  create_backend_env
fi

ensure_env_key "$ROOT_ENV_FILE" "MYSQL_ROOT_PASSWORD" "${MYSQL_ROOT_PASSWORD:-manttoai_root}"
ensure_env_key "$ROOT_ENV_FILE" "MYSQL_DATABASE" "${MYSQL_DATABASE:-manttoai_db}"
ensure_env_key "$ROOT_ENV_FILE" "MQTT_USERNAME" "${MQTT_USERNAME:-manttoai_mqtt}"
ensure_env_key "$ROOT_ENV_FILE" "MQTT_PASSWORD" "${MQTT_PASSWORD:-manttoai_mqtt_dev}"
ensure_env_key "$ROOT_ENV_FILE" "COMPOSE_PROJECT_NAME" "${COMPOSE_PROJECT_NAME:-manttoai}"

ensure_env_key "$BACKEND_ENV_FILE" "MQTT_USERNAME" "${MQTT_USERNAME:-manttoai_mqtt}"
ensure_env_key "$BACKEND_ENV_FILE" "MQTT_PASSWORD" "${MQTT_PASSWORD:-manttoai_mqtt_dev}"
ensure_env_key "$BACKEND_ENV_FILE" "PREDICTION_SCHEDULER_MAX_WORKERS" "${PREDICTION_SCHEDULER_MAX_WORKERS:-4}"
ensure_env_key "$BACKEND_ENV_FILE" "SEED_ADMIN_PASSWORD" "${SEED_ADMIN_PASSWORD:-Admin123!}"

printf 'Entorno local listo: %s y %s\n' "$ROOT_ENV_FILE" "$BACKEND_ENV_FILE"
