import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import date

@st.cache_data
def get_nifty_200_tickers():
    df = pd.read_csv("dashboard/nifty_200_tickers.csv")  # Must be in same folder
    return df

# --- Page Config and Styling ---
st.set_page_config(
    page_title="Interactive Stock Market Dashboard",
    page_icon="📈",
    layout="wide"
)

st.markdown("""
    <style>
    .main > div {
        padding-top: 2rem;
    }
    [alt="Logo"] {
        height: 60px;
        margin-right: 10px;
    }
    .css-1kyxreq {
        background-color: #0E1117;
    }
    </style>
""", unsafe_allow_html=True)

# Optional logo (uncomment if you add one to /imgs/logo.png)
# st.image("imgs/logo.png", width=100)

# --- Title ---
st.markdown("## 📊 Welcome to the NIFTY 200 Stock Visualizer")

# --- Sidebar Inputs ---
st.sidebar.title("Options")
st.sidebar.header("Stock Selection")
ticker = st.sidebar.text_input("Enter Stock Ticker (e.g., RELIANCE.NS)", value="RELIANCE.NS")
start_date = st.sidebar.date_input("Start Date", value=date(2020, 1, 1))
end_date = st.sidebar.date_input("End Date", value=date.today())

# --- Data Fetching ---
@st.cache_data
def fetch_stock_data(ticker, start_date, end_date):
    stock = yf.Ticker(ticker)
    return stock.history(start=start_date, end=end_date)

data = fetch_stock_data(ticker, start_date, end_date)

# --- Visualizations ---
def plot_candlestick(data):
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
    st.plotly_chart(fig, use_container_width=True)

