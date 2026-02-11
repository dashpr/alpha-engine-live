import json
import datetime
import requests
import os

OUTPUT_PATH = "output/market_commentary.json"

def fetch_dummy_news():
    """
    Free, stable placeholder until paid APIs added.
    """
    headlines = [
        "Nifty shows resilience amid global uncertainty",
        "Banking stocks lead market momentum",
        "IT sector stabilises after recent correction",
        "Midcaps outperform broader indices",
        "FII flows turn mildly positive"
    ]
    return headlines


def ai_summarise(headlines):
    """
    Simple deterministic AI-style summary (no API cost).
    """
    bullish = sum("outperform" in h.lower() or "positive" in h.lower() for h in headlines)
    bearish = sum("uncertainty" in h.lower() or "correction" in h.lower() for h in headlines)

    if bullish > bearish:
        sentiment = "Bullish"
    elif bearish > bullish:
        sentiment = "Cautious"
    else:
        sentiment = "Neutral"

    summary = f"Market sentiment appears {sentiment.lower()} with focus on banking leadership and midcap strength."

    return sentiment, summary


def build_commentary():
    headlines = fetch_dummy_news()
    sentiment, summary = ai_summarise(headlines)

    data = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "sentiment": sentiment,
        "summary": summary,
        "headlines": headlines
    }

    os.makedirs("output", exist_ok=True)

    with open(OUTPUT_PATH, "w") as f:
        json.dump(data, f, indent=2)

    print("Market commentary generated.")


if __name__ == "__main__":
    build_commentary()
