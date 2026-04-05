// Implementación demo de publicación MQTT.

#ifdef ARDUINO
#include <Arduino.h>
#else
#include <cstdio>

struct SerialShim {
  void println(const char* message) { std::puts(message); }
};

static SerialShim Serial;
#endif

#include "mqtt_client.h"

void setupMqttClient() {
  Serial.println("Inicializando cliente MQTT demo...");
}

void maintainMqttConnection() {}

void publishSensorReading() {
  Serial.println("Publicando lectura demo...");
}
