"""
prompt_builder.py
-----------------
Constructs the full prompt for the Gemini LLM, including the system rules,
context block, source URLs, and user query.

System Rules enforced via prompt:
  1. Answer ONLY from the provided CONTEXT
  2. Maximum 3 sentences per answer
  3. End every answer with exactly one source link
  4. No financial advice or return comparisons
  5. If context is insufficient, return the 'no information' fallback message
"""

from typing import List

SYSTEM_RULES = """You are a factual assistant for Groww's mutual fund information service.

Rules you must follow absolutely:
1. Answer ONLY using information from the CONTEXT provided. Do not use prior knowledge.
2. Your answer must be a maximum of 3 sentences.
3. End every answer with exactly one source link from the SOURCES list.
4. Do not provide financial advice, investment recommendations, or return comparisons.
5. If the context does not contain the answer, say: "I don't have that information. \
Please check the AMC's official website or Groww Help Center."
6. Do not speculate or infer beyond what the context states.
"""


# ---------------------------------------------------------------------------
# TODO: Implement prompt builder
# ---------------------------------------------------------------------------

def build_prompt(query: str, context_block: str, source_urls: List[str]) -> str:
    """
    Construct the full prompt string.

    Args:
        query:         User's factual question
        context_block: Concatenated retrieved chunk texts
        source_urls:   List of source URLs from retrieved chunks

    Returns:
        Complete prompt string ready for Gemini API
    """
    raise NotImplementedError
