import os
import requests

def get_airtable_metadata(base_id, table_name):
    api_key = os.getenv("AIRTABLE_API_KEY")
    if not api_key:
        raise ValueError("Missing AIRTABLE_API_KEY environment variable.")

    url = f"https://api.airtable.com/v0/meta/bases/{base_id}/tables"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    response = requests.get(url, headers=headers)
    #print("🔧 Airtable Metadata Response:", response.text) 

    if response.status_code != 200:
        raise Exception(f"Failed to fetch metadata: {response.text}")

    data = response.json()
    for table in data.get("tables", []):
        if table["name"] == table_name:
            return table["fields"]

    raise Exception(f"Table '{table_name}' not found in base '{base_id}'.")