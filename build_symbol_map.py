"""
Run this once.
Reads  symbol_map.txt              ->  "TICKER": "INSTRUMENT_KEY"
Writes symbol+sector_map.txt       ->  "TICKER": "INSTRUMENT_KEY|SECTOR"
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

# ───────────────── 2 · Fetch sector names (with retry + tqdm) ─────────────
@retry(wait=wait_exponential(multiplier=1, min=1, max=8),
       stop=stop_after_attempt(5))
def get_sector(sym: str) -> str:
    return yf.Ticker(f"{sym}.NS").info.get("sector") or "Unknown"

out_lines = []
for sym, instr in tqdm(pairs, desc="Fetching sectors", unit="stk"):
    try:
        sector = get_sector(sym)
    except Exception as e:
        sector = "Unknown"
        print(f"⚠️  {sym}: {e}")
    out_lines.append(f'"{sym}": "{instr}|{sector}",\n')
    time.sleep(0.2)        # polite to Yahoo

# ───────────────── 3 · Write the new .txt file ─────────────────
TXT_OUT.write_text("".join(out_lines), encoding="utf-8")
print(f"✅ Wrote {TXT_OUT.relative_to(ROOT)} with {len(out_lines)} entries")
