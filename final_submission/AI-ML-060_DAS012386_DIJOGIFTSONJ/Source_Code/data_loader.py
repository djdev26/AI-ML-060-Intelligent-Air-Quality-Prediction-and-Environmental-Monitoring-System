"""
Data loading and ingestion module for AI-ML-060:
Intelligent Air Quality Prediction and Environmental Monitoring System
"""

import os
import sys
import re
import csv
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
import pandas as pd
import config
from Source_Code.utils import logger, save_json


def detect_delimiter(file_path):
    """
    Automatically detect whether the file is semicolon-separated or comma-separated.
    
    Parameters
    ----------
    file_path : str or Path
    
    Returns
    -------
    sep : str (';' or ',')
    """
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        sample = "".join([f.readline() for _ in range(15)])
    
    semicolon_count = sample.count(";")
    comma_count = sample.count(",")
    
    if semicolon_count > comma_count:
        return ";"
    elif comma_count > 0:
        return ","
    else:
        # Fallback to csv sniffer
        try:
            dialect = csv.Sniffer().sniff(sample)
            return dialect.delimiter
        except Exception:
            return ";"


def parse_datetime_series(date_series, time_series):
    """
    Parse date and time strings reliably into a single datetime series.
    Date format in UCI dataset: 'DD/MM/YYYY'
    Time format in UCI dataset: 'HH.MM.SS' or 'HH:MM:SS'
    """
    # Standardize time delimiter
    clean_time = time_series.astype(str).str.replace(".", ":", regex=False).str.strip()
    clean_date = date_series.astype(str).str.strip()
    
    combined = clean_date + " " + clean_time
    # Parse with dayfirst=True
    parsed_dt = pd.to_datetime(combined, format="%d/%m/%Y %H:%M:%S", errors="coerce", dayfirst=True)
    
    # Fallback if any failed
    if parsed_dt.isnull().any():
        alt_parsed = pd.to_datetime(combined, errors="coerce", dayfirst=True)
        parsed_dt = parsed_dt.fillna(alt_parsed)
        
    return parsed_dt


def load_raw_dataset(file_path=None):
    """
    Load the raw Air Quality dataset, automatically detecting delimiter,
    stripping whitespace, fixing decimal comma separators, replacing -200 with NaN,
    and handling empty trailing columns/rows.
    
    Parameters
    ----------
    file_path : str or Path, optional
    
    Returns
    -------
    df : pd.DataFrame
    summary : dict
    """
    path = Path(file_path or config.RAW_DATA_PATH)
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found at: {path}. Please place AirQuality.csv in {path.parent}")
    
    sep = detect_delimiter(path)
    logger.info(f"Detected delimiter '{sep}' for {path.name}")
    
    # Read raw CSV
    # If semicolon separated, decimals are typically commas
    decimal = "," if sep == ";" else "."
    df_raw = pd.read_csv(path, sep=sep, decimal=decimal, low_memory=False)
    
    raw_shape = df_raw.shape
    logger.info(f"Raw dataset shape read: {raw_shape}")
    
    # 1. Strip whitespace from column names
    df_raw.columns = [str(c).strip() for c in df_raw.columns]
    
    # 2. Drop trailing un-named or completely empty columns
    unnamed_cols = [c for c in df_raw.columns if c.startswith("Unnamed") or c == ""]
    if unnamed_cols:
        logger.info(f"Dropping empty trailing columns: {unnamed_cols}")
        df_raw = df_raw.drop(columns=unnamed_cols)
        
    # 3. Drop completely empty rows (trailing empty rows in UCI CSV)
    # Investigate dimensions: UCI CSV contains 114 blank rows at the end
    non_empty_mask = df_raw.notnull().any(axis=1) & (df_raw["Date"].notnull() if "Date" in df_raw.columns else True)
    dropped_blank_rows = len(df_raw) - non_empty_mask.sum()
    df_clean = df_raw[non_empty_mask].copy()
    logger.info(f"Dropped {dropped_blank_rows} trailing blank/corrupted rows. Remaining rows: {len(df_clean)}")
    
    # 4. Parse Date and Time
    if "Date" in df_clean.columns and "Time" in df_clean.columns:
        df_clean["timestamp"] = parse_datetime_series(df_clean["Date"], df_clean["Time"])
        logger.info(f"Successfully parsed timestamp. Valid timestamps: {df_clean['timestamp'].notnull().sum()}/{len(df_clean)}")
    
    # 5. Handle decimal strings if any column was read as object instead of numeric
    for col in df_clean.columns:
        if col not in ["Date", "Time", "timestamp"]:
            if df_clean[col].dtype == object:
                # Replace comma with dot and convert to numeric
                cleaned_col = df_clean[col].astype(str).str.replace(",", ".", regex=False).str.strip()
                df_clean[col] = pd.to_numeric(cleaned_col, errors="coerce")
            else:
                df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")
                
    # 6. Replace sensor error value -200 with NaN
    numeric_cols = [c for c in df_clean.columns if c not in ["Date", "Time", "timestamp"]]
    error_counts = {}
    for col in numeric_cols:
        errors = (df_clean[col] == config.SENSOR_ERROR_VALUE).sum()
        error_counts[col] = int(errors)
        df_clean[col] = df_clean[col].replace(config.SENSOR_ERROR_VALUE, np.nan)
        
    logger.info(f"Replaced -200 error values with NaN. Top sensor error counts: "
                f"{sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:5]}")
    
    # Compile preprocessing summary
    missing_counts = df_clean.isnull().sum().to_dict()
    missing_pcts = (df_clean.isnull().mean() * 100).round(2).to_dict()
    
    desc_stats = df_clean[numeric_cols].describe().to_dict()
    
    summary = {
        "raw_shape": list(raw_shape),
        "cleaned_shape": list(df_clean.shape),
        "delimiter_detected": sep,
        "trailing_blank_rows_removed": int(dropped_blank_rows),
        "trailing_empty_cols_removed": unnamed_cols,
        "columns": df_clean.columns.tolist(),
        "dtypes": {k: str(v) for k, v in df_clean.dtypes.items()},
        "sensor_error_minus_200_counts": error_counts,
        "missing_counts": {k: int(v) for k, v in missing_counts.items()},
        "missing_percentages": {k: float(v) for k, v in missing_pcts.items()},
        "descriptive_statistics": desc_stats,
    }
    
    return df_clean, summary


def save_cleaned_data_and_summary(df, summary, output_path=None, summary_path=None):
    """
    Save the cleaned dataset to CSV and summary to JSON.
    """
    out_csv = Path(output_path or config.PROCESSED_DATA_PATH)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_csv, index=False)
    logger.info(f"Cleaned dataset saved to {out_csv}")
    
    out_sum = Path(summary_path or (config.METRICS_DIR / "preprocessing_summary.json"))
    save_json(summary, out_sum)
    logger.info(f"Preprocessing summary saved to {out_sum}")
    return out_csv, out_sum


if __name__ == "__main__":
    df, summary = load_raw_dataset()
    save_cleaned_data_and_summary(df, summary)
    print("\nDataset Loading & Summary Successful:")
    print(f"Raw Shape: {summary['raw_shape']} -> Cleaned Shape: {summary['cleaned_shape']}")
    print(f"Valid CO(GT) count: {df['CO(GT)'].notnull().sum()}")
    print(f"Missing CO(GT) count: {df['CO(GT)'].isnull().sum()}")
