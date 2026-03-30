# TEMPORAL RESEARCH NOTES

## Context
MuseTalk is fundamentally attractive for productization, but a known limitation of single-frame or weakly temporal generation is frame-to-frame jitter and local instability.

## Research question
How can we improve temporal stability without destroying the latency profile that makes conversational use viable?

## Candidate approaches

### 1. Post-process temporal smoothing
Examples:
- EMA-style mouth region stabilization
- optical-flow-guided blending
- lightweight temporal consistency filter

**Pros**
- no retraining required
- good first experiment

**Cons**
- can blur details
- can add lag or ghosting

### 2. Lightweight recurrent cache
Introduce limited state across adjacent speaking frames.

**Pros**
- may improve continuity

**Cons**
- architecture complexity
- harder export and benchmarking

### 3. Temporal convolution / transformer head
Small temporal module on top of existing runtime.

**Pros**
- more principled temporal modeling

**Cons**
- likely retraining
- more latency risk

### 4. Distilled temporal variant
Train a runtime-oriented model variant for session inference.

**Pros**
- potentially best long-term result

**Cons**
- biggest investment
- needs strong dataset and evaluation plan

## Product caution
Temporal improvements should be judged against:
- first-frame latency
- speaking continuity
- identity stability
- artifact suppression

A temporal method that lowers jitter but delays speaking start too much may be wrong for this product.

## Suggested order
1. benchmark jitter in current baseline
2. try post-process smoother
3. try limited-state runtime experiment
4. only then consider retraining-backed temporal module

## Required evaluation additions
- side-by-side video review
- temporal stability score or proxy
- subjective "feels more alive" evaluation
