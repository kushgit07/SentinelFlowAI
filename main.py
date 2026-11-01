import os
from dotenv import load_dotenv
from src.ingestion.scraper import fetch_rbi_press_releases
from src.ingestion.content_processor import scrape_content, chunk_text
from src.ingestion.vector_store import initialize_db, add_to_vault

load_dotenv()

def run_pipeline():
    print("--- Starting Regulatory Alpha Ingestion Pipeline ---")
    vault = initialize_db()
    releases = fetch_rbi_press_releases()
    if not releases:
        print("No releases found. Pipeline stopped.")
        return
    for item in releases[:3]:
        print(f"\nProcessing: {item['title']}")
        prid = item['link'].split('prid=')[-1]
        full_text = scrape_content(item['link'])
        if full_text:
            chunks = chunk_text(full_text)
            metadata = {
                "title": item['title'],
                "link": item['link'],
                "prid": prid,
                "source": "RBI"
            }
            add_to_vault(vault, chunks, metadata)
        else:
            print(f"Skipping {prid} due to empty content.")
    print("\n--- Pipeline Completed Successfully ---")

if __name__ == "__main__":
    run_pipeline()
