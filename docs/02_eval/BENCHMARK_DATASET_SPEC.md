# BENCHMARK DATASET SPEC

## Purpose
Define a stable evaluation set for runtime and quality comparison.

## Dataset philosophy
The benchmark set should reflect the intended product:
- conversational avatars
- mostly frontal or near-frontal faces
- idle-loop compatible assets
- multilingual audio with emphasis on Japanese
- realistic app answer lengths

## Proposed split
### Runtime benchmark subset
Fast, repeatable, small
- 5 avatars
- 20 audio clips
- used on every PR or experiment

### Standard validation subset
Broader and still practical
- 20 avatars
- 100 utterances
- used for milestone evaluation

### Human review subset
Curated for subjective review
- 10 avatars
- 30 representative utterances
- reviewed periodically, not on every patch

## Avatar coverage
Include:
- male and female faces
- different ages
- glasses / no glasses
- light facial hair / clean-shaven
- different lighting conditions
- slight head motion
- clean idle-loop compatibility

Avoid in the first benchmark version:
- extreme profile views
- rapid camera cuts
- severe occlusion
- highly dynamic body motion
- unstable source footage

## Audio coverage
### Language distribution
- Japanese: 60%
- English: 25%
- Korean: 15%

### Style distribution
- short confirmations
- medium-length explanatory answers
- slightly emotional or emphatic segments
- calm neutral delivery

### Length distribution
- 1 to 3 seconds: 25%
- 3 to 8 seconds: 50%
- 8 to 15 seconds: 25%

## Critical benchmark annotations
Each avatar should include:
- avatar_id
- source asset type
- idle compatibility note
- bbox_shift recommendation if known
- known visual risk tags

Each audio clip should include:
- language
- duration
- speaking rate
- emotional intensity
- turn type (short / medium / long)

## Benchmark outputs per sample
For each test case record:
- cold or warm start
- first-frame latency
- avg fps
- peak VRAM
- stall count
- visual artifact flags
- reviewer note

## Human review protocol
Reviewers should score:
- responsiveness impression
- mouth plausibility
- identity consistency
- transition naturalness
- overall acceptability

## Data governance notes
- keep benchmark set versioned
- avoid mixing benchmark and training clips
- lock evaluation clips for at least one optimization cycle
- document any benchmark changes in ADRs or release notes

## Initial benchmark creation plan
1. collect 30 to 40 candidate avatars
2. filter for quality and idle-loop compatibility
3. select 20 final benchmark avatars
4. generate or collect multilingual response audio
5. tag and version all samples
6. freeze v1 benchmark
