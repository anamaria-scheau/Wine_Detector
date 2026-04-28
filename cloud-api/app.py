"""
Wine Detector REST API - Hierarchical Prediction (4 Models)
Loads four separate models:
- Presence Model (air vs wine)
- Type Model (red vs white)
- Red Region Model (toro, garnacha, monastrel)
- White Region Model (macabeo, chardonnay, etc.)
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import numpy as np
import pandas as pd
import os
import logging
from datetime import datetime
from collections import Counter
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# ============================================
# In-memory storage
# ============================================
latest_prediction = {
    "majority_vote": "unknown",
    "avg_confidence": 0.0,
    "timestamp": ""
}
latest_full_results = {
    "sensor_results": [],
    "ensemble_statistics": {},
    "timestamp": ""
}

# ============================================
# Configuration
# ============================================
MODELS_DIR = 'models'
FEATURES = ['humidity', 'gas_resistance']

RED_WINES = ['toro', 'garnacha', 'monastrel']
WHITE_WINES = ['macabeo', 'chardonnay']


class HierarchicalModelManager:
    """
    Manages four hierarchical models:
    - Level 1: Presence (air vs wine)
    - Level 2: Type (red vs white)
    - Level 3a: Red Region (toro, garnacha, monastrel)
    - Level 3b: White Region (macabeo, chardonnay, etc.)
    """
    
    def __init__(self):
        self.model_presence = None
        self.model_type = None
        self.model_red_region = None
        self.model_white_region = None
        
        self.scaler_presence = None
        self.scaler_type = None
        self.scaler_red_region = None
        self.scaler_white_region = None
        
        self.has_red_model = False
        self.has_white_model = False
        self.is_loaded = False
        
    def load_models(self) -> bool:
        """Load all hierarchical models"""
        try:
            # Level 1: Presence (air vs wine)
            with open(os.path.join(MODELS_DIR, 'presence_model.pkl'), 'rb') as f:
                self.model_presence = pickle.load(f)
            with open(os.path.join(MODELS_DIR, 'presence_scaler.pkl'), 'rb') as f:
                self.scaler_presence = pickle.load(f)
            logger.info("Loaded Presence model (air vs wine)")
            
            # Level 2: Type (red vs white)
            with open(os.path.join(MODELS_DIR, 'type_model.pkl'), 'rb') as f:
                self.model_type = pickle.load(f)
            with open(os.path.join(MODELS_DIR, 'type_scaler.pkl'), 'rb') as f:
                self.scaler_type = pickle.load(f)
            logger.info("Loaded Type model (red vs white)")
            
            # Level 3a: Red Region (if exists)
            red_model_path = os.path.join(MODELS_DIR, 'red_region_model.pkl')
            red_scaler_path = os.path.join(MODELS_DIR, 'red_region_scaler.pkl')
            if os.path.exists(red_model_path) and os.path.exists(red_scaler_path):
                with open(red_model_path, 'rb') as f:
                    self.model_red_region = pickle.load(f)
                with open(red_scaler_path, 'rb') as f:
                    self.scaler_red_region = pickle.load(f)
                self.has_red_model = True
                logger.info("Loaded Red Region model")
            else:
                logger.warning("Red Region model not found - will use default")
            
            # Level 3b: White Region (if exists)
            white_model_path = os.path.join(MODELS_DIR, 'white_region_model.pkl')
            white_scaler_path = os.path.join(MODELS_DIR, 'white_region_scaler.pkl')
            if os.path.exists(white_model_path) and os.path.exists(white_scaler_path):
                with open(white_model_path, 'rb') as f:
                    self.model_white_region = pickle.load(f)
                with open(white_scaler_path, 'rb') as f:
                    self.scaler_white_region = pickle.load(f)
                self.has_white_model = True
                logger.info("Loaded White Region model")
            else:
                logger.warning("White Region model not found - will use default (macabeo)")
            
            self.is_loaded = True
            return True
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            return False
    
    def predict_presence(self, features: np.ndarray) -> tuple:
        """Level 1: Predict if it's air or wine"""
        features_scaled = self.scaler_presence.transform(features)
        prediction = self.model_presence.predict(features_scaled)[0]
        probabilities = self.model_presence.predict_proba(features_scaled)[0]
        confidence = float(max(probabilities))
        return prediction, confidence
    
    def predict_type(self, features: np.ndarray) -> tuple:
        """Level 2: Predict if wine is red or white"""
        features_scaled = self.scaler_type.transform(features)
        prediction = self.model_type.predict(features_scaled)[0]
        probabilities = self.model_type.predict_proba(features_scaled)[0]
        confidence = float(max(probabilities))
        return prediction, confidence
    
    def predict_red_region(self, features: np.ndarray) -> tuple:
        """Level 3a: Predict which red wine region"""
        if not self.has_red_model:
            return 'unknown', 0.0
        features_scaled = self.scaler_red_region.transform(features)
        prediction = self.model_red_region.predict(features_scaled)[0]
        probabilities = self.model_red_region.predict_proba(features_scaled)[0]
        confidence = float(max(probabilities))
        return prediction, confidence
    
    def predict_white_region(self, features: np.ndarray) -> tuple:
        """Level 3b: Predict which white wine"""
        if not self.has_white_model:
            # Default: if only one white wine, return it
            if len(WHITE_WINES) == 1:
                return WHITE_WINES[0], 1.0
            return 'unknown', 0.0
        
        features_scaled = self.scaler_white_region.transform(features)
        prediction = self.model_white_region.predict(features_scaled)[0]
        probabilities = self.model_white_region.predict_proba(features_scaled)[0]
        confidence = float(max(probabilities))
        return prediction, confidence
    
    def predict_hierarchical(self, sensor_data: Dict[str, float]) -> Dict[str, Any]:
        """Complete hierarchical prediction for a single sensor"""
        
        # Prepare features
        features = pd.DataFrame([{
            'humidity': sensor_data.get('humidity', 0),
            'gas_resistance': sensor_data.get('gas_resistance', 0)
        }])
        
        # Level 1: Presence
        presence, presence_conf = self.predict_presence(features)
        
        if presence == 'air':
            return {
                'type': 'air',
                'type_confidence': presence_conf,
                'region': None,
                'region_confidence': 0,
                'full_prediction': 'air'
            }
        
        # Level 2: Type (red vs white)
        wine_type, type_conf = self.predict_type(features)
        
        if wine_type == 'red':
            # Level 3a: Red region
            region, region_conf = self.predict_red_region(features)
            return {
                'type': 'red',
                'type_confidence': type_conf,
                'region': region,
                'region_confidence': region_conf,
                'full_prediction': region
            }
        else:  # white
            # Level 3b: White region
            region, region_conf = self.predict_white_region(features)
            return {
                'type': 'white',
                'type_confidence': type_conf,
                'region': region,
                'region_confidence': region_conf,
                'full_prediction': region
            }


