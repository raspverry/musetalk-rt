# Getting Started

- Language: **EN** | [KO](GETTING_STARTED.ko.md) | [JA](GETTING_STARTED.ja.md)

## Scope
This repository is for **flagged, non-production** reliability/quality/QA validation.

## 10-minute setup
1. Python 3.10+
2. Run representative reports already in `benchmarks/baseline/reports`.
3. Build QA pack and decision summary.

```bash
python benchmarks/baseline/run_flagged_e2e_human_qa_pack.py
python benchmarks/baseline/run_flagged_e2e_human_qa_decision.py
```

## Project problem solved
It shortens feedback loops for startup and continuity trade-offs when full runtime wiring is incomplete.

## First docs to read
- `ARCHITECTURE.md`
- `QA_WORKFLOW.md`
- `REPORTS_AND_DECISIONS.md`
- `CLI_USAGE.md`

