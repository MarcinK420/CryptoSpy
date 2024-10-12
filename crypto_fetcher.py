import requests
import json
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, before_log, after_log
import pandas as pd
import matplotlib.pyplot as plt
import os

# Configure logging
logger = logging.getLogger('crypto_fetcher')
if not logger.hasHandlers():
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler('crypto_fetcher.log')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

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

def process_data(data):
    """
    Converts the fetched cryptocurrency data into a pandas DataFrame.

    Args:
        data (dict): A dictionary containing the prices of the cryptocurrencies.

    Returns:
        pandas.DataFrame: A DataFrame with the cryptocurrency prices.
    """
    df = pd.DataFrame(data).T
    df.columns = ['usd', 'pln']
    return df

def add_percent_change(df):
    """
    Adds percentage change columns to the DataFrame for USD and PLN prices.

    Args:
        df (pandas.DataFrame): A DataFrame with the cryptocurrency prices.

    Returns:
        pandas.DataFrame: The DataFrame with added percentage change columns.
    """
    df['usd_change'] = df['usd'].pct_change()*100
    df['pln_change'] = df['pln'].pct_change()*100
    df = df.fillna(0)
    return df

def format_data(df):
    """
    Rounds the data in the DataFrame to 2 decimal places.

    Args:
        df (pandas.DataFrame): A DataFrame with the cryptocurrency prices and percentage changes.

    Returns:
        pandas.DataFrame: The DataFrame with rounded values.
    """
    df['usd'] = df['usd'].round(2)
    df['pln'] = df['pln'].round(2)
    df['usd_change'] = df['usd_change'].round(2)
    df['pln_change'] = df['pln_change'].round(2)
    return df

def week_change_chart(df):
    """
    Creates a bar chart showing the weekly percentage change of the cryptocurrencies in USD and PLN.

    Args:
        df (pandas.DataFrame): A DataFrame with the cryptocurrency prices and percentage changes.
    """
    df = df[['usd_change']]
    df = df.rename(index={'bitcoin': 'Bitcoin', 'ethereum': 'Ethereum', 'ripple': 'Ripple'})
    df.plot(kind='bar', figsize=(10, 6))
    plt.title('Weekly Price Change (%)')
    plt.ylabel('Change (%)')
    plt.xticks(rotation=0)
    plt.tight_layout()
    os.makedirs('charts', exist_ok=True)  # Ensure the directory exists
    plt.savefig(f'charts/barchart_{pd.Timestamp.now().strftime("%Y%m%d")}.png', bbox_inches='tight')
    plt.show()

def plot_price_comparison(df):
    """
    Creates a line chart showing the prices of the cryptocurrencies in USD and PLN.

    Args:
        df (pandas.DataFrame): A DataFrame with the cryptocurrency prices.
    """
    df[['usd', 'pln']].plot(kind='line', figsize=(10, 6))
    plt.title('Cryptocurrency Prices')
    plt.ylabel('Price')
    plt.xlabel('Cryptocurrency')
    plt.xticks(rotation=45)
    plt.tight_layout()
    os.makedirs('charts', exist_ok=True)  # Ensure the directory exists
    plt.savefig(f'charts/linechart_{pd.Timestamp.now().strftime("%Y%m%d")}.png', bbox_inches='tight')
    plt.show()

def append_to_csv(df, filename='crypto_prices.csv'):
    """
    Appends the DataFrame to an existing CSV file or creates a new one if it doesn't exist.

    Args:
        df (pandas.DataFrame): A DataFrame with the cryptocurrency prices.
        filename (str): The name of the CSV file to append to. Defaults to 'crypto_prices.csv'.
    """
    if os.path.exists(filename):
        df_old = pd.read_csv(filename)
        df = pd.concat([df_old, df], ignore_index=True)
    df.to_csv(filename, index=False)

# Fetch, process, and save cryptocurrency prices
data = get_crypto_prices()
if data and "error" not in data:
    df = process_data(data)
    df = add_percent_change(df)
    df = format_data(df)
    df.to_csv('crypto_prices.csv', index=False)
    print(df)
    append_to_csv(df)
    week_change_chart(df)
    plot_price_comparison(df)
else:
    print("Failed to fetch cryptocurrency prices:", data)