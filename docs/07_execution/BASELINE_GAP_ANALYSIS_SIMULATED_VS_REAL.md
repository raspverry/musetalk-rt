# Gap Analysis: Simulated vs Real Baseline Measurement

## Purpose
Document the difference between:
- **simulated harness mode** (deterministic scaffolding), and
- **real command baseline mode** (actual executed command timing and frame observation).

## What changed in this milestone
- Added a real-command wrapper (`benchmarks/baseline/musetalk_baseline_runner.py`) and wired harness scenarios to it.
- Preserved the existing harness report schema.
- Added separate cold-start and warm-start real scenarios.

## Remaining gaps
1. **MuseTalk model coupling not embedded in this repo**
   - Current repository is documentation + instrumentation scaffold.
   - Real MuseTalk script paths are supplied via template scenarios.

2. **First-frame measurement proxy**
   - Current real path measures first output frame file creation time.
   - Target long-term definition should use explicit runtime/event timestamps from a streaming session path.

3. **Steady-state FPS source**
   - Current real path computes FPS from output frame mtimes.
   - Target long-term should include runtime-internal produced-vs-sent frame counters.

4. **VRAM attribution granularity**
   - Current real path samples global `nvidia-smi` usage.
   - Target long-term should capture per-process attribution when concurrency increases.

## Why this is still truthful
- Measurements are taken from actual command execution and filesystem outputs, not synthetic metric injection.
- Any approximation is explicitly documented and isolated to measurement limitations.
- No optimization claims are made.

## Next integration step
- Replace template commands with pinned real MuseTalk commands and fixed assets on benchmark hosts (RTX 3070 + reference server GPU) to freeze production baseline numbers.
