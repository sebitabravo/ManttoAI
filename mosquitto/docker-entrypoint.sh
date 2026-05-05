#!/bin/ash
# Genera passwd en el arranque si no existe.
# En local: se puede hacer bind mount del passwd generado por make setup-mqtt-creds.
# En Dokploy / producción: se genera desde variables de entorno.
# Seguridad: MQTT_USERNAME y MQTT_PASSWORD son obligatorios.
# No se usan fallbacks hardcodeados para evitar credenciales por defecto en producción.
set -e

if [ ! -f /mosquitto/config/passwd ]; then
  if [ -z "$MQTT_USERNAME" ] || [ -z "$MQTT_PASSWORD" ]; then
    echo "[mosquitto-entrypoint] ERROR: MQTT_USERNAME y MQTT_PASSWORD son obligatorios." >&2
    echo "[mosquitto-entrypoint] Definilas en el entorno antes de iniciar el contenedor." >&2
    exit 1
  fi
  echo "[mosquitto-entrypoint] passwd no encontrado, generando desde variables de entorno..."
  mosquitto_passwd -c -b /mosquitto/config/passwd "$MQTT_USERNAME" "$MQTT_PASSWORD"
  echo "[mosquitto-entrypoint] passwd generado correctamente."
fi

# Ejecutar mosquitto directamente (NO llamar a /docker-entrypoint.sh porque
# este archivo lo sobreescribió y causaría un bucle infinito).
exec /usr/sbin/mosquitto -c /mosquitto/config/mosquitto.conf
