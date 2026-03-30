# ADR-001: Server-first inference for Phase 1

## Status
Accepted

## Context
The desired product is an iPhone app with a conversational avatar. MuseTalk upstream is oriented around Python, CUDA, PyTorch, FFmpeg, and other server-style dependencies. Full iPhone on-device inference would require major portability and runtime redesign work.

## Decision
Phase 1 will use:
- iPhone as capture, playback, and session-control client
- GPU server as inference backend

## Why
- fastest path to product validation
- best alignment with current MuseTalk runtime reality
- lower technical risk
- easier benchmarking and iteration
- easier use of Claude Code / Codex on the core runtime

## Consequences
### Positive
- rapid prototyping
- cleaner runtime observability
- better control of performance tuning

### Negative
- requires network connectivity
- adds backend cost
- on-device privacy/offline benefits deferred

## Follow-up
On-device feasibility may be explored later as a separate research track, not as a blocker for Phase 1.
