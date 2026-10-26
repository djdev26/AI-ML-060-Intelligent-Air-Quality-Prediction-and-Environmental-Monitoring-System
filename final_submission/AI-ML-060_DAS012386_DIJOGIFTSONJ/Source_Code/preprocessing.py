"""
Preprocessing module for AI-ML-060:
Intelligent Air Quality Prediction and Environmental Monitoring System
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from imblearn.pipeline import Pipeline as ImbPipeline
from imblearn.over_sampling import SMOTE

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config
from Source_Code.utils import logger


class IQROutlierClipper(BaseEstimator, TransformerMixin):
    """
    Scikit-Learn compatible transformer that learns IQR bounds strictly from
    the training data and clips outliers in transform().
    
    This preserves realistic high-pollution measurements while preventing
    extreme measurement anomalies from destabilizing linear decision boundaries,
    without dropping test set rows or altering the test distribution.
    """
    def __init__(self, factor=2.5):
        """
        Parameters
        ----------
        factor : float, default=2.5
            IQR multiplier (using 2.5 to avoid clipping genuine high pollution events)
        """
        self.factor = factor
        self.lower_bounds_ = None
        self.upper_bounds_ = None
        self.feature_names_in_ = None

    def fit(self, X, y=None):
        X_df = pd.DataFrame(X)
        self.feature_names_in_ = getattr(X, "columns", None)
        
        q25 = X_df.quantile(0.25)
        q75 = X_df.quantile(0.75)
        iqr = q75 - q25
        
        self.lower_bounds_ = (q25 - self.factor * iqr).values
        self.upper_bounds_ = (q75 + self.factor * iqr).values
        return self

    def transform(self, X):
        X_df = pd.DataFrame(X).copy()
        for idx in range(X_df.shape[1]):
            col_vals = X_df.iloc[:, idx]
            low = self.lower_bounds_[idx]
            high = self.upper_bounds_[idx]
            X_df.iloc[:, idx] = np.clip(col_vals, low, high)
            
        if self.feature_names_in_ is not None:
            X_df.columns = self.feature_names_in_
            return X_df
        return X_df.values


def prepare_features_and_target(df):
    """
    Filter missing target values, construct binary target 'co_high',
    and isolate predictor features (strictly excluding CO(GT)).
    
    Parameters
    ----------
    df : pd.DataFrame
    
    Returns
    -------
    X : pd.DataFrame
    y : pd.Series
    df_valid : pd.DataFrame (cleaned rows with ground-truth target)
    """
    # 1. Drop rows where CO(GT) is missing (sensor error)
    valid_mask = df[config.TARGET_RAW_COLUMN].notnull()
    df_valid = df[valid_mask].copy()
    dropped_target_count = len(df) - len(df_valid)
    logger.info(f"Target preparation: Dropped {dropped_target_count} rows with missing {config.TARGET_RAW_COLUMN}. "
                f"Valid labeled samples: {len(df_valid)}")
    
    # 2. Binary target: 1 if CO(GT) > 4.0 mg/m^3 else 0
    y = (df_valid[config.TARGET_RAW_COLUMN] > config.CO_HIGH_THRESHOLD).astype(int)
    y.name = config.TARGET_COLUMN
    
    pos_count = (y == 1).sum()
    neg_count = (y == 0).sum()
    logger.info(f"Target distribution - High CO (> 4.0 mg/m^3): {pos_count} ({pos_count/len(y)*100:.2f}%), "
                f"Low CO: {neg_count} ({neg_count/len(y)*100:.2f}%)")
    
    # 3. Select predictor features (CO(GT) is excluded!)
    available_predictors = [col for col in config.ALL_PREDICTORS if col in df_valid.columns]
    X = df_valid[available_predictors].copy()
    
    missing_pred = [col for col in config.ALL_PREDICTORS if col not in available_predictors]
    if missing_pred:
        logger.warning(f"Predictor columns not found in dataset: {missing_pred}")
        
    return X, y, df_valid


def split_data(X, y, test_size=config.TEST_SIZE, random_state=config.RANDOM_STATE):
    """
    Perform stratified train-test split strictly before any data-dependent transformations.
    """
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=test_size,
        random_state=random_state,
        stratify=y
    )
    logger.info(f"Data split (stratified {int((1-test_size)*100)}:{int(test_size*100)}): "
                f"Train shape={X_train.shape}, Test shape={X_test.shape}")
    logger.info(f"Train target balance: {np.bincount(y_train)} ({np.mean(y_train)*100:.2f}% positive)")
    logger.info(f"Test target balance: {np.bincount(y_test)} ({np.mean(y_test)*100:.2f}% positive)")
    return X_train, X_test, y_train, y_test


def build_pipeline(classifier, k_neighbors=5, random_state=config.RANDOM_STATE):
    """
    Build an imblearn Pipeline ensuring:
    Imputation (median) -> Outlier Clipping (train-fitted IQR) -> Scaling (StandardScaler)
    -> SMOTE (only applied to training fold) -> Classifier.
    
    Parameters
    ----------
    classifier : scikit-learn estimator
    k_neighbors : int, default=5
    random_state : int, default=42
    
    Returns
    -------
    pipeline : imblearn.pipeline.Pipeline
    """
    smote_step = SMOTE(k_neighbors=k_neighbors, random_state=random_state)
    
    pipeline = ImbPipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("outlier_clipper", IQROutlierClipper(factor=2.5)),
        ("scaler", StandardScaler()),
        ("smote", smote_step),
        ("classifier", classifier),
    ])
    return pipeline


if __name__ == "__main__":
    from Source_Code.data_loader import load_raw_dataset
    from Source_Code.feature_engineering import derive_features
    
    df_raw, _ = load_raw_dataset()
    df_eng = derive_features(df_raw)
    X, y, _ = prepare_features_and_target(df_eng)
    X_train, X_test, y_train, y_test = split_data(X, y)
    print("\nPreprocessing Module Verification Successful.")
    print("X_train columns:", list(X_train.columns))
