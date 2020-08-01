#include <ESP8266WiFi.h>
#include <Wire.h>
#include <IRremoteESP8266.h>
#include <IRsend.h>

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

WiFiClient client;

const uint16_t IR_LED_PIN = 4; //GPIO 2
IRsend irsend(IR_LED_PIN);

uint16_t result1[] = {};
uint16_t result2[] = {};
uint16_t result3[] = {};
uint16_t result4[] = {};


void setup() {
    // Serial communication is used for debugging
    Serial.begin(115200);

    // We start by connecting to a WiFi network
    Serial.println(); Serial.println();
    Serial.print("Connecting to ");
    Serial.println(ssid);

    WiFi.mode(WIFI_STA);    
    WiFi.config( ip, gateway, subnet );
    WiFi.begin(ssid, password);

    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }

    Serial.println("");
    Serial.println("WiFi connected");
    Serial.println("IP address: ");
    Serial.println(WiFi.localIP());
    Serial.print("connecting to ");
    Serial.print(host);
    Serial.print(':');
    Serial.println(port);
  
    // create TCP connections
    if (!client.connect(host, port)) {
        Serial.println("connection failed"); 
        delay(1000); 
        return;
    }


}

void loop() {
    while (client.connected()) {
        if (client.available()) {
            int input = client.parseInt();
            while (client.available()) {
                client.read();
            }

            switch (input) {
                case 10: {                 // record preset 1
                    break;
                }
                case 11: {                 // emmit preset 1
                    irsend.sendRaw(result1, sizeof(result1)/sizeof(result1[0]), 38);
                    break;
                }
                case 20: {                 // record preset 2
                    break;
                }
                case 21: {                 // emmit preset 2
                    irsend.sendRaw(result1, sizeof(result2)/sizeof(result2[0]), 38);
                    break;
                }
                case 30: {                 // record preset 3
                    break;
                }
                case 31: {                 // emmit preset 3
                    irsend.sendRaw(result1, sizeof(result3)/sizeof(result3[0]), 38);
                    break;
                }
                case 40: {                 // record preset 4
                    break;
                }
                case 41: {                 // emmit preset 4
                    irsend.sendRaw(result1, sizeof(result4)/sizeof(result4[0]), 38);
                    break;
                }
            }
        }

    }
    setup();
}
