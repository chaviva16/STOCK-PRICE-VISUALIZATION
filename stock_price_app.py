import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objs as go
from ta.momentum import RSIIndicator

st.set_page_config(page_title="📈 Global Asset Visualizer", layout="wide")
st.title("📈 Visualize & Compare Stocks, Nigerian Equities, and Crypto")

# --------------------------- #
# ASSET SELECTION
# --------------------------- #
us_stocks = {
    "Apple (AAPL)": "AAPL",
    "Tesla (TSLA)": "TSLA",
    "Microsoft (MSFT)": "MSFT",
    "Amazon (AMZN)": "AMZN",
    "Google (GOOGL)": "GOOGL",
    "NVIDIA (NVDA)": "NVDA",
    "Meta (META)": "META",
    "Netflix (NFLX)": "NFLX",
    "JPMorgan Chase (JPM)": "JPM",
    "Chevron (CVX)": "CVX",
    "Coca-Cola (KO)": "KO",
    "Walmart (WMT)": "WMT",
    "Disney (DIS)": "DIS"
}

nigerian_stocks = {
    "GTCO (GTCO.LG)": "GTCO.LG",
    "Zenith Bank (ZENITHBANK.LG)": "ZENITHBANK.LG",
    "Access Holdings (ACCESSCORP.LG)": "ACCESSCORP.LG",
    "UBA (UBA.LG)": "UBA.LG",
    "MTN Nigeria (MTNN.LG)": "MTNN.LG",
    "Dangote Cement (DANGCEM.LG)": "DANGCEM.LG",
    "Nestle Nigeria (NESTLE.LG)": "NESTLE.LG",
    "Seplat Energy (SEPLAT.LG)": "SEPLAT.LG"
}

cryptos = {
    "Bitcoin (BTC-USD)": "BTC-USD",
    "Ethereum (ETH-USD)": "ETH-USD",
    "Solana (SOL-USD)": "SOL-USD",
    "Binance Coin (BNB-USD)": "BNB-USD",
    "Cardano (ADA-USD)": "ADA-USD",
    "XRP (XRP-USD)": "XRP-USD",
    "Dogecoin (DOGE-USD)": "DOGE-USD"
}

asset_options = {**us_stocks, **nigerian_stocks, **cryptos}

st.sidebar.header("Choose Assets & Date Range")
ticker1_name = st.sidebar.selectbox("Primary Asset", list(asset_options.keys()), index=0)
ticker2_name = st.sidebar.selectbox("Compare With", list(asset_options.keys()), index=1)

ticker1 = asset_options[ticker1_name]
ticker2 = asset_options[ticker2_name]

start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2024-01-01"))
end_date = st.sidebar.date_input("End Date", pd.to_datetime("today"))

# Determine currency symbol based on ticker
if ".LG" in ticker1:
    currency_symbol = "₦"
elif "-USD" in ticker1:
    currency_symbol = "$"
else:
    currency_symbol = "$"

# --------------------------- #
# DATA LOADING
# --------------------------- #
@st.cache_data
def load_data(ticker, start, end):
    stock = yf.Ticker(ticker)
    return stock.history(start=start, end=end)

data1 = load_data(ticker1, start_date, end_date)
data2 = load_data(ticker2, start_date, end_date)

data1["MA7"] = data1["Close"].rolling(7).mean()
data1["MA30"] = data1["Close"].rolling(30).mean()
data1["Daily Return"] = data1["Close"].pct_change() * 100  # Convert to percentage
rsi = RSIIndicator(data1["Close"]).rsi()

# --------------------------- #
# TABS
# --------------------------- #
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Price Chart",
    "💹 Candlestick",
    "🔁 Compare",
    "📉 RSI",
    "⬇️ Download"
])

with tab1:
    st.subheader(f"{ticker1_name} - Closing Price & Moving Averages")
    fig1, ax1 = plt.subplots(figsize=(12, 6))
    ax1.plot(data1["Close"], label=f"Closing Price ({currency_symbol})", color="blue")
    ax1.plot(data1["MA7"], label="7-Day Moving Average", linestyle="--", color="orange")
    ax1.plot(data1["MA30"], label="30-Day Moving Average", linestyle="--", color="green")
    ax1.set_title(f"{ticker1} Price Trend")
    ax1.set_ylabel(f"Price ({currency_symbol})")
    ax1.legend()
    ax1.grid(True)
    st.pyplot(fig1)

    st.markdown("### 📈 Daily Returns (% Change from Previous Day)")
    fig2, ax2 = plt.subplots(figsize=(12, 4))
    data1["Daily Return"].plot(ax=ax2, color="purple")
    ax2.set_ylabel("Daily Return (%)")
    ax2.grid(True)
    st.pyplot(fig2)

with tab2:
    st.subheader(f"Candlestick Chart - {ticker1_name}")
    candle = go.Figure(data=[go.Candlestick(
        x=data1.index,
        open=data1['Open'],
        high=data1['High'],
        low=data1['Low'],
        close=data1['Close'],
        increasing_line_color='green',
        decreasing_line_color='red'
    )])
    candle.update_layout(title=f"{ticker1} Candlestick Chart", xaxis_rangeslider_visible=False)
    st.plotly_chart(candle, use_container_width=True)

with tab3:
    st.subheader(f"Comparison: {ticker1_name} vs {ticker2_name}")
    compare_df = pd.DataFrame({
        f"{ticker1} Close": data1["Close"],
        f"{ticker2} Close": data2["Close"]
    }).dropna()
    fig3, ax3 = plt.subplots(figsize=(12, 5))
    compare_df.plot(ax=ax3)
    ax3.set_title(f"{ticker1} vs {ticker2} - Closing Prices")
    ax3.set_ylabel("Price")
    ax3.grid(True)
    st.pyplot(fig3)

with tab4:
    st.subheader(f"RSI Indicator - {ticker1_name}")
    fig_rsi, ax_rsi = plt.subplots(figsize=(12, 3))
    ax_rsi.plot(data1.index, rsi, color='darkred')
    ax_rsi.axhline(70, color='gray', linestyle='--')
    ax_rsi.axhline(30, color='gray', linestyle='--')
    ax_rsi.set_title("RSI (Relative Strength Index) - Overbought/Undersold Levels")
    ax_rsi.set_ylabel("RSI Value")
    ax_rsi.grid(True)
    st.pyplot(fig_rsi)

with tab5:
    st.subheader("Download CSV Data")
    st.download_button(
        label=f"Download {ticker1} Data as CSV",
        data=data1.to_csv().encode('utf-8'),
        file_name=f"{ticker1}_data.csv",
        mime="text/csv"
    )

st.markdown("---")
st.markdown("Made with ❤️ by Chaviva — Powered by [Yahoo Finance](https://finance.yahoo.com)")