# Initialize model manager
model_manager = HierarchicalModelManager()


# ============================================
# API Routes
# ============================================

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'name': 'Wine Detector API - Hierarchical Prediction',
        'version': '4.0.0',
        'status': 'operational',
        'endpoints': {
            '/health': 'GET - Check API health',
            '/info': 'GET - Model information',
            '/predict': 'POST - Single sensor prediction',
            '/predict_8sensors': 'POST - 8-sensor prediction',
            '/latest_full': 'GET - Get latest full results'
        }
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy' if model_manager.is_loaded else 'degraded',
        'model_loaded': model_manager.is_loaded,
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/info', methods=['GET'])
def info():
    if not model_manager.is_loaded:
        return jsonify({'error': 'Models not loaded'}), 503
    return jsonify({
        'presence_classes': list(model_manager.model_presence.classes_),
        'type_classes': list(model_manager.model_type.classes_),
        'red_wines': RED_WINES,
        'white_wines': WHITE_WINES,
        'features': FEATURES
    })

@app.route('/predict', methods=['POST'])
def predict():
    if not model_manager.is_loaded:
        return jsonify({'error': 'Models not loaded'}), 503
        
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        result = model_manager.predict_hierarchical(data)
        
        response = {
            'timestamp': datetime.utcnow().isoformat(),
            'input_data': data,
            'prediction': result['full_prediction'],
            'type': result['type'],
            'type_confidence': result['type_confidence'],
            'region': result['region'],
            'region_confidence': result['region_confidence']
        }
        
        logger.info(f"Prediction: {result['full_prediction']}")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/predict_8sensors', methods=['POST'])
