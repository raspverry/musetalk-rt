# MuseTalk-RT (Flagged, Non-Production Evaluation Toolkit)

- Language: **English** | [한국어](README.ko.md) | [日本語](README.ja.md)

## What is this project?
MuseTalk-RT is a **local evaluation and QA toolkit** for testing MuseTalk-style session startup and continuity behavior.
It is not a production app. It helps teams compare stable vs disturbed conditions, review lifecycle telemetry, run human QA, and make guarded canary decisions.

## Current maturity / status
- ✅ Strong flagged reliability and stress telemetry workflows.
- ✅ Human-QA pack + canary decision layer are in place.
- ⚠️ Still **experimental** for product-readiness claims; broader readiness requires repeated human scores and agreement analysis.

## Typical workflow
1. Read [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md).
2. Run flagged reliability/quality scenarios via `benchmarks/baseline`.
3. Build QA pack: `run_flagged_e2e_human_qa_pack.py`.
4. Fill scorecard template.
5. Evaluate decision: `run_flagged_e2e_human_qa_decision.py`.
6. Review `GO_WARN_ONLY_CANARY / WARN_ONLY_HOLD / NO_GO` outputs.

## What is still experimental?
- Proxy fixtures (`approx_infer.py`, `approx_prep.py`) are not full runtime streaming integration.
- Visual/perceptual quality claims require human review evidence.
- Canary guidance is explicitly **flagged non-production**.

## How to run QA
See [docs/QA_WORKFLOW.md](docs/QA_WORKFLOW.md).

## How to interpret decisions
See [docs/REPORTS_AND_DECISIONS.md](docs/REPORTS_AND_DECISIONS.md).

## Local GUI (Streamlit)
A lightweight local dashboard is available at `app/qa_dashboard.py`.

```bash
pip install streamlit
streamlit run app/qa_dashboard.py
```

The GUI is local-only and intended for report browsing, QA scoring support, and decision review.

## New teammate: read this first (10-minute path)
1. [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md)
2. [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
3. [docs/QA_WORKFLOW.md](docs/QA_WORKFLOW.md)
4. [docs/REPORTS_AND_DECISIONS.md](docs/REPORTS_AND_DECISIONS.md)
5. [docs/CLI_USAGE.md](docs/CLI_USAGE.md)
