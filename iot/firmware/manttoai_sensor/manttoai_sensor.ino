// Firmware base del ESP32 para ManttoAI.

#include "config.h"
#include "mqtt_client.h"
#include "sensors.h"

void setup() {
  Serial.begin(115200);
  setupSensors();
  setupMqttClient();
}

void loop() {
  maintainMqttConnection();
  const SensorSnapshot snapshot = readSensorSnapshot();
  logSensorReadings(snapshot);
  publishSensorReading(snapshot);
  delay(MAIN_LOOP_DELAY_MS);
}
