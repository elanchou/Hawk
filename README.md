
# 🌐 Hawk Trading System 🚀

Hawk Trading is a high-frequency cryptocurrency trading system designed for speed, accuracy, and flexibility.

---

## ✨ Features

- 📈 **Real-time market data streaming**
- ⚡ **High-frequency trading support**
- 📊 **Order book visualization**
- 💼 **Trading history and position management**
- 📋 **Performance analytics**
- 🔄 **Backtesting capabilities**

---

## 🛠️ Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/yourusername/hawk-trading.git
   cd hawk-trading/backend
   ```

2. **Create and activate a virtual environment**:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # macOS/Linux
   .venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

---

## ▶️ Usage

### 🎯 Training and Backtesting

To train the model and perform backtesting, run:

```bash
python scripts/train_and_backtest.py
```

---

### 📡 Market Data Retrieval

Before training and backtesting, ensure market data retrieval is properly configured. Verify that the data source provides data with a `timestamp` column. 

Check the data retrieval logic in `src/services/market_data_service.py`.

---

### 🛑 Error Handling

Encountering this error?  
```
KeyError: "None of ['timestamp'] are in the columns"
```

Here’s how to resolve it:

1. ✅ Confirm that the data source includes the `timestamp` column.  
2. 🐛 Debug by printing the DataFrame's column names in the `get_market_data` method:

   ```python
   print("DataFrame columns:", df.columns)
   ```

3. ⚙️ Double-check the data loading logic and format.

---

## 🤝 Contribution

Contributions are welcome! 🙌 Submit your issues or pull requests to help us improve. 🚀

---

## 📜 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details. 📄

Happy Trading! 🎉
