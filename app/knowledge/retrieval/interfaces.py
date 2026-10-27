from abc import ABC, abstractmethod
from typing import List, Dict, Any
from app.knowledge.retrieval.models import SearchRequest, SearchResult, EvidencePackage

class SearchEngine(ABC):
    @abstractmethod
    def search(self, request: SearchRequest) -> List[SearchResult]:
        pass

class RetrievalEngine(ABC):
    @abstractmethod
    def retrieve(self, request: SearchRequest) -> EvidencePackage:
        pass

class RankingEngine(ABC):
    @abstractmethod
    def rank(self, results: List[SearchResult]) -> List[SearchResult]:
        pass

class ContextCompressor(ABC):
    @abstractmethod
    def compress(self, results: List[SearchResult]) -> str:
        pass

class CitationBuilder(ABC):
    @abstractmethod
    def build(self, metadata: Dict[str, Any]) -> str:
        pass

class QueryExpansionEngine(ABC):
    @abstractmethod
    def expand(self, query: str) -> List[str]:
        pass

class EntityLinker(ABC):
    @abstractmethod
    def link(self, text: str) -> List[str]:
        pass

class CrossEncoderReranker(ABC):
    @abstractmethod
    def rerank(self, query: str, results: List[SearchResult]) -> List[SearchResult]:
        pass

class KnowledgeGraphSearcher(ABC):
    @abstractmethod
    def search_graph(self, entities: List[str]) -> List[SearchResult]:
        pass

class AgentTool(ABC):
    @abstractmethod
    def get_tool_schema(self) -> Dict[str, Any]:
        pass

class LLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> str:
        pass
