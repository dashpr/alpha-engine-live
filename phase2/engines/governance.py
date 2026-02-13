from datetime import datetime, timedelta, timezone
from phase2.utils import read_json, write_json, ist_now

STATE_FILE = "phase2/data/portfolio_state.json"
GOV_FILE = "phase2/data/governance.json"


def next_friday(dt):
    days_ahead = 4 - dt.weekday()  # Friday = 4
    if days_ahead <= 0:
        days_ahead += 7
    return dt + timedelta(days=days_ahead)


def regime_explainer(regime: str) -> str:
    explain = {
        "RISK_ON": "Liquidity supportive and breadth strong; portfolio can stay fully invested.",
        "NEUTRAL": "Mixed signals and moderate volatility; maintain balanced exposure.",
        "RISK_OFF": "Weak breadth and rising risk; defensive positioning preferred.",
    }
    return explain.get(regime, "Market regime assessment in progress.")


def run():
    state = read_json(STATE_FILE, {})

    regime = state.get("regime", "NEUTRAL")
    rebalance_required = state.get("rebalance_required", False)

    now_utc = datetime.now(timezone.utc)
    next_eval = next_friday(now_utc)

    gov = {
        "timestamp": ist_now(),
        "regime": regime,
        "regime_note": regime_explainer(regime),
        "last_rebalance": ist_now() if rebalance_required else None,
        "next_evaluation": next_eval.isoformat(),
        "frequency": "WEEKLY",
    }

    write_json(GOV_FILE, gov)

    print("Governance updated:", regime)
