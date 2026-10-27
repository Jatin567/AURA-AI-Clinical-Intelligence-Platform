from app.knowledge.retrieval.models import RetrievalStatistics

class RetrievalStatisticsTracker:
    def __init__(self):
        self.stats = RetrievalStatistics()
        
    def record_query(self, latency_ms: float, cache_hit: bool):
        self.stats.total_queries += 1
        if cache_hit:
            self.stats.cache_hits += 1
        else:
            self.stats.cache_misses += 1
            
        # Moving average
        n = self.stats.total_queries
        self.stats.avg_latency_ms = ((n-1) * self.stats.avg_latency_ms + latency_ms) / n
