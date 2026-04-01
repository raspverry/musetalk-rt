# Reviewer Handoff (Immediate Use)

Use this when you are a reviewer starting today.

## 1) Open the QA pack
- File: `benchmarks/baseline/reports/lifecycle_e2e_flagged_human_qa_pack_v1.md`
- Review order: **stable → bursty → jittery**, and inside each profile **best → median → worst**.

## 2) Score every sample (1-5)
Dimensions:
- continuity_seam_perception
- first_response_naturalness
- speaking_stability
- audio_visual_alignment_at_response_start

## 3) Enter scores in the scorecard template
- File: `benchmarks/baseline/reports/lifecycle_e2e_flagged_human_qa_pack_v1_scorecard_template.json`
- Fill `reviewer_id` and all score fields.
- Keep `profile`, `representative`, `run_index` unchanged.

## 4) Save and hand off
After saving your filled scorecard JSON, notify the maintainer to run the decision evaluator.

## Notes
- This is flagged non-production validation.
- If you see severe visual breaks, score honestly (including low values).
