# Pinout ESP32 (DHT22 + MPU-6050)

## Tabla de conexiones

| Pin ESP32 | Sensor | Descripción |
|-----------|--------|-------------|
| GPIO 4 | DHT22 DATA | Señal digital temperatura/humedad |
| GPIO 21 | MPU-6050 SDA | Bus I2C datos |
| GPIO 22 | MPU-6050 SCL | Bus I2C reloj |
| 3V3 | DHT22 VCC / MPU-6050 VCC | Alimentación de sensores |
| GND | DHT22 GND / MPU-6050 GND | Tierra común |

## Notas de armado

- DHT22 (vista frontal, grilla hacia vos):
  1. VCC
  2. DATA
  3. NC (sin conexión)
  4. GND
- Agregar resistencia pull-up de **10kΩ** entre DATA (pin 2 de DHT22) y 3V3.
- El pin **INT** del MPU-6050 no se usa en este firmware MVP.
- Mantener tierra compartida entre ESP32 y ambos sensores para lecturas estables.
