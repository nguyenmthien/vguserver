#include <ESP8266WiFi.h>
#include <Wire.h>
#include "Adafruit_Si7021.h"

#ifndef STASSID
#define STASSID "nguyenmthien"
#define STAPSK  "299792458"
#define SLEEP_CONVERSION 10e6 //in microseconds
#define I2C_MASTER 0x02
#define I2C_SLAVE 0x40
#endif

const char* ssid     = STASSID;
const char* password = STAPSK;

IPAddress ip( 192, 168, 0, 128 );
IPAddress gateway( 192, 168, 0, 1);
IPAddress subnet( 255, 255, 255, 0);

const char* host    = "192.168.0.100";
const uint16_t port = 2033;

uint16_t sleeptime = 60;

Adafruit_Si7021 sensor = Adafruit_Si7021();

void setup() {
    Serial.begin(115200);

    // We start by connecting to a WiFi network

    Serial.println(); Serial.println();
    Serial.print("Connecting to ");
    Serial.println(ssid);

    WiFi.mode(WIFI_STA);    
    //WiFi.config( ip, gateway, subnet );
    WiFi.begin(ssid, password);

    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }

    Serial.println("");
    Serial.println("WiFi connected");
    Serial.println("IP address: ");
    Serial.println(WiFi.localIP());

    Serial.println("Starting sensor");
    if (!sensor.begin()) {
      Serial.println("Did not find Si7021 sensor!");
      while (true)
        ;
    }
}

void loop() {
  Serial.print("connecting to ");
  Serial.print(host);
  Serial.print(':');
  Serial.println(port);

  // Use WiFiClient class to create TCP connections
  WiFiClient client;
  if (!client.connect(host, port)) {
    Serial.println("connection failed"); 
    delay(1000); 
    return;
  }

  // Get data from sensor
  Serial.println("getting data from sensor");
  String message = "";
  message = String(sensor.readTemperature(), 1) + " " + String(sensor.readHumidity(), 0);
  Serial.println(message);


  // This will send a string to the server
  Serial.println("sending data to server");
  if (client.connected()) { 
    client.println(message);
  }

  String input_str = "";
  
  while (client.available()) {
     int input_byte = client.read() ; 
     input_str.concat(input_byte);  
  }                     

  sleeptime = input_str.toInt();

  // Close the connection
  Serial.println();
  Serial.println("closing connection");
  client.stop();

  ESP.deepSleep(sleeptime*SLEEP_CONVERSION);
}
