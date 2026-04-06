// Funciones de lectura de sensores del scaffold.

#pragma once

struct SensorSnapshot {
  float temperatura;
  float humedad;
  float vib_x;
  float vib_y;
  float vib_z;
  bool valid;
};

void setupSensors();
SensorSnapshot readSensorSnapshot();
bool isSensorSnapshotValid(const SensorSnapshot& snapshot);
float readTemperature();
float readHumidity();
float readVibrationX();
float readVibrationY();
float readVibrationZ();
void logSensorReadings(const SensorSnapshot& snapshot);
