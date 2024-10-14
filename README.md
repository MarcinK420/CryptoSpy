# CryptoSpy
project to track changes in the cryptocurrency rate, visualizing them


---

# Cryptocurrency Price Fetcher

This project is a Python-based application that fetches real-time cryptocurrency prices (Bitcoin, Ethereum, and Ripple) from the [CoinGecko API](https://www.coingecko.com/en/api) and performs various tasks, such as logging, data processing, chart generation, and saving to a CSV file.

## Features

- Fetches current prices for Bitcoin, Ethereum, and Ripple in both USD and PLN.
- Logs retry attempts with exponential backoff in case of network errors using the `tenacity` library.
- Generates:
  - **Weekly price change chart**: A bar chart showing the percentage change in price.
  - **Price comparison chart**: A line chart comparing the current prices of the cryptocurrencies.
  - **Price history chart**: A line chart showing the price change over the past 7 days.
- Stores historical data in a CSV file with a timestamp.
  
## Requirements

- Python 3.x
- Required libraries (install via `pip`):
  ```bash
  pip install requests pandas matplotlib tenacity
  ```

## Usage

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/crypto-fetcher.git
cd crypto-fetcher
```

### 2. Install Dependencies

  ```bash
  pip install requests pandas matplotlib tenacity
  ```

### 3. Run the Script

You can run the script by executing:

```bash
python crypto_fetcher.py
```

The script will:
- Fetch the current prices of Bitcoin, Ethereum, and Ripple.
- Process and format the fetched data.
- Generate various charts:
  - **Weekly price change chart** (saved in `charts/barchart_YYYYMMDD.png`)
  - **Price comparison chart** (saved in `charts/linechart_YYYYMMDD.png`)
  - **Price history chart** for the past 7 days (saved in `charts/price_history_YYYYMMDD.png`)
- Append the prices to a CSV file (`crypto_prices.csv`) with a timestamp.

### 4. Logging

The application logs all retry attempts and errors to a log file `crypto_fetcher.log`.

### 5. Data Output

- **CSV File**: Each time the script is run, it appends the fetched prices to `crypto_prices.csv` with a timestamp.
- **Charts**: Charts are generated in the `charts/` directory.

## Functions Overview

- **`get_crypto_prices()`**: Fetches the current cryptocurrency prices from CoinGecko.
- **`process_data(data)`**: Converts the fetched data into a pandas DataFrame.
- **`add_percent_change(df)`**: Adds percentage change columns to the DataFrame.
- **`format_data(df)`**: Rounds the data to 2 decimal places.
- **`week_change_chart(df)`**: Creates a bar chart showing the weekly percentage change.
- **`plot_price_comparison(df)`**: Generates a line chart comparing the prices of Bitcoin, Ethereum, and Ripple in USD and PLN.
- **`append_to_csv(df)`**: Appends the fetched data to a CSV file with a timestamp.
- **`fetch_historical_data(crypto_id, days)`**: Fetches historical price data for a cryptocurrency.
- **`plot_price_history(crypto_ids, days)`**: Plots the historical percentage price changes for a given period.

## Example Output

- **Bar Chart**: Displays the weekly price percentage change.
- **Line Chart**: Shows the comparison of cryptocurrency prices in USD and PLN.
- **Historical Chart**: Shows the percentage price change over the last 7 days.


---

