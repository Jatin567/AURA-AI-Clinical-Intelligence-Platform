# Retrieval Engine

This module serves as the Enterprise Hybrid Retrieval Engine for the AURA platform. It is strictly deterministic and provides the infrastructure for Multi-Agent Workflows, RAG, and LLM Tool Calling.

## Architecture

```mermaid
graph TD
    A[SearchRequest] --> B(RetrievalEngine)
    B -->|Query Expansion| C(QueryExpander)
    B -->|Entity Linking| D(EntityLinker)
    B --> E(HybridSearchEngine)
    
    E --> F(SemanticSearchEngine)
    E --> G(KeywordSearchEngine)
    E --> H(GraphSearchEngine)
    
    F --> I[(FAISS Vector Store)]
    G --> J[(BM25 Index)]
    H --> K[(Knowledge Graph)]
    
    E --> L(RankingEngine)
    L --> M(CrossEncoderReranker)
    M --> N(ContextCompressor)
    
    N --> O[EvidencePackage]
```
