"""
config_utils.py

Description:
    Provides configuration loading utilities for the Airtable to Tableau export tool.
    Supports both legacy and profile-based JSON configurations.

Functions:
    - load_config(path, profile_name=None): Loads and validates the JSON config file.
      Supports profile selection via "profiles" structure or flat "tables" structure.

Raises:
    - ValueError if the configuration file is invalid or the specified profile is missing.

Author: Jaimie Garner
Date: 2025-06-06
"""
import json
import os


def load_config(path, profile_name=None):
    """Load a JSON config file and extract the selected profile if applicable."""
    with open(path, "r") as file:
        config_data = json.load(file)

    if "profiles" in config_data:
        if not profile_name:
            profile_name = "default"
        profiles = config_data["profiles"]
        if profile_name not in profiles:
            raise ValueError(f"❌ Profile '{profile_name}' not found in config.")
        profile = profiles[profile_name]
        tables = profile.get("tables")
        if not tables:
            raise ValueError(f"❌ Profile '{profile_name}' must contain a 'tables' list.")
        return {"tables": tables}

    if "tables" in config_data:
        return config_data

    raise ValueError("❌ Config file must contain either 'tables' or 'profiles'.")


def find_table_name_for_hyper(config_dir, hyper_filename, profile_name="default"):
    """Find the table name from a config file that matches the given hyper filename."""
    config_files = [f for f in os.listdir(config_dir) if f.endswith(".json")]
    for config_file in config_files:
        config_path = os.path.join(config_dir, config_file)
        try:
            config = load_config(config_path, profile_name=profile_name)
            for entry in config.get("tables", []):
                output_file = entry.get("output_file", "")
                if os.path.basename(output_file) == hyper_filename:
                    return entry.get("table_name", "Data")
        except Exception as e:
            print(f"⚠️ Could not process config {config_file}: {e}")
            continue
    return None