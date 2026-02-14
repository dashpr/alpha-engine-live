from .data_loader import load_prices
from .features import build_features
from .alpha import compute_alpha
from .portfolio import rebalance_portfolio


def run_backtest():
    df = load_prices()
    df = build_features(df)
    df = compute_alpha(df)

    equity_curve = rebalance_portfolio(df)
    return equity_curve
