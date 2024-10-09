import unittest
from unittest.mock import patch, Mock
import requests
from crypto_fetcher import get_crypto_prices

class TestCryptoFetcher(unittest.TestCase):

    @patch('crypto_fetcher.requests.get')
    def test_fetch_crypto_prices_success(self, mock_get):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            'bitcoin': {'usd': 50000, 'pln': 200000},
            'ethereum': {'usd': 4000, 'pln': 16000},
            'ripple': {'usd': 1, 'pln': 4}
        }
        mock_get.return_value = mock_response

        data = get_crypto_prices()
        self.assertIsNotNone(data)
        self.assertIn('bitcoin', data)
        self.assertIn('ethereum', data)
        self.assertIn('ripple', data)

    @patch('crypto_fetcher.requests.get')
    def test_fetch_crypto_prices_http_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.HTTPError("HTTP error")
        with self.assertLogs('crypto_fetcher', level='ERROR') as log:
            data = get_crypto_prices()
            self.assertEqual(data, {"error": "HTTP error", "message": "HTTP error"})
            self.assertGreater(len(log.output), 0)
            self.assertIn("HTTP error occurred: HTTP error", log.output[0])

    @patch('crypto_fetcher.requests.get')
    def test_fetch_crypto_prices_connection_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection error")
        with self.assertLogs('crypto_fetcher', level='ERROR') as log:
            data = get_crypto_prices()
            self.assertEqual(data, {"error": "Connection error", "message": "Connection error"})
            self.assertGreater(len(log.output), 0)
            self.assertIn("Connection error occurred: Connection error", log.output[0])

    @patch('crypto_fetcher.requests.get')
    def test_fetch_crypto_prices_timeout_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.Timeout("Timeout error")
        with self.assertLogs('crypto_fetcher', level='ERROR') as log:
            data = get_crypto_prices()
            self.assertEqual(data, {"error": "Timeout error", "message": "Timeout error"})
            self.assertGreater(len(log.output), 0)
            self.assertIn("Timeout error occurred: Timeout error", log.output[0])

    @patch('crypto_fetcher.requests.get')
    def test_fetch_crypto_prices_request_exception(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("Request exception")
        with self.assertLogs('crypto_fetcher', level='ERROR') as log:
            data = get_crypto_prices()
            self.assertEqual(data, {"error": "Request error", "message": "Request exception"})
            self.assertGreater(len(log.output), 0)
            self.assertIn("An error occurred: Request exception", log.output[0])

    @patch('crypto_fetcher.requests.get')
    def test_fetch_crypto_prices_json_error(self, mock_get):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.side_effect = ValueError("JSON decode error")
        mock_get.return_value = mock_response

        with self.assertLogs('crypto_fetcher', level='ERROR') as log:
            data = get_crypto_prices()
            self.assertEqual(data, {"error": "JSON decode error", "message": "JSON decode error"})
            self.assertGreater(len(log.output), 0)
            self.assertIn("JSON decode error: JSON decode error", log.output[0])

if __name__ == '__main__':
    unittest.main()