import json
from pathlib import Path
def load_scenarios(path=None):
    p = Path(path) if path else Path(__file__).resolve().parent.parent / "data" / "scenarios.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    scenarios = data["scenarios"]
    for s in scenarios:
        assert s["slice"] in {"clean","barge_in","intent_change","asr_error"}, s
        assert s["turns"], s["id"]
    return scenarios
