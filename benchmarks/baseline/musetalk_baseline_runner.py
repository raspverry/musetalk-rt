#!/usr/bin/env python3
"""Real-command baseline runner for MuseTalk-like cold/warm session measurement.

This script is intentionally wrapper-level instrumentation and avoids major runtime rewrites.
It can drive an upstream MuseTalk command path (preferred) or any command that emits frames
into a directory to approximate hot-path timing when streaming is not yet wired.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import subprocess
import time
from typing import Dict, Optional


OOM_PATTERNS = ("out of memory", "cuda oom", "cudnn_status_alloc_failed")


def detect_oom(stderr: str) -> bool:
    text = (stderr or "").lower()
    return any(token in text for token in OOM_PATTERNS)


def run_cmd(command: str, timeout_s: float) -> Dict[str, object]:
    started = time.perf_counter()
    proc = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        stdout, stderr = proc.communicate(timeout=timeout_s)
    except subprocess.TimeoutExpired:
        proc.kill()
        return {
            "returncode": -9,
            "stdout": "",
            "stderr": f"Timeout after {timeout_s}s",
            "duration_ms": (time.perf_counter() - started) * 1000.0,
        }

    return {
        "returncode": proc.returncode,
        "stdout": stdout,
        "stderr": stderr,
        "duration_ms": (time.perf_counter() - started) * 1000.0,
    }


def max_vram_mb() -> Optional[float]:
    try:
        out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        return None

    vals = []
    for line in out.splitlines():
        try:
            vals.append(float(line.strip()))
        except ValueError:
            pass
    return max(vals) if vals else None


def count_frames(pattern: str) -> int:
    return len(glob.glob(pattern))


def newest_frame_mtime(pattern: str) -> Optional[float]:
    files = glob.glob(pattern)
    if not files:
        return None
    return max(os.path.getmtime(f) for f in files)


def first_frame_mtime(pattern: str) -> Optional[float]:
    files = glob.glob(pattern)
    if not files:
        return None
    return min(os.path.getmtime(f) for f in files)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["cold_start", "warm_start"], required=True)
    parser.add_argument("--prep-cmd", default="")
    parser.add_argument("--infer-cmd", required=True)
    parser.add_argument("--frame-glob", required=True)
    parser.add_argument("--cleanup-glob", default="")
    parser.add_argument("--timeout-s", type=float, default=600.0)
    parser.add_argument("--poll-ms", type=float, default=50.0)
    args = parser.parse_args()

    if args.cleanup_glob:
        for p in glob.glob(args.cleanup_glob):
            try:
                os.remove(p)
            except OSError:
                pass

    prep_ms = None
    prep_status = 0
    prep_stderr = ""

    if args.mode == "cold_start":
        if not args.prep_cmd:
            raise SystemExit("cold_start requires --prep-cmd")
        prep = run_cmd(args.prep_cmd, args.timeout_s)
        prep_ms = float(prep["duration_ms"])
        prep_status = int(prep["returncode"])
        prep_stderr = str(prep["stderr"])
        if prep_status != 0:
            status = "oom" if detect_oom(prep_stderr) else "crash"
            print(
                json.dumps(
                    {
                        "status": status,
                        "avatar_preparation_time_ms": prep_ms,
                        "first_frame_latency_ms": None,
                        "steady_state_fps": None,
                        "peak_vram_mb": max_vram_mb(),
                        "error_message": prep_stderr[:500],
                    }
                )
            )
            return
    else:
        prep_ms = 0.0

    start = time.time()
    proc = subprocess.Popen(
        args.infer_cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    peak = max_vram_mb()
    first_frame_ts = None

    poll_s = args.poll_ms / 1000.0
    deadline = time.perf_counter() + args.timeout_s
    while proc.poll() is None:
        sample = max_vram_mb()
        if sample is not None and (peak is None or sample > peak):
            peak = sample

        ff = first_frame_mtime(args.frame_glob)
        if ff is not None:
            first_frame_ts = ff
            break

        if time.perf_counter() >= deadline:
            proc.kill()
            break

        time.sleep(poll_s)

    stdout, stderr = proc.communicate()
    infer_end = time.time()

    frame_count = count_frames(args.frame_glob)
    if first_frame_ts is None:
        first_frame_ts = first_frame_mtime(args.frame_glob)

    last_frame_ts = newest_frame_mtime(args.frame_glob)

    if first_frame_ts is not None:
        first_frame_latency_ms = (first_frame_ts - start) * 1000.0
    else:
        first_frame_latency_ms = None

    steady_fps = None
    if first_frame_ts is not None and last_frame_ts is not None and frame_count >= 2 and last_frame_ts > first_frame_ts:
        steady_fps = (frame_count - 1) / (last_frame_ts - first_frame_ts)

    status = "ok"
    if proc.returncode != 0:
        status = "oom" if detect_oom(stderr) else "crash"
    elif frame_count == 0:
        status = "error"

    print(
        json.dumps(
            {
                "status": status,
                "avatar_preparation_time_ms": prep_ms,
                "first_frame_latency_ms": first_frame_latency_ms,
                "steady_state_fps": steady_fps,
                "peak_vram_mb": peak,
                "error_message": (stderr or "")[:500] if status != "ok" else None,
                "duration_ms": (infer_end - start) * 1000.0,
                "frame_count": frame_count,
            }
        )
    )


if __name__ == "__main__":
    main()
