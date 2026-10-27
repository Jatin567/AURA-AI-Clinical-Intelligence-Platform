import pytest
from app.rag.claim_validation.validators import ClaimExtractor, EvidenceVerifier, CitationValidator, ConfidenceAdjuster
from app.rag.claim_validation.coordinator import ClaimValidatorCoordinator

def test_claim_extractor():
    extractor = ClaimExtractor()
    claims = extractor.extract("Patient has fever. Also unsupported claim.")
    assert len(claims) == 2

def test_claim_validator_coordinator():
    coord = ClaimValidatorCoordinator()
    response = "Patient has fever. Also unsupported claim."
    safe_response = coord.validate(response, evidence=None)
    # The verifier rejects "unsupported"
    assert "unsupported" not in safe_response
    assert "Patient has fever" in safe_response
