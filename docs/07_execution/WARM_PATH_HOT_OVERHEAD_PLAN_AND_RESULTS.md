# Warm-Path Hot Overhead Plan and Baseline Results

## Objective
Reduce warm-session hot-path overhead without changing product goals, and benchmark against existing baseline reports.

## Ranked hypotheses (latency-first)
1. **H1: save-images path removal/bypass lowers warm first-frame latency**
   - Rationale: writing every frame to disk introduces synchronous I/O overhead in the hot path.
2. **H2: remove file-mtime dependence for first-frame timing when infer command can emit event timestamps**
   - Rationale: marker/file polling adds boundary uncertainty and extra filesystem calls.
3. **H3: reduce file-glob polling dependence in wrapper path**
   - Rationale: repeated glob scans and mtime checks are avoidable when command provides structured timing output.
4. **H4: preserve throughput while prioritizing first-frame latency**
   - Rationale: product priority is perceived responsiveness first.

## Small patches applied (no major rewrite)
1. **Patch A**: `approx_infer.py` adds optional in-memory mode (`--disable-frame-write`) and infer-event JSON output (`--emit-metrics-json`).
2. **Patch B**: `musetalk_baseline_runner.py` adds `--prefer-infer-json` and consumes emitted timing metrics (`audio_accepted_ts`, `first_frame_ts`, `steady_state_fps`) before falling back to file mtimes.
3. **Patch C**: `validate_report.py` adds strict warm-anchor validation (`--strict-warm-anchor`) and frame-source provenance requirement.
4. **Patch D**: warm optimized scenario added (`real_warm_start_session_proxy_optimized.json`) and docs updated with provenance boundaries.

## Baseline comparison (same harness, warm path)
Compared reports:
- Before: `real_warm_start_session_proxy_report.json`
- After: `real_warm_start_session_proxy_optimized_report.json`

### Summary metrics (mean)
- `first_frame_latency_ms`: **407.996 -> 391.371** (improved)
- `steady_state_fps`: **22.713 -> 22.472** (slight regression)
- `avatar_preparation_time_ms`: `0.0 -> 0.0` (unchanged warm semantics)
- `status`: all runs `ok` for both reports

## Regression/stability risk note
- Risk: bypassing file writes may reduce compatibility with workflows that inspect frame artifacts directly.
- Risk: infer-JSON timing depends on command cooperation; missing JSON falls back to file-based path.
- Current quality risk: no visual-regression harness is included here; only runtime metric behavior is compared.

## Recommendation
**Keep Patch B + Patch C immediately** (better provenance and warm-anchor truthfulness with no product-path rewrite).

**Conditionally keep Patch A for server warm path** where stream/event outputs are available and frame-file artifacts are not required in hot path.

Do not claim final runtime improvement beyond this controlled benchmark proxy until the same measurement path is wired to real MuseTalk session events.
