from phase2.engines.market_data import run as market_data
from phase2.engines.portfolio_construction import run as portfolio_construction
from phase2.engines.capital_deployment import run as capital_deployment
from phase2.engines.position_sizing import run as position_sizing
from phase2.engines.nav_mtm import run as nav_mtm
from phase2.engines.risk_sector import run as risk_sector
from phase2.engines.governance import run as governance
from phase2.engines.watchlist_memory import run as watchlist_memory
from phase2.engines.ai_commentary import run as ai_commentary


def main():
    print("=== Phase-2 Orchestrator Start ===")

    market_data()
    portfolio_construction()
    capital_deployment()
    position_sizing()
    nav_mtm()
    risk_sector()
    governance()
    watchlist_memory()
    ai_commentary()

    print("=== Phase-2 Orchestrator Complete ===")


if __name__ == "__main__":
    main()
