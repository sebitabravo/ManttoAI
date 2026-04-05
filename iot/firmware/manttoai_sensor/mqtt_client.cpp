// Implementación real de conexión WiFi y publicación MQTT.

#ifdef ARDUINO

#include <Arduino.h>
#include <PubSubClient.h>
#include <WiFi.h>

#include <cmath>
#include <cstdio>

#include "config.h"
#include "mqtt_client.h"
#include "sensors.h"

namespace {
WiFiClient wifi_client;
PubSubClient mqtt_client(wifi_client);

char mqtt_topic[64] = {0};
unsigned long last_publish_ms = 0;
unsigned long last_wifi_retry_ms = 0;
unsigned long last_mqtt_retry_ms = 0;
bool wifi_was_connected = false;
bool mqtt_was_connected = false;

void buildMqttTopic() {
  const int written = std::snprintf(
      mqtt_topic,
      sizeof(mqtt_topic),
      "manttoai/equipo/%d/lecturas",
      EQUIPO_ID);

  if (written <= 0 || static_cast<size_t>(written) >= sizeof(mqtt_topic)) {
    mqtt_topic[0] = '\0';
    Serial.println("[mqtt] ERROR: topic inválido por tamaño.");
  }
}

void connectWifiIfNeeded() {
  if (WiFi.status() == WL_CONNECTED) {
    return;
  }

  const unsigned long now = millis();
  if (now - last_wifi_retry_ms < WIFI_RETRY_INTERVAL_MS) {
    return;
  }

  last_wifi_retry_ms = now;
  Serial.print("[mqtt] Conectando WiFi SSID: ");
  Serial.println(WIFI_SSID);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
}

void syncWifiConnectionLogs() {
  const bool wifi_connected = WiFi.status() == WL_CONNECTED;
  if (wifi_connected && !wifi_was_connected) {
    Serial.print("[mqtt] WiFi conectado. IP local: ");
    Serial.println(WiFi.localIP());
  }

  if (!wifi_connected && wifi_was_connected) {
    Serial.println("[mqtt] WiFi desconectado. Reintentando conexión...");
  }

  wifi_was_connected = wifi_connected;
}

void connectMqttIfNeeded() {
  if (WiFi.status() != WL_CONNECTED || mqtt_client.connected()) {
    return;
  }

  const unsigned long now = millis();
  if (now - last_mqtt_retry_ms < MQTT_RETRY_INTERVAL_MS) {
    return;
  }

  last_mqtt_retry_ms = now;

  char client_id[48] = {0};
  std::snprintf(client_id, sizeof(client_id), "manttoai-esp32-%d", EQUIPO_ID);

  Serial.print("[mqtt] Conectando broker ");
  Serial.print(MQTT_HOST);
  Serial.print(":");
  Serial.println(MQTT_PORT);

  const bool use_auth =
      MQTT_USERNAME != nullptr &&
      MQTT_PASSWORD != nullptr &&
      MQTT_USERNAME[0] != '\0' &&
      MQTT_PASSWORD[0] != '\0';

  const bool connected = use_auth
      ? mqtt_client.connect(client_id, MQTT_USERNAME, MQTT_PASSWORD)
      : mqtt_client.connect(client_id);

  if (!connected) {
    Serial.print("[mqtt] Falló conexión MQTT. state=");
    Serial.println(mqtt_client.state());
  }
}

void syncMqttConnectionLogs() {
  const bool mqtt_connected = mqtt_client.connected();
  if (mqtt_connected && !mqtt_was_connected) {
    Serial.print("[mqtt] Broker conectado. Topic publicación: ");
    Serial.println(mqtt_topic);
  }

  if (!mqtt_connected && mqtt_was_connected) {
    Serial.println("[mqtt] Broker desconectado. Reintentando conexión...");
  }

  mqtt_was_connected = mqtt_connected;
}

bool buildPayload(char* payload, size_t payload_size) {
  const float temperatura = readTemperature();
  const float humedad = readHumidity();
  const float vib_x = readVibrationX();
  const float vib_y = readVibrationY();
  const float vib_z = readVibrationZ();

  const bool has_nan =
      std::isnan(temperatura) ||
      std::isnan(humedad) ||
      std::isnan(vib_x) ||
      std::isnan(vib_y) ||
      std::isnan(vib_z);

  if (has_nan) {
    Serial.println("[mqtt] Lectura inválida de sensores. Se omite publicación.");
    return false;
  }

  const int written = std::snprintf(
      payload,
      payload_size,
      "{\"temperatura\":%.2f,\"humedad\":%.2f,\"vib_x\":%.3f,\"vib_y\":%.3f,\"vib_z\":%.3f}",
      temperatura,
      humedad,
      vib_x,
      vib_y,
      vib_z);

  if (written <= 0 || static_cast<size_t>(written) >= payload_size) {
    Serial.println("[mqtt] Payload inválido por tamaño insuficiente.");
    return false;
  }

  return true;
}
}  // namespace

void setupMqttClient() {
  buildMqttTopic();
  if (mqtt_topic[0] == '\0') {
    Serial.println("[mqtt] ERROR: no se puede iniciar MQTT sin topic válido.");
    return;
  }

  WiFi.mode(WIFI_STA);
  mqtt_client.setServer(MQTT_HOST, MQTT_PORT);

  Serial.print("[mqtt] Topic objetivo: ");
  Serial.println(mqtt_topic);

  const bool use_auth =
      MQTT_USERNAME != nullptr &&
      MQTT_PASSWORD != nullptr &&
      MQTT_USERNAME[0] != '\0' &&
      MQTT_PASSWORD[0] != '\0';
  Serial.print("[mqtt] Autenticación broker: ");
  Serial.println(use_auth ? "habilitada" : "deshabilitada");

  connectWifiIfNeeded();
  connectMqttIfNeeded();
}

void maintainMqttConnection() {
  connectWifiIfNeeded();
  syncWifiConnectionLogs();

  if (WiFi.status() != WL_CONNECTED) {
    if (mqtt_client.connected()) {
      mqtt_client.disconnect();
    }
    syncMqttConnectionLogs();
    return;
  }

  connectMqttIfNeeded();
  if (mqtt_client.connected()) {
    mqtt_client.loop();
  }
  syncMqttConnectionLogs();
}

void publishSensorReading() {
  if (mqtt_topic[0] == '\0' || !mqtt_client.connected()) {
    return;
  }

  const unsigned long now = millis();
  if (last_publish_ms != 0 && now - last_publish_ms < MQTT_PUBLISH_INTERVAL_MS) {
    return;
  }

  last_publish_ms = now;
  char payload[192] = {0};
  if (!buildPayload(payload, sizeof(payload))) {
    return;
  }

  const bool published = mqtt_client.publish(mqtt_topic, payload);
  if (published) {
    Serial.print("[mqtt] Lectura publicada: ");
    Serial.println(payload);
  } else {
    Serial.println("[mqtt] Falló publicación de lectura.");
  }
}

#else

#include <cstdio>

#include "mqtt_client.h"

void setupMqttClient() {
  std::puts("Inicializando cliente MQTT (modo no-ARDUINO)...");
}

void maintainMqttConnection() {}

void publishSensorReading() {
  std::puts("Publicando lectura MQTT (modo no-ARDUINO)...");
}

#endif
