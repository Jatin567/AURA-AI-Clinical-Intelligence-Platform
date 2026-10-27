import pytest
from app.orchestrator.prompt_layers import SystemPromptBuilder, FinalPromptAssembler
from app.orchestrator.prompt_context import PromptContext

def test_prompt_layers():
    context = PromptContext(
        patient_profile={"name": "John Doe"},
        timeline=[],
        workspace=[],
        memory={},
        retrieved_evidence=None,
        clinical_recommendations=[],
        missing_information=[],
        drug_safety=[],
        current_message="Hi"
    )
    
    builder = SystemPromptBuilder()
    assert "expert AI medical assistant" in builder.build(context)
    
    assembler = FinalPromptAssembler()
    final_prompt = assembler.assemble(context)
    assert "System:" in final_prompt
    assert "John Doe" in final_prompt