def plot_volume(data):
    fig = px.bar(data, x=data.index, y='Volume', title="Trading Volume", template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

def plot_daily_returns(data):
    data['Daily Return'] = data['Close'].pct_change() * 100
    fig = px.line(data, x=data.index, y='Daily Return', title="Daily Returns (%)", template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

def plot_cumulative_returns(data):
    data['Cumulative Return'] = (1 + data['Close'].pct_change()).cumprod() - 1
    fig = px.line(data, x=data.index, y='Cumulative Return', title="Cumulative Returns", template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

def plot_moving_averages(data, windows):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name="Close Price"))
    for window in windows:
        data[f"MA{window}"] = data['Close'].rolling(window=window).mean()
        fig.add_trace(go.Scatter(x=data.index, y=data[f"MA{window}"], mode='lines', name=f"MA {window}"))
    fig.update_layout(title="Moving Averages", xaxis_title="Date", yaxis_title="Price", template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

def plot_correlation_matrix(data):
    corr = data.corr()
    fig = px.imshow(corr, title="Correlation Matrix", template="plotly_dark", text_auto=True, color_continuous_scale='RdBu_r')
    st.plotly_chart(fig, use_container_width=True)

def get_top_movers(tickers):
    movers = []
    for ticker in tickers:
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
    df = df.sort_values(by='% Change', ascending=False)
    return df.head(5), df.tail(5).sort_values(by='% Change')


# --- Show Stock Data ---
if not data.empty:
    st.subheader(f"📈 Stock Data for {ticker}")
    st.write(data.tail())

    # Charts
    st.subheader("📊 Candlestick Chart")
    plot_candlestick(data)

    st.subheader("📦 Volume Chart")
    plot_volume(data)

    st.subheader("📉 Daily Returns")
    plot_daily_returns(data)

    st.subheader("📈 Cumulative Returns")
    plot_cumulative_returns(data)

    # Moving Averages
    st.sidebar.header("Moving Averages")
    moving_averages = st.sidebar.multiselect("Select Moving Averages (days)", options=[10, 20, 50, 100, 200], default=[20, 50])
    if moving_averages:
        st.subheader("📏 Moving Averages")
        plot_moving_averages(data, moving_averages)

# --- Portfolio Analysis ---
st.sidebar.header("Portfolio Analysis")
portfolio_file = st.sidebar.file_uploader("Upload Portfolio (CSV or Excel)")
if portfolio_file:
    portfolio = pd.read_csv(portfolio_file) if portfolio_file.name.endswith("csv") else pd.read_excel(portfolio_file)
    tickers = portfolio['Ticker'].tolist()
    st.subheader("📁 Portfolio Data")
    st.write(portfolio)

    portfolio_data = {t: fetch_stock_data(t, start_date, end_date)['Close'] for t in tickers}
    portfolio_df = pd.DataFrame(portfolio_data)
    st.subheader("🔗 Correlation Matrix")
    plot_correlation_matrix(portfolio_df)

# --- Top Gainers and Losers in Card Style ---
# --- Top Gainers and Losers in Stylish Card Style ---
st.markdown("<h2 style='text-align:center; color:#f9fafb;'>📈 Top 5 Gainers & 📉 Top 5 Losers</h2>", unsafe_allow_html=True)

# Modern CSS styling for glowing cards
st.markdown("""
<style>
.card-container {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 1.5rem;
    padding: 1rem 0;
}
.card {
    width: 200px;
    background: linear-gradient(135deg, #1f1f1f, #292929);
    border-radius: 15px;
    box-shadow: 0 0 15px rgba(0, 255, 255, 0.15);
    padding: 1rem;
    color: white;
    text-align: center;
    transition: 0.3s ease-in-out;
}
.card:hover {
    transform: scale(1.05);
    box-shadow: 0 0 25px rgba(0, 255, 255, 0.3);
}
.card-title {
    font-size: 1.2rem;
    font-weight: 600;
}
.card-change {
    font-size: 1.5rem;
    font-weight: bold;
    margin: 0.5rem 0;
}
.up .card-change {
    color: #00ff88;
}
.down .card-change {
    color: #ff4d4d;
}
.card-icon {
    font-size: 2rem;
    margin-bottom: 0.5rem;
}
</style>
""", unsafe_allow_html=True)

# Get Nifty 200 tickers from CSV
nifty_200 = get_nifty_200_tickers()['Symbol'].tolist()

# Fetch data and calculate changes
gain_data = []
for t in nifty_200:
    try:
        df = yf.Ticker(t).history(period="2d")
        if len(df) >= 2:
            change = ((df['Close'][-1] - df['Close'][-2]) / df['Close'][-2]) * 100
            gain_data.append((t, round(change, 2)))
    except:
        pass

sorted_gainers = sorted(gain_data, key=lambda x: x[1], reverse=True)
top_5_gainers = sorted_gainers[:5]
top_5_losers = sorted_gainers[-5:]

# Generate cards HTML
def generate_card(symbol, change, is_up=True):
    direction = "up" if is_up else "down"
    icon = "📈" if is_up else "📉"
    return f"""
    <div class="card {direction}">
        <div class="card-icon">{icon}</div>
        <div class="card-title">{symbol}</div>
        <div class="card-change">{change}%</div>
    </div>
    """

gainers_html = "<div class='card-container'>" + "".join([generate_card(s, c, True) for s, c in top_5_gainers]) + "</div>"
losers_html = "<div class='card-container'>" + "".join([generate_card(s, c, False) for s, c in top_5_losers]) + "</div>"

# Show cards
st.markdown("#### 🟢 Gainers", unsafe_allow_html=True)
st.markdown(gainers_html, unsafe_allow_html=True)
st.markdown("#### 🔴 Losers", unsafe_allow_html=True)
st.markdown(losers_html, unsafe_allow_html=True)





st.markdown("<h4>Top 5 Losers</h4>", unsafe_allow_html=True)
losers_html = "<div class='card-container'>" + "".join([create_card(s, c, "down") for s, c in top_5_losers]) + "</div>"
st.markdown(losers_html, unsafe_allow_html=True)
