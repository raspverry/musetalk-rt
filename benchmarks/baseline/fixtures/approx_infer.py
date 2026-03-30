#!/usr/bin/env python3
"""Approximate hot-path frame emitter when real streaming integration is unavailable.

This is *not* a MuseTalk model implementation. It only approximates session hot-path timing by
creating frame files at a fixed cadence so the benchmark harness path can be validated end-to-end.
"""

import argparse
import time
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('--frames-dir', required=True)
p.add_argument('--startup-ms', type=float, default=500.0)
p.add_argument('--fps', type=float, default=24.0)
p.add_argument('--num-frames', type=int, default=48)
args = p.parse_args()

out = Path(args.frames_dir)
out.mkdir(parents=True, exist_ok=True)

time.sleep(args.startup_ms / 1000.0)
interval = 1.0 / max(args.fps, 0.1)
for idx in range(args.num_frames):
    (out / f'frame_{idx:05d}.png').write_bytes(b'\x89PNG\r\n')
    time.sleep(interval)
