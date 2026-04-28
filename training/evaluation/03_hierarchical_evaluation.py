"""
Hierarchical Evaluation - Levels 1, 2, 3
Evaluates the cascade classification system

Classes: air, toro, garnacha, monastrel (red), macabeo, novell (white)
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
OUTPUT_DIR = 'results/hierarchical'
TEST_SIZE = 0.2
RANDOM_STATE = 42
K_NEIGHBORS = 17

# ALL 6 CLASSES
ALL_CLASSES = ['air', 'toro', 'garnacha', 'monastrel', 'macabeo', 'novell']

# Red wines (3 classes)
RED_WINES = ['toro', 'garnacha', 'monastrel']

# White wines (2 classes)
WHITE_WINES = ['macabeo', 'novell']

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

def clean_data(X, y):
    """Remove rows with NaN and impute missing values"""
    # Remove rows where y is NaN
    mask = ~y.isna()
    X = X[mask]
    y = y[mask]
    
    # Impute NaN values in X
    if X.isnull().sum().sum() > 0:
        imputer = SimpleImputer(strategy='median')
        X = pd.DataFrame(imputer.fit_transform(X), columns=X.columns)
    
    return X, y

def train_model(X, y, model_name=""):
    """Train and evaluate a model"""
    X, y = clean_data(X, y)
    
    if len(X) == 0:
        print(f"  ERROR: No valid data for {model_name}")
        return None, None, None, None, None
    
    # Check if we have enough samples
    if len(y.unique()) < 2:
        print(f"  WARNING: Only one class found in {model_name}: {y.unique()}")
        return None, None, None, None, None
    
    # Use stratified split if possible
    min_class_count = y.value_counts().min()
    if min_class_count < 2:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE
        )
    else:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
        )
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    n_neighbors = min(K_NEIGHBORS, len(X_train))
    model = KNeighborsClassifier(n_neighbors=n_neighbors)
    model.fit(X_train_scaled, y_train)
    
    y_pred = model.predict(X_test_scaled)
    acc = accuracy_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)
    
    return acc, cm, model.classes_, y_test, y_pred

def plot_confusion_matrix(cm, classes, title, filename):
    """Plot and save confusion matrix"""
    plt.figure(figsize=(max(5, len(classes) * 1.5), max(4, len(classes) * 1.2)))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=classes, yticklabels=classes)
    plt.title(title, fontsize=14, fontweight='bold')
    plt.ylabel('Actual', fontsize=12)
    plt.xlabel('Predicted', fontsize=12)
    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    plt.close()

def main():
    print("="*70)
    print("HIERARCHICAL EVALUATION - 6 CLASSES")
    print("="*70)
    print(f"Classes: {ALL_CLASSES}")
    print(f"  - Red wines: {RED_WINES}")
    print(f"  - White wines: {WHITE_WINES}")
    print("="*70)
    
    df = load_and_pivot_data(DATA_DIR)
    if df is None:
        return
    
    features = get_features(df)
    
    # ============================================
    # LEVEL 1: Air vs Wine
    # ============================================
    print("\n" + "="*70)
    print("LEVEL 1: Air vs Wine")
    print("="*70)
    
    df_l1 = df.copy()
    df_l1['label_l1'] = df_l1['label'].apply(lambda x: 'air' if x == 'air' else 'wine')
    X_l1 = df_l1[features].copy()
    y_l1 = df_l1['label_l1'].copy()
    
    acc1, cm1, classes1, _, _ = train_model(X_l1, y_l1, "Level 1")
    
    if acc1 is not None:
        print(f"  Accuracy: {acc1:.4f} ({acc1*100:.2f}%)")
        print(f"  Samples: {len(y_l1)}")
        print(f"  Classes: {classes1}")
        
        plot_confusion_matrix(cm1, classes1, 
                              f'Level 1: Air vs Wine\nAccuracy: {acc1*100:.2f}%',
                              f'{OUTPUT_DIR}/level1_air_vs_wine.png')
    else:
        print("  ERROR: Could not train Level 1 model")
    
    # ============================================
    # LEVEL 2: Red vs White (only wine samples)
    # ============================================
    print("\n" + "="*70)
    print("LEVEL 2: Red vs White")
    print("="*70)
    
    df_wine = df[df['label'] != 'air'].copy()
    
    # Check if we have both red and white wines
    has_red = any(label in RED_WINES for label in df_wine['label'].unique())
    has_white = any(label in WHITE_WINES for label in df_wine['label'].unique())
    
    if has_red and has_white:
        df_wine['label_l2'] = df_wine['label'].apply(
            lambda x: 'red' if x in RED_WINES else 'white'
        )
        X_l2 = df_wine[features].copy()
        y_l2 = df_wine['label_l2'].copy()
        
        acc2, cm2, classes2, _, _ = train_model(X_l2, y_l2, "Level 2")
        
        if acc2 is not None:
            print(f"  Accuracy: {acc2:.4f} ({acc2*100:.2f}%)")
            print(f"  Samples: {len(y_l2)}")
            print(f"  Classes: {classes2}")
            
            # Show class distribution
            print(f"  Distribution:")
            print(f"    Red wines: {sum(df_wine['label_l2'] == 'red')}")
            print(f"    White wines: {sum(df_wine['label_l2'] == 'white')}")
            
            plot_confusion_matrix(cm2, classes2,
                                  f'Level 2: Red vs White\nAccuracy: {acc2*100:.2f}%',
                                  f'{OUTPUT_DIR}/level2_red_vs_white.png')
        else:
            print("  ERROR: Could not train Level 2 model")
    else:
        print("  SKIPPED: Missing red or white wine classes")
        print(f"    Red wines present: {has_red}")
        print(f"    White wines present: {has_white}")
    
    # ============================================
    # LEVEL 3a: Red Region (3 classes)
    # ============================================
    print("\n" + "="*70)
    print("LEVEL 3a: Red Region (Toro, Garnacha, Monastrel)")
    print("="*70)
    
    df_red = df[df['label'].isin(RED_WINES)].copy()
    
    if len(df_red) > 0 and len(df_red['label'].unique()) >= 2:
        X_l3a = df_red[features].copy()
        y_l3a = df_red['label'].copy()
        
        acc3a, cm3a, classes3a, y_test3a, y_pred3a = train_model(X_l3a, y_l3a, "Level 3a")
        
        if acc3a is not None:
            print(f"  Accuracy: {acc3a:.4f} ({acc3a*100:.2f}%)")
            print(f"  Samples: {len(y_l3a)}")
            print(f"  Classes: {classes3a}")
            
            print("\n  Classification Report:")
            print(classification_report(y_test3a, y_pred3a))
            
            plot_confusion_matrix(cm3a, classes3a,
                                  f'Level 3a: Red Region\nAccuracy: {acc3a*100:.2f}%',
                                  f'{OUTPUT_DIR}/level3a_red_region.png')
        else:
            print("  ERROR: Could not train Level 3a model")
    else:
        print("  SKIPPED: Insufficient red wine data")
        print(f"    Samples: {len(df_red)}")
        print(f"    Unique classes: {df_red['label'].unique()}")
    
    # ============================================
    # LEVEL 3b: White Region (2 classes: Macabeo, Novell)
    # ============================================
    print("\n" + "="*70)
    print("LEVEL 3b: White Region (Macabeo, Novell)")
    print("="*70)
    
    df_white = df[df['label'].isin(WHITE_WINES)].copy()
    
    if len(df_white) > 0 and len(df_white['label'].unique()) >= 2:
        X_l3b = df_white[features].copy()
        y_l3b = df_white['label'].copy()
        
        acc3b, cm3b, classes3b, y_test3b, y_pred3b = train_model(X_l3b, y_l3b, "Level 3b")
        
        if acc3b is not None:
            print(f"  Accuracy: {acc3b:.4f} ({acc3b*100:.2f}%)")
            print(f"  Samples: {len(y_l3b)}")
            print(f"  Classes: {classes3b}")
            
            print("\n  Classification Report:")
            print(classification_report(y_test3b, y_pred3b))
            
            plot_confusion_matrix(cm3b, classes3b,
                                  f'Level 3b: White Region\nAccuracy: {acc3b*100:.2f}%',
                                  f'{OUTPUT_DIR}/level3b_white_region.png')
        else:
            print("  ERROR: Could not train Level 3b model")
    else:
        if len(df_white) > 0:
            print(f"  SKIPPED: Only one white wine class found: {df_white['label'].unique()}")
            print(f"    Need both Macabeo and Novell for 2-class classification")
        else:
            print("  SKIPPED: No white wine data found")
    
    # ============================================
    # SUMMARY
    # ============================================
    print("\n" + "="*70)
    print("HIERARCHICAL PERFORMANCE SUMMARY")
    print("="*70)
    
    summary = []
    if acc1 is not None:
        summary.append(f"Level 1 (Air vs Wine):          {acc1*100:.2f}%")
    if 'acc2' in locals() and acc2 is not None:
        summary.append(f"Level 2 (Red vs White):         {acc2*100:.2f}%")
    if 'acc3a' in locals() and acc3a is not None:
        summary.append(f"Level 3a (Red Region - 3 wines): {acc3a*100:.2f}%")
    if 'acc3b' in locals() and acc3b is not None:
        summary.append(f"Level 3b (White Region - 2 wines): {acc3b*100:.2f}%")
    
    for line in summary:
        print(f"  {line}")
    
    print("="*70)
    
    # Calculate overall cascade accuracy
    if acc1 is not None and 'acc2' in locals() and acc2 is not None:
        overall = acc1 * acc2
        print(f"\nOverall Cascade Accuracy (Level 1 × Level 2): {overall*100:.2f}%")
    
    # Save summary to file
    with open(f'{OUTPUT_DIR}/hierarchical_summary.txt', 'w') as f:
        f.write("HIERARCHICAL EVALUATION SUMMARY\n")
        f.write("="*50 + "\n")
        f.write(f"Classes: {ALL_CLASSES}\n")
        f.write(f"Red wines: {RED_WINES}\n")
        f.write(f"White wines: {WHITE_WINES}\n")
        f.write("-"*50 + "\n")
        for line in summary:
            f.write(line + "\n")
        f.write("-"*50 + "\n")
        if acc1 is not None and 'acc2' in locals() and acc2 is not None:
            f.write(f"Overall Cascade Accuracy: {overall*100:.2f}%\n")
    
    print(f"\n✅ Results saved to: {OUTPUT_DIR}/")
    print(f"   - level1_air_vs_wine.png")
    print(f"   - level2_red_vs_white.png")
    print(f"   - level3a_red_region.png")
    if 'acc3b' in locals() and acc3b is not None:
        print(f"   - level3b_white_region.png")
    print(f"   - hierarchical_summary.txt")

if __name__ == "__main__":
    main()