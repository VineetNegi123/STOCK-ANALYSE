import streamlit as st
import yfinance as yf
import pandas as pd
import datetime

st.set_page_config(page_title="Stock Dip Notifier", layout="wide")

st.title("📉 US Stock Dip Notifier")
st.markdown("Monitor selected US stocks and get notified when they dip by a custom threshold.")

# Sidebar - Stock selection and thresholds
st.sidebar.header("⚙️ Settings")
stocks_input = st.sidebar.text_input("Enter stock tickers (comma separated):", "AAPL,MSFT,GOOGL")
tickers = [x.strip().upper() for x in stocks_input.split(",") if x.strip() != ""]
thresh_percent = st.sidebar.slider("Dip alert threshold (% drop)", min_value=1, max_value=20, value=3)

# Date settings
today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)

@st.cache_data(ttl=300)
def fetch_data(ticker):
    data = yf.download(ticker, start=yesterday, end=today + datetime.timedelta(days=1), progress=False)
    return data

if tickers:
    alert_data = []
    st.subheader("📊 Stock Monitoring Dashboard")
    for ticker in tickers:
        data = fetch_data(ticker)
        if data.empty or len(data) < 2:
            st.warning(f"Not enough data for {ticker}")
            continue

        latest = data.iloc[-1]
        prev = data.iloc[-2]
        change_pct = ((latest['Close'] - prev['Close']) / prev['Close']) * 100

        alert = "✅ DIP!" if change_pct <= -thresh_percent else "❌"
        alert_data.append({
            'Ticker': ticker,
            'Price': f"${latest['Close']:.2f}",
            'Change (%)': f"{change_pct:.2f}%",
            'Dip Alert': alert
        })

    df_alert = pd.DataFrame(alert_data)
    st.dataframe(df_alert, use_container_width=True)
else:
    st.info("Enter at least one stock ticker to begin monitoring.")

st.caption("Data provided by Yahoo Finance. This app refreshes every 5 minutes.")
