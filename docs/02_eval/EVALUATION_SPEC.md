# EVALUATION SPEC

## Purpose
Define how progress is measured so that autonomous agents optimize the right outcomes.

## Evaluation philosophy
This project should not use a single scalar metric as its only truth. We need:
- hard gates for failure
- weighted score for optimization
- human visual review for quality-sensitive changes

## Evaluation levels
### Level 0 — Smoke
Does it run at all?

### Level 1 — Runtime benchmark
Latency, fps, memory, stability

### Level 2 — Visual benchmark
Lip-sync credibility, identity, jitter, mouth artifacts

### Level 3 — UX benchmark
Perceived responsiveness and continuity in end-to-end conversational flow

## Core runtime metrics
- avatar preparation time
- warm-start first-frame latency
- cold-start first-frame latency
- steady-state speaking fps
- frame delivery jitter
- peak VRAM
- CPU utilization
- crash rate
- OOM rate

## Core quality metrics
- lip-sync score (tool-based and/or proxy-based)
- identity preservation score
- temporal stability / jitter score
- mouth artifact rate
- human preference score
- transition smoothness score

## End-to-end product metrics
- time from end of user turn to first visible speaking
- time from first TTS chunk available to first visible speaking
- speaking stall count per utterance
- recoverability after transient backend issues

## Hard gates (initial)
A run fails if any of the following occur:
- crash
- OOM
- output unusable for visual review
- warm-start first-frame latency > 2.0 s on reference server GPU
- average speaking fps < 20 on reference server GPU
- severe identity breakage in review sample
- speaking continuity stall > 500 ms in standard test utterance

## Weighted score (initial)
For patches that pass the hard gates:

- first-frame latency: 35%
- speaking continuity / jitter: 25%
- identity stability: 15%
- lip-sync quality: 15%
- peak VRAM: 5%
- implementation complexity penalty: 5%

## Hardware profiles
### Profile A — Local dev sanity
- RTX 3070 laptop
- used for developer feedback and relative trend tracking
- not the sole ship criterion

### Profile B — Reference server
- A10G, L4, or similar production-credible GPU
- primary acceptance benchmark

## Benchmark protocol
1. run cold-start benchmark
2. run warm-start benchmark
3. run speaking continuity benchmark
4. collect 3 visual samples
5. log structured metrics JSON
6. store one short reviewer note

## Visual review rubric
### 1 — unacceptable
severe mouth artifacts, broken identity, unusable

### 2 — poor
noticeable artifacts or jitter, only useful for internal debugging

### 3 — acceptable
good enough for iteration, still visibly imperfect

### 4 — good
natural enough for product prototype

### 5 — excellent
hard to notice artifacts in normal use

## Acceptance policy
A patch may be accepted when:
- it passes hard gates
- it improves weighted score, or
- it keeps weighted score flat while materially reducing operational complexity

A patch should usually be rejected when:
- it worsens first-frame latency for small visual gains
- it improves one metric by harming speaking continuity
- it creates future maintenance burden without clear upside

## Required outputs from every benchmark run
- machine-readable metrics file
- benchmark environment summary
- git commit SHA
- model/runtime config
- sample artifacts or links
- short reviewer note

## Notes
These thresholds are starting values. After baseline collection, update this file and add an ADR if thresholds materially change.
