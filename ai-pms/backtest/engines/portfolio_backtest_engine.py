import pandas as pd
import numpy as np


class PortfolioBacktestEngine:
    """
    Institutional Regime-Adaptive Portfolio Backtester
    Output contract (STRICT):
        date | equity | returns | drawdown
    """

    def __init__(
        self,
        initial_capital: float = 200000,
        transaction_cost: float = 0.0015,   # 15 bps realistic
        slippage: float = 0.0005,           # 5 bps
        cash_buffer: float = 0.05,          # 5% defensive cash
    ):
        self.initial_capital = initial_capital
        self.transaction_cost = transaction_cost
        self.slippage = slippage
        self.cash_buffer = cash_buffer

    # ---------------------------------------------------------
    # Regime → allocation logic (INSTITUTIONAL CORE)
    # ---------------------------------------------------------
    def _regime_weights(self, regime: str):
        """
        Returns allocation weights across alpha sleeves.
        """
        if regime == "bull":
            return {"momentum": 0.7, "mean_reversion": 0.2, "ml_factor": 0.1}

        if regime == "sideways":
            return {"momentum": 0.3, "mean_reversion": 0.5, "ml_factor": 0.2}

        if regime == "bear":
            return {"momentum": 0.1, "mean_reversion": 0.2, "ml_factor": 0.2, "cash": 0.5}

        # fallback defensive
        return {"cash": 1.0}

    # ---------------------------------------------------------
    # Core backtest
    # ---------------------------------------------------------
    def run(self, alpha_df: pd.DataFrame) -> pd.DataFrame:
        """
        alpha_df REQUIRED columns:
        date | ret | model | regime
        """

        required = {"date", "ret", "model", "regime"}
        if not required.issubset(alpha_df.columns):
            raise ValueError(f"Alpha DF must contain columns: {required}")

        alpha_df = alpha_df.sort_values("date")

        equity = self.initial_capital
        equity_curve = []

        for date, day_df in alpha_df.groupby("date"):

            regime = day_df["regime"].iloc[0]
            weights = self._regime_weights(regime)

            daily_return = 0.0

            for model, w in weights.items():

                if model == "cash":
                    continue

                model_ret = day_df.loc[day_df["model"] == model, "ret"]

                if len(model_ret) > 0:
                    daily_return += w * model_ret.mean()

            # apply institutional frictions
            cost = self.transaction_cost + self.slippage
            daily_return -= cost

            # update equity
            equity *= (1 + daily_return)

            equity_curve.append(
                {
                    "date": date,
                    "equity": equity,
                }
            )

        eq = pd.DataFrame(equity_curve)

        # -----------------------------------------------------
        # STRICT METRICS FIELDS (fixes all crashes)
        # -----------------------------------------------------
        eq["returns"] = eq["equity"].pct_change().fillna(0)
        eq["drawdown"] = eq["equity"] / eq["equity"].cummax() - 1

        return eq
