"""
PHASE-4 STEP-6
Investor Reporting & PMS Dashboard Data Layer (GitHub production version)

Purpose:
- Generate investor-grade performance tables
- Build monthly factsheet metrics
- Prepare NAV + capital curves for dashboard
- Create downloadable report artifacts

Inputs:
    data/processed/performance_timeseries.parquet
    data/processed/deployment_plan.parquet

Outputs:
    data/processed/investor_monthly_table.parquet
    data/processed/investor_summary.json
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


TS_PATH = Path("data/processed/performance_timeseries.parquet")
PLAN_PATH = Path("data/processed/deployment_plan.parquet")

MONTHLY_OUT = Path("data/processed/investor_monthly_table.parquet")
SUMMARY_OUT = Path("data/processed/investor_summary.json")


class InvestorReportingEngine:
    """Produces investor-facing PMS performance artifacts."""

    def run(self) -> pd.DataFrame:
        ts = self._load_timeseries()
        plan = self._load_plan()
        monthly = self._build_monthly_table(ts, plan)
        self._save_monthly(monthly)
        self._save_summary(monthly)
        return monthly

    # ---------------- LOAD ----------------

    def _load_timeseries(self) -> pd.DataFrame:
        if not TS_PATH.exists():
            raise FileNotFoundError("performance_timeseries.parquet missing. Run Step-4.")
        return pd.read_parquet(TS_PATH).sort_values("date")

    def _load_plan(self) -> pd.DataFrame:
        if not PLAN_PATH.exists():
            raise FileNotFoundError("deployment_plan.parquet missing. Run Step-5.")
        return pd.read_parquet(PLAN_PATH).sort_values("date")

    # ---------------- MONTHLY BUILD ----------------

    def _build_monthly_table(self, ts: pd.DataFrame, plan: pd.DataFrame) -> pd.DataFrame:
        df = ts.merge(plan[["date", "deployable_capital"]], on="date", how="left")

        df["month"] = pd.to_datetime(df["date"]).dt.to_period("M")

        monthly = (
            df.groupby("month")
            .agg(
                nav_start=("nav", "first"),
                nav_end=("nav", "last"),
                capital_end=("deployable_capital", "last"),
                max_drawdown=("drawdown", "min"),
                avg_sharpe=("rolling_sharpe", "mean"),
            )
            .reset_index()
        )

        monthly["monthly_return"] = monthly["nav_end"] / monthly["nav_start"] - 1
        monthly["month"] = monthly["month"].astype(str)

        return monthly

    # ---------------- SAVE MONTHLY ----------------

    def _save_monthly(self, df: pd.DataFrame) -> None:
        MONTHLY_OUT.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(MONTHLY_OUT, index=False)
        print(f"✓ investor_monthly_table.parquet created → {MONTHLY_OUT}")

    # ---------------- SUMMARY ----------------

    def _save_summary(self, df: pd.DataFrame) -> None:
        total_return = df["nav_end"].iloc[-1] / df["nav_start"].iloc[0] - 1
        months = len(df)

        cagr = (1 + total_return) ** (12 / months) - 1 if months > 0 else 0
        avg_sharpe = float(df["avg_sharpe"].mean())
        worst_month = float(df["monthly_return"].min())
        final_capital = float(df["capital_end"].iloc[-1])

        summary = {
            "months": int(months),
            "total_return": float(total_return),
            "cagr": float(cagr),
            "average_sharpe": avg_sharpe,
            "worst_month": worst_month,
            "final_deployable_capital": final_capital,
        }

        SUMMARY_OUT.parent.mkdir(parents=True, exist_ok=True)
        with open(SUMMARY_OUT, "w") as f:
            json.dump(summary, f, indent=2)

        print("✓ Investor summary saved →", SUMMARY_OUT)
        print(summary)


# ---------------- CLI ----------------


def main():
    engine = InvestorReportingEngine()
    monthly = engine.run()

    print("Months:", len(monthly))
    print("Final capital:", monthly["capital_end"].iloc[-1])


if __name__ == "__main__":
    main()
