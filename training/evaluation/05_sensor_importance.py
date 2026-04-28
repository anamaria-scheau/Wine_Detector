"""
Sensor Importance Analysis
Determines which sensors contribute most to classification
Classes: air, toro, garnacha, monastrel, macabeo, novell
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score
import glob
import os
import warnings
warnings.filterwarnings('ignore')

# ============================================
# Configuration
# ============================================
DATA_DIR = '../csv_data_all_sensors'
OUTPUT_DIR = 'results/sensor_importance'
TEST_SIZE = 0.2
RANDOM_STATE = 42
K_NEIGHBORS = 17

# ALL 6 CLASSES
ALL_CLASSES = ['air', 'toro', 'garnacha', 'monastrel', 'macabeo', 'novell']

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================
# Load and pivot data
# ============================================
def load_and_pivot_data(data_dir):
    all_files = glob.glob(os.path.join(data_dir, "*.csv"))
    if not all_files:
        print(f"No CSV files found in {data_dir}")
        return None
    
    dfs = []
    for file in all_files:
        df = pd.read_csv(file)
        dfs.append(df)
    
    combined_df = pd.concat(dfs, ignore_index=True)
    print(f"Loaded {len(combined_df)} total raw samples")
    print(f"Unique labels: {combined_df['label'].unique()}")
    
    n_sensors = 8
    n_samples = len(combined_df) // n_sensors
    
    pivoted_data = []
    for i in range(n_samples):
        start_idx = i * n_sensors
        end_idx = start_idx + n_sensors
        sample_rows = combined_df.iloc[start_idx:end_idx]
        
        row_data = {'label': sample_rows['label'].iloc[0]}
        
        for _, row in sample_rows.iterrows():
            sensor_id = int(row['sensor_id'])
            row_data[f'sensor_{sensor_id}_temperature'] = row['temperature']
            row_data[f'sensor_{sensor_id}_humidity'] = row['humidity']
            row_data[f'sensor_{sensor_id}_gas_resistance'] = row['gas_resistance']
        
        pivoted_data.append(row_data)
    
    result_df = pd.DataFrame(pivoted_data)
    print(f"Pivoted to {len(result_df)} samples")
    print(f"Class distribution:\n{result_df['label'].value_counts()}")
    
    return result_df

def get_features(df):
    return [col for col in df.columns if col.startswith('sensor_')]

def evaluate_features(df, feature_cols, verbose=False):
    """Evaluate model accuracy with given features"""
    X = df[feature_cols]
    y = df['label']
    
    if X.isnull().sum().sum() > 0:
        imputer = SimpleImputer(strategy='median')
        X = pd.DataFrame(imputer.fit_transform(X), columns=feature_cols)
    
    # Use stratified split
    try:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
        )
    except ValueError:
        # If stratification fails (too few samples), use simple split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE
        )
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    n_neighbors = min(K_NEIGHBORS, len(X_train))
    model = KNeighborsClassifier(n_neighbors=n_neighbors)
    model.fit(X_train_scaled, y_train)
    
    y_pred = model.predict(X_test_scaled)
    acc = accuracy_score(y_test, y_pred)
    
    if verbose:
        print(f"  Features: {len(feature_cols)}")
        print(f"  Accuracy: {acc:.4f}")
    
    return acc

def plot_individual_performance(sensor_accuracies, baseline_acc):
    """Plot individual sensor performance"""
    sensors = list(sensor_accuracies.keys())
    accs = list(sensor_accuracies.values())
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    colors = ['green' if acc >= baseline_acc else 'steelblue' for acc in accs]
    bars = ax.bar(sensors, accs, color=colors)
    ax.axhline(y=baseline_acc, color='red', linestyle='--', 
               label=f'All 8 sensors ({baseline_acc:.2%})', linewidth=2)
    ax.set_xlabel('Sensor ID', fontsize=12)
    ax.set_ylabel('Accuracy', fontsize=12)
    ax.set_title('Individual Sensor Performance (6-class classification)\nAir + 5 wines', 
                 fontsize=14, fontweight='bold')
    ax.set_ylim(0, 1)
    ax.set_xticks(sensors)
    ax.legend()
    
    # Add value labels on bars
    for bar, acc in zip(bars, accs):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f'{acc:.1%}', ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/sensor_individual_performance.png', dpi=150)
    plt.show()

def plot_leave_one_out(loo_accuracies, baseline_acc):
    """Plot leave-one-sensor-out impact"""
    sensors = list(loo_accuracies.keys())
    impacts = [baseline_acc - loo_accuracies[s] for s in sensors]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    colors = ['red' if impact > 0 else 'green' for impact in impacts]
    bars = ax.bar(sensors, impacts, color=colors)
    ax.axhline(y=0, color='black', linestyle='-', linewidth=1)
    ax.set_xlabel('Sensor Removed', fontsize=12)
    ax.set_ylabel('Accuracy Drop (percentage points)', fontsize=12)
    ax.set_title('Impact of Removing Each Sensor (6-class classification)\nPositive = sensor is useful', 
                 fontsize=14, fontweight='bold')
    ax.set_xticks(sensors)
    
    # Add value labels
    for bar, impact in zip(bars, impacts):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + (0.01 if impact >= 0 else -0.03),
                f'{impact:.1%}', ha='center', va='bottom' if impact >= 0 else 'top', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/sensor_leave_one_out.png', dpi=150)
    plt.show()

def plot_sensor_type_breakdown(df, baseline_acc):
    """Analyze which sensor types (temp, humidity, gas) are most important"""
    features = get_features(df)
    
    # Separate by measurement type
    temp_features = [f for f in features if 'temperature' in f]
    hum_features = [f for f in features if 'humidity' in f]
    gas_features = [f for f in features if 'gas_resistance' in f]
    
    print("\n--- Sensor Type Breakdown ---")
    print(f"Temperature features: {len(temp_features)}")
    print(f"Humidity features: {len(hum_features)}")
    print(f"Gas features: {len(gas_features)}")
    
    temp_acc = evaluate_features(df, temp_features)
    hum_acc = evaluate_features(df, hum_features)
    gas_acc = evaluate_features(df, gas_features)
    
    print(f"\nTemperature only: {temp_acc:.2%}")
    print(f"Humidity only: {hum_acc:.2%}")
    print(f"Gas only: {gas_acc:.2%}")
    print(f"All sensors: {baseline_acc:.2%}")
    
    # Plot
    fig, ax = plt.subplots(figsize=(8, 5))
    
    types = ['Temperature', 'Humidity', 'Gas', 'All 8 Sensors']
    accs = [temp_acc, hum_acc, gas_acc, baseline_acc]
    colors = ['orange', 'skyblue', 'lightgreen', 'darkblue']
    
    bars = ax.bar(types, accs, color=colors)
    ax.set_ylim(0, 1)
    ax.set_ylabel('Accuracy', fontsize=12)
    ax.set_title('Performance by Sensor Type (6-class classification)', 
                 fontsize=14, fontweight='bold')
    
    for bar, acc in zip(bars, accs):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f'{acc:.1%}', ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/sensor_type_breakdown.png', dpi=150)
    plt.show()
    
    return {'temperature': temp_acc, 'humidity': hum_acc, 'gas': gas_acc}

def main():
    print("="*70)
    print("SENSOR IMPORTANCE ANALYSIS (6 classes)")
    print("="*70)
    print(f"Classes: {ALL_CLASSES}")
    print("="*70)
    
    df = load_and_pivot_data(DATA_DIR)
    if df is None:
        return
    
    print(f"\nClass distribution:\n{df['label'].value_counts()}")
    
    # Baseline with all sensors
    all_features = get_features(df)
    baseline_acc = evaluate_features(df, all_features, verbose=True)
    print(f"\n📊 BASELINE (all 8 sensors): {baseline_acc:.2%}")
    
    # Test each sensor individually
    print("\n" + "="*70)
    print("INDIVIDUAL SENSOR PERFORMANCE")
    print("="*70)
    
    sensor_accuracies = {}
    for sensor in range(8):
        sensor_features = [
            f'sensor_{sensor}_temperature',
            f'sensor_{sensor}_humidity',
            f'sensor_{sensor}_gas_resistance'
        ]
        acc = evaluate_features(df, sensor_features)
        sensor_accuracies[sensor] = acc
        print(f"  Sensor {sensor}: {acc:.2%}")
    
    # Test sensor combinations (remove one at a time)
    print("\n" + "="*70)
    print("LEAVE-ONE-SENSOR-OUT ANALYSIS")
    print("="*70)
    
    loo_accuracies = {}
    for sensor in range(8):
        features = [f for f in all_features if not f.startswith(f'sensor_{sensor}_')]
        acc = evaluate_features(df, features)
        loo_accuracies[sensor] = acc
        delta = baseline_acc - acc
        print(f"  Without Sensor {sensor}: {acc:.2%} (Δ = {delta:+.2%})")
    
    # Test sensor combinations (cumulative)
    print("\n" + "="*70)
    print("CUMULATIVE SENSOR COMBINATIONS")
    print("="*70)
    
    # Start with best individual sensor
    best_sensor = max(sensor_accuracies, key=sensor_accuracies.get)
    print(f"  Best individual sensor: Sensor {best_sensor} ({sensor_accuracies[best_sensor]:.2%})")
    
    # Add sensors one by one in order of importance
    remaining_sensors = list(range(8))
    current_sensors = [best_sensor]
    remaining_sensors.remove(best_sensor)
    
    cumulative_acc = {tuple(sorted(current_sensors)): sensor_accuracies[best_sensor]}
    
    while remaining_sensors:
        best_next = None
        best_next_acc = 0
        
        for s in remaining_sensors:
            test_features = []
            for sens in current_sensors + [s]:
                test_features.extend([
                    f'sensor_{sens}_temperature',
                    f'sensor_{sens}_humidity',
                    f'sensor_{sens}_gas_resistance'
                ])
            acc = evaluate_features(df, test_features)
            if acc > best_next_acc:
                best_next_acc = acc
                best_next = s
        
        if best_next is not None:
            current_sensors.append(best_next)
            remaining_sensors.remove(best_next)
            cumulative_acc[tuple(sorted(current_sensors))] = best_next_acc
            print(f"  + Sensor {best_next}: accuracy = {best_next_acc:.2%}")
    
    # Plots
    print("\n" + "="*70)
    print("GENERATING PLOTS")
    print("="*70)
    
    plot_individual_performance(sensor_accuracies, baseline_acc)
    plot_leave_one_out(loo_accuracies, baseline_acc)
    sensor_type_acc = plot_sensor_type_breakdown(df, baseline_acc)
    
    # Save results to CSV
    results_df = pd.DataFrame({
        'sensor': list(sensor_accuracies.keys()),
        'individual_accuracy': list(sensor_accuracies.values()),
        'accuracy_without': [loo_accuracies[s] for s in range(8)],
        'drop_when_removed': [baseline_acc - loo_accuracies[s] for s in range(8)]
    })
    results_df.to_csv(f'{OUTPUT_DIR}/sensor_importance.csv', index=False)
    
    # Sensor type summary
    type_df = pd.DataFrame([
        {'type': 'temperature', 'accuracy': sensor_type_acc['temperature']},
        {'type': 'humidity', 'accuracy': sensor_type_acc['humidity']},
        {'type': 'gas', 'accuracy': sensor_type_acc['gas']},
        {'type': 'all_sensors', 'accuracy': baseline_acc}
    ])
    type_df.to_csv(f'{OUTPUT_DIR}/sensor_type_importance.csv', index=False)
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"  Best individual sensor: Sensor {best_sensor} ({sensor_accuracies[best_sensor]:.2%})")
    print(f"  Worst individual sensor: Sensor {min(sensor_accuracies, key=sensor_accuracies.get)} "
          f"({sensor_accuracies[min(sensor_accuracies, key=sensor_accuracies.get)]:.2%})")
    
    most_important = max(loo_accuracies, key=lambda s: baseline_acc - loo_accuracies[s])
    least_important = min(loo_accuracies, key=lambda s: baseline_acc - loo_accuracies[s])
    print(f"  Most important sensor: Sensor {most_important} "
          f"(removing drops accuracy by {baseline_acc - loo_accuracies[most_important]:.2%})")
    print(f"  Least important sensor: Sensor {least_important} "
          f"(removing changes accuracy by {baseline_acc - loo_accuracies[least_important]:+.2%})")
    
    print(f"\n✅ Results saved to: {OUTPUT_DIR}/")
    print(f"   - sensor_individual_performance.png")
    print(f"   - sensor_leave_one_out.png")
    print(f"   - sensor_type_breakdown.png")
    print(f"   - sensor_importance.csv")
    print(f"   - sensor_type_importance.csv")

if __name__ == "__main__":
    main()