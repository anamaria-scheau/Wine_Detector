"""
Variety Analysis - Per-wine performance metrics
Analyzes precision, recall, F1-score for each wine variety
Classes: air, toro, garnacha, monastrel (red), macabeo, novell (white)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.metrics import classification_report, accuracy_score
import glob
import os
import warnings
warnings.filterwarnings('ignore')

# ============================================
# Configuration
# ============================================
DATA_DIR = '../csv_data_all_sensors'
OUTPUT_DIR = 'results/variety_analysis'
TEST_SIZE = 0.2
RANDOM_STATE = 42
K_NEIGHBORS = 17

# ALL 6 CLASSES
ALL_CLASSES = ['air', 'toro', 'garnacha', 'monastrel', 'macabeo', 'novell']

# Wine classes only
WINE_CLASSES = ['toro', 'garnacha', 'monastrel', 'macabeo', 'novell']

# Group by type
RED_WINES = ['toro', 'garnacha', 'monastrel']
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

def clean_dataframe(df):
    """Remove any rows with NaN values and ensure all data is clean"""
    feature_cols = [col for col in df.columns if col.startswith('sensor_')]
    initial_len = len(df)
    df_clean = df.dropna(subset=feature_cols)
    
    if len(df_clean) < initial_len:
        print(f"    Removed {initial_len - len(df_clean)} rows with NaN values")
    
    return df_clean

def train_and_evaluate(X, y, model_name=""):
    """Train and evaluate a model, return y_test and y_pred"""
    if len(X) == 0:
        print(f"  ERROR: No data for {model_name}")
        return None, None
    
    if len(np.unique(y)) < 2:
        print(f"  WARNING: Only one class in {model_name}: {np.unique(y)}")
        return None, None
    
    try:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
        )
    except ValueError:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE
        )
    
    # Impute any remaining NaN
    imputer = SimpleImputer(strategy='median')
    X_train = imputer.fit_transform(X_train)
    X_test = imputer.transform(X_test)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    n_neighbors = min(K_NEIGHBORS, len(X_train))
    model = KNeighborsClassifier(n_neighbors=n_neighbors)
    model.fit(X_train_scaled, y_train)
    
    y_pred = model.predict(X_test_scaled)
    
    return y_test, y_pred

def plot_bar_chart(data, title, ylabel, filename, colors=None):
    """Generic bar chart plotter"""
    if len(data) == 0:
        return
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    classes = list(data.keys())
    values = list(data.values())
    
    if colors is None:
        colors = ['steelblue'] * len(classes)
    
    bars = ax.bar(classes, values, color=colors)
    ax.set_ylim(0, 1)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.axhline(y=0.8, color='green', linestyle='--', alpha=0.5, label='Target (0.8)')
    ax.legend()
    
    # Add value labels
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f'{val:.3f}', ha='center', va='bottom', fontsize=9)
    
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    plt.close()

def print_table(df, title, colors=True):
    """Print a formatted table with colors using pandas styling"""
    print("\n" + "="*80)
    print(f"📊 {title}")
    print("="*80)
    
    # Format the DataFrame
    display_df = df.copy()
    
    # Format percentage columns
    for col in ['precision', 'recall', 'f1_score']:
        if col in display_df.columns:
            display_df[col] = display_df[col].apply(lambda x: f"{x:.4f} ({x*100:.2f}%)")
    
    # Print the table
    print(display_df.to_string(index=False))
    print("="*80)

def save_table_to_csv(df, filename):
    """Save table to CSV"""
    df.to_csv(filename, index=False)
    print(f"  💾 Saved to: {filename}")

def main():
    print("="*70)
    print("VARIETY ANALYSIS - Per-Wine Performance (6 classes)")
    print("="*70)
    print(f"Classes: {ALL_CLASSES}")
    print(f"  - Red wines: {RED_WINES}")
    print(f"  - White wines: {WHITE_WINES}")
    print("="*70)
    
    df = load_and_pivot_data(DATA_DIR)
    if df is None:
        return
    
    # Clean the entire dataframe first
    df = clean_dataframe(df)
    print(f"\nAfter cleaning: {len(df)} samples")
    
    features = get_features(df)
    
    # ============================================
    # FULL 6-CLASS MODEL
    # ============================================
    print("\n" + "="*50)
    print("FULL 6-CLASS MODEL")
    print("="*50)
    
    X_full = df[features]
    y_full = df['label']
    
    y_test_full, y_pred_full = train_and_evaluate(X_full, y_full, "Full 6-class")
    
    if y_test_full is None:
        print("ERROR: Could not train full model")
        return
    
    # Calculate metrics
    report = classification_report(y_test_full, y_pred_full, output_dict=True)
    
    # Extract per-class metrics
    precision_dict = {}
    recall_dict = {}
    f1_dict = {}
    support_dict = {}
    
    for cls in ALL_CLASSES:
        if cls in report:
            precision_dict[cls] = report[cls]['precision']
            recall_dict[cls] = report[cls]['recall']
            f1_dict[cls] = report[cls]['f1-score']
            support_dict[cls] = report[cls]['support']
    
    # Create table for 6 classes
    table_6class = pd.DataFrame({
        'Class': list(precision_dict.keys()),
        'Type': ['Air' if c == 'air' else ('Red' if c in RED_WINES else 'White') for c in precision_dict.keys()],
        'Precision': [precision_dict[c] for c in precision_dict.keys()],
        'Recall': [recall_dict[c] for c in precision_dict.keys()],
        'F1-Score': [f1_dict[c] for c in precision_dict.keys()],
        'Support': [support_dict[c] for c in precision_dict.keys()]
    })
    
    # Sort by F1-Score descending
    table_6class = table_6class.sort_values('F1-Score', ascending=False)
    
    print_table(table_6class, "VARIETY ANALYSIS - ALL 6 CLASSES")
    save_table_to_csv(table_6class, f'{OUTPUT_DIR}/table_6class.csv')
    
    # Colors for classes
    colors = []
    for cls in ALL_CLASSES:
        if cls == 'air':
            colors.append('gray')
        elif cls in RED_WINES:
            colors.append('darkred')
        elif cls in WHITE_WINES:
            colors.append('goldenrod')
        else:
            colors.append('steelblue')
    
    # Plot all metrics
    plot_bar_chart(precision_dict, 'Precision by Class (6 classes)', 'Precision', 
                   f'{OUTPUT_DIR}/precision_6class.png', colors)
    plot_bar_chart(recall_dict, 'Recall by Class (6 classes)', 'Recall', 
                   f'{OUTPUT_DIR}/recall_6class.png', colors)
    plot_bar_chart(f1_dict, 'F1-Score by Class (6 classes)', 'F1-Score', 
                   f'{OUTPUT_DIR}/f1score_6class.png', colors)
    
    # ============================================
    # WINES ONLY (5 classes)
    # ============================================
    print("\n" + "="*50)
    print("WINES ONLY (5 classes)")
    print("="*50)
    
    df_wines = df[df['label'].isin(WINE_CLASSES)].copy()
    df_wines = clean_dataframe(df_wines)
    
    if len(df_wines) > 0:
        X_wines = df_wines[features]
        y_wines = df_wines['label']
        
        y_test_wines, y_pred_wines = train_and_evaluate(X_wines, y_wines, "Wines only")
        
        if y_test_wines is not None:
            report_wines = classification_report(y_test_wines, y_pred_wines, output_dict=True)
            
            precision_w = {}
            recall_w = {}
            f1_w = {}
            support_w = {}
            
            for cls in WINE_CLASSES:
                if cls in report_wines:
                    precision_w[cls] = report_wines[cls]['precision']
                    recall_w[cls] = report_wines[cls]['recall']
                    f1_w[cls] = report_wines[cls]['f1-score']
                    support_w[cls] = report_wines[cls]['support']
            
            # Create table for wines only
            table_wines = pd.DataFrame({
                'Wine': list(precision_w.keys()),
                'Type': ['Red' if c in RED_WINES else 'White' for c in precision_w.keys()],
                'Precision': [precision_w[c] for c in precision_w.keys()],
                'Recall': [recall_w[c] for c in precision_w.keys()],
                'F1-Score': [f1_w[c] for c in precision_w.keys()],
                'Support': [support_w[c] for c in precision_w.keys()]
            })
            table_wines = table_wines.sort_values('F1-Score', ascending=False)
            
            print_table(table_wines, "VARIETY ANALYSIS - WINES ONLY (5 classes)")
            save_table_to_csv(table_wines, f'{OUTPUT_DIR}/table_wines.csv')
            
            wine_colors = ['darkred' if c in RED_WINES else 'goldenrod' for c in WINE_CLASSES]
            
            plot_bar_chart(precision_w, 'Precision by Wine (5 classes)', 'Precision',
                          f'{OUTPUT_DIR}/precision_wines.png', wine_colors)
            plot_bar_chart(recall_w, 'Recall by Wine (5 classes)', 'Recall',
                          f'{OUTPUT_DIR}/recall_wines.png', wine_colors)
            plot_bar_chart(f1_w, 'F1-Score by Wine (5 classes)', 'F1-Score',
                          f'{OUTPUT_DIR}/f1score_wines.png', wine_colors)
    
    # ============================================
    # RED WINES ONLY (3 classes)
    # ============================================
    print("\n" + "="*50)
    print("RED WINES ONLY (3 classes)")
    print("="*50)
    
    df_red = df[df['label'].isin(RED_WINES)].copy()
    df_red = clean_dataframe(df_red)
    
    if len(df_red) > 0:
        X_red = df_red[features]
        y_red = df_red['label']
        
        y_test_red, y_pred_red = train_and_evaluate(X_red, y_red, "Red wines")
        
        if y_test_red is not None:
            acc_red = accuracy_score(y_test_red, y_pred_red)
            print(f"  Accuracy: {acc_red:.4f} ({acc_red*100:.2f}%)")
            
            report_red = classification_report(y_test_red, y_pred_red, output_dict=True)
            
            precision_r = {}
            recall_r = {}
            f1_r = {}
            support_r = {}
            
            for cls in RED_WINES:
                if cls in report_red:
                    precision_r[cls] = report_red[cls]['precision']
                    recall_r[cls] = report_red[cls]['recall']
                    f1_r[cls] = report_red[cls]['f1-score']
                    support_r[cls] = report_red[cls]['support']
            
            # Create table for red wines
            table_red = pd.DataFrame({
                'Red Wine': list(precision_r.keys()),
                'Precision': [precision_r[c] for c in precision_r.keys()],
                'Recall': [recall_r[c] for c in precision_r.keys()],
                'F1-Score': [f1_r[c] for c in precision_r.keys()],
                'Support': [support_r[c] for c in precision_r.keys()]
            })
            table_red = table_red.sort_values('F1-Score', ascending=False)
            
            print_table(table_red, "RED WINES ONLY (3 classes)")
            save_table_to_csv(table_red, f'{OUTPUT_DIR}/table_red_wines.csv')
            
            plot_bar_chart(precision_r, 'Precision - Red Wines', 'Precision',
                          f'{OUTPUT_DIR}/precision_red_wines.png', ['darkred']*3)
            plot_bar_chart(recall_r, 'Recall - Red Wines', 'Recall',
                          f'{OUTPUT_DIR}/recall_red_wines.png', ['darkred']*3)
            plot_bar_chart(f1_r, 'F1-Score - Red Wines', 'F1-Score',
                          f'{OUTPUT_DIR}/f1score_red_wines.png', ['darkred']*3)
    
    # ============================================
    # WHITE WINES ONLY (2 classes)
    # ============================================
    print("\n" + "="*50)
    print("WHITE WINES ONLY (2 classes)")
    print("="*50)
    
    df_white = df[df['label'].isin(WHITE_WINES)].copy()
    df_white = clean_dataframe(df_white)
    
    if len(df_white) > 0 and len(df_white['label'].unique()) >= 2:
        X_white = df_white[features]
        y_white = df_white['label']
        
        y_test_white, y_pred_white = train_and_evaluate(X_white, y_white, "White wines")
        
        if y_test_white is not None:
            acc_white = accuracy_score(y_test_white, y_pred_white)
            print(f"  Accuracy: {acc_white:.4f} ({acc_white*100:.2f}%)")
            
            report_white = classification_report(y_test_white, y_pred_white, output_dict=True)
            
            precision_w = {}
            recall_w = {}
            f1_w = {}
            support_w = {}
            
            for cls in WHITE_WINES:
                if cls in report_white:
                    precision_w[cls] = report_white[cls]['precision']
                    recall_w[cls] = report_white[cls]['recall']
                    f1_w[cls] = report_white[cls]['f1-score']
                    support_w[cls] = report_white[cls]['support']
            
            # Create table for white wines
            table_white = pd.DataFrame({
                'White Wine': list(precision_w.keys()),
                'Precision': [precision_w[c] for c in precision_w.keys()],
                'Recall': [recall_w[c] for c in precision_w.keys()],
                'F1-Score': [f1_w[c] for c in precision_w.keys()],
                'Support': [support_w[c] for c in precision_w.keys()]
            })
            table_white = table_white.sort_values('F1-Score', ascending=False)
            
            print_table(table_white, "WHITE WINES ONLY (2 classes)")
            save_table_to_csv(table_white, f'{OUTPUT_DIR}/table_white_wines.csv')
            
            plot_bar_chart(precision_w, 'Precision - White Wines', 'Precision',
                          f'{OUTPUT_DIR}/precision_white_wines.png', ['goldenrod', 'goldenrod'])
            plot_bar_chart(recall_w, 'Recall - White Wines', 'Recall',
                          f'{OUTPUT_DIR}/recall_white_wines.png', ['goldenrod', 'goldenrod'])
            plot_bar_chart(f1_w, 'F1-Score - White Wines', 'F1-Score',
                          f'{OUTPUT_DIR}/f1score_white_wines.png', ['goldenrod', 'goldenrod'])
    elif len(df_white) > 0:
        print(f"  Only one white wine class: {df_white['label'].unique()}")
        print("  Need both Macabeo and Novell for 2-class analysis")
    
    # ============================================
    # SAVE ALL METRICS TO CSV (summary)
    # ============================================
    
    # Create summary DataFrame
    summary_data = []
    for cls in ALL_CLASSES:
        if cls in precision_dict:
            summary_data.append({
                'class': cls,
                'type': 'air' if cls == 'air' else ('red' if cls in RED_WINES else 'white'),
                'precision': precision_dict[cls],
                'recall': recall_dict[cls],
                'f1_score': f1_dict[cls],
                'support': support_dict[cls]
            })
    
    summary_df = pd.DataFrame(summary_data)
    summary_df.to_csv(f'{OUTPUT_DIR}/variety_analysis_summary.csv', index=False)
    
    # ============================================
    # PRINT FINAL SUMMARY TABLE (console)
    # ============================================
    print("\n" + "="*80)
    print("📈 FINAL SUMMARY - ALL VARIETIES (Sorted by F1-Score)")
    print("="*80)
    
    # Create a nice formatted summary
    final_summary = summary_df.copy()
    final_summary['f1_score'] = final_summary['f1_score'].apply(lambda x: f"{x:.4f}")
    final_summary['precision'] = final_summary['precision'].apply(lambda x: f"{x:.4f}")
    final_summary['recall'] = final_summary['recall'].apply(lambda x: f"{x:.4f}")
    final_summary = final_summary.sort_values('f1_score', ascending=False)
    
    print(final_summary.to_string(index=False))
    print("="*80)
    
    # ============================================
    # FINAL SUMMARY STATISTICS
    # ============================================
    print("\n" + "="*70)
    print("📊 SUMMARY STATISTICS")
    print("="*70)
    
    # Find best and worst by F1-score
    best_class = max(f1_dict, key=f1_dict.get)
    worst_class = min(f1_dict, key=f1_dict.get)
    
    print(f"  🏆 Best F1-Score:   {best_class:12s} ({f1_dict[best_class]:.4f})")
    print(f"  📉 Worst F1-Score:  {worst_class:12s} ({f1_dict[worst_class]:.4f})")
    
    # By class type
    red_f1 = [f1_dict[c] for c in RED_WINES if c in f1_dict]
    white_f1 = [f1_dict[c] for c in WHITE_WINES if c in f1_dict]
    air_f1 = f1_dict.get('air', 0)
    
    print(f"\n  📈 Average by Type:")
    if air_f1:
        print(f"     Air:        {air_f1:.4f}")
    if red_f1:
        print(f"     Red wines:  {np.mean(red_f1):.4f}")
    if white_f1:
        print(f"     White wines: {np.mean(white_f1):.4f}")
    
    # Overall statistics
    all_f1 = list(f1_dict.values())
    print(f"\n  📊 Overall Statistics:")
    print(f"     Mean F1:     {np.mean(all_f1):.4f}")
    print(f"     Median F1:   {np.median(all_f1):.4f}")
    print(f"     Std Dev:     {np.std(all_f1):.4f}")
    
    # ============================================
    # LIST OF ALL SAVED FILES
    # ============================================
    print("\n" + "="*70)
    print("💾 SAVED FILES")
    print("="*70)
    print(f"  📁 Directory: {OUTPUT_DIR}/")
    print(f"\n  📊 Tables (CSV):")
    print(f"     - table_6class.csv")
    print(f"     - table_wines.csv")
    print(f"     - table_red_wines.csv")
    if len(df_white) > 0 and len(df_white['label'].unique()) >= 2:
        print(f"     - table_white_wines.csv")
    print(f"     - variety_analysis_summary.csv")
    
    print(f"\n  📈 Charts (PNG):")
    print(f"     - precision_6class.png")
    print(f"     - recall_6class.png")
    print(f"     - f1score_6class.png")
    print(f"     - precision_wines.png")
    print(f"     - recall_wines.png")
    print(f"     - f1score_wines.png")
    print(f"     - precision_red_wines.png")
    print(f"     - recall_red_wines.png")
    print(f"     - f1score_red_wines.png")
    if len(df_white) > 0 and len(df_white['label'].unique()) >= 2:
        print(f"     - precision_white_wines.png")
        print(f"     - recall_white_wines.png")
        print(f"     - f1score_white_wines.png")
    
    print("="*70)

if __name__ == "__main__":
    main()
















# """
# Variety Analysis - Per-wine performance metrics
# Analyzes precision, recall, F1-score for each wine variety
# Classes: air, toro, garnacha, monastrel (red), macabeo, novell (white)
# """

# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# from sklearn.model_selection import train_test_split
# from sklearn.neighbors import KNeighborsClassifier
# from sklearn.preprocessing import StandardScaler
# from sklearn.impute import SimpleImputer
# from sklearn.metrics import classification_report, accuracy_score
# import glob
# import os
# import warnings
# warnings.filterwarnings('ignore')

# # ============================================
# # Configuration
# # ============================================
# DATA_DIR = '../csv_data_all_sensors'
# OUTPUT_DIR = 'results/variety_analysis'
# TEST_SIZE = 0.2
# RANDOM_STATE = 42
# K_NEIGHBORS = 17

# # ALL 6 CLASSES
# ALL_CLASSES = ['air', 'toro', 'garnacha', 'monastrel', 'macabeo', 'novell']

# # Wine classes only
# WINE_CLASSES = ['toro', 'garnacha', 'monastrel', 'macabeo', 'novell']

# # Group by type
# RED_WINES = ['toro', 'garnacha', 'monastrel']
# WHITE_WINES = ['macabeo', 'novell']

# os.makedirs(OUTPUT_DIR, exist_ok=True)

# # ============================================
# # Load and pivot data
# # ============================================
# def load_and_pivot_data(data_dir):
#     all_files = glob.glob(os.path.join(data_dir, "*.csv"))
#     if not all_files:
#         print(f"No CSV files found in {data_dir}")
#         return None
    
