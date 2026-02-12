import json, pathlib


OUTPUT = pathlib.Path("output")


nav = json.loads((OUTPUT / "portfolio_nav.json").read_text())


summary = f"Portfolio value ₹{nav['value']:.0f}. Return {nav['return_pct']}%. Regime stable."


(OUTPUT / "ai_portfolio.txt").write_text(summary)
