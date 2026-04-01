# Flagged E2E Reliability Summary (lifecycle_e2e_flagged_session_probe_avatar_real_r30)

- Total runs: 30
- Runs with fallback: 0
- Fallback rate: 0.0

## Stage signal mix
- **session_start**: {'proxy_command': 30} | errors=0
- **avatar_ready_or_warm_assumed**: {'real_wired_avatar_probe': 30} | errors=0
- **audio_accepted**: {'proxy_command': 30} | errors=0
- **first_speaking_frame_signal**: {'real_wired_first_frame_observation': 30} | errors=0

## Recommendation
- Eligible to trial stricter fallback (warn-only fallback) in canary flagged runs.
- Next stage to deepen: avatar_ready_or_warm_assumed

## Lightweight QA checklist
- Verify response-start feels prompt (first speaking frame timing within expected envelope).
- Spot-check seam/continuity artifacts around response onset.
- Confirm no obvious audio/video desync at first speaking frame.
- Record whether fallback stage was user-visible in perceived startup quality.

## Before vs after comparison
- Before fallback rate: 0.0
- After fallback rate: 0.0
- Delta fallback rate: 0.0

### Stage-by-stage signal_kind mix
- **audio_accepted**: before={'proxy_command': 8} | after={'proxy_command': 30}
- **avatar_ready_or_warm_assumed**: before={'real_wired_avatar_probe': 8} | after={'real_wired_avatar_probe': 30}
- **first_speaking_frame_signal**: before={'real_wired_first_frame_observation': 8} | after={'real_wired_first_frame_observation': 30}
- **session_start**: before={'proxy_command': 8} | after={'proxy_command': 30}