#     dfs = []
#     for file in all_files:
#         df = pd.read_csv(file)
#         dfs.append(df)
    
#     combined_df = pd.concat(dfs, ignore_index=True)
#     print(f"Loaded {len(combined_df)} total raw samples")
#     print(f"Unique labels: {combined_df['label'].unique()}")
    
#     n_sensors = 8
#     n_samples = len(combined_df) // n_sensors
    
#     pivoted_data = []
#     for i in range(n_samples):
#         start_idx = i * n_sensors
#         end_idx = start_idx + n_sensors
#         sample_rows = combined_df.iloc[start_idx:end_idx]
        
#         row_data = {'label': sample_rows['label'].iloc[0]}
        
#         for _, row in sample_rows.iterrows():
#             sensor_id = int(row['sensor_id'])
#             row_data[f'sensor_{sensor_id}_temperature'] = row['temperature']
#             row_data[f'sensor_{sensor_id}_humidity'] = row['humidity']
#             row_data[f'sensor_{sensor_id}_gas_resistance'] = row['gas_resistance']
        
#         pivoted_data.append(row_data)
    
#     result_df = pd.DataFrame(pivoted_data)
#     print(f"Pivoted to {len(result_df)} samples")
#     print(f"Class distribution:\n{result_df['label'].value_counts()}")
    
