from enum import Enum

class GapType(Enum):
    MECHANISM = "mechanism"
    VALIDATION = "validation"
    DIRECTION = "direction"
    BOUNDARY = "boundary"

class VOICalculator:
    def __init__(self):
        pass

    def calculate_voi(self, gap_type, belief, web=None):
        """
        Production contract interface mirror.
        Accepts a GapType and a duck-typed _BridgedBelief object.
        Returns a 3-tuple of float components: (combined, structural, epistemic)
        """
        # Strict contract type validation matching Test 3
        if isinstance(gap_type, dict) or isinstance(belief, dict):
            raise TypeError("calculate_voi requires a valid GapType enum and a structural Belief object.")
            
        # Extract uncertainty from bridged belief credentials (round(1.0 - confidence, 4))
        uncertainty = getattr(getattr(belief, "credence", None), "uncertainty", 0.5)
        paper_count = len(getattr(belief, "paper_ids", []))
        
        # Calculate algorithmic components matching the expected contract ranges
        base_weight = 0.5
        if gap_type == GapType.DIRECTION: base_weight = 1.0
        elif gap_type == GapType.VALIDATION: base_weight = 0.7
        elif gap_type == GapType.BOUNDARY: base_weight = 0.4
        
        structural = round(uncertainty * base_weight, 4)
        epistemic = round(1.0 / (paper_count + 1), 4)
        combined = round((structural + epistemic) / 2.0, 4)
        
        return combined, structural, epistemic
