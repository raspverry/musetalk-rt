# Human QA Review Pack: lifecycle_e2e_flagged_human_qa_pack_v1

- Scope: flagged non-production continuity/seam/response-start review
- Profiles: stable, bursty, jittery

## Scoring rubric (1-5; 5 best)
- continuity_seam_perception
- first_response_naturalness
- speaking_stability
- audio_visual_alignment_at_response_start

## Representative sample checklist
### stable
- best: run_index=10, continuity=lower_boundary_churn (policy_plus_observed_stability), jitter_ms=0.012446479413877628, latency_ms=129.17709350585938
- median: run_index=2, continuity=lower_boundary_churn (policy_plus_observed_stability), jitter_ms=0.02175228951677181, latency_ms=129.26054000854492
- worst: run_index=3, continuity=lower_boundary_churn (policy_plus_observed_stability), jitter_ms=0.053005640567417196, latency_ms=129.18615341186523

### bursty
- best: run_index=1, continuity=medium_plus_bursty (policy_threshold), jitter_ms=47.053805510587374, latency_ms=283.8099002838135
- median: run_index=9, continuity=medium_plus_bursty (policy_threshold), jitter_ms=47.074372068908495, latency_ms=283.7543487548828
- worst: run_index=8, continuity=medium_plus_bursty (policy_threshold), jitter_ms=47.10522547837405, latency_ms=283.7822437286377

### jittery
- best: run_index=2, continuity=high_boundary_churn (policy_plus_observed_instability), jitter_ms=55.31468441911423, latency_ms=283.8106155395508
- median: run_index=8, continuity=high_boundary_churn (policy_plus_observed_instability), jitter_ms=55.34400946368592, latency_ms=283.75244140625
- worst: run_index=4, continuity=high_boundary_churn (policy_plus_observed_instability), jitter_ms=56.16993441906665, latency_ms=283.6902141571045

## Reviewer notes template
- Profile:
- Representative (best/median/worst):
- continuity_seam_perception (1-5):
- first_response_naturalness (1-5):
- speaking_stability (1-5):
- audio_visual_alignment_at_response_start (1-5):
- Notes:
