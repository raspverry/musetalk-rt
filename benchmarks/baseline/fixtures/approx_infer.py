#!/usr/bin/env python3
"""Approximate hot-path frame emitter when real streaming integration is unavailable.

This is *not* a MuseTalk model implementation. It approximates session hot-path timing by
emitting an optional audio-accepted marker followed by frame cadence simulation.
"""

import argparse
import json
import random
import time
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('--frames-dir', required=True)
p.add_argument('--audio-accepted-marker', default='')
p.add_argument('--audio-accept-ms', type=float, default=50.0)
p.add_argument('--post-accept-startup-ms', type=float, default=420.0)
p.add_argument('--fps', type=float, default=24.0)
p.add_argument('--num-frames', type=int, default=48)
p.add_argument('--disable-frame-write', action='store_true')
p.add_argument('--emit-metrics-json', action='store_true')
# Chunk-boundary model for warm-path startup latency analysis.
p.add_argument('--chunk-ms', type=float, default=0.0)
p.add_argument('--startup-chunks', type=int, default=0)
p.add_argument('--chunk-overhead-ms', type=float, default=0.0)
p.add_argument('--cadence-profile', choices=['fixed', 'tts_bursty', 'jittery'], default='fixed')
p.add_argument('--jitter-min-ms', type=float, default=0.0)
p.add_argument('--jitter-max-ms', type=float, default=0.0)
p.add_argument('--first-chunk-delay-ms', type=float, default=0.0)
p.add_argument('--drop-rate', type=float, default=0.0)
p.add_argument('--random-seed', type=int, default=7)
args = p.parse_args()
rng = random.Random(args.random_seed)

out = Path(args.frames_dir)
out.mkdir(parents=True, exist_ok=True)

time.sleep(args.audio_accept_ms / 1000.0)
audio_accepted_ts = time.time()
if args.audio_accepted_marker:
    marker = Path(args.audio_accepted_marker)
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text('audio_accepted')

# Deterministic cadence multipliers to emulate bursty TTS/session chunk arrivals.
BURSTY_MULT = [0.8, 1.35, 0.9, 1.25, 0.95, 1.15]
chunk_startup_ms = 0.0
if args.startup_chunks > 0 and args.chunk_ms > 0:
    per_chunk_ms = args.chunk_ms + max(args.chunk_overhead_ms, 0.0)
    if args.cadence_profile == 'fixed':
        chunk_startup_ms = args.startup_chunks * per_chunk_ms
    else:
        for i in range(args.startup_chunks):
            chunk_startup_ms += per_chunk_ms * BURSTY_MULT[i % len(BURSTY_MULT)]

startup_ms = max(args.post_accept_startup_ms, chunk_startup_ms)
startup_ms += max(args.first_chunk_delay_ms, 0.0)
time.sleep(startup_ms / 1000.0)

first_frame_ts = None
frame_timestamps = []
interval = 1.0 / max(args.fps, 0.1)
frame_payload = b'\x89PNG\r\n' + (b'0' * 65536)
for idx in range(args.num_frames):
    if args.drop_rate > 0 and rng.random() < min(max(args.drop_rate, 0.0), 0.9):
        time.sleep(interval)
    now_ts = time.time()
    if first_frame_ts is None:
        first_frame_ts = now_ts
    frame_timestamps.append(now_ts)
    if not args.disable_frame_write:
        (out / f'frame_{idx:05d}.png').write_bytes(frame_payload)
    cadence_mult = 1.0
    if args.cadence_profile == 'tts_bursty':
        cadence_mult = BURSTY_MULT[idx % len(BURSTY_MULT)]
    elif args.cadence_profile == 'jittery':
        cadence_mult = 1.0 + rng.uniform(-0.25, 0.35)
    jitter_sleep_ms = 0.0
    if args.jitter_max_ms > 0:
        low = min(args.jitter_min_ms, args.jitter_max_ms)
        high = max(args.jitter_min_ms, args.jitter_max_ms)
        jitter_sleep_ms = rng.uniform(low, high)
    sleep_s = max(interval * cadence_mult + (jitter_sleep_ms / 1000.0), 0.0)
    time.sleep(sleep_s)

last_frame_ts = time.time()
steady_state_fps = None
if first_frame_ts is not None and last_frame_ts > first_frame_ts and args.num_frames >= 2:
    steady_state_fps = (args.num_frames - 1) / (last_frame_ts - first_frame_ts)

frame_jitter_ms = None
if len(frame_timestamps) >= 3:
    intervals = [frame_timestamps[i] - frame_timestamps[i - 1] for i in range(1, len(frame_timestamps))]
    avg = sum(intervals) / len(intervals)
    variance = sum((x - avg) ** 2 for x in intervals) / len(intervals)
    frame_jitter_ms = (variance ** 0.5) * 1000.0

chunk_boundary_rate_hz = None
if args.chunk_ms > 0:
    chunk_boundary_rate_hz = 1000.0 / args.chunk_ms

continuity_risk_basis = 'policy_threshold'
if args.chunk_ms <= 80 and args.startup_chunks <= 1:
    continuity_risk_hint = 'high_boundary_churn'
elif args.chunk_ms <= 120 and args.startup_chunks <= 2:
    continuity_risk_hint = 'medium_boundary_churn'
else:
    continuity_risk_hint = 'lower_boundary_churn'

# Diagnosability upgrade for fixed cadence: if measured frame jitter is very low and
# startup delay did not inflate beyond expected chunk-driven startup, downgrade one level.
if (
    args.cadence_profile == 'fixed'
    and continuity_risk_hint == 'medium_boundary_churn'
    and frame_jitter_ms is not None
    and frame_jitter_ms < 0.12
    and chunk_startup_ms > 0
    and startup_ms <= (chunk_startup_ms * 1.05)
):
    continuity_risk_hint = 'lower_boundary_churn'
    continuity_risk_basis = 'policy_plus_observed_stability'

if args.cadence_profile == 'tts_bursty' and continuity_risk_hint == 'medium_boundary_churn':
    continuity_risk_hint = 'medium_plus_bursty'
if args.cadence_profile == 'jittery' and continuity_risk_hint in ('lower_boundary_churn', 'medium_boundary_churn'):
    continuity_risk_hint = 'high_boundary_churn'
    continuity_risk_basis = 'policy_plus_observed_instability'

if args.emit_metrics_json:
    print(
        json.dumps(
            {
                'infer_metrics': {
                    'audio_accepted_ts': audio_accepted_ts,
                    'first_frame_ts': first_frame_ts,
                    'last_frame_ts': last_frame_ts,
                    'frame_count': args.num_frames,
                    'steady_state_fps': steady_state_fps,
                    'frame_source': 'in_memory_no_file_write' if args.disable_frame_write else 'file_write',
                    'chunk_ms': args.chunk_ms,
                    'startup_chunks': args.startup_chunks,
                    'chunk_overhead_ms': args.chunk_overhead_ms,
                    'startup_delay_ms': startup_ms,
                    'frame_jitter_ms': frame_jitter_ms,
                    'chunk_boundary_rate_hz': chunk_boundary_rate_hz,
                    'continuity_risk_hint': continuity_risk_hint,
                    'continuity_risk_basis': continuity_risk_basis,
                    'cadence_profile': args.cadence_profile,
                    'jitter_min_ms': args.jitter_min_ms,
                    'jitter_max_ms': args.jitter_max_ms,
                    'first_chunk_delay_ms': args.first_chunk_delay_ms,
                    'drop_rate': args.drop_rate,
                    'random_seed': args.random_seed,
                }
            }
        )
    )
