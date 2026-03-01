import sys
from src.services.epistemic_causal_bridge import EpistemicCausalBridge, TheoryRelativeModel, StructuralEquation
from src.services.web_of_belief import WebOfBelief, Belief, EpistemicLevel

class MockWeb:
    def __init__(self):
        self.beliefs = { "b1": Belief(belief_id="b1", content="Nat", level=EpistemicLevel.EMPIRICAL) }
        self.constraints = []
        self.edges = []
    def get_entrenchment(self, bid): return 0.5

web = MockWeb()
bridge = EpistemicCausalBridge(web)

mock_model = TheoryRelativeModel("ART", 0.9, {
    "env.nature": StructuralEquation("eq1", "env.nature", [], "linear", {}, ["b1"]),
    "out.restoration": StructuralEquation("eq2", "out.restoration", ["env.nature"], "linear", {"beta_env.nature": 0.8}, ["b1"])
})
class DummyMulti:
    def __init__(self, tm):
        self.theory_models = tm
        self.variables = {"env.nature": None, "out.restoration": None}

bridge.multi_theory_model = DummyMulti({"ART": mock_model})

intervention = {"env.nature": 1.0}
outcome = "out.restoration"

# Simulate just Step 1
query = bridge._create_query(intervention, outcome, None, None, None, None)
theory_results = {}
for theory_id, model in bridge.multi_theory_model.theory_models.items():
    print(f"Theory ID: {theory_id}, Model type: {type(model)}")
    tcf = bridge._compute_theory_counterfactual(query, model)
    theory_results[theory_id] = tcf
    print(f"Result type: {type(tcf)}, theory_credence type: {type(tcf.theory_credence)}")
