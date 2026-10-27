from app.terminology.drug_mapper import DrugMapper

class MedicalTerminologyNormalizer:
    def __init__(self):
        self.drug_mapper = DrugMapper()

    def normalize(self, text: str) -> str:
        # Simple token replacement logic for demonstration
        tokens = text.split()
        normalized_tokens = [self.drug_mapper.map_drug(token) for token in tokens]
        return " ".join(normalized_tokens)
