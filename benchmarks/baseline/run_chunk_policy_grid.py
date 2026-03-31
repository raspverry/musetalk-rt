#!/usr/bin/env python3
"""Run chunk-policy warm-path study grid and produce ranked summary."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

CHUNK_MS = [40, 80, 120, 160, 240, 320]
STARTUP_CHUNKS = [1, 2, 3]

SCENARIO_DIR = Path("benchmarks/baseline/scenarios")
REPORT_DIR = Path("benchmarks/baseline/reports")


def run_cmd(cmd: str) -> None:
    subprocess.run(cmd, shell=True, check=True)


def main() -> None:
    rows = []
    for chunk_ms in CHUNK_MS:
        for startup_chunks in STARTUP_CHUNKS:
            scenario_id = f"real_warm_chunk_ms{chunk_ms}_sc{startup_chunks}"
            scenario_path = SCENARIO_DIR / f"{scenario_id}.json"
            report_path = REPORT_DIR / f"{scenario_id}_report.json"

            scenario = {
                "scenario_id": scenario_id,
                "mode": "warm_start",
                "adapter": "command",
                "runs": 2,
                "timeout_s": 120,
                "command": (
                    "python benchmarks/baseline/musetalk_baseline_runner.py --mode warm_start "
                    "--infer-cmd 'python benchmarks/baseline/fixtures/approx_infer.py "
                    "--frames-dir benchmarks/baseline/tmp/frames "
                    "--audio-accept-ms 80 --post-accept-startup-ms 0 "
                    f"--chunk-ms {chunk_ms} --startup-chunks {startup_chunks} --chunk-overhead-ms 8 "
                    "--fps 23 --num-frames 50 --disable-frame-write --emit-metrics-json' "
                    "--frame-glob 'benchmarks/baseline/tmp/frames/*.png' "
                    "--require-audio-accepted-marker --prefer-infer-json "
                    "--cleanup-glob 'benchmarks/baseline/tmp/frames/*.png'"
                ),
            }
            scenario_path.write_text(json.dumps(scenario, indent=2) + "\n")

            run_cmd(
                f"python benchmarks/baseline/benchmark_harness.py --scenario {scenario_path} --output-dir {REPORT_DIR}"
            )
            run_cmd(
                "python benchmarks/baseline/validate_report.py "
                f"--report {report_path} --strict-warm-anchor --require-chunk-provenance"
            )

            report = json.loads(report_path.read_text())
            summary = report["summary"]
            first_lat = summary["first_frame_latency_ms"]["mean"]
            fps = summary["steady_state_fps"]["mean"]
            status_ok = summary["ok_runs"]
            risk = report["results"][0]["measurement_provenance"].get("continuity_risk_hint")
            rows.append(
                {
                    "scenario_id": scenario_id,
                    "chunk_ms": chunk_ms,
                    "startup_chunks": startup_chunks,
                    "first_frame_latency_ms": first_lat,
                    "steady_state_fps": fps,
                    "ok_runs": status_ok,
                    "continuity_risk_hint": risk,
                    "report": str(report_path),
                }
            )

    rows_sorted = sorted(rows, key=lambda r: (r["first_frame_latency_ms"], -r["steady_state_fps"]))

    summary_json = REPORT_DIR / "chunk_policy_grid_summary.json"
    summary_md = REPORT_DIR / "chunk_policy_grid_summary.md"
    summary_json.write_text(json.dumps(rows_sorted, indent=2))

    lines = [
        "# Chunk Policy Grid Summary",
        "",
        "| rank | chunk_ms | startup_chunks | first_frame_latency_ms | steady_state_fps | ok_runs | continuity_risk_hint | report |",
        "|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for idx, row in enumerate(rows_sorted, start=1):
        lines.append(
            f"| {idx} | {row['chunk_ms']} | {row['startup_chunks']} | {row['first_frame_latency_ms']} | {row['steady_state_fps']} | {row['ok_runs']} | {row['continuity_risk_hint']} | `{Path(row['report']).name}` |"
        )
    summary_md.write_text("\n".join(lines) + "\n")

    print(json.dumps({"summary_json": str(summary_json), "summary_md": str(summary_md), "rows": len(rows_sorted)}))


if __name__ == "__main__":
    main()
