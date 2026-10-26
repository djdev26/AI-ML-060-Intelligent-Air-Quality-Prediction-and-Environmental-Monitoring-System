"""
Utility functions for AI-ML-060:
Intelligent Air Quality Prediction and Environmental Monitoring System
"""

import os
import json
import logging
import joblib
import numpy as np
import pandas as pd
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("AI-ML-060")


def safe_divide(numerator, denominator, eps=1e-6):
    """
    Perform safe division preventing ZeroDivisionError and NaN / inf outputs.
    
    Parameters
    ----------
    numerator : array-like or float
    denominator : array-like or float
    eps : float
        Small positive constant added to denominator or used when denominator == 0
        
    Returns
    -------
    result : array-like or float
    """
    if isinstance(numerator, (pd.Series, np.ndarray)) or isinstance(denominator, (pd.Series, np.ndarray)):
        denom = np.where(np.abs(denominator) < eps, eps, denominator)
        result = np.divide(numerator, denom)
        result = np.nan_to_num(result, nan=0.0, posinf=1e6, neginf=-1e6)
        return result
    else:
        denom = eps if abs(denominator) < eps else denominator
        res = numerator / denom
        if np.isnan(res) or np.isinf(res):
            return 0.0
        return res


def save_json(data, filepath):
    """Save dictionary to JSON with formatting."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, default=str)
    logger.info(f"Saved JSON metrics to {path}")


def load_json(filepath):
    """Load JSON file."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_model(pipeline, filepath):
    """Save fitted pipeline using joblib."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, path)
    logger.info(f"Saved model pipeline to {path}")


def load_model(filepath):
    """Load fitted pipeline using joblib."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Model file not found: {path}")
    model = joblib.load(path)
    logger.info(f"Loaded model pipeline from {path}")
    return model
