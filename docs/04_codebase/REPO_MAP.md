# REPO MAP

## Purpose
Provide a practical map of the upstream MuseTalk repository and the likely productization targets.

## Important note
This map reflects the current upstream layout visible from the public repository and should be verified after cloning the exact commit you plan to fork.

## Observed top-level structure (upstream)
- `assets/`
- `configs/`
- `data/`
- `musetalk/`
- `scripts/`
- `app.py`
- `inference.sh`
- `train.py`
- `requirements.txt`
- weight download scripts and entrypoint helpers

## Likely role of major areas
### `configs/`
Configuration files for inference and training.
Expected to contain:
- normal inference config
- realtime inference config
- training preprocess / train configs

### `musetalk/`
Core library code.
Likely contains:
- model code
- utilities
- pipeline support modules

### `scripts/`
Operational entry points.
Upstream docs indicate:
- `scripts.inference`
- `scripts.realtime_inference`
- `scripts.preprocess`

This directory is likely where product hot-path extraction starts.

### `app.py`
Gradio-style demo entry point.
Useful for understanding practical runtime wiring, but not a clean product backend as-is.

### `train.py`
Training entry point.
Not Phase 1 critical, but important for later research and retraining work.

### `inference.sh`
Convenience launcher exposing normal vs realtime paths.
Useful for mapping current operational assumptions.

## Productization hotspots
### Highest-value inspect-first files
1. `scripts/realtime_inference.py`
2. `scripts/inference.py`
3. avatar prep related helper modules
4. frame save / ffmpeg interaction points
5. audio feature extraction path
6. config handling path

## Likely code smells to look for
- file-based intermediate artifacts in hot path
- mixed concerns between offline and real-time logic
- global state that resists sessionization
- hidden dependency on local folders
- implicit assumptions about ffmpeg/file export
- single-script orchestration instead of reusable runtime classes

## Proposed future codebase shape
### Keep
- model weights and core model components
- preprocess logic that is still valid
- core inference math

### Extract / wrap
- session runtime
- cache manager
- streaming output interface
- metrics instrumentation
- benchmark runner

### De-emphasize
- demo-specific UI code
- batch/offline export assumptions in product path

## Initial repo analysis checklist
- map every file touched in realtime path
- identify cold vs hot functions
- identify disk I/O in hot path
- identify ffmpeg coupling
- identify reusable prep outputs
- identify exportable/compile-friendly modules

## References
Upstream repository root visible here:
https://github.com/TMElyralab/MuseTalk
