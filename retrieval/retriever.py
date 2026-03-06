"""
retriever.py
------------
Retrieves the top-k most relevant document chunks from the vector store.

Settings:
  - k (top results):          5
  - Similarity metric:        Cosine
  - Min similarity threshold: 0.65  (chunks below this are discarded)
  - Scheme-aware filtering:   if a scheme name is detected in the query,
                              a Chroma `where` filter narrows the search.
"""

from typing import List, Optional
import numpy as np
from embeddings.index import VectorIndex

TOP_K = 5
MIN_SIMILARITY = 0.65


# ---------------------------------------------------------------------------
# TODO: Implement retriever with metadata filtering
# ---------------------------------------------------------------------------

class Retriever:
    """Retrieves relevant chunks from the Chroma vector store."""

    def __init__(self, index: VectorIndex):
        self.index = index

    def retrieve(
        self,
        query_embedding: np.ndarray,
        scheme_filter: Optional[str] = None,
    ) -> List[dict]:
        """
        Run top-k retrieval.
        Returns list of chunk dicts (text + metadata) above MIN_SIMILARITY.
        """
        raise NotImplementedError

    def _detect_scheme(self, query: str) -> Optional[str]:
        """
        Detect if the query mentions a specific scheme name.
        Returns the scheme name string or None.
        """
        raise NotImplementedError
