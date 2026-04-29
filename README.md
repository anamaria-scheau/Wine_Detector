# Wine Detector - Complete Project Documentation

## An IoT-Based Electronic Nose for Wine Classification Using BME688 Sensor Array and Hierarchical Machine Learning

---

## 📋 **Project Overview**

The Wine Detector is a complete IoT system that "smells" wine and classifies it by type (red/white) and region (Toro, Garnacha, Monastrel, Macabeo, Novell) using an array of 8 BME688 gas sensors. The system reads raw sensor data, processes it through hierarchical KNN machine learning models, and displays real-time predictions on a professional dashboard.

### System Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   ESP32     │────▶│ ThingsBoard │────▶│   Flask     │────▶│  Dashboard  │
│  (Sensors)  │ MQTT│   Cloud     │ HTTP│    API      │ HTTP│ (Streamlit) │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
      │                    │                    │                    │
      │              Publishes          Loads models        Displays
   Reads 8            telemetry          and predicts        results
   sensors
```

### What It Does

| Capability | Description |
|------------|-------------|
| **Wine Detection** | Identifies whether a sample is air or wine |
| **Wine Type** | Distinguishes between red and white wine |
| **Region Classification** | Identifies specific wine regions (Toro, Garnacha, Monastrel, Macabeo, Novell) |
| **Real-time Monitoring** | Displays predictions every 3 seconds on a live dashboard |
| **Multi-sensor Fusion** | Uses all 8 sensors with weighted voting for ensemble decisions |

---

## 📁 **Project Structure**

```
wine-detector/
│
├── firmware/                      # ESP32 firmware
│   ├── include/                   # Header files
│   │   ├── commMux.h             # Multiplexer control
│   │   └── mqtt_datalogger.h     # MQTT logging
│   ├── src/                       # Source files
│   │   ├── main.cpp              # Main firmware
│   │   ├── commMux.cpp           # Multiplexer implementation
│   │   ├── mqtt_datalogger.cpp   # MQTT data formatting
│   │   └── bsec_config.h         # BSEC2 configuration
│   ├── platformio.ini            # PlatformIO build config
│   └── README.md                 # Firmware documentation
│
├── cloud-api/                     # Flask backend
│   ├── models/                   # Trained ML models
│   │   ├── presence_model.pkl    # Level 1: air vs wine
│   │   ├── type_model.pkl        # Level 2: red vs white
│   │   ├── red_region_model.pkl  # Level 3a: red region (toro/garnacha/monastrel)
│   │   └── white_region_model.pkl# Level 3b: white region (macabeo/novell)
│   ├── app.py                    # Flask application
│   ├── mqtt_subscriber.py        # MQTT client for ThingsBoard
│   ├── wine_detector_wsgi.py     # WSGI for PythonAnywhere
│   ├── config.py                 # Centralized configuration
│   ├── api_requirements.txt      # Python dependencies
│   └── README.md                 # API documentation
│
├── dashboard/                     # Streamlit frontend
│   ├── dashboard.py              # Main dashboard application
│   ├── bme688.jpg                # Logo image
│   ├── sensor.JPG                # Sensor icon
│   ├── requirements.txt          # Dashboard dependencies
│   └── README.md                 # Dashboard documentation
│
├── training/                      # Model training pipeline
│   ├── raw_data/                 # Input: .bmerawdata files from SD card
│   ├── csv_data/                 # Output: Converted CSV files
│   ├── models/                   # Output: Trained models (.pkl)
│   │   ├── presence_model.pkl
│   │   ├── type_model.pkl
│   │   ├── red_region_model.pkl
│   │   └── white_region_model.pkl
│   ├── evaluation/               # Model evaluation outputs
│   ├── convert_bmerawdata_to_csv.py
│   ├── train_hierarchical_models.py
│   ├── requirements.txt
│   └── README.md                 # Training documentation
│
├── iot/                          # BSEC2 configuration (edge AI)
│   ├── presence_model/           # Level 1 model files
│   ├── type_model/               # Level 2 model files
│   ├── red_region_model/         # Level 3a model files
│   ├── white_region_model/       # Level 3b model files
│   ├── bsec_config.h             # Main BSEC configuration
│   └── README.md                 # IoT documentation
│
└── README.md                     # This file
```

---

## 🔧 **Hardware Requirements**

| Component | Description |
|-----------|-------------|
| **ESP32** | Dev Module or Adafruit Feather HUZZAH32 |
| **BME688 Evaluation Board** | 8 BME688 sensors with I2C multiplexer |
| **USB Cable** | For power and programming |
| **Power Supply** | 3.3V or USB power (200-300mA) |

### Pin Connections

| BME688 Board | ESP32 Pin | Function |
|--------------|-----------|----------|
| SDA | GPIO21 | I2C Data |
| SCL | GPIO22 | I2C Clock |
| VCC | 3.3V | Power |
| GND | GND | Ground |

---

## 📊 **Model Performance Results**

### Overall Accuracy: **84.95%**

### Per-Class Performance

| Class | Precision | Recall | F1-Score | Support |
|-------|-----------|--------|----------|---------|
| **Air** | 0.87 | 0.95 | 0.90 | 300 |
| **Garnacha** | 0.72 | 0.63 | 0.67 | 240 |
| **Macabeo** | 0.83 | 0.83 | 0.83 | 329 |
| **Monastrel** | 0.74 | 0.73 | 0.74 | 325 |
| **Novell** | 0.86 | 0.94 | 0.90 | 250 |
| **Toro** | 0.98 | 0.95 | 0.96 | 490 |

### Hierarchical Model Breakdown

| Level | Model | Accuracy | Classes |
|-------|-------|----------|---------|
| 1 | Presence (air vs wine) | 96.5% | air, wine |
| 2 | Type (red vs white) | 91.3% | red, white |
| 3a | Red Region | 89.5% | toro, garnacha, monastrel |
| 3b | White Region | 100.0% | macabeo, novell |

### Key Observations

- **Toro** is the most accurately classified wine (98% precision, 95% recall)
- **Garnacha** and **Monastrel** are the most challenging to distinguish (F1-scores of 0.67 and 0.74)
- **Air** detection is excellent (95% recall, 90% F1-score)
- **Novell** (white wine) performs well (86% precision, 94% recall)
- The white‑region model achieves perfect separation between Macabeo and Novell.

---

## 🚀 **Quick Start Guide**

### Prerequisites

- Python 3.9+
- PlatformIO (for firmware compilation)
- Git

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/wine-detector.git
cd wine-detector
```

