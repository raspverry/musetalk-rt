#!/usr/bin/env python3
"""Build a lightweight human-QA review pack for flagged non-production e2e runs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple


def _load_report(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text())


def _run_key(run: Dict[str, Any], idx: int) -> Tuple[float, float, int]:
    prov = run.get("measurement_provenance", {})
    jitter = prov.get("frame_jitter_ms")
    latency = run.get("first_frame_latency_ms")
    jitter_v = float(jitter) if jitter is not None else 0.0
    latency_v = float(latency) if latency is not None else 0.0
    return (jitter_v, latency_v, idx)


def _select_representatives(report: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    runs = report.get("results", [])
    if not runs:
        return {}
    indexed = sorted([(i, run) for i, run in enumerate(runs)], key=lambda x: _run_key(x[1], x[0]))
    best_idx, best_run = indexed[0]
    worst_idx, worst_run = indexed[-1]
    median_idx, median_run = indexed[len(indexed) // 2]

    def summarize(i: int, run: Dict[str, Any]) -> Dict[str, Any]:
        prov = run.get("measurement_provenance", {})
        return {
            "run_index": i,
            "status": run.get("status"),
            "first_frame_latency_ms": run.get("first_frame_latency_ms"),
            "steady_state_fps": run.get("steady_state_fps"),
            "continuity_risk_hint": prov.get("continuity_risk_hint"),
            "continuity_risk_basis": prov.get("continuity_risk_basis"),
            "frame_jitter_ms": prov.get("frame_jitter_ms"),
            "cadence_profile": prov.get("cadence_profile"),
            "lifecycle_signal_kinds": prov.get("lifecycle_signal_kinds"),
            "lifecycle_proxy_fallbacks": prov.get("lifecycle_proxy_fallbacks"),
        }

    return {
        "best": summarize(best_idx, best_run),
        "median": summarize(median_idx, median_run),
        "worst": summarize(worst_idx, worst_run),
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--stable-report", type=Path, default=Path("benchmarks/baseline/reports/lifecycle_e2e_flagged_session_probe_audio_session_real_qv12_report.json"))
    p.add_argument("--bursty-report", type=Path, default=Path("benchmarks/baseline/reports/lifecycle_e2e_flagged_session_probe_audio_session_real_stress_bursty_qv12_report.json"))
    p.add_argument("--jittery-report", type=Path, default=Path("benchmarks/baseline/reports/lifecycle_e2e_flagged_session_probe_audio_session_real_stress_jittery_qv12_report.json"))
    p.add_argument("--output-dir", type=Path, default=Path("benchmarks/baseline/reports"))
    p.add_argument("--pack-id", default="lifecycle_e2e_flagged_human_qa_pack_v1")
    args = p.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)

    stable = _load_report(args.stable_report)
    bursty = _load_report(args.bursty_report)
    jittery = _load_report(args.jittery_report)

    pack = {
        "pack_id": args.pack_id,
        "scope": "flagged_non_production_human_qa",
        "reviewer_procedure": [
            "Review stable profile first (best -> median -> worst), then bursty, then jittery.",
            "Use the same prompt/content and playback setup across all profiles.",
            "Score each representative sample on all rubric dimensions before comparing profiles.",
            "If any sample shows severe seam or A/V break (score <=2), flag immediate no-go candidate.",
        ],
        "profiles": {
            "stable": {
                "report": str(args.stable_report),
                "representatives": _select_representatives(stable),
            },
            "bursty": {
                "report": str(args.bursty_report),
                "representatives": _select_representatives(bursty),
            },
            "jittery": {
                "report": str(args.jittery_report),
                "representatives": _select_representatives(jittery),
            },
        },
        "rubric": {
            "scale": "1-5 (5 is best)",
            "dimensions": [
                "continuity_seam_perception",
                "first_response_naturalness",
                "speaking_stability",
                "audio_visual_alignment_at_response_start",
            ],
            "thresholds_for_warn_only_canary": {
                "continuity_seam_perception": 3.8,
                "first_response_naturalness": 3.5,
                "speaking_stability": 3.8,
                "audio_visual_alignment_at_response_start": 4.0,
                "minimum_allowed_single_sample": 3.0,
            },
            "guidance": [
                "Use the same prompt/content across profiles when possible.",
                "Score best/median/worst sample per profile before cross-profile comparison.",
                "Record any visible seam transitions around first speaking frames.",
            ],
        },
    }

    out_json = args.output_dir / f"{args.pack_id}.json"
    out_md = args.output_dir / f"{args.pack_id}.md"
    out_scorecard = args.output_dir / f"{args.pack_id}_scorecard_template.json"
    out_json.write_text(json.dumps(pack, indent=2))

    scorecard = {
        "pack_id": args.pack_id,
        "reviewers": [],
        "scores": [],
        "notes": "Fill one score row per reviewer x profile x representative.",
    }
    for profile_name, profile in pack["profiles"].items():
        reps = profile["representatives"]
        for label in ["best", "median", "worst"]:
            sample = reps.get(label)
            if not sample:
                continue
            scorecard["scores"].append(
                {
                    "reviewer_id": "",
                    "profile": profile_name,
                    "representative": label,
                    "run_index": sample["run_index"],
                    "continuity_seam_perception": None,
                    "first_response_naturalness": None,
                    "speaking_stability": None,
                    "audio_visual_alignment_at_response_start": None,
                    "notes": "",
                }
            )
    out_scorecard.write_text(json.dumps(scorecard, indent=2))

    md_lines: List[str] = [
        f"# Human QA Review Pack: {args.pack_id}",
        "",
        "- Scope: flagged non-production continuity/seam/response-start review",
        "- Profiles: stable, bursty, jittery",
        "",
        "## Scoring rubric (1-5; 5 best)",
        "- continuity_seam_perception",
        "- first_response_naturalness",
        "- speaking_stability",
        "- audio_visual_alignment_at_response_start",
        "",
        "## Representative sample checklist",
    ]
    for profile_name, profile in pack["profiles"].items():
        md_lines.append(f"### {profile_name}")
        reps = profile["representatives"]
        for label in ["best", "median", "worst"]:
            sample = reps.get(label)
            if not sample:
                continue
            md_lines.append(
                f"- {label}: run_index={sample['run_index']}, continuity={sample['continuity_risk_hint']} ({sample['continuity_risk_basis']}), jitter_ms={sample['frame_jitter_ms']}, latency_ms={sample['first_frame_latency_ms']}"
            )
        md_lines.append("")

    md_lines.extend(
        [
            "## Reviewer notes template",
            "- Profile:",
            "- Representative (best/median/worst):",
            "- continuity_seam_perception (1-5):",
            "- first_response_naturalness (1-5):",
            "- speaking_stability (1-5):",
            "- audio_visual_alignment_at_response_start (1-5):",
            "- Notes:",
        ]
    )

    out_md.write_text("\n".join(md_lines) + "\n")
    print(json.dumps({"qa_pack_json": str(out_json), "qa_pack_md": str(out_md), "scorecard_template_json": str(out_scorecard)}))


if __name__ == "__main__":
    main()
