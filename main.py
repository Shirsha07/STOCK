
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import date

st.set_page_config(
    page_title="Stock Market Dashboard",
    page_icon="📈",
    layout="wide"
)

# --- Sidebar Inputs ---
st.sidebar.title("Options")
st.sidebar.header("Stock Selection")
ticker = st.sidebar.text_input("Enter Stock Ticker (e.g., RELIANCE.NS)", value="RELIANCE.NS")
start_date = st.sidebar.date_input("Start Date", value=date(2020, 1, 1))
end_date = st.sidebar.date_input("End Date", value=date.today())

# --- Data Fetching ---
@st.cache_data
def fetch_stock_data(ticker, start_date, end_date):
    try:
        stock = yf.Ticker(ticker)
        return stock.history(start=start_date, end=end_date)
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

data = fetch_stock_data(ticker, start_date, end_date)

# --- Show Stock Data ---
if not data.empty:
    st.title(f"📊 Stock Data for {ticker}")
    st.write(data.tail())

    # Candlestick chart
    fig_candle = go.Figure(data=[go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close']
    )])
    fig_candle.update_layout(title="Candlestick Chart", template="plotly_dark")
    st.plotly_chart(fig_candle, use_container_width=True)

    # Volume chart
    fig_volume = px.bar(data, x=data.index, y='Volume', title="Trading Volume")
    st.plotly_chart(fig_volume, use_container_width=True)

    # Daily returns
    data['Daily Return'] = data['Close'].pct_change() * 100
    fig_returns = px.line(data, x=data.index, y='Daily Return', title="Daily Returns (%)")
    st.plotly_chart(fig_returns, use_container_width=True)
    
    # Download section
    st.subheader("📥 Download Data")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Download Stock Data (CSV)"):
            csv = data.to_csv().encode('utf-8')
            st.download_button(
                label="Click to Download",
                data=csv,
                file_name=f'{ticker}_stock_data.csv',
                mime='text/csv'
            )
    
    with col2:
        if st.button("Download Daily Returns (CSV)"):
            returns_data = pd.DataFrame({
                'Date': data.index,
                'Daily_Returns': data['Daily Return']
            })
            csv = returns_data.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Click to Download",
                data=csv,
                file_name=f'{ticker}_daily_returns.csv',
                mime='text/csv'
            )
else:
    st.error("No data available for the selected stock and date range")

# Top Gainers and Losers Section
st.subheader("📈 Top Gainers & 📉 Top Losers")

def get_top_movers(tickers):
    movers = []
    for ticker in ['RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFCBANK.NS', 'ICICIBANK.NS', 
                  'HINDUNILVR.NS', 'ITC.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'KOTAKBANK.NS']:
        try:
            data = yf.Ticker(ticker).history(period="2d")
            if len(data) >= 2:
                prev_close = data['Close'].iloc[-2]
                last_close = data['Close'].iloc[-1]
                change_pct = ((last_close - prev_close) / prev_close) * 100
                movers.append({
                    'Ticker': ticker,
                    'Previous Close': round(prev_close, 2),
                    'Last Close': round(last_close, 2),
                    '% Change': round(change_pct, 2)
                })
        except:
            continue
    df = pd.DataFrame(movers)
    if not df.empty:
        df = df.sort_values(by='% Change', ascending=False)
        return df.head(5), df.tail(5).sort_values(by='% Change')
    return pd.DataFrame(), pd.DataFrame()

col1, col2 = st.columns(2)

top_gainers, top_losers = get_top_movers([])

with col1:
    st.markdown("### 🔼 Top Gainers")
    if not top_gainers.empty:
        st.dataframe(top_gainers, use_container_width=True)
    else:
        st.info("No data available for top gainers")

with col2:
    st.markdown("### 🔽 Top Losers")
    if not top_losers.empty:
        st.dataframe(top_losers, use_container_width=True)
    else:
        st.info("No data available for top losers")