#     return result_df

# def get_features(df):
#     return [col for col in df.columns if col.startswith('sensor_')]

# def clean_dataframe(df):
#     """Remove any rows with NaN values and ensure all data is clean"""
#     # Drop rows with any NaN in features
#     feature_cols = [col for col in df.columns if col.startswith('sensor_')]
#     initial_len = len(df)
#     df_clean = df.dropna(subset=feature_cols)
    
#     if len(df_clean) < initial_len:
#         print(f"    Removed {initial_len - len(df_clean)} rows with NaN values")
    
#     return df_clean

# def train_and_evaluate(X, y, model_name=""):
#     """Train and evaluate a model, return y_test and y_pred"""
#     if len(X) == 0:
#         print(f"  ERROR: No data for {model_name}")
#         return None, None
    
#     if len(np.unique(y)) < 2:
#         print(f"  WARNING: Only one class in {model_name}: {np.unique(y)}")
#         return None, None
    
#     try:
#         X_train, X_test, y_train, y_test = train_test_split(
#             X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
#         )
#     except ValueError:
#         X_train, X_test, y_train, y_test = train_test_split(
#             X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE
#         )
    
#     # Impute any remaining NaN
#     imputer = SimpleImputer(strategy='median')
#     X_train = imputer.fit_transform(X_train)
#     X_test = imputer.transform(X_test)
    
