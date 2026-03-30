# STREAMING PLAYBACK SPEC

## Purpose
Define how the client should present idle and speaking states so the system feels like a real-time avatar conversation.

## UX thesis
The avatar should feel continuously alive.
Idle playback is not filler. It is part of the real-time illusion.

## Playback states
- `idle`
- `thinking`
- `speaking`
- `fallback`

## Idle state
### Requirements
- loop must be visually stable
- loop should include subtle life cues if available
- playback should continue while the backend thinks
- app must tolerate repeated looping cleanly

### Constraints
- fps and aspect ratio should match speaking mode as closely as possible
- visual style should not clash with speaking frames

## Speaking state
### Requirements
- begin as soon as speaking-start condition is met
- minimize visible discontinuity from idle
- continue until utterance end or interruption
- avoid abrupt frame cadence changes

## Transition rules
### Idle -> speaking
Trigger when:
- first speaking frames are available, and
- minimum startup buffer is satisfied

Recommended startup buffer:
- 150 to 400 ms of speaking frames for prototype
- tune after end-to-end measurement

Transition style:
- hard switch acceptable for internal prototype
- short blend preferred for product prototype if it does not add latency

### Speaking -> idle
Trigger when:
- speaking frames complete, or
- utterance cancelled, or
- system falls back

Transition style:
- brief settle period preferred
- do not visibly freeze before returning to idle

## Thinking state
If used, this should be idle-plus:
- subtle UI or animation cue
- no heavy motion change
- should not delay speaking start

## Fallback state
If speaking stream fails:
- continue idle loop
- optionally play audio-only response
- optionally show subtle recovery indicator
- never leave the avatar frozen on a broken speaking frame

## Buffering policy
### Goal
Optimize for quick start without future stalls.

### Initial recommendation
- keep a small startup buffer
- prioritize continuous playback after start
- adapt buffer size by network condition

## Interruption handling
If user interrupts:
- stop current speaking stream
- return cleanly to idle
- do not finish old utterance visually unless product explicitly wants barge-in disabled

## Visual continuity requirements
- same resolution class
- same crop framing
- stable eye and face region alignment
- no obvious brightness jump between idle and speaking

## Metrics
Track:
- time from `speaking_started` event to visible playback
- transition artifact rate
- stall count
- fallback frequency
