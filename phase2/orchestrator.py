from phase2.signal_engine import build_signals
from phase2.portfolio_constructor import build_portfolio
from phase2.risk_engine import run as risk_run
from phase2.event_commentary_engine import run as event_run


def main():
    print("=== NEW PHASE-2 ORCHESTRATOR START ===")

    build_signals()
    build_portfolio()
    risk_run()
    event_run()

    print("=== NEW PHASE-2 ORCHESTRATOR COMPLETE ===")


if __name__ == "__main__":
    main()
