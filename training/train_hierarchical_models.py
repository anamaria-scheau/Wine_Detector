
"""
Train hierarchical models for wine detection using ALL 8 sensors.
Handles NaN values by dropping or filling them.
No evaluation output - only training and saving models.
"""

import pandas as pd
import glob
import os
import pickle
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer

# ============================================
# Configuration
# ============================================
DATA_DIR = 'csv_data_all_sensors'
MODEL_DIR = 'models_all_sensors'
TEST_SIZE = 0.2
RANDOM_STATE = 42
K_NEIGHBORS = 17

# ============================================
# Wine class definitions
# ============================================
RED_WINES = ['toro', 'garnacha', 'monastrel']
WHITE_WINES = ['macabeo', 'novell']

# Suppress warnings
import warnings
warnings.filterwarnings('ignore')

def load_all_data(data_dir):
    """Load all CSV files and combine into one dataframe"""
    all_files = glob.glob(os.path.join(data_dir, "*.csv"))
    
    if not all_files:
        print(f"No CSV files found in {data_dir}")
        return None
    
    dfs = []
    for file in all_files:
        df = pd.read_csv(file)
        dfs.append(df)
    
    combined_df = pd.concat(dfs, ignore_index=True)
    
    # Drop rows with NaN values
    before = len(combined_df)
    combined_df = combined_df.dropna()
    
    return combined_df

def pivot_by_sensor(df):
    """
    Pivot the dataframe to have one row per sample (time) with features from all sensors.
    Each sensor contributes temperature, humidity, gas_resistance.
    """
    pivoted_data = []
    
    # Group by time (each complete cycle has all 8 sensors)
    n_sensors = 8
    n_samples = len(df) // n_sensors
    
    for i in range(n_samples):
        start_idx = i * n_sensors
        end_idx = start_idx + n_sensors
        sample_rows = df.iloc[start_idx:end_idx]
        
        # Get label from first row (all rows have same label)
        row_data = {'label': sample_rows['label'].iloc[0]}
        
        for _, row in sample_rows.iterrows():
            sensor_id = int(row['sensor_id'])
            row_data[f'sensor_{sensor_id}_temperature'] = row['temperature']
            row_data[f'sensor_{sensor_id}_humidity'] = row['humidity']
            row_data[f'sensor_{sensor_id}_gas_resistance'] = row['gas_resistance']
        
        pivoted_data.append(row_data)
    
    result_df = pd.DataFrame(pivoted_data)
    return result_df

def prepare_features(df, exclude_label=True):
    """Extract feature columns (all numeric sensor columns)"""
    feature_cols = [col for col in df.columns if col.startswith('sensor_')]
    if exclude_label:
        X = df[feature_cols]
    else:
        X = df
    return X

def prepare_presence_data(df):
    """Level 1: air vs wine"""
    presence_df = df.copy()
    presence_df['presence_label'] = presence_df['label'].apply(
        lambda x: 'air' if x == 'air' else 'wine'
    )
    return presence_df

def prepare_type_data(df):
    """Level 2: red vs white (only wine samples)"""
    wine_df = df[df['label'] != 'air'].copy()
    wine_df['type_label'] = wine_df['label'].apply(
        lambda x: 'red' if x in RED_WINES else 'white'
    )
    return wine_df

def prepare_red_region_data(df):
    """Level 3a: red region classification"""
    red_df = df[df['label'].isin(RED_WINES)].copy()
    return red_df

def prepare_white_region_data(df):
    """Level 3b: white region classification"""
    white_df = df[df['label'].isin(WHITE_WINES)].copy()
    return white_df

def train_and_save_model(X, y, model_name, output_dir):
    """Train KNN model and save to disk - no output"""
    # If only one class, skip training (no model needed)
    if len(y.unique()) <= 1:
        return None, None
    
    # Check for NaN values in features
    if X.isnull().sum().sum() > 0:
        imputer = SimpleImputer(strategy='median')
        X = pd.DataFrame(imputer.fit_transform(X), columns=X.columns)
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    model = KNeighborsClassifier(
        n_neighbors=K_NEIGHBORS,
        weights='uniform',
        metric='euclidean'
    )
    model.fit(X_train_scaled, y_train)
    
    os.makedirs(output_dir, exist_ok=True)
    
    with open(os.path.join(output_dir, f'{model_name}_model.pkl'), 'wb') as f:
        pickle.dump(model, f)
    
    with open(os.path.join(output_dir, f'{model_name}_scaler.pkl'), 'wb') as f:
        pickle.dump(scaler, f)
    
    return model, scaler

def main():
    print("="*70)
    print("HIERARCHICAL MODEL TRAINING FOR WINE DETECTION")
    print(f"Using ALL 8 sensors")
    print("="*70)
    
    # Load and pivot data
    df_raw = load_all_data(DATA_DIR)
    if df_raw is None:
        return
    
    # Pivot to have one row per sample with all sensors
    df = pivot_by_sensor(df_raw)
    
    # Prepare data for each level
    presence_df = prepare_presence_data(df)
    type_df = prepare_type_data(df)
    red_df = prepare_red_region_data(df)
    white_df = prepare_white_region_data(df)
    
    # Train models
    print("\nTraining Level 1: Presence Model (air vs wine)...")
    X_presence = prepare_features(presence_df)
    y_presence = presence_df['presence_label']
    train_and_save_model(X_presence, y_presence, 'presence', MODEL_DIR)
    print("  ✓ Presence model saved")
    
    print("\nTraining Level 2: Type Model (red vs white)...")
    if not type_df.empty:
        X_type = prepare_features(type_df)
        y_type = type_df['type_label']
        train_and_save_model(X_type, y_type, 'type', MODEL_DIR)
        print("  ✓ Type model saved")
    else:
        print("  ✗ No wine data found")
    
    print("\nTraining Level 3a: Red Region Model...")
    if not red_df.empty:
        X_red = prepare_features(red_df)
        y_red = red_df['label']
        train_and_save_model(X_red, y_red, 'red_region', MODEL_DIR)
        print("  ✓ Red region model saved")
    else:
        print("  ✗ No red wine data found")
    
    print("\nTraining Level 3b: White Region Model...")
    if not white_df.empty and len(white_df['label'].unique()) > 1:
        X_white = prepare_features(white_df)
        y_white = white_df['label']
        train_and_save_model(X_white, y_white, 'white_region', MODEL_DIR)
        print("  ✓ White region model saved")
    else:
        if not white_df.empty:
            print(f"  ✗ Only one white wine class ({white_df['label'].unique()[0]}), no model needed")
        else:
            print("  ✗ No white wine data found")
    
    print("\n" + "="*70)
    print("TRAINING COMPLETE!")
    print(f"Models saved to {MODEL_DIR}/")
    print("\nFiles to copy to cloud-api/models/:")
    print("  - presence_model.pkl")
    print("  - presence_scaler.pkl")
    print("  - type_model.pkl")
    print("  - type_scaler.pkl")
    
    if not red_df.empty:
        print("  - red_region_model.pkl")
        print("  - red_region_scaler.pkl")
    
    if not white_df.empty and len(white_df['label'].unique()) > 1:
        print("  - white_region_model.pkl")
        print("  - white_region_scaler.pkl")
    print("="*70)

if __name__ == "__main__":
    main()



