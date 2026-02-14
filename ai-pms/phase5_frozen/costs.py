from .config import BROKERAGE, SLIPPAGE, IMPACT


def transaction_cost(trade_value: float) -> float:
    return trade_value * (BROKERAGE + SLIPPAGE + IMPACT)
