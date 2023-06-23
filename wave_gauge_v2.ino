#include <Wire.h>
#include <SparkFun_MS5803_I2C.h>
#include <SD.h>
#include "RTClib.h"
#include <TimerOne.h>

// Begin class with selected address
// available addresses (selected by jumper on board)
// default is ADDRESS_HIGH
// ADDRESS_HIGH = 0x44
// ADDRESS_LOW  = 0x45
MS5803 sensor(ADDRESS_HIGH);
double pressure_abs;

// Set Variables for Intermittent SD logging
String Stringfile = String("");
int n = 1;

int Year, Month, Day, Hour, Minute, Second; // variables to differentiate time elements
RTC_DS3231 rtc;                              // define the Real-Time Clock object

const int chipSelect = 4; // digital pin 10 for SD cs
volatile boolean flag = true;
int led = LED_BUILTIN;

// Variables for water height and wave speed
double water_height = 0.0;
unsigned long previous_pressure_time = 0;
double max_pressure = 0.0;
double wave_speed = 0.0;

// the logging file
File logfile;

/**
 * @brief Prints an error message and enters an infinite loop
 *
 * @param str The error message to print
 */
void error(char *str)
{
  Serial.print("error: ");
  Serial.println(str);

  // red LED indicates error
  // digitalWrite(redLEDpin, HIGH);

  while (1);
}

void setup()
{
  // disable ADC
  ADCSRA = 0;
  // set a timer of length 62500/100000/125000 for 16/10/8 Hz sampling, respectively
  Timer1.initialize(100000);
  Timer1.attachInterrupt(timerIsr); // attach the service routine here

  // initialize digital pin 13 as an output. This will indicate that the power is connected and will flash approx. every 5 seconds
  // pinMode(13, OUTPUT);
  pinMode(led, OUTPUT);

  Serial.begin(115200);
  sensor.reset();
  sensor.begin();
  pressure_abs = sensor.getPressure(ADC_4096);
  DateTime now = rtc.now();
  Year = now.year();
  Month = now.month();
  Day = now.day();
  Hour = now.hour();
  Minute = now.minute();
  Second = now.second();
  Serial.println();

#if WAIT_TO_START
  Serial.println("Type any character to start");
  while (!Serial.available());
#endif //WAIT_TO_START

  // initialize the SD card
  Serial.print("Initializing SD card...");
  // make sure that the default chip select pin is set to
  // output, even if you don't use it:
  pinMode(10, OUTPUT);

  // see if the card is present and can be initialized:
  if (!SD.begin(chipSelect))
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

  // connect to RTC
  rtc.begin();
  Wire.begin();
  if (!rtc.begin())
  {
    logfile.println("RTC failed");
#if ECHO_TO_SERIAL
    Serial.println("RTC failed");
#endif //ECHO_TO_SERIAL
  }
  logfile.println("date, time, pressure, height, wave_speed"); //++++++++++++++++++++++++ CREATING HEADERS
#if ECHO_TO_SERIAL
  Serial.println("date, time, pressure, height, wave_speed");
#endif //ECHO_TO_SERIAL
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

  if (millis() % 1000 == 0)
  {
    digitalWrite(led, HIGH);
    digitalWrite(led, LOW);
  }
  if (flag == true)
  {
    pressure_abs = sensor.getPressure(ADC_4096);
    DateTime now = rtc.now();
    Year = now.year();
    Month = now.month();
    Day = now.day();
    Hour = now.hour();
    Minute = now.minute();
    Second = now.second();

    // Calculate water height in centimeters (pressure / 10)
    water_height = pressure_abs / 10.0;

    // Calculate wave speed in cm/s (time between two maximum pressure readings)
    if (pressure_abs > max_pressure)
    {
      max_pressure = pressure_abs;
      previous_pressure_time = millis();
    }
    else if (millis() - previous_pressure_time >= 1000)
    {
      wave_speed = water_height / ((millis() - previous_pressure_time) / 1000.0);
      max_pressure = pressure_abs;
      previous_pressure_time = millis();
    }

    // print the results to the Serial Monitor:
    // Serial.print("sensor = ");
    // Serial.print(pressure_abs);
    // Serial.print("\t date = ");
    // Serial.print(Year);
    // Serial.print("/");
    // Serial.print(Month);
    // Serial.print("/");
    // Serial.print(Day);
    // Serial.print("\t time = ");
    // Serial.print(Hour);
    // Serial.print(":");
    // Serial.print(Minute);
    // Serial.print(":");
    // Serial.println(Second);

    // Write to SD card:
    Stringfile += String(Year);
    Stringfile += "/";
    Stringfile += String(Month);
    Stringfile += "/";
    Stringfile += String(Day);
    Stringfile += ", ";
    Stringfile += String(Hour);
    Stringfile += ":";
    Stringfile += String(Minute);
    Stringfile += ":";
    Stringfile += String(Second);
    Stringfile += ", ";
    Stringfile += String(pressure_abs);
    Stringfile += ", ";
    Stringfile += String(water_height);
    Stringfile += ", ";
    Stringfile += String(wave_speed);
    Stringfile += "\r\n";
    flag = false;
    n = n + 1;
  }
}

/**
 * @brief Interrupt service routine for Timer1 interrupt
 */
void timerIsr()
{
  flag = true;
}
