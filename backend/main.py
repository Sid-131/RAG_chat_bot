"""
main.py
-------
FastAPI backend service for the Mutual Fund RAG Chatbot.

Orchestrates the full pipeline:
1. Guardrails (Layer 1 Regex + Layer 2 LLM)
2. Retrieval (Query embedding + Chroma fetch + Scheme filter)
3. Answer Generation (Gemini LLM prompt + formatting)

Exposes a POST /query endpoint used by the Streamlit frontend.
"""

import os
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Setup basic logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s — %(message)s")
logger = logging.getLogger(__name__)

# Vercel ChromaDB SQLite patch (Must be done before imports)
if os.environ.get("VERCEL"):
    try:
        import pysqlite3
        import sys
        sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
    except ImportError:
        pass

# Import RAG components
from guardrails.patterns import is_advisory
from guardrails.classifier import classify_intent
from guardrails.refusal import get_refusal

from retrieval.query_embedder import embed_query
from retrieval.retriever import Retriever
from retrieval.context_builder import build_context
from embeddings.index import VectorIndex

from llm.prompt_builder import build_prompt
from llm.generator import AnswerGenerator
from llm.formatter import format_answer

# Globals to hold our initialized components
API_KEY = os.environ.get("GEMINI_API_KEY")
retriever = None
generator = None

app = FastAPI(title="Mutual Fund FAQ Backend")

@app.get("/")
def read_root():
    return {"status": "Vercel FastAPI Backend is running properly!"}

# ---------------------------------------------------------------------------
# Pydantic Schemas
# ---------------------------------------------------------------------------

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    source: Optional[str] = None
    type: str  # "factual" or "refusal"

# ---------------------------------------------------------------------------
# App Lifespan (Startup)
# ---------------------------------------------------------------------------

scheduler_instance = None

@app.on_event("startup")
def startup_event():
    """Initialise global RAG components and background scheduler on app startup."""
    global retriever, generator, API_KEY, scheduler_instance
    if not API_KEY:
        logger.warning("GEMINI_API_KEY environment variable not set. API calls will fail.")
    
    logger.info("Connecting to ChromaDB...")
    vi = VectorIndex()
    logger.info(f"Connected. {vi.count()} chunks in database.")
    
    retriever = Retriever(index=vi)
    if API_KEY:
        generator = AnswerGenerator(api_key=API_KEY)
        logger.info("Generator initialized.")
        
    # Start the Phase 13 background data refresh scheduler ONLY if not on Vercel
    if not os.environ.get("VERCEL"):
        from scheduler.refresh_job import start_scheduler
        scheduler_instance = start_scheduler()
    else:
        logger.info("Running on Vercel Serverless: APScheduler disabled.")

@app.on_event("shutdown")
def shutdown_event():
    """Cleanly shut down the background scheduler."""
    global scheduler_instance
    if scheduler_instance:
        scheduler_instance.shutdown(wait=False)
        logger.info("APScheduler shut down gracefully.")

# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
def health_check():
    return {"status": "ok", "chunks_indexed": retriever.index.count() if retriever else 0}

@app.post("/query", response_model=QueryResponse)
def handle_query(req: QueryRequest):
    """
    Main endpoint for answering user queries.
    Passes through guardrails, retrieval, and LLM generation.
    """
    query = req.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
        
    if not API_KEY:
        raise HTTPException(status_code=500, detail="Server misconfigured: GEMINI_API_KEY missing.")

    logger.info(f"Received query: '{query}'")

    # -----------------------------------------------------------------------
    # 1. Guardrails (Safety Layer)
    # -----------------------------------------------------------------------
    # Layer 1: Regex
    if is_advisory(query):
        logger.info("Blocked by Guardrail Layer 1 (Regex)")
        return QueryResponse(
            answer=get_refusal("ADVISORY"),
            type="refusal"
        )
        
    # Layer 2: LLM Classifier
    intent = classify_intent(query, api_key=API_KEY)
    if intent == "ADVISORY":
        logger.info("Blocked by Guardrail Layer 2 (LLM Classifier)")
        return QueryResponse(
            answer=get_refusal("ADVISORY"),
            type="refusal"
        )
        
    # -----------------------------------------------------------------------
    # 2. Retrieval Pipeline
    # -----------------------------------------------------------------------
    logger.info("Classified as FACTUAL. Proceeding to retrieval...")
    try:
        q_vec = embed_query(query, api_key=API_KEY)
        scheme = retriever.detect_scheme(query)
        chunks = retriever.retrieve(q_vec, k=5, scheme_filter=scheme)
    except Exception as e:
        logger.error(f"Retrieval error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    if not chunks:
        logger.info("No relevant context found.")
        return QueryResponse(
            answer=get_refusal("NO_CONTEXT"),
            type="refusal"  # Or "factual" but no context; refusal fits UI handling well
        )

    # -----------------------------------------------------------------------
    # 3. Answer Generation (LLM Foundation Layer)
    # -----------------------------------------------------------------------
    try:
        context_block, source_urls = build_context(chunks)
        prompt = build_prompt(query, context_block, source_urls)
        raw_answer = generator.generate(prompt)
        
        # Post-process to enforce 3-sentence limit & citations
        final_answer = format_answer(raw_answer, source_urls)
        
        # Determine the primary source link to return in structured JSON
        primary_source = source_urls[0] if source_urls else None
        
        return QueryResponse(
            answer=final_answer,
            source=primary_source,
            type="factual"
        )
    except Exception as e:
        logger.error(f"Generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

