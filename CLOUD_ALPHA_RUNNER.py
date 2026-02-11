def load_nifty():
    for _ in range(3):  # retry 3 times
        try:
            nifty = yf.download("^NSEI", period=DATA_PERIOD, progress=False)

            if nifty is None or nifty.empty:
                continue

            close = nifty["Close"]

            if close.empty:
                continue

            dma200 = close.rolling(200).mean()
            risk_on = close > dma200

            return pd.DataFrame({"Close": close, "RiskOn": risk_on})

        except Exception:
            continue

    # final fallback → create minimal safe dataframe
    dates = pd.date_range(end=datetime.today(), periods=300)
    close = pd.Series(np.nan, index=dates)
    risk_on = pd.Series(False, index=dates)

    return pd.DataFrame({"Close": close, "RiskOn": risk_on})
