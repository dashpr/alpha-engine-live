from phase2.engines.market_data import run as market_data
from phase2.engines.nav_mtm import run as nav_mtm


def main():
    print("=== Phase-2 Orchestrator Start ===")

    # Engine-1
    market_data()

    # Engine-4 (NAV depends on prices)
    nav_mtm()

    print("=== Phase-2 Orchestrator Complete ===")


if __name__ == "__main__":
    main()
