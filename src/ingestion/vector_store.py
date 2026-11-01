import chromadb
from chromadb.utils import embedding_functions

_default_ef = None

def get_embedding_function():
    global _default_ef
    if _default_ef is None:
        _default_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    return _default_ef

def initialize_db():
    client = chromadb.PersistentClient(path="./data/rbi_vault")
    return client.get_or_create_collection(
        name="regulatory_updates",
        embedding_function=get_embedding_function()
    )

def add_to_vault(collection, chunks, metadata):
    """Stores the text chunks in the database."""
    ids = [f"{metadata['prid']}_{i}" for i in range(len(chunks))]
    metadatas = [metadata for _ in chunks]
    collection.add(documents=chunks, ids=ids, metadatas=metadatas)
    print(f"Successfully added {len(chunks)} chunks to the vault.")

def batch_query(collection, questions, n_results=3):
    """Retrieve top-k chunks for multiple questions in one ChromaDB call."""
    if not questions:
        return []
    query_embeddings = get_embedding_function()(questions)
    results = collection.query(query_embeddings=query_embeddings, n_results=n_results)
    return [
        {"question": q, "documents": docs}
        for q, docs in zip(questions, results["documents"])
    ]
