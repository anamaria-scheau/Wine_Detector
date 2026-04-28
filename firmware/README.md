# README for `firmware/` Folder

## Firmware - ESP32 Wine Detector with ThingsBoard Integration

This folder contains the complete firmware for the ESP32 microcontroller that reads data from 8 BME688 sensors via an I2C multiplexer, processes the data using BSEC2 algorithms, and publishes telemetry to ThingsBoard cloud platform via MQTT.

---

## 📁 **Folder Structure**

```
firmware/
├── include/                    # Header files
│   ├── commMux.h              # Multiplexer control header
│   ├── mqtt_datalogger.h      # MQTT data logger header
│   └── README                 # Documentation for include folder
│
├── lib/                        # External libraries (zipped)
│   ├── Bosch_BME68x_Library.zip
│   ├── Bosch-BSEC2-Library.zip
│   └── README
│
├── src/                        # Source files
│   ├── bsec_config.h          # BSEC2 configuration (binary)
│   ├── CMakeLists.txt         # CMake build configuration
│   ├── commMux.cpp            # Multiplexer implementation
│   ├── main.cpp               # Main firmware entry point
│   └── mqtt_datalogger.cpp    # MQTT data formatting
│
├── test/                       # Unit tests
│   └── README
│
├── tools/                      # Utility scripts
│   ├── convert_config.py      # Configuration converter
│   └── .gitignore
│
├── CMakeLists.txt              # Root CMake configuration
├── compile_commands.json       # Compilation database (for IDE)
├── config.bmeconfig            # BME688 sensor configuration file
├── platformio.ini              # PlatformIO build configuration
└── README.md                   # This file
```

---

## 🚀 **Overview**

This firmware runs on an ESP32 and reads data from 8 BME688 sensors mounted on the Bosch BME688 Evaluation Board. It processes the raw sensor data using BSEC2 algorithms and publishes calibrated telemetry to ThingsBoard cloud platform via MQTT.

**Key Features:**
- Supports all 8 sensors on the BME688 evaluation board via I2C multiplexer
- Uses BSEC2 for calibrated temperature, humidity, pressure, gas resistance, and IAQ
- Publishes data to ThingsBoard cloud (thingsboard.cloud) using MQTT
- Automatic sensor detection and initialization
- Robust error handling and reconnection logic

---

## 🔌 **Hardware Requirements**

### Components
| Component                   | Description                             |
|-----------------------------|-----------------------------------------|
| **ESP32**                   | Dev Module or Adafruit Feather HUZZAH32 |
| **BME688 Evaluation Board** | 8 BME688 sensors on a single board      |
| **USB Cable**               | For power and programming               |

### Connections
The evaluation board connects directly to the ESP32 via pin headers. No external wiring is needed.

### Communication Protocols
| Protocol | Pins                       | Purpose                                                           |
|----------|----------------------------|-------------------------------------------------------------------|
| **I2C**  | GPIO21 (SDA), GPIO22 (SCL) | Controls the multiplexer at address 0x20                          |
| **SPI**  | MOSI, MISO, SCK            | Communicates with the selected sensor after multiplexer switching |

---

## 🧠 **How It Works**

### 1. Multiplexer Control (commMux)

The evaluation board has 8 BME688 sensors sharing the same SPI bus. A hardware multiplexer (PCAL6416A) selects which sensor is active.

```
ESP32 ──I2C──► Multiplexer ──SPI──► Sensor 0 (when channel 0 selected)
                (0x20)       │
                             ├──SPI──► Sensor 1 (when channel 1 selected)
                             └──SPI──► Sensor 7 (when channel 7 selected)
```

The `commMux` library handles:
- Selecting the correct sensor channel via I2C
- Routing SPI commands to the selected sensor
- Returning sensor data

### 2. Sensor Reading Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                      ESP32 Firmware                             │
├─────────────────────────────────────────────────────────────────┤
│  1. commMux selects channel 0                                   │
│  2. BSEC2 reads sensor 0 via SPI                                │
│  3. Data stored in array[0]                                     │
│  4. Repeat for channels 1-7                                     │
│  5. When all 8 sensors read:                                    │
│     - Build JSON with all data                                  │
│     - Publish to ThingsBoard via MQTT                           │
│  6. Wait 3 seconds, repeat                                      │
└─────────────────────────────────────────────────────────────────┘
```

### 3. Data Flow to Cloud

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│    ESP32    │────▶│ ThingsBoard │────▶│  Dashboard │
│   Firmware  │ MQTT│   Cloud     │ HTTP│  (Streamlit)│
└─────────────┘     └─────────────┘     └─────────────┘
```

---

## 📡 **MQTT / ThingsBoard Configuration**

The firmware publishes telemetry to ThingsBoard cloud using the following parameters:

| Parameter        | Value                     |
|----------------  |---------------------------|
| **Broker**       | `thingsboard.cloud`       |
| **Port**         | `1883`                    |
| **Access Token** | `dXF4HlErrhymJFnV6YQf`    |
| **Topic**        | `v1/devices/me/telemetry` |

### Published Data Format

