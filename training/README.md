# README for `training/` Folder

## Training Module - Wine Detector Hierarchical Models

This folder contains scripts for converting BME688 raw data (`.bmerawdata` files) into CSV format and training hierarchical KNN models for wine classification.

---

## 📁 **Folder Structure**

```
training/
├── raw_data/                          # Input: Raw data from SD card
│   ├── air_1.bmerawdata               # Air sample 1
│   ├── air_2.bmerawdata               # Air sample 2
│   ├── r_garnacha_1.bmerawdata        # Red wine - Garnacha
│   ├── r_monastrell_1.bmerawdata      # Red wine - Monastrel
│   ├── r_Toro_1.bmerawdata            # Red wine - Toro (sample 1)
│   ├── r_Toro_2.bmerawdata            # Red wine - Toro (sample 2)
│   ├── w_macabeo_1.bmerawdata         # White wine - Macabeo
│   └── w_novell_1.bmerawdata          # White wine - Novell
│
├── csv_data/                          # Output: Converted CSV files
│   ├── air_1.csv                      # 7,200 samples
│   ├── air_2.csv                      # 4,800 samples
│   ├── r_garnacha_1.csv               # 9,600 samples
│   ├── r_monastrell_1.csv             # 10,000 samples
│   ├── r_Toro_1.csv                   # 8,800 samples
│   ├── r_Toro_2.csv                   # 10,800 samples
│   ├── w_macabeo_1.csv                # 13,160 samples
│   └── w_novell_1.csv                 # 10,000 samples
│
├── models/                            # Output: Trained models (.pkl files)
│   ├── presence_model.pkl             # Level 1: air vs wine
│   ├── presence_scaler.pkl            # Scaler for presence model
│   ├── type_model.pkl                 # Level 2: red vs white
│   ├── type_scaler.pkl                # Scaler for type model
│   ├── red_region_model.pkl           # Level 3a: toro/garnacha/monastrel
│   ├── red_region_scaler.pkl          # Scaler for red region model
│   ├── white_region_model.pkl         # Level 3b: macabeo vs novell
│   └── white_region_scaler.pkl        # Scaler for white region model
│
├── evaluation/                        # Model evaluation outputs (confusion matrices, reports)
│
├── convert_bmerawdata_to_csv.py       # Script to convert .bmerawdata to CSV
├── train_hierarchical_models.py       # Script to train hierarchical KNN models
├── requirements.txt                   # Python dependencies
└── README.md                          # This file
```

---

## 🚀 **Overview**

This folder handles the complete machine learning pipeline for the Wine Detector system:

1. **Data Conversion** – Converts Bosch `.bmerawdata` files (raw sensor logs from the development kit SD card) into CSV format with labeled samples.

2. **Model Training** – Trains four hierarchical KNN classifiers in a cascade architecture:
   - **Level 1 (Presence)** : Distinguishes between `air` and `wine`
   - **Level 2 (Type)** : Distinguishes between `red` and `white` wine
   - **Level 3a (Red Region)** : Distinguishes between `toro`, `garnacha`, and `monastrel` (3 classes)
   - **Level 3b (White Region)** : Distinguishes between `macabeo` and `novell` (2 classes)

3. **Model Export** – Saves the trained models and scalers as `.pkl` files for deployment in the `cloud-api/` backend.

---

## 📝 **File Naming Convention**

The conversion script automatically extracts labels from filenames using the following convention:

| Filename Pattern | Label | Class Type |
|------------------|-------|-------------|
| `air_*.bmerawdata` | `air` | Reference |
| `r_*_*.bmerawdata` | red wine name (`toro`, `garnacha`, `monastrel`) | Red wine |
| `w_*_*.bmerawdata` | white wine name (`macabeo`, `novell`) | White wine |

### Examples:
| Filename | Extracted Label |
|----------|-----------------|
| `air_1.bmerawdata` | `air` |
| `r_toro_1.bmerawdata` | `toro` |
| `r_garnacha_1.bmerawdata` | `garnacha` |
| `r_monastrell_1.bmerawdata` | `monastrel` |
| `w_macabeo_1.bmerawdata` | `macabeo` |
| `w_novell_1.bmerawdata` | `novell` |

---

## 🧠 **Hierarchical Model Architecture**

The classification is performed in a cascade (hierarchical) structure:

```
                    ┌─────────────────────────────────────────┐
                    │         Level 1: Presence              │
                    │      Model: air vs wine                │
                    │      Features: humidity, gas_resistance│
                    └─────────────────────────────────────────┘
                                       │
                    ┌──────────────────┴──────────────────┐
                    ▼                                      ▼
              Sample = AIR                           Sample = WINE
                    │                                      │
                    ▼                                      ▼
           Prediction: "air"                     Level 2: Type
                                                  Model: red vs white
                                                  Features: humidity, gas_resistance
                                                       │
                                    ┌──────────────────┴──────────────────┐
                                    ▼                                      ▼
                              Sample = RED                            Sample = WHITE
                                    │                                      │
                                    ▼                                      ▼
                         Level 3a: Red Region                   Level 3b: White Region
                         Model: toro, garnacha,                  Model: macabeo, novell
                         monastrel (3 classes)                            (2 classes)
                                    │                                      │
                                    ▼                                      ▼
                         Prediction: "toro",                       Prediction: "macabeo"
                         "garnacha", or "monastrel"                 or "novell"
```

