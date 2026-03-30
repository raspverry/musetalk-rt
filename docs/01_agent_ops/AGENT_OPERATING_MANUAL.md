# AGENT OPERATING MANUAL

## Purpose
This project uses Claude Code and/or Codex as autonomous engineering agents. They are expected to perform significant implementation work, but only inside a **strict evaluation and scope-control framework**.

## Prime directive
Do not optimize the wrong thing.
The project goal is:
- perceived real-time conversational avatar behavior
- not offline video generation throughput
- not paper-first novelty
- not generalized body generation

## Operating model
Human leadership defines:
- product objective
- benchmark gates
- allowed edit surface
- experiment budget
- acceptance criteria

Agents perform:
- code reading
- patching
- refactoring
- testing
- benchmarking
- documentation updates
- proposal drafting

## Global rules
1. Never claim success without benchmark evidence.
2. Prefer contained patches to broad rewrites.
3. Separate cold-path and hot-path work.
4. Do not expand the architecture casually.
5. If quality improves but first-frame latency regresses beyond tolerance, the patch fails by default.
6. If latency improves but speaking continuity or identity visibly regresses, the patch fails by default.
7. All new flags require documentation and test coverage.
8. All risky architectural changes require an ADR entry.

## Edit surface policy
### Default mode
An agent task should modify:
- one primary target file
- plus tests
- plus minimal supporting config or docs

### Escalation mode
More than 5 source files changed requires:
- written justification
- rollback plan
- explicit benchmark plan
- architecture note

## Work packet template
Every task card should specify:
- objective
- allowed files
- forbidden files
- runtime budget
- required tests
- acceptance metrics
- expected deliverables

## Benchmark doctrine
A patch must report:
- first-frame latency
- steady-state fps
- peak VRAM
- crash/OOM status
- notable visual side effects
- whether speaking continuity improved or regressed

## Safe defaults
Prefer:
- cache reuse
- reduced disk I/O
- explicit memory ownership
- stream-friendly buffers
- measured fallbacks

Avoid:
- hidden global state
- giant framework swaps
- unmeasured compile/export changes
- invasive refactors without a gateable milestone

## Branching model
Recommended branches:
- `main` for stable baseline
- `exp/<id>-<short-name>` for experiments
- `rt/<feature>` for runtime improvements
- `res/<research-topic>` for research tracks

## Submission format
Every agent completion report must include:
### 1. Summary
What changed and why

### 2. Files changed
Exact files touched

### 3. Measurements
Before vs after numbers

### 4. Quality note
Observed visual impact

### 5. Risks
Known unknowns or edge cases

### 6. Recommendation
Ship / iterate / revert

## Failure handling
If a patch:
- crashes
- OOMs
- increases first-frame latency beyond gate
- damages speaking continuity
- breaks session flow

then:
- mark patch as failed
- keep logs and metrics
- write a short postmortem
- revert or isolate the change

## Agent priorities by phase
### Phase 1
- baseline import
- packaging
- runtime extraction
- cache isolation
- benchmark harness
- stream output path

### Phase 2
- latency optimization
- frame queue design
- compile/export exploration
- stability improvements

### Phase 3
- temporal smoothing research
- compression
- optional retraining support

## Human review checkpoints
Human approval required for:
- changing evaluation metrics
- changing acceptance gates
- changing API contracts
- adding model dependencies
- retraining plan changes
- any move toward on-device scope
