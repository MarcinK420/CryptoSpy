
import unittest
from unittest.mock import patch, MagicMock
import requests
import pandas as pd
from crypto_fetcher import get_crypto_prices, process_data, add_percent_change, format_data, week_change_chart, plot_price_comparison, append_to_csv

class TestCryptoFetcher(unittest.TestCase):

    @patch('crypto_fetcher.requests.get')
    def test_get_crypto_prices_success(self, mock_get):
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
    def test_get_crypto_prices_http_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.HTTPError("HTTP Error")
        result = get_crypto_prices()
        self.assertEqual(result['error'], 'HTTP error')

    @patch('crypto_fetcher.requests.get')
    def test_get_crypto_prices_connection_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection Error")
        result = get_crypto_prices()
        self.assertEqual(result['error'], 'Connection error')

    @patch('crypto_fetcher.requests.get')
    def test_get_crypto_prices_timeout_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.Timeout("Timeout Error")
        result = get_crypto_prices()
        self.assertEqual(result['error'], 'Timeout error')

    @patch('crypto_fetcher.requests.get')
    def test_get_crypto_prices_request_exception(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("Request Exception")
        result = get_crypto_prices()
        self.assertEqual(result['error'], 'Request error')

    def test_process_data(self):
        data = {
            'bitcoin': {'usd': 50000, 'pln': 200000},
            'ethereum': {'usd': 4000, 'pln': 16000},
            'ripple': {'usd': 1, 'pln': 4}
        }
        df = process_data(data)
        self.assertEqual(df.loc['bitcoin', 'usd'], 50000)
        self.assertEqual(df.loc['ethereum', 'pln'], 16000)

    def test_add_percent_change(self):
        data = {
            'bitcoin': {'usd': 50000, 'pln': 200000},
            'ethereum': {'usd': 4000, 'pln': 16000},
            'ripple': {'usd': 1, 'pln': 4}
        }
        df = process_data(data)
        df = add_percent_change(df)
        self.assertIn('usd_change', df.columns)
        self.assertIn('pln_change', df.columns)

    def test_format_data(self):
        data = {
            'bitcoin': {'usd': 50000.123, 'pln': 200000.456},
            'ethereum': {'usd': 4000.789, 'pln': 16000.123},
            'ripple': {'usd': 1.456, 'pln': 4.789}
        }
        df = process_data(data)
        df = add_percent_change(df)  # Ensure percent change columns are added
        df = format_data(df)
        self.assertEqual(df.loc['bitcoin', 'usd'], 50000.12)
        self.assertEqual(df.loc['ethereum', 'pln'], 16000.12)

    @patch('crypto_fetcher.plt.show')
    def test_week_change_chart(self, mock_show):
        data = {
            'bitcoin': {'usd': 50000, 'pln': 200000},
            'ethereum': {'usd': 4000, 'pln': 16000},
            'ripple': {'usd': 1, 'pln': 4}
        }
        df = process_data(data)
        df = add_percent_change(df)
        week_change_chart(df)
        mock_show.assert_called_once()

    @patch('crypto_fetcher.plt.show')
    def test_plot_price_comparison(self, mock_show):
        data = {
            'bitcoin': {'usd': 50000, 'pln': 200000},
            'ethereum': {'usd': 4000, 'pln': 16000},
            'ripple': {'usd': 1, 'pln': 4}
        }
        df = process_data(data)
        plot_price_comparison(df)
        mock_show.assert_called_once()

    @patch('crypto_fetcher.os.path.exists')
    @patch('crypto_fetcher.pd.read_csv')
    def test_append_to_existing_csv(self, mock_read_csv, mock_path_exists):
        mock_path_exists.return_value = True
        mock_read_csv.return_value = pd.DataFrame({
            'usd': [50000, 4000, 1],
            'pln': [200000, 16000, 4],
            'usd_change': [0, -96.09, -99.98],
            'pln_change': [0, -96.09, -99.98]
        }, index=['bitcoin', 'ethereum', 'ripple'])
        data = {
            'bitcoin': {'usd': 60000, 'pln': 240000},
            'ethereum': {'usd': 5000, 'pln': 20000},
            'ripple': {'usd': 2, 'pln': 8}
        }
        df = process_data(data)
        append_to_csv(df)
        self.assertEqual(mock_read_csv.call_count, 1)

    @patch('crypto_fetcher.os.path.exists')
    @patch('crypto_fetcher.pd.read_csv')
    def test_append_to_new_csv(self, mock_read_csv, mock_path_exists):
        mock_path_exists.return_value = False
        data = {
            'bitcoin': {'usd': 60000, 'pln': 240000},
            'ethereum': {'usd': 5000, 'pln': 20000},
            'ripple': {'usd': 2, 'pln': 8}
        }
        df = process_data(data)
        append_to_csv(df)
        self.assertEqual(mock_read_csv.call_count, 0)

if __name__ == '__main__':
    unittest.main()