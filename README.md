#  SentinelFlow AI
### *Regulatory Intelligence & Automated Compliance Engine*

*SentinelFlow AI* is a high-leverage RAG (Retrieval-Augmented Generation) system architected to navigate the "non-linear chaos" of financial regulation. Built specifically for the Indian banking landscape, it automates the ingestion of RBI press releases and transforms fragmented policy updates into a searchable, high-fidelity knowledge vault.

In a sector where precision is the only currency, SentinelFlow provides a "Quiet Luxury" solution: minimal, mathematically rigorous, and incredibly fast.

---

##  The Architecture

The engine is built on a "Privacy-First, Performance-Always" framework. By handling heavy vectorization locally and offloading inference to high-speed hardware, we ensure compliance data stays secure while response times remain sub-second.

* *Inference Layer:* Powered by *Groq LPU Acceleration* for near-instant, human-speed dialogue.
* *Vector Database:* Utilizes *ChromaDB* for persistent, semantic storage of regulatory "memory."
* *Local Embeddings:* Runs the *all-MiniLM-L6-v2* transformer model on-device. This ensures that sensitive regulatory text is vectorized without external API exposure, maintaining a higher standard of data privacy.
* *Ingestion Pipeline:* A custom scraper designed for the RBI interface that handles semantic boundary detection and intelligent chunking.

---

##  Engine Capabilities

