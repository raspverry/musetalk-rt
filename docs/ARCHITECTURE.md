# Architecture (Flagged Evaluation Stack)

- Language: **EN** | [KO](ARCHITECTURE.ko.md) | [JA](ARCHITECTURE.ja.md)

## Components
- `benchmark_harness.py`: scenario orchestrator
- `musetalk_baseline_runner.py`: lifecycle + provenance runner
- `fixtures/approx_*.py`: proxy approximation layer
- `run_flagged_e2e_*`: reliability/quality/human-QA/decision workflows
- `reports/`: auditable outputs

## Real vs proxy boundaries
- Real-wired lifecycle observation exists for flagged stages where configured.
- Proxy fixtures still approximate frame generation/cadence behavior.
- Fallback visibility is preserved in stage outcomes/provenance.

## Maturity
Strong for flagged evaluation; not a production runtime orchestration layer.

