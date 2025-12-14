import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Stock Financial Dashboard",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Stock Financial Dashboard")
st.markdown("Enter a stock symbol to view financial data, charts, and download reports.")

# Sidebar for inputs
with st.sidebar:
    st.header("Stock Search")
    symbol = st.text_input("Enter Stock Symbol", value="AAPL", placeholder="e.g., AAPL, GOOGL, MSFT").upper().strip()
    
    st.subheader("Time Period")
    period_options = {
        "1 Week": "5d",
        "1 Month": "1mo",
        "3 Months": "3mo",
        "6 Months": "6mo",
        "1 Year": "1y",
        "2 Years": "2y",
        "5 Years": "5y",
        "Max": "max"
    }
    selected_period = st.selectbox("Select Time Period", list(period_options.keys()), index=4)
    period = period_options[selected_period]
    
    fetch_button = st.button("Fetch Data", type="primary", use_container_width=True)

# Initialize session state
if 'stock_data' not in st.session_state:
    st.session_state.stock_data = None
if 'stock_info' not in st.session_state:
    st.session_state.stock_info = None
if 'symbol' not in st.session_state:
    st.session_state.symbol = None

def format_large_number(num):
    """Format large numbers with K, M, B suffixes"""
    if num is None or pd.isna(num):
        return "N/A"
    if abs(num) >= 1e12:
        return f"${num/1e12:.2f}T"
    elif abs(num) >= 1e9:
        return f"${num/1e9:.2f}B"
    elif abs(num) >= 1e6:
        return f"${num/1e6:.2f}M"
    elif abs(num) >= 1e3:
        return f"${num/1e3:.2f}K"
    else:
        return f"${num:.2f}"

