"""
generator.py
------------
Calls the Gemini LLM API to generate a factual answer given a prompt.

Model:       gemini-1.5-flash  (upgrade to gemini-1.5-pro if quality is insufficient)
Temperature: 0.0               (deterministic — maximises factual accuracy)
Max tokens:  256               (enforces concise 3-sentence answers)
"""

import google.generativeai as genai
from config.settings import GEMINI_API_KEY

MODEL_NAME = "gemini-1.5-flash"


# ---------------------------------------------------------------------------
# TODO: Implement Gemini answer generator
# ---------------------------------------------------------------------------

class AnswerGenerator:
    """Generates answers using the Gemini LLM API."""

    def __init__(self):
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel(MODEL_NAME)

    def generate(self, prompt: str) -> str:
        """
        Send the prompt to Gemini and return the response text.
        Uses temperature=0.0 and max_output_tokens=256.
        """
        raise NotImplementedError
