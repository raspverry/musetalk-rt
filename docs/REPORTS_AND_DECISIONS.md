# Reports and Decisions

- Language: **EN** | [KO](REPORTS_AND_DECISIONS.ko.md) | [JA](REPORTS_AND_DECISIONS.ja.md)

## Key artifacts
- `*_quality_summary.json`
- `*_reliability_summary.json`
- `*_human_qa_pack_v1*.json/md`
- `*_decision_summary.json/md`

## Decision meanings
- `GO_WARN_ONLY_CANARY`: threshold pass; proceed in flagged canary scope.
- `WARN_ONLY_HOLD`: partial pass; collect more evidence.
- `NO_GO`: severe quality failure.
- `NO_GO_INSUFFICIENT_HUMAN_QA`: missing reviewer evidence.

## Rollback guidance
If decision degrades after canary start, return to fully permissive fallback and rerun QA.

