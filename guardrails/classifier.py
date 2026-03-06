"""
classifier.py
-------------
Layer 2 guardrail: LLM-based intent classification.

Used only when Layer 1 (regex patterns) gives no match but the query might
still be advisory. Sends a simple prompt to Gemini asking for a one-word
classification: FACTUAL or ADVISORY.

This call is very fast and prevents subtle requests for advice from
reaching the RAG pipeline.
"""

import os
import logging
from google import genai
from google.genai import types as genai_types

logger = logging.getLogger(__name__)

CLASSIFICATION_PROMPT = """Classify this user query as exactly one of: FACTUAL or ADVISORY.
- FACTUAL: asks for specific data about a mutual fund (expense ratio, exit load, SIP amount, etc.)
- ADVISORY: asks for investment advice, recommendations, portfolio building, or comparisons

Respond with a single word only: FACTUAL or ADVISORY

Query: "{query}"
"""


def classify_intent(query: str, api_key: str = None) -> str:
    """
    Classify the user query as 'FACTUAL' or 'ADVISORY' using Gemini.
    Returns 'FACTUAL' by default on any API error to prevent blocking completely.
    """
    if not api_key:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            logger.warning("No API key for classifier. Defaulting to FACTUAL.")
            return "FACTUAL"

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=CLASSIFICATION_PROMPT.format(query=query),
            config=genai_types.GenerateContentConfig(
                temperature=0.0,
                max_output_tokens=5, # only need 1 word
            ),
        )
        result = response.text.strip().upper()
        
        # Strip any markdown punctuation just in case
        for char in ["*", "`", ".", "\n"]:
            result = result.replace(char, "")
            
        if "ADVISORY" in result:
            logger.info("LLM Classifier caught ADVISORY intent for query: %r", query)
            return "ADVISORY"
            
        return "FACTUAL"
        
    except Exception as e:
        logger.error("Classifier API error: %s. Defaulting to FACTUAL.", e)
        return "FACTUAL"
