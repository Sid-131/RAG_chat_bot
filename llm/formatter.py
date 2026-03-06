"""
formatter.py
------------
Post-processes the raw LLM answer to enforce output constraints:

1. Sentence count check: if > 3 sentences, truncate to first 3
2. Citation appending:   append `source_url` of the highest-ranked chunk
                         if not already present in the answer

Output: final response string shown to the user.
"""

import re
from typing import List


# ---------------------------------------------------------------------------
# TODO: Implement answer formatter
# ---------------------------------------------------------------------------

def format_answer(raw_answer: str, source_urls: List[str]) -> str:
    """
    Apply post-processing rules and append citation.

    Args:
        raw_answer:  Raw text returned by the LLM
        source_urls: Ordered list of source URLs (most relevant first)

    Returns:
        Formatted answer string with citation appended.
    """
    raise NotImplementedError


def _count_sentences(text: str) -> int:
    """Count sentences using regex."""
    raise NotImplementedError


def _truncate_to_n_sentences(text: str, n: int = 3) -> str:
    """Return at most n sentences from text."""
    raise NotImplementedError
