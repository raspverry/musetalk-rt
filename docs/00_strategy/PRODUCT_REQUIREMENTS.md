# PRODUCT REQUIREMENTS

## Product
Conversational avatar system for iPhone, powered by a server-side MuseTalk-RT runtime.

## Product vision
A user talks to an on-screen avatar that appears alive even when silent. The avatar starts responding quickly, with believable mouth motion and stable identity, and the whole experience feels like a low-latency conversational video rather than a batch-rendered clip.

## Core UX principle
Optimize for **perceived real-time**:
- fast reaction
- smooth continuation
- believable idle behavior
- speaking state that looks continuous with idle state

## Primary user journey
1. App opens and avatar idle loop is already present.
2. User speaks.
3. System detects end of turn.
4. Backend begins STT/LLM/TTS pipeline.
5. As soon as the first useful TTS chunk exists, speaking frames begin streaming.
6. Avatar transitions from idle to speaking.
7. Speaking continues without obvious buffering.
8. Avatar returns to idle naturally at utterance end.

## Target UX thresholds
### Phase 1 target
- visible speaking begins within **1.2 to 2.0 seconds** after the system has enough response audio to start
- speaking playback remains continuous once started
- idle-to-speaking transition must not feel like a hard cut if avoidable

### Stretch target
- first visible speaking < 1.2 seconds
- < 250 ms frame delivery jitter once stream starts
- no disruptive stalls for typical short-form answers

## What users will forgive
- a brief thinking pause before speech begins
- slightly imperfect phoneme match
- small reductions in mouth-detail sharpness if the avatar feels responsive

## What users will not forgive
- long dead air with a frozen avatar
- speaking starts and then stutters
- identity instability frame-to-frame
- obvious "rendered clip" waiting behavior each turn

## Product priorities
1. perceived responsiveness
2. continuity of speaking playback
3. identity and face stability
4. operational reliability
5. visual fidelity
6. eventual portability and efficiency

## Functional requirements
### Must-have
- idle-loop playback
- session-based avatar selection
- reusable avatar preparation cache
- stream-oriented speaking output
- server-side TTS-to-lipsync path
- session state signaling to client
- speaking start / speaking end events
- error recovery path back to idle

### Should-have
- partial speaking start from early TTS chunks
- configurable latency vs quality modes
- avatar warm-up and prefetch
- metrics collection per session
- visual regression sample generation

### Nice-to-have
- multi-quality ladder
- fallback low-motion talking mode
- hybrid audio-only fallback with idle animation
- future feasibility path for on-device components

## Non-functional requirements
- easy reproducibility in Docker
- benchmarkable runtime
- machine-readable metrics
- CI sanity checks
- rollback-friendly architecture

## Platform scope
### Phase 1
- iPhone app front end
- GPU server backend
- WebRTC or equivalent low-latency stream/control channel
- no full on-device inference

### Phase 2
- runtime optimization
- optional TensorRT / ONNX route
- optional on-device subcomponents such as VAD / partial STT

### Phase 3
- research track for temporal stability and compression
- selective Core ML feasibility studies

## KPIs
- first-frame latency
- speaking continuity / stall rate
- frame delivery jitter
- session success rate
- average peak VRAM
- human-rated perceived naturalness
- human-rated responsiveness

## Release phases
### R0
Internal benchmarked fork, no client integration

### R1
Backend runtime with stream-capable API and benchmark harness

### R2
End-to-end iPhone prototype with idle and speaking transitions

### R3
Optimization release with measurable latency and stability improvements

### R4
Research extensions: compression, temporal module, eventual on-device exploration
