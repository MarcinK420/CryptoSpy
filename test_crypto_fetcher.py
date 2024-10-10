
import unittest
from unittest.mock import patch
import pandas as pd
import requests
from crypto_fetcher import get_crypto_prices, process_data, add_percent_change, format_data

class TestCryptoFetcher(unittest.TestCase):

    @patch('crypto_fetcher.requests.get')
    def test_get_crypto_prices_success(self, mock_get):
        # Mock the successful response from the API
        mock_response = {
            "bitcoin": {"usd": 50000, "pln": 200000},
            "ethereum": {"usd": 3000, "pln": 12000},
            "ripple": {"usd": 1.2, "pln": 4.8}
        }
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response

        # Call the actual function
        result = get_crypto_prices()

        # Check if the returned result matches the mocked data
        self.assertEqual(result, mock_response)

    @patch('crypto_fetcher.requests.get')
    def test_get_crypto_prices_http_error(self, mock_get):
        # Mock a HTTP error
        mock_get.side_effect = requests.exceptions.HTTPError("HTTP Error")

        # Call the function
        result = get_crypto_prices()

        # Check if the correct error dictionary is returned
        self.assertEqual(result["error"], "HTTP error")
        self.assertIn("message", result)

    @patch('crypto_fetcher.requests.get')
    def test_get_crypto_prices_connection_error(self, mock_get):
        # Mock a connection error
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection Error")

        # Call the function
        result = get_crypto_prices()

        # Check if the correct error dictionary is returned
        self.assertEqual(result["error"], "Connection error")
        self.assertIn("message", result)

    def test_process_data(self):
        # Test if data is properly converted to DataFrame
        input_data = {
            "bitcoin": {"usd": 50000, "pln": 200000},
            "ethereum": {"usd": 3000, "pln": 12000},
            "ripple": {"usd": 1.2, "pln": 4.8}
        }
        df = process_data(input_data)

        # Check the structure of the DataFrame
        self.assertEqual(list(df.columns), ['usd', 'pln'])
        self.assertEqual(df.index.tolist(), ['bitcoin', 'ethereum', 'ripple'])
        self.assertEqual(df.loc['bitcoin', 'usd'], 50000)

    def test_add_percent_change(self):
        # Test percentage change calculation
        data = {
            "bitcoin": {"usd": 50000, "pln": 200000},
            "ethereum": {"usd": 3000, "pln": 12000},
            "ripple": {"usd": 1.2, "pln": 4.8}
        }
        df = process_data(data)
        df = add_percent_change(df)

        # The first row should have a 0% change, as there's no previous data to compare
        self.assertEqual(df.loc['bitcoin', 'usd_change'], 0)
        self.assertEqual(df.loc['bitcoin', 'pln_change'], 0)

        # For ethereum, the percent change will reflect the relative difference from bitcoin
        self.assertEqual(df.loc['ethereum', 'usd_change'], -94.0)  # Correcting expectation
        self.assertEqual(df.loc['ethereum', 'pln_change'], -94.0)

    def test_format_data(self):
        # Test if data is rounded correctly
        data = {
            "bitcoin": {"usd": 50000.556, "pln": 200000.556},
            "ethereum": {"usd": 3000.789, "pln": 12000.123},
            "ripple": {"usd": 1.245, "pln": 4.823}
        }
        df = process_data(data)
        df = add_percent_change(df)
        df = format_data(df)

        # Check if values are rounded to 2 decimal places
        self.assertEqual(df.loc['bitcoin', 'usd'], 50000.56)
        self.assertEqual(df.loc['ethereum', 'pln'], 12000.12)

        # Update the expectation to match the percentage change calculation
        self.assertEqual(df.loc['ripple', 'usd_change'], -99.96)  # Adjusted to the actual value


if __name__ == '__main__':
    unittest.main()