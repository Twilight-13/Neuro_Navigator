import unittest
from utils import extract_tickers_from_goal, safe_json_parse

class TestUtils(unittest.TestCase):

    def test_extract_tickers(self):
        self.assertEqual(extract_tickers_from_goal("Price of Bitcoin"), ["BTC-USD"])
        self.assertCountEqual(extract_tickers_from_goal("apple and tesla"), ["AAPL", "TSLA"])
        self.assertEqual(extract_tickers_from_goal("No tickers here"), [])
        # Test uppercased potential tickers
        self.assertIn("NVDA", extract_tickers_from_goal("Check NVDA price"))

    def test_safe_json_parse(self):
        # Valid JSON
        self.assertEqual(safe_json_parse('{"a": 1}'), {"a": 1})
        # Dict input
        self.assertEqual(safe_json_parse({"a": 1}), {"a": 1})
        # Markdown block
        self.assertEqual(safe_json_parse('```json\n{"a": 1}\n```'), {"a": 1})
        # Single quotes fix
        self.assertEqual(safe_json_parse("{'a': 1}"), {"a": 1})
        # Trailing comma fix
        self.assertEqual(safe_json_parse('{"a": 1, }'), {"a": 1})

if __name__ == '__main__':
    unittest.main()
