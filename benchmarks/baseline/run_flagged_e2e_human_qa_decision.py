#!/usr/bin/env python3
"""Evaluate flagged canary readiness from human-QA scorecards."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean
from typing import Any, Dict, List


DIMENSIONS = [
    "continuity_seam_perception",
    "first_response_naturalness",
    "speaking_stability",
    "audio_visual_alignment_at_response_start",
]


def _num(v: Any) -> float | None:
    try:
        return float(v) if v is not None else None
    except (TypeError, ValueError):
        return None


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--qa-pack", type=Path, default=Path("benchmarks/baseline/reports/lifecycle_e2e_flagged_human_qa_pack_v1.json"))
    p.add_argument("--scorecard", type=Path, default=Path("benchmarks/baseline/reports/lifecycle_e2e_flagged_human_qa_pack_v1_scorecard_template.json"))
    p.add_argument("--output-dir", type=Path, default=Path("benchmarks/baseline/reports"))
    args = p.parse_args()

    pack = json.loads(args.qa_pack.read_text())
    scorecard = json.loads(args.scorecard.read_text())
    thresholds = pack["rubric"]["thresholds_for_warn_only_canary"]

    by_dim: Dict[str, List[float]] = {d: [] for d in DIMENSIONS}
    min_sample = None
    missing_scores = 0
    total_rows = 0

    for row in scorecard.get("scores", []):
        total_rows += 1
        row_has_missing = False
        for d in DIMENSIONS:
            v = _num(row.get(d))
            if v is None:
                row_has_missing = True
                continue
            by_dim[d].append(v)
            min_sample = v if min_sample is None else min(min_sample, v)
        if row_has_missing:
            missing_scores += 1

    avg = {d: (mean(vals) if vals else None) for d, vals in by_dim.items()}

    decision = "NO_GO_INSUFFICIENT_HUMAN_QA"
    reason = "Missing human scores; cannot establish canary readiness."
    rollback = "Keep fully permissive fallback and do not progress canary tightening."

    if missing_scores == 0 and total_rows > 0:
        below_threshold = [d for d in DIMENSIONS if (avg[d] is None or avg[d] < float(thresholds[d]))]
        if min_sample is not None and min_sample <= 2.0:
            decision = "NO_GO"
            reason = "At least one severe sample score (<=2) indicates visible quality failure."
            rollback = "Immediate rollback to fully permissive fallback and rerun QA after remediation."
        elif not below_threshold and min_sample is not None and min_sample >= float(thresholds["minimum_allowed_single_sample"]):
            decision = "GO_WARN_ONLY_CANARY"
            reason = "All dimension averages meet thresholds and no single sample is below minimum allowed."
            rollback = "If post-canary score drift drops below thresholds, revert to fully permissive fallback."
        else:
            decision = "WARN_ONLY_HOLD"
            reason = "Mixed quality results; keep warn-only trials gated and collect more reviewer evidence."
            rollback = "Do not widen canary; keep fallback permissive and gather additional scored sessions."

    output = {
        "analysis": "flagged_human_qa_decision_layer",
        "qa_pack": str(args.qa_pack),
        "scorecard": str(args.scorecard),
        "decision": decision,
        "reason": reason,
        "rollback_recommendation": rollback,
        "thresholds": thresholds,
        "avg_scores": avg,
        "minimum_single_sample_score": min_sample,
        "score_rows_total": total_rows,
        "score_rows_with_missing_values": missing_scores,
        "additional_evidence_needed_before_broader_readiness_claim": [
            "Completed multi-reviewer scorecards across multiple sessions and prompts.",
            "Reviewer agreement analysis (inter-rater consistency) on seam/naturalness.",
            "Repeated stressed-run QA passes showing threshold stability over time.",
            "Documented canary rollback drill with explicit trigger thresholds.",
        ],
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    out_json = args.output_dir / f"{pack['pack_id']}_decision_summary.json"
    out_md = args.output_dir / f"{pack['pack_id']}_decision_summary.md"
    out_json.write_text(json.dumps(output, indent=2))
    md_lines = [
        f"# Human QA Decision Summary ({pack['pack_id']})",
        "",
        f"- Decision: **{decision}**",
        f"- Reason: {reason}",
        f"- Rollback recommendation: {rollback}",
        "",
        "## Thresholds",
    ]
    for k, v in thresholds.items():
        md_lines.append(f"- {k}: {v}")
    md_lines.extend(["", "## Average scores"])
    for d in DIMENSIONS:
        md_lines.append(f"- {d}: {avg[d]}")
    md_lines.extend(
        [
            "",
            "## Additional evidence required before broader readiness claim",
            *[f"- {x}" for x in output["additional_evidence_needed_before_broader_readiness_claim"]],
        ]
    )
    out_md.write_text("\n".join(md_lines) + "\n")
    print(json.dumps({"decision_summary_json": str(out_json), "decision_summary_md": str(out_md)}))


if __name__ == "__main__":
    main()
