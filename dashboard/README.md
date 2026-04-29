# README for `dashboard/` Folder

## Dashboard - Wine Detector Visualization Interface

This folder contains the Streamlit dashboard for real-time visualization of the Wine Detector system. It provides a professional interface to display hierarchical wine classification results from 8 BME688 sensors.

---

## 📁 **Folder Structure**

```
dashboard/
├── dashboard.py                    # Main Streamlit application
├── bme688.jpg                      # Logo image for header
├── sensor.JPG                      # Generic sensor icon for individual sensors
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

---

## 🚀 **Overview**

This dashboard is the **frontend visualization component** of the Wine Detector system. It:

1. **Fetches predictions** from the Flask API (deployed on PythonAnywhere)
2. **Displays hierarchical classification results**:
   - **Level 1 (Presence)**: Air vs Wine
   - **Level 2 (Type)**: Red vs White
   - **Level 3 (Region)**: Specific wine region (Toro, Garnacha, Monastrel, Macabeo,Novell)
3. **Shows individual sensor readings** with their specialized functions
4. **Provides session analysis** with distribution charts and historical data
5. **Updates in real-time** (every 3 seconds)

---

## 🎨 **Dashboard Layout**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Header                                          │
│  [Logo]  Wine Classification System                                         │
│          Real-Time Analysis using 8 BME688 Sensors                          │
├─────────────────────────────────────────────────────────────────────────────┤
│ Sidebar                              │ Main Content                         │
│ ┌─────────────────────┐              │ ┌─────────────────────────────────┐ │
│ │ Connection          │              │ │ Current Classification          │ │
│ │ API URL             │              │ │ ┌─────────┐ ┌─────────────────┐ │ │
│ │ API Status          │              │ │ │ RED WINE│ │ Type Conf: 95%  │ │ │
│ │ Sensors Status      │              │ │ │ TORO    │ │ Region Conf: 92%│ │ │
│ ├─────────────────────┤              │ │ │         │ │ Agreement: 87%  │ │ │
│ │ Settings            │              │ │ └─────────┘ └─────────────────┘ │ │
│ │ Confidence Threshold│              │ └─────────────────────────────────┘ │
│ │ Show Detailed Values│              │                                       │
│ └─────────────────────┘              │ ┌─────────────────────────────────┐ │
│                                      │ │ Individual Sensors              │ │
│                                      │ │ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐│
│                                      │ │ │Sensor0│ │Sensor1│ │Sensor2│ │Sensor3││
│                                      │ │ │ RED  │ │ RED  │ │ RED  │ │ RED  ││
│                                      │ │ │ 95%  │ │ 92%  │ │ 88%  │ │ 91%  ││
│                                      │ │ └──────┘ └──────┘ └──────┘ └──────┘│
│                                      │ └─────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📡 **Data Flow**

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   ESP32     │────▶│ ThingsBoard │────▶│   Flask     │────▶│  Dashboard  │
│  (Sensors)  │ MQTT│   Cloud     │ HTTP│    API      │ HTTP│ (Streamlit) │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                                                                    │
                                                    ┌───────────────┴───────────────┐
                                                    ▼                               ▼
                                            ┌─────────────────┐           ┌─────────────────┐
                                            │  Real-time      │           │  Historical     │
                                            │  Predictions    │           │  Analysis       │
                                            └─────────────────┘           └─────────────────┘
```

---

## 🔧 **Key Components**

### 1. **Sidebar Configuration**

| Element | Purpose |
|---------|---------|
| **API URL** | Endpoint of the Flask API (default: `https://WineDetector.pythonanywhere.com`) |
| **API Status** | Shows if the API is online/offline |
| **Sensors Status** | Indicates if data is being received (Live/Waiting) |
| **Confidence Threshold** | Filters low-confidence predictions |
| **Show Detailed Values** | Toggles display of raw sensor values |

### 2. **Current Classification Section**

Displays the ensemble prediction from all 8 sensors:
- **Wine Type**: AIR, RED WINE, or WHITE WINE (color-coded)
- **Region**: Specific wine region (if applicable)
- **Type Confidence**: Average confidence across sensors for the wine type
- **Region Confidence**: Average confidence for the region prediction
- **Sensor Agreement**: Percentage of sensors agreeing on the prediction

### 3. **Individual Sensors Section**

Each of the 8 sensors is displayed with:
- **Specialization** (e.g., "Volatile Organic Compounds (General)")
- **Prediction**: Type and region (if applicable)
- **Confidence**: Prediction confidence (progress bar)
- **Detailed values**: Temperature, humidity, gas resistance, IAQ (optional)

### 4. **Session Analysis (Expandable)**

Appears when monitoring is stopped:
- **Type Distribution**: Pie chart of wine types detected during the session
- **Region Distribution**: Pie chart of regions detected (wine samples only)
- **Recent Samples**: Table of the last 15 predictions with timestamps

---

## 🏃 **How to Run**

### Prerequisites

```bash
pip install -r requirements.txt
```

**`requirements.txt`:**
```
streamlit>=1.25.0
pandas>=2.0.0
plotly>=5.14.0
requests>=2.31.0
```

### Local Development

```bash
cd dashboard
streamlit run dashboard.py
```

The dashboard will open at `http://localhost:8501`

### Production (PythonAnywhere)

