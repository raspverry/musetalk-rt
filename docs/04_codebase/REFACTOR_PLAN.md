# REFACTOR PLAN

## Goal
Restructure the fork so that the product path is clean, benchmarkable, and stream-oriented.

## Current problem
Upstream MuseTalk appears to expose:
- normal inference path
- realtime inference path
- demo path

But these are not yet organized as a product-ready runtime with explicit session lifecycle and clean backend API boundaries.

## Refactor objectives
1. isolate avatar preparation
2. isolate hot-path speaking runtime
3. make stream-oriented output first-class
4. reduce file-system coupling
5. add metrics and benchmark hooks
6. keep rollback path simple

## Refactor phases

### Phase 1 — Inventory and wrappers
- clone upstream baseline
- add repo map notes
- wrap existing realtime path without major internal changes
- create benchmark harness around current runtime

### Phase 2 — Cold/hot split
- extract avatar preparation manager
- define runtime session object
- define cache schema
- make warm path explicit

### Phase 3 — Streamable output
- replace MP4-first assumptions in hot path
- create frame queue / transport abstraction
- emit speaking lifecycle events

### Phase 4 — Runtime cleanup
- reduce disk writes
- reduce unnecessary ffmpeg dependence
- clarify memory ownership
- unify config loading and runtime flags

### Phase 5 — Optimization
- mixed precision matrix
- compile / export experiments
- frame queue tuning
- temporal smoothing experiments

## Suggested module layout for the fork
- `runtime/engine.py`
- `runtime/session.py`
- `runtime/cache.py`
- `runtime/stream.py`
- `runtime/metrics.py`
- `benchmarks/`
- `api/`
- `adapters/upstream/`

## Refactor guardrails
- benchmark at every stage
- keep visual sample comparison
- avoid "clean architecture" rewrites without runtime payoff
- preserve ability to compare to upstream baseline

## Rollback strategy
Every large refactor step must be:
- isolated by branch
- benchmarked
- reversible without losing baseline runner

## Exit criteria
Refactor phase is successful when:
- hot path is callable as a reusable runtime
- preparation is explicit and reusable
- client/backend integration can consume stream semantics
- basic metrics are automatic
