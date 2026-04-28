"""
MQTT Subscriber for Wine Detector - ThingsBoard
Ascultă datele de la ThingsBoard și le trimite la Flask API
"""

import paho.mqtt.client as mqtt
import json
import requests
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================
# Configuration - THINGSBOARD
# ============================================
THINGSBOARD_HOST = "thingsboard.cloud"
THINGSBOARD_PORT = 1883
THINGSBOARD_ACCESS_TOKEN = "dXF4HlErrhymJFnV6YQf"  # Token-ul tău
MQTT_TOPIC = "v1/devices/me/telemetry"

# API URL 
API_URL = "http://WineDetector.pythonanywhere.com/predict_8sensors"
#API_URL = "http://localhost:5000/predict_8sensors"  #  test local

# ============================================
# Callbacks
# ============================================
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info(f"Connected to ThingsBoard at {THINGSBOARD_HOST}")
        client.subscribe(MQTT_TOPIC)
    else:
        logger.error(f"Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        logger.info(f"Received from ThingsBoard: {json.dumps(payload)[:200]}...")
        
        # Trimite la API
        response = requests.post(API_URL, json=payload, timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            ensemble = result.get('ensemble_statistics', {})
            logger.info(f"API response: {ensemble.get('majority_vote', 'N/A')} "
                       f"(conf: {ensemble.get('average_confidence', 0):.2f})")
        else:
            logger.error(f"API error: {response.status_code}")
            
    except Exception as e:
        logger.error(f"Error: {e}")

# ============================================
# Main
# ============================================
def main():
    # ThingsBoard folosește token ca username
    client = mqtt.Client()
    client.username_pw_set(THINGSBOARD_ACCESS_TOKEN)
    
    client.on_connect = on_connect
    client.on_message = on_message
    
    client.connect(THINGSBOARD_HOST, THINGSBOARD_PORT, 60)
    
    logger.info("Starting MQTT subscriber for ThingsBoard...")
    client.loop_forever()

if __name__ == "__main__":
    main()







