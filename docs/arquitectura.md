# Arquitectura general

ManttoAI implementa una arquitectura MVP orientada a demo académica: pocos componentes,
flujo explícito y trazabilidad técnica suficiente para defensa.

## Diagrama de alto nivel

```mermaid
flowchart LR
  A[ESP32 nodo 1..N\nDHT22 + MPU6050] -->|MQTT JSON\nmanttoai/equipo/{id}/lecturas| B[(Mosquitto)]
  S[Simulador MQTT\niot/simulator] -->|MQTT JSON| B

  B --> C[FastAPI backend\nrouters + services]
  C --> D[(MySQL 8)]
  C --> E[RandomForest\napp/ml/modelo.joblib]
  C --> F[SMTP (Mailpit en demo)]

  G[React + Vite Dashboard] -->|/api/*| H[Nginx]
  H --> C
  H --> G
```

## Flujo operativo

1. Dispositivo ESP32 (o simulador) publica telemetría en MQTT.
2. `mqtt_service` consume, valida y persiste lecturas.
3. `alerta_service` evalúa umbrales y crea alertas deduplicadas.
4. `prediccion_scheduler_service` y/o endpoint manual ejecutan inferencia ML.
5. `email_service` dispara notificaciones críticas vía SMTP.
6. Frontend consume `/dashboard/resumen`, `/lecturas`, `/alertas`, `/predicciones` vía polling.

## Contratos clave

- Topic MQTT: `manttoai/equipo/{equipo_id}/lecturas`
- Payload telemetría: temperatura, humedad, vib_x, vib_y, vib_z, timestamp opcional
- Endpoint agregador: `GET /dashboard/resumen`

## Alcance y límites (MVP académico)

- Sin microservicios, sin Kubernetes, sin colas distribuidas.
- Persistencia única en MySQL.
- Modelo clásico (`RandomForest`) por simplicidad y explicabilidad.
- Canal de alerta por email como primera etapa.

La versión extensa y narrativa para informe está en `docs/arquitectura-manttoai.md`.
