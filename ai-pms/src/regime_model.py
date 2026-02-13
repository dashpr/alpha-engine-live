import pandas as pd
import numpy as np
from hmmlearn.hmm import GaussianHMM


class RegimeDetector:
    """
    Institutional regime detection engine.

    Features:
    - HMM with diagonal covariance for numerical stability
    - Cold-start safe (never crashes)
    - Produces daily probabilities
    - Aggregates into weekly confirmed regime
    """

    def __init__(self, n_states: int = 3):
        self.n_states = n_states
        self.model = None
        self.fitted = False

    # --------------------------------------------------
    # Data preparation
    # --------------------------------------------------

    def _prepare(self, df: pd.DataFrame):
        cols = ["ret_1d", "vol_20d", "mom_20_60"]

        if not all(c in df.columns for c in cols):
            return None

        X = df[cols].dropna()

        # Need minimum history for HMM stability
        if len(X) < 50:
            return None

        return X

    # --------------------------------------------------
    # Model fitting
    # --------------------------------------------------

    def fit(self, df: pd.DataFrame):
        X = self._prepare(df)

        if X is None:
            self.fitted = False
            return

        try:
            self.model = GaussianHMM(
                n_components=self.n_states,
                covariance_type="diag",   # ⭐ stability
                n_iter=100,
                random_state=42,
            )

            self.model.fit(X.values)
            self.fitted = True

        except Exception:
            # Cold-start or numerical instability → stay unfitted
            self.fitted = False

    # --------------------------------------------------
    # Daily regime probabilities
    # --------------------------------------------------

    def predict_daily_probabilities(self, df: pd.DataFrame):
        if not self.fitted:
            return pd.DataFrame()

        X = self._prepare(df)
        if X is None:
            return pd.DataFrame()

        probs = self.model.predict_proba(X.values)

        out = pd.DataFrame(
            probs,
            columns=[f"regime_{i}_prob" for i in range(self.n_states)],
        )

        out["date"] = df.loc[X.index, "date"].values

        return out

    # --------------------------------------------------
    # ⭐ Weekly confirmed regime (REQUIRED BY PIPELINE)
    # --------------------------------------------------

    def weekly_confirmed_regime(self, daily_probs: pd.DataFrame):
        """
        Convert daily probabilities → weekly confirmed regime.

        Rules:
        - Average probabilities within each week
        - Choose regime with highest mean probability
        - Cold-start safe (returns NEUTRAL)
        """

        if daily_probs is None or len(daily_probs) == 0:
            return pd.DataFrame(
                [{"week": None, "confirmed_regime": "NEUTRAL"}]
            )

        df = daily_probs.copy()

        df["date"] = pd.to_datetime(df["date"])
        df["week"] = df["date"].dt.to_period("W").astype(str)

        prob_cols = [c for c in df.columns if c.startswith("regime_")]

        weekly = (
            df.groupby("week")[prob_cols]
            .mean()
            .reset_index()
        )

        # Determine winning regime
        weekly["confirmed_regime"] = (
            weekly[prob_cols]
            .idxmax(axis=1)
            .str.replace("_prob", "")
        )

        return weekly[["week", "confirmed_regime"]]
