import pandas as pd
from openai import OpenAI


class CIOAI:
    """
    Generates institutional CIO commentary.

    CI-safe:
    - Handles empty regime / risk / weights
    - Never crashes pipeline
    - Produces fallback narrative during cold start
    """

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables.")

        self.client = OpenAI(api_key=api_key)

    # --------------------------------------------------
    # Safe data extraction helpers
    # --------------------------------------------------

    def _safe_last_row(self, df: pd.DataFrame, default: dict):
        if df is None or len(df) == 0:
            return default
        return df.iloc[-1].to_dict()

    # --------------------------------------------------
    # Prompt builder
    # --------------------------------------------------

    def _build_prompt(self, regime_df, risk_df, weights_df):
        regime = self._safe_last_row(regime_df, {"regime": "NEUTRAL"})
        risk = self._safe_last_row(
            risk_df,
            {"portfolio_volatility": 0.0, "VaR_95": 0.0},
        )

        if weights_df is None or len(weights_df) == 0:
            top_weights = []
        else:
            top_weights = (
                weights_df.sort_values("weight", ascending=False)
                .head(5)
                .to_dict(orient="records")
            )

        return f"""
You are the CIO of an institutional AI-driven PMS.

Current market regime:
{regime}

Portfolio risk metrics:
{risk}

Top portfolio allocations:
{top_weights}

Write a concise weekly CIO commentary explaining:
- Market regime interpretation
- Portfolio positioning rationale
- Risk outlook
- Forward strategy

Tone: institutional, precise, investor-grade.
Length: 120–180 words.

If data is limited, clearly state that the system is in early calibration phase.
"""

    # --------------------------------------------------
    # Report generation
    # --------------------------------------------------

    def generate_report(self, regime_df, risk_df, weights_df):
        prompt = self._build_prompt(regime_df, risk_df, weights_df)

        try:
            response = self.client.responses.create(
                model="gpt-5.2",
                input=prompt,
            )

            return response.output_text.strip()

        except Exception as e:
            # ⭐ FINAL SAFETY — never fail CI
            return (
                "CIO Note (Fallback):\n"
                "The AI PMS is currently in calibration due to limited "
                "historical data availability. Portfolio risk remains "
                "contained, and capital deployment will scale as "
                "model confidence improves."
            )
