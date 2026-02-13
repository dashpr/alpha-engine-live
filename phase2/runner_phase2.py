import json
import os
import subprocess
from datetime import datetime

# ============================================
# PATHS
# ============================================
OUTPUT_DIR = "output"
PHASE2_DIR = "phase2"

PORTFOLIO_FILE = f"{OUTPUT_DIR}/target_portfolio.json"

NAV_FILE = f"{PHASE2_DIR}/nav.json"
POSITIONS_FILE = f"{PHASE2_DIR}/positions.json"
DEPLOY_FILE = f"{PHASE2_DIR}/deployment.json"
GOV_FILE = f"{PHASE2_DIR}/governance.json"
AI_FILE = f"{PHASE2_DIR}/ai.json"

INITIAL_CAPITAL = 200000

os.makedirs(PHASE2_DIR, exist_ok=True)

# ============================================
# LOAD MODEL PORTFOLIO (single source of truth)
# ============================================
if not os.path.exists(PORTFOLIO_FILE):
    raise Exception("❌ target_portfolio.json not found")

with open(PORTFOLIO_FILE) as f:
    model = json.load(f)

selected_stocks = model.get("stocks", [])
regime = model.get("regime", "Neutral")
rebalance_flag = model.get("rebalance_required", False)

# ============================================
# CAPITAL DEPLOYMENT LOGIC (Phase-2B core)
# ============================================

cash = INITIAL_CAPITAL
positions = []

# Rule A → weak regime = 100% cash
if len(selected_stocks) == 0:
    deployed = 0

else:
    # Dynamic deployment pace (Rule C)
    if regime == "Strong":
        deploy_pct = 0.30
    elif regime == "Neutral":
        deploy_pct = 0.15
    else:
        deploy_pct = 0.05

    deployed = INITIAL_CAPITAL * deploy_pct
    cash -= deployed

    # Equal-weight across dynamic stock count
    per_stock_capital = deployed / len(selected_stocks)

    for s in selected_stocks:
        positions.append(
            {
                "symbol": s,
                "qty": 0,          # qty becomes real in Phase-2C with live price
                "avg_cost": 0,
                "price": 0,
                "mtm": 0,
                "weight": round(100 / len(selected_stocks), 2),
            }
        )

# ============================================
# NAV CALCULATION
# ============================================
portfolio_value = cash  # prices = 0 until live price engine (Phase-2C)

nav = {
    "capital": INITIAL_CAPITAL,
    "value": round(portfolio_value, 2),
    "return_pct": round((portfolio_value - INITIAL_CAPITAL) / INITIAL_CAPITAL * 100, 2),
    "since_text": "Since inception",
    "regime": regime,
    "chart_dates": ["Start", "Now"],
    "chart_values": [100, 100],
    "updated": datetime.utcnow().isoformat(),
}

# ============================================
# GOVERNANCE STATE
# ============================================
governance = {
    "regime": regime,
    "stable_days": model.get("stable_days", 0),
    "rebalance_required": rebalance_flag,
}

# ============================================
# DEPLOYMENT STATE
# ============================================
deployment = {
    "deployed": round(deployed, 2),
    "remaining": round(cash, 2),
    "weeks_elapsed": model.get("weeks_elapsed", 1),
    "series_labels": ["W1"],
    "series_values": [round(deployed, 2)],
}

# ============================================
# AI CIO NOTE (model-driven narrative)
# ============================================
if len(selected_stocks) == 0:
    ai_text = (
        "Model signals are weak. Portfolio remains fully in cash to preserve capital "
        "until stronger opportunities emerge."
    )
else:
    ai_text = (
        f"{len(selected_stocks)} stocks passed absolute signal filters. "
        f"Deployment paced conservatively under {regime} regime conditions. "
        "Further capital will be allocated as signal strength improves."
    )

ai = {"text": ai_text}

# ============================================
# SAVE ALL JSON
# ============================================
with open(NAV_FILE, "w") as f:
    json.dump(nav, f, indent=2)

with open(POSITIONS_FILE, "w") as f:
    json.dump(positions, f, indent=2)

with open(DEPLOY_FILE, "w") as f:
    json.dump(deployment, f, indent=2)

with open(GOV_FILE, "w") as f:
    json.dump(governance, f, indent=2)

with open(AI_FILE, "w") as f:
    json.dump(ai, f, indent=2)

print("✅ Phase-2B dynamic engine generated real portfolio state.")

# ============================================
# COMMIT TO GITHUB (for Pages visibility)
# ============================================
subprocess.run(["git", "config", "--global", "user.name", "github-actions"])
subprocess.run(["git", "config", "--global", "user.email", "actions@github.com"])

subprocess.run(["git", "add", "phase2/"])
subprocess.run(["git", "commit", "-m", "Phase-2B dynamic capital update"], check=False)
subprocess.run(["git", "push"])
