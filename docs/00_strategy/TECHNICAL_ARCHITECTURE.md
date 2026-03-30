# TECHNICAL ARCHITECTURE

## Architectural thesis
Treat MuseTalk-RT as a **session-oriented face animation runtime**, not as a conventional offline video renderer.

## High-level system
### Client: iPhone app
Responsibilities:
- microphone capture
- VAD / turn-taking UI
- idle loop playback
- stream playback
- session control
- fallback UX if stream stalls

### Backend services
1. Session manager
2. STT service
3. Dialogue service (LLM or orchestration)
4. TTS service
5. MuseTalk-RT runtime
6. Metrics / logging service
7. Asset and cache manager

## Core dataflow
1. `avatar_id` selected or restored.
2. Avatar preparation is checked.
3. If cache missing, backend prepares avatar once.
4. App displays idle loop while user speaks.
5. User audio reaches backend.
6. STT and response generation run.
7. TTS starts emitting chunks.
8. MuseTalk-RT ingests early TTS chunks and generates speaking frames.
9. Frames are streamed to client.
10. Client switches idle -> speaking playback.
11. On utterance completion, playback transitions back to idle.

## Key architectural split
### Cold path
Preparation and asset loading:
- face detection and alignment
- mask preparation
- bbox tuning data
- frame indexing
- avatar-specific cache
- optional idle-loop normalization

### Hot path
Per-turn speaking runtime:
- chunked response audio ingestion
- audio feature extraction
- lip-sync inference
- speaking frame transport
- playback signaling

This split is the most important productization decision.

## Recommended component boundaries
### `avatar-prep-service`
Input:
- avatar asset pack
Output:
- reusable preparation cache
- avatar metadata
- quality warnings

### `speech-orchestrator`
Input:
- user audio stream
Output:
- response text
- response audio chunks
- speaking start signal

### `musetalk-rt-engine`
Input:
- avatar preparation cache
- response audio chunk(s)
Output:
- speaking frame stream
- timing metadata
- quality/latency metrics

### `stream-gateway`
Input:
- speaking frames + control events
Output:
- WebRTC or equivalent stream to client

## Session state
Each session should maintain:
- `session_id`
- `avatar_id`
- cache availability
- speaking state
- current utterance id
- playback clock reference
- metrics buffer
- failure state / fallback mode

## Suggested deployment topology
### Minimum viable deployment
- one GPU backend node
- one app API node
- one metrics store

### Recommended production-ready topology
- stateless API nodes
- GPU runtime worker pool
- persistent avatar asset store
- shared metrics / tracing backend
- optional TTS worker isolation

## Stream/control separation
Prefer separate semantics for:
- control events: start/ready/end/error
- media payload: frames / encoded low-latency video units
- metrics / telemetry: async reporting

## Why not MP4-first
MP4-first is wrong for conversational UX because:
- file finalization adds avoidable delay
- it hides first-frame latency behind total export time
- it encourages batch workflows
- it complicates rapid interruption and turn-taking

## Packaging goals
- Docker-first operation
- pinned dependencies
- explicit GPU support matrix
- benchmark command that works locally and in CI
- clean interface between upstream-like code and product runtime wrappers

## Near-term architecture milestones
1. baseline upstream mirror
2. preparation cache abstraction
3. runtime hot-path extraction
4. streaming output interface
5. metrics harness
6. client integration

## Technology notes
### Likely backend stack
- Python runtime initially
- FastAPI / WebSocket or WebRTC control plane
- FFmpeg minimized, not central to hot path
- PyTorch first, export/compile options later

### Likely client stack
- Swift / SwiftUI
- AVFoundation
- low-latency media rendering
- simple state machine for idle / speaking / fallback

## Architecture risks
- upstream code paths may entangle offline and real-time logic
- FFmpeg and file-oriented assumptions may leak into hot path
- avatar preparation cost may be underestimated
- TTS chunking semantics may not align cleanly with existing realtime_inference path
- streamable output may require substantial refactor around frame ownership and buffer lifecycle
