# Warm-Path Hot Overhead and Runtime-Facing Policy Validation (Iteration 5)

## Scope
Transition from proxy-only chunk conclusions to runtime-facing validation approximation while preserving schema/provenance strictness.

## Configured warm policy (implementation)
Policy file:
- `benchmarks/baseline/policies/warm_path_policy.json`

Configured values:
- **default:** `chunk_ms=120`, `startup_chunks=1`
- **fallback:** `chunk_ms=160`, `startup_chunks=2`

Fallback triggers:
- repeated continuity artifacts,
- high chunk arrival jitter,
- elevated partial/error outcomes under default.

Aggressive non-default:
- `(40,1)` and `(80,1)` kept for experiments only.

## Ranked remaining warm-path overhead sources
1. Audio chunk boundary startup delay
2. Residual file handoff fallback path
3. Subprocess startup overhead (mostly reduced)
4. File polling fallback overhead
5. FFmpeg re-entry risk (not seen in current proxy hot path)

## Patches in this iteration (3)
1. **Policy config + selection encoding**
   - Added `warm_path_policy.json` with default/fallback/aggressive policy metadata.
2. **Cadence realism step**
   - Added `tts_bursty` cadence profile in `approx_infer.py` and preserved provenance fields.
3. **Runtime-facing validation runner**
   - Added `run_policy_runtime_facing_validation.py` to benchmark configured default/fallback under bursty cadence.

## Runtime-facing validation step (proxy approximation)
Generated reports:
- `runtime_facing_default_tts_bursty_report.json`
- `runtime_facing_fallback_tts_bursty_report.json`
- summary: `runtime_facing_policy_validation_summary.json`

Observed means:
- Default `(120,1)` first-frame latency: `104.559 ms`
- Fallback `(160,2)` first-frame latency: `362.248 ms`
- Both scenarios: all runs `ok`

Interpretation:
- default remains preferred for perceived response start,
- fallback remains stability-oriented and slower by design.

## Keep/drop recommendation
- **KEEP default:** `(120,1)` for normal warm sessions.
- **KEEP fallback:** `(160,2)` for stability-sensitive sessions or jitter spikes.
- **DROP as default:** `(40,1)` and `(80,1)` due high churn risk hints, despite lower latency.

## Proxy limitation note (still not production claim)
- Real TTS cadence may have non-stationary burst patterns, silence gaps, and transport jitter not fully matched by this proxy.
- Real session event timestamps (`audio_accepted`, `first_frame_emitted`) must be wired from runtime to replace proxy timing anchors.
- Visual continuity validation with real lip-sync output is still required before production claims.
