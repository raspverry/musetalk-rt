#!/usr/bin/env python3
"""Baseline benchmark harness for MuseTalk-RT.

Focus metrics:
- avatar preparation time
- first-frame latency
- steady-state FPS
- peak VRAM
- crash/OOM behavior
"""

from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class RunResult:
    run_id: int
    scenario_id: str
    mode: str
    status: str  # ok | crash | oom | error
    avatar_preparation_time_ms: Optional[float]
    first_frame_latency_ms: Optional[float]
    steady_state_fps: Optional[float]
    peak_vram_mb: Optional[float]
    duration_ms: float
    error_message: Optional[str] = None


class ScenarioError(Exception):
    pass


def load_scenario(path: Path) -> Dict[str, Any]:
    data = json.loads(path.read_text())
    required = ["scenario_id", "mode", "adapter", "runs"]
    missing = [k for k in required if k not in data]
    if missing:
        raise ScenarioError(f"Missing required scenario keys: {missing}")
    return data


def _max_memory_used_mb() -> Optional[float]:
    """Returns max memory.used across visible GPUs, if nvidia-smi exists."""
    try:
        out = subprocess.check_output(
            [
                "nvidia-smi",
                "--query-gpu=memory.used",
                "--format=csv,noheader,nounits",
            ],
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except (FileNotFoundError, subprocess.SubprocessError):
        return None

    values: List[float] = []
    for line in out.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            values.append(float(line))
        except ValueError:
            continue

    if not values:
        return None
    return max(values)


def run_command_adapter(command: str, timeout_s: float) -> Dict[str, Any]:
    start = time.perf_counter()
    peak_vram_mb = _max_memory_used_mb()

    proc = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    sampled_peak = peak_vram_mb
    while proc.poll() is None:
        sample = _max_memory_used_mb()
        if sample is not None and (sampled_peak is None or sample > sampled_peak):
            sampled_peak = sample
        if time.perf_counter() - start > timeout_s:
            proc.kill()
            raise TimeoutError(f"Command timed out after {timeout_s}s")
        time.sleep(0.1)

    stdout, stderr = proc.communicate()
    elapsed_ms = (time.perf_counter() - start) * 1000.0

    payload: Dict[str, Any] = {}
    for line in stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
            break
        except json.JSONDecodeError:
            continue

    if not payload:
        payload = {"status": "error", "error_message": "No JSON payload in stdout"}

    payload.setdefault("status", "ok" if proc.returncode == 0 else "crash")
    payload.setdefault("error_message", None if proc.returncode == 0 else stderr.strip()[:500])
    payload.setdefault("peak_vram_mb", sampled_peak)
    payload.setdefault("duration_ms", elapsed_ms)
    return payload


def run_simulated_adapter(config: Dict[str, Any], run_id: int) -> Dict[str, Any]:
    profile = config.get("simulated_profile", {})
    # deterministic variation for repeatability
    drift = (run_id % 5) * 4.0

    failure_pattern = profile.get("failure_pattern", "none")
    if failure_pattern == "oom_every_5" and run_id % 5 == 0:
        return {
            "status": "oom",
            "avatar_preparation_time_ms": profile.get("avatar_preparation_time_ms", 0.0),
            "first_frame_latency_ms": None,
            "steady_state_fps": None,
            "peak_vram_mb": profile.get("peak_vram_mb", 0.0) + 512.0,
            "error_message": "Simulated CUDA OOM",
            "duration_ms": 120.0,
        }

    return {
        "status": "ok",
        "avatar_preparation_time_ms": profile.get("avatar_preparation_time_ms", 0.0) + drift,
        "first_frame_latency_ms": profile.get("first_frame_latency_ms", 0.0) + drift,
        "steady_state_fps": profile.get("steady_state_fps", 0.0) - drift / 20.0,
        "peak_vram_mb": profile.get("peak_vram_mb", 0.0) + drift,
        "error_message": None,
        "duration_ms": profile.get("duration_ms", 100.0) + drift,
    }


def summarize(results: List[RunResult]) -> Dict[str, Any]:
    def vals(key: str) -> List[float]:
        out: List[float] = []
        for r in results:
            value = getattr(r, key)
            if value is not None:
                out.append(float(value))
        return out

    statuses = [r.status for r in results]
    return {
        "runs": len(results),
        "ok_runs": statuses.count("ok"),
        "crash_runs": statuses.count("crash") + statuses.count("error"),
        "oom_runs": statuses.count("oom"),
        "avatar_preparation_time_ms": _agg(vals("avatar_preparation_time_ms")),
        "first_frame_latency_ms": _agg(vals("first_frame_latency_ms")),
        "steady_state_fps": _agg(vals("steady_state_fps")),
        "peak_vram_mb": _agg(vals("peak_vram_mb")),
    }


def _agg(values: List[float]) -> Dict[str, Optional[float]]:
    if not values:
        return {"mean": None, "p50": None, "p95": None, "min": None, "max": None}
    values_sorted = sorted(values)
    return {
        "mean": round(statistics.mean(values), 3),
        "p50": round(values_sorted[int(0.50 * (len(values_sorted) - 1))], 3),
        "p95": round(values_sorted[int(0.95 * (len(values_sorted) - 1))], 3),
        "min": round(values_sorted[0], 3),
        "max": round(values_sorted[-1], 3),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()

    scenario = load_scenario(args.scenario)
    runs = int(scenario["runs"])
    adapter = scenario["adapter"]

    results: List[RunResult] = []
    for run_id in range(1, runs + 1):
        started = time.perf_counter()
        try:
            if adapter == "simulated":
                payload = run_simulated_adapter(scenario, run_id)
            elif adapter == "command":
                payload = run_command_adapter(
                    scenario["command"],
                    timeout_s=float(scenario.get("timeout_s", 60)),
                )
            else:
                raise ScenarioError(f"Unknown adapter: {adapter}")

            results.append(
                RunResult(
                    run_id=run_id,
                    scenario_id=scenario["scenario_id"],
                    mode=scenario["mode"],
                    status=payload.get("status", "error"),
                    avatar_preparation_time_ms=payload.get("avatar_preparation_time_ms"),
                    first_frame_latency_ms=payload.get("first_frame_latency_ms"),
                    steady_state_fps=payload.get("steady_state_fps"),
                    peak_vram_mb=payload.get("peak_vram_mb"),
                    duration_ms=payload.get(
                        "duration_ms",
                        (time.perf_counter() - started) * 1000.0,
                    ),
                    error_message=payload.get("error_message"),
                )
            )
        except Exception as exc:
            results.append(
                RunResult(
                    run_id=run_id,
                    scenario_id=scenario["scenario_id"],
                    mode=scenario["mode"],
                    status="error",
                    avatar_preparation_time_ms=None,
                    first_frame_latency_ms=None,
                    steady_state_fps=None,
                    peak_vram_mb=None,
                    duration_ms=(time.perf_counter() - started) * 1000.0,
                    error_message=str(exc),
                )
            )

    summary = summarize(results)
    report = {
        "scenario": scenario,
        "summary": summary,
        "results": [asdict(r) for r in results],
        "generated_at_epoch_ms": int(time.time() * 1000),
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    out_file = args.output_dir / f"{scenario['scenario_id']}_report.json"
    out_file.write_text(json.dumps(report, indent=2))
    print(json.dumps({"report": str(out_file), "summary": summary}))


if __name__ == "__main__":
    main()