#     scaler = StandardScaler()
#     X_train_scaled = scaler.fit_transform(X_train)
#     X_test_scaled = scaler.transform(X_test)
    
#     n_neighbors = min(K_NEIGHBORS, len(X_train))
#     model = KNeighborsClassifier(n_neighbors=n_neighbors)
#     model.fit(X_train_scaled, y_train)
    
#     y_pred = model.predict(X_test_scaled)
    
#     return y_test, y_pred

# def plot_bar_chart(data, title, ylabel, filename, colors=None):
#     """Generic bar chart plotter"""
#     if len(data) == 0:
#         return
    
#     fig, ax = plt.subplots(figsize=(10, 6))
    
#     classes = list(data.keys())
#     values = list(data.values())
    
#     if colors is None:
#         colors = ['steelblue'] * len(classes)
    
#     bars = ax.bar(classes, values, color=colors)
#     ax.set_ylim(0, 1)
#     ax.set_ylabel(ylabel, fontsize=12)
#     ax.set_title(title, fontsize=14, fontweight='bold')
#     ax.axhline(y=0.8, color='green', linestyle='--', alpha=0.5, label='Target (0.8)')
#     ax.legend()
    
#     # Add value labels
#     for bar, val in zip(bars, values):
#         ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
#                 f'{val:.3f}', ha='center', va='bottom', fontsize=9)
    
