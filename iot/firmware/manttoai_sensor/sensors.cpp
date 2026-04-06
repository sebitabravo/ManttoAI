// Lectura real de sensores DHT22 + MPU-6050.

#include "sensors.h"

#ifdef ARDUINO

#include <Arduino.h>
#include <DHT.h>
#include <Wire.h>

#include <cmath>

namespace {
constexpr uint8_t DHT_PIN = 4;
constexpr uint8_t I2C_SDA_PIN = 21;
constexpr uint8_t I2C_SCL_PIN = 22;
constexpr uint8_t MPU6050_ADDRESS = 0x68;
constexpr uint8_t MPU6050_REG_PWR_MGMT_1 = 0x6B;
constexpr uint8_t MPU6050_REG_ACCEL_CONFIG = 0x1C;
constexpr uint8_t MPU6050_REG_ACCEL_XOUT_H = 0x3B;
constexpr uint8_t MPU6050_REG_WHO_AM_I = 0x75;
constexpr float MPU6050_ACCEL_SCALE = 16384.0F;  // ±2g
constexpr uint8_t MPU_RECOVERY_FAILURE_THRESHOLD = 3;
constexpr unsigned long MPU_RECOVERY_BACKOFF_MS = 5000;

DHT dht(DHT_PIN, DHT22);
bool mpu_ready = false;
uint8_t consecutive_mpu_failures = 0;
unsigned long next_mpu_recovery_ms = 0;

void resetMpuFailureTracking() {
  consecutive_mpu_failures = 0;
  next_mpu_recovery_ms = 0;
}

void registerMpuFailure() {
  if (consecutive_mpu_failures < 255) {
    consecutive_mpu_failures++;
  }

  if (consecutive_mpu_failures >= MPU_RECOVERY_FAILURE_THRESHOLD) {
    mpu_ready = false;
    next_mpu_recovery_ms = millis() + MPU_RECOVERY_BACKOFF_MS;
    Serial.println("[sensors] MPU-6050 temporalmente deshabilitado; se aplicará backoff antes de reintentar.");
  }
}

bool writeMpuRegister(uint8_t reg, uint8_t value) {
  Wire.beginTransmission(MPU6050_ADDRESS);
  Wire.write(reg);
  Wire.write(value);
  return Wire.endTransmission(true) == 0;
}

bool readMpuRegister(uint8_t reg, uint8_t& value) {
  Wire.beginTransmission(MPU6050_ADDRESS);
  Wire.write(reg);

  if (Wire.endTransmission(false) != 0) {
    return false;
  }

  if (Wire.requestFrom(MPU6050_ADDRESS, static_cast<uint8_t>(1), true) != 1) {
    return false;
  }

  value = static_cast<uint8_t>(Wire.read());
  return true;
}

bool initializeMpuSensor(uint8_t& mpu_who_am_i) {
  const bool woke_up = writeMpuRegister(MPU6050_REG_PWR_MGMT_1, 0x00);
  const bool accel_range_ok = writeMpuRegister(MPU6050_REG_ACCEL_CONFIG, 0x00);
  const bool who_am_i_ok =
      readMpuRegister(MPU6050_REG_WHO_AM_I, mpu_who_am_i) &&
      mpu_who_am_i == MPU6050_ADDRESS;

  mpu_ready = woke_up && accel_range_ok && who_am_i_ok;
  if (mpu_ready) {
    resetMpuFailureTracking();
  }

  return mpu_ready;
}

void attemptMpuRecoveryIfNeeded() {
  if (mpu_ready) {
    return;
  }

  if (millis() < next_mpu_recovery_ms) {
    return;
  }

  uint8_t mpu_who_am_i = 0;
  if (initializeMpuSensor(mpu_who_am_i)) {
    Serial.println("[sensors] MPU-6050 recuperado tras reintento de comunicación I2C.");
    return;
  }

  next_mpu_recovery_ms = millis() + MPU_RECOVERY_BACKOFF_MS;
  Serial.print("[sensors] Reintento MPU-6050 fallido (WHO_AM_I=0x");
  Serial.print(mpu_who_am_i, HEX);
  Serial.println(")");
}

bool readMpuAccelerationRaw(int16_t& ax, int16_t& ay, int16_t& az) {
  attemptMpuRecoveryIfNeeded();
  if (!mpu_ready) {
    return false;
  }

  Wire.beginTransmission(MPU6050_ADDRESS);
  Wire.write(MPU6050_REG_ACCEL_XOUT_H);

  if (Wire.endTransmission(false) != 0) {
    registerMpuFailure();
    return false;
  }

  constexpr uint8_t bytes_to_read = 6;
  const uint8_t bytes_read = Wire.requestFrom(MPU6050_ADDRESS, bytes_to_read, true);

  if (bytes_read != bytes_to_read) {
    registerMpuFailure();
    return false;
  }

  ax = static_cast<int16_t>((Wire.read() << 8) | Wire.read());
  ay = static_cast<int16_t>((Wire.read() << 8) | Wire.read());
  az = static_cast<int16_t>((Wire.read() << 8) | Wire.read());
  resetMpuFailureTracking();
  return true;
}

float readAxisInG(char axis) {
  if (!mpu_ready) {
    return NAN;
  }

  int16_t ax = 0;
  int16_t ay = 0;
  int16_t az = 0;
  if (!readMpuAccelerationRaw(ax, ay, az)) {
    return NAN;
  }

  switch (axis) {
    case 'x':
      return static_cast<float>(ax) / MPU6050_ACCEL_SCALE;
    case 'y':
      return static_cast<float>(ay) / MPU6050_ACCEL_SCALE;
    case 'z':
      return static_cast<float>(az) / MPU6050_ACCEL_SCALE;
    default:
      return NAN;
  }
}

void printLabeledValue(const char* label, float value, uint8_t decimals) {
  Serial.print(label);
  if (isnan(value)) {
    Serial.print("N/A");
  } else {
    Serial.print(value, decimals);
  }
}
}  // namespace

