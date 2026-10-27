import math


class ConfidenceEngine:
    """
    Mathematical normalization engine that derives confidence scores.
    Guarantees all confidence values remain strictly bounded within [0.0, 1.0].
    
    Derivation Methodology:
    -----------------------
    Given:
      - S_base  : Raw symptom matching score derived from primary and secondary symptoms [0.0, 1.0].
      - R_mod   : Cumulative risk factor modifier derived from patient risk profile [0.0, 0.6].
      - P_conf  : Penalty factor for contradicting symptoms present [-0.2 per symptom].
    
    1. Composite Score:
       S_composite = S_base + R_mod - P_conf
       
    2. Strict Zero Constraint:
       If S_base == 0.0 (no supporting symptoms present), Confidence = 0.0.
       This prevents risk factors alone from producing false-positive condition matches.
       
    3. Normalization & Bounded Clamping:
       Confidence = min(1.0, max(0.0, S_composite))
    """

    def calculate_confidence(self, base_score: float, risk_modifier: float) -> float:
        """
        Calculates a normalized confidence score bounded strictly between 0.0 and 1.0.
        
        Args:
            base_score (float): Raw symptom match score.
            risk_modifier (float): Total additive risk weight from risk factors.
            
        Returns:
            float: Normalized confidence score in range [0.0, 1.0].
        """
        # Rule: No supporting symptoms -> Confidence = 0.0
        if base_score <= 0.0:
            return 0.0

        # Composite additive formulation
        raw_composite = base_score + (risk_modifier * 0.4)  # Scale risk modifier to prevent over-domination

        # Strict clamping between 0.0 and 1.0
        clamped = max(0.0, min(1.0, raw_composite))

        return round(clamped, 3)
