from phase2.engines.market_data import run as market_data
from phase2.engines.portfolio_construction import run as portfolio_construction
from phase2.engines.capital_deployment import run as capital_deployment
from phase2.engines.nav_mtm import run as nav_mtm


def main():
    print("=== Phase-2 Orchestrator Start ===")

    # 1. Market prices
    market_data()

    # 2. Build portfolio from model
    portfolio_construction()

    # 3. Deploy capital immediately on signal
    capital_deployment()

    # 4. Compute NAV from live prices + positions
    nav_mtm()

    print("=== Phase-2 Orchestrator Complete ===")


if __name__ == "__main__":
    main()
