"""Compare sequential and batched ChromaDB retrieval using a synthetic corpus."""
import random
import statistics
import time
import chromadb

def build_synthetic_corpus(real_embeddings, target_size, seed=42):
    rng = random.Random(seed)
    return [
        [value + rng.gauss(0, 0.02) for value in rng.choice(real_embeddings)]
        for _ in range(target_size)
    ]

def time_naive(collection, query_vectors, n_results=3):
    start = time.perf_counter()
    for vector in query_vectors:
        collection.query(query_embeddings=[vector], n_results=n_results)
    return time.perf_counter() - start

def time_batched(collection, query_vectors, n_results=3):
    start = time.perf_counter()
    collection.query(query_embeddings=query_vectors, n_results=n_results)
    return time.perf_counter() - start

def run_benchmark(corpus_size=5000, n_queries=50, trials=5):
    real_client = chromadb.PersistentClient(path="./data/rbi_vault")
    real_collection = real_client.get_collection(name="regulatory_updates")
    real_data = real_collection.get(include=["embeddings"])
    real_embeddings = [list(item) for item in real_data["embeddings"]]
    synthetic = build_synthetic_corpus(real_embeddings, corpus_size)
    bench_client = chromadb.EphemeralClient()
    bench = bench_client.get_or_create_collection(name=f"benchmark_{corpus_size}_{n_queries}")
    ids = [f"vec_{i}" for i in range(len(synthetic))]
    for offset in range(0, len(synthetic), 500):
        bench.add(ids=ids[offset:offset + 500], embeddings=synthetic[offset:offset + 500])
    query_vectors = build_synthetic_corpus(real_embeddings, n_queries, seed=99)
    naive = [time_naive(bench, query_vectors) for _ in range(trials)]
    batched = [time_batched(bench, query_vectors) for _ in range(trials)]
    naive_mean, batched_mean = statistics.mean(naive), statistics.mean(batched)
    speedup = naive_mean / batched_mean if batched_mean else float("inf")
    print(f"Corpus: {corpus_size}; queries: {n_queries}; trials: {trials}")
    print(f"Naive mean: {naive_mean:.4f}s")
    print(f"Batched mean: {batched_mean:.4f}s")
    print(f"Speedup: {speedup:.2f}x")
    return {"corpus_size": corpus_size, "n_queries": n_queries, "trials": trials, "speedup": speedup}

if __name__ == "__main__":
    run_benchmark()
