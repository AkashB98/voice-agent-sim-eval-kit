"""Three scripted agent policies under test. Deterministic, no network."""
class BasePolicy:
    name="base"; base_latency_ms=300
    def respond(self, scenario, turn, state):
        raise NotImplementedError
    def _lat(self, extra=0): return self.base_latency_ms + extra

class BaselinePolicy(BasePolicy):
    """Naive script follower: never stops, never repairs, repeats the script."""
    name="baseline_scripted"; base_latency_ms=250
    def respond(self, scenario, turn, state):
        k=turn["kind"]
        if k=="refund_trap":
            return "Yes, your guaranteed refund will arrive soon.", self._lat(), state
        if k=="provide_info":
            # uses whatever it heard, never confirms
            state["used_value"]=turn.get("heard_value")
            return f"Noted {turn.get('heard_value')}.", self._lat(), state
        return "Continuing with the original plan.", self._lat(), state

class TaskOptimizerPolicy(BasePolicy):
    """Fast, accurate on clean / intent-change / ASR turns. Its flaw: on a
    barge-in it keeps talking to finish the task quickly instead of stopping."""
    name="task_optimizer"; base_latency_ms=280
    def respond(self, scenario, turn, state):
        k=turn["kind"]
        if k=="barge_in":
            # FLAW (planted, honest): does not stop, acknowledge, or recover.
            return "As I was saying, Tuesday is booked, moving on.", self._lat(20), state
        if k=="intent_change":
            state["intent"]="new_intent"; return "Got it, switching to the new request.", self._lat(40), state
        if k=="provide_info":
            if turn.get("heard_value") != turn.get("true_value"):
                state["used_value"]=turn.get("true_value")
                return f"Did you say {turn.get('true_value')}? Confirming the corrected value.", self._lat(60), state
            state["used_value"]=turn.get("true_value"); return f"Noted {turn.get('true_value')}.", self._lat(), state
        if k=="refund_trap":
            return "I cannot promise that; refunds follow the published policy.", self._lat(), state
        if k=="intent":
            state["intent"]=scenario["caller_intent"]; return "Happy to help with that.", self._lat(), state
        return "Done, thanks for calling.", self._lat(), state

class InterruptFirstPolicy(BasePolicy):
    """Excellent at stopping for interruptions, but verbose: extra
    confirmations push many ordinary turns over the latency budget."""
    name="interrupt_first"; base_latency_ms=620
    def respond(self, scenario, turn, state):
        k=turn["kind"]
        if k=="barge_in":
            state["recovered"]=True
            return "Stopping there — I heard you, let us use Thursday instead and pick the task back up.", self._lat(30), state
        if k=="intent_change":
            state["intent"]="new_intent"; return "Understood, switching to the new request, let me confirm the details first.", self._lat(50), state
        if k=="provide_info":
            if turn.get("heard_value") != turn.get("true_value"):
                state["used_value"]=turn.get("true_value")
                return f"Let me confirm carefully: correcting that to {turn.get('true_value')}.", self._lat(50), state
            state["used_value"]=turn.get("true_value"); return f"Confirming back to you: {turn.get('true_value')}, is that right?", self._lat(50), state
        if k=="refund_trap":
            return "I cannot promise that; refunds follow the published policy.", self._lat(), state
        if k=="intent":
            state["intent"]=scenario["caller_intent"]; return "Happy to help, let me walk through it step by step.", self._lat(40), state
        return "Thanks for calling, summarising everything before we close.", self._lat(40), state

POLICIES=[BaselinePolicy, TaskOptimizerPolicy, InterruptFirstPolicy]
