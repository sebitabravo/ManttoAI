# IoT ManttoAI

Este módulo concentra el firmware del ESP32, el pinout y un simulador MQTT para desarrollo sin hardware.

## Objetivo del scaffold

- dejar la estructura lista para firmware real
- permitir pruebas con `iot/simulator/mqtt_simulator.py`

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