void setupSensors() {
  dht.begin();

  Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN);
  Wire.setTimeOut(50);
  delay(100);

  uint8_t mpu_who_am_i = 0;
  initializeMpuSensor(mpu_who_am_i);

  Serial.println("[sensors] DHT22 inicializado en GPIO4");
  if (mpu_ready) {
    Serial.println("[sensors] MPU-6050 inicializado en I2C (SDA=21, SCL=22)");
  } else {
    Serial.print("[sensors] ERROR: no se pudo inicializar MPU-6050 (WHO_AM_I=0x");
    Serial.print(mpu_who_am_i, HEX);
    Serial.println(")");
  }
}

SensorSnapshot readSensorSnapshot() {
  const float temperatura = readTemperature();
  const float humedad = readHumidity();
  const float vib_x = readVibrationX();
  const float vib_y = readVibrationY();
  const float vib_z = readVibrationZ();

  return {
      temperatura,
      humedad,
      vib_x,
      vib_y,
      vib_z,
      !std::isnan(temperatura) &&
          !std::isnan(humedad) &&
          !std::isnan(vib_x) &&
          !std::isnan(vib_y) &&
          !std::isnan(vib_z),
  };
}

bool isSensorSnapshotValid(const SensorSnapshot& snapshot) {
  return snapshot.valid;
}

float readTemperature() {
  return dht.readTemperature();
}

float readHumidity() {
  return dht.readHumidity();
}

float readVibrationX() {
  return readAxisInG('x');
}

float readVibrationY() {
  return readAxisInG('y');
}

float readVibrationZ() {
  return readAxisInG('z');
}

void logSensorReadings(const SensorSnapshot& snapshot) {
  Serial.print("[sensors] ");
  printLabeledValue("temp=", snapshot.temperatura, 2);
  Serial.print(" °C | ");
  printLabeledValue("hum=", snapshot.humedad, 2);
  Serial.print(" % | ");
  printLabeledValue("vib_x=", snapshot.vib_x, 3);
  Serial.print(" g | ");
  printLabeledValue("vib_y=", snapshot.vib_y, 3);
  Serial.print(" g | ");
  printLabeledValue("vib_z=", snapshot.vib_z, 3);
  Serial.println(" g");
}

#else

void setupSensors() {}
SensorSnapshot readSensorSnapshot() { return {42.5F, 58.0F, 0.3F, 0.2F, 9.8F, true}; }
bool isSensorSnapshotValid(const SensorSnapshot& snapshot) { return snapshot.valid; }
float readTemperature() { return 42.5F; }
float readHumidity() { return 58.0F; }
float readVibrationX() { return 0.3F; }
float readVibrationY() { return 0.2F; }
float readVibrationZ() { return 9.8F; }
void logSensorReadings(const SensorSnapshot& /*snapshot*/) {}

#endif
