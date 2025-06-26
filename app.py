import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
from telegram_alert import send_telegram_alert

st.set_page_config(page_title="Stock Dip Notifier", layout="wide")
st.title("📉 US Stock Dip Notifier with Telegram Alerts")

st.sidebar.header("⚙️ Settings")
stocks_input = st.sidebar.text_input("Enter stock tickers (comma separated):", "AAPL,MSFT,GOOGL")
tickers = [x.strip().upper() for x in stocks_input.split(",") if x.strip()]
thresh_percent = st.sidebar.slider("Dip alert threshold (% drop)", min_value=1, max_value=20, value=3)
show_trend = st.sidebar.checkbox("Show 7-day trend chart", value=True)

today = datetime.date.today()
start_date = today - datetime.timedelta(days=7)

@st.cache_data(ttl=300)
def fetch_data(ticker):
    data = yf.download(ticker, start=start_date, end=today + datetime.timedelta(days=1), progress=False)
    return data

BOT_TOKEN = st.secrets["BOT_TOKEN"]
CHAT_ID = st.secrets["CHAT_ID"]

if tickers:
    st.subheader("📊 Stock Monitoring Dashboard")
    alert_data = []
    
    for ticker in tickers:
        data = fetch_data(ticker)
        if data.empty or len(data) < 2:
            st.warning(f"Not enough data for {ticker}")
            continue

        latest = data.iloc[-1]
        prev = data.iloc[-2]
        change_pct = ((latest['Close'] - prev['Close']) / prev['Close']) * 100
        alert = "✅ DIP!" if change_pct <= -thresh_percent else "❌"

        if alert == "✅ DIP!":
            message = f"📉 {ticker} dropped {change_pct:.2f}% to ${latest['Close']:.2f} — Dip Alert!"
            send_telegram_alert(BOT_TOKEN, CHAT_ID, message)

        alert_data.append({
            'Ticker': ticker,
            'Price': f"${latest['Close']:.2f}",
            'Change (%)': f"{change_pct:.2f}%",
            'Dip Alert': alert
        })

        if show_trend:
            st.line_chart(data['Close'], height=150, use_container_width=True)

    st.dataframe(pd.DataFrame(alert_data), use_container_width=True)
else:
    st.info("Enter at least one stock ticker to begin monitoring.")

st.caption("Data by Yahoo Finance. This app refreshes every 5 mins.")
