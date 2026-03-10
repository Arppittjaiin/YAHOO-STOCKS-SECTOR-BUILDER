# 📈 Yahoo Stocks Sector Builder

A lightweight Python utility that enriches a list of Indian stock symbols with **sector**, **industry**, and **market-cap** details fetched from Yahoo Finance.  
It reads an existing `symbol_map.txt` containing `"TICKER": "INSTRUMENT_KEY"` pairs and generates an enhanced file:


This tool is useful for analysts, quants, traders, and data engineers who need enriched metadata for NSE-listed stocks.

---

## ⚙️ Features

- 📄 **Parses input symbol–instrument map** from `symbol_map.txt`
- 🌐 **Fetches live metadata** from Yahoo Finance via `yfinance`
- 🔁 **Retry logic** (via `tenacity`) to handle API throttling/failures
- 📊 **Formats market cap** into readable values (e.g., `12.5B`, `480M`)
- 📝 **Outputs enriched dataset** as `symbol+sector_map.txt`
- 🧹 **Polite API pacing** using `time.sleep` to avoid Yahoo rate limits

---

## 🧠 Tech Stack

- **Python 3.9+**
- [`yfinance`](https://pypi.org/project/yfinance/)
- [`tenacity`](https://pypi.org/project/tenacity/)
- [`tqdm`](https://pypi.org/project/tqdm/)
- Standard library: `re`, `pathlib`, `time`

---

## 🛠️ Installation & Setup

```

### 🚀 Usage

Run the script using the convenient batch file:
- Simply double-click **`run.bat`**.

Or manually:
```bash
pip install -r requirements.txt
python build_symbol_map.py
```

Make sure **`symbol_map.txt`** is in the same folder as the script.

Example input (symbol_map.txt)

"TCS": "NSE_EQ|INE467B01029"

"INFY": "NSE_EQ|INE009A01021"

Example output (symbol+sector_map.txt)

"TCS": "NSE_EQ|INE467B01029|Technology|IT Services|13.4T",

"INFY": "NSE_EQ|INE009A01021|Technology|Consulting Services|6.8T",

🛠️ How It Works
1. Parse Input File

Extracts "TICKER": "INSTRUMENT_KEY" using regex:

pat = r'"(?P<sym>[A-Z0-9\-]+)"\s*:\s*"(?P<instr>[^"]+)"'

2. Fetch Stock Metadata

For each symbol:
Calls Yahoo Finance using yfinance.Ticker

Uses retry logic:

@retry(wait=wait_exponential(min=1, max=8), stop=stop_after_attempt(5))

Extracts:

sector

industry

marketCap

3. Format & Write Output

Converts market cap → B, M

Writes formatted string to symbol+sector_map.txt

📊 Configuration

File	Purpose

symbol_map.txt	Input mapping ("TICKER": "INSTRUMENT_KEY")

symbol+sector_map.txt	Output enriched mapping

requirements.txt	Python dependencies

No .env file or API keys are required—Yahoo data is free and public.

👤 Author
Arpit Jain (AJ)


License

This project is open source and available for any use(MIT License).


Disclaimer

This tool is for educational and research purposes. Always verify the accuracy of data before using it for trading decisions. The authors are not responsible for any financial losses.


Contributing

Contributions are welcome! Feel free to:


Report bugs

Suggest features

Submit pull requests

Improve documentation

Support


For issues or questions:

Check errors.log for detailed error messages

Review this README's troubleshooting section

Open an issue on the repository



