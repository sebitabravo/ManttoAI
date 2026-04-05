# ADR 003 — Usar MQTT sobre HTTP desde el dispositivo

## Decisión

Se usa MQTT como protocolo de ingesta desde ESP32.

## Motivo

- menor overhead que HTTP polling
- patrón natural pub/sub para telemetría
- encaja bien con Mosquitto en un VPS simple

## Consecuencia

El backend puede desacoplar recepción, almacenamiento y evaluación de alertas.
