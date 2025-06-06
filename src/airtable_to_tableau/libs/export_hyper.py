"""
export_hyper.py

Description:
    Exports a sanitized pandas DataFrame to a Tableau .hyper file using the Tableau Hyper API.
    Dynamically infers column data types and creates a schema and table in the Hyper file.

Functions:
    - infer_sqltype(dtype): Infers Tableau SqlType based on pandas dtype.
    - export_to_hyper(df, output_file, table_name): Writes a DataFrame to a .hyper file with the specified schema.

Usage:
    Typically used within the CLI pipeline or automated export tools.

Requires:
    - pandas
    - tableauhyperapi

Author: Jaimie Garner
Date: 2025-06-06
"""
import pandas as pd
from tableauhyperapi import (
    HyperProcess,
    Connection,
    Telemetry,
    TableDefinition,
    SqlType,
    Inserter,
    TableName,
    CreateMode,
    Name,
)


def infer_sqltype(dtype):
    if pd.api.types.is_integer_dtype(dtype):
        return SqlType.big_int()
    elif pd.api.types.is_float_dtype(dtype):
        return SqlType.double()
    elif pd.api.types.is_bool_dtype(dtype):
        return SqlType.bool()
    elif pd.api.types.is_datetime64_any_dtype(dtype):
        return SqlType.timestamp()
    else:
        return SqlType.text()


def export_to_hyper(df, output_file="output.hyper", table_name="Data"):
    # Define schema and table
    schema_name = "Extract"
    table = TableName(schema_name, table_name)

    # Initialize table definition
    table_def = TableDefinition(table_name=table)

    # Add each column using .add_column
    for col_name, dtype in df.dtypes.items():
        table_def.add_column(Name(col_name), infer_sqltype(dtype))

    with HyperProcess(telemetry=Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU) as hyper:
        with Connection(endpoint=hyper.endpoint, database=output_file, create_mode=CreateMode.CREATE_AND_REPLACE) as connection:
            # ✅ Create the "Extract" schema first
            connection.catalog.create_schema(schema_name)

            # Then create the table
            connection.catalog.create_table(table_def)

            with Inserter(connection, table_def) as inserter:
                inserter.add_rows(df.values.tolist())
                inserter.execute()