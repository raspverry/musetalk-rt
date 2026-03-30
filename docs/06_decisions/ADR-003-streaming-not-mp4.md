# ADR-003: Streaming-first runtime, not MP4-first runtime

## Status
Accepted

## Context
Offline export workflows encourage waiting for a finished asset. Conversational UX requires speaking to begin as soon as enough output exists, not after full finalization.

## Decision
The canonical runtime path is:
- stream-oriented
- session-based
- start speaking as soon as threshold conditions are met

MP4 export may remain for diagnostics or offline testing, but it is not the primary product path.

## Why
- supports perceived real-time
- separates first-frame latency from full-output completion time
- aligns with iPhone playback needs

## Consequences
- backend API must expose live events and media stream semantics
- frame ownership and buffering become first-class engineering concerns
- benchmark design must include start latency and continuity
