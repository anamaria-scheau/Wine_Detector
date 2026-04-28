"""
Professional Dashboard for Wine Detector - 8 Sensor Version
Hierarchical Display: Wine Type first, then Region
Supports 4-level classification: Presence -> Type -> Red Region -> White Region
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import time
from datetime import datetime

# ============================================
# Page Configuration
# ============================================
st.set_page_config(
    page_title="Wine Detector - BME688",
    layout="wide"
)

# ============================================
# Custom CSS for clean professional look
# ============================================
st.markdown("""
<style>
.main-title {
    font-size: 34px;
    font-weight: 600;
    margin-bottom: 0px;
}
.subtitle {
    font-size: 18px;
    color: gray;
    margin-top: 0px;
}
.section-title {
    font-size: 22px;
    font-weight: 600;
    margin-top: 25px;
}
.sensor-container {
    background-color: transparent;
    border: none;
    border-radius: 0px;
    padding: 10px;
    margin-bottom: 10px;
    text-align: center;
}
.sensor-header {
    font-weight: 600;
    margin-bottom: 5px;
    margin-top: 8px;
    color: #2c3e50;
}
.sensor-specialty {
    font-size: 0.8em;
    color: #6c757d;
    margin-bottom: 10px;
    font-style: italic;
}
.prediction-box {
    background-color: #f8f9fa;
    border-left: 4px solid;
    padding: 8px;
    margin: 8px 0;
    border-radius: 4px;
    text-align: left;
}
.metric-text {
    font-size: 0.9em;
    color: #495057;
}
.sensor-image {
    display: flex;
    justify-content: center;
    margin-bottom: 5px;
}
</style>
""", unsafe_allow_html=True)

# ============================================
# Sensor Specializations
# ============================================
SENSOR_SPECIALIZATIONS = {
    0: "Volatile Organic Compounds (General)",
    1: "Ethanol / Alcohol Compounds",
    2: "Humidity Sensor",
    3: "Temperature Sensor",
    4: "Aromatic Compounds",
    5: "Pressure Sensor",
    6: "Sulfur Compounds",
    7: "Baseline Reference"
}

# ============================================
# Header
# ============================================
col_logo, col_title = st.columns([1,4])

with col_logo:
    st.image("bme688.jpg", width=120)

with col_title:
    st.markdown('<p class="main-title">Wine Classification System</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Real-Time Analysis using 8 BME688 Sensors</p>', unsafe_allow_html=True)

st.markdown("---")

# ============================================
# Sidebar
# ============================================
with st.sidebar:

    st.header("Connection")

    api_url = st.text_input(
        "API URL",
        value="https://WineDetector.pythonanywhere.com"
    )

    # api_url = st.text_input(
    #     "API URL",
    #     value="http://localhost:5000"
    # )
    
    try:
        r = requests.get(f"{api_url}/health", timeout=2)
        api_status = r.status_code == 200
    except:
        api_status = False

    st.write("API:", "Online" if api_status else "Offline")

    if "last_data_time" in st.session_state:
        time_since = (datetime.now() - st.session_state.last_data_time).seconds
    else:
        time_since = 999

    if time_since < 10:
        st.write("Sensors:", "Live")
    else:
        st.write("Sensors:", "Waiting")

    st.markdown("---")

    with st.expander("Settings"):
        confidence_threshold = st.slider(
            "Confidence Threshold",
            0.0, 1.0, 0.0, 0.05
        )
        show_detailed = st.checkbox("Show Detailed Values", True)

# ============================================
# Session State
# ============================================
if "sensor_history" not in st.session_state:
    st.session_state.sensor_history = {
        i: pd.DataFrame(columns=[
            'timestamp','temperature','humidity',
            'gas_resistance','iaq','type_prediction','type_confidence',
            'region_prediction','region_confidence'
        ]) for i in range(8)
    }

if "ensemble_history" not in st.session_state:
    st.session_state.ensemble_history = pd.DataFrame(columns=[
        'timestamp','type_majority','type_confidence','region_majority','region_confidence','agreement'
    ])

if "sample_history" not in st.session_state:
    st.session_state.sample_history = []

if "running" not in st.session_state:
    st.session_state.running = False

if "sample_count" not in st.session_state:
    st.session_state.sample_count = 0

if "last_data_time" not in st.session_state:
    st.session_state.last_data_time = datetime.now()

# ============================================
# Status Bar
# ============================================
col_status1, col_status2, col_status3 = st.columns([2,1,1])

with col_status1:
    if st.session_state.running:
        st.success("● System Running")
    else:
        st.info("○ System Ready")

with col_status2:
    st.caption(f"Samples: {st.session_state.sample_count}")

with col_status3:
    st.caption(f"Last: {st.session_state.last_data_time.strftime('%H:%M:%S')}")

st.markdown("---")

# ============================================
# ============================================
# API Functions (replace old ones)
# ============================================
def fetch_latest_full():
    try:
        response = requests.get(f"{api_url}/latest_full", timeout=2)
        if response.status_code == 200:
            return response.json(), None
        return None, f"HTTP {response.status_code}"
    except Exception as e:
        return None, str(e)

# ============================================
# Hierarchical Classification Processing
# ============================================
def add_to_history(result):
    """
    Process incoming data with hierarchical classification.
    """
    st.session_state.sample_count += 1
    now = datetime.now()
    st.session_state.last_data_time = now

    type_scores = {"air": 0, "red": 0, "white": 0}
    region_scores = {}
    
    sensor_types = []
    sensor_regions = []
    
    for s in result["sensor_results"]:
        if s["success"]:
            prediction = s["prediction"]
            # Use type_confidence (API provides this)
            confidence = s["type_confidence"]
            
            if prediction in ["toro", "garnacha", "monastrel"]:
                type_pred = "red"
            elif prediction == "macabeo":
                type_pred = "white"
            elif prediction in ["air", "red", "white"]:
                type_pred = prediction
            else:
                type_pred = prediction
            
            type_scores[type_pred] += confidence
            sensor_types.append(type_pred)
            
            if type_pred in ["red", "white"] and prediction not in ["red", "white"]:
                region_scores.setdefault(prediction, 0)
                region_scores[prediction] += confidence
                sensor_regions.append(prediction)
    
    type_majority = max(type_scores, key=type_scores.get)
    type_confidence = type_scores[type_majority] / max(sensor_types.count(type_majority), 1)
    
    region_majority = None
    region_confidence = 0
    if type_majority != "air" and region_scores:
        region_majority = max(region_scores, key=region_scores.get)
        region_confidence = region_scores[region_majority] / max(sensor_regions.count(region_majority), 1)
    
    agreement = sensor_types.count(type_majority) / len(sensor_types) if sensor_types else 0
    
    new_row = {
        'timestamp': now,
        'type_majority': type_majority,
        'type_confidence': type_confidence,
        'region_majority': region_majority,
        'region_confidence': region_confidence if region_majority else 0,
        'agreement': agreement
    }
    
    st.session_state.ensemble_history = pd.concat([
        st.session_state.ensemble_history,
        pd.DataFrame([new_row])
    ]).tail(50)
    
    sample_record = {
        "id": st.session_state.sample_count,
        "timestamp": now,
        "type": type_majority,
        "type_conf": type_confidence,
        "region": region_majority,
        "region_conf": region_confidence if region_majority else 0,
        "agreement": agreement
    }
    st.session_state.sample_history.append(sample_record)
    
    for s in result["sensor_results"]:
        if s["success"]:
            sid = s["sensor_id"]
            prediction = s["prediction"]
            confidence = s["type_confidence"]   # use type_confidence
            
            if prediction in ["toro", "garnacha", "monastrel"]:
                sensor_type = "red"
                sensor_region = prediction
            elif prediction == "macabeo":
                sensor_type = "white"
                sensor_region = prediction
            elif prediction in ["air", "red", "white"]:
                sensor_type = prediction
                sensor_region = None
            else:
                sensor_type = prediction
                sensor_region = None
            
            # Get input values safely (no iaq)
            input_data = s.get("input", {})
            df = pd.DataFrame([{
                "timestamp": now,
                "temperature": input_data.get("temperature", 0),
                "humidity": input_data.get("humidity", 0),
                "gas_resistance": input_data.get("gas_resistance", 0),
                "iaq": input_data.get("iaq", 0),   # default to 0 if missing
                "type_prediction": sensor_type,
                "type_confidence": confidence,
                "region_prediction": sensor_region if sensor_region else None,
                "region_confidence": confidence if sensor_region else 0
            }])
            
            st.session_state.sensor_history[sid] = pd.concat([
                st.session_state.sensor_history[sid], df
            ]).tail(50)
# ============================================
# Control Buttons
# ============================================
c1, c2, c3 = st.columns(3)

with c1:
    if st.button("Start", use_container_width=True):
        st.session_state.running = True

with c2:
    if st.button("Stop", use_container_width=True):
        st.session_state.running = False

with c3:
    if st.button("Clear", use_container_width=True):
        st.session_state.sensor_history = {i: pd.DataFrame() for i in range(8)}
        st.session_state.ensemble_history = pd.DataFrame()
        st.session_state.sample_history = []
        st.session_state.sample_count = 0
        st.rerun()

st.markdown("---")

# ============================================
# Current Ensemble Prediction - Hierarchical Display
# ============================================
st.markdown('<p class="section-title">Current Classification</p>', unsafe_allow_html=True)

if not st.session_state.ensemble_history.empty:
    latest = st.session_state.ensemble_history.iloc[-1]
    
    if latest['type_majority'] == "red":
        type_color = "#8B0000"
        type_label = "RED WINE"
    elif latest['type_majority'] == "white":
        type_color = "#F5DEB3"
        type_label = "WHITE WINE"
    else:
        type_color = "#3498db"
        type_label = "AIR"
    
    col_main, col_stats = st.columns([2, 1])
    
    with col_main:
        st.markdown(
            f"<h2 style='color:{type_color}; font-weight:600'>{type_label}</h2>",
            unsafe_allow_html=True
        )
        
        if latest['type_majority'] != "air" and latest['region_majority']:
            region_label = latest['region_majority'].upper()
            st.markdown(
                f"<h3 style='color:#555555;'>{region_label}</h3>",
                unsafe_allow_html=True
            )
    
    with col_stats:
        st.metric("Type Confidence", f"{latest['type_confidence']:.1%}")
        if latest['type_majority'] != "air" and latest['region_majority']:
            st.metric("Region Confidence", f"{latest['region_confidence']:.1%}")
        st.metric("Sensor Agreement", f"{latest['agreement']:.1%}")
    
else:
    st.info("No data available. Start monitoring to see predictions.")

st.markdown("---")

# ============================================
# Individual Sensors - Centered Design with Images
# ============================================
st.markdown('<p class="section-title">Individual Sensors</p>', unsafe_allow_html=True)

with st.expander("View Individual Sensor Readings", expanded=True):
    
    for row in range(2):
        cols = st.columns(4)
        for col in range(4):
            sensor_id = row * 4 + col
            
            with cols[col]:
                st.markdown(f'<div class="sensor-container">', unsafe_allow_html=True)
                
                # Center the image
                st.markdown('<div class="sensor-image">', unsafe_allow_html=True)
                st.image("sensor.JPG", width=60)
                st.markdown('</div>', unsafe_allow_html=True)
                
                st.markdown(f'<div class="sensor-header">Sensor {sensor_id}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="sensor-specialty">{SENSOR_SPECIALIZATIONS[sensor_id]}</div>', unsafe_allow_html=True)
                
                if not st.session_state.sensor_history[sensor_id].empty:
                    last = st.session_state.sensor_history[sensor_id].iloc[-1]
                    
                    if last["type_confidence"] >= confidence_threshold:
                        if last["type_prediction"] == "red":
                            type_color = "#8B0000"
                            type_label = "RED WINE"
                        elif last["type_prediction"] == "white":
                            type_color = "#F5DEB3"
                            type_label = "WHITE WINE"
                        else:
                            type_color = "#3498db"
                            type_label = "AIR"
                        
                        st.markdown(
                            f'<div class="prediction-box" style="border-left-color: {type_color};">'
                            f'<strong>Type:</strong> {type_label}<br>'
                            f'<span class="metric-text">Confidence: {last["type_confidence"]:.1%}</span>'
                            f'</div>',
                            unsafe_allow_html=True
                        )
                        
                        if last["type_prediction"] != "air" and last["region_prediction"]:
                            st.markdown(
                                f'<div class="prediction-box" style="border-left-color: #555555;">'
                                f'<strong>Region:</strong> {last["region_prediction"].upper()}<br>'
                                f'<span class="metric-text">Confidence: {last["region_confidence"]:.1%}</span>'
                                f'</div>',
                                unsafe_allow_html=True
                            )
                        
                        if show_detailed:
                            st.text(f"Temp: {last['temperature']:.1f}°C")
                            st.text(f"Humidity: {last['humidity']:.1f}%")
                            st.text(f"Gas: {last['gas_resistance']:.0f}Ω")
                            st.text(f"IAQ: {last['iaq']:.0f}")
                    else:
                        st.caption("Low confidence reading")
                else:
                    st.caption("No data")
                
                st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# ============================================
# Final Analysis Section
# ============================================
if not st.session_state.running and len(st.session_state.sample_history) > 0:

    with st.expander("Session Analysis", expanded=False):
        
        df = pd.DataFrame(st.session_state.sample_history)
        
        tab1, tab2, tab3 = st.tabs(["Type Distribution", "Region Distribution", "Recent Samples"])
        
        with tab1:
            type_counts = df["type"].value_counts()
            type_labels = {
                "red": "RED WINE",
                "white": "WHITE WINE", 
                "air": "AIR"
            }
            type_display = {type_labels.get(k, k): v for k, v in type_counts.items()}
            type_colors = {
                "RED WINE": "#8B0000",
                "WHITE WINE": "#F5DEB3", 
                "AIR": "#3498db"
            }
            fig_type = px.pie(
                values=list(type_display.values()),
                names=list(type_display.keys()),
                color=list(type_display.keys()),
                color_discrete_map=type_colors,
                title=f"Wine Types ({len(df)} samples)"
            )
            st.plotly_chart(fig_type, use_container_width=True)
        
        with tab2:
            wine_samples = df[df["type"] != "air"]
            if not wine_samples.empty:
                region_counts = wine_samples["region"].value_counts()
                region_display = {r.upper(): c for r, c in region_counts.items()}
                region_colors = {
                    "TORO": "#8B0000",
                    "GARNACHA": "#B22222", 
                    "MONASTREL": "#CD5C5C",
                    "MACABEO": "#F5DEB3"
                }
                fig_region = px.pie(
                    values=list(region_display.values()),
                    names=list(region_display.keys()),
                    color=list(region_display.keys()),
                    color_discrete_map=region_colors,
                    title=f"Regions ({len(wine_samples)} wine samples)"
                )
                st.plotly_chart(fig_region, use_container_width=True)
            else:
                st.info("No wine samples in this session")
        
        with tab3:
            display_df = df[["id", "timestamp", "type", "type_conf", "region", "region_conf", "agreement"]].tail(15)
            display_df["timestamp"] = display_df["timestamp"].dt.strftime("%H:%M:%S")
            display_df["type"] = display_df["type"].apply(lambda x: "RED" if x == "red" else "WHITE" if x == "white" else "AIR")
            display_df["type_conf"] = display_df["type_conf"].apply(lambda x: f"{x:.1%}")
            display_df["region_conf"] = display_df["region_conf"].apply(lambda x: f"{x:.1%}" if x > 0 else "-")
            display_df["agreement"] = display_df["agreement"].apply(lambda x: f"{x:.1%}")
            st.dataframe(display_df, use_container_width=True, hide_index=True)

# ============================================
# Monitoring Loop (replace the existing one)
# ============================================
if st.session_state.running:
    status_placeholder = st.empty()
    status_placeholder.info("Monitoring active – fetching predictions...")

    full_data, error = fetch_latest_full()
    if full_data and full_data.get("sensor_results"):
        add_to_history(full_data)   # your existing add_to_history works
        status_placeholder.success(f"Data received at {datetime.now().strftime('%H:%M:%S')}")
    else:
        if error:
            status_placeholder.error(f"Error: {error}")
        else:
            status_placeholder.warning("No data yet. Waiting for ESP32...")

    time.sleep(3)
    st.rerun()
