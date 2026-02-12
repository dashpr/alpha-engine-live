import json
import pathlib

OUTPUT = pathlib.Path("output")
OUTPUT.mkdir(exist_ok=True)

NAV = json.loads((OUTPUT / "portfolio_nav.json").read_text())
DEPLOY = json.loads((OUTPUT / "deployment_state.json").read_text())

MEMO_FILE = OUTPUT / "scale_up_memo.json"

memo = {
    "current_value": NAV["value"],
    "return_pct": NAV["return_pct"],
    "capital_deployed": DEPLOY["deployed"],
    "eligible_for_scale": NAV["return_pct"] > 8 and DEPLOY["week"] >= 8,
    "note": "Manual approval required before adding capital."
}

MEMO_FILE.write_text(json.dumps(memo, indent=2))

print("Scale‑up memo generated.")
