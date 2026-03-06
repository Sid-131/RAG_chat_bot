"""
context_builder.py
------------------
Assembles the context string and source URL list from retrieved chunks.

The context block is injected into the LLM system prompt (Phase 7).
Each chunk is labelled with its source number so the LLM can reference it.

Output:
  context_block : str       — numbered chunk texts for the LLM prompt
  source_urls   : List[str] — deduplicated source URLs (most relevant first)
  formatted_results : List[dict] — full structured result for UI display
"""

import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)


def build_context(chunks: List[dict]) -> Tuple[str, List[str]]:
    """
    Build a numbered context block and deduplicated source URL list
    from retrieved chunk dicts.

    Args:
        chunks: List of result dicts returned by Retriever.retrieve().
                Each dict must have: 'text', 'source_url', 'title',
                'similarity', 'chunk_id'.

    Returns:
        (context_block, source_urls)

        context_block : Multi-line string formatted as:
            [1] Source: <title> | <url>
            <chunk text>

            [2] Source: <title> | <url>
            <chunk text>
            ...

        source_urls : Deduplicated list of source URLs, most-relevant first.
    """
    if not chunks:
        logger.warning("build_context called with 0 chunks — returning empty context")
        return "", []

    context_lines: List[str] = []
    seen_urls: set = set()
    source_urls: List[str] = []

    for i, chunk in enumerate(chunks, start=1):
        url   = chunk.get("source_url", "")
        title = chunk.get("title", "Unknown")
        text  = chunk.get("text", "").strip()
        sim   = chunk.get("similarity", 0.0)

        # Build numbered context entry
        context_lines.append(
            f"[{i}] Source: {title}\n"
            f"    URL: {url}\n"
            f"    Relevance: {sim:.2%}\n"
            f"{text}"
        )

        # Collect unique URLs in order
        if url and url not in seen_urls:
            source_urls.append(url)
            seen_urls.add(url)

    context_block = "\n\n".join(context_lines)
    logger.info(
        "Context built: %d chunks, %d unique sources, %d total chars",
        len(chunks), len(source_urls), len(context_block),
    )
    return context_block, source_urls


def format_results_for_display(chunks: List[dict]) -> List[dict]:
    """
    Format retrieved chunks for UI or API response display.

    Args:
        chunks: List of retrieval result dicts.

    Returns:
        List of simplified display dicts:
          {
            "rank":       int,     — 1-based rank by similarity
            "chunk_id":   str,
            "text":       str,     — chunk text
            "source_url": str,
            "title":      str,
            "similarity": float,   — 0.0–1.0 cosine similarity
            "scheme":     str,
          }
    """
    return [
        {
            "rank":       i,
            "chunk_id":   c.get("chunk_id", ""),
            "text":       c.get("text", ""),
            "source_url": c.get("source_url", ""),
            "title":      c.get("title", ""),
            "similarity": c.get("similarity", 0.0),
            "scheme":     c.get("scheme_name", ""),
        }
        for i, c in enumerate(chunks, start=1)
    ]
