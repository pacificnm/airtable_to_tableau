import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Ensure output directory exists
output_dir = os.path.join(os.path.dirname(__file__), '..', 'output')
os.makedirs(output_dir, exist_ok=True)

from dotenv import load_dotenv
import pandas as pd
from airtable_to_tableau.libs.fetch_airtable import fetch_airtable
from airtable_to_tableau.libs.export_hyper import export_to_hyper
from airtable_to_tableau.libs.sanitize_dataframe import sanitize_dataframe

# Load environment variables
load_dotenv()

api_key = os.getenv("AIRTABLE_API_KEY")
base_id = os.getenv("SPACE_BASE_ID")
table_name = os.getenv("SPACE_TABLE_NAME")
output_filename = os.getenv("SPACE_OUTPUT", "space.hyper")
output = os.path.join(output_dir, output_filename)

# Fetch data from Airtable
records = fetch_airtable(base_id, table_name, api_key)
df = pd.DataFrame(records)

# sanitize 
df = sanitize_dataframe(df)  # sanitize without forcing all strings

# Export to .hyper
export_to_hyper(df, output_file=output, table_name="Building")