### Why Hierarchical?

| Benefit | Explanation |
|---------|-------------|
| **Simplicity** | Each model deals with only 2-3 classes, not 6 |
| **Accuracy** | Specialized models are more accurate than a single 6‑class model |
| **Diagnosability** | If a prediction fails, you know exactly which level caused the error |
| **Extensibility** | Adding a new wine requires retraining only the relevant level |

---

## 🔧 **Prerequisites**

### Python Dependencies

Install required packages:

```bash
pip install -r requirements.txt
```

**`requirements.txt`:**
```
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0
joblib>=1.3.0
matplotlib>=3.7.0
seaborn>=0.12.0
```

---

## 🏃 **Usage**

### Step 1: Place Raw Data Files

Copy all `.bmerawdata` files from the BME688 development kit SD card into the `raw_data/` folder.

### Step 2: Convert Raw Data to CSV

```bash
python convert_bmerawdata_to_csv.py --input_dir raw_data --output_dir csv_data
```

**Arguments:**
| Argument | Default | Description |
|----------|---------|-------------|
| `--input_dir` | `raw_data` | Directory containing `.bmerawdata` files |
| `--output_dir` | `csv_data` | Directory for output CSV files |

**Output:** CSV files with columns: `temperature`, `humidity`, `gas_resistance`, `iaq`, `label`

### Step 3: Train Hierarchical Models

```bash
python train_hierarchical_models.py
```

**Output:** Trained models and scalers saved to `models/` folder:
- `presence_model.pkl` + `presence_scaler.pkl`
- `type_model.pkl` + `type_scaler.pkl`
- `red_region_model.pkl` + `red_region_scaler.pkl`
- `white_region_model.pkl` + `white_region_scaler.pkl`

### Step 4: Deploy Models to API

```bash
cp models/*.pkl ../cloud-api/models/
```

Then restart the Flask API to load the new models.

---

## 📊 **Dataset Statistics**

After pivoting (8 sensors × 3 features each) and discarding incomplete cycles, the final dataset contains **9,668 labelled examples**. The distribution across classes is:

| Class     | Type  | Total samples | Training (80%) | Testing (20%) |
|-----------|-------|---------------|----------------|----------------|
| Air       | Ref.  | 1,500         | 1,200          | 300            |
| Toro      | Red   | 2,450         | 1,960          | 490            |
| Garnacha  | Red   | 1,200         | 960            | 240            |
| Monastrel | Red   | 1,624         | 1,299          | 325            |
| Macabeo   | White | 1,645         | 1,316          | 329            |
| Novell    | White | 1,249         | 999            | 250            |
| **Total** |       | **9,668**     | **7,734**      | **1,934**      |

---

## 📈 **Expected Performance**

Based on training with the dataset above:

| Model | Classes | Accuracy |
|-------|---------|----------|
| **Presence** | air vs wine | 96.5% |
| **Type** | red vs white | 91.3% |
| **Red Region** | toro, garnacha, monastrel | 89.5% |
| **White Region** | macabeo, novell | 100.0% |

**Overall cascade accuracy:** 88.0%  
**Overall flat accuracy (6 classes):** 84.95%

---

## 📚 **Related Folders**

| Folder | Purpose |
|--------|---------|
| `../cloud-api/` | Flask backend that uses these trained models (including white region) |
| `../dashboard/` | Streamlit dashboard for visualization |
| `../firmware/` | ESP32 code that collects sensor data |
| `../iot/` | BSEC2 configuration files (alternative edge AI approach) |

---

## 🔄 **Relationship with `iot/` Folder**

The `iot/` folder contains BSEC2 configuration files (`bsec_selectivity.h`, `bsec_config_*.h`) that are used when running the AI-Studio trained model directly on the sensor (professional Bosch workflow). The `training/` folder, in contrast, is used for the DIY machine learning pipeline where models run in the cloud API.

Both approaches are valid and complementary:
- **`iot/`** → Models run on ESP32 (edge AI)
- **`training/`** → Models run in cloud API (cloud AI)

---

## 🐛 **Troubleshooting**

| Problem | Solution |
|---------|----------|
| `No .bmerawdata files found` | Ensure files are in `raw_data/` and have the correct extension |
| `KeyError: 'rawDataBody'` | File may be corrupted; check with a JSON validator |
| `ImportError: No module named sklearn` | Run `pip install -r requirements.txt` |
| `Models not loading in API` | Verify `.pkl` files were copied to `cloud-api/models/` |
| `White region model missing` | Ensure `w_novell_1.bmerawdata` is present and `train_hierarchical_models.py` runs completely |

---

**Created for the Wine Detector Project**  
*Last updated: April 2026*
