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

FALLBACK_MESSAGE = "The information is not available in the provided official sources."

def format_answer(raw_answer: str, source_urls: List[str]) -> str:
    """
    Apply post-processing rules and append citation.
    """
    answer = _truncate_to_n_sentences(raw_answer.strip(), 3)

    # Do not append citation if the answer is the fallback message
    if FALLBACK_MESSAGE.lower() in answer.lower():
        return answer

    # Append citation only if not already present
    if source_urls:
        primary_url = source_urls[0]
        if primary_url not in answer:
            answer = f"{answer}\n\n[Source]({primary_url})"

    return answer


def _count_sentences(text: str) -> int:
    """Count sentences using regex."""
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return len([s for s in sentences if s])


def _truncate_to_n_sentences(text: str, n: int = 3) -> str:
    """Return at most n sentences from text."""
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    sentences = [s for s in sentences if s]
    return " ".join(sentences[:n])
