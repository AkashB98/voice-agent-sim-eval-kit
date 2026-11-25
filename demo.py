#!/usr/bin/env python3
"""Demo: one barge-in scenario through all three policies."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from voice_agent_sim_eval_kit.scenarios import load_scenarios
from voice_agent_sim_eval_kit.policies import POLICIES
from voice_agent_sim_eval_kit.scoring import score_turn
def main():
    sc=[s for s in load_scenarios() if s["slice"]=="barge_in"][0]
    print(f"Scenario {sc['id']} ({sc['slice']}): {sc['caller_intent']}")
    for cls in POLICIES:
        pol=cls(); state={}; scores=[]
        print(f"\n{pol.name}:")
        for turn in sc["turns"]:
            resp,lat,state=pol.respond(sc,turn,state); score,_=score_turn(sc,turn,resp,lat,state); scores.append(score)
            print(f"  [{turn['kind']}] caller: {turn['user_text']}")
            print(f"           agent ({lat} ms, score {score}): {resp}")
        print(f"  mean score: {round(sum(scores)/len(scores),4)}")
    return 0
if __name__=="__main__": raise SystemExit(main())
