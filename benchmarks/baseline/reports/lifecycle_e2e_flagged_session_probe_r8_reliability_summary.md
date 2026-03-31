# Flagged E2E Reliability Summary (lifecycle_e2e_flagged_session_probe_r8)

- Total runs: 8
- Runs with fallback: 8
- Fallback rate: 1.0

## Stage signal mix
- **session_start**: {'proxy_command': 8} | errors=0
- **avatar_ready_or_warm_assumed**: {'proxy_fallback_command': 8} | errors=0
- **audio_accepted**: {'proxy_command': 8} | errors=0
- **first_speaking_frame_signal**: {'real_wired_first_frame_observation': 8} | errors=0

## Recommendation
- Do not tighten yet. Keep fallback permissive until >=30 flagged runs with fallback_rate < 0.10 and zero lifecycle stage errors.
- Next stage to deepen: avatar_ready_or_warm_assumed

## Lightweight QA checklist
- Verify response-start feels prompt (first speaking frame timing within expected envelope).
- Spot-check seam/continuity artifacts around response onset.
- Confirm no obvious audio/video desync at first speaking frame.
- Record whether fallback stage was user-visible in perceived startup quality.
