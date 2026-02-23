# Performance Report

**Date**: 2026-02-12
**Scope**: TASK-5 lightweight profiling pass

## Method
- In-memory synthetic web with 300 empirical beliefs + ~100 theoretical beliefs
- 5 repeats per operation, reported as min/avg/max milliseconds
- Local development environment profiling (not production hardware)

## Results

| Operation | Min (ms) | Avg (ms) | Max (ms) |
|-----------|----------|----------|----------|
| GapPredictor.find_all_gaps(max_gaps=50) | 4.78 | 8.01 | 20.49 |
| EdgeJustificationService.get_justification (4 edges batch) | 2.22 | 2.32 | 2.47 |
| CrossLayerQueryService.get_layer_statistics | 0.09 | 0.09 | 0.10 |
| CrossLayerQueryService.find_environment_outcome_beliefs | 0.02 | 0.03 | 0.04 |

## Notes
- Gap analysis time is dominated by relationship grouping and type-specific scans.
- Edge justification performance remains low-latency in this synthetic workload.
- Real-world performance will depend heavily on persistent-store load path and web size.
