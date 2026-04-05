// Configuración mínima del firmware ESP32 para entorno de demo.
// Importante: no subas credenciales reales al repositorio.

#pragma once

static const char* WIFI_SSID = "REEMPLAZAR_SSID";
static const char* WIFI_PASSWORD = "REEMPLAZAR_PASSWORD";

static const char* MQTT_HOST = "192.168.1.10";
static const int MQTT_PORT = 1883;
static const char* MQTT_USERNAME = "";
static const char* MQTT_PASSWORD = "";
static const int EQUIPO_ID = 1;

static const unsigned long MQTT_PUBLISH_INTERVAL_MS = 5000;
static const unsigned long WIFI_RETRY_INTERVAL_MS = 5000;
static const unsigned long MQTT_RETRY_INTERVAL_MS = 3000;
static const unsigned long MAIN_LOOP_DELAY_MS = 1000;
