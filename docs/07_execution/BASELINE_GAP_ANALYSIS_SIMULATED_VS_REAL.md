# Gap Analysis: Simulated vs Real Baseline Measurement

## Purpose
Document the current gap between:
- `simulated` harness mode (deterministic scaffold), and
- command-executed warm/cold baseline measurement.

## Warm-path truthfulness improvements in this milestone
- Warm-start first-frame latency anchor now prefers **audio accepted marker -> first speaking frame**.
- Warm-start runs can require the marker; missing marker becomes `partial`, not `ok`.
- Per-run `measurement_provenance` records exactly how each metric was measured.
- Report includes machine/environment metadata for reproducibility context.

## What still prevents true streaming-faithful measurement
1. No direct runtime event hook for `audio_accepted` in a live session transport path.
2. First-frame detection still depends on output frame file mtime, not stream egress timestamp.
3. No synchronized client/server clock in this harness, so end-to-end visible latency is out of scope.

## Why the current approach is still useful
- It improves warm-path semantic alignment without changing runtime architecture.
- It makes approximation boundaries explicit and machine-auditable in each run.
- It avoids optimization claims and focuses on baseline instrumentation quality.

## Next non-optimization step
Wire real MuseTalk runtime/session events (`audio accepted`, `first frame emitted`) into this wrapper to replace marker/file proxies while preserving report schema.
