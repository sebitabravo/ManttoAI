# Arquitectura general

ManttoAI sigue un flujo simple:

1. ESP32 o simulador publica en MQTT.
2. Backend FastAPI recibe y procesa lecturas.
3. Se generan alertas y predicciones base.
4. Frontend consulta el resumen y muestra el dashboard.

La arquitectura detallada del árbol vive en `docs/arquitectura-manttoai.md`.
