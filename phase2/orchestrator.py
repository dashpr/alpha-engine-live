from phase2.engines.market_data import run as market_data
from phase2.engines.portfolio_construction import run as portfolio_construction
from phase2.engines.capital_deployment import run as capital_deployment
from phase2.engines.position_sizing import run as position_sizing
from phase2.engines.nav_mtm import run as nav_mtm
from phase2.engines.risk_sector import run as risk_sector


def main():
    print("=== Phase-2 Orchestrator Start ===")

    market_data()
    portfolio_construction()
    capital_deployment()
    position_sizing()      # 🔥 new real qty engine
    nav_mtm()
    risk_sector()

    print("=== Phase-2 Orchestrator Complete ===")


if __name__ == "__main__":
    main()
