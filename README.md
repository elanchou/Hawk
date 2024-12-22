# Hawk Trading System

Hawk Trading is a high-frequency cryptocurrency trading system designed to support the OKX exchange.

## Features

- Real-time market data streaming
- High-frequency trading support
- Order book visualization
- Trading history and position management
- Performance analytics
- Backtesting capabilities

## Directory Structure
backend/
├── scripts/ # Directory for scripts
│ ├── train_and_backtest.py # Script for training and backtesting
├── src/ # Source code directory
│ ├── api/ # API related code
│ ├── config/ # Configuration files
│ ├── models/ # Data models
│ ├── services/ # Service layer
│ ├── utils/ # Utility classes
└── requirements.txt # Dependency file

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/hawk-trading.git
   cd hawk-trading/backend
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # macOS/Linux
   .venv\Scripts\activate     # Windows
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Training and Backtesting

To train the model and perform backtesting, run the following command:

```bash
python scripts/train_and_backtest.py
```

### Market Data Retrieval

Before running training and backtesting, ensure that you have correctly configured the market data retrieval functionality. Check the data retrieval logic in `src/services/market_data_service.py` to ensure that the data source returns data containing the `timestamp` column.

### Error Handling

If you encounter the following error during execution:

```
KeyError: "None of ['timestamp'] are in the columns"
```

Please check the following:

1. Ensure that the data returned from the data source contains the `timestamp` column.
2. Print the DataFrame's column names in the `get_market_data` method for debugging:

   ```python
   print("DataFrame columns:", df.columns)
   ```

3. Ensure that the data loading logic is correct and that the data format meets expectations.

## Contribution

Contributions are welcome! Please submit issues or pull requests.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

