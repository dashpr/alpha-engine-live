import os
import pandas as pd
from pathlib import Path

from src.cio_ai import CIOAI


REGIME_PATH = Path("data/output/regime_state.parquet")
RISK_PATH = Path("data/output/risk_state.parquet")
WEIGHTS_PATH = Path("data/output/final_weights.parquet")

REPORT_OUT = Path("data/output/cio_report.txt")


def main():
    api_key = os.environ.get("OPENAI_API_KEY")

    regime = pd.read_parquet(REGIME_PATH)
    risk = pd.read_parquet(RISK_PATH)
    weights = pd.read_parquet(WEIGHTS_PATH)

    cio = CIOAI(api_key=api_key)
    report = cio.generate_report(regime, risk, weights)

    REPORT_OUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT_OUT.write_text(report)

    print("✅ CIO AI report generated")
    print(f"Report saved to: {REPORT_OUT}")


if __name__ == "__main__":
    main()
