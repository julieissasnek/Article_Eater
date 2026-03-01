import sys
from src.services.epistemic_causal_bridge import TheoryCounterfactual

print("TheoryCounterfactual Dataclass fields:")
for field_name, field_def in TheoryCounterfactual.__dataclass_fields__.items():
    print(f"  {field_name}: {field_def.type}")