The dashboard is designed to connect to the API deployed on PythonAnywhere. The default API URL is:
```
https://WineDetector.pythonanywhere.com
```

For local testing, you can uncomment the localhost line and comment the production URL:

```python
# api_url = st.text_input(
#     "API URL",
#     value="https://WineDetector.pythonanywhere.com"
# )

api_url = st.text_input(
    "API URL",
    value="http://localhost:5000"
)
```

---

## 🧠 **How the Dashboard Works**

### 1. **Data Fetching**

The dashboard polls the API every 3 seconds using the `/latest_full` endpoint:

```python
def fetch_latest_full():
    response = requests.get(f"{api_url}/latest_full", timeout=2)
    if response.status_code == 200:
        return response.json(), None
    return None, error
```

### 2. **Hierarchical Processing**

The `add_to_history()` function processes the API response:

- **Weighted voting**: Each sensor's prediction contributes to the ensemble decision
- **Type determination**: Aggregates individual sensor predictions to determine majority type
- **Region determination**: For wine samples, determines the majority region
- **Confidence calculation**: Weighted average of confidence scores

### 3. **Real-time Updates**

When "Start" is clicked:
```python
if st.session_state.running:
    full_data, error = fetch_latest_full()
    if full_data:
        add_to_history(full_data)
    time.sleep(3)
    st.rerun()
```

---

## 📊 **Sensor Specializations**

| Sensor | Specialization | Purpose |
|--------|----------------|---------|
| 0 | Volatile Organic Compounds (General) | General VOC detection |
| 1 | Ethanol / Alcohol Compounds | Wine alcohol detection |
| 2 | Humidity Sensor | Humidity measurement |
| 3 | Temperature Sensor | Temperature measurement |
| 4 | Aromatic Compounds | Aromatic VOC detection |
| 5 | Pressure Sensor | Atmospheric pressure |
| 6 | Sulfur Compounds | Sulfur compound detection |
| 7 | Baseline Reference | Reference for calibration |

These specializations are displayed under each sensor card to help understand why different sensors may produce different predictions.

---

## 🎨 **Custom CSS Styling**

The dashboard uses custom CSS for a professional look:

| Class | Purpose |
|-------|---------|
| `.main-title` | Large header title |
| `.subtitle` | Subtitle text |
| `.section-title` | Section headers |
| `.sensor-container` | Container for individual sensors |
| `.sensor-header` | Sensor ID and name |
| `.sensor-specialty` | Sensor specialization text |
| `.prediction-box` | Prediction display with colored left border |
| `.metric-text` | Small metric text |

---

## 📈 **Results Visualization**

### Type Distribution Pie Chart
Shows the proportion of AIR, RED WINE, and WHITE WINE predictions.

### Region Distribution Pie Chart
Shows the proportion of different wine regions (Toro, Garnacha, Monastrel, Macabeo).

### Recent Samples Table
Displays:
- Sample ID
- Timestamp
- Type (AIR/RED/WHITE)
- Type Confidence
- Region (if applicable)
- Region Confidence
- Sensor Agreement

---

## 🔄 **Integration with Backend**

The dashboard expects the Flask API to provide the `/latest_full` endpoint with the following structure:

```json
{
  "sensor_results": [
    {
      "sensor_id": 0,
      "prediction": "toro",
      "type": "red",
      "type_confidence": 0.95,
      "region": "toro",
      "region_confidence": 0.92,
      "success": true,
      "input": {
        "temperature": 23.5,
        "humidity": 65.2,
        "gas_resistance": 82345
      }
    }
  ],
  "ensemble_statistics": {
    "majority_vote": "toro",
    "average_confidence": 0.93
  }
}
```

---

## 🐛 **Troubleshooting**

| Problem | Solution |
|---------|----------|
| **API offline** | Check API URL and ensure `app.py` is running |
| **No data** | Verify ESP32 is publishing to ThingsBoard and subscriber is running |
| **Images not loading** | Ensure `bme688.jpg` and `sensor.JPG` are in the dashboard folder |
| **Slow updates** | Adjust `time.sleep(3)` to a higher value |
| **Memory issues** | Session history is limited to 50 records per sensor |

---

## 📚 **Related Folders**

| Folder | Purpose |
|--------|---------|
| `../cloud-api/` | Flask backend that provides the `/latest_full` endpoint |
| `../firmware/` | ESP32 code that collects sensor data |
| `../training/` | Model training scripts |
| `../iot/` | BSEC2 configuration files (alternative edge AI approach) |

---

## ⚙️ **Configuration Options**

| Setting | Default | Description |
|---------|---------|-------------|
| `api_url` | `https://WineDetector.pythonanywhere.com` | Flask API endpoint |
| `confidence_threshold` | 0.0 | Minimum confidence to display a prediction |
| `show_detailed` | True | Show raw sensor values |
| `publishInterval` | 3 seconds | Data refresh rate |

---

## ✅ **Features Summary**

| Feature | Status |
|---------|--------|
| Real-time predictions | ✅ |
| 8-sensor grid display | ✅ |
| Hierarchical classification | ✅ |
| Weighted voting ensemble | ✅ |
| Session analysis | ✅ |
| Historical data table | ✅ |
| Color-coded results | ✅ |
| Confidence thresholds | ✅ |
| Detailed sensor values | ✅ |
| API connection monitoring | ✅ |

---

**Created for the Wine Detector Project**  
*Last updated: April 2026*
