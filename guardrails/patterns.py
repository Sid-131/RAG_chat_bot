"""
patterns.py
-----------
Layer 1 guardrail: regex-based detection of advisory or non-factual queries.

If any pattern in ADVISORY_PATTERNS matches the user query (case-insensitive),
the query is immediately classified as ADVISORY without touching the LLM.
"""

import re

# --- Advisory intent patterns ---
ADVISORY_PATTERNS = [
    r"should i invest",
    r"which fund is best",
    r"recommend",
    r"better fund",
    r"compare funds",
    r"which is better",
    r"where should i put my money",
    r"top performing",
    r"highest return",
    r"should i switch",
    r"is .+ worth.+invest",
    r"should i buy",
    r"best mutual fund",
    r"which scheme should",
]

# Compile for performance
_COMPILED = [re.compile(p, re.IGNORECASE) for p in ADVISORY_PATTERNS]


def is_advisory(query: str) -> bool:
    """
    Return True if the query matches any advisory keyword pattern.
    """
    return any(pattern.search(query) for pattern in _COMPILED)
