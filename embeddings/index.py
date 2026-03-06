"""
index.py
--------
Builds, persists, and queries the Chroma vector store.

Collection : mf_faq_chunks
  documents  : chunk text strings
  embeddings : 768-dim float32 cosine vectors
  metadatas  : per-chunk metadata dicts (chunk_id, source_url, title, ...)
  ids        : chunk_id strings (unique per chunk)

Persistence : Chroma's built-in SQLite-backed PersistentClient.
              The index survives process restarts — just recreate VectorIndex
              pointing at the same persist_dir.
"""

import logging
from pathlib import Path
from typing import List, Optional

import chromadb
import numpy as np

logger = logging.getLogger(__name__)

CHROMA_PERSIST_DIR = Path("db/chroma")
COLLECTION_NAME    = "mf_faq_chunks"


class VectorIndex:
    """
    Wraps a Chroma persistent collection.

    Provides:
      - add()   → upsert chunks with pre-computed embeddings + metadata
      - query() → nearest-neighbour search returning top-k chunks
      - count() → number of vectors currently in the collection
      - delete()→ remove chunks by their chunk_ids
    """

    def __init__(self, persist_dir: Path = CHROMA_PERSIST_DIR):
        persist_dir.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=str(persist_dir))
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},   # cosine similarity
        )
        logger.info(
            "VectorIndex ready — collection '%s' has %d vectors  (persist_dir=%s)",
            COLLECTION_NAME, self.collection.count(), persist_dir,
        )

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def add(
        self,
        chunk_ids:  List[str],
        texts:      List[str],
        embeddings: np.ndarray,
        metadatas:  List[dict],
    ) -> None:
        """
        Upsert a batch of chunks into the collection.

        Chroma's `upsert` is idempotent: re-running the pipeline with the
        same chunk_ids simply overwrites the existing vectors, which is the
        correct behaviour for incremental refresh.

        Args:
            chunk_ids:  Unique string IDs (one per chunk).
            texts:      Raw chunk text (stored for retrieval context).
            embeddings: np.ndarray of shape (N, 768), float32.
            metadatas:  List of metadata dicts — one per chunk.
                        Values must be str | int | float | bool (Chroma requirement).
        """
        # Chroma expects a list of lists, not a numpy array
        embeddings_list = embeddings.tolist()

        # Sanitise metadata: Chroma rejects None values — replace with ""
        safe_metadatas = [
            {k: (v if v is not None else "") for k, v in m.items()}
            for m in metadatas
        ]

        self.collection.upsert(
            ids=chunk_ids,
            documents=texts,
            embeddings=embeddings_list,
            metadatas=safe_metadatas,
        )
        logger.info(
            "Upserted %d chunks → collection now has %d total vectors",
            len(chunk_ids), self.collection.count(),
        )

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def query(
        self,
        query_embedding: np.ndarray,
        n_results: int = 5,
        where: Optional[dict] = None,
    ) -> dict:
        """
        Run a nearest-neighbour cosine similarity search.

        Args:
            query_embedding: 1-D np.ndarray of shape (768,) — the query vector.
            n_results:       Number of top chunks to return (default 5).
            where:           Optional Chroma metadata filter dict,
                             e.g. {"scheme_name": "Mirae Asset Large Cap Fund"}.

        Returns:
            Chroma result dict with keys:
              ids, documents, metadatas, distances
            Each value is a list-of-lists (outer = one per query).
        """
        kwargs: dict = {
            "query_embeddings": [query_embedding.tolist()],
            "n_results": min(n_results, self.collection.count() or 1),
            "include": ["documents", "metadatas", "distances"],
        }
        if where:
            kwargs["where"] = where

        results = self.collection.query(**kwargs)
        logger.debug(
            "Query returned %d results (top distance=%.4f)",
            len(results["ids"][0]),
            results["distances"][0][0] if results["distances"][0] else -1,
        )
        return results

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def count(self) -> int:
        """Return the number of vectors currently in the collection."""
        return self.collection.count()

    def delete(self, chunk_ids: List[str]) -> None:
        """Remove chunks by their IDs (used during incremental refresh)."""
        self.collection.delete(ids=chunk_ids)
        logger.info("Deleted %d chunks from collection", len(chunk_ids))

    def peek(self, limit: int = 3) -> dict:
        """Return a small sample of stored chunks (for debugging)."""
        return self.collection.peek(limit=limit)
