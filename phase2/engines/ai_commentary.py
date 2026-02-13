from phase2.utils import read_json, write_json, ist_now

NAV_FILE = "phase2/data/nav.json"
GOV_FILE = "phase2/data/governance.json"
SECTOR_FILE = "phase2/data/sectors.json"

AI_FILE = "phase2/data/ai_commentary.json"


def run():
    nav = read_json(NAV_FILE, {})
    gov = read_json(GOV_FILE, {})
    sectors = read_json(SECTOR_FILE, [])

    value = nav.get("value", 0)
    ret = nav.get("return_pct", 0)
    regime = gov.get("regime", "NEUTRAL")
    note = gov.get("regime_note", "")

    top_sector = max(
        sectors,
        key=lambda x: x.get("weight", 0),
        default={"sector": "N/A", "weight": 0},
    )

    text = (
        f"Portfolio NAV stands at ₹{value:,.0f} with return of {ret:.2f}%. "
        f"Current regime is {regime.replace('_',' ')} — {note} "
        f"Highest allocation is in {top_sector['sector']} sector "
        f"at {top_sector['weight']:.1f}% weight."
    )

    ai = {
        "timestamp": ist_now(),
        "text": text,
    }

    write_json(AI_FILE, ai)

    print("AI commentary generated")
