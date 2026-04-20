/*
 * ENEL 678 - Group 01: Final DLR Prototype Demonstration
 * Hardware Mapping:
 * A0 -> Temperature (TMP36)
 * A1 -> Wind Sensor
 * A2 -> Solar / Light Sensor
 *
 * Python-ready serial output format:
 * temp_c,wind_ms,light_voltage,solar_percent
 */

const int tmp36Pin = A0;
const int windPin = A1;
const int lightSensorPin = A2;

void setup() {
  Serial.begin(9600);
  delay(1000);

  // Header line for Python / Excel logging
  Serial.println("temp_c,wind_ms,light_voltage,solar_percent");
}

void loop() {

  // ---------- TEMPERATURE ----------
  int rawTemp = analogRead(tmp36Pin);
  delay(50);

  float vTemp = rawTemp * (5.0 / 1023.0);
  float ambientC = (vTemp - 0.5) * 100.0;   // TMP36 formula


  // ---------- WIND SPEED ----------
  int rawWind = analogRead(windPin);
  delay(50);

  float vWind = rawWind * (5.0 / 1023.0);

  float windSpeed = 0.0;
  if (vWind >= 0.4) {
    windSpeed = (vWind - 0.4) * (32.4 / 1.6);
  }


  // ---------- SOLAR SENSOR ----------
  int rawLight = analogRead(lightSensorPin);
  delay(50);

  float vLight = rawLight * (5.0 / 1023.0);

  // FIXED solar calculation (uses full ADC range)
  float solarPercent = (rawLight / 1023.0) * 100.0;


  // ---------- SERIAL OUTPUT FOR PYTHON ----------
  Serial.print(ambientC, 1);
  Serial.print(",");

  Serial.print(windSpeed, 2);
  Serial.print(",");

  Serial.print(vLight, 2);
  Serial.print(",");

  Serial.println(solarPercent, 1);


  delay(800);
}
