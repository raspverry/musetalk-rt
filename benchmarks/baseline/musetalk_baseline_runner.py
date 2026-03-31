#!/usr/bin/env python3
"""Real-command baseline runner for MuseTalk-like cold/warm session measurement.

This is wrapper-level instrumentation only (no runtime optimization).
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import argparse
import glob
import json
import os
import shlex
import subprocess
import time
from datetime import datetime, timezone
from typing import Dict, Optional, List

from runtime.session.warm_path_policy import resolve_policy

OOM_PATTERNS = ("out of memory", "cuda oom", "cudnn_status_alloc_failed")
SHELL_META = set("|&;<>()$`\\\n")


def detect_oom(stderr: str) -> bool:
    text = (stderr or "").lower()
    return any(token in text for token in OOM_PATTERNS)


def spawn_command(command: str) -> tuple[subprocess.Popen, str]:
    """Use shell=False when possible to reduce shell startup overhead."""
    if any(c in command for c in SHELL_META):
        return subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True), "shell"
    argv = shlex.split(command)
    return subprocess.Popen(argv, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True), "exec"


def run_cmd(command: str, timeout_s: float) -> Dict[str, object]:
    started = time.perf_counter()
    proc, spawn_mode = spawn_command(command)
    try:
        stdout, stderr = proc.communicate(timeout=timeout_s)
    except subprocess.TimeoutExpired:
        proc.kill()
        return {
            "returncode": -9,
            "stdout": "",
            "stderr": f"Timeout after {timeout_s}s",
            "duration_ms": (time.perf_counter() - started) * 1000.0,
            "spawn_mode": spawn_mode,
        }
    return {
        "returncode": proc.returncode,
        "stdout": stdout,
        "stderr": stderr,
        "duration_ms": (time.perf_counter() - started) * 1000.0,
        "spawn_mode": spawn_mode,
    }


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def run_lifecycle_stage(stage: str, command: str, timeout_s: float) -> Dict[str, object]:
    started_iso = _now_iso()
    started = time.perf_counter()
    result = run_cmd(command, timeout_s=timeout_s)
    ended_iso = _now_iso()
    ok = int(result["returncode"]) == 0
    return {
        "stage": stage,
        "status": "ok" if ok else "error",
        "started_at": started_iso,
        "ended_at": ended_iso,
        "duration_ms": (time.perf_counter() - started) * 1000.0,
        "returncode": int(result["returncode"]),
        "stderr_preview": str(result.get("stderr", ""))[:300],
        "spawn_mode": result.get("spawn_mode"),
        "signal_kind": "proxy_command",
    }


def run_lifecycle_path_probe(stage: str, path: str, timeout_s: float, poll_ms: float = 25.0) -> Dict[str, object]:
    started_iso = _now_iso()
    started = time.perf_counter()
    deadline = time.perf_counter() + timeout_s
    while time.perf_counter() < deadline:
        if path and os.path.exists(path):
            ended_iso = _now_iso()
            return {
                "stage": stage,
                "status": "ok",
                "started_at": started_iso,
                "ended_at": ended_iso,
                "duration_ms": (time.perf_counter() - started) * 1000.0,
                "returncode": 0,
                "stderr_preview": "",
                "spawn_mode": "probe",
                "signal_kind": "real_wired_avatar_probe",
                "observed_path": path,
            }
        time.sleep(max(poll_ms, 1.0) / 1000.0)
    ended_iso = _now_iso()
    return {
        "stage": stage,
        "status": "error",
        "started_at": started_iso,
        "ended_at": ended_iso,
        "duration_ms": (time.perf_counter() - started) * 1000.0,
        "returncode": 1,
        "stderr_preview": f"path not observed before timeout: {path}",
        "spawn_mode": "probe",
        "signal_kind": "real_wired_avatar_probe",
        "observed_path": path,
        "failure_reason": "path_probe_timeout",
    }


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
    parser.add_argument("--policy-config", default="benchmarks/baseline/policies/warm_path_policy.json")
    parser.add_argument("--policy-mode", choices=["default", "fallback", "experimental"], default="default")
    parser.add_argument("--chunk-ms-override", type=int, default=None)
    parser.add_argument("--startup-chunks-override", type=int, default=None)
    parser.add_argument("--cleanup-glob", default="")
    parser.add_argument("--cleanup-path", default="")
    parser.add_argument("--timeout-s", type=float, default=600.0)
    parser.add_argument("--poll-ms", type=float, default=50.0)
    parser.add_argument("--lifecycle-session-start-cmd", default="")
    parser.add_argument("--lifecycle-avatar-ready-cmd", default="")
    parser.add_argument("--lifecycle-audio-accepted-cmd", default="")
    parser.add_argument("--lifecycle-first-frame-signal-cmd", default="")
    parser.add_argument("--lifecycle-timeout-s", type=float, default=2.0)
    parser.add_argument("--enable-limited-real-lifecycle-wiring", action="store_true")
    parser.add_argument("--real-avatar-ready-path", default="")
    parser.add_argument("--real-avatar-ready-timeout-s", type=float, default=0.75)
    parser.add_argument("--real-first-frame-source", choices=["infer_json", "file_glob"], default="infer_json")
    parser.add_argument("--allow-proxy-fallback-on-real-wire-failure", action="store_true")
    parser.add_argument("--enable-flagged-e2e-session-experiment", action="store_true")
    parser.add_argument("--enable-real-session-start-observation", action="store_true")
    parser.add_argument("--real-session-start-min-alive-ms", type=float, default=20.0)
    parser.add_argument("--enable-real-audio-accepted-observation", action="store_true")
    parser.add_argument("--real-audio-accepted-marker-path", default="")
    args = parser.parse_args()


    ffmpeg_in_infer_cmd = False
    lifecycle_stage_outcomes: List[Dict[str, object]] = []
    lifecycle_any_failed = False
    lifecycle_proxy_fallbacks: List[Dict[str, str]] = []
    e2e_experiment: Dict[str, object] = {
        "enabled": bool(args.enable_flagged_e2e_session_experiment),
        "status": "not_enabled",
        "failure_classification": None,
        "note": "non-production telemetry experiment path",
    }

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

    prep_spawn_mode = None
    if args.mode == "cold_start":
        if not args.prep_cmd:
            raise SystemExit("cold_start requires --prep-cmd")
        prep = run_cmd(args.prep_cmd, args.timeout_s)
        prep_spawn_mode = prep.get("spawn_mode")
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
                    "spawn_mode": prep_spawn_mode,
                },
            }))
            return
    else:
        prep_ms = 0.0

    lifecycle_stages = [
        ("session_start", args.lifecycle_session_start_cmd),
        ("avatar_ready_or_warm_assumed", args.lifecycle_avatar_ready_cmd),
        ("audio_accepted", args.lifecycle_audio_accepted_cmd),
        ("first_speaking_frame_signal", args.lifecycle_first_frame_signal_cmd),
    ]
    for stage_name, stage_cmd in lifecycle_stages:
        if stage_name == "first_speaking_frame_signal" and args.enable_limited_real_lifecycle_wiring:
            # real-wired first-frame stage is evaluated from infer output after command execution
            continue
        if stage_name == "session_start" and args.enable_real_session_start_observation:
            # real-wired session start is evaluated from infer process spawn below
            continue
        if stage_name == "audio_accepted" and args.enable_real_audio_accepted_observation:
            # real-wired audio-accepted is evaluated from infer metrics/marker below
            continue
        if stage_name == "avatar_ready_or_warm_assumed" and args.enable_limited_real_lifecycle_wiring:
            if args.real_avatar_ready_path:
                outcome = run_lifecycle_path_probe(
                    stage_name,
                    path=args.real_avatar_ready_path,
                    timeout_s=args.real_avatar_ready_timeout_s,
                )
                if outcome["status"] != "ok" and stage_cmd and args.allow_proxy_fallback_on_real_wire_failure:
                    fallback = run_lifecycle_stage(stage_name, stage_cmd, timeout_s=args.lifecycle_timeout_s)
                    fallback["signal_kind"] = "proxy_fallback_command"
                    fallback["fallback_from_real_wiring"] = True
                    fallback["fallback_reason"] = "avatar_path_probe_failed"
                    lifecycle_proxy_fallbacks.append(
                        {"stage": stage_name, "reason": "avatar_path_probe_failed"}
                    )
                    outcome = fallback
            elif stage_cmd and args.allow_proxy_fallback_on_real_wire_failure:
                outcome = run_lifecycle_stage(stage_name, stage_cmd, timeout_s=args.lifecycle_timeout_s)
                outcome["signal_kind"] = "proxy_fallback_command"
                outcome["fallback_from_real_wiring"] = True
                outcome["fallback_reason"] = "avatar_real_probe_unconfigured"
                lifecycle_proxy_fallbacks.append(
                    {"stage": stage_name, "reason": "avatar_real_probe_unconfigured"}
                )
            else:
                outcome = {
                    "stage": stage_name,
                    "status": "error",
                    "started_at": _now_iso(),
                    "ended_at": _now_iso(),
                    "duration_ms": 0.0,
                    "returncode": 2,
                    "stderr_preview": "real avatar wiring enabled but no probe path configured",
                    "spawn_mode": "probe",
                    "signal_kind": "real_wired_path_probe",
                    "failure_reason": "avatar_real_probe_unconfigured",
                }
        elif not stage_cmd:
            continue
        else:
            outcome = run_lifecycle_stage(stage_name, stage_cmd, timeout_s=args.lifecycle_timeout_s)
        lifecycle_stage_outcomes.append(outcome)
        if outcome["status"] != "ok":
            lifecycle_any_failed = True
            break

    selection = resolve_policy(
        policy_path=args.policy_config,
        policy_mode=args.policy_mode,
        chunk_ms_override=args.chunk_ms_override,
        startup_chunks_override=args.startup_chunks_override,
    )
    resolved_infer_cmd = args.infer_cmd.format(
        chunk_ms=selection.chunk_ms,
        startup_chunks=selection.startup_chunks,
    )
    ffmpeg_in_infer_cmd = "ffmpeg" in resolved_infer_cmd.lower()

    infer_start_ts = time.time()
    proc, infer_spawn_mode = spawn_command(resolved_infer_cmd)
    if args.enable_real_session_start_observation:
        stage_started_iso = _now_iso()
        stage_started = time.perf_counter()
        observed_ok = bool(proc.pid)
        failure_reason = None
        stderr_preview = ""
        min_alive_s = max(float(args.real_session_start_min_alive_ms), 0.0) / 1000.0
        if observed_ok and min_alive_s > 0:
            time.sleep(min_alive_s)
            if proc.poll() is not None:
                observed_ok = False
                failure_reason = "infer_process_exited_before_session_start_observation"
                stderr_preview = "infer process exited before min-alive observation window"
        if not observed_ok and not failure_reason:
            failure_reason = "infer_process_not_started"
            stderr_preview = "infer process did not start"

        if observed_ok:
            lifecycle_stage_outcomes.insert(
                0,
                {
                    "stage": "session_start",
                    "status": "ok",
                    "started_at": stage_started_iso,
                    "ended_at": _now_iso(),
                    "duration_ms": (time.perf_counter() - stage_started) * 1000.0,
                    "returncode": 0,
                    "stderr_preview": "",
                    "spawn_mode": infer_spawn_mode,
                    "signal_kind": "real_wired_session_start_observation",
                },
            )
        elif args.lifecycle_session_start_cmd and args.allow_proxy_fallback_on_real_wire_failure:
            fallback = run_lifecycle_stage("session_start", args.lifecycle_session_start_cmd, timeout_s=args.lifecycle_timeout_s)
            fallback["signal_kind"] = "proxy_fallback_command"
            fallback["fallback_from_real_wiring"] = True
            fallback["fallback_reason"] = failure_reason
            lifecycle_proxy_fallbacks.append({"stage": "session_start", "reason": str(failure_reason)})
            lifecycle_stage_outcomes.insert(0, fallback)
        else:
            lifecycle_stage_outcomes.insert(
                0,
                {
                    "stage": "session_start",
                    "status": "error",
                    "started_at": stage_started_iso,
                    "ended_at": _now_iso(),
                    "duration_ms": (time.perf_counter() - stage_started) * 1000.0,
                    "returncode": 1,
                    "stderr_preview": stderr_preview,
                    "spawn_mode": infer_spawn_mode,
                    "signal_kind": "real_wired_session_start_observation",
                    "failure_reason": failure_reason,
                },
            )
            lifecycle_any_failed = True

    peak = max_vram_mb()
    first_frame_ts = None
    # When prefer-infer-json is enabled, anchor should come from infer metrics before marker file polling.
    audio_accepted_ts = None if args.prefer_infer_json else marker_mtime(args.audio_accepted_marker)

    poll_s = args.poll_ms / 1000.0
    deadline = time.perf_counter() + args.timeout_s
    while proc.poll() is None:
        sample = max_vram_mb()
        if sample is not None and (peak is None or sample > peak):
            peak = sample

        if not args.prefer_infer_json and audio_accepted_ts is None:
            audio_accepted_ts = marker_mtime(args.audio_accepted_marker)

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

    if args.prefer_infer_json:
        audio_accepted_ts = infer_metrics.get("audio_accepted_ts") or marker_mtime(args.audio_accepted_marker)
    real_audio_marker_ts = marker_mtime(args.real_audio_accepted_marker_path)

    frame_count = int(infer_metrics.get("frame_count", 0)) if infer_metrics else count_frames(args.frame_glob)
    if first_frame_ts is None:
        first_frame_ts = infer_metrics.get("first_frame_ts") if infer_metrics else first_frame_mtime(args.frame_glob)
    if audio_accepted_ts is None:
        audio_accepted_ts = marker_mtime(args.audio_accepted_marker)

    if args.enable_real_audio_accepted_observation:
        observed_audio_ts = infer_metrics.get("audio_accepted_ts") or real_audio_marker_ts
        source = (
            "infer_json_audio_accepted_ts"
            if infer_metrics.get("audio_accepted_ts") is not None
            else ("marker_path" if real_audio_marker_ts is not None else "missing")
        )
        if observed_audio_ts is not None:
            lifecycle_stage_outcomes.append(
                {
                    "stage": "audio_accepted",
                    "status": "ok",
                    "started_at": _now_iso(),
                    "ended_at": _now_iso(),
                    "duration_ms": 0.0,
                    "returncode": 0,
                    "stderr_preview": "",
                    "spawn_mode": "probe",
                    "signal_kind": "real_wired_audio_accepted_observation",
                    "audio_accepted_ts": observed_audio_ts,
                    "audio_accepted_source_used": source,
                }
            )
        elif args.lifecycle_audio_accepted_cmd and args.allow_proxy_fallback_on_real_wire_failure:
            fallback = run_lifecycle_stage("audio_accepted", args.lifecycle_audio_accepted_cmd, timeout_s=args.lifecycle_timeout_s)
            fallback["signal_kind"] = "proxy_fallback_command"
            fallback["fallback_from_real_wiring"] = True
            fallback["fallback_reason"] = (
                "audio_accepted_path_contract_missing"
                if not args.real_audio_accepted_marker_path and infer_metrics.get("audio_accepted_ts") is None
                else "audio_accepted_observation_missing"
            )
            lifecycle_proxy_fallbacks.append(
                {"stage": "audio_accepted", "reason": str(fallback["fallback_reason"])}
            )
            lifecycle_stage_outcomes.append(fallback)
        else:
            lifecycle_stage_outcomes.append(
                {
                    "stage": "audio_accepted",
                    "status": "error",
                    "started_at": _now_iso(),
                    "ended_at": _now_iso(),
                    "duration_ms": 0.0,
                    "returncode": 1,
                    "stderr_preview": "audio_accepted signal not observed",
                    "spawn_mode": "probe",
                    "signal_kind": "real_wired_audio_accepted_observation",
                    "failure_reason": (
                        "audio_accepted_path_contract_missing"
                        if not args.real_audio_accepted_marker_path and infer_metrics.get("audio_accepted_ts") is None
                        else "audio_accepted_observation_missing"
                    ),
                }
            )
            lifecycle_any_failed = True

    last_frame_ts = infer_metrics.get("last_frame_ts") if infer_metrics else newest_frame_mtime(args.frame_glob)

    if args.enable_limited_real_lifecycle_wiring:
        stage_start_iso = _now_iso()
        stage_start = time.perf_counter()
        source_used = "infer_json"
        observed_ts = infer_metrics.get("first_frame_ts")
        if args.real_first_frame_source == "file_glob":
            source_used = "file_glob"
            observed_ts = first_frame_mtime(args.frame_glob)
        if observed_ts is None and first_frame_ts is not None:
            observed_ts = first_frame_ts
            source_used = "fallback_existing_first_frame_ts"

        stage_payload = {
            "stage": "first_speaking_frame_signal",
            "started_at": stage_start_iso,
            "ended_at": _now_iso(),
            "duration_ms": (time.perf_counter() - stage_start) * 1000.0,
            "spawn_mode": "probe",
            "first_frame_ts": observed_ts,
            "first_frame_source_used": source_used,
        }
        if observed_ts is not None:
            stage_payload.update(
                {
                    "status": "ok",
                    "returncode": 0,
                    "stderr_preview": "",
                    "signal_kind": "real_wired_first_frame_observation",
                }
            )
        elif args.lifecycle_first_frame_signal_cmd and args.allow_proxy_fallback_on_real_wire_failure:
            fallback = run_lifecycle_stage(
                "first_speaking_frame_signal",
                args.lifecycle_first_frame_signal_cmd,
                timeout_s=args.lifecycle_timeout_s,
            )
            fallback["signal_kind"] = "proxy_fallback_command"
            fallback["fallback_from_real_wiring"] = True
            fallback["fallback_reason"] = "first_frame_observation_missing"
            lifecycle_proxy_fallbacks.append(
                {"stage": "first_speaking_frame_signal", "reason": "first_frame_observation_missing"}
            )
            stage_payload = fallback
        else:
            stage_payload.update(
                {
                    "status": "error",
                    "returncode": 1,
                    "stderr_preview": "first_frame_ts not observed",
                    "signal_kind": "real_wired_first_frame_observation",
                    "failure_reason": "first_frame_observation_missing",
                }
            )
        lifecycle_stage_outcomes.append(stage_payload)
        real_first_frame_ok = stage_payload["status"] == "ok"
        if not real_first_frame_ok:
            lifecycle_any_failed = True

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
    if lifecycle_any_failed:
        status = "error"
    elif proc.returncode != 0:
        status = "oom" if detect_oom(stderr) else "crash"
    elif frame_count == 0 or first_frame_ts is None:
        status = "error"
    elif args.require_audio_accepted_marker and audio_accepted_ts is None:
        status = "partial"

    if args.enable_flagged_e2e_session_experiment:
        failure_classification = None
        if lifecycle_any_failed:
            failure_classification = "lifecycle_stage_failed"
        elif proc.returncode != 0:
            failure_classification = "infer_process_failed"
        elif first_frame_ts is None:
            failure_classification = "first_frame_not_observed"
        e2e_experiment = {
            "enabled": True,
            "status": "ok" if failure_classification is None else "error",
            "failure_classification": failure_classification,
            "stage_count": len(lifecycle_stage_outcomes),
            "proxy_fallback_count": len(lifecycle_proxy_fallbacks),
            "stage_signal_kinds": [s.get("signal_kind", "unknown") for s in lifecycle_stage_outcomes],
            "note": "bounded non-production end-to-end session experiment behind flag",
        }

    provenance = {
        "mode": args.mode,
        "avatar_preparation_time_ms": "prep_cmd_wall_clock" if args.mode == "cold_start" else "warm_path_prep_skipped_zero",
        "first_frame_latency_ms": f"first_frame_ts_minus_{latency_anchor}",
        "first_frame_latency_anchor": latency_anchor,
        "audio_accepted_marker_present": audio_accepted_ts is not None,
        "steady_state_fps": "infer_json_steady_state_fps" if infer_metrics.get("steady_state_fps") is not None else "(frame_count-1)/(last_frame-first_frame)",
        "peak_vram_mb": "nvidia_smi_sampled_max",
        "frame_source": infer_metrics.get("frame_source", "file_glob_mtime"),
        "infer_spawn_mode": infer_spawn_mode,
        "prep_spawn_mode": prep_spawn_mode,
        "file_polling_used": not args.prefer_infer_json,
        "ffmpeg_in_hot_path_cmd": ffmpeg_in_infer_cmd,
        "chunk_ms": infer_metrics.get("chunk_ms"),
        "startup_chunks": infer_metrics.get("startup_chunks"),
        "chunk_overhead_ms": infer_metrics.get("chunk_overhead_ms"),
        "startup_delay_ms": infer_metrics.get("startup_delay_ms"),
        "frame_jitter_ms": infer_metrics.get("frame_jitter_ms"),
        "chunk_boundary_rate_hz": infer_metrics.get("chunk_boundary_rate_hz"),
        "continuity_risk_hint": infer_metrics.get("continuity_risk_hint"),
        "continuity_risk_basis": infer_metrics.get("continuity_risk_basis"),
        "cadence_profile": infer_metrics.get("cadence_profile", "unknown"),
        "policy_mode": selection.policy_mode,
        "policy_selection_source": selection.source,
        "policy_chunk_ms": selection.chunk_ms,
        "policy_startup_chunks": selection.startup_chunks,
        "lifecycle_stage_count": len(lifecycle_stage_outcomes),
        "lifecycle_stage_statuses": [s["status"] for s in lifecycle_stage_outcomes],
        "lifecycle_signal_kinds": [s.get("signal_kind", "unknown") for s in lifecycle_stage_outcomes],
        "lifecycle_proxy_fallbacks": lifecycle_proxy_fallbacks,
        "lifecycle_signals_are_proxy": not args.enable_limited_real_lifecycle_wiring,
        "limited_real_lifecycle_wiring_enabled": args.enable_limited_real_lifecycle_wiring,
        "avatar_real_probe_path": args.real_avatar_ready_path or None,
        "real_audio_accepted_marker_path": args.real_audio_accepted_marker_path or None,
        "flagged_e2e_session_experiment_enabled": args.enable_flagged_e2e_session_experiment,
        "proxy_fallback_permissive": args.allow_proxy_fallback_on_real_wire_failure,
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
        "lifecycle_stage_outcomes": lifecycle_stage_outcomes,
        "end_to_end_experiment": e2e_experiment,
        "measurement_provenance": provenance,
    }))


if __name__ == "__main__":
    main()
