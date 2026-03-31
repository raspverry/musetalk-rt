# Session warm-path policy integration

This directory includes:
- `warm_path_policy.py` for policy selection + override precedence.
- `musetalk_integration.py` for policy-aware command rendering and runtime readiness checks.

## Precedence rules
Highest to lowest:
1. CLI overrides (`chunk_ms_override`, `startup_chunks_override`)
2. Scenario-provided values forwarded as overrides
3. Policy mode in config (`default`, `fallback`, `experimental`)

## Current policy config
- `benchmarks/baseline/policies/warm_path_policy.json`

## Real vs proxy/scaffolding (short note)
The integration now has staged checks plus a minimal lifecycle-aware non-production path:
- readiness checks
- dry-run
- executable smoke (permanent pre-gate)
- tiny real execution
- lifecycle-aware probe (`session_start` → `avatar_ready_or_warm_assumed` → `audio_accepted` → `first_speaking_frame_signal`)

This is still **not full session/runtime integration**. Remaining blockers include production orchestration wiring, real session lifecycle hooks with actual runtime callbacks/events, end-to-end media correctness checks, stable GPU/runtime environment contracts, and robust error-recovery semantics.

## Recommendation: keep smoke as a permanent gate
Yes—keep executable smoke as a permanent pre-gate before tiny real execution and lifecycle probing.

## Recommendation: warm policy defaults on real-oriented path
Keep `default`/`fallback` warm policy values unchanged for now. They remain policy-layer decisions and should only be adjusted after evidence from repeated lifecycle-aware runs on real runtime environments.
