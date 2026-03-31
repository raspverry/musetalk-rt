# QA Workflow

- Language: **EN** | [KO](QA_WORKFLOW.ko.md) | [JA](QA_WORKFLOW.ja.md)

## End-to-end QA flow
1. Generate/refresh stable, bursty, jittery reports.
2. Build QA pack (`run_flagged_e2e_human_qa_pack.py`).
3. Review best/median/worst samples per profile.
4. Fill scorecard template.
5. Evaluate decision (`run_flagged_e2e_human_qa_decision.py`).

## How to run QA
```bash
python benchmarks/baseline/run_flagged_e2e_human_qa_pack.py
# fill *_scorecard_template.json
python benchmarks/baseline/run_flagged_e2e_human_qa_decision.py
```

## Scoring dimensions
- continuity/seam
- first-response naturalness
- speaking stability
- A/V alignment at response start

