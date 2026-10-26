"""
Root Evaluation Script for AI-ML-060:
Intelligent Air Quality Prediction and Environmental Monitoring System
"""

import sys
import time
from pathlib import Path
import pandas as pd

# Set up project root in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config
from Source_Code.utils import logger, load_model
from Source_Code.data_loader import load_raw_dataset
from Source_Code.feature_engineering import derive_features
from Source_Code.preprocessing import prepare_features_and_target, split_data
from Source_Code.evaluation import evaluate_all_models


def run_evaluation_pipeline():
    start_time = time.time()
    print("=" * 70)
    print("AI-ML-060: INTELLIGENT AIR QUALITY PREDICTION - EVALUATION PIPELINE")
    print("=" * 70)
    
    # 1. Ingest Data and Prepare Held-out Test Split
    logger.info("Loading dataset and preparing test split...")
    df_raw, _ = load_raw_dataset(config.RAW_DATA_PATH)
    df_eng = derive_features(df_raw)
    X, y, _ = prepare_features_and_target(df_eng)
    _, X_test, _, y_test = split_data(X, y)
    
    # 2. Load Saved Models
    logger.info("Loading fitted pipelines from models/ directory...")
    models = {
        "Model_A_L1": load_model(config.MODELS_DIR / "lasso_classifier.joblib"),
        "Model_B_L2": load_model(config.MODELS_DIR / "ridge_classifier.joblib"),
    }
    
    # Load optional regression baselines if present
    if (config.MODELS_DIR / "lasso_regression.joblib").exists():
        models["Reg_Lasso"] = load_model(config.MODELS_DIR / "lasso_regression.joblib")
    if (config.MODELS_DIR / "ridge_regression.joblib").exists():
        models["Reg_Ridge"] = load_model(config.MODELS_DIR / "ridge_regression.joblib")
        
    # 3. Evaluate Performance
    logger.info("Evaluating models on untouched test set (N = 1,535)...")
    results, best_model_name = evaluate_all_models(models, X_test, y_test)
    
    elapsed = time.time() - start_time
    print("\n" + "=" * 70)
    print(f"EVALUATION COMPLETED IN {elapsed:.2f} SECONDS")
    print("=" * 70)
    print("HELD-OUT TEST SET PERFORMANCE (N = 1,535):")
    df_comp = pd.read_csv(config.METRICS_DIR / "model_comparison.csv")
    print(df_comp.to_string(index=False))
    print("-" * 70)
    print(f"SELECTED BEST MODEL: {best_model_name} (Saved to models/best_model.joblib)")
    print("Evaluation charts saved to 'results/images/' (Figures 11 to 17).")
    print("Metrics and classification reports saved to 'results/metrics/'.")
    print("=" * 70)
    return results, best_model_name


if __name__ == "__main__":
    run_evaluation_pipeline()
