"""
index.py
--------
Builds, persists, and loads the Chroma vector store.

Collection: mf_faq_chunks
  - documents:  chunk text strings
  - embeddings: 768-dim float32 vectors
  - metadatas:  per-chunk metadata dicts (see processing/metadata.py)
  - ids:        chunk_id strings

Persistence: Chroma's built-in SQLite-backed persistence.
Fallback:    FAISS IndexFlatIP (L2-normalised = cosine), for scale-up.
"""

from pathlib import Path
from typing import List, Optional
import chromadb
import numpy as np

CHROMA_PERSIST_DIR = Path("db/chroma")
COLLECTION_NAME = "mf_faq_chunks"


# ---------------------------------------------------------------------------
# TODO: Implement Chroma index builder and loader
# ---------------------------------------------------------------------------

class VectorIndex:
    """Manages the Chroma vector collection."""

    def __init__(self, persist_dir: Path = CHROMA_PERSIST_DIR):
        self.client = chromadb.PersistentClient(path=str(persist_dir))
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

    def add(
        self,
        chunk_ids: List[str],
        texts: List[str],
        embeddings: np.ndarray,
        metadatas: List[dict],
    ) -> None:
        """Add a batch of chunks to the collection."""
        raise NotImplementedError

    def query(
        self,
        query_embedding: np.ndarray,
        n_results: int = 5,
        where: Optional[dict] = None,
    ) -> dict:
        """
        Run a nearest-neighbour query.
        Returns Chroma query result dict with documents, metadatas, distances.
        """
        raise NotImplementedError
