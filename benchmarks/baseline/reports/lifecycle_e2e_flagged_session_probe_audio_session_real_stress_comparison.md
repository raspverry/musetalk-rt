# Stable vs Stress Continuity Comparison

## baseline
- Continuity hints: {'lower_boundary_churn': 12}
- Continuity basis: {'policy_plus_observed_stability': 12}
- Frame jitter p95: 0.05035846094470439
- Fallback rate: 0.0
- Lifecycle stage errors: 0

## stress_bursty
- Continuity hints: {'medium_plus_bursty': 12}
- Continuity basis: {'policy_threshold': 12}
- Frame jitter p95: 47.092671753181676
- Fallback rate: 0.0
- Lifecycle stage errors: 0

## stress_jittery
- Continuity hints: {'high_boundary_churn': 12}
- Continuity basis: {'policy_plus_observed_instability': 12}
- Frame jitter p95: 55.73499584798925
- Fallback rate: 0.0
- Lifecycle stage errors: 0
