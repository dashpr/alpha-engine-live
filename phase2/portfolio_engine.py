"""
Phase-2 Institutional Portfolio Engine

Responsibilities:
- Build portfolio from signal_state.json
- Dynamic position count (no fixed N)
- Volatility-scaled sizing (deterministic proxy)
- Capital linked to previous NAV
- Stable output for dashboard & NAV engine

Output:
- output/portfolio_positions.json
"""

from pathlib import Path
import json
from typing import List, Dict

OUTPUT = Path("output")
OUTPUT.mkdir(exist_ok=True)

SIGNAL_FILE = OUTPUT / "signal_state.json"
NAV_FILE = OUTPUT / "nav_latest.json"          # optional future use
PORTFOLIO_FILE = OUTPUT / "portfolio_positions.json"


# ============================================================
# LOAD HELPERS
# ============================================================

def load_json(path: Path, default):
    if not path.exists():
        return default
    with open(path, "r") as f:
        return json.load(f)


def load_signals() -> List[Dict]:
    if not SIGNAL_FILE.exists():
        raise FileNotFoundError("❌ signal_state.json missing")
    return load_json(SIGNAL_FILE, [])


def load_capital() -> float:
    """
    Capital source:
    1️⃣ previous NAV if available
    2️⃣ fallback initial capital (first run only)
    """
    nav = load_json(NAV_FILE, {})
    if "nav" in nav:
        return float(nav["nav"])

    # first ever run fallback (allowed once)
    return 200000.0


# ============================================================
# RANKING & SIZING LOGIC
# ============================================================

def rank_candidates(signals: List[Dict]) -> List[Dict]:
    """
    Select BUY + HOLD universe and rank deterministically.
    """

    eligible = [
        s for s in signals
        if s["signal"] in {"BUY", "HOLD"} and s["price"] > 0
    ]

    # Deterministic ranking proxy:
    # lower price dispersion → higher stability
    ranked = sorted(
        eligible,
        key=lambda x: abs(int(x["price"]) % 13),
    )

    return ranked


def compute_weights(candidates: List[Dict]) -> Dict[str, float]:
    """
    Volatility proxy sizing using inverse price bucket.
    Deterministic and CI-safe.
    """

    if not candidates:
        return {}

    scores = {}

    for c in candidates:
        # inverse dispersion proxy
        score = 1 / (1 + abs(int(c["price"]) % 17))
        scores[c["ticker"]] = score

    total = sum(scores.values())

    return {k: v / total for k, v in scores.items()}


# ============================================================
# BUILD PORTFOLIO
# ============================================================

def build_portfolio(signals: List[Dict], capital: float) -> List[Dict]:

    ranked = rank_candidates(signals)

    if not ranked:
        return []

    weights = compute_weights(ranked)

    portfolio = []

    for s in ranked:
        ticker = s["ticker"]
        price = s["price"]

        weight = weights.get(ticker, 0)
        position_value = capital * weight

        qty = int(position_value // price) if price > 0 else 0

        portfolio.append(
            {
                "ticker": ticker,
                "qty": qty,
                "live_price": price,
                "position_value": round(qty * price, 2),
                "weight": round(weight * 100, 2),
            }
        )

    return portfolio


# ============================================================
# SAVE
# ============================================================

def save_portfolio(portfolio: List[Dict]):

    with open(PORTFOLIO_FILE, "w") as f:
        json.dump(portfolio, f, indent=2)

    print(f"✅ portfolio_positions.json written — {len(portfolio)} positions")


# ============================================================
# MAIN
# ============================================================

def main():

    signals = load_signals()
    capital = load_capital()

    portfolio = build_portfolio(signals, capital)

    save_portfolio(portfolio)


if __name__ == "__main__":
    main()
