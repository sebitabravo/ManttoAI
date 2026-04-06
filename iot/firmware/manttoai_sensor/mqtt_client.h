// Funciones de conectividad WiFi/MQTT del firmware ESP32.

#pragma once

#include "sensors.h"

void setupMqttClient();
void maintainMqttConnection();
void publishSensorReading(const SensorSnapshot& snapshot);
