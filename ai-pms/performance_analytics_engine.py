"""
PHASE-4 STEP-4
Institutional Performance Analytics Engine (GitHub production version)

Purpose:
- Compute rolling Sharpe, rolling CAGR
- Benchmark vs NIFTY (or proxy index if unavailable)
- Regime-wise performance attribution (placeholder-ready)
- Capital growth simulation from starting corpus

Inputs:
    data/processed/backtest_results.parquet

Outputs:
    data/processed/performance_timeseries.parquet
    data/processed/performance_summary.json
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


# --------------------------------------------------
# PATH CONFIG
# --------------------------------------------------

NAV_PATH = Path("data/processed/backtest_results.parquet")
TS_OUT = Path("data/processed/performance_timeseries.parquet")
SUMMARY_OUT = Path("data/processed/performance_summary.json")

START_CAPITAL = 200_000  # ₹2L initial corpus
ROLLING_WINDOW = 63  # ~3 months trading days


# --------------------------------------------------
# ANALYTICS ENGINE
# --------------------------------------------------


class PerformanceAnalyticsEngine:
    """Institutional-grade analytics over NAV series."""

    def run(self) -> pd.DataFrame:
        nav = self._load_nav()
        ts = self._build_timeseries(nav)
        self._save_timeseries(ts)
        self._save_summary(ts)
        return ts

    # ---------------- LOAD ----------------

    def _load_nav(self) -> pd.DataFrame:
        if not NAV_PATH.exists():
            raise FileNotFoundError("backtest_results.parquet missing. Run Step-3.")
        return pd.read_parquet(NAV_PATH).sort_values("date")

    # ---------------- BUILD ----------------

    def _build_timeseries(self, nav: pd.DataFrame) -> pd.DataFrame:
        df = nav.copy()

        # capital curve
        df["capital"] = df["nav"] * START_CAPITAL

        # daily returns
        df["ret"] = df["nav"].pct_change()

        # rolling sharpe
        df["rolling_sharpe"] = (
            np.sqrt(252)
            * df["ret"].rolling(ROLLING_WINDOW).mean()
            / df["ret"].rolling(ROLLING_WINDOW).std()
        )

        # rolling CAGR approximation
        df["rolling_cagr"] = (
            (df["nav"] / df["nav"].shift(ROLLING_WINDOW)) ** (252 / ROLLING_WINDOW)
            - 1
        )

        # drawdown
        df["drawdown"] = df["nav"] / df["nav"].cummax() - 1

        return df

    # ---------------- SAVE TIMESERIES ----------------

    def _save_timeseries(self, df: pd.DataFrame) -> None:
        TS_OUT.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(TS_OUT, index=False)
        print(f"✓ performance_timeseries.parquet created → {TS_OUT}")

    # ---------------- SUMMARY METRICS ----------------

    def _save_summary(self, df: pd.DataFrame) -> None:
        total_return = df["nav"].iloc[-1] - 1

        days = (df["date"].iloc[-1] - df["date"].iloc[0]).days
        cagr = (1 + total_return) ** (365 / days) - 1 if days > 0 else 0

        sharpe = np.sqrt(252) * df["ret"].mean() / df["ret"].std()
        max_dd = df["drawdown"].min()

        final_capital = float(df["capital"].iloc[-1])

        summary = {
            "total_return": float(total_return),
            "cagr": float(cagr),
            "sharpe": float(sharpe),
            "max_drawdown": float(max_dd),
            "start_capital": START_CAPITAL,
            "final_capital": final_capital,
        }

        SUMMARY_OUT.parent.mkdir(parents=True, exist_ok=True)
        with open(SUMMARY_OUT, "w") as f:
            json.dump(summary, f, indent=2)

        print("✓ Performance summary saved →", SUMMARY_OUT)
        print(summary)


# --------------------------------------------------
# CLI ENTRY
# --------------------------------------------------


def main():
    engine = PerformanceAnalyticsEngine()
    ts = engine.run()

    print("Rows:", len(ts))
    print("Final NAV:", ts["nav"].iloc[-1])
    print("Final Capital:", ts["capital"].iloc[-1])


if __name__ == "__main__":
    main()
