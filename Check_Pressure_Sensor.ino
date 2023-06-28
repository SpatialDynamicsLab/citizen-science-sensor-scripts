#include <Arduino.h>
#include <Wire.h>
#include <SparkFun_MS5803_I2C.h>

MS5803 sensor(ADDRESS_HIGH);

void setup()
{
  Serial.begin(115200);
  Wire.begin();
  sensor.reset();
  sensor.begin();
}

void loop()
{
  // Read pressure value from the sensor
  double pressure = sensor.getPressure(ADC_4096);

  // Check if the pressure value is within a valid range
  if (pressure >= 0 && pressure <= 200)
  {
    Serial.print("Pressure reading: ");
    Serial.print(pressure);
    Serial.println(" mbar");
  }
  else
  {
    Serial.println("Invalid pressure reading. Sensor may not be working properly.");
  }

  // Delay between readings
  delay(1000);
}
