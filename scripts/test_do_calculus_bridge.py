import json
from pathlib import Path
from src.services.epistemic_causal_bridge import EpistemicCausalBridge, ContrastClass, PopulationContext, ConditionSpec, ContrastType, CounterfactualQuery
from src.services.web_of_belief import WebOfBelief, Belief, EpistemicLevel

# 1. Create a minimal fake WebOfBelief to test the counterfactual logic
class MockWeb:
    def __init__(self):
        self.beliefs = {
            "b1": Belief(belief_id="b1", content="Nature exposure restores attention", level=EpistemicLevel.EMPIRICAL)
        }
        self.constraints = []
        self.edges = []
    def get_entrenchment(self, bid): return 0.5
    
web = MockWeb()
bridge = EpistemicCausalBridge(web)

# 2. Add some fake nodes/edges into the mock WebOfBelief
from src.services.epistemic_causal_bridge import TheoryRelativeModel, StructuralEquation

mock_model = TheoryRelativeModel("m1", "ART", 0.9, variables={}, equations={
    "env.nature": StructuralEquation("eq1", "env.nature", [], "linear", {}, ["b1"]),
    "out.restoration": StructuralEquation("eq2", "out.restoration", ["env.nature"], "linear", {"beta_env.nature": 0.8}, ["b1"])
}, edges=[("env.nature", "out.restoration")])

class DummyMulti:
    def __init__(self, tm):
        self.theory_models = tm
        self.variables = {"env.nature": None, "out.restoration": None}
bridge.multi_theory_model = DummyMulti({"ART": mock_model})

# Formulate the do() query
intervention = {"env.nature": 1.0}
outcome = "out.restoration"

print(f"Executing counterfactual query: do({intervention}) -> {outcome}")
result = bridge.counterfactual(intervention=intervention, outcome=outcome)

print("\n==== RESULT ====")
print(f"Point estimate: {result.point_estimate}")
print(f"Confidence Interval: {result.confidence_interval}")
print(f"Quality: {result.epistemic_quality}")
print(f"Warnings: {result.warnings}")
for cid, t_res in result.by_theory.items():
    print(f"[{cid}] Est: {t_res.estimate:.3f} | CI: {t_res.confidence_interval[0]:.3f} to {t_res.confidence_interval[1]:.3f}")
    print(f"      Mechanism Path: {t_res.mechanism_path}")
