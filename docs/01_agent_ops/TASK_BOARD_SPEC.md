# TASK BOARD SPEC

## Purpose
Standardize the task format given to Claude Code / Codex so that each task is self-contained, benchmarkable, and easy to review.

## Task card schema

### Header
- Task ID
- Title
- Priority
- Owner agent
- Date opened
- Status

### Goal
One paragraph describing the concrete outcome.

### Why now
Explain the product or technical reason this task matters.

### Allowed edit surface
List exact files or directories that may be changed.

### Forbidden changes
List files, systems, or behaviors that must not change.

### Inputs
Relevant docs, benchmark configs, issue references, or ADRs.

### Runtime budget
Specify maximum time allowed for:
- implementation
- benchmark run
- optional extended validation

### Required tests
List:
- unit tests
- integration tests
- performance tests
- visual sample generation

### Acceptance criteria
Use measurable criteria.

### Deliverables
Must include:
- code patch
- benchmark report
- brief quality note
- rollback note if applicable

## Example task card

### Task ID
RT-014

### Title
Remove image-save dependency from hot path

### Priority
P1

### Goal
Reduce hot-path latency by avoiding intermediate image serialization during speaking frame generation.

### Why now
The product goal is perceived real-time conversational playback, and image serialization is a likely avoidable contributor to first-frame delay and overall runtime overhead.

### Allowed edit surface
- `scripts/realtime_inference.py`
- `musetalk/runtime/*`
- `tests/test_realtime_path.py`
- docs updates if needed

### Forbidden changes
- no changes to model weights
- no changes to training code
- no client API contract changes

### Inputs
- `EVALUATION_SPEC.md`
- `REFACTOR_PLAN.md`
- `ADR-003-streaming-not-mp4.md`

### Runtime budget
- implementation: 4 hours max
- benchmark: 30 minutes max

### Required tests
- smoke test
- benchmark on small avatar/audio subset
- visual regression sample x 3

### Acceptance criteria
- first-frame latency improves by >= 10%
- no quality regression rated "major"
- no OOM
- speaking continuity not worse

### Deliverables
- patch
- benchmark JSON
- before/after numbers
- one-paragraph risk note
