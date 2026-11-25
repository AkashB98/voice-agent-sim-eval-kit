# voice-agent-sim-eval-kit

Deterministic simulation evals for **voice agents** — before a voice agent ships, run it against synthetic callers who interrupt, change their mind mid-call, and get misheard, and see exactly which slice breaks it.

> **Honesty line: this kit scores timestamped text transcripts and uses no audio.** There is no microphone, no speech synthesis, and no acoustic model here. "Voice" complications are represented at the transcript level — barge-in turns, intent changes, simulated per-turn latency values, and speech-recognition errors planted as substituted values (a misheard digit, name, or amount). That is a deliberate scope choice: transcript-level simulation is fast, deterministic, and reproducible, and it is not a substitute for real-audio evaluation.

Inspired by the November 2025 wave of voice-agent evaluation launches (e.g. simulation-to-production eval tooling on Product Hunt) — this is an original, stdlib-only implementation, not a clone.

## The headline result

The policy that wins overall **fails on the barge-in slice** — which is exactly why aggregate scores alone are not enough for voice agents:

| Policy | Overall | Clean | Barge-in | Intent-change | ASR-error |
|---|---|---|---|---|---|
| `task_optimizer` | **0.9000** | 1.0000 | **0.6800** | 1.0000 | 1.0000 |
| `interrupt_first` | 0.8375 | 0.8000 | **0.8800** | 0.8000 | 0.8500 |
| `baseline_scripted` | 0.5375 | 0.7333 | 0.5200 | 0.6000 | 0.3500 |

`task_optimizer` is fast and accurate everywhere except when a caller talks over it: it keeps speaking to finish the task, so it never stops, acknowledges, or recovers. `interrupt_first` handles interruptions best, but its verbose confirmations push ordinary turns over the latency budget, costing it the overall lead. The naive baseline also states a planted forbidden claim ("guaranteed refund") 6 times — every one scored zero as a guardrail violation. Numbers above are the real output of `python3 run_evals.py` on the seeded scenarios in `data/` (24 scenarios, 96 turns per policy); see `eval_report.json`.

## How it works

- **Synthetic caller scenarios** (`data/scenarios.json`, seeded and fixed): 24 scenarios, 6 per slice — `clean`, `barge_in`, `intent_change`, `asr_error`. Complications are planted, never random at run time: barge-in interruptions (two per barge-in scenario), a mid-call intent change, and injected speech-recognition errors where the heard value differs from the true value (digits, names, amounts). ASR errors are value substitutions only — no accent or noise markers.
- **Three scripted policies under test** (`voice_agent_sim_eval_kit/policies.py`): `baseline_scripted` (naive script follower), `task_optimizer` (fast, confirmation-driven), and `interrupt_first` (stop-and-recover first, verbose). Policies are deterministic functions of the transcript — same input, same output, every run.
- **Turn-level scoring** (`voice_agent_sim_eval_kit/scoring.py`): each turn scores task completion (did the agent use the true value / adopt the new intent / stop-acknowledge-recover after a barge-in), latency-budget compliance (simulated latency vs. a per-turn budget — 600 ms for ordinary turns, 900 ms for barge-in turns, where stopping and recovering legitimately takes longer), and a disallowed-claim guardrail (stating a planted forbidden claim zeroes the turn).
- **Slice reporting** (`voice_agent_sim_eval_kit/simulator.py`): scores are averaged overall *and* per slice, so a policy cannot hide a broken slice inside a good average.

## How to run

```bash
python3 demo.py        # one barge-in scenario through all three policies
python3 run_evals.py   # full eval; writes eval_report.json
python3 -m unittest discover -s tests -v   # 10 tests (unittest, stdlib only)
```

Python 3, standard library only. No network, no API keys, no installation.

## Honest limits

- **No audio** (see the honesty line above): real barge-in involves overlapping speech and endpointing; this kit models the *conversational consequence*, not the acoustics.
- Latency values are simulated constants per policy, not measured from a live system — they test budget *logic*, not real serving latency.
- Policies are scripted reference implementations, not LLMs; the kit evaluates policy *behaviour patterns*, and wiring a real agent in means implementing the same `respond(scenario, turn, state)` interface.
- 24 seeded scenarios is a smoke-scale eval set, designed to expose slice failures clearly — not a production benchmark.
- Synthetic data only; no real callers, calls, or personal data.

## What this proves

Simulation eval design for conversational agents: planted complications, turn-level scoring, guardrails, latency budgets, and slice-level reporting that surfaces the failure an overall score hides — the reliability layer voice-agent teams need before simulation results can be trusted on the way to production.

## License

MIT — see `LICENSE`.
