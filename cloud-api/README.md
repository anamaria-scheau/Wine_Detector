# README for `cloud-api/` Folder

## Cloud-API - Wine Detector Backend

This folder contains the complete cloud backend for the Wine Detector system. It provides a REST API for hierarchical wine classification, MQTT integration for receiving sensor data, and WSGI configuration for deployment on PythonAnywhere.

---

## 📁 Folder Structure

```
cloud-api/
├── models/                     # Trained machine learning models (.pkl files)
│   ├── presence_model.pkl      # Level 1: Air vs Wine
│   ├── presence_scaler.pkl     # StandardScaler for level 1
│   ├── type_model.pkl           # Level 2: Red vs White
│   ├── type_scaler.pkl          # StandardScaler for level 2
│   ├── red_region_model.pkl     # Level 3a: Red Region (toro/garnacha/monastrel)
│   ├── red_region_scaler.pkl    # StandardScaler for level 3a
│   ├── white_region_model.pkl   # Level 3b: White Region (macabeo/novell)
│   └── white_region_scaler.pkl  # StandardScaler for level 3b
│
├── app.py                       # Main Flask application
├── mqtt_subscriber.py           # MQTT client for ThingsBoard
├── wine_detector_wsgi.py        # WSGI entry point for PythonAnywhere
├── config.py                    # Centralized configuration
├── api_requirements.txt         # Python dependencies
└── README.md                    # This file
```

---

## 🚀 What This Backend Does

The backend is the **intelligent core** of the Wine Detector system. It:

1. **Receives raw sensor data** via HTTP POST from an MQTT subscriber (or directly)
2. **Loads four hierarchical machine learning models** (KNN classifiers)
3. **Performs hierarchical classification**:
   - **Level 1**: Determines if the sample is AIR or WINE
   - **Level 2**: If wine, determines if RED or WHITE
   - **Level 3a**: If red, identifies the region (Toro, Garnacha, Monastrel) – 3 classes
   - **Level 3b**: If white, identifies the variety (Macabeo, Novell) – 2 classes
4. **Returns predictions** for individual sensors and ensemble statistics
5. **Stores the latest results** in memory for the dashboard to fetch
6. **Can be deployed** locally or on PythonAnywhere cloud

---

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information and available endpoints |
| `/health` | GET | Health check and model loading status |
| `/info` | GET | Model metadata (classes, features, etc.) |
| `/predict` | POST | Single sensor prediction |
| `/predict_8sensors` | POST | Predictions for all 8 sensors with ensemble statistics |
| `/latest_full` | GET | Most recent full prediction results (for dashboard) |

---

## 📤 API Request/Response Examples

### POST `/predict_8sensors`

**Request:**
```json
{
  "timestamp": 12345678,
  "sensors": [
    {
      "id": 0,
      "temperature": 23.5,
      "humidity": 65.2,
      "gas_resistance": 82345
    },
    {
      "id": 1,
      "temperature": 23.6,
      "humidity": 64.8,
      "gas_resistance": 84567
    }
  ]
}
```

**Response:**
```json
{
  "sensor_results": [
    {
      "sensor_id": 0,
      "prediction": "toro",
      "type": "red",
      "type_confidence": 0.95,
      "region": "toro",
      "region_confidence": 0.92
    }
  ],
  "ensemble_statistics": {
    "total_sensors": 2,
    "active_sensors": 2,
    "majority_vote": "toro",
    "average_confidence": 0.93
  }
}
```

---

## 🧠 How the Hierarchical Models Work

```
                    ┌─────────────────────────────────────────┐
                    │         Level 1: Presence              │
                    │      Model: air vs wine                │
                    └─────────────────────────────────────────┘
                                       │
                    ┌──────────────────┴──────────────────┐
                    ▼                                      ▼
              Sample = AIR                           Sample = WINE
                    │                                      │
                    ▼                                      ▼
           Publish "air"                          Level 2: Type
                                                  Model: red vs white
                                                       │
                                    ┌──────────────────┴──────────────────┐
                                    ▼                                      ▼
                              Sample = RED                           Sample = WHITE
                                    │                                      │
                                    ▼                                      ▼
                         Level 3: Red Region                    Level 3: White Region
                         Model: toro, garnacha,                  Model: macabeo, novell
                         monastrel (3 classes)                            (2 classes)
```

