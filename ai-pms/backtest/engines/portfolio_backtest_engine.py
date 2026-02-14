import pandas as pd
import numpy as np


class PortfolioBacktestEngine:
    """
    Institutional weekly portfolio simulator.
    Risk-parity weighting + real costs.
    """

    def __init__(
        self,
        initial_capital=200_000,
        brokerage=0.0003,
        slippage=0.0005,
        stt=0.00025,
        cash_drag=0.03,
    ):
        self.initial_capital = initial_capital
        self.cost = brokerage + slippage + stt
        self.cash_drag = cash_drag / 252

    # -----------------------------------------------------
    def _risk_parity_weights(self, df: pd.DataFrame) -> pd.DataFrame:
        vol = df.groupby("symbol")["ret"].std()
        inv_vol = 1 / (vol + 1e-6)
        weights = inv_vol / inv_vol.sum()

        df["weight"] = df["symbol"].map(weights)
        return df

    # -----------------------------------------------------
    def run(self, alpha_df: pd.DataFrame) -> pd.DataFrame:
        required = {"date", "symbol", "ret", "model"}
        if not required.issubset(alpha_df.columns):
            raise ValueError(f"Alpha DF must contain columns: {required}")

        print(f"💼 Portfolio simulation → {alpha_df['model'].iloc[0]}")

        equity = self.initial_capital
        equity_curve = []

        for date, group in alpha_df.groupby("date"):

            group = self._risk_parity_weights(group)

            pnl = (group["weight"] * group["ret"]).sum()

            # apply costs + cash drag
            pnl -= self.cost
            pnl -= self.cash_drag

            equity *= (1 + pnl)

            equity_curve.append({"date": date, "equity": equity})

        return pd.DataFrame(equity_curve)
