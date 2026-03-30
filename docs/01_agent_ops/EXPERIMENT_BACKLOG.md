# EXPERIMENT BACKLOG

## Purpose
Maintain a prioritized experiment queue for runtime optimization, productization, and research.

## Priority legend
- P0: unblock product path
- P1: major latency/stability upside
- P2: medium-value optimization
- P3: research or optional exploration

---

## EXP-001 — Baseline benchmark harness
**Priority:** P0  
**Hypothesis:** Without a stable baseline harness, all later optimization work will be noisy and hard to trust.  
**Scope:** add repeatable benchmark commands and structured output  
**Metrics:** first-frame latency, steady fps, peak VRAM, crash rate  
**Success:** reproducible benchmark output on reference hardware

## EXP-002 — Preparation cache extraction
**Priority:** P0  
**Hypothesis:** Separating avatar preparation from hot-path speaking generation will materially improve perceived latency.  
**Scope:** factor cache creation and reuse into explicit API/runtime module  
**Metrics:** cold-start vs warm-start latency  
**Success:** warm-start first-frame latency materially lower than cold-start

## EXP-003 — Remove disk writes from hot path
**Priority:** P0  
**Hypothesis:** image saving / file-based intermediates are hurting hot-path responsiveness.  
**Scope:** replace intermediate saves with in-memory frame flow where possible  
**Metrics:** first-frame latency, avg fps  
**Success:** measurable latency reduction without quality regression

## EXP-004 — Frame queue / streaming interface
**Priority:** P0  
**Hypothesis:** stream-friendly frame ownership will make iPhone integration straightforward and lower end-to-end perceived delay.  
**Scope:** create output queue contract for speaking frames  
**Metrics:** speaking start timing, stream continuity  
**Success:** backend can emit streamable frames/events without MP4 finalize step

## EXP-005 — Turn-start from partial TTS
**Priority:** P1  
**Hypothesis:** starting speaking from the first useful TTS chunk will improve UX even if full answer audio is not ready.  
**Scope:** chunked audio ingestion path  
**Metrics:** speaking start latency, stall rate  
**Success:** earlier start with acceptable continuity

## EXP-006 — `torch.compile` evaluation
**Priority:** P1  
**Hypothesis:** compile may help steady-state throughput or hot-path latency on server GPUs.  
**Scope:** runtime-only compile experiment  
**Metrics:** compile overhead, steady fps, first-frame latency  
**Success:** useful gain without unacceptable warm-up cost

## EXP-007 — FP16/BF16 runtime matrix
**Priority:** P1  
**Hypothesis:** mixed precision can lower VRAM and improve speed with tolerable quality impact.  
**Scope:** runtime inference precision sweep  
**Metrics:** VRAM, fps, artifact rate  
**Success:** one precision mode chosen as default and one as fallback

## EXP-008 — Low-latency media transport prototype
**Priority:** P1  
**Hypothesis:** WebRTC-style delivery will outperform naive file or chunk polling for app UX.  
**Scope:** transport proof of concept  
**Metrics:** delivery jitter, start latency  
**Success:** stable low-jitter speaking playback demo

## EXP-009 — Lightweight temporal smoothing
**Priority:** P2  
**Hypothesis:** a post-filter can reduce single-frame jitter without retraining.  
**Scope:** optional post-processing module  
**Metrics:** visual stability score, human preference  
**Success:** reduced jitter with minimal added latency

## EXP-010 — Bbox and avatar prep parameter caching
**Priority:** P2  
**Hypothesis:** per-avatar tuning metadata should be stored and reused instead of re-discovered.  
**Scope:** prep metadata persistence  
**Metrics:** prep time, operator intervention rate  
**Success:** less manual tuning per avatar

## EXP-011 — ONNX feasibility
**Priority:** P2  
**Hypothesis:** exportable subgraphs may unlock later runtime improvements or deployment portability.  
**Scope:** feasibility study only  
**Metrics:** export coverage, numerical parity, runtime delta  
**Success:** documented go/no-go

## EXP-012 — TensorRT feasibility
**Priority:** P2  
**Hypothesis:** if major runtime blocks can be exported cleanly, TensorRT may improve server economics.  
**Scope:** selective proof of concept  
**Metrics:** first-frame latency, steady fps, engineering cost  
**Success:** documented go/no-go with blockers

## EXP-013 — Idle-to-speaking transition controller
**Priority:** P1  
**Hypothesis:** a better transition controller will improve perceived naturalness more than a small lip-sync metric gain.  
**Scope:** playback-state controller and blend logic  
**Metrics:** human-rated naturalness, transition artifacts  
**Success:** better subjective UX without slowing start

## EXP-014 — Benchmark on 3070 laptop and server GPU
**Priority:** P0  
**Hypothesis:** local-dev and server-prod numbers differ enough that both must be tracked.  
**Scope:** dual-hardware benchmark profiles  
**Metrics:** all core runtime metrics by hardware tier  
**Success:** performance matrix available in repo docs

## EXP-015 — Failure-mode fallback path
**Priority:** P1  
**Hypothesis:** a graceful fallback to idle/audio-only or lower-motion speaking mode improves product resilience.  
**Scope:** runtime fallback and client signaling  
**Metrics:** session success rate, recovery behavior  
**Success:** sessions degrade gracefully instead of hard failing