```json
{
  "sensor_0_temp": 23.5,
  "sensor_0_hum": 65.2,
  "sensor_0_gas": 82345,
  "sensor_0_iaq": 115,
  "sensor_1_temp": 23.6,
  "sensor_1_hum": 64.8,
  ...
}
```

---

## 🔧 **Key Files Explained**

### `main.cpp`
The main firmware entry point. It:
- Initializes I2C, WiFi, and MQTT
- Scans and detects all 8 sensors
- Reads each sensor sequentially using BSEC2
- Publishes telemetry to ThingsBoard every 3 seconds

### `commMux.h` / `commMux.cpp`
Handles the I2C multiplexer for selecting individual sensors:
- `commMuxBegin()` - Initializes I2C and SPI
- `commMuxSetConfig()` - Assigns a channel to a sensor
- `commMuxWrite()` / `commMuxRead()` - SPI communication via multiplexer

### `bsec_config.h`
Contains the binary BSEC2 configuration for the BME688 sensors. This configuration is generated by the BME AI-Studio tool and contains the trained model parameters for IAQ calculation and gas selectivity.

### `mqtt_datalogger.h` / `mqtt_datalogger.cpp`
Helper class for formatting MQTT messages. It builds JSON payloads with sensor data and publishes them to the MQTT broker.

### `platformio.ini`
PlatformIO build configuration specifying:
- Target platform (espressif32)
- Board (esp32dev)
- Library dependencies
- Build flags for include paths

---

## 🔧 **PlatformIO Configuration (`platformio.ini`)**

```ini
[env:esp32dev]
platform = espressif32
board = esp32dev
framework = arduino
monitor_speed = 115200
upload_port = COM7
monitor_port = COM7

lib_deps = 
    https://github.com/BoschSensortec/Bosch-BME68x-Library.git
    https://github.com/BoschSensortec/Bosch-BSEC2-Library.git#v1.5.2400
    bblanchon/ArduinoJson @ ^6.21.5
    knolleary/PubSubClient @ ^2.8
    adafruit/Adafruit BME680 Library @ ^2.0.0
    adafruit/Adafruit Unified Sensor @ ^1.1.6

build_flags =
    -DBME68X_USE_SPI 
    -I.pio/libdeps/esp32dev/bsec2/src
    -I.pio/libdeps/esp32dev/bsec2/src/inc
    -I.pio/libdeps/esp32dev/bsec2/src/config
    -I.pio/libdeps/esp32dev/BME68x\ Sensor\ library/src
    -I../iot
    -I../iot/presence_model
    -I../iot/type_model
    -I../iot/red_region_model
    -I../iot/white_region_model
```

---

## 🏃 **How to Build and Upload**

### 1. Install PlatformIO
- Install Visual Studio Code
- Install the PlatformIO extension

### 2. Open Project
```bash
cd firmware
code .
```

### 3. Select COM Port
Edit `platformio.ini` and set:
```ini
upload_port = COMx   # Your COM port number
monitor_port = COMx
```

### 4. Build
```bash
pio run
```

### 5. Upload to ESP32
```bash
pio run --target upload
```

### 6. Monitor Serial Output
```bash
pio device monitor
```

---

## ✅ **Expected Serial Output**

```
==============================================
WINE DETECTOR - THINGSBOARD
==============================================
Multiplexer OK
Connecting to WiFi...
WiFi connected!
IP: 192.168.x.x
Connecting to ThingsBoard... connected!

Scanning sensors...
  Sensor 0: detected
  Sensor 1: detected
  ...
  Sensor 7: detected

Found 8/8 sensors

System ready. Reading all sensors every 3 seconds.

Reading sensor 0... OK (T=22.5, H=45.2, G=123456)
Reading sensor 1... OK (T=22.6, H=44.8, G=123789)
...
Published to ThingsBoard
```

---

## 🐛 **Troubleshooting**

| Problem                       | Solution                                                         |
|------------------------------ |------------------------------------------------------------------|
| **Multiplexer not found**     | Check I2C connections (SDA=GPIO21, SCL=GPIO22)                   |
| **Sensors not detected**      | Ensure board is powered (3.3V) and CSB pin is connected properly |
| **MQTT connection fails**     | Verify ThingsBoard access token and internet connectivity        |
| **BSEC initialization fails** | Ensure `bsec_config.h` contains valid configuration              |
| **Compilation errors**        | Run `pio run --target clean` then rebuild                        |

---

## 📚 **Related Folders**

| Folder | Purpose |
|--------|---------|
| `../cloud-api/` | Flask backend that receives data from ThingsBoard |
| `../dashboard/` | Streamlit dashboard for visualization |
| `../training/` | Model training scripts |

---

## 📝 **Notes**

- The firmware uses **BSEC2 library version 1.5.2400** (specified in `platformio.ini`)
- ThingsBoard access token is hardcoded; change it if you use a different device
- The MQTT topic follows ThingsBoard's standard telemetry format (`v1/devices/me/telemetry`)
- Data is published every 3 seconds; adjust `publishInterval` if needed

---

**Created for the Wine Detector Project**  
*Last updated: April 2026*