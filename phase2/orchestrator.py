"""
PHASE-2 ORCHESTRATOR (FINAL STABLE)
-----------------------------------

Runs engines and generates dashboard JSON.
No git operations inside Python.
GitHub Actions handles commit automatically.
"""

from phase2.signal_engine import build_signals
from phase2.dashboard_builder import build_dashboard


def main():
    print("=== PHASE-2 ORCHESTRATOR START ===")

    # Step 1: Build signals
    build_signals()

    # Step 2: Build dashboard JSON
    build_dashboard()

    print("=== PHASE-2 COMPLETE ===")


if __name__ == "__main__":
    main()
