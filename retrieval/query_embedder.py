"""
query_embedder.py
-----------------
Embeds a user's query using the Gemini API with RETRIEVAL_QUERY task type.

Uses the same model (gemini-embedding-001) as the document indexing step,
but with task_type=RETRIEVAL_QUERY which is optimised for asymmetric
retrieval (short query matching longer document chunks).

The embed_query() function is synchronous for easy use in the retrieval
pipeline — it internally runs the async call via asyncio.run().
"""

import asyncio
import logging
import numpy as np

from embeddings.generate import EmbeddingGenerator

logger = logging.getLogger(__name__)


def embed_query(query: str, api_key: str) -> np.ndarray:
    """
    Embed a user query into a 3072-dim float32 vector.

    Args:
        query:   Raw user question string.
        api_key: Google Gemini API key.

    Returns:
        np.ndarray of shape (3072,), dtype float32.
    """
    generator = EmbeddingGenerator(api_key=api_key)
    vector = asyncio.run(generator.embed_query(query))
    logger.info(
        "Query embedded — shape: %s  preview: [%.4f, %.4f, ...]",
        vector.shape, vector[0], vector[1],
    )
    return vector
