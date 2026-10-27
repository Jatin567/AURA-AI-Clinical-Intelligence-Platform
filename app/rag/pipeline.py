from typing import Dict, Any

class RAGPipeline:
    def __init__(self, retrieval_executor, context_manager, prompt_builder, claim_validator, response_validator, citation_manager, metrics, confidence_fusion):
        self.retrieval_executor = retrieval_executor
        self.context_manager = context_manager
        self.prompt_builder = prompt_builder
        self.claim_validator = claim_validator
        self.response_validator = response_validator
        self.citation_manager = citation_manager
        self.metrics = metrics
        self.confidence_fusion = confidence_fusion

    async def execute_stream(self, session, llm_provider):
        self.metrics.start_timer("total_rag_time")
        self.metrics.record("intent", getattr(session, "intent", "unknown"))
        self.metrics.record("workflow", "rag")
        self.metrics.record("provider", getattr(llm_provider, "provider_name", "unknown"))
        
        # 1. Retrieval Decision & Execution
        self.metrics.start_timer("retrieval_time")
        evidence = self.retrieval_executor.execute(session.intent, session.query)
        self.metrics.stop_timer("retrieval_time")
        
        self.metrics.record("retrievals_count", len(evidence) if evidence else 0)

        # Zero-document check
        if not evidence:
            self.metrics.stop_timer("total_rag_time")
            import logging
            logging.getLogger(__name__).warning(f"Zero-document retrieval for intent {session.intent}. Emitting NO_EVIDENCE.")
            yield {
                "event": "NO_EVIDENCE",
                "message": "No relevant medical evidence found in knowledge base."
            }
            return
        
        # 2. Context Aggregation
        context = self.context_manager.build_context(session, evidence)
        
        # 3. Prompt Construction
        self.metrics.start_timer("prompt_build_time")
        prompt = self.prompt_builder.build(context)
        self.metrics.stop_timer("prompt_build_time")
        
        # 4. LLM Generation (Streaming)
        self.metrics.start_timer("llm_time")
        full_response_text = ""
        async for chunk in llm_provider.generate_stream(prompt):
            full_response_text += chunk
            yield {"event": "TEXT_CHUNK", "text": chunk}
        self.metrics.stop_timer("llm_time")
        
        # Assume ~4 chars per token for a rough estimate if provider doesn't stream token counts
        self.metrics.record("tokens", len(full_response_text) // 4)
        
        # 5. Claim Validation (On completed text)
        self.metrics.start_timer("safety_time")
        validated_response = self.claim_validator.validate(full_response_text, evidence)
        self.metrics.stop_timer("safety_time")
        
        # 6. Response Quality & Telemetry
        quality_score = self.response_validator.score(validated_response)
        overall_confidence = self.confidence_fusion.fuse(evidence, validated_response)
        self.metrics.record("confidence", overall_confidence)
        
        self.metrics.stop_timer("total_rag_time")
        
        final_metrics = self.metrics.get_metrics()
        import logging
        logging.getLogger(__name__).info(f"RAG Pipeline Executed: {final_metrics}")
        
        yield {
            "event": "RAG_COMPLETE",
            "response": validated_response,
            "quality_score": quality_score,
            "confidence": overall_confidence,
            "metrics": final_metrics,
            "evidence": evidence
        }
