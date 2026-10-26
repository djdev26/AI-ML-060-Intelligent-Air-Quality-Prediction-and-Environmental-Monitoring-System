"""
Model training and cross-validation module for AI-ML-060:
Intelligent Air Quality Prediction and Environmental Monitoring System
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression, Lasso, Ridge
from sklearn.model_selection import StratifiedKFold, cross_validate, learning_curve

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config
from Source_Code.utils import logger, save_json, save_model
from Source_Code.preprocessing import build_pipeline


def train_and_cross_validate_models(X_train, y_train):
    """
    Train and cross-validate Model A (L1 / Lasso-style) and Model B (L2 / Ridge-style)
    using 5-Fold Stratified Cross-Validation on the training set exclusively.
    
    Parameters
    ----------
    X_train : pd.DataFrame
    y_train : pd.Series
    
    Returns
    -------
    models : dict of fitted imblearn pipelines
    cv_results : dict of 5-fold cross-validation metrics
    learning_curves_data : dict of train vs validation scores across dataset sizes
    """
    cv = StratifiedKFold(n_splits=config.CV_FOLDS, shuffle=True, random_state=config.RANDOM_STATE)
    scoring = {
        "accuracy": "accuracy",
        "precision_weighted": "precision_weighted",
        "recall_weighted": "recall_weighted",
        "f1_weighted": "f1_weighted",
        "roc_auc": "roc_auc",
    }
    
    # Instantiate Base Estimators
    clf_a = LogisticRegression(**config.MODEL_A_PARAMS)
    clf_b = LogisticRegression(**config.MODEL_B_PARAMS)
    
    pipeline_a = build_pipeline(clf_a, random_state=config.RANDOM_STATE)
    pipeline_b = build_pipeline(clf_b, random_state=config.RANDOM_STATE)
    
    logger.info("Running 5-fold stratified cross-validation for Model A (L1 / Lasso-style LogisticRegression)...")
    cv_a = cross_validate(pipeline_a, X_train, y_train, cv=cv, scoring=scoring, return_train_score=True, n_jobs=-1)
    
    logger.info("Running 5-fold stratified cross-validation for Model B (L2 / Ridge-style LogisticRegression)...")
    cv_b = cross_validate(pipeline_b, X_train, y_train, cv=cv, scoring=scoring, return_train_score=True, n_jobs=-1)
    
    def summarize_cv(scores):
        summary = {}
        for metric in ["accuracy", "precision_weighted", "recall_weighted", "f1_weighted", "roc_auc"]:
            val_scores = scores[f"test_{metric}"]
            train_scores = scores[f"train_{metric}"]
            summary[metric] = {
                "val_mean": float(np.mean(val_scores)),
                "val_std": float(np.std(val_scores)),
                "train_mean": float(np.mean(train_scores)),
                "train_std": float(np.std(train_scores)),
                "folds": [float(x) for x in val_scores],
            }
        return summary
    
    cv_results = {
        "Model_A_L1_LassoStyle": summarize_cv(cv_a),
        "Model_B_L2_RidgeStyle": summarize_cv(cv_b),
    }
    
    # Save CV results to JSON
    save_json(cv_results, config.METRICS_DIR / "cross_validation.json")
    
    logger.info(f"Model A 5-Fold CV Accuracy: {cv_results['Model_A_L1_LassoStyle']['accuracy']['val_mean']:.4f} "
                f"± {cv_results['Model_A_L1_LassoStyle']['accuracy']['val_std']:.4f}, "
                f"F1: {cv_results['Model_A_L1_LassoStyle']['f1_weighted']['val_mean']:.4f}, "
                f"ROC-AUC: {cv_results['Model_A_L1_LassoStyle']['roc_auc']['val_mean']:.4f}")
    logger.info(f"Model B 5-Fold CV Accuracy: {cv_results['Model_B_L2_RidgeStyle']['accuracy']['val_mean']:.4f} "
                f"± {cv_results['Model_B_L2_RidgeStyle']['accuracy']['val_std']:.4f}, "
                f"F1: {cv_results['Model_B_L2_RidgeStyle']['f1_weighted']['val_mean']:.4f}, "
                f"ROC-AUC: {cv_results['Model_B_L2_RidgeStyle']['roc_auc']['val_mean']:.4f}")
    
    # Fit full pipelines on complete training set
    logger.info("Fitting final pipelines on the entire 80% training set...")
    pipeline_a.fit(X_train, y_train)
    pipeline_b.fit(X_train, y_train)
    
    # Save trained pipelines
    save_model(pipeline_a, config.MODELS_DIR / "lasso_classifier.joblib")
    save_model(pipeline_b, config.MODELS_DIR / "ridge_classifier.joblib")
    
    # Compute genuine learning curves
    logger.info("Computing learning curves across training dataset fractions...")
    train_sizes = np.linspace(0.2, 1.0, 5)
    train_sizes_abs, train_scores_a, val_scores_a = learning_curve(
        pipeline_a, X_train, y_train, cv=cv, scoring="f1_weighted",
        train_sizes=train_sizes, n_jobs=-1, random_state=config.RANDOM_STATE
    )
    _, train_scores_b, val_scores_b = learning_curve(
        pipeline_b, X_train, y_train, cv=cv, scoring="f1_weighted",
        train_sizes=train_sizes, n_jobs=-1, random_state=config.RANDOM_STATE
    )
    
    learning_curves_data = {
        "train_sizes": [int(s) for s in train_sizes_abs],
        "Model_A": {
            "train_mean": [float(m) for m in np.mean(train_scores_a, axis=1)],
            "train_std": [float(s) for s in np.std(train_scores_a, axis=1)],
            "val_mean": [float(m) for m in np.mean(val_scores_a, axis=1)],
            "val_std": [float(s) for s in np.std(val_scores_a, axis=1)],
        },
        "Model_B": {
            "train_mean": [float(m) for m in np.mean(train_scores_b, axis=1)],
            "train_std": [float(s) for s in np.std(train_scores_b, axis=1)],
            "val_mean": [float(m) for m in np.mean(val_scores_b, axis=1)],
            "val_std": [float(s) for s in np.std(val_scores_b, axis=1)],
        }
    }
    save_json(learning_curves_data, config.METRICS_DIR / "learning_curves.json")
    
    # Optional continuous regression baseline (Lasso alpha=0.01 and Ridge alpha=1.0)
    # Using 0.5 decision threshold on continuous predictions as requested in Section 7
    logger.info("Fitting continuous Lasso(alpha=0.01) and Ridge(alpha=1.0) regression baselines...")
    reg_lasso_pipe = build_pipeline(Lasso(alpha=0.01, random_state=config.RANDOM_STATE), random_state=config.RANDOM_STATE)
    reg_ridge_pipe = build_pipeline(Ridge(alpha=1.0, random_state=config.RANDOM_STATE), random_state=config.RANDOM_STATE)
    reg_lasso_pipe.fit(X_train, y_train)
    reg_ridge_pipe.fit(X_train, y_train)
    save_model(reg_lasso_pipe, config.MODELS_DIR / "lasso_regression.joblib")
    save_model(reg_ridge_pipe, config.MODELS_DIR / "ridge_regression.joblib")
    
    models = {
        "Model_A_L1": pipeline_a,
        "Model_B_L2": pipeline_b,
        "Reg_Lasso": reg_lasso_pipe,
        "Reg_Ridge": reg_ridge_pipe,
    }
    
    return models, cv_results, learning_curves_data


if __name__ == "__main__":
    from Source_Code.data_loader import load_raw_dataset
    from Source_Code.feature_engineering import derive_features
    from Source_Code.preprocessing import prepare_features_and_target, split_data
    
    df_raw, _ = load_raw_dataset()
    df_eng = derive_features(df_raw)
    X, y, _ = prepare_features_and_target(df_eng)
    X_train, X_test, y_train, y_test = split_data(X, y)
    
    models, cv_results, _ = train_and_cross_validate_models(X_train, y_train)
    print("\nTraining & 5-Fold Cross-Validation Completed Successfully.")
