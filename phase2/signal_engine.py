"""
Phase-2 Institutional Signal Engine

Responsibilities:
- Load NSE-200 universe
- Read latest live prices
- Generate deterministic signals
- Persist signal state with rollover
- Provide stable downstream schema

Outputs:
- output/signal_state.json
- output/previous_signal_state.json
"""

from pathlib import Path
import json
from datetime import datetime
from typing import Dict, List


# ============================================================
# PATHS
# ============================================================

OUTPUT = Path("output")
OUTPUT.mkdir(exist_ok=True)

UNIVERSE_FILE = OUTPUT / "universe.json"
PRICES_FILE = OUTPUT / "prices_live.json"

STATE_FILE = OUTPUT / "signal_state.json"
PREV_STATE_FILE = OUTPUT / "previous_signal_state.json"


# ============================================================
# LOADERS
# ============================================================

def load_json(path: Path, default):
    if not path.exists():
        return default
    with open(path, "r") as f:
        return json.load(f)


def load_universe() -> List[str]:
    if not UNIVERSE_FILE.exists():
        raise FileNotFoundError("❌ universe.json missing. Run universe_loader first.")

    symbols = load_json(UNIVERSE_FILE, [])
    return [s.strip().upper() for s in symbols if s]


def load_prices() -> Dict[str, float]:
    if not PRICES_FILE.exists():
        raise FileNotFoundError("❌ prices_live.json missing. Run live_prices first.")

    return load_json(PRICES_FILE, {})


def load_previous_state() -> List[Dict]:
    return load_json(STATE_FILE, [])


# ============================================================
# SIGNAL LOGIC (DETERMINISTIC & EXTENSIBLE)
# ============================================================

def compute_signal(price: float) -> Dict[str, str]:
    """
    Placeholder deterministic logic.
    Designed to be replaced by Phase-3 ML model
    without changing schema.
    """

    if price <= 0:
        return {"signal": "WAIT", "reason": "Invalid price"}

    # Simple deterministic bands to avoid randomness
    mod5 = int(price) % 5
    mod7 = int(price) % 7

    if mod5 == 0:
        return {"signal": "BUY", "reason": "Momentum breakout"}
    elif mod7 == 0:
        return {"signal": "SELL", "reason": "Mean reversion risk"}
    else:
        return {"signal": "HOLD", "reason": "Trend stable"}


# ============================================================
# BUILD SIGNAL STATE
# ============================================================

def build_signal_state(symbols: List[str], prices: Dict[str, float], prev_state: List[Dict]) -> List[Dict]:
    """
    Generates today's full signal state.
    Maintains entry_date continuity.
    """

    prev_map = {p["ticker"]: p for p in prev_state}

    today = datetime.utcnow().strftime("%Y-%m-%d")

    state: List[Dict] = []

    for sym in symbols:
        price = prices.get(sym, 0.0)

        sig = compute_signal(price)

        # Preserve original entry date if still active
        if sym in prev_map and prev_map[sym]["signal"] in {"BUY", "HOLD"}:
            entry_date = prev_map[sym].get("entry_date", today)
        else:
            entry_date = today

        state.append(
            {
                "ticker": sym,
                "price": price,
                "signal": sig["signal"],
                "reason": sig["reason"],
                "entry_date": entry_date,
            }
        )

    return state


# ============================================================
# STATE ROLLOVER
# ============================================================

def rollover_state():
    """
    Moves today's state → previous_state before writing new one.
    Ensures deterministic historical tracking.
    """
    if STATE_FILE.exists():
        STATE_FILE.replace(PREV_STATE_FILE)


# ============================================================
# SAVE
# ============================================================

def save_state(state: List[Dict]):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

    print(f"✅ signal_state.json written — {len(state)} symbols")


# ============================================================
# MAIN
# ============================================================

def main():

    symbols = load_universe()
    prices = load_prices()
    prev_state = load_previous_state()

    # rollover yesterday → previous
    rollover_state()

    # build today's signals
    new_state = build_signal_state(symbols, prices, prev_state)

    # save
    save_state(new_state)


if __name__ == "__main__":
    main()
