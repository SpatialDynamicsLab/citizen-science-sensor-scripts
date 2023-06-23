#include <SD.h>
#include <Adafruit_MQTT.h>
#include <Adafruit_MQTT_Client.h>

#define SD_CS_PIN 10
#define SERIAL_BAUD_RATE 9600
#define MQTT_SERVER "your-mqtt-server"
#define MQTT_PORT 1883
#define MQTT_USERNAME "your-mqtt-username"
#define MQTT_PASSWORD "your-mqtt-password"
#define MQTT_TOPIC "your-mqtt-topic"

File dataFile;

// Create an MQTT client instance
WiFiClient client;
Adafruit_MQTT_Client mqtt(Client, MQTT_SERVER, MQTT_PORT, MQTT_USERNAME, MQTT_PASSWORD);

void setup() {
  // Initialize the serial connection
  Serial.begin(SERIAL_BAUD_RATE);
  
  // Initialize the SD card
  if (!SD.begin(SD_CS_PIN)) {
    Serial.println("SD card initialization failed!");
    while (1);
  }
  
  // Connect to Wi-Fi network or smartphone hotspot
  // Code for connecting to Wi-Fi or smartphone hotspot
  
  // Connect to the MQTT broker
  if (!mqtt.connected()) {
    Serial.println("Connecting to MQTT broker...");
    int8_t ret;
    while ((ret = mqtt.connect()) != 0) {
      Serial.println(mqtt.connectErrorString(ret));
      Serial.println("Retrying MQTT connection in 5 seconds...");
      mqtt.disconnect();
      delay(5000);
    }
    Serial.println("MQTT connected!");
  }
}

void loop() {
  // Read the collected data from the SD card
  dataFile = SD.open("data.txt", FILE_READ);
  if (dataFile) {
    while (dataFile.available()) {
      String data = dataFile.readStringUntil('\n');
      
      // Send the data to the API via MQTT
      Adafruit_MQTT_Publish dataPublish = Adafruit_MQTT_Publish(&mqtt, MQTT_TOPIC);
      if (dataPublish.publish(data.c_str())) {
        Serial.println("Data sent to API via MQTT!");
      } else {
        Serial.println("Failed to send data to API via MQTT!");
      }
    }
    
    // Close the file and delete it
    dataFile.close();
    SD.remove("data.txt");
  }
  
  // Other code or delay for collecting more data from sensors
  
  // Handle MQTT connections and keep alive
  mqtt.processPackets(10000);
  if (!mqtt.ping()) {
    mqtt.disconnect();
  }
}
