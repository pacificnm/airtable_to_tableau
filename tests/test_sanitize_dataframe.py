import unittest
import pandas as pd
from src.airtable_to_tableau.libs.sanitize_dataframe import sanitize_dataframe

class TestSanitizeDataFrame(unittest.TestCase):
    def test_mixed_types(self):
        df = pd.DataFrame({
            "col": ["abc", 123, 45.6, {"id": 1}, [1, 2], True, None]
        })
        result = sanitize_dataframe(df)
        self.assertTrue(all(isinstance(v, str) or pd.isna(v) for v in result["col"]))

if __name__ == "__main__":
    unittest.main()
