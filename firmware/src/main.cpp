/**
 * Wine Detector - ESP32 with ThingsBoard
 * Trimite date la ThingsBoard prin MQTT
 */

#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <Wire.h>
#include <bsec2.h>
#include "bsec_config.h"

// ============================================
// WiFi Configuration
// ============================================
const char* ssid = "en XC";
const char* password = "necesitamosfinanciacion";

// ============================================
// MQTT Configuration - THINGSBOARD
// ============================================
const char* mqtt_broker = "thingsboard.cloud";
const int mqtt_port = 1883;
const char* tb_access_token = "dXF4HlErrhymJFnV6YQf";  // Token-ul tău
const char* mqtt_topic = "v1/devices/me/telemetry";
const char* mqtt_client_id = "ESP32-WineDetector";

// ============================================
// I2C Multiplexer
// ============================================
#define MUX_ADDR 0x20
#define I2C_SDA 23
#define I2C_SCL 22
#define NUM_SENSORS 8
#define BME68X_ADDR 0x68

// ============================================
// BSEC2 instance
// ============================================
Bsec2 bsec;

// ============================================
// Data storage
// ============================================
struct SensorReading {
    float temperature;
    float humidity;
    float pressure;
    float gasResistance;
    float iaq;
    bool valid;
};
SensorReading allSensors[NUM_SENSORS];
bool sensorPresent[NUM_SENSORS] = {false};

// ============================================
// MQTT Client (fără TLS pentru ThingsBoard Cloud)
// ============================================
WiFiClient espClient;
PubSubClient mqttClient(espClient);

// ============================================
// Timer
// ============================================
unsigned long lastPublish = 0;
const unsigned long publishInterval = 3000;

// ============================================
// Delay function for BSEC
// ============================================
void myDelayUs(uint32_t period, void *intfPtr) {
    delayMicroseconds(period);
}

// ============================================
// Select channel on multiplexer
// ============================================
void muxSelect(uint8_t channel) {
    if (channel > 7) return;
    Wire.beginTransmission(MUX_ADDR);
    Wire.write(1 << channel);
    Wire.endTransmission();
    delay(50);
}

// ============================================
// Check if sensor exists on current channel
// ============================================
bool sensorExists() {
    Wire.beginTransmission(BME68X_ADDR);
    return (Wire.endTransmission() == 0);
}

// ============================================
// Initialize BSEC for current sensor
// ============================================
bool initBSECForSensor() {
    if (!bsec.begin(BME68X_ADDR, Wire, myDelayUs)) {
        return false;
    }
    if (!bsec.setConfig(bsec_config)) {
        // Continue even if config fails
    }
    bsec_virtual_sensor_t sensorList[] = {
        BSEC_OUTPUT_SENSOR_HEAT_COMPENSATED_TEMPERATURE,
        BSEC_OUTPUT_SENSOR_HEAT_COMPENSATED_HUMIDITY,
        BSEC_OUTPUT_RAW_PRESSURE,
        BSEC_OUTPUT_RAW_GAS,
        BSEC_OUTPUT_IAQ
    };
    if (!bsec.updateSubscription(sensorList, 5, 0.05f)) {
        return false;
    }
    return true;
}

// ============================================
// Read current sensor
// ============================================
bool readCurrentSensor(SensorReading &reading) {
    unsigned long start = millis();
    while (millis() - start < 2000) {
        if (bsec.run()) {
            const bsecOutputs *outputs = bsec.getOutputs();
            if (outputs && outputs->nOutputs > 0) {
                for (uint8_t i = 0; i < outputs->nOutputs; i++) {
                    const bsecData &out = outputs->output[i];
                    switch (out.sensor_id) {
                        case BSEC_OUTPUT_SENSOR_HEAT_COMPENSATED_TEMPERATURE:
                            reading.temperature = out.signal;
                            break;
                        case BSEC_OUTPUT_SENSOR_HEAT_COMPENSATED_HUMIDITY:
                            reading.humidity = out.signal;
                            break;
                        case BSEC_OUTPUT_RAW_PRESSURE:
                            reading.pressure = out.signal * 0.01f;
                            break;
                        case BSEC_OUTPUT_RAW_GAS:
                            reading.gasResistance = out.signal;
                            break;
                        case BSEC_OUTPUT_IAQ:
                            reading.iaq = out.signal;
                            break;
                    }
                }
                reading.valid = true;
                return true;
            }
        }
        delay(50);
    }
    reading.valid = false;
    return false;
}

