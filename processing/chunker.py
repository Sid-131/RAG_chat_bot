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
        sentences = self._sentence_tokenize(text)
        chunks: List[str] = []
        current_tokens: List[str] = []

        for sentence in sentences:
            sent_tokens = sentence.split()
            # If adding this sentence would exceed the chunk size, flush
            if len(current_tokens) + len(sent_tokens) > CHUNK_SIZE_TOKENS and current_tokens:
                chunk_text = " ".join(current_tokens)
                if len(current_tokens) >= MIN_CHUNK_TOKENS:
                    chunks.append(chunk_text)
                # Keep overlap: retain last OVERLAP_TOKENS tokens
                current_tokens = current_tokens[-OVERLAP_TOKENS:]
            current_tokens.extend(sent_tokens)

        # Flush the last chunk
        if len(current_tokens) >= MIN_CHUNK_TOKENS:
            chunks.append(" ".join(current_tokens))

        total = len(chunks)
        return [
            {"text": c, "chunk_index": i, "total_chunks": total}
            for i, c in enumerate(chunks)
        ]

    def _sentence_tokenize(self, text: str) -> List[str]:
        """Use spaCy to split text into sentences."""
        doc = nlp(text)
        return [sent.text.strip() for sent in doc.sents if sent.text.strip()]
