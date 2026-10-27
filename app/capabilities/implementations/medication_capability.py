from typing import Dict, Any
import asyncio
from app.capabilities.core.interfaces import ICapability, CapabilityMetadata

class MedicationCapability(ICapability):
    def get_metadata(self) -> CapabilityMetadata:
        return CapabilityMetadata(
            name="medication",
            description="Checks drug interactions",
            input_schema={"type": "object", "properties": {"drugs": {"type": "array"}}},
            output_schema={"type": "object", "properties": {"interactions": {"type": "array"}}},
            requires_retrieval=True
        )

    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        # Stub logic
        await asyncio.sleep(0.1)
        return {"interactions": []}
