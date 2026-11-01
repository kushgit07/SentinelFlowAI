"""SentinelFlow document extraction & compliance-query microservice."""
from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from src.ingestion.content_processor import clean_content, chunk_text, scrape_content
from src.nlp.entity_extractor import extract_entities_grouped

app = FastAPI(
    title="SentinelFlow Document Extraction Service",
    description="NLP microservice for parsing unstructured RBI/SEBI regulatory text.",
    version="0.2.0",
)

class ExtractRequest(BaseModel):
    text: str = Field(..., description="Raw or pre-cleaned document text to parse.")
    clean_first: bool = Field(True, description="Run RBI boilerplate cleaning before extraction.")

class ExtractResponse(BaseModel):
    cleaned_text_preview: str
    entity_count: int
    entities: dict
    chunks: List[str]

class ScrapeRequest(BaseModel):
    url: str = Field(..., description="RBI press release URL to scrape and parse.")

class QueryRequest(BaseModel):
    question: str

class BatchQueryRequest(BaseModel):
    questions: List[str] = Field(..., min_length=1)

class QueryResponse(BaseModel):
    question: str
    answer: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/extract", response_model=ExtractResponse)
def extract(req: ExtractRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="text must not be empty")
    cleaned = clean_content(req.text) if req.clean_first else req.text
    chunks = chunk_text(cleaned)
    entities = extract_entities_grouped(cleaned)
    return ExtractResponse(
        cleaned_text_preview=cleaned[:300],
        entity_count=sum(len(v) for v in entities.values()),
        entities=entities,
        chunks=chunks,
    )

@app.post("/scrape-and-extract", response_model=ExtractResponse)
def scrape_and_extract(req: ScrapeRequest):
    text = scrape_content(req.url)
    if not text:
        raise HTTPException(status_code=502, detail="Failed to scrape or parse the given URL.")
    chunks = chunk_text(text)
    entities = extract_entities_grouped(text)
    return ExtractResponse(
        cleaned_text_preview=text[:300],
        entity_count=sum(len(v) for v in entities.values()),
        entities=entities,
        chunks=chunks,
    )

@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest):
    try:
        from src.agents.compliance_agent import query_regulatory_knowledge
        answer = query_regulatory_knowledge(req.question)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Query failed: {e}")
    return QueryResponse(question=req.question, answer=answer)

@app.post("/query/batch", response_model=List[QueryResponse])
def query_batch(req: BatchQueryRequest):
    try:
        from src.agents.compliance_agent import query_regulatory_knowledge_batch
        results = query_regulatory_knowledge_batch(req.questions)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Batch query failed: {e}")
    return [QueryResponse(**r) for r in results]

@app.get("/vault/stats")
def vault_stats():
    try:
        from src.ingestion.vector_store import initialize_db
        collection = initialize_db()
        return {"chunk_count": collection.count()}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Vault unavailable: {e}")
