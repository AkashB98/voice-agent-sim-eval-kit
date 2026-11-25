from .scoring import score_turn
from .policies import POLICIES
SLICES=["clean","barge_in","intent_change","asr_error"]
def run_policy(policy, scenarios):
    per_slice={s:[] for s in SLICES}; all_scores=[]; violations=0; latency_fails=0; turns_n=0
    for sc in scenarios:
        state={}
        for turn in sc["turns"]:
            resp, lat, state = policy.respond(sc, turn, state)
            score, det = score_turn(sc, turn, resp, lat, state)
            per_slice[sc["slice"]].append(score); all_scores.append(score); turns_n+=1
            if not det["guardrail_ok"]: violations+=1
            if not det["latency_ok"]: latency_fails+=1
    def mean(xs): return round(sum(xs)/len(xs),4) if xs else 0.0
    return {"policy":policy.name,"overall":mean(all_scores),
            "slices":{s:mean(v) for s,v in per_slice.items()},
            "turns":turns_n,"guardrail_violations":violations,"latency_budget_failures":latency_fails}
def run_all(scenarios):
    return [run_policy(cls(), scenarios) for cls in POLICIES]
