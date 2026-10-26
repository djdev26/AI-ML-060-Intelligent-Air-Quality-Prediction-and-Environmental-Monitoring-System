"""
Pytest unit tests for Preprocessing, Leak-Free Target Creation, and Pipeline (AI-ML-060)
"""

import pytest
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
import config
from Source_Code.preprocessing import (
    IQROutlierClipper, prepare_features_and_target, split_data, build_pipeline
)


def test_target_creation_and_leakage_exclusion():
    """Verify binary target definition and ensure CO(GT) is NOT in predictor matrix."""
    dummy_df = pd.DataFrame({
        "CO(GT)": [2.5, 4.5, -200, np.nan, 5.0, 3.8],
        "PT08.S1(CO)": [1000, 1500, 900, 1100, 1600, 1200],
        "T": [10, 15, 20, 25, 30, 35],
    })
    # Replace -200
    dummy_df["CO(GT)"] = dummy_df["CO(GT)"].replace(-200, np.nan)
    
    # Add all predictor columns as dummy
    for col in config.ALL_PREDICTORS:
        if col not in dummy_df.columns:
            dummy_df[col] = 1.0
            
    X, y, df_valid = prepare_features_and_target(dummy_df)
    
    # 4 valid labeled rows
    assert len(y) == 4
    # Check binary target threshold
    assert y.iloc[0] == 0  # 2.5 <= 4.0
    assert y.iloc[1] == 1  # 4.5 > 4.0
    assert y.iloc[2] == 1  # 5.0 > 4.0
    assert y.iloc[3] == 0  # 3.8 <= 4.0
    
    # STRICT LEAKAGE PREVENTION CHECK:
    assert "CO(GT)" not in X.columns, "CRITICAL ERROR: CO(GT) target column leaked into predictors!"
    assert config.TARGET_RAW_COLUMN not in X.columns


def test_iqr_outlier_clipper():
    """Verify IQR clipper fits strictly and clips without changing shape."""
    X_train = np.array([[1.0], [2.0], [3.0], [4.0], [100.0]])
    clipper = IQROutlierClipper(factor=1.5)
    clipper.fit(X_train)
    
    # Transform test array containing extreme outlier
    X_test = np.array([[2.0], [200.0]])
    X_clipped = clipper.transform(X_test)
    assert X_clipped.shape == (2, 1)
    assert X_clipped[1, 0] <= clipper.upper_bounds_[0]


def test_pipeline_construction_and_smote():
    """Verify imblearn pipeline construction with SMOTE inside."""
    clf = LogisticRegression(penalty="l2", C=1.0, max_iter=200, random_state=42)
    pipe = build_pipeline(clf, k_neighbors=2, random_state=42)
    
    assert "imputer" in pipe.named_steps
    assert "outlier_clipper" in pipe.named_steps
    assert "scaler" in pipe.named_steps
    assert "smote" in pipe.named_steps
    assert "classifier" in pipe.named_steps
