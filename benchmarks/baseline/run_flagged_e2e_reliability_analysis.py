#!/usr/bin/env python3
"""Run repeated flagged e2e probes and summarize fallback/failure reliability patterns."""

from __future__ import annotations

import argparse
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Any


def _signal_bucket(signal_kind: str) -> str:
    if signal_kind.startswith("real_wired"):
        return "real_wired"
    if signal_kind.startswith("proxy_fallback"):
        return "fallback"
    return "proxy"


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--scenario", type=Path, default=Path("benchmarks/baseline/scenarios/lifecycle_e2e_flagged_session_probe.json"))
    p.add_argument("--runs", type=int, default=8)
    p.add_argument("--output-dir", type=Path, default=Path("benchmarks/baseline/reports"))
    p.add_argument("--compare-summary", type=Path, default=None)
    args = p.parse_args()

    scenario = json.loads(args.scenario.read_text())
    scenario["runs"] = int(args.runs)
    scenario_id = f"{scenario['scenario_id']}_r{args.runs}"
    scenario["scenario_id"] = scenario_id

    tmp_scenario = args.output_dir / f"{scenario_id}.scenario.json"
    args.output_dir.mkdir(parents=True, exist_ok=True)
    tmp_scenario.write_text(json.dumps(scenario, indent=2))

    cmd = [
        "python",
        "benchmarks/baseline/benchmark_harness.py",
        "--scenario",
        str(tmp_scenario),
        "--output-dir",
        str(args.output_dir),
    ]
    subprocess.check_call(cmd)

    report_path = args.output_dir / f"{scenario_id}_report.json"
    report = json.loads(report_path.read_text())

    total = len(report["results"])
    runs_with_fallback = 0
    stage_signal_kind_counts: Dict[str, Counter] = defaultdict(Counter)
    stage_failure_counts: Counter = Counter()

    for run in report["results"]:
        outcomes = run.get("lifecycle_stage_outcomes") or []
        used_fallback = False
        for stage in outcomes:
            name = stage.get("stage", "unknown")
            signal_kind = stage.get("signal_kind", "unknown")
            stage_signal_kind_counts[name][signal_kind] += 1
            if signal_kind.startswith("proxy_fallback"):
                used_fallback = True
            if stage.get("status") == "error":
                stage_failure_counts[name] += 1
        if used_fallback:
            runs_with_fallback += 1

    fallback_rate = (runs_with_fallback / total) if total else 0.0

    stage_mix = {}
    for stage_name, counts in stage_signal_kind_counts.items():
        stage_total = sum(counts.values())
        stage_mix[stage_name] = {
            "total": stage_total,
            "signal_kind_counts": dict(counts),
            "bucket_rates": {
                "real_wired": round(sum(v for k, v in counts.items() if _signal_bucket(k) == "real_wired") / stage_total, 4) if stage_total else 0.0,
                "proxy": round(sum(v for k, v in counts.items() if _signal_bucket(k) == "proxy") / stage_total, 4) if stage_total else 0.0,
                "fallback": round(sum(v for k, v in counts.items() if _signal_bucket(k) == "fallback") / stage_total, 4) if stage_total else 0.0,
            },
            "error_count": int(stage_failure_counts.get(stage_name, 0)),
        }

    tighten_recommendation = (
        "Do not tighten yet. Keep fallback permissive until >=30 flagged runs with fallback_rate < 0.10 and zero lifecycle stage errors."
    )
    if total >= 30 and fallback_rate < 0.10 and sum(stage_failure_counts.values()) == 0:
        tighten_recommendation = "Eligible to trial stricter fallback (warn-only fallback) in canary flagged runs."

    summary: Dict[str, Any] = {
        "analysis": "flagged_e2e_reliability",
        "source_report": str(report_path),
        "total_runs": total,
        "runs_with_fallback": runs_with_fallback,
        "fallback_rate": round(fallback_rate, 4),
        "stage_failure_counts": dict(stage_failure_counts),
        "stage_signal_mix": stage_mix,
        "recommendation_fallback_tightening": tighten_recommendation,
        "next_stage_to_deepen": "avatar_ready_or_warm_assumed",
        "notes": {
            "non_production": True,
            "scope": "telemetry-only reliability learning",
        },
        "qa_checklist": [
            "Verify response-start feels prompt (first speaking frame timing within expected envelope).",
            "Spot-check seam/continuity artifacts around response onset.",
            "Confirm no obvious audio/video desync at first speaking frame.",
            "Record whether fallback stage was user-visible in perceived startup quality.",
        ],
    }

    if args.compare_summary:
        before = json.loads(args.compare_summary.read_text())
        stage_mix_compare: Dict[str, Any] = {}
        for stage_name in sorted(set(before.get("stage_signal_mix", {}).keys()) | set(stage_mix.keys())):
            before_mix = before.get("stage_signal_mix", {}).get(stage_name, {})
            after_mix = stage_mix.get(stage_name, {})
            stage_mix_compare[stage_name] = {
                "before_signal_kind_counts": before_mix.get("signal_kind_counts", {}),
                "after_signal_kind_counts": after_mix.get("signal_kind_counts", {}),
                "before_bucket_rates": before_mix.get("bucket_rates", {}),
                "after_bucket_rates": after_mix.get("bucket_rates", {}),
            }
        summary["comparison"] = {
            "compare_summary": str(args.compare_summary),
            "before_fallback_rate": before.get("fallback_rate"),
            "after_fallback_rate": summary["fallback_rate"],
            "delta_fallback_rate": round(summary["fallback_rate"] - float(before.get("fallback_rate", 0.0)), 4),
            "stage_signal_mix_compare": stage_mix_compare,
        }

    json_out = args.output_dir / f"{scenario_id}_reliability_summary.json"
    md_out = args.output_dir / f"{scenario_id}_reliability_summary.md"
    json_out.write_text(json.dumps(summary, indent=2))

    md_lines = [
        f"# Flagged E2E Reliability Summary ({scenario_id})",
        "",
        f"- Total runs: {summary['total_runs']}",
        f"- Runs with fallback: {summary['runs_with_fallback']}",
        f"- Fallback rate: {summary['fallback_rate']}",
        "",
        "## Stage signal mix",
    ]
    for stage_name, mix in stage_mix.items():
        md_lines.append(f"- **{stage_name}**: {mix['signal_kind_counts']} | errors={mix['error_count']}")
    md_lines.extend(
        [
            "",
            "## Recommendation",
            f"- {summary['recommendation_fallback_tightening']}",
            f"- Next stage to deepen: {summary['next_stage_to_deepen']}",
            "",
            "## Lightweight QA checklist",
        ]
    )
    md_lines.extend([f"- {item}" for item in summary["qa_checklist"]])
    if summary.get("comparison"):
        comp = summary["comparison"]
        md_lines.extend(
            [
                "",
                "## Before vs after comparison",
                f"- Before fallback rate: {comp['before_fallback_rate']}",
                f"- After fallback rate: {comp['after_fallback_rate']}",
                f"- Delta fallback rate: {comp['delta_fallback_rate']}",
                "",
                "### Stage-by-stage signal_kind mix",
            ]
        )
        for stage_name, info in comp["stage_signal_mix_compare"].items():
            md_lines.append(
                f"- **{stage_name}**: before={info['before_signal_kind_counts']} | after={info['after_signal_kind_counts']}"
            )
    md_out.write_text("\n".join(md_lines) + "\n")

    print(json.dumps({"report": str(report_path), "summary_json": str(json_out), "summary_md": str(md_out)}))


if __name__ == "__main__":
    main()
