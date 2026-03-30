# MODEL OPTIMIZATION PLAYBOOK

## Purpose
List practical optimization avenues in likely ROI order.

## Optimization philosophy
Optimize the product path in the order that best improves perceived responsiveness:
1. remove avoidable overhead
2. improve runtime path clarity
3. reduce memory and transport cost
4. only then pursue heavier model-level changes

## Tier 1 — high-ROI, low-risk
### A. Remove file-based intermediates
Expected benefit:
- lower first-frame latency
- lower total overhead

### B. Warm cache reuse
Expected benefit:
- much lower warm-start latency

### C. Precision tuning
Modes to evaluate:
- fp32
- fp16
- bf16 if practical
Expected benefit:
- lower VRAM
- possible speedup

### D. Batch and chunk sizing
Expected benefit:
- better time-to-first-speaking
- better stall resistance

## Tier 2 — medium-ROI, medium-risk
### E. `torch.compile`
Evaluate:
- compile overhead
- hot-path speedup
- compatibility issues

### F. ONNX export feasibility
Focus on:
- export coverage
- parity
- operational complexity

### G. TensorRT feasibility
Only after export coverage looks promising.

## Tier 3 — higher-risk research
### H. Quantization
Potential targets:
- selected modules
- runtime-specific variants
- not a default first move

### I. Audio encoder simplification
Potential gain:
- latency and VRAM
Potential risk:
- sync quality loss

### J. Lightweight temporal smoother
Potential gain:
- less jitter
Potential risk:
- added latency and blur

## Decision checklist for each optimization
- does it improve first-frame latency?
- does it improve steady-state fps?
- does it reduce memory?
- does it preserve visual stability?
- does it make deployment easier or harder?
- can it be rolled back cleanly?

## Default recommendation order
1. cache and runtime path cleanup
2. remove disk writes
3. precision matrix
4. chunking improvements
5. compile tests
6. export feasibility
7. temporal smoother
8. quantization
