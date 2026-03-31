# Foundation Plan and Baseline Harness (Phase 0 -> Phase 1)

## Scope and constraints
This plan follows the repository source-of-truth docs:
- server-first runtime and session semantics
- streaming-first, not MP4-first
- explicit cold-path (avatar prep) vs hot-path (speaking)
- no unmeasured optimization claims
- no major architectural rewrite before ADR

---

## 1) Proposed repository structure

```text
musetalk-rt/
  runtime/
    api/                # REST + event contracts and handlers
    session/            # session + utterance lifecycle/state machine
    avatar/             # preparation pipeline + cache manager
    streaming/          # frame queue, transport-facing stream interfaces
    metrics/            # metric event emitters and aggregators

  benchmarks/
    baseline/
      benchmark_harness.py
      scenarios/
      reports/
      README.md

  docs/
    07_execution/
      FOUNDATION_PLAN_AND_BASELINE.md
```

Design intent:
- `runtime/avatar` is cold-path and cache-centric.
- `runtime/session` + `runtime/streaming` are hot-path and low-latency.
- `benchmarks/baseline` is the stable gate for optimization claims.

---

## 2) First 2-week sprint plan

### Week 1: baseline and plumbing (P0)
1. **Benchmark harness v1 hardening**
   - Implement cold/warm scenario configs.
   - Lock report schema.
   - Add run metadata (commit SHA, GPU profile, precision mode).
2. **Runtime interface contract draft**
   - Add a minimal runtime command contract that returns benchmark JSON.
   - Add event timeline markers required for first-frame measurement.
3. **Session skeleton**
   - Define states: `initializing -> avatar_warming -> idle_ready -> thinking -> speaking -> idle_ready`.
4. **Avatar prep contract**
   - Define `prepare_avatar` and `load_prepared_avatar` interface signatures.

Exit criteria (end of week 1):
- Harness runs reproducibly and produces comparable JSON reports for cold/warm tests.

### Week 2: measurable baseline on real runtime (P0)
1. **Connect command adapter to real runtime path**
   - Wire runtime to emit required metrics fields.
2. **Collect baseline matrix**
   - Profile A: RTX 3070 local.
   - Profile B: reference server GPU (A10G/L4 class).
3. **Crash/OOM characterization pass**
   - Sweep 2-3 stress conditions (long utterance, high concurrency, larger avatar set).
4. **Baseline freeze**
   - Save reports and lock baseline numbers for future comparisons.

Exit criteria (end of week 2):
- A versioned baseline report exists for all five target metrics.

---

## 3) Benchmark harness design

## Objective
Provide a repeatable harness with machine-readable output for:
- avatar preparation time
- first-frame latency
- steady-state FPS
- peak VRAM
- crash/OOM behavior

## Components
- `benchmark_harness.py`
  - Loads scenario JSON.
  - Runs N iterations.
  - Supports `simulated` and `command` adapters.
  - Aggregates mean/p50/p95/min/max.
  - Emits JSON report.
- `scenarios/*.json`
  - Cold/warm profile definitions.
- `reports/*.json`
  - Stored benchmark artifacts for PR review and trend tracking.

## Measurement conventions
- **avatar preparation time**: elapsed from prep start to cache-ready signal (cold path only).
- **first-frame latency**: elapsed from first usable TTS chunk to first speaking frame ready.
- **steady-state FPS**: average speaking FPS excluding startup buffer window.
- **peak VRAM**: max sampled GPU memory used during run (via `nvidia-smi` when available).
- **crash/OOM behavior**: status counts per scenario (`ok`, `crash`, `oom`, `error`).

## Report schema (v1)
Top-level keys:
- `scenario`
- `summary`
- `results`
- `generated_at_epoch_ms`

---

## 4) Task breakdown

### Track A: benchmark foundation
- A1: stabilize scenario schema + validation
- A2: add environment metadata (GPU, precision, runtime commit)
- A3: add CSV exporter for dashboard ingestion
- A4: add CI dry-run benchmark target

### Track B: runtime instrumentation
- B1: emit prep start/ready timestamps
- B2: emit first-frame event timestamp
- B3: emit FPS counters every speaking window
- B4: emit failure reason taxonomy (OOM/timeout/runtime crash)

### Track C: session + streaming readiness
- C1: session state machine module skeleton
- C2: utterance lifecycle IDs and event correlation
- C3: frame queue contract (producer/consumer backpressure)
- C4: fallback signaling contract (`fallback_entered`, `error`)

### Track D: operations and reproducibility
- D1: benchmark artifact retention policy
- D2: profile configs (3070 vs server)
- D3: runbook for baseline collection
- D4: regression gate policy for PRs

---

## 5) Risk list

1. **Metric ambiguity risk**
   - Risk: inconsistent first-frame definition across teams.
   - Mitigation: fix event-based definition and enforce it in harness docs and runtime instrumentation.

2. **Cold/warm contamination risk**
   - Risk: warm tests accidentally trigger prep work.
   - Mitigation: explicit cache-ready precheck and scenario preconditions.

3. **VRAM observability gaps**
   - Risk: missing `nvidia-smi` in some environments.
   - Mitigation: allow null VRAM with warning and require VRAM on reference benchmark hosts.

4. **False optimization claims risk**
   - Risk: noisy measurements interpreted as gains.
   - Mitigation: run multiple iterations, report p50/p95, and require baseline diff against frozen reports.

5. **Streaming semantics drift risk**
   - Risk: hot path regresses into MP4/file-centric behavior.
   - Mitigation: maintain API/state contracts with streaming-first events and add regression checks.

6. **OOM under burst load risk**
   - Risk: acceptable single-session behavior but poor concurrent stability.
   - Mitigation: include stress scenario variants and explicit OOM tracking in summary.

7. **Uncontrolled architecture expansion risk**
   - Risk: broad rewrites before measurable baseline.
   - Mitigation: ADR gate for major architecture change; prioritize incremental modules and instrumentation.

