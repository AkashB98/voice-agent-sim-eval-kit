#!/usr/bin/env python3
"""Run all policies over all scenarios and write eval_report.json."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from voice_agent_sim_eval_kit.scenarios import load_scenarios
from voice_agent_sim_eval_kit.simulator import run_all
def main():
    scenarios=load_scenarios(); results=run_all(scenarios)
    report={"scenarios":len(scenarios),"results":results,
            "headline":{"overall_winner":max(results,key=lambda r:r["overall"])["policy"],
                        "barge_in_winner":max(results,key=lambda r:r["slices"]["barge_in"])["policy"],
                        "slice_reversal": max(results,key=lambda r:r["overall"])["policy"] != max(results,key=lambda r:r["slices"]["barge_in"])["policy"]}}
    out=Path(__file__).parent/"eval_report.json"; out.write_text(json.dumps(report,indent=2)+"\n")
    for r in results: print(r["policy"], "overall", r["overall"], "slices", r["slices"])
    print("headline:", report["headline"]); print("wrote", out); return 0
if __name__=="__main__": raise SystemExit(main())
