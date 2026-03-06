"""
prompt_builder.py
-----------------
Constructs the full prompt for the Gemini LLM, including the system rules,
context block, and user query.

System Rules enforced via prompt:
  - Answer ONLY from the provided CONTEXT
  - Maximum 3 sentences per answer
  - Include exactly one citation link
  - No financial advice or return comparisons
  - If context is insufficient, return a standard fallback message
"""

from typing import List

SYSTEM_RULES = """You are a factual, professional assistant for a mutual fund information service.
Your task is to answer the user's question using ONLY the information provided in the CONTEXT block below.

Strict Rules:
1. FACTUAL ONLY: Answer strictly using facts from the CONTEXT. Do not use your prior knowledge.
2. LENGTH: Keep your answer concise. It MUST be a maximum of 3 sentences.
3. ADVICE: Do not provide financial advice, investment recommendations, or predict future returns.
4. CITATION: You MUST include exactly one citation link at the end of your answer in this format:
   Source: <URL>
   Choose the most relevant URL from the CONTEXT block.
5. NO HALLUCINATION: If the context does not contain enough information to factualy answer the question, you MUST respond EXACTLY with this phrase and nothing else:
   "The information is not available in the provided official sources."

--- CONTEXT ---
{context_block}

--- USER QUESTION ---
{query}

Answer:"""


def build_prompt(query: str, context_block: str, source_urls: List[str] = None) -> str:
    """
    Construct the full prompt string.

    Args:
        query:         User's factual question
        context_block: Concatenated retrieved chunk texts (numbered with URLs)
        source_urls:   (Optional) List of source URLs. Handled mostly in context_block now.

    Returns:
        Complete prompt string ready for Gemini API
    """
    return SYSTEM_RULES.format(
        context_block=context_block if context_block.strip() else "No relevant context found.",
        query=query
    )
