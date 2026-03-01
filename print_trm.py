import sys
from src.services.epistemic_causal_bridge import TheoryRelativeModel

print("TheoryRelativeModel Dataclass fields:")
for field_name, field_def in TheoryRelativeModel.__dataclass_fields__.items():
    print(f"  {field_name}: {field_def.type}")
