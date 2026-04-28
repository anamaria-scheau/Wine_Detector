"""
01_confusion_matrix_all.py - Full 6-class confusion matrix
Classes: Air, Toro, Garnacha, Monastrel (red), Macabeo, NOVELL (white)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score
import glob
import os
import warnings
warnings.filterwarnings('ignore')

# ============================================
# Configuration
# ============================================
DATA_DIR = '../csv_data_all_sensors'
OUTPUT_DIR = 'results/confusion_matrices'
TEST_SIZE = 0.2
RANDOM_STATE = 42
K_NEIGHBORS = 17

# ALL 6 CLASSES - CORRECT: 'novell' (not 'norvell')
ALL_CLASSES = ['air', 'toro', 'garnacha', 'monastrel', 'macabeo', 'novell']

# Group by type
RED_WINES = ['toro', 'garnacha', 'monastrel']      # 3 red wines
WHITE_WINES = ['macabeo', 'novell']                # 2 white wines

os.makedirs(OUTPUT_DIR, exist_ok=True)

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
    print(f"Unique labels in data: {combined_df['label'].unique()}")
    
    n_sensors = 8
    n_samples = len(combined_df) // n_sensors
    
    pivoted_data = []
    for i in range(n_samples):
        start_idx = i * n_sensors
        end_idx = start_idx + n_sensors
        sample_rows = combined_df.iloc[start_idx:end_idx]
        
        label = sample_rows['label'].iloc[0]
        row_data = {'label': label}
        
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

def main():
    print("="*70)
    print("CONFUSION MATRIX - ALL 6 CLASSES")
    print("="*70)
    print(f"Classes: {ALL_CLASSES}")
    print(f"  - Red wines: {RED_WINES}")
    print(f"  - White wines: {WHITE_WINES}")
    print("="*70)
    
    df = load_and_pivot_data(DATA_DIR)
    if df is None:
        return
    
    # Check if all classes exist
    missing_classes = [c for c in ALL_CLASSES if c not in df['label'].values]
    if missing_classes:
        print(f"\n⚠️ WARNING: Missing classes: {missing_classes}")
    
    features = get_features(df)
    X = df[features]
    y = df['label']
    
    if X.isnull().sum().sum() > 0:
        print(f"\nFound {X.isnull().sum().sum()} NaN values. Filling with median...")
        imputer = SimpleImputer(strategy='median')
        X = pd.DataFrame(imputer.fit_transform(X), columns=features)
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )
    
    print(f"\nTraining samples: {len(X_train)}")
    print(f"Test samples: {len(X_test)}")
    print(f"\nTest class distribution:")
    print(y_test.value_counts())
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    model = KNeighborsClassifier(n_neighbors=K_NEIGHBORS, weights='uniform', metric='euclidean')
    model.fit(X_train_scaled, y_train)
    
    y_pred = model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\n{'='*70}")
    print(f"OVERALL ACCURACY (6 classes): {accuracy:.4f} ({accuracy*100:.2f}%)")
    print(f"{'='*70}")
    
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    cm = confusion_matrix(y_test, y_pred, labels=ALL_CLASSES)
    
    # Plot confusion matrix
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=ALL_CLASSES, yticklabels=ALL_CLASSES)
    plt.title(f'Confusion Matrix - All 6 Classes\nAccuracy: {accuracy*100:.2f}%', fontsize=14, fontweight='bold')
    plt.ylabel('Actual', fontsize=12)
    plt.xlabel('Predicted', fontsize=12)
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/confusion_matrix_6class.png', dpi=150)
    plt.show()
    
    # Normalized (handle division by zero)
    with np.errstate(divide='ignore', invalid='ignore'):
        cm_norm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        cm_norm = np.nan_to_num(cm_norm, nan=0.0)
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm_norm, annot=True, fmt='.2f', cmap='Blues',
                xticklabels=ALL_CLASSES, yticklabels=ALL_CLASSES)
    plt.title(f'Confusion Matrix - All 6 Classes (Normalized %)\nAccuracy: {accuracy*100:.2f}%', 
              fontsize=14, fontweight='bold')
    plt.ylabel('Actual', fontsize=12)
    plt.xlabel('Predicted', fontsize=12)
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/confusion_matrix_6class_norm.png', dpi=150)
    plt.show()
    
    # Save
    cm_df = pd.DataFrame(cm, index=ALL_CLASSES, columns=ALL_CLASSES)
    cm_df.to_csv(f'{OUTPUT_DIR}/confusion_matrix_6class.csv')
    
    with open(f'{OUTPUT_DIR}/classification_report_6class.txt', 'w') as f:
        f.write(f"Overall Accuracy: {accuracy*100:.2f}%\n\n")
        f.write(classification_report(y_test, y_pred))
    
    # Per-class accuracy
    print("\n" + "="*70)
    print("PER-CLASS ACCURACY")
    print("="*70)
    for i, name in enumerate(ALL_CLASSES):
        class_correct = cm[i, i]
        class_total = cm[i, :].sum()
        if class_total > 0:
            class_acc = class_correct / class_total
            wine_type = "Red" if name in RED_WINES else ("White" if name in WHITE_WINES else "Air")
            print(f"  {name:12s} ({wine_type:5s}): {class_acc:.4f} ({class_acc*100:.2f}%) - {class_correct}/{class_total}")
        else:
            print(f"  {name:12s}: NO SAMPLES IN TEST SET")
    
    print(f"\n✅ Results saved to: {OUTPUT_DIR}/")

if __name__ == "__main__":
    main()