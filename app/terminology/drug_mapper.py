class DrugMapper:
    def __init__(self):
        self._mappings = {
            "pcm": "Paracetamol",
            "paracetmol": "Paracetamol",
            "acetaminophen": "Paracetamol",
            "metformin hcl": "Metformin"
        }

    def map_drug(self, token: str) -> str:
        clean_token = token.lower().strip()
        return self._mappings.get(clean_token, token)