def predict_8sensors():
    global latest_prediction, latest_full_results
    if not model_manager.is_loaded:
        return jsonify({'error': 'Models not loaded'}), 503
        
    try:
        data = request.get_json()
        if not data or 'sensors' not in data:
            return jsonify({'error': 'Invalid format. Expected {"sensors": [...]}'}), 400
            
        sensors = data['sensors']
        timestamp = data.get('timestamp', datetime.utcnow().isoformat())
        
        results = []
        predictions_list = []
        
        for sensor in sensors:
            sensor_id = sensor.get('id', 0)
            sensor_data = {
                'humidity': sensor.get('humidity', 0),
                'gas_resistance': sensor.get('gas_resistance', 0)
            }
            
            try:
                result = model_manager.predict_hierarchical(sensor_data)
                results.append({
                    'sensor_id': sensor_id,
                    'prediction': result['full_prediction'],
                    'type': result['type'],
                    'type_confidence': result['type_confidence'],
                    'region': result['region'],
                    'region_confidence': result['region_confidence'],
                    'success': True,
                    'input': {
                        'temperature': sensor.get('temperature', 0),
                        'humidity': sensor.get('humidity', 0),
                        'gas_resistance': sensor.get('gas_resistance', 0)
                    }
                })
                predictions_list.append(result['full_prediction'])
            except Exception as e:
                results.append({
                    'sensor_id': sensor_id,
                    'error': str(e),
                    'success': False,
                    'input': sensor
                })
        
        successful = [r for r in results if r.get('success', False)]
        
        if successful:
            pred_counts = Counter([r['prediction'] for r in successful])
            majority_vote = pred_counts.most_common(1)[0][0] if pred_counts else "unknown"
            avg_confidence = sum(r['type_confidence'] for r in successful) / len(successful)
            ensemble_stats = {
                'total_sensors': len(sensors),
                'active_sensors': len(successful),
                'majority_vote': majority_vote,
                'average_confidence': avg_confidence,
                'prediction_distribution': dict(pred_counts)
            }
        else:
            ensemble_stats = {
                'total_sensors': len(sensors),
                'active_sensors': 0,
                'majority_vote': 'unknown',
                'average_confidence': 0.0,
                'prediction_distribution': {}
            }
        
        # Store for dashboard
        latest_prediction = {
            "majority_vote": ensemble_stats.get("majority_vote", "unknown"),
            "avg_confidence": ensemble_stats.get("average_confidence", 0.0),
            "timestamp": datetime.utcnow().isoformat()
        }
        latest_full_results = {
            "sensor_results": results,
            "ensemble_statistics": ensemble_stats,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return jsonify({
            'timestamp': timestamp,
            'processed_at': datetime.utcnow().isoformat(),
            'sensor_results': results,
            'ensemble_statistics': ensemble_stats
        })
        
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/latest_full', methods=['GET'])
def latest_full():
    return jsonify(latest_full_results)


if __name__ == '__main__':
    if not model_manager.load_models():
        logger.warning("API starting in degraded mode (models not loaded)")
    app.run(host='0.0.0.0', port=5000, debug=True)