#!/usr/bin/env python3
"""Approximate hot-path frame emitter when real streaming integration is unavailable.

This is *not* a MuseTalk model implementation. It approximates session hot-path timing by
emitting an optional audio-accepted marker followed by frame cadence simulation.
"""

import argparse
import json
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
p.add_argument('--cadence-profile', choices=['fixed', 'tts_bursty'], default='fixed')
args = p.parse_args()

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
time.sleep(startup_ms / 1000.0)

first_frame_ts = None
frame_timestamps = []
interval = 1.0 / max(args.fps, 0.1)
frame_payload = b'\x89PNG\r\n' + (b'0' * 65536)
for idx in range(args.num_frames):
    now_ts = time.time()
    if first_frame_ts is None:
        first_frame_ts = now_ts
    frame_timestamps.append(now_ts)
    if not args.disable_frame_write:
        (out / f'frame_{idx:05d}.png').write_bytes(frame_payload)
    time.sleep(interval)

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

if args.chunk_ms <= 80 and args.startup_chunks <= 1:
    continuity_risk_hint = 'high_boundary_churn'
elif args.chunk_ms <= 120 and args.startup_chunks <= 2:
    continuity_risk_hint = 'medium_boundary_churn'
else:
    continuity_risk_hint = 'lower_boundary_churn'

if args.cadence_profile == 'tts_bursty' and continuity_risk_hint == 'medium_boundary_churn':
    continuity_risk_hint = 'medium_plus_bursty'

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
                    'cadence_profile': args.cadence_profile,
                }
            }
        )
    )
