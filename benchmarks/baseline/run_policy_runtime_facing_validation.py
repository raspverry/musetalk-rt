#!/usr/bin/env python3
"""Run runtime-facing proxy validation for configured warm default/fallback policies."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

POLICY_PATH = Path("benchmarks/baseline/policies/warm_path_policy.json")
SCENARIO_DIR = Path("benchmarks/baseline/scenarios")
REPORT_DIR = Path("benchmarks/baseline/reports")


def run_cmd(cmd: str) -> None:
    subprocess.run(cmd, shell=True, check=True)


def make_scenario(policy_mode: str, cadence_profile: str, chunk_override: int | None = None, startup_override: int | None = None) -> Path:
    scenario_id = f"runtime_facing_{policy_mode}_{cadence_profile}"
    overrides = ""
    if chunk_override is not None:
        overrides += f" --chunk-ms-override {chunk_override}"
    if startup_override is not None:
        overrides += f" --startup-chunks-override {startup_override}"

    scenario = {
        "scenario_id": scenario_id,
        "mode": "warm_start",
        "adapter": "command",
        "runs": 3,
        "timeout_s": 120,
        "command": (
            "python benchmarks/baseline/musetalk_baseline_runner.py --mode warm_start "
            f"--policy-config {POLICY_PATH} --policy-mode {policy_mode}{overrides} "
            "--infer-cmd 'python benchmarks/baseline/fixtures/approx_infer.py "
            "--frames-dir benchmarks/baseline/tmp/frames "
            "--audio-accept-ms 80 --post-accept-startup-ms 0 "
            "--chunk-ms {chunk_ms} --startup-chunks {startup_chunks} --chunk-overhead-ms 8 "
            f"--cadence-profile {cadence_profile} "
            "--fps 23 --num-frames 50 --disable-frame-write --emit-metrics-json' "
            "--frame-glob 'benchmarks/baseline/tmp/frames/*.png' "
            "--require-audio-accepted-marker --prefer-infer-json "
            "--cleanup-glob 'benchmarks/baseline/tmp/frames/*.png'"
        ),
    }
    path = SCENARIO_DIR / f"{scenario_id}.json"
    path.write_text(json.dumps(scenario, indent=2) + "\n")
    return path


def main() -> None:
    outputs = []
    for policy_mode in ["default", "fallback"]:
        scenario_path = make_scenario(policy_mode, "tts_bursty")
        run_cmd(f"python benchmarks/baseline/benchmark_harness.py --scenario {scenario_path} --output-dir {REPORT_DIR}")
        report_path = REPORT_DIR / f"{scenario_path.stem}_report.json"
        run_cmd(
            "python benchmarks/baseline/validate_report.py "
            f"--report {report_path} --strict-warm-anchor --require-chunk-provenance"
        )
        report = json.loads(report_path.read_text())
        prov = report["results"][0]["measurement_provenance"]
        outputs.append(
            {
                "scenario": scenario_path.stem,
                "first_frame_latency_ms_mean": report["summary"]["first_frame_latency_ms"]["mean"],
                "steady_state_fps_mean": report["summary"]["steady_state_fps"]["mean"],
                "continuity_risk_hint": prov.get("continuity_risk_hint"),
                "policy_mode": prov.get("policy_mode"),
                "policy_selection_source": prov.get("policy_selection_source"),
                "policy_chunk_ms": prov.get("policy_chunk_ms"),
                "policy_startup_chunks": prov.get("policy_startup_chunks"),
            }
        )

    summary_path = REPORT_DIR / "runtime_facing_policy_validation_summary.json"
    summary_path.write_text(json.dumps(outputs, indent=2))
    print(json.dumps({"summary": str(summary_path), "runs": len(outputs)}))


if __name__ == "__main__":
    main()
