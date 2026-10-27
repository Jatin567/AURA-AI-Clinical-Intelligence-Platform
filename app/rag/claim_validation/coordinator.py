from typing import Dict, Any
from app.rag.claim_validation.validators import ClaimExtractor, EvidenceVerifier, CitationValidator, ConfidenceAdjuster

class ClaimValidatorCoordinator:
    def __init__(self):
        self.extractor = ClaimExtractor()
        self.verifier = EvidenceVerifier()
        self.citation_validator = CitationValidator()
        self.confidence_adjuster = ConfidenceAdjuster()

    def validate(self, response: str, evidence: Any) -> str:
        claims = self.extractor.extract(response)
        
        valid_claims = []
        validation_results = []
        
        for claim in claims:
            is_valid = self.verifier.verify(claim, evidence)
            has_citation = self.citation_validator.validate(claim, evidence)
            
            success = is_valid and has_citation
            validation_results.append(success)
            
            if success:
                valid_claims.append(claim)
                
        # Reconstruct response securely omitting invalid claims
        safe_response = ". ".join(valid_claims)
        if safe_response:
            safe_response += "."
            
        return safe_response
