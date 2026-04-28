/**
 * Wine Detector with BME688 - Data Collection & Classification
 * 
 * This firmware supports two modes:
 * 1. Data Collection Mode - Sends labeled data via Serial for training
 * 2. Classification Mode - Sends data to REST API for real-time prediction
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <bsec2.h>

// ============================================
// Configuration
// ============================================

// WiFi Credentials
const char* WIFI_SSID = "en XC";
const char* WIFI_PASSWORD = "necesitamosfinanciacion";

// API Configuration
const char* API_URL = "http://192.168.1.xxx:5000/predict";  // Local or cloud URL

// Sensor Configuration
#define BME68X_I2C_ADDR 0x76
#define SERIAL_BAUD 115200
#define READING_INTERVAL_MS 3000  // 3 seconds

// Operating Mode
#define MODE_COLLECTION 0  // Send data via Serial with labels
#define MODE_CLASSIFICATION 1  // Send to API for prediction
int operatingMode = MODE_CLASSIFICATION;  // Change as needed

// ============================================
// Global Objects
// ============================================

Bsec2 bsec;
unsigned long lastReading = 0;
bool ledState = false;

// Button for labeling during collection mode
const int BUTTON_PIN = 0;  // GPIO0 (boot button on most ESP32)
String currentLabel = "air";  // Default label

// ============================================
// Delay Function for BSEC
// ============================================

void bme68xDelayUs(uint32_t period, void *intfPtr) {
    delayMicroseconds(period);
}

// ============================================
// WiFi Connection
// ============================================

void connectToWiFi() {
    Serial.print("Connecting to WiFi");
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 30) {
        delay(1000);
        Serial.print(".");
        attempts++;
    }
    
    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("\nWiFi connected");
        Serial.print("IP address: ");
        Serial.println(WiFi.localIP());
    } else {
        Serial.println("\nWiFi connection failed");
    }
}

// ============================================
// BME688 Initialization
// ============================================

bool initBME688() {
    Serial.print("Initializing BME688...");
    
    if (!bsec.begin(BME68X_I2C_ADDR, Wire, bme68xDelayUs)) {
        Serial.println(" FAILED");
        printBsecStatus();
        return false;
    }
    
    // Configure virtual sensors
    bsec_virtual_sensor_t sensorList[] = {
        BSEC_OUTPUT_SENSOR_HEAT_COMPENSATED_TEMPERATURE,
        BSEC_OUTPUT_SENSOR_HEAT_COMPENSATED_HUMIDITY,
        BSEC_OUTPUT_RAW_PRESSURE,
        BSEC_OUTPUT_RAW_GAS,
        BSEC_OUTPUT_IAQ
    };
    
    if (!bsec.updateSubscription(sensorList, 5, BSEC_SAMPLE_RATE_LP)) {
        Serial.println(" FAILED");
        printBsecStatus();
        return false;
    }
    
    Serial.println(" OK");
    return true;
}

// ============================================
// BSEC Status Check
// ============================================

void printBsecStatus() {
    if (bsec.status < BSEC_OK) {
        Serial.print("BSEC error: ");
        Serial.println(bsec.status);
    } else if (bsec.status > BSEC_OK) {
        Serial.print("BSEC warning: ");
        Serial.println(bsec.status);
    }
    
    if (bsec.sensor.status < BME68X_OK) {
        Serial.print("BME68X error: ");
        Serial.println(bsec.sensor.status);
    } else if (bsec.sensor.status > BME68X_OK) {
        Serial.print("BME68X warning: ");
        Serial.println(bsec.sensor.status);
    }
}

// ============================================
// Button Handler for Labeling
// ============================================

void handleButton() {
    static unsigned long lastPress = 0;
    unsigned long now = millis();
    
    if (digitalRead(BUTTON_PIN) == LOW && (now - lastPress) > 300) {
        lastPress = now;
        
        // Cycle through labels: air -> red_wine -> white_wine -> air
        if (currentLabel == "air") {
            currentLabel = "red_wine";
            Serial.println("Label changed to: red_wine");
        } else if (currentLabel == "red_wine") {
            currentLabel = "white_wine";
            Serial.println("Label changed to: white_wine");
        } else {
            currentLabel = "air";
            Serial.println("Label changed to: air");
        }
    }
}

// ============================================
// Send Data to API (Classification Mode)
// ============================================

void sendToAPI(float temp, float hum, float press, float gas, float iaq) {
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("WiFi disconnected");
        return;
    }
    
    HTTPClient http;
    http.begin(API_URL);
    http.addHeader("Content-Type", "application/json");
    
    // Create JSON payload
    StaticJsonDocument<256> doc;
    doc["temperature"] = temp;
    doc["humidity"] = hum;
    doc["pressure"] = press;
    doc["gas_resistance"] = gas;
    doc["iaq"] = iaq;
    
    String jsonString;
    serializeJson(doc, jsonString);
    
    Serial.print("Sending to API: ");
    Serial.println(jsonString);
    
    int httpResponseCode = http.POST(jsonString);
    
    if (httpResponseCode > 0) {
        String response = http.getString();
        Serial.print("Response: ");
        Serial.println(response);
    } else {
        Serial.print("Error sending data: ");
        Serial.println(httpResponseCode);
    }
    
    http.end();
}

// ============================================
// Send Data via Serial (Collection Mode)
// ============================================

void sendSerialData(float temp, float hum, float press, float gas, float iaq) {
    // Format: temperature,humidity,pressure,gas_resistance,iaq,label
    Serial.print(temp, 2);
    Serial.print(",");
    Serial.print(hum, 2);
    Serial.print(",");
    Serial.print(press, 2);
    Serial.print(",");
    Serial.print(gas, 0);
    Serial.print(",");
    Serial.print(iaq, 0);
    Serial.print(",");
    Serial.println(currentLabel);
}

// ============================================
// Setup
// ============================================

void setup() {
    Serial.begin(SERIAL_BAUD);
    delay(1000);
    
    Serial.println("\nWine Detector with BME688");
    Serial.println("=========================");
    
    pinMode(BUTTON_PIN, INPUT_PULLUP);
    
    if (!initBME688()) {
        Serial.println("Sensor initialization failed. Halting.");
        while (1) delay(1000);
    }
    
    if (operatingMode == MODE_CLASSIFICATION) {
        connectToWiFi();
        Serial.println("Mode: Classification (API)");
    } else {
        Serial.println("Mode: Data Collection (Serial)");
        Serial.println("Press button to change label");
        Serial.println("Current label: air");
    }
    
    Serial.println("System ready");
}

// ============================================
// Main Loop
// ============================================

void loop() {
    unsigned long now = millis();
    
    if (operatingMode == MODE_COLLECTION) {
        handleButton();
    }
    
    if (bsec.run()) {
        if (now - lastReading >= READING_INTERVAL_MS) {
            lastReading = now;
            
            float temp = bsec.temperature;
            float hum = bsec.humidity;
            float press = bsec.pressure;
            float gas = bsec.gasResistance;
            float iaq = bsec.iaq;
            
            // Print to serial for monitoring
            Serial.printf("T:%.1f H:%.1f G:%.0f IAQ:%.0f\n", 
                         temp, hum, gas, iaq);
            
            if (operatingMode == MODE_CLASSIFICATION) {
                sendToAPI(temp, hum, press, gas, iaq);
            } else {
                sendSerialData(temp, hum, press, gas, iaq);
            }
        }
    } else {
        printBsecStatus();
    }
    
    delay(100);
}