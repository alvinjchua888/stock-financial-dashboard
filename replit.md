# Stock Financial Dashboard

## Overview
A Streamlit-based web application for viewing and analyzing stock financial data from Yahoo Finance. Users can input any stock symbol to view comprehensive financial metrics, interactive price charts, and download data as CSV files.

## Features
- Stock symbol search with real-time data from Yahoo Finance
- Key financial metrics display (price, market cap, P/E ratio, dividend yield, volume)
- Interactive candlestick chart with 20-day and 50-day moving averages
- Volume chart with color-coded bars (green for up days, red for down days)
- Customizable time periods (1 week to max history)
- Financial data table with 23+ metrics
- Historical price data table
- CSV export for both financial metrics and historical data
- Company information panel with sector, industry, and business summary

## Project Structure
```
/
├── app.py                    # Main Streamlit application
├── .streamlit/
│   └── config.toml           # Streamlit server configuration
├── pyproject.toml            # Python dependencies
└── replit.md                 # This file
```

## Dependencies
- streamlit: Web application framework
- yfinance: Yahoo Finance API wrapper
- plotly: Interactive charting library
- pandas: Data manipulation

## Running the Application
```bash
streamlit run app.py --server.port 5000
```

## Recent Changes
- December 14, 2025: Initial MVP release with all core features
