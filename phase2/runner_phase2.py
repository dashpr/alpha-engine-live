import json
import os
from datetime import datetime
import subprocess

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PHASE2_DIR = os.path.join(BASE_DIR, "phase2")


def save_json(name, data):
    path = os.path.join(PHASE2_DIR, name)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def generate_mock_data():
    """
    Phase-2A safe deterministic data
    so dashboard NEVER shows blank.
    """

    nav = {
        "capital": 200000,
        "value": 200000,
        "return_pct": 0.0,
        "since_text": "Since inception",
        "regime": "Neutral",
        "chart_dates": ["Start", "Now"],
        "chart_values": [100, 100],
    }

    holdings = [
        {
            "symbol": "RELIANCE",
            "weight": 12,
            "qty": 0,
            "avg_cost": 0,
            "price": 0,
            "mtm": 0,
        },
        {
            "symbol": "INFY",
            "weight": 10,
            "qty": 0,
            "avg_cost": 0,
            "price": 0,
            "mtm": 0,
        },
    ]

    sectors = [
        {"sector": "Energy", "pct": 30},
        {"sector": "IT", "pct": 20},
        {"sector": "Financials", "pct": 18},
    ]

    risk = {"cagr": 0, "max_drawdown": 0, "sharpe": 0}

    deployment = {
        "deployed": 0,
        "remaining": 200000,
        "weeks_elapsed": 1,
        "series_labels": ["W1"],
        "series_values": [0],
    }

    ai = {
        "text": "Phase-2A initialized. Capital deployment will begin as signals confirm. Regime neutral."
    }

    events = {"highlights": ["System initialized", "Awaiting first deployment signal"]}

    save_json("nav.json", nav)
    save_json("holdings.json", holdings)
    save_json("sectors.json", sectors)
    save_json("risk.json", risk)
    save_json("deployment.json", deployment)
    save_json("ai.json", ai)
    save_json("events.json", events)


def commit_and_push():
    """
    CRITICAL:
    GitHub Pages shows data ONLY if committed.
    """
    try:
        subprocess.run(["git", "config", "--global", "user.name", "alpha-bot"])
        subprocess.run(
            ["git", "config", "--global", "user.email", "alpha@engine.ai"]
        )

        subprocess.run(["git", "add", "phase2/*.json"], shell=True)
        subprocess.run(["git", "commit", "-m", "auto: phase2 data update"], shell=True)
        subprocess.run(["git", "push"], shell=True)

    except Exception as e:
        print("Git push skipped:", e)


def main():
    print("Phase-2 runner started:", datetime.now())

    os.makedirs(PHASE2_DIR, exist_ok=True)

    generate_mock_data()

    commit_and_push()

    print("Phase-2 data generated and pushed successfully.")


if __name__ == "__main__":
    main()
