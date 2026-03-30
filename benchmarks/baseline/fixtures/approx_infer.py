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
args = p.parse_args()

out = Path(args.frames_dir)
out.mkdir(parents=True, exist_ok=True)

time.sleep(args.audio_accept_ms / 1000.0)
audio_accepted_ts = time.time()
if args.audio_accepted_marker:
    marker = Path(args.audio_accepted_marker)
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text('audio_accepted')

chunk_startup_ms = 0.0
if args.startup_chunks > 0 and args.chunk_ms > 0:
    per_chunk_ms = args.chunk_ms + max(args.chunk_overhead_ms, 0.0)
    chunk_startup_ms = args.startup_chunks * per_chunk_ms

startup_ms = max(args.post_accept_startup_ms, chunk_startup_ms)
time.sleep(startup_ms / 1000.0)

first_frame_ts = None
interval = 1.0 / max(args.fps, 0.1)
frame_payload = b'\x89PNG\r\n' + (b'0' * 65536)
for idx in range(args.num_frames):
    now_ts = time.time()
    if first_frame_ts is None:
        first_frame_ts = now_ts
    if not args.disable_frame_write:
        (out / f'frame_{idx:05d}.png').write_bytes(frame_payload)
    time.sleep(interval)

last_frame_ts = time.time()
steady_state_fps = None
if first_frame_ts is not None and last_frame_ts > first_frame_ts and args.num_frames >= 2:
    steady_state_fps = (args.num_frames - 1) / (last_frame_ts - first_frame_ts)

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
                }
            }
        )
    )
