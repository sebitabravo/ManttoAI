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

> `WiFi.h` y `Wire.h` vienen integradas en el core de ESP32 (no requieren instalación adicional).

Referencia: `iot/firmware/libraries.txt`

## Configuración mínima del firmware

Editar `iot/firmware/manttoai_sensor/config.h` con valores reales de red/broker:

```cpp
WIFI_SSID
WIFI_PASSWORD
MQTT_HOST
MQTT_PORT
MQTT_USERNAME
MQTT_PASSWORD
EQUIPO_ID
MQTT_PUBLISH_INTERVAL_MS
```

Parámetros recomendados para demo local:

- `MQTT_HOST`: IP del host con Mosquitto accesible desde el ESP32.
- `MQTT_PORT`: `1883`.
- `MQTT_USERNAME` / `MQTT_PASSWORD`: requeridos cuando Mosquitto está configurado con `allow_anonymous false`.
- `MQTT_PUBLISH_INTERVAL_MS`: `5000` (una lectura cada 5 segundos).

El archivo de credenciales del broker (`mosquitto/passwd`) se genera con:

```bash
make setup-mqtt-creds
```

Si no existe, `make setup-env` lo crea automáticamente.

> ⚠️ No versionar credenciales reales del broker. Usar placeholders en `config.h` y valores reales solo en entorno local/dispositivo.

Topic publicado por firmware:

```text
manttoai/equipo/{EQUIPO_ID}/lecturas
```

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

## Verificación end-to-end hardware -> broker -> backend -> dashboard

> Si el ESP32 está fuera del host Docker, recordá exponer Mosquitto para LAN.
> En `docker-compose.yml` podés cambiar temporalmente `127.0.0.1:1883:1883` por `1883:1883` para la demo física,
> y luego revertir para mantener menor superficie de exposición en desarrollo local.

1. Cargar firmware al ESP32.
2. En el host del broker, abrir:

   ```bash
   mosquitto_sub -h <broker> -u <mqtt_user> -P <mqtt_pass> -t "manttoai/#" -v
   ```

3. Verificar llegada de payload JSON con `temperatura`, `humedad`, `vib_x`, `vib_y`, `vib_z`.
4. Confirmar persistencia en backend consultando lecturas del equipo.
5. Confirmar visualización en dashboard (`/dashboard` y detalle de equipo).

## Escenario físico objetivo: 3 nodos ESP32 simultáneos

Para la defensa/demo oficial se espera validar 3 nodos en paralelo.

### 1) Configurar cada nodo con `EQUIPO_ID` distinto

Usar el mismo broker/credenciales y cambiar solo `EQUIPO_ID` en cada placa:

- Nodo A -> `EQUIPO_ID=1`
- Nodo B -> `EQUIPO_ID=2`
- Nodo C -> `EQUIPO_ID=3`

### 2) Verificar publicación simultánea en broker

```bash
mosquitto_sub -h <broker> -u <mqtt_user> -P <mqtt_pass> -t "manttoai/#" -v
```

Resultado esperado: mensajes intercalados para `.../1/lecturas`, `.../2/lecturas`, `.../3/lecturas`.

### 3) Verificar persistencia y dashboard para los 3 equipos

Desde la raíz del repo:

```bash
python scripts/verify_three_nodes.py --api-url "http://localhost:8000" --equipos "1,2,3" --auth-email "admin@manttoai.local" --ventana-minutos 10 --max-desfase-segundos 120
```

También disponible como atajo:

```bash
make verify-3-nodes
```

> Si no definís `VERIFY_ADMIN_PASSWORD`, el script pedirá password en un prompt oculto.
> Para ejecución no interactiva, definir `VERIFY_ADMIN_PASSWORD` en el entorno antes de ejecutar.

### 4) Evidencia mínima recomendada

- Captura de `mosquitto_sub` con los 3 topics activos.
- Salida del script `verify_three_nodes.py` en verde.
- Captura de Dashboard mostrando 3 equipos con telemetría activa.

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
python iot/simulator/mqtt_simulator.py --host localhost --port 1883 --username <mqtt_user> --password <mqtt_pass> --count 5 --interval 1
```

Compatibilidad hacia atrás:

```bash
python iot/simulator/mqtt_simulator.py --host localhost --port 1883 --username <mqtt_user> --password <mqtt_pass> --equipo-id 1 --count 5
```

### Multi-equipo

```bash
python iot/simulator/mqtt_simulator.py --host localhost --port 1883 --username <mqtt_user> --password <mqtt_pass> --devices 3 --count 5 --interval 0.5
```

### Datos reproducibles

```bash
python iot/simulator/mqtt_simulator.py --host localhost --port 1883 --username <mqtt_user> --password <mqtt_pass> --devices 2 --count 5 --seed 42
```

### Topic prefix personalizado

```bash
python iot/simulator/mqtt_simulator.py --host localhost --port 1883 --username <mqtt_user> --password <mqtt_pass> --topic-prefix "manttoai/equipo" --devices 2
```

### IDs iniciales personalizados

```bash
python iot/simulator/mqtt_simulator.py --host localhost --port 1883 --username <mqtt_user> --password <mqtt_pass> --devices 2 --start-id 10 --count 3
```

Publica en:

- `manttoai/equipo/10/lecturas`
- `manttoai/equipo/11/lecturas`

## Escuchar mensajes publicados

```bash
mosquitto_sub -h localhost -u <mqtt_user> -P <mqtt_pass> -t "manttoai/#" -v
```
