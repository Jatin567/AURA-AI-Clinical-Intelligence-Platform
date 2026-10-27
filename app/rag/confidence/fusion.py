class ConfidenceFusionEngine:
    def fuse(self, evidence, validated_response: str) -> float:
        # Stub logic to merge Confidence across retrieval, rules, safety
        if "unsupported" in validated_response.lower():
            return 0.1
        return 0.92
