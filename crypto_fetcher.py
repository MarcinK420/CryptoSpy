import requests
import json
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, before_log, after_log

# Configure logging
logger = logging.getLogger('crypto_fetcher')
logger.setLevel(logging.INFO)
handler = logging.FileHandler('crypto_fetcher.log')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

"""
This module provides functionality to fetch cryptocurrency prices from the CoinGecko API.

Functions:
    get_crypto_prices: Fetches the current prices of Bitcoin, Ethereum, and Ripple in USD and PLN.
"""

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(requests.exceptions.RequestException),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.INFO),
    reraise=True
)
def get_crypto_prices():
    """
    Fetches the current prices of Bitcoin, Ethereum, and Ripple in USD and PLN from the CoinGecko API.

    Retries the request up to 3 times with exponential backoff in case of a RequestException.
    Logs each retry attempt and the result of the operation.

    Returns:
        dict: A dictionary containing the prices of the cryptocurrencies in USD and PLN.
              If an error occurs, returns a dictionary with error details.
    """
    url = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin%2Cethereum%2Cripple&vs_currencies=usd%2Cpln'
    try:
        logger.info("Attempting to fetch crypto prices")
        response = requests.get(url, timeout=30)  # Set timeout to 30 seconds
        response.raise_for_status()  # Raise HTTPError for bad responses
        data = response.json()
        logger.info("Successfully fetched cryptocurrency prices")
        return data
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP error occurred: {http_err}")
        return {"error": "HTTP error", "message": str(http_err)}
    except requests.exceptions.ConnectionError as conn_err:
        logger.error(f"Connection error occurred: {conn_err}")
        return {"error": "Connection error", "message": str(conn_err)}
    except requests.exceptions.Timeout as timeout_err:
        logger.error(f"Timeout error occurred: {timeout_err}")
        return {"error": "Timeout error", "message": str(timeout_err)}
    except requests.exceptions.RequestException as req_err:
        logger.error(f"An error occurred: {req_err}")
        return {"error": "Request error", "message": str(req_err)}
    except ValueError as json_err:
        logger.error(f"JSON decode error: {json_err}")
        return {"error": "JSON decode error", "message": str(json_err)}

data = get_crypto_prices()
if data and "error" not in data:
    print(json.dumps(data, indent=4))
else:
    print("Failed to fetch cryptocurrency prices:", data)