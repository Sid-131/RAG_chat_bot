"""
retriever.py
------------
Retrieves the top-k most relevant document chunks from the Chroma vector store.

Settings:
  TOP_K          : 5   — number of results to fetch from Chroma
  MIN_SIMILARITY : 0.30 — cosine distance threshold (Chroma returns distance,
                          lower = more similar; 0.0 = identical, 2.0 = opposite)

Note on Chroma distance vs similarity:
  Chroma with hnsw:space=cosine returns *cosine distance* = 1 - cosine_similarity.
  So a chunk with distance 0.10 has cosine_similarity = 0.90 (very relevant).
  We keep chunks with distance < MIN_DISTANCE (i.e. above similarity threshold).

Scheme-aware filtering:
  If the query explicitly mentions a known scheme name (e.g. "Mirae Asset ELSS"),
  a Chroma `where` filter narrows the search to that scheme's chunks only,
  reducing cross-scheme noise.
"""

import logging
from typing import List, Optional

import numpy as np

from embeddings.index import VectorIndex

logger = logging.getLogger(__name__)

TOP_K        = 5
MIN_DISTANCE = 0.45    # cosine distance threshold (lower = more similar; 0.45 dist = 0.55 sim)

# Known scheme names for metadata-aware filtering
KNOWN_SCHEMES = [
    "Mirae Asset Large Cap Fund",
    "Mirae Asset ELSS Tax Saver Fund",
    "Mirae Asset Emerging Bluechip Fund",
    "Mirae Asset Liquid Fund",
    "Mirae Asset Balanced Advantage Fund",
]


class Retriever:
    """Retrieves relevant chunks from the Chroma vector store."""

    def __init__(self, index: VectorIndex):
        self.index = index

    def retrieve(
        self,
        query_embedding: np.ndarray,
        k: int = TOP_K,
        scheme_filter: Optional[str] = None,
    ) -> List[dict]:
        """
        Run top-k cosine similarity retrieval.

        Args:
            query_embedding: 1-D float32 array of shape (3072,).
            k:               Number of results to retrieve (default 5).
            scheme_filter:   Optional scheme name to narrow the search scope.
                             If None, auto-detection from the query is used.

        Returns:
            List of result dicts, each containing:
              {
                "chunk_id":       str,
                "text":           str,   — chunk text content
                "source_url":     str,
                "title":          str,
                "scheme_name":    str,
                "amc":            str,
                "page_type":      str,
                "scraped_at":     str,
                "chunk_index":    int,
                "total_chunks":   int,
                "distance":       float, — cosine distance (0 = identical)
                "similarity":     float, — 1 - distance  (1 = identical)
              }
            Only chunks with distance < MIN_DISTANCE are returned.
        """
        if self.index.count() == 0:
            logger.warning("Vector store is empty — run the embedding pipeline first.")
            return []

        # Build optional metadata filter
        where = {"scheme_name": scheme_filter} if scheme_filter else None

        raw = self.index.query(
            query_embedding=query_embedding,
            n_results=min(k, self.index.count()),
            where=where,
        )

        results = []
        ids        = raw["ids"][0]
        documents  = raw["documents"][0]
        metadatas  = raw["metadatas"][0]
        distances  = raw["distances"][0]

        for chunk_id, text, meta, dist in zip(ids, documents, metadatas, distances):
            if dist > MIN_DISTANCE:
                logger.debug("Dropped chunk %s — distance %.4f > threshold %.4f",
                             chunk_id, dist, MIN_DISTANCE)
                continue
            results.append({
                "chunk_id":     chunk_id,
                "text":         text,
                "source_url":   meta.get("source_url", ""),
                "title":        meta.get("title", ""),
                "scheme_name":  meta.get("scheme_name", ""),
                "amc":          meta.get("amc", ""),
                "page_type":    meta.get("page_type", ""),
                "scraped_at":   meta.get("scraped_at", ""),
                "chunk_index":  meta.get("chunk_index", 0),
                "total_chunks": meta.get("total_chunks", 0),
                "distance":     round(dist, 4),
                "similarity":   round(1 - dist, 4),
            })

        logger.info(
            "Retrieved %d/%d chunks above similarity threshold (query dim=%s)",
            len(results), k, query_embedding.shape,
        )
        return results

    def detect_scheme(self, query: str) -> Optional[str]:
        """
        Detect if the query explicitly mentions a known scheme name.

        Args:
            query: Raw user question string.

        Returns:
            Matched scheme name string, or None if no match found.
        """
        query_lower = query.lower()
        for scheme in KNOWN_SCHEMES:
            # Match on any significant word in the scheme name
            keywords = [w for w in scheme.lower().split() if len(w) > 3]
            matches  = sum(1 for kw in keywords if kw in query_lower)
            if matches >= 2:   # at least 2 meaningful words must match
                logger.info("Scheme detected in query: %r", scheme)
                return scheme
        return None
