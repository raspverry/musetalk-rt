# AVATAR PREPARATION SPEC

## Purpose
Specify how avatars are prepared, cached, and reused for session-based runtime.

## Key idea
Avatar preparation is a **cold-path asset compilation step**. It should not be repeated during normal conversational use unless the avatar asset or prep settings change.

## Avatar asset pack
Each avatar should eventually be represented as an asset pack containing:
- source idle loop or source video
- canonical thumbnail
- metadata
- prep profile
- optional tuned bbox settings
- version identifier

## Preparation outputs
Preparation should produce:
- aligned face references
- crop / bbox metadata
- masks and face region data
- frame indexing
- runtime-ready cache blobs
- quality warnings if detected

## Preparation triggers
Preparation occurs when:
- avatar first imported
- prep profile changes
- source asset changes
- cache is invalid or missing
- runtime version makes cache incompatible

## Warm vs cold behavior
### Cold path
- may take noticeable time
- should happen before conversation begins whenever possible
- can run during app loading or avatar selection

### Warm path
- should reuse existing cache
- should be the default for all live utterances
- is the basis for perceived real-time behavior

## Cache invalidation rules
Invalidate cache when:
- avatar source content changes
- prep parameters materially change
- runtime cache schema changes
- model version compatibility changes
- resolution/crop assumptions change

## Cache version fields
Store:
- `avatar_id`
- source asset hash
- runtime version
- prep pipeline version
- bbox_shift setting
- target fps
- target resolution
- created_at

## Operator controls
Allow operators to adjust:
- bbox_shift
- target fps normalization
- crop policy
- quality mode

## Product requirements
- the app should never silently wait for cold prep during a live utterance if it can be avoided
- avatars likely to be used should be prewarmed
- the user should see idle as soon as possible, even if backend prep is still finishing

## Recommended engineering tasks
- explicit cache manager abstraction
- cache health check endpoint
- cache invalidation audit logging
- warm-path benchmark command
