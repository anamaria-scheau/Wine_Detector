"""
Configurație unificată pentru Wine Detector Backend
"""

# ============================================
# PythonAnywhere (pentru deploy și WSGI)
# ============================================
PYANYWHERE_USERNAME = "WineDetector"
PYANYWHERE_DOMAIN = "WineDetector.pythonanywhere.com"
API_TOKEN = "dbae51c141ef4c315a7db915876fb372720e89a0"

# Căi pe server (nu trebuie schimbate)
WEBAPP_PATH = f"/home/WineDetector/mysite"
WSGI_FILE = f"/var/www/WineDetector_pythonanywhere_com_wsgi.py"
VENV_PATH = f"/home/WineDetector/.virtualenvs/my_venv"

# ============================================
# ThingsBoard (pentru subscriber)
# ============================================
THINGSBOARD_HOST = "thingsboard.cloud"
THINGSBOARD_PORT = 1883
THINGSBOARD_ACCESS_TOKEN = "dXF4HlErrhymJFnV6YQf"
THINGSBOARD_MQTT_TOPIC = "v1/devices/me/telemetry"  # Standard, nu schimba!

# ============================================
# Flask API
# ============================================
FLASK_APP = "app.py"
FLASK_VARIABLE = "app"
API_PORT = 5000
API_HOST = "0.0.0.0"

# Modele
MODELS_DIR = "models"
FEATURES = ["humidity", "gas_resistance"]
RED_WINES = ["toro", "garnacha", "monastrel"]
WHITE_WINES = ["macabeo", "chardonnay"]

# Endpoint-uri
PREDICT_ENDPOINT = "/predict_8sensors"