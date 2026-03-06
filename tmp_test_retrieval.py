"""
Test script for the Phase 6 Retrieval Pipeline.

Takes a user query, embeds it (query_embedder.py), searches Chroma (retriever.py),
and formats the resulting chunks (context_builder.py).
"""
import sys, os, json
sys.path.insert(0, ".")

# Force utf-8 printing on Windows
sys.stdout.reconfigure(encoding="utf-8")

from retrieval.query_embedder import embed_query
from retrieval.retriever import Retriever
from retrieval.context_builder import build_context, format_results_for_display
from embeddings.index import VectorIndex

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    print("ERROR: GEMINI_API_KEY is not set.")
    sys.exit(1)

# Sample query related to the data we know is in Chroma (Mirae Asset home page)
QUERY = "What types of mutual funds does Mirae Asset offer?"

print("=" * 60)
print(f"QUERY: {QUERY}")
print("=" * 60)

# 1. Embed the query
print("1. Embedding query with gemini-embedding-001...")
q_vec = embed_query(QUERY, api_key=API_KEY)
print(f"   Shape: {q_vec.shape}")

# 2. Retrieve from Vector DB
print("\n2. Querying Chroma Vector DB...")
vi = VectorIndex()
print(f"   Chroma has {vi.count()} chunks total.")

retriever = Retriever(index=vi)
scheme    = retriever.detect_scheme(QUERY)
if scheme:
    print(f"   Detected scheme name filter: {scheme}")

# Get top 5, but we only have 2 in the DB right now
chunks = retriever.retrieve(q_vec, k=5, scheme_filter=scheme)
print(f"   Retrieved {len(chunks)} chunks above similarity threshold.")

if not chunks:
    print("\nNo relevant chunks found.")
    sys.exit(0)

# 3. Build Context
print("\n3. Building Context Block for LLM...")
ctx_block, sources = build_context(chunks)
display = format_results_for_display(chunks)

print("\n" + "-"*60)
print("🎯 FINAL CONTEXT BLOCK (passed to LLM text generation)")
print("-" * 60)
print(ctx_block)

print("\n" + "-"*60)
print("📄 SOURCE URLs (returned to User UI)")
print("-" * 60)
for i, url in enumerate(sources, 1):
    print(f" [{i}] {url}")

print("\n" + "-"*60)
print("📊 DETAILED METADATA (Internal View)")
print("-" * 60)
for r in display:
    print(f"Rank {r['rank']} | Sim: {r['similarity']:.1%} | {r['chunk_id']}")
