"""
FINAL PHASE-5 ENTRYPOINT
Works with hyphen folder names (ai-pms)
No package import required.
Permanent production design.
"""

import sys
from pathlib import Path

# -------------------------------------------------
# BOOTSTRAP PROJECT ROOT INTO PYTHON PATH (ONCE)
# -------------------------------------------------
CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[2]  # repo root

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# -------------------------------------------------
# NOW SAFE TO IMPORT INTERNAL MODULES
# -------------------------------------------------
from ai-pms.phase5_frozen.backtest import run_backtest  # type: ignore
from ai-pms.phase5_frozen.governance import save_outputs  # type: ignore


def main():
    equity_curve = run_backtest()
    save_outputs(equity_curve)
    print("✅ Phase-5 frozen backtest complete.")


if __name__ == "__main__":
    main()
