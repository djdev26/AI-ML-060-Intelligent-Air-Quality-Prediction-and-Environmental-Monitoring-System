"""
Pytest unit tests for Data Ingestion and Sanitization (AI-ML-060)
"""

import pytest
import numpy as np
import pandas as pd
from pathlib import Path
import config
from Source_Code.data_loader import detect_delimiter, load_raw_dataset, parse_datetime_series


def test_delimiter_detection():
    """Verify delimiter detection for semicolon-separated file."""
    assert Path(config.RAW_DATA_PATH).exists(), "Raw dataset must exist."
    sep = detect_delimiter(config.RAW_DATA_PATH)
    assert sep == ";", f"Expected semicolon delimiter, got '{sep}'"


def test_load_raw_dataset_and_dimensions():
    """Verify dataset dimensions and error code replacement."""
    df, summary = load_raw_dataset(config.RAW_DATA_PATH)
    
    # Check dimensions
    assert summary["raw_shape"][0] == 9471, "Raw rows must match 9471"
    assert len(df) == 9357, f"Cleaned valid data rows must be 9357, got {len(df)}"
    assert summary["trailing_blank_rows_removed"] == 114, "Must drop exactly 114 blank trailing rows"
    
    # Check -200 error code replacement with NaN
    for col in config.BASE_PREDICTORS:
        assert (df[col] == -200).sum() == 0, f"Error code -200 found in column {col}"
        
    # Check timestamp parsed
    assert "timestamp" in df.columns, "Parsed timestamp column must exist"
    assert df["timestamp"].notnull().sum() == 9357, "All rows must have valid timestamps"