### Why hierarchical?

- **Simpler models** (2–3 classes each) → higher accuracy
- **Easier to diagnose errors** (you know exactly which level failed)
- **Easier to extend** (add new wines without retraining everything)

---

## 🔧 Dependencies

Install with:

```bash
pip install -r api_requirements.txt
```

**`api_requirements.txt`:**
```
Flask==2.3.3
flask-cors==4.0.0
numpy==1.24.3
pandas==2.0.3
scikit-learn==1.3.0
joblib==1.3.2
paho-mqtt==1.6.1
requests==2.31.0
```

---

## 🏃 How to Run Locally

### 1. Start the Flask API
```bash
cd cloud-api
python app.py
```
API runs on `http://localhost:5000`

### 2. Start the MQTT Subscriber (in another terminal)
```bash
cd cloud-api
python mqtt_subscriber.py
```

### 3. Test the API
```bash
curl http://localhost:5000/health
curl http://localhost:5000/info
```

---

## ☁️ Deploy to PythonAnywhere

1. **Upload files** to `/home/yourusername/mysite/`
2. **Configure WSGI** (`wine_detector_wsgi.py`):
   ```python
   PROJECT_PATH = '/home/yourusername/mysite'
   ```
3. **Install dependencies** in PythonAnywhere console:
   ```bash
   pip install --user -r api_requirements.txt
   ```
4. **Reload the web app** from the PythonAnywhere dashboard

Your API will be available at:
```
https://yourusername.pythonanywhere.com
```

---

## 🧪 Testing

### Health Check
```bash
curl https://yourusername.pythonanywhere.com/health
```

### Test Prediction
```bash
curl -X POST https://yourusername.pythonanywhere.com/predict_8sensors \
  -H "Content-Type: application/json" \
  -d '{"sensors":[{"id":0,"humidity":65.2,"gas_resistance":82345}]}'
```

---

## 🔐 Features

| Feature | Description |
|---------|-------------|
| **Hierarchical classification** | 4-level decision tree for wine identification |
| **Multi-sensor support** | Processes up to 8 sensors simultaneously |
| **Ensemble voting** | Combines predictions from all sensors |
| **In-memory storage** | Caches latest results for dashboard polling |
| **CORS enabled** | Allows dashboard (different port) to communicate |
| **Production ready** | WSGI configuration for PythonAnywhere |
| **Extensible** | Easy to add new wine varieties |

---

## 📊 Model Information

The backend loads the following models (must be present in `models/` folder):

| File | Purpose | Classes |
|------|---------|---------|
| `presence_model.pkl` | Air vs Wine | air, wine |
| `type_model.pkl` | Red vs White | red, white |
| `red_region_model.pkl` | Red Wine Region | toro, garnacha, monastrel |
| `white_region_model.pkl` | White Wine Region | macabeo, novell |

All models are KNN classifiers (K=17) trained on `humidity` and `gas_resistance` features using a standard scaler.

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| **Models not loading** | Ensure `.pkl` files exist in `models/` folder |
| **CORS errors** | `CORS(app)` is already enabled |
| **MQTT connection fails** | Check ThingsBoard token and host |
| **API returns 503** | Models not loaded; check logs |
| **White wines not distinguished** | Verify `white_region_model.pkl` exists and was trained with both classes |

---

## 📚 Related Folders

| Folder | Purpose |
|--------|---------|
| `../dashboard/` | Streamlit dashboard that consumes this API |
| `../firmware/` | ESP32 code that sends raw sensor data via MQTT |
| `../training/` | Scripts for training the KNN models (including white region) |

---

## 👥 Contributing

To add a new wine variety:

1. For a **new red wine**: add to `RED_WINES` list, collect data, retrain `red_region_model`
2. For a **new white wine**: add to `WHITE_WINES` list, collect data, retrain `white_region_model`
3. Update the API (no code changes needed for the hierarchical logic)

---

**Created for the Wine Detector Project**  
*Last updated: April 2026*
