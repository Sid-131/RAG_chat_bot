"""
classifier.py
-------------
Layer 2 guardrail: LLM-based intent classification.

Used only when Layer 1 (regex patterns) gives no match but the query is
ambiguous. Sends a single-shot prompt to Gemini asking for a one-word
classification: FACTUAL or ADVISORY.

This LLM call is cheap (< 10 tokens output) and fast.
"""

import google.generativeai as genai
from config.settings import GEMINI_API_KEY

CLASSIFICATION_PROMPT = """Classify this user query as exactly one of: FACTUAL or ADVISORY.
- FACTUAL: asks for specific data about a mutual fund (expense ratio, exit load, SIP amount, etc.)
- ADVISORY: asks for investment advice, recommendations, or comparisons

Respond with a single word only: FACTUAL or ADVISORY

Query: "{query}"
"""


# ---------------------------------------------------------------------------
# TODO: Implement LLM-based intent classifier
# ---------------------------------------------------------------------------

def classify_intent(query: str) -> str:
    """
    Classify the user query as 'FACTUAL' or 'ADVISORY' using Gemini.
    Returns 'FACTUAL' by default on any API error.
    """
    raise NotImplementedError
