# PROJECT BRIEF

## Project name
MuseTalk-RT

## One-line description
A production-oriented fork of MuseTalk optimized for **perceived-real-time conversational avatar playback** using a fixed avatar, idle loop, server-side lip-sync generation, and iPhone app streaming.

## Why this project exists
Upstream MuseTalk is a strong open-source lip-sync base, but it still behaves more like a research repository than a product runtime. The current pain points are:
- environment fragility
- heavy setup and dependency complexity
- offline-video assumptions in parts of the workflow
- unclear separation between avatar preparation and low-latency session inference
- limited packaging for app/server deployment
- real-time claims that do not directly map to product UX expectations

## Problem statement
We do not need perfect zero-latency video generation. We need an avatar product that **feels** real time:
- an idle avatar is already on screen
- the avatar starts speaking quickly after response generation begins
- the speech animation continues without visible stalls
- quality is acceptable and identity remains stable

## Product interpretation of "real-time"
For this project, real-time means **perceived responsiveness**, not raw end-to-end video export speed.
The user should feel that:
- the avatar is already alive before speaking
- the system begins speaking soon after the answer is ready enough to start
- the speaking sequence streams smoothly
- small buffering is acceptable if the first visible reaction is fast enough

## Phase 1 scope
- fork upstream MuseTalk
- modernize runtime and packaging
- separate preparation stage from session stage
- expose stream-friendly server API
- optimize for fixed-avatar conversational use
- support iPhone app playback with server-side inference

## Phase 1 non-goals
- full on-device iPhone inference
- SOTA research publication
- multi-avatar compositing
- highly dynamic body generation
- replacing all upstream model internals immediately
- full retraining before runtime value is proven

## Initial success criteria
### User-facing
- speaking starts quickly enough to feel conversational
- idle loop transitions smoothly into speaking
- users perceive the avatar as "video-like" rather than as a static image being manipulated

### Technical
- reusable avatar preparation cache
- stream-friendly speaking output
- measurable first-frame latency improvement over upstream baseline
- fewer operational dependencies and clearer deployment path

## Initial target hardware
- development sanity check: RTX 3070 laptop
- production reference: server GPU such as A10G / L4 / similar class
- iPhone client: playback, capture, session control, not heavy inference in Phase 1

## Strategic hypothesis
The biggest near-term value is not inventing a totally new lip-sync model. It is turning an existing strong model into a **session runtime** with:
- clearer architecture
- measurable latency targets
- better cache reuse
- lower I/O overhead
- better streaming semantics
- better agent-driven experimentation loops

## References
- MuseTalk repo: https://github.com/TMElyralab/MuseTalk
- MuseTalk report: https://arxiv.org/abs/2410.10122
- autoresearch: https://github.com/karpathy/autoresearch
