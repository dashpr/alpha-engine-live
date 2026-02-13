import pandas as pd
import numpy as np
from hmmlearn.hmm import GaussianHMM


class RegimeDetector:
    def __init__(self, n_states: int = 3):
        self.n_states = n_states
        self.model = None
        self.fitted = False

    def _prepare(self, df: pd.DataFrame):
        cols = ["ret_1d", "vol_20d", "mom_20_60"]
        if not all(c in df.columns for c in cols):
            return None
        X = df[cols].dropna()
        return X if len(X) >= 50 else None

    def fit(self, df: pd.DataFrame):
        X = self._prepare(df)

        if X is None:
            self.fitted = False
            return

        try:
            self.model = GaussianHMM(
                n_components=self.n_states,
                covariance_type="diag",  # ⭐ stability fix
                n_iter=100,
                random_state=42,
            )
            self.model.fit(X.values)
            self.fitted = True
        except Exception:
            self.fitted = False

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
