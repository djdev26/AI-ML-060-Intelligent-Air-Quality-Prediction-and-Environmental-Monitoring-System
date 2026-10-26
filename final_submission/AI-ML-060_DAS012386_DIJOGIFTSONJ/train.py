"""
Root Training Script for AI-ML-060:
Intelligent Air Quality Prediction and Environmental Monitoring System
"""

import sys
import time
from pathlib import Path

# Set up project root in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config
from Source_Code.utils import logger
from Source_Code.data_loader import load_raw_dataset, save_cleaned_data_and_summary
from Source_Code.feature_engineering import derive_features
from Source_Code.preprocessing import prepare_features_and_target, split_data
from Source_Code.eda import generate_all_eda_visualizations
from Source_Code.model_training import train_and_cross_validate_models


def run_training_pipeline():
    start_time = time.time()
    print("=" * 70)
    print("AI-ML-060: INTELLIGENT AIR QUALITY PREDICTION SYSTEM - TRAINING PIPELINE")
    print("=" * 70)
    
    # 1. Ingest Raw Dataset
    logger.info("Step 1: Ingesting and validating raw dataset...")
    df_raw, summary = load_raw_dataset(config.RAW_DATA_PATH)
    save_cleaned_data_and_summary(df_raw, summary)
    
    # 2. Feature Engineering
    logger.info("Step 2: Engineering environmental and temporal features...")
    df_eng = derive_features(df_raw)
    
    # 3. Target Construction & Leakage Prevention
    logger.info("Step 3: Isolating features and creating binary target (co_high)...")
    X, y, df_valid = prepare_features_and_target(df_eng)
    
    # 4. Stratified Train-Test Split (80:20)
    logger.info("Step 4: Executing stratified train-test split (80:20)...")
    X_train, X_test, y_train, y_test = split_data(X, y)
    
    # 5. Exploratory Data Analysis Visualizations (10 figures)
    logger.info("Step 5: Generating 10 mandatory EDA visualizations...")
    generate_all_eda_visualizations(df_valid, df_eng.loc[df_valid.index], y, y_train)
    
    # 6. Model Training & 5-Fold Stratified Cross-Validation
    logger.info("Step 6: Training and cross-validating L1 and L2 regularized pipelines...")
    models, cv_results, _ = train_and_cross_validate_models(X_train, y_train)
    
    elapsed = time.time() - start_time
    print("\n" + "=" * 70)
    print(f"TRAINING PIPELINE COMPLETED IN {elapsed:.2f} SECONDS")
    print("=" * 70)
    print(f"Dataset Size: {len(df_valid)} valid samples (Train: {len(X_train)}, Test: {len(X_test)})")
    print(f"Target Class Imbalance: High CO = {(y==1).sum()} ({(y==1).mean()*100:.2f}%), Low CO = {(y==0).sum()}")
    print("-" * 70)
    print("5-FOLD STRATIFIED CROSS-VALIDATION RESULTS (Training Set):")
    cv_a = cv_results["Model_A_L1_LassoStyle"]
    cv_b = cv_results["Model_B_L2_RidgeStyle"]
    print(f"  Model A (L1 / Lasso-style): Accuracy = {cv_a['accuracy']['val_mean']*100:.2f}% ± {cv_a['accuracy']['val_std']*100:.2f}%, F1 = {cv_a['f1_weighted']['val_mean']:.4f}, ROC-AUC = {cv_a['roc_auc']['val_mean']:.4f}")
    print(f"  Model B (L2 / Ridge-style): Accuracy = {cv_b['accuracy']['val_mean']*100:.2f}% ± {cv_b['accuracy']['val_std']*100:.2f}%, F1 = {cv_b['f1_weighted']['val_mean']:.4f}, ROC-AUC = {cv_b['roc_auc']['val_mean']:.4f}")
    print("=" * 70)
    print("Fitted pipelines saved to 'models/' directory.")
    print("Next step: Run 'python evaluate.py' to evaluate on held-out test data.")
    return models, X_train, X_test, y_train, y_test


if __name__ == "__main__":
    run_training_pipeline()
