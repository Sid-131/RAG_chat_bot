"""
embedding_pipeline.py
---------------------
End-to-end orchestrator: reads data/raw/ JSON documents, chunks each one,
generates Gemini embeddings, and upserts into the Chroma vector store.

Run:
    python -m embeddings.embedding_pipeline

Environment variable required:
    GEMINI_API_KEY=<your-key>

Flow:
    data/raw/*.json
        → [Chunker]         split clean text into 400-token sentence-chunks
        → [MetadataBuilder] attach chunk_id, source_url, title, scheme_name ...
        → [EmbeddingGenerator] call Gemini text-embedding-004 in batches of 100
        → [VectorIndex]     upsert into Chroma (db/chroma/)
        → data/embeddings/  .npy backup of raw vectors
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path

from processing.chunker import Chunker
from processing.metadata import MetadataBuilder
from embeddings.generate import EmbeddingGenerator
from embeddings.index import VectorIndex

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

RAW_DIR = Path("data/raw")


async def run_embedding_pipeline(api_key: str) -> None:
    """
    Main async pipeline. Reads all .json files from data/raw/,
    chunks them, embeds, and upserts into Chroma.

    Args:
        api_key: Google Gemini API key.
    """
    raw_files = sorted(RAW_DIR.glob("*.json"))
    if not raw_files:
        logger.warning("No documents found in %s — run the ingestion pipeline first.", RAW_DIR)
        return

    logger.info("Found %d documents in %s", len(raw_files), RAW_DIR)

    chunker   = Chunker()
    meta_builder = MetadataBuilder()
    embedder  = EmbeddingGenerator(api_key=api_key)
    index     = VectorIndex()

    # Collect all chunks across all documents
    all_chunk_ids:  list[str]  = []
    all_texts:      list[str]  = []
    all_metadatas:  list[dict] = []

    for doc_path in raw_files:
        doc = json.loads(doc_path.read_text(encoding="utf-8"))
        url         = doc.get("url", "")
        title       = doc.get("title", "")
        content     = doc.get("content", "")
        scheme_name = doc.get("scheme_name")
        amc         = doc.get("amc")
        page_type   = doc.get("page_type", "unknown")
        scraped_at  = doc.get("scraped_at")

        if not content.strip():
            logger.warning("Empty content in %s — skipping", doc_path.name)
            continue

        # Chunk the document
        raw_chunks = chunker.chunk(content)
        logger.info(
            "Document: %s → %d chunks  (title=%r)",
            doc_path.name, len(raw_chunks), title,
        )

        for chunk in raw_chunks:
            meta = meta_builder.build(
                source_url   = url,
                title        = title,
                scheme_name  = scheme_name,
                amc          = amc,
                page_type    = page_type,
                chunk_index  = chunk["chunk_index"],
                total_chunks = chunk["total_chunks"],
                scraped_at   = scraped_at,
            )
            all_chunk_ids.append(meta["chunk_id"])
            all_texts.append(chunk["text"])
            all_metadatas.append(meta)

    if not all_texts:
        logger.warning("No chunks to embed — pipeline exiting.")
        return

    logger.info("Total chunks to embed: %d", len(all_texts))

    # Generate embeddings
    embeddings = await embedder.embed_documents(all_texts)

    # Save .npy backup
    embedder.save_backup(embeddings, filename="mf_faq_embeddings.npy")

    # Upsert into Chroma
    index.add(
        chunk_ids  = all_chunk_ids,
        texts      = all_texts,
        embeddings = embeddings,
        metadatas  = all_metadatas,
    )

    logger.info(
        "✅ Embedding pipeline complete — %d chunks stored in Chroma  (total in DB: %d)",
        len(all_texts), index.count(),
    )

    # Print a quick sample from the index
    sample = index.peek(limit=2)
    logger.info("Sample stored chunks: %s", json.dumps(sample, indent=2, default=str))


if __name__ == "__main__":
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        print("ERROR: GEMINI_API_KEY environment variable is not set.")
        sys.exit(1)
    asyncio.run(run_embedding_pipeline(api_key=key))
