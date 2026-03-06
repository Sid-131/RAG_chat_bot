"""
test_guardrails.py
------------------
Unit tests for the Layer 1 regex guardrail (guardrails/patterns.py).
"""

import pytest
from guardrails.patterns import is_advisory

# --- Advisory queries (should return True) ---
@pytest.mark.parametrize("query", [
    "Should I invest in ELSS?",
    "Which mutual fund is best for me?",
    "Can you recommend a good SIP?",
    "Which fund gives the highest return?",
    "Should I switch from large cap to mid cap?",
    "Compare Mirae Asset and HDFC funds",
    "Which is better: growth or dividend?",
    "Best mutual fund for beginners",
])
def test_advisory_queries_detected(query):
    assert is_advisory(query) is True


# --- Factual queries (should return False for Layer 1) ---
@pytest.mark.parametrize("query", [
    "What is the expense ratio of Mirae Asset Large Cap Fund?",
    "What is the exit load of Mirae Asset ELSS?",
    "What is the minimum SIP amount for Mirae Asset Liquid Fund?",
    "What is the ELSS lock-in period?",
    "What is the riskometer of Mirae Asset Emerging Bluechip Fund?",
    "How can I download my capital gains report from Groww?",
    "What benchmark does Mirae Asset Large Cap Fund track?",
])
def test_factual_queries_not_flagged(query):
    assert is_advisory(query) is False
