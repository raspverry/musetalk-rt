# MuseTalk-RT: Productization + Validation Stack for a MuseTalk Runtime Candidate

- Language: **English** | [한국어](README.ko.md) | [日本語](README.ja.md)

## What is this project?
MuseTalk-RT is a **productization and validation stack** for a MuseTalk-based perceived real-time conversational avatar runtime candidate.

This repository is **not** a full production runtime yet. It is the flagged, non-production layer used to make the runtime candidate measurable, debuggable, trustworthy, and canary-ready.

## Project north star
Build a MuseTalk-derived runtime candidate toward a perceived real-time conversational avatar system, then graduate it from flagged non-production validation into controlled canary readiness with human-validated quality evidence.

## Current status (concise)
See [docs/PROJECT_STATUS.md](docs/PROJECT_STATUS.md) for details.

### Completed (high level)
- Warm-path policy defined and operationalized.
- End-to-end lifecycle validation stack in place (readiness → dry-run → smoke → tiny real → lifecycle-aware → flagged e2e).
- Four key lifecycle stages provisionally real-wired on flagged path.
- 30-run flagged reliability pass with zero fallback and zero lifecycle stage errors.
- Stress validation under bursty/jittery conditions with preserved lifecycle stability.
- Quality telemetry and human-QA pack/scorecard/decision layer implemented.
- Local GUI + multilingual docs available.

### Remaining (high level)
- Collect real human reviewer scores at scale.
- Complete canary evidence package.
- Validate mobile/network-like perceptual behavior with human evidence.
- Establish broader product-readiness evidence beyond flagged scope.

## What this repo currently is
- Runtime validation + productization layer for a runtime candidate.
- Flagged, non-production experimentation and evidence-building stack.
- Decision support layer for GO/WARN/NO-GO canary outcomes.

## What this repo is not (yet)
- Not a production orchestration layer.
- Not a broad deployment/monitoring/rollback platform.
- Not a finalized production UI.

## Typical workflow
1. Read [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md).
2. Run reliability/quality/stress workflows.
3. Build human-QA pack and fill scorecard.
4. Evaluate decision summary.
5. Assess canary readiness against explicit thresholds.

## Execution readiness docs
- Reviewer handoff: [docs/REVIEWER_HANDOFF.md](docs/REVIEWER_HANDOFF.md)
- Maintainer decision checklist: [docs/MAINTAINER_DECISION_CHECKLIST.md](docs/MAINTAINER_DECISION_CHECKLIST.md)

## What is still experimental?
- Full perceptual confidence still depends on collected human scores.
- Canary evidence is still being completed.
- Broader product-readiness remains unproven.

## How to run QA
See [docs/QA_WORKFLOW.md](docs/QA_WORKFLOW.md).

## How to interpret GO_WARN_ONLY_CANARY / WARN_ONLY_HOLD / NO_GO
See [docs/REPORTS_AND_DECISIONS.md](docs/REPORTS_AND_DECISIONS.md).

## Local GUI (Streamlit)
A lightweight local dashboard is available at `app/qa_dashboard.py`.

```bash
pip install streamlit
streamlit run app/qa_dashboard.py
```

## New teammate: read this first (10-minute path)
1. [docs/PROJECT_STATUS.md](docs/PROJECT_STATUS.md)
2. [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md)
3. [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
4. [docs/QA_WORKFLOW.md](docs/QA_WORKFLOW.md)
5. [docs/REPORTS_AND_DECISIONS.md](docs/REPORTS_AND_DECISIONS.md)
6. [docs/ROADMAP.md](docs/ROADMAP.md)
