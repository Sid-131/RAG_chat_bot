"""
generate.py
-----------
Batch embedding generation using Google Gemini Embeddings API.

SDK       : google-genai  (new canonical SDK)
Model     : gemini-embedding-001
Dimension : 3072 floats
Task types:
  - RETRIEVAL_DOCUMENT — used when indexing document chunks
  - RETRIEVAL_QUERY    — used when embedding live user queries

Batching  : 100 chunks per API call
Retry     : tenacity exponential backoff (3 attempts) on rate-limit / 5xx
Backup    : raw .npy arrays saved to data/embeddings/ for reproducibility
"""

import asyncio
import logging
from pathlib import Path
from typing import List

import numpy as np
from google import genai
from google.genai import types as genai_types
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

logger = logging.getLogger(__name__)

EMBEDDING_MODEL       = "gemini-embedding-001"
EMBEDDING_DIM         = 3072
BATCH_SIZE            = 100
EMBEDDINGS_BACKUP_DIR = Path("data/embeddings")


class EmbeddingGenerator:
    """
    Generates dense embeddings for document chunks and queries
    using the Google Gemini gemini-embedding-001 model.
    """

    def __init__(self, api_key: str):
        self._client = genai.Client(api_key=api_key)
        logger.info("EmbeddingGenerator initialised — model: %s, dim: %d",
                    EMBEDDING_MODEL, EMBEDDING_DIM)

    # ------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------

    async def embed_documents(self, texts: List[str]) -> np.ndarray:
        """
        Embed a list of document chunk texts (RETRIEVAL_DOCUMENT task type).

        Args:
            texts: List of chunk text strings.

        Returns:
            np.ndarray of shape (len(texts), 3072), dtype float32.
        """
        all_vectors: List[List[float]] = []
        batches = _batch(texts, BATCH_SIZE)

        for i, batch in enumerate(batches):
            logger.info(
                "Embedding document batch %d/%d (%d texts)",
                i + 1, len(batches), len(batch),
            )
            vectors = await self._embed_batch(batch, task_type="RETRIEVAL_DOCUMENT")
            all_vectors.extend(vectors)

        arr = np.array(all_vectors, dtype=np.float32)
        logger.info("Document embeddings shape: %s", arr.shape)
        return arr

    async def embed_query(self, query: str) -> np.ndarray:
        """
        Embed a single user query (RETRIEVAL_QUERY task type).

        Args:
            query: Raw user question string.

        Returns:
            np.ndarray of shape (3072,), dtype float32.
        """
        vectors = await self._embed_batch([query], task_type="RETRIEVAL_QUERY")
        return np.array(vectors[0], dtype=np.float32)

    def save_backup(self, embeddings: np.ndarray, filename: str = "embeddings.npy") -> Path:
        """Save raw embedding array to data/embeddings/<filename> as a .npy backup."""
        EMBEDDINGS_BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        out_path = EMBEDDINGS_BACKUP_DIR / filename
        np.save(str(out_path), embeddings)
        logger.info("Saved embedding backup: %s  shape=%s", out_path, embeddings.shape)
        return out_path

    def load_backup(self, filename: str = "embeddings.npy") -> np.ndarray:
        """Load a previously saved .npy embedding backup."""
        path = EMBEDDINGS_BACKUP_DIR / filename
        arr = np.load(str(path))
        logger.info("Loaded embedding backup: %s  shape=%s", path, arr.shape)
        return arr

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
    )
    async def _embed_batch(self, batch: List[str], task_type: str) -> List[List[float]]:
        """
        Call the Gemini embedding API for a single batch with retry.

        Args:
            batch:     List of text strings (max 100).
            task_type: "RETRIEVAL_DOCUMENT" or "RETRIEVAL_QUERY".

        Returns:
            List of embedding vectors (each 3072 floats).
        """
        loop = asyncio.get_event_loop()

        def _call():
            response = self._client.models.embed_content(
                model=EMBEDDING_MODEL,
                contents=batch,
                config=genai_types.EmbedContentConfig(task_type=task_type),
            )
            # response.embeddings is a list of ContentEmbedding objects
            return [emb.values for emb in response.embeddings]

        return await loop.run_in_executor(None, _call)


# ------------------------------------------------------------------
# Utilities
# ------------------------------------------------------------------

def _batch(items: List, size: int) -> List[List]:
    """Split a list into sub-lists of at most `size` elements."""
    return [items[i : i + size] for i in range(0, len(items), size)]
