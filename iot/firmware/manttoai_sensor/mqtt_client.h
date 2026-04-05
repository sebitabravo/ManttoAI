// Funciones de conectividad WiFi/MQTT del firmware ESP32.

#pragma once

void setupMqttClient();
void maintainMqttConnection();
void publishSensorReading();
