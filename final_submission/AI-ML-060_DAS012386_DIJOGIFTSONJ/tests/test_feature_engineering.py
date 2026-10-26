"""
Pytest unit tests for Feature Engineering and Target Leakage Prevention (AI-ML-060)
"""

import pytest
import numpy as np
import pandas as pd
import config
from Source_Code.feature_engineering import derive_features
from Source_Code.utils import safe_divide


def test_safe_divide():
    """Verify safe division handles zero and epsilon properly."""
    assert safe_divide(10, 2) == 5.0
    res_zero = safe_divide(10, 0, eps=1e-6)
    assert np.isfinite(res_zero)
    assert res_zero > 0
    
    # Series test
    s_num = pd.Series([10.0, 5.0, 0.0])
    s_den = pd.Series([2.0, 0.0, 1.0])
    s_res = safe_divide(s_num, s_den)
    assert np.all(np.isfinite(s_res))


def test_derive_features():
    """Verify engineered features and check that CO(GT) is NOT used."""
    dummy_data = {
        "PT08.S1(CO)": [1360.0, 1200.0],
        "PT08.S3(NOx)": [1056.0, 1100.0],
        "T": [13.6, 20.0],
        "RH": [48.9, 60.0],
        "timestamp": pd.to_datetime(["2004-03-10 18:00:00", "2004-03-11 09:30:00"]),
    }
    df = pd.DataFrame(dummy_data)
    df_eng = derive_features(df)
    
    for f in config.ENGINEERED_FEATURES:
        assert f in df_eng.columns, f"Engineered feature {f} missing."
        assert not df_eng[f].isnull().all(), f"Engineered feature {f} all null."
        
    assert df_eng["hour"].iloc[0] == 18
    assert df_eng["hour"].iloc[1] == 9
