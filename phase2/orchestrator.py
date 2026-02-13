"""
PHASE-2 INSTITUTIONAL ORCHESTRATOR
---------------------------------

Runs full allocator pipeline and produces dashboard JSON.
"""

from phase2.signal_engine import build_signals
from phase2.dashboard_builder import build_dashboard


def main():
    print("=== NEW PHASE-2 ORCHESTRATOR START ===")

    # Step-1: Build signals
    build_signals()

    # Step-2: Build dashboard JSON
    build_dashboard()

    print("=== PHASE-2 RUN COMPLETE ===")


if __name__ == "__main__":
    main()
