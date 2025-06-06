"""
flatten_utils.py

Description:
    Utilities to flatten nested values in Airtable records, specifically handling list-type fields.
    Converts lists (e.g. multiple select values or linked records) into comma-separated strings.

Functions:
    - flatten_value(val): Converts list values to comma-separated strings.
    - flatten_lists_in_dataframe(records): Converts a list of dicts to a flattened DataFrame.

Usage:
    Used as part of the Airtable export pipeline to sanitize and prepare data before transformation.

Requires:
    - pandas

Author: Jaimie Garner
Date: 2025-06-06
"""
import pandas as pd

def flatten_value(val):
    if isinstance(val, list):
        return ", ".join(map(str, val))
    return val

def flatten_lists_in_dataframe(records):
    """Convert list of dicts into DataFrame and flatten list fields."""
    df = pd.DataFrame(records)  # 🔁 Convert list to DataFrame
    return df.applymap(flatten_value)
