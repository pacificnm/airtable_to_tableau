import os
import json

# 📁 Folder paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", ".."))
HYPER_DIR = os.path.join(ROOT_DIR, "output")
CONFIG_DIR = os.path.join(ROOT_DIR, "configs")

def get_table_name_for_file(filename, profile="default"):
    for fname in os.listdir(CONFIG_DIR):
        if not fname.endswith(".json"):
            continue

        config_path = os.path.join(CONFIG_DIR, fname)
        try:
            with open(config_path, "r") as f:
                config = json.load(f)

            # Handle profile-based configsa
            if "profiles" in config:
                config = config.get("profiles", {}).get(profile, {})

            tables = config.get("tables", [])
            for table in tables:
                output_file = os.path.basename(table.get("output_file", ""))
                if output_file == filename:
                    return table.get("table_name", "Building")
        except Exception:
            continue

    return "Building"  # Fallback
