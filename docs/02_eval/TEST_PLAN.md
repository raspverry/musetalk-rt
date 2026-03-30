# TEST PLAN

## Purpose
Define the testing pyramid for MuseTalk-RT.

## Test layers
### 1. Unit tests
Validate:
- config parsing
- cache metadata handling
- state transitions
- timing calculations
- frame queue interfaces

### 2. Integration tests
Validate:
- avatar preparation flow
- speaking generation flow
- session lifecycle
- API event ordering
- idle/speaking control signaling

### 3. Performance tests
Validate:
- cold-start latency
- warm-start latency
- steady fps
- memory use
- stall behavior

### 4. Visual regression tests
Validate:
- speaking sample output vs baseline
- jitter changes
- identity stability changes
- transition behavior

### 5. End-to-end tests
Validate:
- iPhone client can connect
- session starts successfully
- speaking frames begin after audio response starts
- client returns to idle cleanly

## Minimum CI test suite
- smoke runtime import test
- one tiny avatar prep test
- one tiny speaking runtime test
- one API contract test
- one benchmark config dry run

## Release candidate test suite
- full runtime benchmark subset
- visual review subset
- fallback mode test
- restart and recovery test
- repeated session reuse test

## Failure classes to watch
- GPU OOM
- broken cache invalidation
- frame ordering bugs
- start/stop race conditions
- stalls caused by transport
- mismatch between idle and speaking aspect/fps settings

## Test artifact policy
Every integration/performance run should preserve:
- logs
- config snapshot
- metrics JSON
- minimal visual artifacts if storage allows
