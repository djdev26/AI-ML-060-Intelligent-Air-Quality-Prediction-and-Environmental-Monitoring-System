"""
Configuration file for AI-ML-060:
Intelligent Air Quality Prediction and Environmental Monitoring System
"""

import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_PATH = DATA_DIR / "raw" / "AirQuality.csv"
PROCESSED_DATA_PATH = DATA_DIR / "processed" / "cleaned_air_quality.csv"
MODELS_DIR = BASE_DIR / "models"
RESULTS_DIR = BASE_DIR / "results"
METRICS_DIR = RESULTS_DIR / "metrics"
IMAGES_DIR = RESULTS_DIR / "images"
PREDICTIONS_DIR = RESULTS_DIR / "predictions"
REPORTS_DIR = RESULTS_DIR / "reports"
DOCS_DIR = BASE_DIR / "docs"
REPORT_OUTPUT_DIR = BASE_DIR / "Report"
FINAL_SUBMISSION_DIR = BASE_DIR / "final_submission"

# Create directories if not exist
for path in [
    DATA_DIR / "raw",
    DATA_DIR / "processed",
    MODELS_DIR,
    METRICS_DIR,
    IMAGES_DIR,
    PREDICTIONS_DIR,
    REPORTS_DIR,
    DOCS_DIR,
    REPORT_OUTPUT_DIR,
    FINAL_SUBMISSION_DIR,
]:
    path.mkdir(parents=True, exist_ok=True)

# Random State for Reproducibility
RANDOM_STATE = 42

# Target Definition
# Binary classification: High CO if CO(GT) > 4.0 mg/m^3, else Low CO (0)
TARGET_COLUMN = "co_high"
TARGET_RAW_COLUMN = "CO(GT)"
CO_HIGH_THRESHOLD = 4.0
SENSOR_ERROR_VALUE = -200.0

# Base Predictor Features (Note: CO(GT) is strictly excluded to prevent target leakage!)
BASE_PREDICTORS = [
    "PT08.S1(CO)",       # Tin oxide sensor response (non-target CO sensor)
    "NMHC(GT)",          # Non-methane hydrocarbons concentration
    "C6H6(GT)",          # Benzene concentration in microg/m^3
    "PT08.S2(NMHC)",     # Titania sensor response
    "NOx(GT)",           # Nitrogen oxides concentration
    "PT08.S3(NOx)",      # Tungsten oxide sensor response
    "NO2(GT)",           # Nitrogen dioxide concentration
    "PT08.S4(NO2)",      # Tungsten oxide sensor response
    "PT08.S5(O3)",       # Indium oxide sensor response
    "T",                 # Temperature in Celsius
    "RH",                # Relative Humidity (%)
    "AH",                # Absolute Humidity
]

# Engineered Features
ENGINEERED_FEATURES = [
    "co_nox_ratio",          # PT08.S1(CO) / (PT08.S3(NOx) + eps)
    "temp_humidity_ratio",   # T / (RH + eps)
    "temp_humidity_product", # T * RH
    "hour",                  # Hour of the day (0-23)
    "month",                 # Month (1-12)
    "day_of_week",           # Day of week (0-6)
]

ALL_PREDICTORS = BASE_PREDICTORS + ENGINEERED_FEATURES

# Model Parameters
# Model A: Lasso-style L1 regularized Logistic Regression
# C=100 is an inverse regularization parameter approximation for weak penalty / alpha=0.01
MODEL_A_PARAMS = {
    "penalty": "l1",
    "solver": "liblinear",
    "C": 100.0,
    "max_iter": 2000,
    "random_state": RANDOM_STATE,
}

# Model B: Ridge-style L2 regularized Logistic Regression
# C=1.0 is the standard inverse regularization parameter corresponding to alpha=1.0
MODEL_B_PARAMS = {
    "penalty": "l2",
    "solver": "lbfgs",
    "C": 1.0,
    "max_iter": 2000,
    "random_state": RANDOM_STATE,
}

# Cross-Validation Configuration
CV_FOLDS = 5
TEST_SIZE = 0.20

# Safe division epsilon
EPSILON = 1e-6
