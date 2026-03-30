#!/usr/bin/env python3
"""Real-command baseline runner for MuseTalk-like cold/warm session measurement.

This is wrapper-level instrumentation only (no runtime optimization).
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
    proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        stdout, stderr = proc.communicate(timeout=timeout_s)
    except subprocess.TimeoutExpired:
        proc.kill()
        return {"returncode": -9, "stdout": "", "stderr": f"Timeout after {timeout_s}s", "duration_ms": (time.perf_counter() - started) * 1000.0}
    return {"returncode": proc.returncode, "stdout": stdout, "stderr": stderr, "duration_ms": (time.perf_counter() - started) * 1000.0}


def parse_infer_metrics(stdout: str) -> Dict[str, object]:
    for line in stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict) and isinstance(payload.get("infer_metrics"), dict):
            return payload["infer_metrics"]
    return {}


def max_vram_mb() -> Optional[float]:
    try:
        out = subprocess.check_output(["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"], text=True, stderr=subprocess.DEVNULL)
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


def marker_mtime(path: str) -> Optional[float]:
    if not path or not os.path.exists(path):
        return None
    return os.path.getmtime(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["cold_start", "warm_start"], required=True)
    parser.add_argument("--prep-cmd", default="")
    parser.add_argument("--infer-cmd", required=True)
    parser.add_argument("--frame-glob", required=True)
    parser.add_argument("--audio-accepted-marker", default="")
    parser.add_argument("--require-audio-accepted-marker", action="store_true")
    parser.add_argument("--prefer-infer-json", action="store_true")
    parser.add_argument("--cleanup-glob", default="")
    parser.add_argument("--cleanup-path", default="")
    parser.add_argument("--timeout-s", type=float, default=600.0)
    parser.add_argument("--poll-ms", type=float, default=50.0)
    args = parser.parse_args()

    if args.cleanup_glob:
        for p in glob.glob(args.cleanup_glob):
            try:
                os.remove(p)
            except OSError:
                pass
    if args.cleanup_path and os.path.exists(args.cleanup_path):
        try:
            os.remove(args.cleanup_path)
        except OSError:
            pass

    if args.mode == "cold_start":
        if not args.prep_cmd:
            raise SystemExit("cold_start requires --prep-cmd")
        prep = run_cmd(args.prep_cmd, args.timeout_s)
        prep_ms = float(prep["duration_ms"])
        prep_stderr = str(prep["stderr"])
        if int(prep["returncode"]) != 0:
            status = "oom" if detect_oom(prep_stderr) else "crash"
            print(json.dumps({
                "status": status,
                "avatar_preparation_time_ms": prep_ms,
                "first_frame_latency_ms": None,
                "steady_state_fps": None,
                "peak_vram_mb": max_vram_mb(),
                "error_message": prep_stderr[:500],
                "measurement_provenance": {
                    "mode": args.mode,
                    "avatar_preparation_time_ms": "prep_cmd_wall_clock",
                    "first_frame_latency_ms": "not_measured_prep_failed",
                    "steady_state_fps": "not_measured_prep_failed",
                    "peak_vram_mb": "nvidia_smi_sampled_max",
                },
            }))
            return
    else:
        prep_ms = 0.0

    infer_start_ts = time.time()
    proc = subprocess.Popen(args.infer_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    peak = max_vram_mb()
    first_frame_ts = None
    audio_accepted_ts = marker_mtime(args.audio_accepted_marker)

    poll_s = args.poll_ms / 1000.0
    deadline = time.perf_counter() + args.timeout_s
    while proc.poll() is None:
        sample = max_vram_mb()
        if sample is not None and (peak is None or sample > peak):
            peak = sample

        if audio_accepted_ts is None:
            audio_accepted_ts = marker_mtime(args.audio_accepted_marker)

        # Only use file polling as primary first-frame source when infer JSON metrics are not preferred.
        if not args.prefer_infer_json:
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

    infer_metrics = parse_infer_metrics(stdout) if args.prefer_infer_json else {}

    frame_count = int(infer_metrics.get("frame_count", 0)) if infer_metrics else count_frames(args.frame_glob)
    if first_frame_ts is None:
        first_frame_ts = infer_metrics.get("first_frame_ts") if infer_metrics else first_frame_mtime(args.frame_glob)
    if audio_accepted_ts is None:
        audio_accepted_ts = infer_metrics.get("audio_accepted_ts") if infer_metrics else marker_mtime(args.audio_accepted_marker)

    last_frame_ts = infer_metrics.get("last_frame_ts") if infer_metrics else newest_frame_mtime(args.frame_glob)

    latency_anchor = "infer_cmd_start"
    latency_anchor_ts = infer_start_ts
    if audio_accepted_ts is not None:
        latency_anchor = "audio_accepted_marker"
        latency_anchor_ts = float(audio_accepted_ts)

    first_frame_latency_ms = (float(first_frame_ts) - latency_anchor_ts) * 1000.0 if first_frame_ts is not None else None

    steady_fps = infer_metrics.get("steady_state_fps")
    if steady_fps is None and first_frame_ts is not None and last_frame_ts is not None and frame_count >= 2 and float(last_frame_ts) > float(first_frame_ts):
        steady_fps = (frame_count - 1) / (float(last_frame_ts) - float(first_frame_ts))

    status = "ok"
    if proc.returncode != 0:
        status = "oom" if detect_oom(stderr) else "crash"
    elif frame_count == 0 or first_frame_ts is None:
        status = "error"
    elif args.require_audio_accepted_marker and audio_accepted_ts is None:
        status = "partial"

    provenance = {
        "mode": args.mode,
        "avatar_preparation_time_ms": "prep_cmd_wall_clock" if args.mode == "cold_start" else "warm_path_prep_skipped_zero",
        "first_frame_latency_ms": f"first_frame_ts_minus_{latency_anchor}",
        "first_frame_latency_anchor": latency_anchor,
        "audio_accepted_marker_present": audio_accepted_ts is not None,
        "steady_state_fps": "infer_json_steady_state_fps" if infer_metrics.get("steady_state_fps") is not None else "(frame_count-1)/(last_frame-first_frame)",
        "peak_vram_mb": "nvidia_smi_sampled_max",
        "frame_source": infer_metrics.get("frame_source", "file_glob_mtime"),
    }

    print(json.dumps({
        "status": status,
        "avatar_preparation_time_ms": prep_ms,
        "first_frame_latency_ms": first_frame_latency_ms,
        "steady_state_fps": steady_fps,
        "peak_vram_mb": peak,
        "error_message": (stderr or "")[:500] if status not in ("ok", "partial") else None,
        "duration_ms": (infer_end - infer_start_ts) * 1000.0,
        "frame_count": frame_count,
        "measurement_provenance": provenance,
    }))


if __name__ == "__main__":
    main()
