#!/usr/bin/env python3
"""Run a limited, flagged, non-production quality-focused e2e validation pass."""

from __future__ import annotations

import argparse
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List


def _quantile(values: List[float], q: float) -> float | None:
    if not values:
        return None
    if len(values) == 1:
        return values[0]
    vals = sorted(values)
    idx = (len(vals) - 1) * q
    lo = int(idx)
    hi = min(lo + 1, len(vals) - 1)
    frac = idx - lo
    return vals[lo] * (1.0 - frac) + vals[hi] * frac


def _safe_float(v: Any) -> float | None:
    try:
        return float(v) if v is not None else None
    except (TypeError, ValueError):
        return None


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--scenario", type=Path, default=Path("benchmarks/baseline/scenarios/lifecycle_e2e_flagged_session_probe_audio_session_real.json"))
    p.add_argument("--runs", type=int, default=12)
    p.add_argument("--output-dir", type=Path, default=Path("benchmarks/baseline/reports"))
    p.add_argument("--compare-summary", type=Path, default=Path("benchmarks/baseline/reports/lifecycle_e2e_flagged_session_probe_audio_session_real_r30_reliability_summary.json"))
    args = p.parse_args()

    scenario = json.loads(args.scenario.read_text())
    scenario_id = f"{scenario['scenario_id']}_qv{args.runs}"
    scenario["scenario_id"] = scenario_id
    scenario["runs"] = int(args.runs)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    tmp_scenario = args.output_dir / f"{scenario_id}.scenario.json"
    tmp_scenario.write_text(json.dumps(scenario, indent=2))

    subprocess.check_call(
        [
            "python",
            "benchmarks/baseline/benchmark_harness.py",
            "--scenario",
            str(tmp_scenario),
            "--output-dir",
            str(args.output_dir),
        ]
    )

    report_path = args.output_dir / f"{scenario_id}_report.json"
    report = json.loads(report_path.read_text())

    latency_vals: List[float] = []
    fps_vals: List[float] = []
    jitter_vals: List[float] = []
    continuity_hints: Counter = Counter()
    continuity_basis: Counter = Counter()
    cadence_profiles: Counter = Counter()
    stage_signal_counts: Dict[str, Counter] = defaultdict(Counter)
    stage_error_counts: Counter = Counter()
    fallback_runs = 0

    for run in report.get("results", []):
        lat = _safe_float(run.get("first_frame_latency_ms"))
        fps = _safe_float(run.get("steady_state_fps"))
        if lat is not None:
            latency_vals.append(lat)
        if fps is not None:
            fps_vals.append(fps)

        prov = run.get("measurement_provenance", {})
        jitter = _safe_float(prov.get("frame_jitter_ms"))
        if jitter is not None:
            jitter_vals.append(jitter)
        continuity_hints[str(prov.get("continuity_risk_hint", "unknown"))] += 1
        continuity_basis[str(prov.get("continuity_risk_basis", "unknown"))] += 1
        cadence_profiles[str(prov.get("cadence_profile", "unknown"))] += 1

        used_fallback = False
        for stage in run.get("lifecycle_stage_outcomes") or []:
            stage_name = str(stage.get("stage", "unknown"))
            signal_kind = str(stage.get("signal_kind", "unknown"))
            stage_signal_counts[stage_name][signal_kind] += 1
            if signal_kind.startswith("proxy_fallback"):
                used_fallback = True
            if stage.get("status") == "error":
                stage_error_counts[stage_name] += 1
        if used_fallback:
            fallback_runs += 1

    total_runs = len(report.get("results", []))
    fallback_rate = (fallback_runs / total_runs) if total_runs else 0.0
    lifecycle_error_total = int(sum(stage_error_counts.values()))

    quality_summary: Dict[str, Any] = {
        "analysis": "flagged_e2e_quality_validation",
        "source_report": str(report_path),
        "total_runs": total_runs,
        "fallback_runs": fallback_runs,
        "fallback_rate": round(fallback_rate, 4),
        "lifecycle_stage_error_total": lifecycle_error_total,
        "stage_error_counts": dict(stage_error_counts),
        "stage_signal_kind_counts": {k: dict(v) for k, v in stage_signal_counts.items()},
        "quality_metrics": {
            "first_frame_latency_ms": {
                "p50": _quantile(latency_vals, 0.5),
                "p95": _quantile(latency_vals, 0.95),
                "spread_ms": (max(latency_vals) - min(latency_vals)) if latency_vals else None,
            },
            "steady_state_fps": {
                "p50": _quantile(fps_vals, 0.5),
                "p95": _quantile(fps_vals, 0.95),
                "spread_fps": (max(fps_vals) - min(fps_vals)) if fps_vals else None,
            },
            "frame_jitter_ms": {
                "p50": _quantile(jitter_vals, 0.5),
                "p95": _quantile(jitter_vals, 0.95),
                "max": max(jitter_vals) if jitter_vals else None,
            },
            "continuity_risk_hint_counts": dict(continuity_hints),
            "continuity_risk_basis_counts": dict(continuity_basis),
            "cadence_profile_counts": dict(cadence_profiles),
        },
        "observations": [],
        "limitations": [
            "Proxy/fixture approximation cannot replace human MOS-style naturalness review.",
            "No network/mobile jitter injection in this pass; cadence sensitivity is approximation-only.",
            "Seam/continuity and first-response naturalness conclusions are telemetry-guided, not perceptual ground truth.",
        ],
    }

    observations = quality_summary["observations"]
    if fallback_runs == 0 and lifecycle_error_total == 0:
        observations.append("No lifecycle fallback or stage errors observed in this quality validation pass.")
    if continuity_hints.get("low", 0) == total_runs:
        observations.append("Continuity risk hints stayed low across all runs under current flagged path.")
    if continuity_hints.get("medium_boundary_churn", 0) > 0:
        observations.append(
            f"Continuity risk hints reported medium boundary churn in {continuity_hints.get('medium_boundary_churn', 0)}/{total_runs} runs."
        )
    if continuity_hints.get("high", 0) > 0:
        observations.append(
            f"Continuity risk hints reported high risk in {continuity_hints.get('high', 0)}/{total_runs} runs."
        )
    if len(cadence_profiles) == 1:
        observations.append(f"TTS cadence sensitivity sampled only for cadence profile: {next(iter(cadence_profiles.keys()))}.")

    warn_only_safe = (
        total_runs >= 8
        and fallback_runs == 0
        and lifecycle_error_total == 0
        and continuity_hints.get("high", 0) == 0
    )
    quality_summary["recommendation_warn_only_canary"] = (
        "safe_to_try_warn_only_canary" if warn_only_safe else "keep_fully_permissive"
    )
    quality_summary["next_validation_under_jitter"] = [
        "Inject bursty + delayed chunk arrival with random jitter envelopes (e.g. 20-200ms) and rerun stage/error tracking.",
        "Run mixed cadence profiles (fixed, tts_bursty, jittery) while checking seam artifacts and first response stability.",
        "Add packet-loss/drop simulation to validate fallback transparency and quality degradation boundaries.",
    ]

    if args.compare_summary and args.compare_summary.exists():
        before = json.loads(args.compare_summary.read_text())
        quality_summary["comparison"] = {
            "compare_summary": str(args.compare_summary),
            "before_fallback_rate": before.get("fallback_rate"),
            "after_fallback_rate": quality_summary["fallback_rate"],
            "before_stage_signal_mix": before.get("stage_signal_mix", {}),
            "after_stage_signal_mix": {
                k: {"signal_kind_counts": v}
                for k, v in quality_summary["stage_signal_kind_counts"].items()
            },
        }

    summary_json = args.output_dir / f"{scenario_id}_quality_summary.json"
    summary_md = args.output_dir / f"{scenario_id}_quality_summary.md"
    summary_json.write_text(json.dumps(quality_summary, indent=2))

    md_lines = [
        f"# Flagged E2E Quality Validation Summary ({scenario_id})",
        "",
        f"- Runs: {total_runs}",
        f"- Fallback runs: {fallback_runs} (rate={quality_summary['fallback_rate']})",
        f"- Lifecycle stage errors: {lifecycle_error_total}",
        f"- Warn-only canary recommendation: {quality_summary['recommendation_warn_only_canary']}",
        "",
        "## Stage signal_kind counts",
    ]
    for stage_name, counts in quality_summary["stage_signal_kind_counts"].items():
        md_lines.append(f"- **{stage_name}**: {counts}")
    md_lines.extend(["", "## Observations"])
    md_lines.extend([f"- {obs}" for obs in observations] or ["- None"])
    md_lines.extend(["", "## Limitations"])
    md_lines.extend([f"- {item}" for item in quality_summary["limitations"]])
    md_lines.extend(["", "## Next validation under jitter"])
    md_lines.extend([f"- {item}" for item in quality_summary["next_validation_under_jitter"]])
    summary_md.write_text("\n".join(md_lines) + "\n")

    print(
        json.dumps(
            {
                "report": str(report_path),
                "quality_summary_json": str(summary_json),
                "quality_summary_md": str(summary_md),
            }
        )
    )


if __name__ == "__main__":
    main()
