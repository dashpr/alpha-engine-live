"""
PHASE-4 STEP-5
Capital Allocation & Deployment Bridge (Research-Aggressive Mode)

Purpose:
- Translate research NAV into deployable capital curve
- Implement aggressive scaling rules
- Enforce soft drawdown protection

Inputs:
    data/processed/performance_timeseries.parquet

Outputs:
    data/processed/deployment_plan.parquet
    data/processed/deployment_summary.json
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


TS_PATH = Path("data/processed/performance_timeseries.parquet")
PLAN_OUT = Path("data/processed/deployment_plan.parquet")
SUMMARY_OUT = Path("data/processed/deployment_summary.json")

BASE_CAPITAL = 200_000
SCALE_MULTIPLIERS = [1, 5, 10, 25, 50]  # research-aggressive ladder
DRAWDOWN_SOFT_LIMIT = -0.20  # pause scaling beyond -20%


class CapitalAllocationEngine:
    """Aggressive research-mode capital scaling simulator."""

    def run(self) -> pd.DataFrame:
        ts = self._load_timeseries()
        plan = self._build_scaling_plan(ts)
        self._save_plan(plan)
        self._save_summary(plan)
        return plan

    # ---------------- LOAD ----------------

    def _load_timeseries(self) -> pd.DataFrame:
        if not TS_PATH.exists():
            raise FileNotFoundError("performance_timeseries.parquet missing. Run Step-4.")
        return pd.read_parquet(TS_PATH).sort_values("date")

    # ---------------- BUILD PLAN ----------------

    def _build_scaling_plan(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        df["scale_level"] = 0
        df["deployable_capital"] = BASE_CAPITAL

        level = 0

        for i in range(1, len(df)):
            dd = df.loc[i, "drawdown"]

            # pause scaling on deep drawdown
            if dd < DRAWDOWN_SOFT_LIMIT:
                df.loc[i, "scale_level"] = level
                df.loc[i, "deployable_capital"] = BASE_CAPITAL * SCALE_MULTIPLIERS[level]
                continue

            # scale up on new equity highs
            if df.loc[i, "nav"] > df.loc[: i - 1, "nav"].max():
                level = min(level + 1, len(SCALE_MULTIPLIERS) - 1)

            df.loc[i, "scale_level"] = level
            df.loc[i, "deployable_capital"] = BASE_CAPITAL * SCALE_MULTIPLIERS[level]

        return df

    # ---------------- SAVE ----------------

    def _save_plan(self, df: pd.DataFrame) -> None:
        PLAN_OUT.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(PLAN_OUT, index=False)
        print(f"✓ deployment_plan.parquet created → {PLAN_OUT}")

    def _save_summary(self, df: pd.DataFrame) -> None:
        final_level = int(df["scale_level"].iloc[-1])
        final_capital = float(df["deployable_capital"].iloc[-1])

        summary = {
            "base_capital": BASE_CAPITAL,
            "final_scale_level": final_level,
            "final_deployable_capital": final_capital,
        }

        SUMMARY_OUT.parent.mkdir(parents=True, exist_ok=True)
        with open(SUMMARY_OUT, "w") as f:
            json.dump(summary, f, indent=2)

        print("✓ Deployment summary saved →", SUMMARY_OUT)
        print(summary)


# ---------------- CLI ----------------


def main():
    engine = CapitalAllocationEngine()
    plan = engine.run()

    print("Rows:", len(plan))
    print("Final deployable capital:", plan["deployable_capital"].iloc[-1])


if __name__ == "__main__":
    main()
