"""
query_embedder.py
-----------------
Embeds the user's query using the Gemini Embeddings API with
task_type=RETRIEVAL_QUERY for asymmetric retrieval.
"""

from embeddings.generate import EmbeddingGenerator
from config.settings import GEMINI_API_KEY
import numpy as np


# ---------------------------------------------------------------------------
# TODO: Implement query embedder
# ---------------------------------------------------------------------------

def embed_query(query: str) -> np.ndarray:
    """
    Embed a user query string.
    Returns a 768-dim float32 numpy array.
    """
    generator = EmbeddingGenerator(api_key=GEMINI_API_KEY)
    raise NotImplementedError
