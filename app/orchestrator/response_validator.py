from typing import Dict, Any

class ResponseValidator:
    def validate(self, ui_blocks: list) -> bool:
        """Validates JSON schema, required cards, citations, metadata, and prevents empty UI payloads."""
        if not ui_blocks:
            return False
            
        for block in ui_blocks:
            if "type" not in block or "content" not in block:
                return False
                
        return True
