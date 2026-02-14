from .backtest import run_backtest
from .governance import save_outputs


def main():
    equity_curve = run_backtest()
    save_outputs(equity_curve)
    print("Phase-5 backtest complete. Output saved.")


if __name__ == "__main__":
    main()
