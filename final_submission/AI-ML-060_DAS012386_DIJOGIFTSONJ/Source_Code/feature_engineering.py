"""
Feature engineering module for AI-ML-060:
Intelligent Air Quality Prediction and Environmental Monitoring System
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config
from Source_Code.utils import logger, safe_divide


def derive_features(df_input):
    """
    Derive domain-specific environmental and temporal features:
    1. co_nox_ratio: PT08.S1(CO) / (PT08.S3(NOx) + eps)
       (Uses the non-target CO sensor to avoid target leakage from CO(GT))
    2. temp_humidity_ratio: T / (RH + eps)
    3. temp_humidity_product: T * RH
    4. hour: timestamp hour (0-23)
    5. month: timestamp month (1-12)
    6. day_of_week: timestamp day of week (0-6)
    
    Parameters
    ----------
    df_input : pd.DataFrame
    
    Returns
    -------
    df : pd.DataFrame with engineered features added
    """
    df = df_input.copy()
    
    # 1. Sensor CO to NOx ratio (Safe division with epsilon)
    # Using PT08.S1(CO) and PT08.S3(NOx) ensures zero leakage from target CO(GT)
    if "PT08.S1(CO)" in df.columns and "PT08.S3(NOx)" in df.columns:
        df["co_nox_ratio"] = safe_divide(df["PT08.S1(CO)"], df["PT08.S3(NOx)"], eps=config.EPSILON)
    elif "PT08.S1(CO)" in df.columns and "NOx(GT)" in df.columns:
        df["co_nox_ratio"] = safe_divide(df["PT08.S1(CO)"], df["NOx(GT)"], eps=config.EPSILON)
    else:
        df["co_nox_ratio"] = 0.0
        logger.warning("Neither PT08.S3(NOx) nor NOx(GT) found for co_nox_ratio; filled with 0.0")
        
    # 2. Temperature to Humidity Ratio
    if "T" in df.columns and "RH" in df.columns:
        df["temp_humidity_ratio"] = safe_divide(df["T"], df["RH"], eps=config.EPSILON)
    else:
        df["temp_humidity_ratio"] = 0.0
        logger.warning("T or RH column missing for temp_humidity_ratio; filled with 0.0")
        
    # 3. Temperature Humidity Interaction Product
    if "T" in df.columns and "RH" in df.columns:
        df["temp_humidity_product"] = df["T"] * df["RH"]
    else:
        df["temp_humidity_product"] = 0.0
        logger.warning("T or RH column missing for temp_humidity_product; filled with 0.0")
        
    # 4. Temporal Features
    if "timestamp" in df.columns and pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
        df["hour"] = df["timestamp"].dt.hour.fillna(12).astype(int)
        df["month"] = df["timestamp"].dt.month.fillna(6).astype(int)
        df["day_of_week"] = df["timestamp"].dt.dayofweek.fillna(2).astype(int)
    else:
        # Fallback if separate Date and Time or manual input
        if "hour" not in df.columns:
            df["hour"] = 12
        if "month" not in df.columns:
            df["month"] = 6
        if "day_of_week" not in df.columns:
            df["day_of_week"] = 2
            
    # Sanitize infinities and NaNs resulting from any operations
    for col in config.ENGINEERED_FEATURES:
        if col in df.columns:
            df[col] = df[col].replace([np.inf, -np.inf], np.nan)
            
    return df


if __name__ == "__main__":
    from Source_Code.data_loader import load_raw_dataset
    df_clean, _ = load_raw_dataset()
    df_feat = derive_features(df_clean)
    print("\nFeature Engineering Successful:")
    print("New columns:", [c for c in config.ENGINEERED_FEATURES if c in df_feat.columns])
    print(df_feat[config.ENGINEERED_FEATURES].describe().T[["mean", "std", "min", "max"]])
