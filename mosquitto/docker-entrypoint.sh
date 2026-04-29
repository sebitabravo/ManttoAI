#!/bin/ash
# Genera passwd en el arranque si no existe.
# En local: se puede hacer bind mount del passwd generado por make setup-mqtt-creds.
# En Dokploy / producción: se genera desde variables de entorno.
set -e

if [ ! -f /mosquitto/config/passwd ]; then
  echo "[mosquitto-entrypoint] passwd no encontrado, generando desde variables de entorno..."
  mosquitto_passwd -c -b /mosquitto/config/passwd \
    "${MQTT_USERNAME:-manttoai_mqtt}" \
    "${MQTT_PASSWORD:-manttoai_mqtt_dev}"
  echo "[mosquitto-entrypoint] passwd generado correctamente."
fi

# Ejecutar mosquitto directamente (NO llamar a /docker-entrypoint.sh porque
# este archivo lo sobreescribió y causaría un bucle infinito).
exec /usr/sbin/mosquitto -c /mosquitto/config/mosquitto.conf
