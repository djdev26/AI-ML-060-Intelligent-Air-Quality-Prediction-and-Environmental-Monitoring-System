# AI-ML-060: Intelligent Air Quality Prediction and Environmental Monitoring System

An end-to-end, leak-free machine learning system and responsive web dashboard designed to predict hazardous carbon monoxide pollution levels (`CO > 4.0 mg/m³`) from low-cost chemical multisensor arrays using regularized linear classifiers, in-fold SMOTE resampling, and training-fitted IQR outlier handling.

---

## 1. Project Overview & Architecture

- **Project Code:** AI-ML-060
- **Domain:** Environmental Data Science, Atmospheric Chemistry & Multisensor Modeling
- **Benchmark Dataset:** UCI Air Quality Dataset (9,357 hourly field recordings from Italian CNR-ISAC station)
- **Target Task:** Binary Risk Classification (`co_high = 1 if CO(GT) > 4.0 mg/m³ else 0`)
- **Strict Leakage Prevention:** The continuous reference analyzer measurement `CO(GT)` is **strictly excluded** from all predictor feature vectors.
- **Empirical Results:**
  - **Model A (L1 Lasso Logistic, C=100.0):** **94.59% Test Accuracy**, **0.9498 Weighted F1**, **94.44% High-CO Recall**, **0.9873 ROC-AUC**
  - **Model B (L2 Ridge Logistic, C=1.0):** **94.20% Test Accuracy**, **0.9466 Weighted F1**, **95.06% High-CO Recall**, **0.9872 ROC-AUC**
  - **Benchmark Status:** Comfortably exceeds the **85.0% performance benchmark**.
  - **5-Fold Cross-Validation Accuracy:** `94.85% ± 0.24%` (verifying zero validation fold leakage).

---

## 2. Directory Structure

```text
AI-ML-060/
├── app.py                     # Flask web application entry point
├── train.py                   # Root model training & cross-validation script
├── evaluate.py                # Root model evaluation & benchmark verification script
├── config.py                  # Central configuration file
├── requirements.txt           # Python dependencies
├── README.md                  # Comprehensive documentation and execution guide
├── conftest.py                # Pytest path configuration
├── Source_Code/               # Modular application source code
│   ├── data_loader.py         # Delimiter sniffing, -200 error replacement, data ingestion
│   ├── preprocessing.py       # Leak-free target preparation, IQR clipper transformer, split
│   ├── feature_engineering.py # Safe ratio features (co_nox, temp_humidity) & cyclic temporal
│   ├── eda.py                 # 10 publication-quality EDA visualizations (300 DPI)
│   ├── model_training.py      # L1/L2 pipelines, in-fold SMOTE, 5-fold CV, learning curves
│   ├── evaluation.py          # Held-out test evaluation, confusion matrices, ROC curves
│   ├── report_generator.py    # Generates TXT, HTML, DOCX, and 35-page PDF reports
│   ├── utils.py               # Safe division with epsilon, model I/O, JSON helpers
│   ├── templates/             # Jinja2 HTML5 responsive UI templates
│   │   ├── base.html          # Base layout with navbar, alerts, disclaimer, and footer
│   │   ├── index.html         # Interactive dashboard with metrics, stats, and plots
│   │   ├── predict.html       # Single-sample inference form with risk probability
│   │   ├── batch.html         # Batch CSV upload, schema validation, and CSV export
│   │   ├── results.html       # Comprehensive results gallery and report downloads
│   │   └── about.html         # Scientific methodology and architecture diagrams
│   └── static/                # Static assets
│       ├── css/style.css      # Professional custom responsive styling
│       └── js/main.js         # Interactive form autofill & loading handlers
├── data/                      # Dataset directories
│   ├── raw/AirQuality.csv     # Raw dataset
│   ├── processed/             # Cleaned preprocessed dataset
│   └── sample_batch_test.csv  # 25-row sample for immediate batch test upload
├── models/                    # Serialized Joblib pipeline models
│   ├── best_model.joblib      # Production deployment pipeline
│   ├── lasso_classifier.joblib# Model A pipeline
│   ├── ridge_classifier.joblib# Model B pipeline
│   ├── lasso_regression.joblib# Continuous baseline
│   └── ridge_regression.joblib# Continuous baseline
├── results/                   # Experimental outputs
│   ├── metrics/               # Evaluation JSON/CSV summaries & classification reports
│   ├── images/                # 17 analytical charts & 8 genuine UI screenshots (300 DPI)
│   ├── predictions/           # Generated batch inference output CSVs
│   └── reports/               # Downloadable plain-text and HTML evaluation reports
├── tests/                     # 16 automated pytest unit tests
│   ├── test_data_loader.py
│   ├── test_feature_engineering.py
│   ├── test_preprocessing_and_pipeline.py
│   ├── test_models_and_inference.py
│   └── test_app_routes.py
├── docs/                      # Architectural diagrams
│   ├── flowchart.png          # End-to-end workflow diagram
│   └── architecture.png       # 4-tier layer architecture diagram
├── Report/                    # Academic evaluation deliverables
│   ├── AI_ML_060_Project_Report.docx # Full editable Word report
│   └── AI_ML_060_Project_Report.pdf  # Full 35-page PDF report (Times New Roman, 12pt)
└── final_submission/          # Packaged submission archive
    └── AI-ML-060_StudentID_YourName.zip
```