// ============================================
// Scan all sensors
// ============================================
void scanSensors() {
    Serial.println("\nScanning sensors...");
    int found = 0;
    for (int i = 0; i < NUM_SENSORS; i++) {
        muxSelect(i);
        if (sensorExists()) {
            sensorPresent[i] = true;
            found++;
            Serial.printf("  Sensor %d: detected\n", i);
        } else {
            sensorPresent[i] = false;
            Serial.printf("  Sensor %d: NOT detected\n", i);
        }
    }
    Serial.printf("\nFound %d/%d sensors\n", found, NUM_SENSORS);
}

// ============================================
// Read all sensors
// ============================================
void readAllSensors() {
    for (int i = 0; i < NUM_SENSORS; i++) {
        if (!sensorPresent[i]) continue;
        
        muxSelect(i);
        Serial.printf("Reading sensor %d... ", i);
        
        if (initBSECForSensor()) {
            SensorReading reading;
            if (readCurrentSensor(reading)) {
                allSensors[i] = reading;
                Serial.printf("OK (T=%.2f, H=%.2f, G=%.0f)\n",
                    reading.temperature, reading.humidity, reading.gasResistance);
            } else {
                allSensors[i].valid = false;
                Serial.println("FAILED (no data)");
            }
        } else {
            allSensors[i].valid = false;
            Serial.println("FAILED (BSEC init)");
        }
    }
}

// ============================================
// Publish data to ThingsBoard (MQTT)
// ============================================
void publishData() {
    if (!mqttClient.connected()) return;

    StaticJsonDocument<2048> doc;
    
    // Format ThingsBoard: chei simple pentru telemetry
    for (int i = 0; i < NUM_SENSORS; i++) {
        if (!sensorPresent[i]) continue;
        if (!allSensors[i].valid) continue;
        
        char key_temp[20], key_hum[20], key_gas[20], key_iaq[20];
        snprintf(key_temp, sizeof(key_temp), "sensor_%d_temp", i);
        snprintf(key_hum, sizeof(key_hum), "sensor_%d_hum", i);
        snprintf(key_gas, sizeof(key_gas), "sensor_%d_gas", i);
        snprintf(key_iaq, sizeof(key_iaq), "sensor_%d_iaq", i);
        
        doc[key_temp] = allSensors[i].temperature;
        doc[key_hum] = allSensors[i].humidity;
        doc[key_gas] = allSensors[i].gasResistance;
        doc[key_iaq] = allSensors[i].iaq;
    }
    
    char buffer[2048];
    serializeJson(doc, buffer);
    
    if (mqttClient.publish(mqtt_topic, buffer)) {
        Serial.println("Published to ThingsBoard");
    } else {
        Serial.println("Publish failed");
    }
}

// ============================================
// Setup
// ============================================
void setup() {
    Serial.begin(115200);
    delay(1000);

    Serial.println("\n==============================================");
    Serial.println("WINE DETECTOR - THINGSBOARD");
    Serial.println("==============================================");

    Wire.begin(I2C_SDA, I2C_SCL);
    Wire.setClock(100000);
    delay(100);

    // Check multiplexer
    Wire.beginTransmission(MUX_ADDR);
    if (Wire.endTransmission() != 0) {
        Serial.println("ERROR: Multiplexer not found!");
        while (1) delay(1000);
    }
    Serial.println("Multiplexer OK");

    // Connect to WiFi
    WiFi.begin(ssid, password);
    Serial.print("Connecting to WiFi");
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nWiFi connected!");
    Serial.print("IP: "); Serial.println(WiFi.localIP());

    // Configure MQTT (fără TLS pentru thingsboard.cloud)
    mqttClient.setServer(mqtt_broker, mqtt_port);
    mqttClient.setBufferSize(2048);

    Serial.print("Connecting to ThingsBoard...");
    while (!mqttClient.connect(mqtt_client_id, tb_access_token, NULL)) {
        Serial.print(".");
        delay(1000);
    }
    Serial.println(" connected!");

    // Scan sensors
    scanSensors();

    Serial.println("\nSystem ready. Reading all sensors every 3 seconds.\n");
}

// ============================================
// Main loop
// ============================================
void loop() {
    if (!mqttClient.connected()) {
        Serial.print("Reconnecting to ThingsBoard...");
        if (mqttClient.connect(mqtt_client_id, tb_access_token, NULL)) {
            Serial.println(" connected!");
        } else {
            Serial.println(" failed");
        }
    }
    mqttClient.loop();

    readAllSensors();

    unsigned long now = millis();
    if (now - lastPublish >= publishInterval) {
        lastPublish = now;
        publishData();
        Serial.println();
    }

    delay(100);
}