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

## Approximation boundaries
- File mtime and marker timestamps remain proxies until runtime streaming events are wired directly.
- `--prefer-infer-json` reduces file-system dependency by consuming command-emitted timing metrics.
- Every run records provenance fields to make boundaries explicit, including `infer_spawn_mode` and `file_polling_used`.

## Validator
`validate_report.py` verifies required fields and consistency.

Strict warm-anchor check example:
```bash
python benchmarks/baseline/validate_report.py \
  --report benchmarks/baseline/reports/real_warm_start_session_proxy_optimized_report.json \
  --strict-warm-anchor
```

## Quick start (warm-path optimized proxy)
```bash
python benchmarks/baseline/benchmark_harness.py \
  --scenario benchmarks/baseline/scenarios/real_warm_start_session_proxy_optimized.json \
  --output-dir benchmarks/baseline/reports
```

## Audio chunk boundary analysis support
- `approx_infer.py` can model warm-start startup from chunk boundaries using:
  - `--chunk-ms`
  - `--startup-chunks`
  - `--chunk-overhead-ms`
- Runner provenance records `chunk_ms`, `startup_chunks`, `chunk_overhead_ms`, and `startup_delay_ms`.
- Use this for latency tradeoff analysis only; it is still a proxy path.
