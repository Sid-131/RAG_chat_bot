"""
generate.py
-----------
Batch embedding generation using Google Gemini Embeddings API.

Model:      models/text-embedding-004
Dimension:  768 (default)
Task types:
  - RETRIEVAL_DOCUMENT  — used when indexing chunks
  - RETRIEVAL_QUERY     — used when embedding user queries

Batching:   100 chunks per API call (API limit)
Async:      asyncio + tenacity for rate-limit retries
"""

import asyncio
from pathlib import Path
from typing import List
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential
import numpy as np

EMBEDDING_MODEL = "models/text-embedding-004"
BATCH_SIZE = 100


# ---------------------------------------------------------------------------
# TODO: Implement batch embedding generation
# ---------------------------------------------------------------------------

class EmbeddingGenerator:
    """Generates embeddings for document chunks using the Gemini API."""

    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)

    async def embed_documents(self, texts: List[str]) -> np.ndarray:
        """
        Embed a list of document chunks (RETRIEVAL_DOCUMENT task type).
        Returns an array of shape (len(texts), 768).
        """
        raise NotImplementedError

    async def embed_query(self, query: str) -> np.ndarray:
        """
        Embed a single user query (RETRIEVAL_QUERY task type).
        Returns an array of shape (768,).
        """
        raise NotImplementedError

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def _embed_batch(self, batch: List[str], task_type: str) -> List[List[float]]:
        """Embed a single batch with retry logic."""
        raise NotImplementedError
