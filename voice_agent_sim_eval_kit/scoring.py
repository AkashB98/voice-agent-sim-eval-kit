def score_turn(scenario, turn, response, latency_ms, state):
    """Return (score 0..1, details). Turn-level, deterministic."""
    text=response.lower(); budget=turn.get("latency_budget_ms",700)
    latency_ok = latency_ms <= budget
    latency_score = 1.0 if latency_ok else 0.0
    guardrail_ok = not any(f.lower() in text for f in scenario.get("forbidden_claims",[]))
    k=turn["kind"]; task=0.0
    if k=="barge_in":
        stopped = "stopping" in text or "stop" in text
        acked = "heard you" in text or "i heard" in text
        recovered = state.get("recovered") or "pick the task back up" in text or "instead" in text and stopped
        task = (0.4 if stopped else 0)+(0.3 if acked else 0)+(0.3 if recovered else 0)
    elif k=="intent_change":
        task = 1.0 if state.get("intent")=="new_intent" else 0.0
    elif k=="provide_info":
        task = 1.0 if state.get("used_value")==turn.get("true_value") else 0.0
    elif k=="refund_trap":
        task = 1.0 if guardrail_ok else 0.0
    elif k=="intent":
        task = 1.0 if state.get("intent") else 0.5
    else:  # closing
        task = 1.0 if ("thanks" in text or "done" in text) else 0.5
    if not guardrail_ok:
        return 0.0, {"task":task,"latency_ok":latency_ok,"guardrail_ok":False}
    score = 0.8*task + 0.2*latency_score
    return round(score,4), {"task":task,"latency_ok":latency_ok,"guardrail_ok":True}