def get_stock_data(symbol, period):
    """Fetch stock data from Yahoo Finance"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)
        info = ticker.info
        return hist, info, None
    except Exception as e:
        return None, None, str(e)

# Fetch data when button is clicked or on initial load
if fetch_button or (st.session_state.stock_data is None and symbol):
    with st.spinner(f"Fetching data for {symbol}..."):
        hist, info, error = get_stock_data(symbol, period)
        if error:
            st.error(f"Error fetching data: {error}")
        elif hist is None or hist.empty:
            st.error(f"No data found for symbol '{symbol}'. Please check the symbol and try again.")
        else:
            st.session_state.stock_data = hist
            st.session_state.stock_info = info
            st.session_state.symbol = symbol

# Display data if available
if st.session_state.stock_data is not None and not st.session_state.stock_data.empty:
    hist = st.session_state.stock_data
    info = st.session_state.stock_info
    current_symbol = st.session_state.symbol
    
    # Company header
    company_name = info.get('longName', current_symbol)
    st.header(f"{company_name} ({current_symbol})")
    
    # Key metrics in columns
    col1, col2, col3, col4, col5 = st.columns(5)
    
    current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
    previous_close = info.get('previousClose', 0)
    price_change = current_price - previous_close if current_price and previous_close else 0
    price_change_pct = (price_change / previous_close * 100) if previous_close else 0
    
    with col1:
        st.metric(
            "Current Price",
            f"${current_price:.2f}" if current_price else "N/A",
            f"{price_change:+.2f} ({price_change_pct:+.2f}%)" if price_change else None,
            delta_color="normal"
        )
    
    with col2:
        market_cap = info.get('marketCap')
        st.metric("Market Cap", format_large_number(market_cap))
    
    with col3:
        pe_ratio = info.get('trailingPE')
        st.metric("P/E Ratio", f"{pe_ratio:.2f}" if pe_ratio else "N/A")
    
    with col4:
        dividend_yield = info.get('dividendYield')
        st.metric("Dividend Yield", f"{dividend_yield*100:.2f}%" if dividend_yield else "N/A")
    
    with col5:
        volume = info.get('volume') or info.get('regularMarketVolume')
        avg_volume = info.get('averageVolume')
        st.metric("Volume", f"{volume:,.0f}" if volume else "N/A")
    
    st.divider()
    
    # Charts section
    st.subheader("📊 Price Chart")
    
    # Create price chart with volume
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        subplot_titles=('Stock Price', 'Volume'),
        row_heights=[0.7, 0.3]
    )
    
    # Candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=hist.index,
            open=hist['Open'],
            high=hist['High'],
            low=hist['Low'],
            close=hist['Close'],
            name='Price'
        ),
        row=1, col=1
    )
    
    # Add moving averages
    if len(hist) >= 20:
        hist['MA20'] = hist['Close'].rolling(window=20).mean()
        fig.add_trace(
            go.Scatter(
                x=hist.index,
                y=hist['MA20'],
                mode='lines',
                name='20-Day MA',
                line=dict(color='orange', width=1)
            ),
            row=1, col=1
        )
    
    if len(hist) >= 50:
        hist['MA50'] = hist['Close'].rolling(window=50).mean()
        fig.add_trace(
            go.Scatter(
                x=hist.index,
                y=hist['MA50'],
                mode='lines',
                name='50-Day MA',
                line=dict(color='blue', width=1)
            ),
            row=1, col=1
        )
    
    # Volume bars
    colors = ['red' if hist['Close'].iloc[i] < hist['Open'].iloc[i] else 'green' 
              for i in range(len(hist))]
    fig.add_trace(
        go.Bar(
            x=hist.index,
            y=hist['Volume'],
            name='Volume',
            marker_color=colors,
            opacity=0.7
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        height=600,
        showlegend=True,
        xaxis_rangeslider_visible=False,
        template='plotly_white'
    )
    
    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="Price ($)", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Financial Data Table
    st.subheader("📋 Key Financial Data")
    
    # Create financial metrics table
    financial_data = {
        "Metric": [
            "Current Price",
            "Previous Close",
            "Open",
            "Day High",
            "Day Low",
            "52 Week High",
            "52 Week Low",
            "Market Cap",
            "P/E Ratio (Trailing)",
            "P/E Ratio (Forward)",
            "PEG Ratio",
            "Price to Book",
            "EPS (TTM)",
            "Dividend Yield",
            "Dividend Rate",
            "Beta",
            "Volume",
            "Avg Volume",
            "Revenue",
            "Profit Margin",
            "Operating Margin",
            "ROE",
            "ROA"
        ],
        "Value": [
            f"${info.get('currentPrice', info.get('regularMarketPrice', 'N/A')):.2f}" if info.get('currentPrice') or info.get('regularMarketPrice') else "N/A",
            f"${info.get('previousClose', 'N/A'):.2f}" if info.get('previousClose') else "N/A",
            f"${info.get('open', info.get('regularMarketOpen', 'N/A')):.2f}" if info.get('open') or info.get('regularMarketOpen') else "N/A",
            f"${info.get('dayHigh', info.get('regularMarketDayHigh', 'N/A')):.2f}" if info.get('dayHigh') or info.get('regularMarketDayHigh') else "N/A",
            f"${info.get('dayLow', info.get('regularMarketDayLow', 'N/A')):.2f}" if info.get('dayLow') or info.get('regularMarketDayLow') else "N/A",
            f"${info.get('fiftyTwoWeekHigh', 'N/A'):.2f}" if info.get('fiftyTwoWeekHigh') else "N/A",
            f"${info.get('fiftyTwoWeekLow', 'N/A'):.2f}" if info.get('fiftyTwoWeekLow') else "N/A",
            format_large_number(info.get('marketCap')),
            f"{info.get('trailingPE', 'N/A'):.2f}" if info.get('trailingPE') else "N/A",
            f"{info.get('forwardPE', 'N/A'):.2f}" if info.get('forwardPE') else "N/A",
            f"{info.get('pegRatio', 'N/A'):.2f}" if info.get('pegRatio') else "N/A",
            f"{info.get('priceToBook', 'N/A'):.2f}" if info.get('priceToBook') else "N/A",
            f"${info.get('trailingEps', 'N/A'):.2f}" if info.get('trailingEps') else "N/A",
            f"{info.get('dividendYield', 0)*100:.2f}%" if info.get('dividendYield') else "N/A",
            f"${info.get('dividendRate', 'N/A'):.2f}" if info.get('dividendRate') else "N/A",
            f"{info.get('beta', 'N/A'):.2f}" if info.get('beta') else "N/A",
            f"{info.get('volume', info.get('regularMarketVolume', 'N/A')):,.0f}" if info.get('volume') or info.get('regularMarketVolume') else "N/A",
            f"{info.get('averageVolume', 'N/A'):,.0f}" if info.get('averageVolume') else "N/A",
            format_large_number(info.get('totalRevenue')),
            f"{info.get('profitMargins', 0)*100:.2f}%" if info.get('profitMargins') else "N/A",
            f"{info.get('operatingMargins', 0)*100:.2f}%" if info.get('operatingMargins') else "N/A",
            f"{info.get('returnOnEquity', 0)*100:.2f}%" if info.get('returnOnEquity') else "N/A",
            f"{info.get('returnOnAssets', 0)*100:.2f}%" if info.get('returnOnAssets') else "N/A"
        ]
    }
    
    financial_df = pd.DataFrame(financial_data)
    st.dataframe(financial_df, use_container_width=True, hide_index=True)
    
    st.divider()
    
    # Historical Data Table
    st.subheader("📅 Historical Price Data")
    
    # Prepare historical data for display and download
    display_hist = hist.copy()
    display_hist = display_hist.reset_index()
    display_hist['Date'] = display_hist['Date'].dt.strftime('%Y-%m-%d')
    
    # Select and rename columns
    display_cols = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
    display_hist = display_hist[display_cols]
    
    # Round numeric columns
    for col in ['Open', 'High', 'Low', 'Close']:
        display_hist[col] = display_hist[col].round(2)
    
    display_hist['Volume'] = display_hist['Volume'].apply(lambda x: f"{x:,.0f}")
    
    # Show data in reverse chronological order
    display_hist = display_hist.iloc[::-1].reset_index(drop=True)
    
    st.dataframe(display_hist, use_container_width=True, hide_index=True, height=400)
    
    # CSV Download
    st.subheader("📥 Download Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Prepare CSV for historical data
        csv_hist = hist.copy()
        csv_hist = csv_hist.reset_index()
        csv_hist['Date'] = csv_hist['Date'].dt.strftime('%Y-%m-%d')
        csv_hist = csv_hist[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
        csv_data = csv_hist.to_csv(index=False)
        
        st.download_button(
            label="Download Historical Data (CSV)",
            data=csv_data,
            file_name=f"{current_symbol}_historical_data.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        # Prepare CSV for financial metrics
        financial_csv = financial_df.to_csv(index=False)
        
        st.download_button(
            label="Download Financial Metrics (CSV)",
            data=financial_csv,
            file_name=f"{current_symbol}_financial_metrics.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    # Company Information
    st.divider()
    st.subheader("ℹ️ Company Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"**Sector:** {info.get('sector', 'N/A')}")
        st.markdown(f"**Industry:** {info.get('industry', 'N/A')}")
        st.markdown(f"**Country:** {info.get('country', 'N/A')}")
        st.markdown(f"**Employees:** {info.get('fullTimeEmployees', 'N/A'):,}" if info.get('fullTimeEmployees') else "**Employees:** N/A")
    
    with col2:
        st.markdown(f"**Exchange:** {info.get('exchange', 'N/A')}")
        st.markdown(f"**Currency:** {info.get('currency', 'N/A')}")
        website = info.get('website', 'N/A')
        if website != 'N/A':
            st.markdown(f"**Website:** [{website}]({website})")
        else:
            st.markdown("**Website:** N/A")
    
    # Business Summary
    if info.get('longBusinessSummary'):
        with st.expander("Business Summary"):
            st.write(info.get('longBusinessSummary'))

else:
    st.info("👆 Enter a stock symbol in the sidebar and click 'Fetch Data' to get started.")
    st.markdown("""
    ### Popular Stock Symbols:
    - **AAPL** - Apple Inc.
    - **GOOGL** - Alphabet Inc.
    - **MSFT** - Microsoft Corporation
    - **AMZN** - Amazon.com Inc.
    - **TSLA** - Tesla Inc.
    - **NVDA** - NVIDIA Corporation
    - **META** - Meta Platforms Inc.
    """)
