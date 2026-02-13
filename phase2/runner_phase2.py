import json
import os
import subprocess
from datetime import datetime

# ==============================
# CONFIG
# ==============================
PHASE2_DIR = "phase2"
NAV_FILE = f"{PHASE2_DIR}/nav.json"
DEPLOY_FILE = f"{PHASE2_DIR}/deployment.json"
POSITIONS_FILE = f"{PHASE2_DIR}/positions.json"
GOV_FILE = f"{PHASE2_DIR}/governance.json"
AI_FILE = f"{PHASE2_DIR}/ai.json"

CAPITAL = 200000


# ==============================
# ENSURE DIR
# ==============================
os.makedirs(PHASE2_DIR, exist_ok=True)


# ==============================
# 1️⃣ NAV ENGINE
# ==============================
nav_data = {
    "capital": CAPITAL,
    "value": CAPITAL,
    "return_pct": 0.0,
    "updated": datetime.utcnow().isoformat()
}

with open(NAV_FILE, "w") as f:
    json.dump(nav_data, f, indent=2)


# ==============================
# 2️⃣ DEPLOYMENT ENGINE
# ==============================
deployment = {
    "deployed": 0,
    "remaining": CAPITAL,
    "weeks_elapsed": 1,
    "drawdown": 0.0
}

with open(DEPLOY_FILE, "w") as f:
    json.dump(deployment, f, indent=2)


# ==============================
# 3️⃣ POSITIONS ENGINE
# ==============================
positions = []

with open(POSITIONS_FILE, "w") as f:
    json.dump(positions, f, indent=2)


# ==============================
# 4️⃣ GOVERNANCE ENGINE
# ==============================
governance = {
    "regime": "Neutral",
    "stable_days": 0,
    "rebalance_required": False
}

with open(GOV_FILE, "w") as f:
    json.dump(governance, f, indent=2)


# ==============================
# 5️⃣ AI ENGINE
# ==============================
ai = {
    "summary": "System initialized. Awaiting first capital deployment."
}

with open(AI_FILE, "w") as f:
    json.dump(ai, f, indent=2)


print("✅ Phase-2 JSON files generated.")


# ==============================
# 6️⃣ AUTO-COMMIT TO GITHUB
# ==============================
subprocess.run(["git", "config", "--global", "user.name", "github-actions"])
subprocess.run(["git", "config", "--global", "user.email", "actions@github.com"])

subprocess.run(["git", "add", "phase2/"])
subprocess.run(["git", "commit", "-m", "Update Phase-2 dashboard data"], check=False)
subprocess.run(["git", "push"])
