# Stock Financial Dashboard

A Streamlit-based web application for viewing and analyzing stock financial data from Yahoo Finance.

## Features

- **Stock Symbol Search** - Enter any stock ticker to get comprehensive financial data
- **Key Metrics Display** - Current price, market cap, P/E ratio, dividend yield, volume
- **Interactive Charts** - Candlestick price chart with 20-day and 50-day moving averages
- **Volume Visualization** - Color-coded volume bars
- **Customizable Time Periods** - From 1 week to maximum available history
- **Financial Data Table** - 23+ key metrics including EPS, margins, ROE, and more
- **Historical Price Table** - Daily OHLCV data
- **CSV Export** - Download financial metrics and historical data

## Installation

```bash
pip install streamlit yfinance plotly pandas
```

## Usage

```bash
streamlit run app.py --server.port 5000
```

## Dependencies

- streamlit
- yfinance
- plotly
- pandas

## License

MIT
