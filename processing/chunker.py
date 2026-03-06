"""
chunker.py
----------
Sentence-aware text chunker using spaCy.

Strategy:
- Target chunk size:  400 tokens
- Overlap:            80 tokens (retained from previous chunk tail)
- Unit:               Sentence boundaries (spaCy en_core_web_sm)
- Min chunk size:     60 tokens (orphan fragments are discarded)

Output: list of dicts with 'text' and positional fields for metadata.
"""

from typing import List
import spacy


# ---------------------------------------------------------------------------
# TODO: Implement sentence-aware chunker
# ---------------------------------------------------------------------------

nlp = spacy.load("en_core_web_sm")

CHUNK_SIZE_TOKENS = 400
OVERLAP_TOKENS = 80
MIN_CHUNK_TOKENS = 60


class Chunker:
    """Splits clean text into overlapping sentence-aligned chunks."""

    def chunk(self, text: str) -> List[dict]:
        """
        Returns a list of chunk dicts:
          { 'text': str, 'chunk_index': int, 'total_chunks': int }
        """
        raise NotImplementedError

    def _sentence_tokenize(self, text: str) -> List[str]:
        """Use spaCy to split text into sentences."""
        raise NotImplementedError
