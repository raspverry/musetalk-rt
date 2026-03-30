#!/usr/bin/env python3
"""Validate benchmark report consistency and required fields."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUIRED_TOP = {"scenario", "summary", "results", "generated_at_epoch_ms", "environment"}
REQUIRED_RUN = {
    "run_id",
    "scenario_id",
    "mode",
    "status",
    "avatar_preparation_time_ms",
    "first_frame_latency_ms",
    "steady_state_fps",
    "peak_vram_mb",
    "duration_ms",
    "measurement_provenance",
}
VALID_STATUS = {"ok", "partial", "oom", "crash", "error"}


def fail(msg: str) -> None:
    raise SystemExit(f"VALIDATION_FAILED: {msg}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--strict-warm-anchor", action="store_true")
    parser.add_argument("--require-chunk-provenance", action="store_true")
    args = parser.parse_args()

    data = json.loads(args.report.read_text())

    missing_top = REQUIRED_TOP - set(data.keys())
    if missing_top:
        fail(f"missing top-level keys: {sorted(missing_top)}")

    if not isinstance(data["results"], list) or not data["results"]:
        fail("results must be a non-empty list")

    mode = data["scenario"].get("mode")

    for idx, run in enumerate(data["results"], start=1):
        missing_run = REQUIRED_RUN - set(run.keys())
        if missing_run:
            fail(f"run[{idx}] missing keys: {sorted(missing_run)}")

        status = run["status"]
        if status not in VALID_STATUS:
            fail(f"run[{idx}] invalid status: {status}")

        prov = run.get("measurement_provenance") or {}
        for key in [
            "first_frame_latency_ms",
            "frame_source",
            "infer_spawn_mode",
            "file_polling_used",
            "ffmpeg_in_hot_path_cmd",
        ]:
            if key not in prov:
                fail(f"run[{idx}] missing {key} provenance")

        if args.require_chunk_provenance:
            for key in ["chunk_ms", "startup_chunks", "chunk_overhead_ms", "startup_delay_ms", "continuity_risk_hint", "cadence_profile"]:
                if key not in prov:
                    fail(f"run[{idx}] missing {key} chunk provenance")

        if status == "ok":
            if run["first_frame_latency_ms"] is None:
                fail(f"run[{idx}] status ok but first_frame_latency_ms is null")
            if run["steady_state_fps"] is None:
                fail(f"run[{idx}] status ok but steady_state_fps is null")

        if mode == "warm_start":
            anchor = prov.get("first_frame_latency_anchor")
            if anchor not in {"audio_accepted_marker", "infer_cmd_start"}:
                fail(f"run[{idx}] warm mode has invalid latency anchor: {anchor}")
            if args.strict_warm_anchor and anchor != "audio_accepted_marker":
                fail(f"run[{idx}] strict warm anchor expected audio_accepted_marker, got: {anchor}")
            if run["avatar_preparation_time_ms"] not in (0, 0.0):
                fail(f"run[{idx}] warm mode must report avatar_preparation_time_ms as 0.0")

    print(json.dumps({"report": str(args.report), "validation": "ok"}))


if __name__ == "__main__":
    main()
