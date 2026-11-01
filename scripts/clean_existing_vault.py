"""Remove boilerplate chunks from an existing local ChromaDB vault."""
import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import chromadb
from src.ingestion.content_processor import is_boilerplate_chunk

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--vault-path", default="./data/rbi_vault")
    parser.add_argument("--collection", default="regulatory_updates")
    args = parser.parse_args()
    client = chromadb.PersistentClient(path=args.vault_path)
    collection = client.get_collection(name=args.collection)
    data = collection.get(include=["documents"])
    ids, documents = data["ids"], data["documents"]
    remove_ids = [doc_id for doc_id, text in zip(ids, documents) if is_boilerplate_chunk(text)]
    print(f"Total chunks: {len(ids)}")
    print(f"Boilerplate chunks: {len(remove_ids)}")
    if args.dry_run or not remove_ids:
        return
    collection.delete(ids=remove_ids)
    print(f"Deleted {len(remove_ids)} chunks. Remaining: {collection.count()}")

if __name__ == "__main__":
    main()
