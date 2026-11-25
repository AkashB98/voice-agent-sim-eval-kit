import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from voice_agent_sim_eval_kit.scenarios import load_scenarios
from voice_agent_sim_eval_kit.simulator import run_all, run_policy
from voice_agent_sim_eval_kit.policies import BaselinePolicy, TaskOptimizerPolicy, InterruptFirstPolicy
from voice_agent_sim_eval_kit.scoring import score_turn

class TestData(unittest.TestCase):
    def test_scenarios_load_and_slices_balanced(self):
        sc=load_scenarios(); self.assertEqual(len(sc),24)
        from collections import Counter; c=Counter(s["slice"] for s in sc)
        self.assertEqual(set(c.values()),{6})
    def test_no_accent_or_noise_markers(self):
        import json; raw=Path(__file__).resolve().parent.parent.joinpath("data/scenarios.json").read_text().lower()
        for bad in ["accent","background noise","noisy audio"]: self.assertNotIn(bad, raw)
    def test_asr_errors_are_value_substitutions(self):
        for s in load_scenarios():
            if s["slice"]=="asr_error":
                t=[x for x in s["turns"] if x["kind"]=="provide_info"][0]
                self.assertNotEqual(t["true_value"], t["heard_value"])
class TestPolicies(unittest.TestCase):
    def setUp(self): self.sc=load_scenarios()
    def test_deterministic(self):
        self.assertEqual(run_all(self.sc), run_all(self.sc))
    def test_headline_slice_reversal_holds(self):
        r={x["policy"]:x for x in run_all(self.sc)}
        self.assertGreater(r["task_optimizer"]["overall"], r["interrupt_first"]["overall"])
        self.assertLess(r["task_optimizer"]["slices"]["barge_in"], r["interrupt_first"]["slices"]["barge_in"])
    def test_baseline_is_worst_overall(self):
        r=run_all(self.sc); self.assertEqual(min(r,key=lambda x:x["overall"])["policy"],"baseline_scripted")
    def test_baseline_commits_guardrail_violation_optimizer_does_not(self):
        r={x["policy"]:x for x in run_all(self.sc)}
        self.assertGreater(r["baseline_scripted"]["guardrail_violations"],0)
        self.assertEqual(r["task_optimizer"]["guardrail_violations"],0)
        self.assertEqual(r["interrupt_first"]["guardrail_violations"],0)
    def test_interrupt_first_latency_failures(self):
        r={x["policy"]:x for x in run_all(self.sc)}
        self.assertGreater(r["interrupt_first"]["latency_budget_failures"], r["task_optimizer"]["latency_budget_failures"])
    def test_barge_in_turn_scoring(self):
        sc=[s for s in self.sc if s["slice"]=="barge_in"][0]; turn=[t for t in sc["turns"] if t["kind"]=="barge_in"][0]
        good,_=score_turn(sc,turn,"Stopping there — I heard you, let us pick the task back up.",300,{"recovered":True})
        bad,_=score_turn(sc,turn,"As I was saying, moving on.",300,{})
        self.assertGreater(good,bad); self.assertEqual(bad,0.2)  # latency only
    def test_guardrail_violation_scores_zero(self):
        sc=self.sc[0]; turn={"kind":"refund_trap","user_text":"?","expected":"x","latency_budget_ms":700}
        s,det=score_turn(sc,turn,"Your guaranteed refund is coming.",100,{}); self.assertEqual(s,0.0); self.assertFalse(det["guardrail_ok"])
if __name__=="__main__": unittest.main()
