import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import requests
from crypto_fetcher import get_crypto_prices, process_data, add_percent_change, format_data, fetch_historical_data, plot_price_history

class TestCryptoFetcher(unittest.TestCase):

    @patch('crypto_fetcher.requests.get')
    def test_fetches_crypto_prices_successfully(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'bitcoin': {'usd': 50000, 'pln': 200000},
            'ethereum': {'usd': 4000, 'pln': 16000},
            'ripple': {'usd': 1, 'pln': 4}
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = get_crypto_prices()
        self.assertIn('bitcoin', result)
        self.assertIn('ethereum', result)
        self.assertIn('ripple', result)

    @patch('crypto_fetcher.requests.get')
    def test_handles_http_error(self, mock_get):
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("HTTP Error")
        mock_get.return_value = mock_response

        result = get_crypto_prices()
        self.assertEqual(result['error'], 'HTTP error')

    def test_processes_data_correctly(self):
        data = {
            'bitcoin': {'usd': 50000, 'pln': 200000},
            'ethereum': {'usd': 4000, 'pln': 16000},
            'ripple': {'usd': 1, 'pln': 4}
        }
        df = process_data(data)
        self.assertEqual(df.loc['bitcoin', 'usd'], 50000)
        self.assertEqual(df.loc['ethereum', 'pln'], 16000)

    def test_adds_percent_change_correctly(self):
        data = {
            'bitcoin': {'usd': 50000, 'pln': 200000},
            'ethereum': {'usd': 4000, 'pln': 16000},
            'ripple': {'usd': 1, 'pln': 4}
        }
        df = process_data(data)
        df = add_percent_change(df)
        self.assertIn('usd_change', df.columns)
        self.assertIn('pln_change', df.columns)

    def test_formats_data_correctly(self):
        data = {
            'bitcoin': {'usd': 50000.1234, 'pln': 200000.5678},
            'ethereum': {'usd': 4000.1234, 'pln': 16000.5678},
            'ripple': {'usd': 1.1234, 'pln': 4.5678}
        }
        df = process_data(data)
        df = add_percent_change(df)  # Ensure percent change columns are added
        df = format_data(df)
        self.assertEqual(df.loc['bitcoin', 'usd'], 50000.12)
        self.assertEqual(df.loc['ethereum', 'pln'], 16000.57)

    @patch('crypto_fetcher.requests.get')
    def test_fetches_historical_data_successfully(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'prices': [
                [1638316800000, 50000],
                [1638403200000, 51000]
            ]
        }
        mock_get.return_value = mock_response

        df = fetch_historical_data('bitcoin', 7)
        self.assertEqual(df.iloc[0]['price'], 50000)
        self.assertEqual(df.iloc[1]['price'], 51000)

    @patch('crypto_fetcher.requests.get')
    def test_handles_historical_data_http_error(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {}  # Simulate missing 'prices' key
        mock_get.return_value = mock_response

        with self.assertRaises(KeyError):
            fetch_historical_data('bitcoin', 7)

if __name__ == '__main__':
    unittest.main()