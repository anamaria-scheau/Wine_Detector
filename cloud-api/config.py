## Configuration

Create a `config.py` file in the `cloud-api/` directory with the following structure. Replace the placeholder values with your own credentials.

```python
"""
Unified configuration for Wine Detector Backend
"""

# ============================================
# PythonAnywhere (for deployment and WSGI)
# ============================================
PYANYWHERE_USERNAME = "your_username"
PYANYWHERE_DOMAIN = "your_username.pythonanywhere.com"
API_TOKEN = "your_api_token_here"

# Server paths (do not change)
WEBAPP_PATH = f"/home/{PYANYWHERE_USERNAME}/mysite"
WSGI_FILE = f"/var/www/{PYANYWHERE_USERNAME}_pythonanywhere_com_wsgi.py"
VENV_PATH = f"/home/{PYANYWHERE_USERNAME}/.virtualenvs/my_venv"

# ============================================
# ThingsBoard (for MQTT subscriber)
# ============================================
THINGSBOARD_HOST = "thingsboard.cloud"
THINGSBOARD_PORT = 1883
THINGSBOARD_ACCESS_TOKEN = "your_device_access_token"
THINGSBOARD_MQTT_TOPIC = "v1/devices/me/telemetry"   # Standard, do not change

# ============================================
# Flask API
# ============================================
FLASK_APP = "app.py"
FLASK_VARIABLE = "app"
API_PORT = 5000
API_HOST = "0.0.0.0"

# Models
MODELS_DIR = "models"
FEATURES = ["humidity", "gas_resistance"]
RED_WINES = ["toro", "garnacha", "monastrel"]
WHITE_WINES = ["macabeo", "chardonnay"]

# Endpoints
PREDICT_ENDPOINT = "/predict_8sensors"
