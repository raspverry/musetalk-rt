# Project Status

- Language: **EN** | [KO](PROJECT_STATUS.ko.md) | [JA](PROJECT_STATUS.ja.md)

## Project identity
MuseTalk-RT is the validation/productization layer for a MuseTalk-derived runtime candidate, targeting perceived real-time conversational avatar sessions.

## What is done / what is left

### Done
1. Warm-path policy operationalized.
2. Lifecycle validation stack operationalized end-to-end.
3. Four key lifecycle stages provisionally real-wired on flagged path.
4. 30-run flagged reliability with zero fallback and zero lifecycle stage errors.
5. Stress validation under bursty/jittery with lifecycle stability preserved.
6. Quality telemetry distinguishes stable vs degraded conditions.
7. Human-QA pack + scorecard + decision layer implemented.
8. Local GUI and multilingual documentation available.

### Left
1. Collect real reviewer scores in repeated sessions.
2. Complete canary evidence package with human-rated quality.
3. Validate mobile/network-like perceptual behavior with human evidence.
4. Define broader readiness gates beyond flagged canary.

## What would count as canary-ready?
- Human scorecards completed for stable/bursty/jittery representative sets.
- Decision layer reaches `GO_WARN_ONLY_CANARY` on agreed thresholds.
- No contradictory reliability/fallback regressions in latest flagged runs.
- Rollback triggers and operational owner are explicitly documented.

## What would count as broader product-ready?
- Repeated multi-reviewer evidence over time (not one-off).
- Inter-rater agreement on continuity/naturalness quality.
- Proven rollback and monitoring posture for real deployments.
- Scope expansion beyond flagged non-production approved by stakeholders.

## Still experimental
- Full perceptual confidence without human review data.
- Broad deployment claims.
- Production UI/orchestration assumptions.
