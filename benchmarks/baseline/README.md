# Baseline benchmark harness

This harness provides truthful, repeatable baseline measurement aligned with `docs/02_eval/EVALUATION_SPEC.md`.

## Report schema stability
Core schema remains stable:
- `scenario`
- `summary`
- `results[]`
- `generated_at_epoch_ms`

Non-breaking extensions used for provenance:
- top-level `environment`
- per-run `measurement_provenance`
- summary `partial_runs`
- per-run `lifecycle_stage_outcomes` (optional, when lifecycle probe enabled)

## Cold-path vs warm-path metric semantics

### Cold start (`mode: cold_start`)
- `avatar_preparation_time_ms`: wall-clock duration of `prep-cmd`.
- `first_frame_latency_ms`: from selected anchor to first speaking frame timestamp.

### Warm start (`mode: warm_start`)
- `avatar_preparation_time_ms`: `0.0` by definition (prep skipped; cache reuse assumption).
- `first_frame_latency_ms`: preferred boundary is **audio accepted -> first speaking frame**.
  - Preferred anchor: `audio_accepted_marker` (or infer JSON `audio_accepted_ts` when `--prefer-infer-json` is enabled).
  - Fallback anchor: `infer_cmd_start`.

## Exact metric provenance
1. **avatar_preparation_time_ms**
   - `prep_cmd_wall_clock` (cold)
   - `warm_path_prep_skipped_zero` (warm)

2. **first_frame_latency_ms**
   - `first_frame_ts_minus_audio_accepted_marker` (preferred warm proxy)
   - fallback: `first_frame_ts_minus_infer_cmd_start`

3. **steady_state_fps**
   - preferred: `infer_json_steady_state_fps`
   - fallback: `(frame_count - 1) / (last_frame - first_frame)`

4. **peak_vram_mb**
   - sampled max from `nvidia-smi --query-gpu=memory.used`

5. **outcome taxonomy**
   - `ok`: command succeeded with required evidence.
   - `partial`: command succeeded but required evidence missing.
   - `oom`: OOM signature detected in stderr.
   - `crash`: non-zero exit without OOM signature.
   - `error`: exited 0 but produced no usable frame/latency evidence.

## Warm-path policy config (default + fallback)
Configured in:
- `benchmarks/baseline/policies/warm_path_policy.json`

Current recommendation:
- default: `chunk_ms=120`, `startup_chunks=1`
- fallback: `chunk_ms=160`, `startup_chunks=2`

Fallback should be selected when:
- continuity artifacts repeat,
- chunk arrival jitter is high,
- partial/error outcomes increase under default policy.

Aggressive policies `(40,1)` and `(80,1)` are kept as experiment-only due to higher churn risk.

## Approximation boundaries
- File mtime and marker timestamps remain proxies until runtime streaming events are wired directly.
- `--prefer-infer-json` reduces file-system dependency by consuming command-emitted timing metrics.
- Every run records provenance fields to make boundaries explicit, including `infer_spawn_mode`, `file_polling_used`, and chunk continuity hints.

Lifecycle probe signal boundaries:
- `session_start`: **proxy** command-level stage (not runtime callback binding yet)
- `avatar_ready_or_warm_assumed`: **proxy** stage by default; can be **limited real-wired** via `--enable-limited-real-lifecycle-wiring --real-avatar-ready-path <path>` (filesystem readiness probe)
- `audio_accepted`: **proxy or semi-real** depending on marker/event source used by the command
- `first_speaking_frame_signal`: **limited real-wired** in flagged mode by observing actual first-frame evidence (`first_frame_ts`) from infer output/file signals

Recommendation for limited real MuseTalk wiring:
- The current lifecycle path is stable enough for **limited, guarded wiring experiments** behind flags.
- It is **not yet sufficient** for broad production wiring without direct runtime event contracts.

Flagged limited real wiring example:
```bash
python benchmarks/baseline/musetalk_baseline_runner.py \
  --enable-limited-real-lifecycle-wiring \
  --real-avatar-ready-path runtime/session/README.md \
  ...
```

## Validator
`validate_report.py` verifies required fields and consistency.

Strict warm-anchor + chunk provenance example:
```bash
python benchmarks/baseline/validate_report.py \
  --report benchmarks/baseline/reports/runtime_facing_default_tts_bursty_report.json \
  --strict-warm-anchor \
  --require-chunk-provenance
```

## Chunk-policy grid runner
Use `run_chunk_policy_grid.py` to execute a controlled warm chunk-policy grid and produce ranked summaries:
```bash
python benchmarks/baseline/run_chunk_policy_grid.py
```

## Runtime-facing policy validation (bursty cadence approximation)
Use `run_policy_runtime_facing_validation.py` to compare configured default/fallback under a `tts_bursty` cadence approximation:
```bash
python benchmarks/baseline/run_policy_runtime_facing_validation.py
```

This generates `runtime_facing_policy_validation_summary.json`.
