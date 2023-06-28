#include <Arduino.h>
#include <SD.h>

// Set Variables for Intermittent SD logging
String Stringfile = String("");
int n = 1;

// Variables for water height and wave speed
double water_height = 0.0;
double wave_speed = 0.0;

// the logging file
File logfile;

/**
 * @brief Prints an error message and enters an infinite loop
 *
 * @param str The error message to print
 */
void error(const char *str)
{
  Serial.print("error: ");
  Serial.println(str);

  while (1)
    ;
}

void setup()
{
  Serial.begin(115200);

  // initialize the SD card
  Serial.print("Initializing SD card...");
  pinMode(SS, OUTPUT);

  if (!SD.begin(SS))
  {
    error("Card failed, or not present");
  }
  Serial.println("card initialized.");

  // create a new file
  char filename[] = "LOGGER00.CSV";
  for (uint8_t i = 0; i < 100; i++)
  {
    filename[6] = i / 10 + '0';
    filename[7] = i % 10 + '0';
    if (!SD.exists(filename))
    {
      // only open a new file if it doesn't exist
      logfile = SD.open(filename, FILE_WRITE);
      break; // leave the loop!
    }
  }

  if (!logfile)
  {
    error("couldn't create file");
  }

  Serial.print("Logging to: ");
  Serial.println(filename);

  // Initialize random seed
  randomSeed(analogRead(0));
}

void loop()
{
  if (n == 11)
  {
    Serial.print(Stringfile);
    logfile.print(Stringfile);
    logfile.flush();
    Stringfile.replace(Stringfile, "");
    n = n - 10;
  }

  // Simulate sensor readings
  double pressure_abs = simulatePressure();
  double water_height = simulateWaterHeight();
  double wave_speed = simulateWaveSpeed();

  // Write to SD card and store in a string
  Stringfile += String(pressure_abs);
  Stringfile += ", ";
  Stringfile += String(water_height);
  Stringfile += ", ";
  Stringfile += String(wave_speed);
  Stringfile += "\r\n";

  // Print simulated values to Serial Monitor
  Serial.print("Pressure: ");
  Serial.print(pressure_abs);
  Serial.print(", Water Height: ");
  Serial.print(water_height);
  Serial.print(", Wave Speed: ");
  Serial.println(wave_speed);

  // Increment counter
  n++;

  // Delay between readings
  delay(1000);
}

/**
 * @brief Generates a simulated pressure value
 *
 * @return Simulated pressure value
 */
double simulatePressure()
{
  // Generate a random pressure value within the expected range
  double pressure = random(1000, 2000) / 10.0;
  return pressure;
}

/**
 * @brief Generates a simulated water height value
 *
 * @return Simulated water height value
 */
double simulateWaterHeight()
{
  // Generate a random water height value within the expected range
  double waterHeight = random(0, 100) / 100.0;
  return waterHeight;
}

/**
 * @brief Generates a simulated wave speed value
 *
 * @return Simulated wave speed value
 */
double simulateWaveSpeed()
{
  // Generate a random wave speed value within the expected range
  double waveSpeed = random(0, 100) / 10.0;
  return waveSpeed;
}
