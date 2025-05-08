import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import date
import ta  # Technical analysis indicators

# App Title
st.title("Stock Market Visualizer with Enhanced Analytics")
st.sidebar.title("Options")

# Helper Functions
def fetch_stock_data(ticker, start_date, end_date):
    """Fetch stock data using yfinance."""
    stock = yf.Ticker(ticker)
    return stock.history(start=start_date, end=end_date)

def plot_candlestick(data):
    """Plot a candlestick chart."""
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name="Candlestick"
    ))
    fig.update_layout(title="Candlestick Chart", xaxis_title="Date", yaxis_title="Price", template="plotly_dark")
    st.plotly_chart(fig)

def plot_volume(data):
    """Plot a volume chart."""
    fig = px.bar(data, x=data.index, y='Volume', title="Trading Volume", template="plotly_dark")
    st.plotly_chart(fig)

def plot_daily_returns(data):
    """Plot daily returns."""
    data['Daily Return'] = data['Close'].pct_change() * 100
    fig = px.line(data, x=data.index, y='Daily Return', title="Daily Returns (%)", template="plotly_dark")
    st.plotly_chart(fig)

def plot_cumulative_returns(data):
    """Plot cumulative returns."""
    data['Cumulative Return'] = (1 + data['Close'].pct_change()).cumprod() - 1
    fig = px.line(data, x=data.index, y='Cumulative Return', title="Cumulative Returns", template="plotly_dark")
    st.plotly_chart(fig)

def plot_moving_averages(data, windows):
    """Plot moving averages."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name="Close Price"))
    for window in windows:
        data[f"MA{window}"] = data['Close'].rolling(window=window).mean()
        fig.add_trace(go.Scatter(x=data.index, y=data[f"MA{window}"], mode='lines', name=f"MA {window}"))
    fig.update_layout(title="Moving Averages", xaxis_title="Date", yaxis_title="Price", template="plotly_dark")
    st.plotly_chart(fig)

def plot_correlation_matrix(data):
    """Plot correlation matrix for stock portfolio."""
    corr = data.corr()
    fig = px.imshow(corr, title="Correlation Matrix", template="plotly_dark", text_auto=True, color_continuous_scale='RdBu_r')
    st.plotly_chart(fig)

# Inputs
st.sidebar.header("Stock Selection")
ticker = st.sidebar.text_input("Enter Stock Ticker (e.g., AAPL)", value="AAPL")
start_date = st.sidebar.date_input("Start Date", value=date(2020, 1, 1))
end_date = st.sidebar.date_input("End Date", value=date.today())

data = fetch_stock_data(ticker, start_date, end_date)

# Visualizations
if not data.empty:
    st.subheader(f"Stock Data for {ticker}")
    st.write(data.tail())

    st.subheader("Candlestick Chart")
    plot_candlestick(data)

    st.subheader("Volume Chart")
    plot_volume(data)

    st.subheader("Daily Returns")
    plot_daily_returns(data)

    st.subheader("Cumulative Returns")
    plot_cumulative_returns(data)

    st.sidebar.header("Moving Averages")
    moving_averages = st.sidebar.multiselect("Select Moving Averages (days)", options=[10, 20, 50, 100, 200], default=[20, 50])
    if moving_averages:
        st.subheader("Moving Averages")
        plot_moving_averages(data, moving_averages)

# Portfolio Correlation
st.sidebar.header("Portfolio Analysis")
portfolio_file = st.sidebar.file_uploader("Upload Portfolio (CSV or Excel)")
if portfolio_file:
    portfolio = pd.read_csv(portfolio_file) if portfolio_file.name.endswith("csv") else pd.read_excel(portfolio_file)
    tickers = portfolio['Ticker'].tolist()
    st.subheader("Portfolio Data")
    st.write(portfolio)

    portfolio_data = {t: fetch_stock_data(t, start_date, end_date)['Close'] for t in tickers}
    portfolio_df = pd.DataFrame(portfolio_data)
    st.subheader("Correlation Matrix")
    plot_correlation_matrix(portfolio_df)

# ====================================
# 🔻 NIFTY 200 Gainers / Losers / Trend
# ====================================

st.markdown("---")
st.header("📊 NIFTY 200: Top Gainers, Losers & Upward Trend")

# Sample list of NIFTY 200 tickers (extend as needed)
nifty200_tickers = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS",
    "ITC.NS", "LT.NS", "KOTAKBANK.NS", "SBIN.NS", "AXISBANK.NS",
    "HINDUNILVR.NS", "BHARTIARTL.NS", "BAJFINANCE.NS", "ASIANPAINT.NS",
    "MARUTI.NS", "SUNPHARMA.NS", "ULTRACEMCO.NS", "TITAN.NS", "NESTLEIND.NS",
    "WIPRO.NS", "TECHM.NS", "ADANIENT.NS", "HCLTECH.NS", "NTPC.NS", "POWERGRID.NS"
]

price_changes = {}
upward_trending_stocks = []

for symbol in nifty200_tickers:
    try:
        df = fetch_stock_data(symbol, start_date, end_date)
        if len(df) < 50:
            continue

        df.dropna(inplace=True)

        # Calculate Price Change
        if len(df) >= 2:
            change = (df['Close'].iloc[-1] - df['Close'].iloc[-2]) / df['Close'].iloc[-2] * 100
            price_changes[symbol] = round(change, 2)

        # Technical Indicators for upward trend
        df['RSI'] = ta.momentum.RSIIndicator(df['Close'], window=14).rsi()
        df['MACD'] = ta.trend.MACD(df['Close']).macd_diff()
        df['EMA20'] = ta.trend.EMAIndicator(df['Close'], window=20).ema_indicator()
        bb = ta.volatility.BollingerBands(close=df['Close'], window=20)
        df['BB_upper'] = bb.bollinger_hband()

        latest = df.iloc[-1]
        if (
            latest['MACD'] > 0 and
            latest['RSI'] > 50 and
            latest['Close'] >= latest['BB_upper'] and
            latest['Close'] > latest['EMA20']
        ):
            upward_trending_stocks.append(symbol)

    except Exception as e:
        continue

# Gainers and Losers
sorted_changes = dict(sorted(price_changes.items(), key=lambda item: item[1], reverse=True))
gainers = dict(list(sorted_changes.items())[:5])
losers = dict(list(sorted_changes.items())[-5:])

# Display Gainers and Losers
col1, col2 = st.columns(2)
with col1:
    st.subheader("🚀 Top Gainers (NIFTY 200)")
    st.write(pd.DataFrame(gainers.items(), columns=["Ticker", "Change (%)"]))
with col2:
    st.subheader("📉 Top Losers (NIFTY 200)")
    st.write(pd.DataFrame(losers.items(), columns=["Ticker", "Change (%)"]))

# Upward Trend Dropdown
if upward_trending_stocks:
    selected_stock = st.selectbox("📈 Select an Upward Trending Stock", upward_trending_stocks)
    st.success(f"You selected: {selected_stock}")
else:
    st.info("No stocks currently meet the upward trend conditions.")
