"""
Run this once.
Reads  symbol_map.txt              ->  "TICKER": "INSTRUMENT_KEY"
Writes symbol+sector_map.txt       ->  "TICKER": "INSTRUMENT_KEY|SECTOR|INDUSTRY|MARKET_CAP"
"""

import re
import time
from pathlib import Path

# ─────────── dependencies ───────────
try:
    from tqdm.auto import tqdm
except ImportError:
    def tqdm(it, **kwargs): return it

try:
    import yfinance as yf
except ImportError:
    yf = None

try:
    from tenacity import retry, wait_exponential, stop_after_attempt
except ImportError:
    # Fallback decorators for environments where tenacity isn't installed yet
    def retry(*args, **kwargs):
        return lambda f: f
    def wait_exponential(*args, **kwargs): return None
    def stop_after_attempt(*args, **kwargs): return None

ROOT = Path(__file__).parent
TXT_IN  = ROOT / "symbol_map.txt"
TXT_OUT = ROOT / "symbol+sector_map.txt"

# ───────────────── 1 · Parse the input file ─────────────────
raw = TXT_IN.read_text(encoding="utf-8")

# matches   "TICKER": "NSE_EQ|ISIN"
pat = re.compile(r'"(?P<sym>[A-Z0-9\-]+)"\s*:\s*"(?P<instr>[^"]+)"')
# Use a dict to automatically deduplicate symbols while preserving the last found instrument key
pairs = list(dict(pat.findall(raw)).items())

if not pairs:
    raise ValueError("No symbol→instrument pairs found in symbol_map.txt")

# ───────────────── 2 · Fetch data (sector, industry, market cap) ─────────────
def get_info(sym: str) -> dict:
    """Fetches details from Yahoo Finance."""
    try:
        if yf is None:
             raise ImportError("yfinance not installed")
        t = yf.Ticker(f"{sym}.NS")
        info = t.info or {}
        return {
            "sector": str(info.get("sector", "Unknown")),
            "industry": str(info.get("industry", "Unknown")),
            "market_cap": info.get("marketCap") # Could be None, int, float
        }
    except Exception:
        return {"sector": "Unknown", "industry": "Unknown", "market_cap": None}

# Decorate with retry after defining it to help some linters
get_info = retry(wait=wait_exponential(multiplier=1, min=1, max=8),
                stop=stop_after_attempt(5))(get_info)

out_lines = []
for sym, instr in tqdm(pairs, desc="Fetching info", unit="stk"):
    data = get_info(sym)

    # Convert market cap to readable format
    mc = data["market_cap"]
    mc_str = "Unknown"
    
    if isinstance(mc, (int, float)):
        val = float(mc)
        if val >= 1e12:
            mc_str = f"{val/1e12:.2f}T"
        elif val >= 1e9:
            mc_str = f"{val/1e9:.2f}B"
        elif val >= 1e6:
            mc_str = f"{val/1e6:.2f}M"
        else:
            mc_str = str(val)

    out_lines.append(f'"{sym}": "{instr}|{data["sector"]}|{data["industry"]}|{mc_str}",\n')
    time.sleep(0.2)  # polite to Yahoo

# ───────────────── 3 · Write the new .txt file ─────────────────
TXT_OUT.write_text("".join(out_lines), encoding="utf-8")
print(f"✅ Wrote {TXT_OUT.relative_to(ROOT)} with {len(out_lines)} entries")
