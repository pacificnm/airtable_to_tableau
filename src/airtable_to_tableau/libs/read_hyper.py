"""
read_hyper.py

Description:
    Utility to read Tableau Hyper files (.hyper) and return contents as a pandas DataFrame.
    Useful for validating export results or inspecting data in scripts.

Functions:
    - read_hyper_to_dataframe(hyper_file_path, table_name="Building"): Reads and returns Hyper file contents.

Usage:
    Used via CLI or programmatically to inspect exported Hyper tables.

Requires:
    - tableauhyperapi
    - pandas
    - os

Author: Jaimie Garner
Date: 2025-06-06
"""
from tableauhyperapi import HyperProcess, Connection, Telemetry, TableName, HyperException
import pandas as pd
import os

def read_hyper_to_dataframe(hyper_file_path, table_name="Building"):
    if not os.path.exists(hyper_file_path):
        print(f"❌ File not found: {hyper_file_path}")
        return None

    try:
        with HyperProcess(telemetry=Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU) as hyper:
            with Connection(endpoint=hyper.endpoint, database=hyper_file_path) as connection:
                query = f"SELECT * FROM {TableName('Extract', table_name)}"
                result = connection.execute_query(query)
                rows = list(result)
                column_names = [col.name.unescaped for col in result.schema.columns]
                return pd.DataFrame(rows, columns=column_names)
    except HyperException as e:
        print(f"❌ Table not found or query failed: {table_name}")
        print(f"📄 Hyper API error: {e.message}")
        return None

