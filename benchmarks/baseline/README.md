# Baseline benchmark harness

This harness provides truthful, repeatable baseline measurement aligned with `docs/02_eval/EVALUATION_SPEC.md`.

## Report schema (preserved)
The harness output schema remains unchanged:
- `scenario`
- `summary`
- `results[]` with per-run values
- `generated_at_epoch_ms`

## Metrics (exact definitions)
1. **avatar_preparation_time_ms**
   - Cold-start: wall-clock duration of `prep-cmd` execution, measured by the wrapper.
   - Warm-start: `0.0` by definition because prep is skipped and cache reuse is assumed.

2. **first_frame_latency_ms**
   - Wall-clock duration from inference-command start (`infer-cmd` launch time) to first detected output speaking frame file mtime (`frame-glob`).
   - Limitation: this approximates session hot-path readiness when true streaming events are not yet wired.

3. **steady_state_fps**
   - Computed as `(frame_count - 1) / (last_frame_mtime - first_frame_mtime)`.
   - Startup buffering is excluded by construction (steady region starts at first speaking frame).

4. **peak_vram_mb**
   - Maximum sampled `nvidia-smi memory.used` during command execution.
   - If `nvidia-smi` is unavailable, value may be `null`.

5. **crash/OOM/error outcomes**
   - `ok`: command exits 0 and frames exist.
   - `oom`: stderr includes OOM signature.
   - `crash`: non-zero exit without OOM signature.
   - `error`: process exits 0 but emits no speaking frames.

## Integration modes
- `simulated` adapter in `benchmark_harness.py`: deterministic CI wiring checks.
- `command` adapter in `benchmark_harness.py`: real command execution.
- `musetalk_baseline_runner.py`: wrapper for real MuseTalk baseline path with cold/warm split.

## Real baseline execution path
Use the harness command adapter to run `musetalk_baseline_runner.py`.

Cold-start scenario contract:
- run prep command
- run inference command
- watch `frame-glob` for first/last frame times

Warm-start scenario contract:
- skip prep
- run inference command
- same frame timing and status logic

## Approximation note (explicit)
If exact streaming session events are not yet available, the wrapper uses frame-file emergence as a hot-path approximation. This is a measurement limitation, not an optimization.

## Quick start (real command path wrapper)
```bash
python benchmarks/baseline/benchmark_harness.py \
  --scenario benchmarks/baseline/scenarios/real_cold_start_local.json \
  --output-dir benchmarks/baseline/reports
```
