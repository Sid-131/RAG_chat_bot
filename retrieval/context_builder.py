"""
context_builder.py
------------------
Assembles the context string and source URL list from retrieved chunks.

Output:
  context_block: str  — concatenated chunk texts separated by newlines
  source_urls:   list[str] — deduplicated list of source_url values
                             from chunk metadata (most relevant first)
"""

from typing import List


# ---------------------------------------------------------------------------
# TODO: Implement context builder
# ---------------------------------------------------------------------------

def build_context(chunks: List[dict]) -> tuple[str, List[str]]:
    """
    Build context block and source URL list from retrieved chunks.

    Args:
        chunks: list of retrieval result dicts with 'text' and 'metadata' keys

    Returns:
        (context_block, source_urls)
    """
    raise NotImplementedError
