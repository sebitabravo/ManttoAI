# IoT ManttoAI

Este módulo concentra el firmware del ESP32, el pinout y un simulador MQTT para desarrollo sin hardware.

## Estado del firmware

- lectura real de **DHT22** (temperatura/humedad)
- lectura real de **MPU-6050** (aceleración en ejes X/Y/Z)
- publicación periódica MQTT (flujo MVP)
- soporte de simulación con `iot/simulator/mqtt_simulator.py` cuando no hay hardware

## Librerías Arduino requeridas

- PubSubClient
- DHT sensor library
- Adafruit Unified Sensor

Referencia: `iot/firmware/libraries.txt`

## Pinout y armado

- Ver detalle actualizado en `iot/wiring/pinout.md`
- Resumen rápido:
  - DHT22 DATA -> GPIO4
  - MPU-6050 SDA -> GPIO21
  - MPU-6050 SCL -> GPIO22
  - 3V3 y GND compartidos

## Verificación en Serial Monitor

Con firmware cargado en ESP32 (115200 baudios), deberían verse líneas similares a:

```text
[sensors] temp=24.80 °C | hum=52.10 % | vib_x=0.012 g | vib_y=-0.004 g | vib_z=0.998 g
```

Checklist rápido:

- temperatura/humedad cambian con el ambiente real
- `vib_x`, `vib_y`, `vib_z` varían al mover el MPU-6050
- no aparecen valores fijos hardcodeados

## Contrato MQTT del simulador

### Topic

```text
manttoai/equipo/{equipo_id}/lecturas
```

Se puede customizar con `--topic-prefix`.

### Payload JSON

```json
{
  "temperatura": 45.2,
  "humedad": 60.0,
  "vib_x": 0.3,
  "vib_y": 0.1,
  "vib_z": 9.8,
  "timestamp": "2026-04-04T22:00:00Z"
}
```

Este formato es compatible con el backend actual (campos telemétricos esperados + timestamp opcional).

## Simulación rápida (desde la raíz del repo)

Un ciclo publica **1 lectura por equipo**.

### Caso mínimo

```bash
python iot/simulator/mqtt_simulator.py --count 5 --interval 1
```

Compatibilidad hacia atrás:

```bash
python iot/simulator/mqtt_simulator.py --equipo-id 1 --count 5
```

### Multi-equipo

```bash
python iot/simulator/mqtt_simulator.py --devices 3 --count 5 --interval 0.5
```

### Datos reproducibles

```bash
python iot/simulator/mqtt_simulator.py --devices 2 --count 5 --seed 42
```

### Topic prefix personalizado

```bash
python iot/simulator/mqtt_simulator.py --topic-prefix "manttoai/equipo" --devices 2
```

### IDs iniciales personalizados

```bash
python iot/simulator/mqtt_simulator.py --devices 2 --start-id 10 --count 3
```

Publica en:

- `manttoai/equipo/10/lecturas`
- `manttoai/equipo/11/lecturas`

## Escuchar mensajes publicados

```bash
mosquitto_sub -h localhost -t "manttoai/#" -v
```
