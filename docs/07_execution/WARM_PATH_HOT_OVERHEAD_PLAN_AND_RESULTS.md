# Warm-Path Hot Overhead Analysis and Results (Iteration 3)

## Objective
Continue narrowing proxy-to-real-session gap for warm-path latency without major redesign.

## Ranked remaining warm-path overhead sources
1. **Audio chunk boundary startup delay (highest remaining)**
   - Startup waits for enough chunk context before first speaking frame.
   - Chunk size and startup chunk count materially shift first-frame latency.
2. **Residual disk/file handoff fallback path**
   - File path still exists for diagnostics and compatibility; optimized path bypasses it.
3. **Subprocess startup overhead**
   - Reduced via `exec` spawn preference; remains only where shell features are needed.
4. **File polling overhead (fallback only)**
   - Removed in optimized infer-JSON path; still present in fallback mode.
5. **FFmpeg dependency in proxy hot path**
   - Current proxy scenarios show `ffmpeg_in_hot_path_cmd=false`; no ffmpeg loop observed in measured hot path.

## Small patches applied (3)
### Patch 1 — chunk-boundary latency instrumentation
- Added chunk model controls in `approx_infer.py`:
  - `--chunk-ms`
  - `--startup-chunks`
  - `--chunk-overhead-ms`
- Emit these in infer metrics for provenance.

### Patch 2 — runner provenance expansion for remaining dependencies
- Added provenance fields:
  - `ffmpeg_in_hot_path_cmd`
  - `chunk_ms`, `startup_chunks`, `chunk_overhead_ms`, `startup_delay_ms`
- Keeps warm-path semantics and report schema compatibility.

### Patch 3 — validator strictness for provenance integrity
- Validator now requires `ffmpeg_in_hot_path_cmd` in provenance (in addition to prior strict fields).

## Before/after benchmark reports (chunk tradeoff)
Compared:
- Before (larger chunks): `real_warm_start_chunk_large_report.json`
- After (smaller chunks): `real_warm_start_chunk_small_report.json`

### Mean metrics
- `first_frame_latency_ms`: **265.131 -> 85.112** (large improvement in response start)
- `steady_state_fps`: **22.452 -> 22.441** (near-flat, tiny regression)
- status: all runs `ok`

## Keep/drop recommendation per patch
- **Patch 1 (chunk instrumentation): KEEP**
  - Required to reason about chunk-size tradeoffs with evidence.
- **Patch 2 (runner dependency provenance): KEEP**
  - Improves decision quality and confirms ffmpeg/file-handoff status in each run.
- **Patch 3 (validator strictness): KEEP**
  - Prevents silent provenance regressions.

## Quality/stability regression risk note
- Smaller chunk sizing may increase boundary churn in real runtimes; visual stability risk must be checked when wiring to real MuseTalk path.
- Proxy path still does not measure true stream egress timestamps; it measures command-side anchors.

## Is proxy path close enough to begin real runtime-facing optimization?
**Yes, for controlled next-step runtime-facing optimization**, because:
- warm semantics are strict and validated,
- provenance now captures remaining major overhead classes,
- chunk-latency tradeoffs are measurable.

**No, for final production claims**, until real MuseTalk session event hooks replace proxy timing sources.