* *Automated Policy Scraping:* Real-time ingestion of official RBI announcements, moving from raw HTML/PDF to structured vector data.
* *Boilerplate-Free Extraction:* Marker-based content cleaning strips site navigation, the archive calendar widget, and footer links before chunking (see [Measured Engineering Decisions](#measured-engineering-decisions) below for the before/after numbers).
* *Financial Entity Extraction:* Rule-based extraction of monetary amounts, percentages, instrument tenors, dates, and regulatory/legal citations from RBI press releases (`src/nlp/entity_extractor.py`).
* *FastAPI Microservice:* The extraction and RAG-query pipeline is also exposed over HTTP (`src/api/service.py`), independent of the Streamlit dashboard, with batched query support.
* *Semantic Risk Analysis:* Context-aware querying (e.g., "What is the impact on prepaid payment instruments?") that finds meaning, not just keywords.
* *Low-Latency RAG:* Optimized for environments where time-to-insight is a critical metric.
* *Repository Hygiene:* A production-ready codebase following modular engineering standards and sanitization protocols.

---

##  Quick Start Guide

### *1. Preparation*
* Python 3.10+ installed.
* A *Groq API Key* (obtainable at [console.groq.com](https://console.groq.com)).

### *2. Installation*
```bash
# Clone the repository
git clone [https://github.com/kushgit07/SentinelFlow-AI.git](https://github.com/kushgit07/SentinelFlow-AI.git)
cd SentinelFlow-AI

# Create and activate a clean environment
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate # Linux/Mac

# Install specialized dependencies
pip install -r requirements.txt
```
### *3. Environment Config*
```bash
Create a .env file in the root directory to store your credentials securely:
GROQ_API_KEY=your_actual_groq_api_key_here
```
### *4. System Launch*
```bash
set PYTHONPATH=. && streamlit run src/app/dashboard.py
```

### *5. Running the FastAPI Microservice (optional, separate from the dashboard)*
```bash
uvicorn src.api.service:app --reload --port 8000
# Interactive API docs: http://localhost:8000/docs
```
Key endpoints: `POST /extract` (entity extraction on raw text, no vault/LLM needed), `POST /scrape-and-extract` (live URL), `POST /query` and `POST /query/batch` (RAG over the vault), `GET /vault/stats`, `GET /health`.

### *6. Running the Evaluation & Benchmark Suite*
```bash
python3 -m src.evaluation.run_eval          # entity-extraction accuracy against labeled set
python3 benchmarks/benchmark_retrieval.py   # vector retrieval: naive vs batched query speed
python3 tests/test_entity_extractor.py      # unit tests
```
---
## Project Structure
``` bash
SentinelFlow-AI/
├── src/
│   ├── agents/         # Intelligence orchestration & compliance logic (single + batched RAG)
│   ├── api/            # FastAPI microservice (extraction + RAG endpoints)
│   ├── nlp/            # Rule-based financial entity extraction
│   ├── evaluation/      # Labeled eval set + accuracy/precision/recall scoring
│   ├── ingestion/      # Scrapers, content cleaning, chunking, vector store
│   └── app/            # Streamlit executive dashboard
├── benchmarks/         # Vector retrieval speed benchmark (naive vs batched)
├── tests/              # Unit tests
├── scripts/            # One-time vault maintenance utilities
├── data/               # Persistent 'rbi_vault' (Local Vector Store)
├── requirements.txt    # Sanitized dependency tree
└── README.md           # System documentation
```
---
## Measured Engineering Decisions

This section exists so every number in this README is traceable to a script in the repo, not just stated. Re-run any of these yourself: `python3 -m src.evaluation.run_eval` and `python3 benchmarks/benchmark_retrieval.py`.

### The boilerplate bug

Auditing the live vault (`data/rbi_vault`) showed **71% of stored chunks were pure site furniture** — the RBI website's nav bar, a month/year archive picker repeated on every press-release page, and footer/social links — not regulatory content. `soup.get_text()` on the raw page pulled in everything indiscriminately, so junk chunks were competing for space in every top-k retrieval and wasting embedding storage.

The fix (`src/ingestion/content_processor.py::clean_content`) anchors on two text markers that are consistent across RBI's press-release template: the page always states `"Press Releases ( N kb ) Date : <date>"` immediately before the real content, and the archive picker always begins with the literal sequence `"January February March ... December"`. The function slices between those markers, with a chunk-level filter as a defense-in-depth backstop and a fallback to the original behavior if the markers aren't found (so a future template change degrades gracefully instead of silently dropping content).

Measured on the 3 documents in the live vault: boilerplate chunks dropped from **71% → 0%**, and total chunk volume dropped **67.7%** (31 chunks → 10, after re-chunking the same source documents with the fix applied). A one-time migration script (`scripts/clean_existing_vault.py`) purged the already-stored boilerplate chunks from the live vault.

### Entity extraction accuracy

Rather than a general-purpose NER model (which isn't tuned to constructs like *"91-Day Treasury Bills"* or *"Section 24 of the Banking Regulation Act, 1949"*), `src/nlp/entity_extractor.py` uses rule-based extraction tuned to RBI's drafting conventions: monetary amounts, percentages, instrument tenors, dates, regulatory citations, legal references, instruments, and organizations.

Accuracy is measured against a hand-labeled set (`src/evaluation/eval_set.json`) of 5 documents / 52 gold entities — 3 real documents pulled from the live vault, plus 2 constructed examples added for entity-type coverage the live vault didn't yet have (clearly marked as `constructed_for_eval_coverage` in the dataset, since only 3 real documents existed at build time). Scoring is exact-string-match set comparison (`src/evaluation/run_eval.py`):

| Metric | Result |
|---|---|
| Recall ("accuracy") | **96.2%** |
| Precision | **100%** |
| F1 | **98.0%** |

The known gap: the percentage/amount patterns require digit-form numbers, so spelled-out quantifiers like *"ten per cent"* aren't matched (2 of the 52 gold entities). This is documented as a scope boundary, not silently swept under the rug — `tests/test_entity_extractor.py::test_known_limitation_spelled_out_numbers` exists specifically so it stays visible.

This is a small initial eval set; it's designed to grow as the live vault accumulates more real scraped documents rather than being treated as a final number.

### Retrieval optimization

"Optimizing vector database queries" specifically means batching: `src/ingestion/vector_store.py::batch_query` embeds multiple questions and issues **one** ChromaDB call with all query vectors, instead of looping `collection.query()` once per question (the original pattern in `compliance_agent.py`). This matters for any workflow checking several compliance questions against the vault at once (e.g. a nightly checklist scan) rather than one interactive question at a time.

`benchmarks/benchmark_retrieval.py` isolates the database-call layer from embedding-inference time (which is identical either way) by timing with pre-computed query vectors, and benchmarks against a synthetic load-test corpus seeded from the vault's real embeddings (the live vault only had 28 chunks — too small to represent "high-volume" load, so vectors were scaled up by sampling real seed embeddings with Gaussian noise; this is explicitly a synthetic load-test corpus, not real regulatory text, and the script's docstring spells out why).

Measured speedup (naive sequential queries vs. one batched call), averaged over multiple trials at each scale:

| Corpus size | Queries/batch | Speedup |
|---|---|---|
| 500 vectors | 10 | 3.67x |
| 5,000 vectors | 50 | 4.35x |
| 10,000 vectors | 100 | 3.88x |

---
 ## Engineering Ethos
 
SentinelFlow was built with a specific mindset: Math over convenience. By avoiding bloated generic wrappers and focusing on specialized local embeddings, we reduce model hallucinations and ensure that every compliance insight is grounded in official documentation. It is an engine built for those who value calm, systematic order within complex financial ecosystems.

---
##Disclaimer and License

This system is intended as an assistant for regulatory research and institutional compliance. It does not constitute formal legal advice.

Maintained by [kushgit07] — Engineering clarity for the financial sector.
