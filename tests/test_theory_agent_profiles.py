"""
Tests for T7.6 Theory Agent Profiles.

Verifies:
- All 10 T1 profiles + biophilia load without error
- Each profile has all 11 required constants
- TheoryAgentCouncil loads all agents
- Each agent can evaluate a sample claim
"""

import importlib.util
import sys
import pytest
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.theories.theory_agent_council import TheoryAgent, TheoryAgentCouncil

PROFILES_DIR = Path(__file__).parent.parent / "src" / "theories" / "profiles"

# All T1 profile files that should exist
T1_PROFILES = [
    "pp_profile.py",
    "sn_profile.py",
    "dp_profile.py",
    "dt_profile.py",
    "nm_profile.py",
    "ic_profile.py",
    "ms_profile.py",
    "ec_profile.py",
    "cb_profile.py",
    "msi_profile.py",
]

# Required constants in every profile module
REQUIRED_CONSTANTS = [
    "THEORY_ID",
    "THEORY_NAME",
    "CORE_MECHANISM",
    "EXPLAINS",
    "DOES_NOT_EXPLAIN",
    "STIMULUS_INCLUDES",
    "STIMULUS_EXCLUDES",
    "STIMULUS_EDGE_CASES",
    "PREDICTED_OUTCOMES",
    "NOT_PREDICTED_OUTCOMES",
    "MATCHING_PROMPT",
    "FEW_SHOT_EXAMPLES",
]


def _load_module(filename: str):
    """Load a profile module by filename."""
    filepath = PROFILES_DIR / filename
    spec = importlib.util.spec_from_file_location(filepath.stem, filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestProfileFilesExist:
    """All 10 T1 profile files should exist."""

    @pytest.mark.parametrize("profile_file", T1_PROFILES)
    def test_profile_file_exists(self, profile_file):
        path = PROFILES_DIR / profile_file
        assert path.exists(), f"Missing profile: {path}"


class TestProfileContractCompliance:
    """Each profile must export all 11 required constants."""

    @pytest.mark.parametrize("profile_file", T1_PROFILES)
    def test_has_all_required_constants(self, profile_file):
        module = _load_module(profile_file)
        missing = [c for c in REQUIRED_CONSTANTS if not hasattr(module, c)]
        assert not missing, f"{profile_file} missing constants: {missing}"

    @pytest.mark.parametrize("profile_file", T1_PROFILES)
    def test_theory_id_is_string(self, profile_file):
        module = _load_module(profile_file)
        assert isinstance(module.THEORY_ID, str)
        assert module.THEORY_ID.startswith("framework:")

    @pytest.mark.parametrize("profile_file", T1_PROFILES)
    def test_lists_are_nonempty(self, profile_file):
        module = _load_module(profile_file)
        for attr in ["EXPLAINS", "DOES_NOT_EXPLAIN", "STIMULUS_INCLUDES",
                      "PREDICTED_OUTCOMES", "NOT_PREDICTED_OUTCOMES",
                      "FEW_SHOT_EXAMPLES"]:
            items = getattr(module, attr)
            assert isinstance(items, list), f"{profile_file}.{attr} should be list"
            assert len(items) > 0, f"{profile_file}.{attr} should not be empty"

    @pytest.mark.parametrize("profile_file", T1_PROFILES)
    def test_few_shot_examples_have_required_keys(self, profile_file):
        module = _load_module(profile_file)
        required_keys = {"claim", "lhs", "rhs", "polarity", "judgment", "reasoning"}
        for i, example in enumerate(module.FEW_SHOT_EXAMPLES):
            missing = required_keys - set(example.keys())
            assert not missing, f"{profile_file} example {i} missing keys: {missing}"

    @pytest.mark.parametrize("profile_file", T1_PROFILES)
    def test_matching_prompt_has_placeholders(self, profile_file):
        module = _load_module(profile_file)
        prompt = module.MATCHING_PROMPT
        assert "{claim}" in prompt, f"{profile_file} MATCHING_PROMPT missing {{claim}}"
        assert "{paper_id}" in prompt, f"{profile_file} MATCHING_PROMPT missing {{paper_id}}"


class TestTheoryAgentInstantiation:
    """Each profile should instantiate a valid TheoryAgent."""

    @pytest.mark.parametrize("profile_file", T1_PROFILES)
    def test_agent_creation(self, profile_file):
        module = _load_module(profile_file)
        agent = TheoryAgent(module)
        assert agent.theory_id == module.THEORY_ID
        assert agent.theory_name == module.THEORY_NAME


class TestTheoryAgentCouncilLoading:
    """TheoryAgentCouncil should load all profiles from the directory."""

    def test_load_all_agents(self):
        council = TheoryAgentCouncil()
        n_loaded = council.load_agents_from_profiles(str(PROFILES_DIR))
        # 10 T1 + 1 biophilia = 11
        assert n_loaded >= 11, f"Expected ≥11 agents, got {n_loaded}"

    def test_all_t1_frameworks_represented(self):
        council = TheoryAgentCouncil()
        council.load_agents_from_profiles(str(PROFILES_DIR))
        loaded_ids = {a.theory_id for a in council.agents.values()}
        expected_ids = {_load_module(pf).THEORY_ID for pf in T1_PROFILES}
        missing = expected_ids - loaded_ids
        assert not missing, f"Missing T1 frameworks in council: {missing}"

    def test_evaluate_sample_claim(self):
        council = TheoryAgentCouncil()
        council.load_agents_from_profiles(str(PROFILES_DIR))
        verdict = council.evaluate_claim(
            claim_id="test:claim:001",
            claim_statement="Indoor plants improve office worker wellbeing",
            lhs_vars=["env.indoor_plants"],
            rhs_var="aff.wellbeing",
            polarity="positive",
        )
        assert verdict is not None
        assert len(verdict.agent_verdicts) >= 11
        # Biophilia agent should confirm this
        bio_verdict = next(
            (v for v in verdict.agent_verdicts if "biophilia" in v.theory_id),
            None
        )
        assert bio_verdict is not None
        assert bio_verdict.judgment.value == "confirms"
