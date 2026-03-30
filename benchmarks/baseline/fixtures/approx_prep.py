#!/usr/bin/env python3
"""Approximate cold-path prep command for harness wiring checks."""
import argparse
import json
import time
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('--sleep-ms', type=float, default=1200.0)
p.add_argument('--cache-flag', required=True)
args = p.parse_args()

time.sleep(args.sleep_ms / 1000.0)
Path(args.cache_flag).parent.mkdir(parents=True, exist_ok=True)
Path(args.cache_flag).write_text('ready')
print(json.dumps({'prep': 'ok', 'cache_flag': args.cache_flag}))
