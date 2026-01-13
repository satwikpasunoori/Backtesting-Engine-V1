# AI Trading Strategy Engine 🚀 (Docker-Based)

An **AI-assisted trading strategy generator and backtesting platform** that runs fully inside **Docker**.  
It converts **natural language trading ideas** into executable Python strategies using **Google Gemini LLM** and **real historical market data from Polygon.io**.

> ⚠️ **Disclaimer**  
> This project is strictly for **educational and research purposes**.  
> It is **NOT a live trading system** and **does not provide financial advice**.

🔹 Important Clarification

>Strategy prompts → must use only supported indicators

>Adding new indicators → requires code changes

>AI will not automatically support new indicators unless they are explicitly added
---
---

## 🔥 What This Project Does

- Runs completely inside a **Docker container**
- Converts **plain English trading strategies** into Python code using Gemini AI
- Backtests strategies on **real historical OHLCV market data**
- Applies **basic risk management**
  - Position sizing
  - Stop loss
  - Risk–reward ratio
- Saves strategies **locally (SQLite)**
- Provides an interactive **Streamlit UI**

---

## 🧠 High-Level Working Flow

1. Start the application using Docker
2. Enter **Gemini API key** and **Polygon API key**
3. Select market & risk settings
4. Write a strategy prompt (supported indicators only)
5. Gemini generates Python strategy code
6. Strategy is backtested on historical data
7. Metrics and trade logs are displayed
8. Strategy can be saved with a custom name

---

## 🛠 Tech Stack

- Python
- Streamlit
- Google Gemini API
- Polygon.io API
- pandas, pandas_ta
- SQLite (local database)
- Docker

---

## 🚀 Getting Started (Docker – Recommended)

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/ai-trading-strategy-engine.git
cd ai-trading-strategy-engine
```

---

### 2️⃣ Build the Docker Image

```bash
docker build -t ai-trading-engine .
```

---

### 3️⃣ Run the Container

```bash
docker run -p 8501:8501 ai-trading-engine
```

Open your browser:

```
http://localhost:8501
```

---

## 🔑 API Keys Setup (MANDATORY)

This application requires **two API keys**.

### ✅ Google Gemini API Key
- Used to generate trading strategy code
- Get it from: https://ai.google.dev/

### ✅ Polygon API Key
- Used to fetch historical market data
- Get it from: https://polygon.io/

### How to Provide Keys
- Enter both keys in the **Streamlit sidebar**
- Keys are **not stored** in the database
- Keys are valid only for the current session

---

## ⚙️ Strategy Configuration

You can configure:

- **Stock Symbol** (e.g., AAPL) (Check For Supported Free Symbols in Polygon)
- **Timeframe**: day / hour / minute
- **Bar Multiplier**
- **Date Range**
- **Risk % per trade**
- **Stop Loss %**
- **Risk–Reward Ratio**

These settings control how the **backtest engine** behaves.

---

## ⚠️ IMPORTANT: STRATEGY PROMPTS & INDICATORS

### ✅ Supported Strategy Type

- **Rule-based technical strategies ONLY**
- No machine learning
- No prediction models

---

## 📊 Supported Indicators (Current)

Only the following indicators are officially supported:

- **RSI (Relative Strength Index)**
  - Example: `RSI(14) < 30`
  - Example: `RSI(14) > 70`

- **MACD (Moving Average Convergence Divergence)**
  - Uses **MACD Histogram**: `MACDh_12_26_9`
  - Example: `MACD histogram turns positive`

Indicators are computed using the **pandas_ta** library.

---

## ✍️ Allowed Prompt Format (MANDATORY)

Strategy prompts must use **ONLY supported indicators**.

### ✅ Valid Prompt Examples
```
Buy when RSI(14) < 30, sell when RSI(14) > 70
Buy when RSI crosses above 30 and MACD histogram is positive
Buy when MACD histogram turns positive, sell when it turns negative
```

### ❌ Invalid / Unsupported Prompt Examples
```
Predict next price using AI
Use LSTM or machine learning
Trade using news sentiment
Use indicators not defined in the system
```

> ⚠️ Invalid prompts may generate unusable or unsafe code.

---

## 🚫 What This Project Does NOT Support

- Machine learning or deep learning
- Price prediction or forecasting
- Fundamental analysis
- News or sentiment trading
- High-frequency trading
- Live broker execution

---

## ▶️ Running a Backtest

1. Click **Generate Code**
2. Review generated Python strategy
3. Click **Run Backtest**
4. View:
   - Final capital
   - Profit %
   - Number of trades
   - Win rate
   - Trade logs

---

## 💾 Saving Strategies

- Enter a **custom strategy name**
- Click **Save Strategy**
- Strategy is saved locally using SQLite
- View saved strategies in the **Saved Strategies** tab

---

## 📂 Database & Storage (Docker Clarification)

- SQLite database is stored **locally**
- When running Docker:
  - Database exists **inside the container**
  - Data persists only while the container exists
- For permanent storage, a **Docker volume** is required

---

## ➕ Adding More Indicators (Project Customization Guide)

This project supports **only predefined technical indicators** when writing strategy prompts.  
You **cannot add new indicators using prompts or the UI alone**.

However, since this is an **open and customizable project**, anyone who downloads or forks the repository **can extend it by modifying the source code locally**.

### 🔹 Key Clarification
- **Prompts** → use only documented indicators
- **New indicators** → require code changes
- AI will **not automatically support new indicators** unless explicitly added

---

### 1️⃣ Add the Indicator in Code

Edit `app.py` and modify the `generate_strategy_code()` function.

Example: Adding **EMA (20)** using `pandas_ta`

```python
ema = ta.ema(df['close'], length=20)
```

> The indicator must exist in the `pandas_ta` library.

---

### 2️⃣ Define Buy/Sell Signal Logic

Use the indicator to generate trading signals:

```python
signals[ema > df['close']] = 1    # Buy signal
signals[ema < df['close']] = -1   # Sell signal
```

Signal rules:
- `1` → Buy  
- `-1` → Sell  

---

### 3️⃣ Update Supported Indicators List

After adding a new indicator, update this README:

```
Supported Indicators:
- RSI
- MACD
- EMA (20)
```

This ensures users know **which indicators are valid in prompts**.

---

### 4️⃣ Rebuild Docker Image

After modifying the code, rebuild and run the container:

in poweshell(windows)
```bash
docker build -t ai-trading-engine .
docker run -p 8501:8501 ai-trading-engine
```

---

## ⚠️ Known Limitations

### Polygon API (Free Tier)
- Historical data often limited to ~1 year
- API rate limits apply

### Gemini API (Free Tier)
- Limited token usage
- Strategy quality depends on prompt clarity

### Backtesting Assumptions
- No brokerage or transaction costs
- No slippage or market impact
- Long-only strategies
- Single asset at a time

### Security
- AI-generated code is executed using `exec()`
- Intended only for **local, trusted environments**

---

## 🚀 Future Enhancements (Backtesting Only)

- Add transaction costs and slippage simulation
- Add more technical indicators
- Multi-timeframe backtesting
- Parameter sweep and optimization
- Advanced metrics (drawdown, Sharpe, expectancy)
- Equity curve visualization
- Strategy comparison dashboards

## 📜 Final Disclaimer

This project is for **learning and research only**.  
Do **NOT** use it for real-money trading.
