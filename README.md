SentinelFlow AI: Regulatory Intelligence & Automated Compliance Engine

SentinelFlow AI is a high-leverage RAG (Retrieval-Augmented Generation) system architected to navigate the complex, non-linear landscape of financial regulation. Built specifically for Indian banking and RBI/SEBI-related research, it automates the ingestion of regulatory press releases and transforms fragmented policy updates into a searchable, high-fidelity knowledge vault.

Operating on a "Privacy-First, Performance-Always" framework, SentinelFlow keeps sensitive regulatory data secure by handling heavy vectorization locally while offloading inference to high-speed hardware for sub-second, mathematically rigorous insights.
Core Architecture & Tech Stack

    Inference Layer: Powered by Groq LPU Acceleration for near-instant, low-latency dialogue.

    Vector Database: Utilizes ChromaDB for persistent, semantic storage of regulatory "memory."

    Local Embeddings: Runs the all-MiniLM-L6-v2 transformer model on-device, ensuring sensitive text is vectorized without external API exposure.

    Microservices: Backend API built with FastAPI; Executive dashboard built with Streamlit.

Measured Engineering Capabilities

    Boilerplate-Free Ingestion: A custom scraper handles semantic boundary detection and intelligent chunking. Marker-based content cleaning strips site navigation and archive widgets, reducing stored junk chunks from 71% to 0% and optimizing vector storage space.

    Financial Entity Extraction: Rule-based NLP tuned specifically for RBI drafting conventions. Accurately extracts monetary amounts, percentages, instrument tenors, dates, and legal citations with a 98.0% F1 Score (96.2% Recall, 100% Precision) against hand-labeled evaluation sets.

    Batched Retrieval Optimization: Replaced looping sequential database queries with batched ChromaDB vector calls, resulting in measured retrieval speedups of 3.67x to 4.35x on large vector corpora.

    Semantic Risk Analysis: Context-aware RAG querying that evaluates the operational impact on specific financial instruments rather than relying on basic keyword searches.

Installation & Setup

Requires Python 3.10+ and a Groq API Key.
Bash

# Clone the repository
git clone https://github.com/kushgit07/SentinelFlowAI.git
cd SentinelFlowAI

# Create and activate a clean environment
python -m venv venv
# Windows: .\venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# Install specialized dependencies
pip install -r requirements.txt

Create a .env file in the root directory to store your credentials securely. The repository ignores this file.
Code snippet

GROQ_API_KEY=your_actual_groq_api_key_here

Usage Guide

1. Build the Local Vector Vault:
Initialize the ingestion pipeline to build local data before using vault-dependent features.
Bash

python main.py

2. Launch the Executive Dashboard:
Bash

set PYTHONPATH=. && streamlit run src/app/dashboard.py

3. Run the FastAPI Microservice:
The extraction and RAG-query pipeline is exposed over HTTP, independent of the dashboard.
Bash

uvicorn src.api.service:app --reload --port 8000

Interactive API docs available at: http://localhost:8000/docs

Key API Endpoints:

    POST /extract: Entity extraction on raw text (no vault/LLM needed)

    POST /scrape-and-extract: Live URL scraping and entity extraction

    POST /query & POST /query/batch: RAG semantic search over the local vault

    GET /vault/stats & GET /health: System diagnostics

Evaluation & Benchmarks

The repository includes a rigorous testing suite to validate entity extraction accuracy and retrieval speeds. The synthetic load-test corpus is intentionally generated locally rather than committed.
Bash

python3 -m src.evaluation.run_eval          # Entity-extraction accuracy against labeled set
python3 benchmarks/benchmark_retrieval.py   # Vector retrieval speed (naive vs batched)
python3 tests/test_entity_extractor.py      # Unit tests

Project Structure
Plaintext

SentinelFlowAI/
├── src/
│   ├── agents/         # Intelligence orchestration & compliance logic
│   ├── api/            # FastAPI microservice endpoints
│   ├── nlp/            # Rule-based financial entity extraction
│   ├── evaluation/     # Labeled eval sets & precision/recall scoring
│   ├── ingestion/      # Scrapers, content cleaning, chunking, ChromaDB store
│   └── app/            # Streamlit executive dashboard
├── benchmarks/         # Vector retrieval speed benchmarks
├── tests/              # Unit tests for the extraction pipeline
├── scripts/            # Vault maintenance utilities
├── data/               # Persistent 'rbi_vault' (Local Vector Store)
├── requirements.txt    # Sanitized dependency tree
└── README.md           # System documentation

Disclaimer and License

This system is intended as an engineering prototype for regulatory research and institutional compliance decision-support. It does not constitute formal legal advice. Always verify regulatory interpretations against official source documents.

Maintained by kushgit07 — Engineering clarity for the financial sector.
