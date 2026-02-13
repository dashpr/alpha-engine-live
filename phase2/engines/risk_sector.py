from statistics import mean, pstdev
from phase2.utils import read_json, write_json

NAV_FILE = "phase2/data/nav.json"
POSITIONS_FILE = "phase2/data/positions.json"

RISK_FILE = "phase2/data/risk.json"
SECTOR_FILE = "phase2/data/sectors.json"


def run():
    nav = read_json(NAV_FILE, {"value": 0})
    positions = read_json(POSITIONS_FILE, [])

    # ---------- Sector weights ----------
    sectors = {}
    total_alloc = sum(p.get("allocated_capital", 0) for p in positions) or 1

    for p in positions:
        sec = p.get("sector", "Unknown")
        sectors[sec] = sectors.get(sec, 0) + p.get("allocated_capital", 0)

    sector_out = [
        {"sector": k, "weight": round(v / total_alloc * 100, 2)}
        for k, v in sectors.items()
    ]

    write_json(SECTOR_FILE, sector_out)

    # ---------- Risk metrics (Phase-2 basic institutional) ----------
    # NOTE: Full drawdown/CAGR will come in Phase-3 with NAV history.
    risk = {
        "nav": nav["value"],
        "volatility_placeholder": 0,
        "sharpe_placeholder": 0,
        "drawdown_placeholder": 0,
    }

    write_json(RISK_FILE, risk)

    print("Risk & sector updated")