---

## 3. Environment Setup & Installation

### Prerequisites
- Python 3.10, 3.11, or compatible (tested on Python 3.13.5 64-bit)
- Windows PowerShell or Linux / macOS Terminal

### Setup Virtual Environment

**Windows PowerShell:**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 4. Execution Workflow

### Step 1: Run Training Pipeline
Ingests raw data, generates 10 EDA visualizations, executes 5-fold stratified cross-validation, fits L1 and L2 pipelines, and saves models to `models/`:
```bash
python train.py
```

### Step 2: Run Evaluation Benchmark
Evaluates fitted pipelines on the untouched 20% test partition (N = 1,535), generates Figures 11–17, and produces metric comparison tables:
```bash
python evaluate.py
```

### Step 3: Launch Web Application
Starts the local Flask web dashboard:
```bash
python app.py
```
Open your web browser and navigate to:
```text
http://127.0.0.1:5000/
```

### Step 4: Run Automated Tests
Executes the complete 16-test unit verification suite:
```bash
python -m pytest -v
```

### Step 5: Regenerate Reports (Optional)
Generates the text, HTML, Word DOCX, and 35-page PDF reports:
```bash
python Source_Code/report_generator.py
```

---

## 5. Batch CSV Upload Format

The batch inference endpoint (`/batch`) accepts CSV files (comma or semicolon delimited). For seamless processing, columns should match the base sensor and meteorological headers:

```csv
PT08.S1(CO),NMHC(GT),C6H6(GT),PT08.S2(NMHC),NOx(GT),PT08.S3(NOx),NO2(GT),PT08.S4(NO2),PT08.S5(O3),T,RH,AH
1360.0,150.0,11.9,1046.0,166.0,1056.0,113.0,1692.0,1268.0,13.6,48.9,0.7578
1292.0,112.0,9.4,955.0,103.0,1174.0,92.0,1559.0,972.0,13.3,47.7,0.7255
```
*Note: A ready-to-use sample batch file is located at `data/sample_batch_test.csv` and can also be downloaded directly from the web interface.*

---

## 6. Key Scientific Findings & Discussion

1. **Target Leakage Strictness:** Excising `CO(GT)` prevents artificial 100% scores. Our 94.59% accuracy reflects genuine generalizable sensor pattern recognition.
2. **In-Fold SMOTE Efficacy:** Restricting SMOTE strictly to training folds eliminated validation leakage while driving high-CO sensitivity from ~52% (unweighted baseline) to **94.44%**.
3. **L1 vs L2 Sparsity:** L1 regularization (Lasso) drove redundant sensor channels to zero, achieving slightly superior parsimony and test accuracy over L2 regularization.

---

## 7. Submission Details

- **Submission Email:** `freeinternships.in@gmail.com`
- **Email Subject:** `AI-ML-060 | Internship ID: AI-ML-060 | Student ID: [YOUR_ID] | Project Submission`
- **Attached Archive:** `final_submission/AI-ML-060_StudentID_YourName.zip`
