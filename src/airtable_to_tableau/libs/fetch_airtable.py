"""
fetch_airtable.py

Description:
    Contains the function to fetch data from Airtable using its REST API.
    Handles pagination and returns the complete list of Airtable records.

Used by:
    - CLI export command
    - Custom batch jobs

Author: Jaimie Garner
Date: 2025-06-06
"""
import requests

def fetch_airtable(base_id, table_name, api_key):
    url = f"https://api.airtable.com/v0/{base_id}/{table_name}"
    headers = { "Authorization": f"Bearer {api_key}" }

    all_records = []
    offset = None

    while True:
        params = {"offset": offset} if offset else {}
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        all_records.extend(data["records"])
        offset = data.get("offset")
        if not offset:
            break

        return [r["fields"] for r in all_records]