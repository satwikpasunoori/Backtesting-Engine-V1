import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from polygon import RESTClient
from google import genai  # Correct import for current SDK
import sqlite3

# Sidebar
st.sidebar.title("Keys")
polygon_key = st.sidebar.text_input("Polygon API Key")
gemini_key = st.sidebar.text_input("Gemini API Key", type="password")

if not polygon_key or not gemini_key:
    st.warning("Enter keys to start")
    st.stop()

client_polygon = RESTClient(polygon_key)

# Client for Gemini (new SDK – no configure, key in client)
client = genai.Client(api_key=gemini_key)

# Database
conn = sqlite3.connect('strategies.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS strategies
             (id INTEGER PRIMARY KEY, name TEXT, prompt TEXT, code TEXT, settings TEXT)''')
conn.commit()

# Generate code – using new SDK
def generate_strategy_code(prompt):
    response = client.models.generate_content(
        model="gemini-2.5-flash",  # Current free fast model
        contents=f"""
Write ONLY the Python function:

def get_signals(df: pd.DataFrame) -> pd.Series:
    import pandas as pd
    import pandas_ta as ta
    
    # Indicators
    rsi = ta.rsi(df['close'], length=14)
    macd = ta.macd(df['close'])  # Use macd['MACDh_12_26_9'] (lowercase h) for histogram
    
    signals = pd.Series(0, index=df.index)
    
    # Strategy: {prompt}
    
    return signals

Rules:
- ALWAYS import pandas and pandas_ta
- ALWAYS use 'MACDh_12_26_9' (lowercase h) for MACD histogram
- Output ONLY the function code – no ```
"""
    )
    code = response.text.strip()
    if '```' in code:
        code = code.split('```')[1].strip()
        if code.startswith('python'):
            code = code[6:].strip()
    return code

# Data
def get_data(ticker, multiplier, timespan, from_date, to_date):
    aggs = list(client_polygon.list_aggs(ticker, multiplier, timespan, from_date, to_date, limit=50000))
    if not aggs:
        return pd.DataFrame()
    df = pd.DataFrame(aggs)
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df = df.set_index('timestamp')[['open', 'high', 'low', 'close', 'volume']]
    return df

# Backtest – safe
def backtest(df, signals, initial_balance=10000, position_sizing=0.01, sl=0.02, tp_rr=2.0):
    if df.empty:
        return {'Final Money': initial_balance, 'Profit %': 0, 'Trades': 0, 'Win %': 0}, pd.DataFrame()
    
    balance = initial_balance
    position = 0
    entry_price = 0
    trades = []
    
    for i in range(1, len(df)):
        price = df['close'].iloc[i]
        high = df['high'].iloc[i]
        low = df['low'].iloc[i]
        signal = signals.iloc[i]
        
        if position > 0:
            pnl = 0
            exited = False
            if low <= entry_price * (1 - sl):
                pnl = position * (entry_price * (1 - sl) - entry_price)
                trades.append({'type': 'SL', 'pnl': pnl})
                exited = True
            elif high >= entry_price * (1 + sl * tp_rr):
                pnl = position * (entry_price * (1 + sl * tp_rr) - entry_price)
                trades.append({'type': 'TP', 'pnl': pnl})
                exited = True
            elif signal == -1:
                pnl = position * (price - entry_price)
                trades.append({'type': 'Sell', 'pnl': pnl})
                exited = True
            if exited:
                balance += pnl
                position = 0
        
        if position == 0 and signal == 1:
            position = (balance * position_sizing) / price
            entry_price = price
            trades.append({'type': 'Buy', 'pnl': 0})
    
    if position > 0:
        pnl = position * (df['close'].iloc[-1] - entry_price)
        balance += pnl
        trades.append({'type': 'End', 'pnl': pnl})
    
    trades_df = pd.DataFrame(trades)
    completed = trades_df[trades_df['pnl'] != 0] if 'pnl' in trades_df.columns else pd.DataFrame()
    num_trades = len(completed)
    win_rate = (completed['pnl'] > 0).mean() * 100 if num_trades > 0 else 0
    
    metrics = {
        'Final Money': round(balance, 2),
        'Profit %': round((balance - initial_balance)/initial_balance * 100, 2),
        'Trades': num_trades,
        'Win %': round(win_rate, 2)
    }
    return metrics, trades_df

# UI
tab1, tab2 = st.tabs(["Backtest", "Saved"])

with tab1:
    st.title("Free Trading Engine")

    ticker = st.text_input("Stock", "AAPL")
    timeframe = st.selectbox("Time", ["day", "hour", "minute"])
    multiplier = st.number_input("Bars", 1, 60, 1)
    from_date = st.date_input("Start", value=pd.to_datetime("2020-01-01"))
    to_date = st.date_input("End", value=pd.to_datetime("today"))

    prompt = st.text_area("Strategy", "Buy when RSI(14) < 30, sell when RSI(14) > 70")

    risk = st.slider("Risk %", 0.5, 5.0, 1.0) / 100
    sl = st.slider("SL %", 1.0, 10.0, 2.0) / 100
    rr = st.slider("RR", 1.5, 5.0, 2.0)

    # ---------- Generate Code ----------
    if st.button("Generate Code"):
        with st.spinner("Gemini creating code..."):
            st.session_state.code = generate_strategy_code(prompt)
            st.session_state.prompt = prompt

    if "code" in st.session_state:
        st.subheader("Generated Code")
        st.code(st.session_state.code)

    # ---------- Run Backtest ----------
    if st.button("Run Backtest"):
        df = get_data(ticker.upper(), multiplier, timeframe, str(from_date), str(to_date))
        if df.empty:
            st.error("No data available")
        else:
            local = {"pd": pd, "np": np, "ta": __import__("pandas_ta")}
            exec(st.session_state.code, {}, local)
            signals = local["get_signals"](df)

            metrics, trades = backtest(
                df,
                signals,
                position_sizing=risk,
                sl=sl,
                tp_rr=rr
            )

            st.session_state.last_metrics = metrics
            st.session_state.last_trades = trades

    # ---------- Results ----------
    if "last_metrics" in st.session_state:
        st.subheader("Results")
        st.json(st.session_state.last_metrics)
        st.dataframe(st.session_state.last_trades)

        # ---------- Save Strategy ----------
        name = st.text_input("Strategy Name", key="save_name")

        if st.button("Save Strategy"):
            settings = f"{ticker},{multiplier},{timeframe},{risk},{sl},{rr}"

            c.execute(
                "INSERT INTO strategies (name, prompt, code, settings) VALUES (?, ?, ?, ?)",
                (name, st.session_state.prompt, st.session_state.code, settings)
            )
            conn.commit()

            st.success("Strategy saved successfully ✅")
            st.session_state.refresh_saved = True

# ---------------- SAVED TAB ----------------
with tab2:
    st.title("Saved Strategies")

    df_saved = pd.read_sql("SELECT * FROM strategies ORDER BY id DESC", conn)
    st.dataframe(df_saved)