### Step 2: Set Up Python Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
# API dependencies
pip install -r cloud-api/api_requirements.txt

# Dashboard dependencies
pip install -r dashboard/requirements.txt

# Training dependencies
pip install -r training/requirements.txt
```

### Step 4: Train Models (if you have data)

```bash
cd training
python convert_bmerawdata_to_csv.py --input_dir raw_data --output_dir csv_data
python train_hierarchical_models.py
cp models/*.pkl ../cloud-api/models/
```

### Step 5: Run the System

```bash
# Terminal 1: Start the API
cd cloud-api
python app.py

# Terminal 2: Start the MQTT subscriber
python mqtt_subscriber.py

# Terminal 3: Start the dashboard
cd dashboard
streamlit run dashboard.py
```

### Step 6: Upload Firmware to ESP32

```bash
cd firmware
pio run --target upload
pio device monitor
```

---

## 📂 **Folder Descriptions**

| Folder | Purpose | Key Files |
|--------|---------|-----------|
| **firmware/** | ESP32 code for reading 8 sensors and publishing to ThingsBoard | `main.cpp`, `platformio.ini`, `commMux.cpp` |
| **cloud-api/** | Flask backend with hierarchical ML models (including white region) | `app.py`, `mqtt_subscriber.py`, `models/*.pkl` |
| **dashboard/** | Streamlit visualization interface | `dashboard.py`, `bme688.jpg` |
| **training/** | Data conversion and model training pipeline (generates all four models) | `convert_bmerawdata_to_csv.py`, `train_hierarchical_models.py` |
| **iot/** | BSEC2 configuration for edge AI (alternative approach) | `bsec_config.h`, model subfolders |

---

## 🔄 **Data Flow (End-to-End)**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              1. Data Collection                             │
│                         BME688 Development Kit + SD card                    │
│                                    │                                        │
│                                    ▼                                        │
│                         training/raw_data/*.bmerawdata                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              2. Model Training                              │
│                    training/train_hierarchical_models.py                    │
│                                    │                                        │
│                                    ▼                                        │
│                         cloud-api/models/*.pkl                              │
│   (presence, type, red_region, white_region)                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              3. Real-Time Inference                         │
│                                                                             │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐│
│  │   ESP32     │────▶│ ThingsBoard │────▶│   Flask     │────▶│  Dashboard  ││
│  │  (sensors)  │ MQTT│   Cloud     │ HTTP│    API      │ HTTP│ (Streamlit) ││
│  └─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘│
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 **Results Summary**

### Quantitative Results

| Metric | Value |
|--------|-------|
| **Overall Accuracy (flat 6 classes)** | 84.95% |
| **Overall Cascade Accuracy** | 88.04% |
| **Number of Classes** | 6 (air + 5 wines) |
| **Number of Sensors** | 8 |
| **Total Training Samples** | 9,668 (after pivoting) |
| **Features Used** | humidity, gas_resistance (from all 8 sensors) |
| **Model Type** | KNN (K=17), hierarchical (4 models) |

### Qualitative Observations

- **Toro** is the most distinct wine (easily separable from others)
- **Garnacha** and **Monastrel** have similar gas profiles (difficult to distinguish)
- **White wines** (Macabeo, Novell) are perfectly separable in the binary white‑region model
- **Air detection** is highly reliable (95% recall)

---

## 🐛 **Troubleshooting**

| Problem | Solution |
|---------|----------|
| **ESP32 not connecting to WiFi** | Check SSID/password in `main.cpp` |
| **MQTT connection fails** | Verify ThingsBoard access token |
| **API returns 503** | Ensure all four model `.pkl` files are present in `cloud-api/models/` |
| **Dashboard shows no data** | Check API URL and ensure `app.py` is running |
| **White wines not distinguished** | Verify `white_region_model.pkl` exists and was trained with both classes |
| **Compilation errors in firmware** | Run `pio run --target clean` then rebuild |

---

## 📚 **Technologies Used**

| Component | Technology | Version |
|-----------|------------|---------|
| **Firmware** | Arduino (C++) | ESP32 core 3.0.0+ |
| **Backend** | Flask | 2.3.3 |
| **Frontend** | Streamlit | 1.25.0+ |
| **ML Library** | scikit-learn | 1.3.0+ |
| **MQTT** | paho-mqtt | 1.6.1+ |
| **Build System** | PlatformIO | latest |
| **Cloud Platform** | PythonAnywhere | N/A |

---

## 👥 **Contributing**

This project was developed as part of the HEAT project (Hybrid Extended reAliTy), funded by Horizon Europe (Grant Agreement ID: 101135637).

---

## 📄 **License**

This project is for academic/research purposes.

---

## 📧 **Contact**

For questions or support, please contact the project maintainers.

---

**Created for the Wine Detector Project**  
*Last updated: April 2026*
