# MuseTalk-RT Documentation Pack

This pack is a working documentation set for a **server-first, perception-real-time avatar product** built by forking and productizing MuseTalk.

## Project intent
Turn MuseTalk from a research-style lip-sync repository into a production-oriented runtime for:
- fixed-avatar conversational agents
- idle-loop based avatar playback
- server-side lip-sync generation
- low-latency iPhone app streaming

## What is in this pack
- strategy docs
- agent operating docs for Claude Code / Codex
- runtime API and playback specs
- benchmark / evaluation specs
- refactor and optimization plans
- training / research notes
- ADRs for major decisions
- a `program.md` file inspired by `autoresearch`

## Recommended reading order
1. `docs/00_strategy/PROJECT_BRIEF.md`
2. `docs/00_strategy/PRODUCT_REQUIREMENTS.md`
3. `docs/00_strategy/TECHNICAL_ARCHITECTURE.md`
4. `docs/01_agent_ops/AGENT_OPERATING_MANUAL.md`
5. `docs/02_eval/EVALUATION_SPEC.md`
6. `docs/03_runtime/RUNTIME_API_SPEC.md`
7. `program.md`

## Current assumptions
- Phase 1 target is **server-side inference**, not full iPhone on-device inference.
- The product goal is **perceived real-time**, not zero-latency full-video generation.
- A single avatar is prepared once and reused across a session.
- Idle motion is looped continuously and speaking frames are streamed on top of that interaction model.
- Claude Code / Codex are expected to be used aggressively, but only inside a tightly scoped evaluation harness.

## Upstream references
- MuseTalk upstream repo: https://github.com/TMElyralab/MuseTalk
- MuseTalk technical report: https://arxiv.org/abs/2410.10122
- autoresearch repo: https://github.com/karpathy/autoresearch
- Core ML overview: https://developer.apple.com/machine-learning/core-ml/

## Important note
Some sections in this pack are intentionally written as **decision-ready operating assumptions**, not as immutable truths. Where the upstream codebase or product direction changes, update:
- ADRs
- evaluation gates
- benchmark dataset spec
- runtime API spec
