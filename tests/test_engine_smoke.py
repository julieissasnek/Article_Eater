import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_offline_pipeline_smoke_runs():
    """The offline pipeline smoke test should complete without errors.

    This indirectly tests:
    - Agent_Finder, Agent_Aggregator, Agent_Linker
    - JSONL graph service
    - Confidence calibrator
    """
    from scripts import offline_pipeline_smoke  # type: ignore

    offline_pipeline_smoke.main()
