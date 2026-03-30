# DATASET AND TRAINING PLAN

## Purpose
Define the eventual retraining track if runtime/productization alone is not enough.

## Strategic stance
Do not rush into retraining before Phase 1 runtime/product goals are validated. However, prepare the plan early so the team can move fast if needed.

## Why retraining might become necessary
- persistent jitter not solved by runtime methods
- identity preservation remains weak
- sync/quality trade-off cannot be solved by inference tuning alone
- target avatar domains differ from upstream training assumptions

## Training objectives
Potential objectives in priority order:
1. better identity consistency
2. lower mouth artifacts
3. improved temporal stability
4. maintain acceptable sync quality
5. preserve latency viability for product runtime

## Data sources
Potential sources:
- licensed talking-head datasets
- internally licensed avatar video assets
- synthetic / staged recordings if needed

## Data requirements
Need:
- high face visibility
- stable frame rate
- clear speech/audio alignment
- diverse but product-relevant demographics and languages
- emphasis on Japanese conversational speech

## Data pipeline stages
1. ingest raw video and rights metadata
2. deduplicate
3. frame extraction
4. face detection / alignment
5. audio sync quality screening
6. quality tagging
7. train/val/test split
8. versioned dataset release

## Annotation needs
Minimum:
- language
- speaker id / avatar id
- duration
- visual quality flags
- occlusion flags
- head motion class
- bbox / crop confidence

## Initial training experiments
- loss reweighting study
- identity-focused tuning
- temporal consistency study
- smaller/faster runtime variant exploration

## Infrastructure notes
Upstream 1.5 training is non-trivial. Estimate resource needs separately before committing to retraining as a project milestone.

## Governance
- track dataset versions explicitly
- track licenses and usage rights
- never mix benchmark clips into training data
- record training configs and model cards

## Exit criteria for training branch
A retrained model candidate is worth promoting only if it:
- beats runtime-optimized baseline on meaningful quality metrics
- does not destroy latency profile
- can be operated in product infrastructure
