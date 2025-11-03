"""
Run this once.
Reads  symbol_map.txt              ->  "TICKER": "INSTRUMENT_KEY"
Writes symbol+sector_map.txt       ->  "TICKER": "INSTRUMENT_KEY|SECTOR|INDUSTRY|MARKET_CAP"
"""

import re
import time
from pathlib import Path

# ─────────── progress bar ───────────
try:
    from tqdm.auto import tqdm            # pip install tqdm
except ImportError:                       # fallback if tqdm missing
    def tqdm(it, **k): return it

import yfinance as yf
from tenacity import retry, wait_exponential, stop_after_attempt

ROOT = Path(__file__).parent
TXT_IN  = ROOT / "symbol_map.txt"
TXT_OUT = ROOT / "symbol+sector_map.txt"

# ───────────────── 1 · Parse the input file ─────────────────
raw = TXT_IN.read_text(encoding="utf-8")

# matches   "TICKER": "NSE_EQ|ISIN"
pat = re.compile(r'"(?P<sym>[A-Z0-9\-]+)"\s*:\s*"(?P<instr>[^"]+)"')
pairs = pat.findall(raw)
if not pairs:
    raise ValueError("No symbol→instrument pairs found in symbol_map.txt")

# ───────────────── 2 · Fetch data (sector, industry, market cap) ─────────────
@retry(wait=wait_exponential(multiplier=1, min=1, max=8),
       stop=stop_after_attempt(5))
def get_info(sym: str):
    t = yf.Ticker(f"{sym}.NS")
    info = t.info or {}
    return {
        "sector": info.get("sector", "Unknown"),
        "industry": info.get("industry", "Unknown"),
        "market_cap": info.get("marketCap", "Unknown")
    }

out_lines = []
for sym, instr in tqdm(pairs, desc="Fetching info", unit="stk"):
    try:
        data = get_info(sym)
    except Exception as e:
        print(f"⚠️  {sym}: {e}")
        data = {"sector": "Unknown", "industry": "Unknown", "market_cap": "Unknown"}

    # Convert market cap to readable format if numeric
    mc = data["market_cap"]
    if isinstance(mc, (int, float)):
        if mc >= 1e9:
            mc_str = f"{mc/1e9:.2f}B"
        elif mc >= 1e6:
            mc_str = f"{mc/1e6:.2f}M"
        else:
            mc_str = str(mc)
    else:
        mc_str = str(mc)

    out_lines.append(f'"{sym}": "{instr}|{data["sector"]}|{data["industry"]}|{mc_str}",\n')
    time.sleep(0.2)  # polite to Yahoo

# ───────────────── 3 · Write the new .txt file ─────────────────
TXT_OUT.write_text("".join(out_lines), encoding="utf-8")
print(f"✅ Wrote {TXT_OUT.relative_to(ROOT)} with {len(out_lines)} entries")
