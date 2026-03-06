"""
test_chunker.py
---------------
Unit tests for the sentence-aware chunker (processing/chunker.py).
"""

import pytest
from processing.chunker import Chunker

chunker = Chunker()


def test_chunk_returns_list():
    text = "The expense ratio of the fund is 1.82% p.a. This fee is deducted from the NAV daily."
    chunks = chunker.chunk(text)
    assert isinstance(chunks, list)


def test_chunk_index_continuity():
    text = " ".join(["The fund has an exit load of 1%." for _ in range(50)])
    chunks = chunker.chunk(text)
    indices = [c["chunk_index"] for c in chunks]
    assert indices == list(range(len(chunks)))


def test_no_empty_chunks():
    text = "Minimum SIP amount is ₹500 per month. The fund category is Large Cap."
    chunks = chunker.chunk(text)
    for chunk in chunks:
        assert len(chunk["text"].strip()) > 0


def test_orphan_fragments_discarded():
    text = "Short."  # below MIN_CHUNK_TOKENS
    chunks = chunker.chunk(text)
    # Either no chunks or only chunks meeting minimum
    for chunk in chunks:
        assert len(chunk["text"].split()) >= 10  # rough proxy for token count
