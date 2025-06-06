# ✅ Airtable to Tableau Export Tool

Effortlessly export Airtable data to Tableau Hyper format using a configurable CLI interface.

---

## 🔁 Exporting Data
- Export data from multiple Airtable bases and tables.
- Save exports in Tableau Hyper format using the Tableau Hyper API.
- Batch export via profiles with multiple tables.

## 📁 Flexible JSON Configuration
- Define all behavior via a JSON config file.
- Supports multiple named profiles in one config (default, metrics_only, etc.).
- Each profile includes:
  - description
  - One or more tables with:
    - base_id
    - table_name
    - output_file
    - columns list
    - Optional column_order

## 📊 Column-Level Customization
- For each column:
  - `source`: Airtable field name (string or regex if `regex: true` is set)
  - `rename`: New column name in output (optional)
  - `type`: One of: `str`, `int`, `float`, `bool`, `date`, `noop`
  - `format`: Optional string formatting (`"%.2f"`, etc.)
  - `default`: Fallback value if input is missing, blank, or fails conversion

## 🧪 Transformations
- Sanitization of all cell values to ensure Hyper-compatible types.
- Handles:
  - Nulls / NaNs
  - Nested types (lists, dicts → strings)
  - Type coercion (float, bool, int, etc.)
- Regex support to match multiple source columns dynamically.

## 📚 Reading Hyper Files
- CLI command to read a `.hyper` file and preview data:
```bash
airtable-export read --input path/to/file.hyper --table TableName
```

## ⚙️ CLI Interface
- Single command-line tool:
```bash
airtable-export export --config configs/buildings.json --profile default
```
- Profile selector via `--profile`
- Graceful handling of:
  - Missing config/profile
  - Missing environment variables
  - Bad column references
  - Invalid or empty exports

## 💥 Error Handling & Logging
- Descriptive terminal output:
  - ✅ Success messages
  - ⚠️ Warnings for missing fields
  - ❌ Errors with reasons (e.g. invalid type, missing field)
- Continues processing other tables even if one fails.

## 🚀 Extendable Architecture
Folder structure in `libs/`:
- `fetch_airtable.py` – retrieves Airtable records via API
- `sanitize_dataframe.py` – ensures clean dataframe values
- `flatten_utils.py` – flattens nested structures
- `export_hyper.py` – writes to Tableau Hyper
- `transform_utils.py` – applies rename, type, format, default logic
- `read_hyper.py` – loads Hyper back into a DataFrame
- `config_utils.py` – loads and validates config/profile

## 🏁 Getting Started
1. Install requirements:
```bash
pip install -r requirements.txt
```

2. Set your Airtable API key:
```bash
export AIRTABLE_API_KEY=your_airtable_api_key
```

## 🚀 Usage
Export Airtable to Hyper:
```bash
airtable-export export --config path/to/config.json --profile your_profile_name
```

Read a Hyper file:
```bash
airtable-export read --input output/buildings.hyper --table Building
```

## 🛠️ Config File Format (JSON)
Supports multiple profiles for different table setups:
```json
{
  "profiles": {
    "default": {
      "description": "Default export profile",
      "tables": [
        {
          "base_id": "appXXXXXXX",
          "table_name": "Building",
          "output_file": "output/buildings.hyper",
          "column_order": ["Building Name", "Region", "Neighborhood", "Capacity", "CBRE Scope"],
          "columns": [
            {
              "source": "Name",
              "rename": "Building Name",
              "type": "str"
            },
            {
              "source": "^Region.*",
              "type": "str",
              "regex": true
            },
            {
              "source": "Neighborhood",
              "type": "str"
            },
            {
              "source": "Max Capacity",
              "rename": "Capacity",
              "type": "float",
              "format": "%.0f",
              "default": 0
            },
            {
              "source": "CBRE Scope",
              "type": "bool",
              "default": false
            }
          ]
        }
      ]
    }
  }
}
```

## 🧱 Column Configuration Options
Each column entry supports:

| Key     | Required | Description                                                   |
|---------|----------|---------------------------------------------------------------|
| source  | ✅        | Airtable field name (regex allowed with `"regex": true`)     |
| rename  | ❌        | Custom name for the output column                             |
| type    | ❌        | Converts value to: `str`, `int`, `float`, `bool`, `date`, `noop` |
| format  | ❌        | Formatting string (e.g., `"%.2f"`, `"%.0f"`)                  |
| default | ❌        | Value to use when input is null or missing                    |
| regex   | ❌        | Enables regex pattern matching for the source field name      |

## 🔢 Available Column Types
| Type   | Description                                                                 |
|--------|-----------------------------------------------------------------------------|
| str    | Converts the value to a string using `str(value)`                          |
| int    | Converts the value to an integer. Will apply default on failure            |
| float  | Converts the value to a float. Supports optional formatting                |
| bool   | Converts values like `"true"`, `"yes"`, `1` to `True`; else `False`        |
| date   | Parses date-like strings into `datetime` objects using `pandas.to_datetime`|
| noop   | No conversion; preserves original sanitized value                          |

## 💡 Behavior Notes
- Empty or invalid values are replaced with:
  - the `"default"` if provided,
  - or `None` if not.
- Formatting via `"format"` is supported only for:
  - `float`, `str`, `date` (as string)
- Boolean conversion supports common truthy/falsy patterns:
  - `"yes"`, `"true"`, `"1"` → `True`
  - `"no"`, `"false"`, `"0"` → `False`

## 🧰 Advanced Features
- ✔ Profiles with `--profile`
- ✔ Regex column matching with `"regex": true`
- ✔ Column ordering with `column_order`
- ✔ Defaults for missing values
- ✔ Format strings for numeric output

## 🔎 Example Mapping
Airtable Input:
```json
{
  "Name": "Windrunner",
  "Region Text": "Americas",
  "Max Capacity": 150
}
```

Config:
```json
{
  "columns": [
    { "source": "Name", "rename": "Building Name", "type": "str" },
    { "source": "^Region.*", "type": "str", "regex": true },
    { "source": "Max Capacity", "rename": "Capacity", "type": "float", "format": "%.0f" }
  ]
}
```

Output:
| Building Name | Region Text | Capacity |
|---------------|-------------|----------|
| Windrunner    | Americas    | 150      |

## ☁️ What Are Azure Functions?
Azure Functions are serverless compute resources. You define small logic units that run on triggers (timer, HTTP, blob). They're scalable, efficient, and low maintenance.

### Benefits:
- Schedule exports automatically
- No need to manage servers
- Deploy independently per job

## 📤 How Tableau Uses the Output
Generated `.hyper` files can be used by Tableau in three ways:

| Option            | Description                                                            |
|-------------------|------------------------------------------------------------------------|
| File Share Path   | Tableau Server/Bridge watches directory for `.hyper` updates           |
| Azure Blob Storage| Use Tableau Connector or Bridge to sync                                |
| Manual Import     | Analysts import `.hyper` in Tableau Desktop                            |