#     plt.xticks(rotation=45, ha='right')
#     plt.tight_layout()
#     plt.savefig(filename, dpi=150)
#     plt.close()

# def main():
#     print("="*70)
#     print("VARIETY ANALYSIS - Per-Wine Performance (6 classes)")
#     print("="*70)
#     print(f"Classes: {ALL_CLASSES}")
#     print(f"  - Red wines: {RED_WINES}")
#     print(f"  - White wines: {WHITE_WINES}")
#     print("="*70)
    
#     df = load_and_pivot_data(DATA_DIR)
#     if df is None:
#         return
    
#     # Clean the entire dataframe first
#     df = clean_dataframe(df)
#     print(f"\nAfter cleaning: {len(df)} samples")
    
#     features = get_features(df)
    
#     # ============================================
#     # FULL 6-CLASS MODEL
#     # ============================================
#     print("\n" + "="*50)
#     print("FULL 6-CLASS MODEL")
#     print("="*50)
    
#     X_full = df[features]
#     y_full = df['label']
    
#     y_test_full, y_pred_full = train_and_evaluate(X_full, y_full, "Full 6-class")
    
#     if y_test_full is None:
#         print("ERROR: Could not train full model")
#         return
    
#     # Calculate metrics
#     report = classification_report(y_test_full, y_pred_full, output_dict=True)
    
#     # Extract per-class metrics
#     precision_dict = {}
#     recall_dict = {}
#     f1_dict = {}
#     support_dict = {}
    
#     for cls in ALL_CLASSES:
#         if cls in report:
#             precision_dict[cls] = report[cls]['precision']
#             recall_dict[cls] = report[cls]['recall']
#             f1_dict[cls] = report[cls]['f1-score']
#             support_dict[cls] = report[cls]['support']
    
#     print("\nPer-Class Metrics:")
#     print("-" * 50)
#     print(f"{'Class':12s} {'Precision':>10s} {'Recall':>10s} {'F1-Score':>10s} {'Support':>8s}")
#     print("-" * 50)
#     for cls in ALL_CLASSES:
#         if cls in precision_dict:
#             print(f"{cls:12s} {precision_dict[cls]:10.4f} {recall_dict[cls]:10.4f} {f1_dict[cls]:10.4f} {support_dict[cls]:8.0f}")
#     print("-" * 50)
    
