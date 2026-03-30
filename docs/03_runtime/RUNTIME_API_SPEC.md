# RUNTIME API SPEC

## Purpose
Define the server-side API contract for the iPhone app and backend orchestration.

## API style
Use a hybrid model:
- REST for session and asset lifecycle
- WebSocket or WebRTC data/control channel for live conversation events
- optional HTTP endpoints for diagnostics and offline tests

## Core entities
- `session`
- `avatar`
- `utterance`
- `stream`
- `metrics`

---

## REST endpoints

### `POST /v1/sessions`
Create a new session.

**Request**
```json
{
  "avatar_id": "avatar_001",
  "quality_mode": "balanced"
}
```

**Response**
```json
{
  "session_id": "sess_123",
  "avatar_id": "avatar_001",
  "prep_status": "warming"
}
```

### `POST /v1/sessions/{session_id}/avatar/load`
Load or switch avatar for a session.

### `GET /v1/sessions/{session_id}/avatar/status`
Return:
- prep cache status
- warnings
- current bbox/profile metadata

### `POST /v1/sessions/{session_id}/utterances`
Create a new utterance object.

### `POST /v1/sessions/{session_id}/utterances/{utterance_id}/audio`
Send or attach generated response audio for non-streaming fallback mode.

### `POST /v1/sessions/{session_id}/close`
Close a session and release resources.

### `GET /v1/sessions/{session_id}/metrics`
Return current session metrics.

---

## Live control channel events

### Client -> server
- `user_audio_chunk`
- `user_turn_end`
- `cancel_utterance`
- `ping`

### Server -> client
- `session_ready`
- `avatar_prep_started`
- `avatar_prep_ready`
- `response_started`
- `tts_chunk_ready`
- `speaking_started`
- `speaking_progress`
- `speaking_ended`
- `fallback_entered`
- `error`

## Event payload examples

### `speaking_started`
```json
{
  "session_id": "sess_123",
  "utterance_id": "utt_456",
  "timestamp_ms": 1712345678,
  "mode": "stream"
}
```

### `error`
```json
{
  "session_id": "sess_123",
  "code": "RUNTIME_TIMEOUT",
  "message": "Speaking frames did not begin within latency budget"
}
```

## Media path
Preferred Phase 1 options:
1. WebRTC low-latency video stream
2. WebSocket binary frame stream for prototype mode

## State machine
### Session states
- `initializing`
- `avatar_warming`
- `idle_ready`
- `listening`
- `thinking`
- `speaking`
- `fallback`
- `closing`

### Utterance states
- `created`
- `awaiting_audio`
- `tts_streaming`
- `speaking_streaming`
- `done`
- `cancelled`
- `failed`

## API guarantees
- `session_ready` means the idle state is usable
- `avatar_prep_ready` means warm-start speaking generation is allowed
- `speaking_started` should only be emitted when the client can begin transition to speaking
- errors must include recoverability hint when possible

## Observability fields
Every event should optionally include:
- `trace_id`
- `session_id`
- `utterance_id`
- `latency_ms`
- `server_ts`

## Notes
Do not design the API around MP4 completion semantics. The canonical product path is streaming-oriented.
