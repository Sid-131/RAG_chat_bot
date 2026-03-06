"""
test_formatter.py
-----------------
Unit tests for the answer formatter (llm/formatter.py).
"""

import pytest
from llm.formatter import format_answer, _count_sentences, _truncate_to_n_sentences


def test_citation_appended():
    answer = "The expense ratio is 1.82% p.a."
    urls = ["https://miraeassetmf.co.in/schemes/large-cap-fund"]
    result = format_answer(answer, urls)
    assert "miraeassetmf.co.in" in result


def test_no_duplicate_citation():
    url = "https://miraeassetmf.co.in/schemes/large-cap-fund"
    answer = f"The expense ratio is 1.82% p.a. {url}"
    result = format_answer(answer, [url])
    assert result.count(url) == 1


def test_truncate_to_3_sentences():
    text = "Sentence one. Sentence two. Sentence three. Sentence four. Sentence five."
    truncated = _truncate_to_n_sentences(text, 3)
    assert _count_sentences(truncated) <= 3


def test_sentence_counter():
    assert _count_sentences("One sentence.") == 1
    assert _count_sentences("First. Second. Third.") == 3