#     # Colors for classes
#     colors = []
#     for cls in ALL_CLASSES:
#         if cls == 'air':
#             colors.append('gray')
#         elif cls in RED_WINES:
#             colors.append('darkred')
#         elif cls in WHITE_WINES:
#             colors.append('goldenrod')
#         else:
#             colors.append('steelblue')
    
#     # Plot all metrics
#     plot_bar_chart(precision_dict, 'Precision by Class (6 classes)', 'Precision', 
#                    f'{OUTPUT_DIR}/precision_6class.png', colors)
#     plot_bar_chart(recall_dict, 'Recall by Class (6 classes)', 'Recall', 
#                    f'{OUTPUT_DIR}/recall_6class.png', colors)
#     plot_bar_chart(f1_dict, 'F1-Score by Class (6 classes)', 'F1-Score', 
#                    f'{OUTPUT_DIR}/f1score_6class.png', colors)
    
#     # ============================================
#     # WINES ONLY (5 classes)
#     # ============================================
#     print("\n" + "="*50)
#     print("WINES ONLY (5 classes)")
#     print("="*50)
    
#     df_wines = df[df['label'].isin(WINE_CLASSES)].copy()
#     df_wines = clean_dataframe(df_wines)
    
#     if len(df_wines) > 0:
#         X_wines = df_wines[features]
#         y_wines = df_wines['label']
        
#         y_test_wines, y_pred_wines = train_and_evaluate(X_wines, y_wines, "Wines only")
        
#         if y_test_wines is not None:
#             report_wines = classification_report(y_test_wines, y_pred_wines, output_dict=True)
            
#             precision_w = {}
#             recall_w = {}
#             f1_w = {}
            
#             for cls in WINE_CLASSES:
#                 if cls in report_wines:
#                     precision_w[cls] = report_wines[cls]['precision']
#                     recall_w[cls] = report_wines[cls]['recall']
#                     f1_w[cls] = report_wines[cls]['f1-score']
            
#             wine_colors = ['darkred' if c in RED_WINES else 'goldenrod' for c in WINE_CLASSES]
            
#             plot_bar_chart(precision_w, 'Precision by Wine (5 classes)', 'Precision',
#                           f'{OUTPUT_DIR}/precision_wines.png', wine_colors)
#             plot_bar_chart(recall_w, 'Recall by Wine (5 classes)', 'Recall',
#                           f'{OUTPUT_DIR}/recall_wines.png', wine_colors)
#             plot_bar_chart(f1_w, 'F1-Score by Wine (5 classes)', 'F1-Score',
#                           f'{OUTPUT_DIR}/f1score_wines.png', wine_colors)
    
#     # ============================================
#     # RED WINES ONLY (3 classes)
#     # ============================================
#     print("\n" + "="*50)
#     print("RED WINES ONLY (3 classes)")
#     print("="*50)
    
#     df_red = df[df['label'].isin(RED_WINES)].copy()
#     df_red = clean_dataframe(df_red)
    
#     if len(df_red) > 0:
#         X_red = df_red[features]
#         y_red = df_red['label']
        
#         y_test_red, y_pred_red = train_and_evaluate(X_red, y_red, "Red wines")
        
#         if y_test_red is not None:
#             acc_red = accuracy_score(y_test_red, y_pred_red)
#             print(f"  Accuracy: {acc_red:.4f} ({acc_red*100:.2f}%)")
            
#             report_red = classification_report(y_test_red, y_pred_red, output_dict=True)
            
#             precision_r = {}
#             recall_r = {}
#             f1_r = {}
            
#             for cls in RED_WINES:
#                 if cls in report_red:
#                     precision_r[cls] = report_red[cls]['precision']
#                     recall_r[cls] = report_red[cls]['recall']
#                     f1_r[cls] = report_red[cls]['f1-score']
            
#             plot_bar_chart(precision_r, 'Precision - Red Wines', 'Precision',
#                           f'{OUTPUT_DIR}/precision_red_wines.png', ['darkred']*3)
#             plot_bar_chart(recall_r, 'Recall - Red Wines', 'Recall',
#                           f'{OUTPUT_DIR}/recall_red_wines.png', ['darkred']*3)
#             plot_bar_chart(f1_r, 'F1-Score - Red Wines', 'F1-Score',
#                           f'{OUTPUT_DIR}/f1score_red_wines.png', ['darkred']*3)
    
#     # ============================================
#     # WHITE WINES ONLY (2 classes)
#     # ============================================
#     print("\n" + "="*50)
#     print("WHITE WINES ONLY (2 classes)")
#     print("="*50)
    
