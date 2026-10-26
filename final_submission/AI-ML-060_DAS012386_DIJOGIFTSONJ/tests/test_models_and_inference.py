"""
Pytest unit tests for Model Loading, Inference, and Probability Calibration (AI-ML-060)
"""

import pytest
import numpy as np
import pandas as pd
from pathlib import Path
import config
from Source_Code.utils import load_model, load_json


def test_model_files_exist():
    """Verify that fitted models and metric JSON files are saved."""
    assert (config.MODELS_DIR / "lasso_classifier.joblib").exists()
    assert (config.MODELS_DIR / "ridge_classifier.joblib").exists()
    assert (config.MODELS_DIR / "best_model.joblib").exists()
    assert (config.METRICS_DIR / "model_comparison.json").exists()
    assert (config.METRICS_DIR / "cross_validation.json").exists()


def test_model_inference_and_probabilities():
    """Verify that loaded model performs inference and outputs valid probabilities."""
    model = load_model(config.MODELS_DIR / "best_model.joblib")
    
    # Create sample feature vector
    sample_dict = {col: 100.0 for col in config.ALL_PREDICTORS}
    df_sample = pd.DataFrame([sample_dict])
    
    pred = model.predict(df_sample)
    probs = model.predict_proba(df_sample)
    
    assert pred.shape == (1,)
    assert pred[0] in [0, 1]
    assert probs.shape == (1, 2)
    assert 0.0 <= probs[0, 1] <= 1.0
    assert np.isclose(probs[0, 0] + probs[0, 1], 1.0)


def test_accuracy_benchmark_exceeded():
    """Verify that test accuracy achieves or exceeds the 85% requirement."""
    metrics = load_json(config.METRICS_DIR / "model_comparison.json")
    acc_a = metrics["Model_A_L1"]["accuracy"]
    acc_b = metrics["Model_B_L2"]["accuracy"]
    
    assert acc_a >= 0.85, f"Model A accuracy {acc_a:.4f} is below 85% target benchmark"
    assert acc_b >= 0.85, f"Model B accuracy {acc_b:.4f} is below 85% target benchmark"
