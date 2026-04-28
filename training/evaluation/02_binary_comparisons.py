"""
Binary Comparisons Between All Classes (6 classes)
Generates pairwise confusion matrices for all combinations
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
from sklearn.metrics import confusion_matrix, accuracy_score
import glob
import os
import warnings
warnings.filterwarnings('ignore')

# ============================================
# Configuration
# ============================================
DATA_DIR = '../csv_data_all_sensors'
OUTPUT_DIR = 'results/binary_comparisons'
TEST_SIZE = 0.2
RANDOM_STATE = 42
K_NEIGHBORS = 17

# ALL 6 CLASSES
ALL_CLASSES = ['air', 'toro', 'garnacha', 'monastrel', 'macabeo', 'novell']

# Wine classes
WINE_CLASSES = ['toro', 'garnacha', 'monastrel', 'macabeo', 'novell']

# Red wines
RED_WINES = ['toro', 'garnacha', 'monastrel']

# White wines
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

def binary_comparison(df, class_a, class_b):
    """Train and evaluate binary classifier between two classes"""
    subset = df[df['label'].isin([class_a, class_b])]
    features = get_features(subset)
    X = subset[features]
    y = subset['label']
    
    if len(subset) == 0:
        return None, None, 0
    
    if X.isnull().sum().sum() > 0:
        imputer = SimpleImputer(strategy='median')
        X = pd.DataFrame(imputer.fit_transform(X), columns=features)
    
    # Need at least 2 samples per class for stratification
    min_class_count = y.value_counts().min()
    if min_class_count < 2:
        # Use simple split without stratification
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
    
    model = KNeighborsClassifier(n_neighbors=min(K_NEIGHBORS, len(X_train)))
    model.fit(X_train_scaled, y_train)
    
    y_pred = model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred, labels=[class_a, class_b])
    
    return accuracy, cm, len(subset)

def plot_binary_cm(class_a, class_b, cm, accuracy):
    """Plot and save binary confusion matrix"""
    plt.figure(figsize=(5, 4))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=[class_a, class_b], yticklabels=[class_a, class_b])
    plt.title(f'{class_a.upper()} vs {class_b.upper()}\nAccuracy: {accuracy:.2%}')
    plt.ylabel('Actual')
    plt.xlabel('Predicted')
    plt.tight_layout()
    filename = f"{OUTPUT_DIR}/{class_a}_vs_{class_b}.png"
    plt.savefig(filename, dpi=150)
    plt.close()
    return filename

def plot_full_matrix(accuracies, classes):
    """Plot heatmap of all pairwise accuracies"""
    n = len(classes)
    matrix = np.zeros((n, n))
    
    for i, ci in enumerate(classes):
        for j, cj in enumerate(classes):
            if i == j:
                matrix[i, j] = 1.0
            else:
                key = f"{ci}_vs_{cj}"
                matrix[i, j] = accuracies.get(key, 0)
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(matrix, annot=True, fmt='.2%', cmap='RdYlGn',
                xticklabels=classes, yticklabels=classes,
                vmin=0.5, vmax=1.0, center=0.75)
    plt.title('Binary Classification Accuracy Matrix (6 classes)', fontsize=14, fontweight='bold')
    plt.ylabel('Class A')
    plt.xlabel('Class B')
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/binary_comparison_matrix_full.png', dpi=150)
    plt.show()

def plot_red_wines_matrix(accuracies):
    """Plot heatmap for red wines only"""
    n = len(RED_WINES)
    matrix = np.zeros((n, n))
    
    for i, ci in enumerate(RED_WINES):
        for j, cj in enumerate(RED_WINES):
            if i == j:
                matrix[i, j] = 1.0
            else:
                key = f"{ci}_vs_{cj}"
                matrix[i, j] = accuracies.get(key, 0)
    
    plt.figure(figsize=(8, 6))
    sns.heatmap(matrix, annot=True, fmt='.2%', cmap='Reds',
                xticklabels=RED_WINES, yticklabels=RED_WINES,
                vmin=0.5, vmax=1.0, center=0.75)
    plt.title('Binary Classification - Red Wines Only\nToro vs Garnacha vs Monastrel', 
              fontsize=14, fontweight='bold')
    plt.ylabel('Class A')
    plt.xlabel('Class B')
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/binary_comparison_red_wines.png', dpi=150)
    plt.show()

def plot_white_wines_matrix(accuracies):
    """Plot heatmap for white wines only"""
    n = len(WHITE_WINES)
    matrix = np.zeros((n, n))
    
    for i, ci in enumerate(WHITE_WINES):
        for j, cj in enumerate(WHITE_WINES):
            if i == j:
                matrix[i, j] = 1.0
            else:
                key = f"{ci}_vs_{cj}"
                matrix[i, j] = accuracies.get(key, 0)
    
    plt.figure(figsize=(6, 5))
    sns.heatmap(matrix, annot=True, fmt='.2%', cmap='Greens',
                xticklabels=WHITE_WINES, yticklabels=WHITE_WINES,
                vmin=0.5, vmax=1.0, center=0.75)
    plt.title('Binary Classification - White Wines Only\nMacabeo vs Novell', 
              fontsize=14, fontweight='bold')
    plt.ylabel('Class A')
    plt.xlabel('Class B')
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/binary_comparison_white_wines.png', dpi=150)
    plt.show()

def main():
    print("="*70)
    print("BINARY COMPARISONS BETWEEN ALL CLASSES (6 classes)")
    print("="*70)
    print(f"Classes: {ALL_CLASSES}")
    print(f"  - Red wines: {RED_WINES}")
    print(f"  - White wines: {WHITE_WINES}")
    print("="*70)
    
    df = load_and_pivot_data(DATA_DIR)
    if df is None:
        return
    
    print(f"\nClass distribution:\n{df['label'].value_counts()}")
    
    accuracies = {}
    
    # Air vs each wine
    print("\n" + "="*70)
    print("1. AIR vs EACH WINE")
    print("="*70)
    for wine in WINE_CLASSES:
        acc, cm, n = binary_comparison(df, 'air', wine)
        if acc is not None:
            accuracies[f"air_vs_{wine}"] = acc
            accuracies[f"{wine}_vs_air"] = acc
            plot_binary_cm('air', wine, cm, acc)
            print(f"  Air vs {wine:12s}: {acc:.2%} (n={n} samples)")
        else:
            print(f"  Air vs {wine:12s}: SKIPPED - insufficient data")
    
    # Wine vs wine (all pairs)
    print("\n" + "="*70)
    print("2. WINE vs WINE (all pairs)")
    print("="*70)
    for i, wa in enumerate(WINE_CLASSES):
        for wb in WINE_CLASSES[i+1:]:
            acc, cm, n = binary_comparison(df, wa, wb)
            if acc is not None:
                accuracies[f"{wa}_vs_{wb}"] = acc
                accuracies[f"{wb}_vs_{wa}"] = acc
                plot_binary_cm(wa, wb, cm, acc)
                print(f"  {wa:12s} vs {wb:12s}: {acc:.2%} (n={n} samples)")
            else:
                print(f"  {wa:12s} vs {wb:12s}: SKIPPED - insufficient data")
    
    # Red wines only
    print("\n" + "="*70)
    print("3. RED WINES ONLY (Toro, Garnacha, Monastrel)")
    print("="*70)
    for i, wa in enumerate(RED_WINES):
        for wb in RED_WINES[i+1:]:
            acc, cm, n = binary_comparison(df, wa, wb)
            if acc is not None:
                accuracies[f"{wa}_vs_{wb}"] = acc
                accuracies[f"{wb}_vs_{wa}"] = acc
                plot_binary_cm(wa, wb, cm, acc)
                print(f"  {wa:12s} vs {wb:12s}: {acc:.2%} (n={n} samples)")
            else:
                print(f"  {wa:12s} vs {wb:12s}: SKIPPED - insufficient data")
    
    # White wines only
    print("\n" + "="*70)
    print("4. WHITE WINES ONLY (Macabeo, Novell)")
    print("="*70)
    for i, wa in enumerate(WHITE_WINES):
        for wb in WHITE_WINES[i+1:]:
            acc, cm, n = binary_comparison(df, wa, wb)
            if acc is not None:
                accuracies[f"{wa}_vs_{wb}"] = acc
                accuracies[f"{wb}_vs_{wa}"] = acc
                plot_binary_cm(wa, wb, cm, acc)
                print(f"  {wa:12s} vs {wb:12s}: {acc:.2%} (n={n} samples)")
            else:
                print(f"  {wa:12s} vs {wb:12s}: SKIPPED - insufficient data")
    
    # Summary matrices
    print("\n" + "="*70)
    print("5. GENERATING SUMMARY MATRICES")
    print("="*70)
    
    plot_full_matrix(accuracies, ALL_CLASSES)
    plot_red_wines_matrix(accuracies)
    plot_white_wines_matrix(accuracies)
    
    # Save accuracies to CSV
    acc_df = pd.DataFrame(list(accuracies.items()), columns=['Comparison', 'Accuracy'])
    acc_df.to_csv(f'{OUTPUT_DIR}/binary_accuracies.csv', index=False)
    
    print(f"\n✅ Results saved to: {OUTPUT_DIR}/")
    print(f"   - Individual comparisons: {len(accuracies)//2} PNG files")
    print(f"   - Full matrix: binary_comparison_matrix_full.png")
    print(f"   - Red wines matrix: binary_comparison_red_wines.png")
    print(f"   - White wines matrix: binary_comparison_white_wines.png")
    print(f"   - Accuracies CSV: binary_accuracies.csv")

if __name__ == "__main__":
    main()