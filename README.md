# SentinelFlow

SentinelFlow is a regulatory intelligence project for RBI/SEBI-related research. It combines an RBI press-release ingestion pipeline, text cleaning and chunking, a ChromaDB vector store, rule-based financial entity extraction, a Groq-backed retrieval-augmented generation (RAG) agent, a Streamlit dashboard, and a FastAPI service.

## Features
- RBI press-release discovery and scraping
- Boilerplate cleaning and recursive text chunking
- Persistent ChromaDB storage with local `all-MiniLM-L6-v2` embeddings
- Batched vector retrieval for multiple questions
- Extraction of monetary amounts, percentages, tenors, dates, circular references, legal citations, instruments, and organizations
- Streamlit dashboard and FastAPI endpoints

## Setup
Requires Python 3.10+.

```bash
git clone https://github.com/kushgit07/SentinelFlowAI.git
cd SentinelFlowAI
python -m venv venv
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Never commit real API keys. The repository ignores `.env`.

## Run
Build/update the local vector vault:

```bash
python main.py
```

Launch the dashboard:

```bash
streamlit run src/app/dashboard.py
```

Run the API:

```bash
uvicorn src.api.service:app --reload --port 8000
```

API documentation is available at `http://localhost:8000/docs`.

Key endpoints: `GET /health`, `POST /extract`, `POST /scrape-and-extract`, `POST /query`, `POST /query/batch`, and `GET /vault/stats`.

## Project layout
```
src/
  agents/       RAG compliance agent
  api/          FastAPI service
  app/          Streamlit dashboard
  evaluation/   Gold-labelled entity extraction evaluation set and runner
  ingestion/    RBI scraper, cleaner, chunker, vector store
  nlp/          Financial entity extraction
benchmarks/     Retrieval benchmark
scripts/        Vault maintenance utility
tests/          Entity extractor tests
```

## Tests, evaluation, and benchmark
Run the unit tests:

```bash
python3 tests/test_entity_extractor.py
```

Run the labelled entity-extraction evaluation:

```bash
python3 -m src.evaluation.run_eval
```

Run the retrieval benchmark:

```bash
python3 benchmarks/benchmark_retrieval.py
```

The retrieval benchmark requires a populated local vault and creates a synthetic test corpus seeded from local embeddings.

## ChromaDB data
The original project archive contains a small ChromaDB snapshot under `data/rbi_vault/`. The SQLite database and HNSW index are binary runtime data rather than source code; they are not included in this repository commit. Run `python main.py` to build a fresh local vault before using vault-dependent features or the retrieval benchmark. Do not commit live database/WAL/SHM files or private source data.

## Disclaimer
SentinelFlow is a research and decision-support aid, not legal or compliance advice. Verify regulatory interpretations against official source documents.
