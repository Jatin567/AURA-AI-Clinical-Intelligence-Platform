import time
import numpy as np
from app.knowledge.vectorstore.faiss_provider import FAISSProvider
from app.knowledge.vectorstore.store import VectorStoreImpl

def run_benchmark():
    dimension = 384
    num_vectors = 1000
    
    provider = FAISSProvider(dimension=dimension)
    store = VectorStoreImpl(provider)
    
    embeddings = np.random.rand(num_vectors, dimension).astype('float32')
    ids = [f"doc_{i}" for i in range(num_vectors)]
    
    start_time = time.time()
    store.batch_insert(embeddings, ids)
    end_time = time.time()
    
    insert_time = end_time - start_time
    print(f"Insertion of {num_vectors} vectors took {insert_time:.4f} seconds.")
    
    query = np.random.rand(dimension).astype('float32')
    start_time = time.time()
    res = store.top_k_search(query, 10)
    end_time = time.time()
    
    search_time = end_time - start_time
    print(f"Top 10 search took {search_time:.4f} seconds.")

if __name__ == "__main__":
    run_benchmark()
