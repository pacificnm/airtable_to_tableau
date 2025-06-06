"""
sanitize_dataframe.py

Description:
    Provides functions to clean and normalize Pandas DataFrames prior to export.
    Ensures compatibility with Tableau Hyper file requirements.

Key Features:
    - Converts unsupported types (lists, dicts) to strings.
    - Replaces NaN/nulls with safe defaults.
    - Coerces boolean, float, int types as needed.

Author: Jaimie Garner
Date: 2025-06-06
"""
import pandas as pd
import numpy as np

def sanitize_value(val):
    try:
        if pd.isna(val):
            return None
    except Exception:
        pass

    if isinstance(val, (list, dict)):
        return str(val)

    if isinstance(val, (bool, int, float, np.number)):
        return str(val)

    return val

def sanitize_dataframe(df):
    # Apply the function to each cell using map on each column
    return df.apply(lambda col: col.map(sanitize_value))
