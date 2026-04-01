# Maintainer Checklist: Run Decision After Score Entry

## Preconditions
- Reviewer scorecard is fully filled (no `null` scores).
- File path is confirmed.

## Run command
```bash
python benchmarks/baseline/run_flagged_e2e_human_qa_decision.py \
  --qa-pack benchmarks/baseline/reports/lifecycle_e2e_flagged_human_qa_pack_v1.json \
  --scorecard benchmarks/baseline/reports/lifecycle_e2e_flagged_human_qa_pack_v1_scorecard_template.json \
  --output-dir benchmarks/baseline/reports
```

## Check outputs
- `benchmarks/baseline/reports/lifecycle_e2e_flagged_human_qa_pack_v1_decision_summary.json`
- `benchmarks/baseline/reports/lifecycle_e2e_flagged_human_qa_pack_v1_decision_summary.md`

## Interpret quickly
- `GO_WARN_ONLY_CANARY`: proceed in flagged canary scope.
- `WARN_ONLY_HOLD`: keep warn-only limited; collect more evidence.
- `NO_GO`: do not proceed; remediate quality issues.
- `NO_GO_INSUFFICIENT_HUMAN_QA`: missing scores or incomplete evidence.

## Final sanity checks
- Decision aligns with thresholds and reviewer notes.
- Rollback recommendation is captured and communicated.
