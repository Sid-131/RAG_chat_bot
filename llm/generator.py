"""
generator.py
------------
Calls the Gemini LLM API to generate a factual answer given a prompt.

SDK:         google.genai
Model:       gemini-1.5-flash
Temperature: 0.0               (deterministic — maximises factual accuracy and grounding)
Max tokens:  256               (enforces concise answers)
"""

import os
import logging
from google import genai
from google.genai import types as genai_types

logger = logging.getLogger(__name__)

MODEL_NAME = "gemini-2.5-flash"


class AnswerGenerator:
    """Generates answers using the Gemini LLM API (google.genai SDK)."""

    def __init__(self, api_key: str = None):
        if not api_key:
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY must be provided or set in environment.")
                
        self._client = genai.Client(api_key=api_key)
        logger.info("AnswerGenerator initialised with model %s", MODEL_NAME)

    def generate(self, prompt: str) -> str:
        """
        Send the full prompt to Gemini and return the generated text.
        Configured for RAG: low temperature to reduce hallucination.

        Args:
            prompt: The full assembled prompt string.

        Returns:
            The generated answer string.
        """
        logger.debug("Calling Gemini API...")
        
        # Configure model behavior for factual RAG
        config = genai_types.GenerateContentConfig(
            temperature=0.0,
            max_output_tokens=256,
        )

        response = self._client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=config,
        )

        answer = response.text
        logger.info("Generated answer (%d chars)", len(answer))
        return answer
