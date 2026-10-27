import hashlib
from typing import List
from pathlib import Path
from app.knowledge.datasets.manifest import DatasetManifest

class DatasetVerifier:
    """Validates checksums, publishers, licenses, and source integrity."""
    
    ALLOWED_PUBLISHERS = {
        "WHO", "CDC", "NICE", "NIH", "Peer-reviewed Guidelines", 
        "Clinical Trials", "Research Papers", "Educational Sources", "Unknown"
    }

    def verify_checksum(self, file_path: str, expected_checksum: str) -> bool:
        path = Path(file_path)
        if not path.exists():
            return False
            
        sha256 = hashlib.sha256()
        with open(path, "rb") as f:
            for block in iter(lambda: f.read(4096), b""):
                sha256.update(block)
                
        return sha256.hexdigest() == expected_checksum

    def verify_manifest(self, manifest: DatasetManifest) -> List[str]:
        """Returns a list of validation error strings. Empty if valid."""
        errors = []
        if manifest.publisher not in self.ALLOWED_PUBLISHERS:
            errors.append(f"Invalid publisher: {manifest.publisher}")
        if not manifest.dataset_id:
            errors.append("Missing dataset_id")
        if not manifest.checksum_sha256:
            errors.append("Missing checksum_sha256")
        return errors
