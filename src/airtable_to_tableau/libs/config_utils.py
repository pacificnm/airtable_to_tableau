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

def load_config(path, profile_name=None):
    with open(path, 'r') as file:
        config_data = json.load(file)

    # Profile-based config
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

    # Legacy single-table format
    if "tables" in config_data:
        return config_data

    raise ValueError("❌ Config file must contain either 'tables' or 'profiles'.")
