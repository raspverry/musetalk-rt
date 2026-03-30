# ADR-004: Avatar preparation cache reuse is a first-class product feature

## Status
Accepted

## Context
Upstream realtime guidance distinguishes between preparing a new avatar and reusing the same avatar for further generation. Product UX depends on warm-start behavior, not just cold-start behavior.

## Decision
Avatar preparation cache reuse is part of the core architecture, not an implementation detail.

## Why
- warm-start performance is essential for perceived real-time
- repeated prep during live use is wasteful
- session behavior becomes more predictable

## Consequences
- explicit cache manager required
- cache invalidation policy required
- benchmarking must separate cold and warm paths
- avatar asset packs should include prep metadata where possible
