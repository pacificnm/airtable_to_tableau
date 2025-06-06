"""
cli.py

Description:
    Command-line interface for the Airtable to Tableau export tool.

    This script supports two primary commands:
    - `export`: Fetches data from Airtable, processes it according to a JSON config,
                and exports it as a Tableau Hyper file.
    - `read`:   Reads a .hyper file and prints the contents as a preview.

Usage:
    Export Airtable to Hyper:
        airtable-export export --config path/to/config.json --profile your_profile_name

    Read a Hyper file:
        airtable-export read --input output/buildings.hyper --table Building

Requirements:
    - Set AIRTABLE_API_KEY as an environment variable.
    - Ensure config.json is properly structured with a tables or profiles list.

Author: Jaimie Garner
Date: 2025-06-06
"""
import argparse
import os
import sys

from airtable_to_tableau.libs.fetch_airtable import fetch_airtable
from airtable_to_tableau.libs.export_hyper import export_to_hyper
from airtable_to_tableau.libs.read_hyper import read_hyper_to_dataframe
from airtable_to_tableau.libs.config_utils import load_config
from airtable_to_tableau.libs.sanitize_dataframe import sanitize_dataframe
from airtable_to_tableau.libs.flatten_utils import flatten_lists_in_dataframe
from airtable_to_tableau.libs.transform_utils import apply_column_transformations


def main():
    parser = argparse.ArgumentParser(
        description="Export Airtable data to Tableau Hyper format."
    )
    subparsers = parser.add_subparsers(dest="command")

    # 🔁 Export subcommand
    config_parser = subparsers.add_parser("export", help="Export using a JSON config")
    config_parser.add_argument("--config", required=True, help="Path to JSON config file")
    config_parser.add_argument("--profile", default="default", help="Profile name (default: default)")

    # 🔍 Read subcommand
    read_parser = subparsers.add_parser("read", help="Read a .hyper file and display it")
    read_parser.add_argument("--input", required=True, help="Path to the .hyper file")
    read_parser.add_argument("--table", default="Building", help="Table name (default: Building)")

    args = parser.parse_args()

    if args.command == "export":
        config = load_config(args.config, profile_name=args.profile)

        api_key = os.getenv("AIRTABLE_API_KEY")
        if not api_key:
            print("❌ Missing AIRTABLE_API_KEY in environment.")
            sys.exit(1)

        for entry in config.get("tables", []):
            base_id = entry["base_id"]
            table_name = entry["table_name"]
            output_file = entry["output_file"]
            column_config = entry.get("columns", [])
            column_order = entry.get("column_order")

            print(f"\n📥 Fetching from {table_name}...")

            try:
                records = fetch_airtable(base_id, table_name, api_key)
            except Exception as e:
                print(f"❌ Error fetching data from {table_name}: {e}")
                continue

            if not records:
                print(f"⚠️  No records returned for table {table_name}. Skipping.")
                continue

            try:
                df = sanitize_dataframe(flatten_lists_in_dataframe(records))
                df = apply_column_transformations(df, column_config, column_order)
            except Exception as e:
                print(f"❌ Error processing records from {table_name}: {e}")
                continue

            print(f"💾 Writing {len(df)} rows to {output_file}...")
            try:
                export_to_hyper(df, output_file=output_file, table_name=table_name)
            except Exception as e:
                print(f"❌ Failed to export {table_name} to Hyper: {e}")
                continue

        print("\n✅ All exports completed.")

    elif args.command == "read":
        try:
            df = read_hyper_to_dataframe(args.input, args.table)
            if df is None:
                print("❌ Unable to read table. Please check the table name and file path.")
                sys.exit(1)
            print(df.head())
        except Exception as e:
            print(f"❌ Error reading Hyper file: {e}")
            sys.exit(1)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
