"""
FINAL Regime Detection Model — Production Safe
• Handles HMM numerical failures
• Deterministic fallback
• Phase-3 backward compatible
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from hmmlearn.hmm import GaussianHMM


class RegimeDetector:
    def __init__(self, n_states: int = 3):
        self.n_states = n_states
        self.model: GaussianHMM | None = None
        self.fallback_mode = False

    # --------------------------------------------------
    # FEATURE MATRIX
    # --------------------------------------------------

    def _prepare_X(self, df: pd.DataFrame) -> np.ndarray:
        X = df[["ret_1d", "vol_20d", "mom_20_60"]].copy()

        X = X.replace([np.inf, -np.inf], np.nan).dropna()

        if len(X) < 50:
            raise ValueError("Not enough data")

        # tiny noise for stability
        X = X + np.random.normal(0, 1e-6, size=X.shape)

        return X.values

    # --------------------------------------------------
    # FIT (Fail-safe)
    # --------------------------------------------------

    def fit(self, df: pd.DataFrame) -> None:
        try:
            X = self._prepare_X(df)

            model = GaussianHMM(
                n_components=self.n_states,
                covariance_type="full",
                n_iter=200,
                random_state=42,
            )

            model.fit(X)

            # Validate probabilities & covariance
            if (
                not np.isfinite(model.startprob_).all()
                or np.isnan(model.transmat_).any()
                or np.isnan(model.covars_).any()
            ):
                raise ValueError("Invalid trained HMM")

            self.model = model
            self.fallback_mode = False

        except Exception:
            # ⭐ Institutional fail-safe
            self.model = None
            self.fallback_mode = True

    # --------------------------------------------------
    # DAILY PROBABILITIES
    # --------------------------------------------------

    def predict_daily_probabilities(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.fallback_mode or self.model is None:
            return self._fallback_probabilities(df)

        try:
            X = self._prepare_X(df)
            probs = self.model.predict_proba(X)
        except Exception:
            return self._fallback_probabilities(df)

        out = df.loc[df.index[-len(probs):], ["date"]].copy()

        for i in range(self.n_states):
            out[f"regime_{i}"] = probs[:, i]

        return out.reset_index(drop=True)

    # --------------------------------------------------
    # WEEKLY CONFIRMED REGIME (Phase-3 compatibility)
    # --------------------------------------------------

    def weekly_confirmed_regime(self, daily_probs: pd.DataFrame) -> pd.DataFrame:
        df = daily_probs.copy()
        df["week"] = pd.to_datetime(df["date"]).dt.to_period("W").apply(lambda r: r.start_time)

        regime_cols = [c for c in df.columns if c.startswith("regime_")]

        weekly = (
            df.groupby("week")[regime_cols]
            .mean()
            .reset_index()
            .rename(columns={"week": "date"})
        )

        return weekly

    # --------------------------------------------------
    # DETERMINISTIC FALLBACK
    # --------------------------------------------------

    def _fallback_probabilities(self, df: pd.DataFrame) -> pd.DataFrame:
        vol = df["vol_20d"].ffill()

        q = vol.quantile([0.33, 0.66]).values
        regimes = np.zeros((len(vol), self.n_states))

        for i, v in enumerate(vol):
            if v <= q[0]:
                regimes[i, 0] = 1
            elif v <= q[1]:
                regimes[i, 1] = 1
            else:
                regimes[i, 2] = 1

        out = df[["date"]].copy()

        for i in range(self.n_states):
            out[f"regime_{i}"] = regimes[:, i]

        return out.reset_index(drop=True)
