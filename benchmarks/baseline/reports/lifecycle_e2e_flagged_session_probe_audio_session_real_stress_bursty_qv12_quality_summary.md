# Flagged E2E Quality Validation Summary (lifecycle_e2e_flagged_session_probe_audio_session_real_stress_bursty_qv12)

- Runs: 12
- Fallback runs: 0 (rate=0.0)
- Lifecycle stage errors: 0
- Warn-only canary recommendation: safe_to_try_warn_only_canary

## Stage signal_kind counts
- **session_start**: {'real_wired_session_start_observation': 12}
- **avatar_ready_or_warm_assumed**: {'real_wired_avatar_probe': 12}
- **audio_accepted**: {'real_wired_audio_accepted_observation': 12}
- **first_speaking_frame_signal**: {'real_wired_first_frame_observation': 12}

## Observations
- No lifecycle fallback or stage errors observed in this quality validation pass.
- TTS cadence sensitivity sampled only for cadence profile: tts_bursty.

## Limitations
- Proxy/fixture approximation cannot replace human MOS-style naturalness review.
- No network/mobile jitter injection in this pass; cadence sensitivity is approximation-only.
- Seam/continuity and first-response naturalness conclusions are telemetry-guided, not perceptual ground truth.

## Next validation under jitter
- Inject bursty + delayed chunk arrival with random jitter envelopes (e.g. 20-200ms) and rerun stage/error tracking.
- Run mixed cadence profiles (fixed, tts_bursty, jittery) while checking seam artifacts and first response stability.
- Add packet-loss/drop simulation to validate fallback transparency and quality degradation boundaries.