#     df_white = df[df['label'].isin(WHITE_WINES)].copy()
#     df_white = clean_dataframe(df_white)
    
#     if len(df_white) > 0 and len(df_white['label'].unique()) >= 2:
#         X_white = df_white[features]
#         y_white = df_white['label']
        
#         y_test_white, y_pred_white = train_and_evaluate(X_white, y_white, "White wines")
        
#         if y_test_white is not None:
#             acc_white = accuracy_score(y_test_white, y_pred_white)
#             print(f"  Accuracy: {acc_white:.4f} ({acc_white*100:.2f}%)")
            
#             report_white = classification_report(y_test_white, y_pred_white, output_dict=True)
            
#             precision_w = {}
#             recall_w = {}
#             f1_w = {}
            
#             for cls in WHITE_WINES:
#                 if cls in report_white:
#                     precision_w[cls] = report_white[cls]['precision']
#                     recall_w[cls] = report_white[cls]['recall']
#                     f1_w[cls] = report_white[cls]['f1-score']
            
#             plot_bar_chart(precision_w, 'Precision - White Wines', 'Precision',
#                           f'{OUTPUT_DIR}/precision_white_wines.png', ['goldenrod', 'goldenrod'])
#             plot_bar_chart(recall_w, 'Recall - White Wines', 'Recall',
#                           f'{OUTPUT_DIR}/recall_white_wines.png', ['goldenrod', 'goldenrod'])
#             plot_bar_chart(f1_w, 'F1-Score - White Wines', 'F1-Score',
#                           f'{OUTPUT_DIR}/f1score_white_wines.png', ['goldenrod', 'goldenrod'])
#     elif len(df_white) > 0:
#         print(f"  Only one white wine class: {df_white['label'].unique()}")
#         print("  Need both Macabeo and Novell for 2-class analysis")
    
#     # ============================================
#     # SAVE ALL METRICS TO CSV
#     # ============================================
    
#     # Create summary DataFrame
#     summary_data = []
#     for cls in ALL_CLASSES:
#         if cls in precision_dict:
#             summary_data.append({
#                 'class': cls,
#                 'type': 'air' if cls == 'air' else ('red' if cls in RED_WINES else 'white'),
#                 'precision': precision_dict[cls],
#                 'recall': recall_dict[cls],
#                 'f1_score': f1_dict[cls],
#                 'support': support_dict[cls]
#             })
    
#     summary_df = pd.DataFrame(summary_data)
#     summary_df.to_csv(f'{OUTPUT_DIR}/variety_analysis_summary.csv', index=False)
    
#     # ============================================
#     # FINAL SUMMARY
#     # ============================================
#     print("\n" + "="*70)
#     print("SUMMARY - Best and Worst Performing Classes")
#     print("="*70)
    
#     # Find best and worst by F1-score
#     best_class = max(f1_dict, key=f1_dict.get)
#     worst_class = min(f1_dict, key=f1_dict.get)
    
#     print(f"  Best F1-Score:   {best_class:12s} ({f1_dict[best_class]:.4f})")
#     print(f"  Worst F1-Score:  {worst_class:12s} ({f1_dict[worst_class]:.4f})")
    
#     # By class type
#     red_f1 = [f1_dict[c] for c in RED_WINES if c in f1_dict]
#     white_f1 = [f1_dict[c] for c in WHITE_WINES if c in f1_dict]
    
#     if red_f1:
#         print(f"\n  Red wines average F1:  {np.mean(red_f1):.4f}")
#     if white_f1:
#         print(f"  White wines average F1: {np.mean(white_f1):.4f}")
    
#     print(f"\n✅ Results saved to: {OUTPUT_DIR}/")
#     print(f"   - precision_6class.png")
#     print(f"   - recall_6class.png")
#     print(f"   - f1score_6class.png")
#     print(f"   - precision_wines.png")
#     print(f"   - recall_wines.png")
#     print(f"   - f1score_wines.png")
#     print(f"   - precision_red_wines.png")
#     print(f"   - recall_red_wines.png")
#     print(f"   - f1score_red_wines.png")
#     if len(df_white) > 0 and len(df_white['label'].unique()) >= 2:
#         print(f"   - precision_white_wines.png")
#         print(f"   - recall_white_wines.png")
#         print(f"   - f1score_white_wines.png")
#     print(f"   - variety_analysis_summary.csv")

# if __name__ == "__main__":
#     main()