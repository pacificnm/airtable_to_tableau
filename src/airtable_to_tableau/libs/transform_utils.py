"""
transform_utils.py

Description:
    Applies column-level transformations to a pandas DataFrame based on JSON config.
    Supports type casting, renaming, default fallback, regex-based column matching, 
    formatting, and column reordering.

Functions:
    - cast_value(val, dtype, fmt=None, default=None): Casts individual values.
    - apply_column_transformations(df, column_config, column_order=None): Transforms DataFrame.

Usage:
    Called during Airtable export to apply schema rules before writing to Tableau Hyper.

Author: Jaimie Garner
Date: 2025-06-06
"""
import re
import numpy as np
import pandas as pd


def cast_value(val, dtype, fmt=None, default=None):
    if pd.isna(val):
        return default

    try:
        if dtype == "str":
            return str(val)
        if dtype == "float":
            return float(val)
        if dtype == "int":
            return int(val)
        if dtype == "bool":
            return bool(val)
    except Exception:
        return default

    return val


def apply_column_transformations(df, column_config, column_order=None):
    transformed = {}

    for col in column_config:
        source = col["source"]
        rename = col.get("rename", source)
        dtype = col.get("type", "str")
        default = col.get("default", None)
        fmt = col.get("format", None)
        is_regex = col.get("regex", False)

        matched_columns = []

        if is_regex:
            pattern = re.compile(source)
            matched_columns = [c for c in df.columns if pattern.match(c)]
        elif source in df.columns:
            matched_columns = [source]

        if not matched_columns:
            transformed[rename] = default
            continue

        for colname in matched_columns:
            series = df[colname].apply(lambda v: cast_value(v, dtype, fmt, default))

            if fmt:
                try:
                    series = series.apply(lambda v: fmt % v if v is not None else None)
                except Exception:
                    pass

            final_name = rename if rename else colname
            transformed[final_name] = series

    result_df = pd.DataFrame(transformed)

    if column_order:
        ordered_cols = [col for col in column_order if col in result_df.columns]
        other_cols = [col for col in result_df.columns if col not in ordered_cols]
        return result_df[ordered_cols + other_cols]

    return result_df
