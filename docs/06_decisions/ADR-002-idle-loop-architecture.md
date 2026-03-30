# ADR-002: Idle-loop-based avatar architecture

## Status
Accepted

## Context
The target UX is not "generate a brand new finished video for each turn." The target UX is "the avatar feels alive and begins speaking quickly." Observed reference apps often feel video-like because an idle motion loop is already present before speaking starts.

## Decision
The product architecture will assume:
- a persistent idle loop is displayed by default
- the speaking state is streamed in response to generated audio
- transitions between idle and speaking are product-critical

## Why
- supports perceived real-time
- lets users tolerate a short thinking delay
- lowers the pressure for instant full-video generation
- better matches how people perceive conversational responsiveness

## Consequences
### Positive
- better UX with realistic backend latency
- easier illusion of continuity
- cleaner product framing for runtime work

### Negative
- requires good transition handling
- needs tighter visual compatibility between idle and speaking states
