import pandas as pd
from .config import PORTFOLIO_SIZE, MIN_REBALANCE_WEIGHT_CHANGE
from .costs import transaction_cost


def rebalance_portfolio(df: pd.DataFrame):
    dates = sorted(df["date"].unique())

    equity = 1.0
    equity_curve = []

    current_weights = {}

    for date in dates:
        day = df[df["date"] == date].sort_values("alpha_score", ascending=False)
        selected = day.head(PORTFOLIO_SIZE)

        target_weight = 1.0 / PORTFOLIO_SIZE
        new_weights = {t: target_weight for t in selected["ticker"]}

        turnover = sum(abs(new_weights.get(t, 0) - current_weights.get(t, 0)) for t in set(new_weights) | set(current_weights))

        cost = transaction_cost(turnover * equity)
        equity -= cost

        daily_ret = selected["ret_5d"].mean()
        equity *= (1 + daily_ret)

        equity_curve.append({"date": date, "equity": equity})
        current_weights = new_weights

    return pd.DataFrame(equity_curve)
