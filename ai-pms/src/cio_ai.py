import pandas as pd
from openai import OpenAI


class CIOAI:
    """
    Generates institutional CIO commentary
    using quant outputs as grounding context.
    """

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables.")

        self.client = OpenAI(api_key=api_key)

    def _build_prompt(self, regime_df, risk_df, weights_df):
        regime = regime_df.iloc[-1].to_dict()
        risk = risk_df.iloc[-1].to_dict()

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
Length: 150–200 words.
"""

    def generate_report(self, regime_df, risk_df, weights_df):
        prompt = self._build_prompt(regime_df, risk_df, weights_df)

        response = self.client.responses.create(
            model="gpt-5.2",
            input=prompt,
        )

        return response.output_text.strip()
