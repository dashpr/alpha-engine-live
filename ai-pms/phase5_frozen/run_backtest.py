"""
FINAL PHASE-5 ENTRYPOINT
Works with hyphen folder names (ai-pms)
No invalid imports
CI/CD safe
Permanent solution
"""

import sys
from pathlib import Path
import importlib.util


# -------------------------------------------------
# Resolve project paths
# -------------------------------------------------
CURRENT_FILE = Path(__file__).resolve()
PHASE_DIR = CURRENT_FILE.parent
PROJECT_ROOT = PHASE_DIR.parent.parent


# -------------------------------------------------
# Helper to load module from file path
# -------------------------------------------------
def load_module(module_name: str, file_path: Path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


# -------------------------------------------------
# Load required internal modules explicitly
# -------------------------------------------------
backtest_module = load_module(
    "phase5_backtest",
    PHASE_DIR / "backtest.py",
)

governance_module = load_module(
    "phase5_governance",
    PHASE_DIR / "governance.py",
)


run_backtest = backtest_module.run_backtest
save_outputs = governance_module.save_outputs


# -------------------------------------------------
# Main execution
# -------------------------------------------------
def main():
    equity_curve = run_backtest()
    save_outputs(equity_curve)
    print("✅ Phase-5 frozen backtest complete.")


if __name__ == "__main__":
    main()
