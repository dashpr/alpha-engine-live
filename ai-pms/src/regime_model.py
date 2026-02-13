import pandas as pd
import numpy as np
from hmmlearn.hmm import GaussianHMM


class RegimeDetector:
    """
    Hidden-Markov-Model based regime detector.

    Safe for CI:
    - Handles insufficient data
    - Never crashes pipeline
    - Falls back to NEUTRAL regime
    """

    def __init__(self, n_states: int = 3):
        self.n_states = n_states
        self.model = GaussianHMM(
            n_components=n_states,
            covariance_type="full",
            n_iter=200,
            random_state=42,
        )
        self.fitted = False

    def _prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        cols = ["ret_1d", "vol_20d", "mom_20_60"]

        if not all(c in df.columns for c in cols):
            return pd.DataFrame()

        return df[cols].dropna()

    def fit(self, df: pd.DataFrame):
        X = self._prepare_features(df)

        # ⭐ CRITICAL SAFETY CHECK
        if len(X) < 30:
            print("⚠️ Not enough data for HMM regime training. Using NEUTRAL fallback.")
            self.fitted = False
            return

        self.model.fit(X.values)
        self.fitted = True

    def predict_daily_probabilities(self, df: pd.DataFrame) -> pd.DataFrame:
        X = self._prepare_features(df)

        if not self.fitted or len(X) == 0:
            # Return neutral probabilities
            dates = df["date"].dropna().unique()
            neutral = pd.DataFrame({
                "date": dates,
                "regime_0_prob": 1.0,
                "regime_1_prob": 0.0,
                "regime_2_prob": 0.0,
            })
            return neutral

        probs = self.model.predict_proba(X.values)

        prob_df = pd.DataFrame(
            probs,
            columns=[f"regime_{i}_prob" for i in range(self.n_states)],
        )

        prob_df["date"] = df.loc[X.index, "date"].values
        return prob_df

    def weekly_confirmed_regime(self, prob_df: pd.DataFrame) -> pd.DataFrame:
        prob_df = prob_df.copy()
        prob_df["week"] = pd.to_datetime(prob_df["date"]).dt.to_period("W")

        weekly = (
            prob_df.groupby("week")
            .mean(numeric_only=True)
        )

        weekly["confirmed_regime"] = weekly.idxmax(axis=1)
        return weekly.reset_index()
