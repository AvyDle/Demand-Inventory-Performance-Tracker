import unittest
import pandas as pd

class TestDataQuality(unittest.TestCase):

    def test_no_missing_values(self):
        df = pd.read_csv('../data/raw/final_orders_perfect_integrity.csv')
        self.assertEqual(df.isna().sum().sum(), 0, "Data contains missing values")

    def test_key_columns_exist(self):
        df = pd.read_csv('../data/raw/final_products_perfect_integrity.csv')
        for col in ['product_id', 'product_name', 'category']:
            self.assertIn(col, df.columns, f"Missing column: {col}")

if __name__ == '__main__':
    unittest.main()
