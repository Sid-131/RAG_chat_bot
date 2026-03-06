"""
settings.py
-----------
Centralised application configuration.

All secrets are loaded from environment variables (via .env file in development).
Do NOT hardcode API keys here.

Usage:
    from config.settings import GEMINI_API_KEY, TOP_K, MIN_SIMILARITY
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# --- Gemini API ---
GEMINI_API_KEY: str = os.environ["GEMINI_API_KEY"]
EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "models/text-embedding-004")
LLM_MODEL: str = os.getenv("LLM_MODEL", "gemini-1.5-flash")
LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.0"))
LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "256"))

# --- Retrieval ---
TOP_K: int = int(os.getenv("TOP_K", "5"))
MIN_SIMILARITY: float = float(os.getenv("MIN_SIMILARITY", "0.65"))

# --- Paths ---
DATA_DIR: Path = Path(os.getenv("DATA_DIR", "data"))
RAW_DIR: Path = DATA_DIR / "raw"
CHUNKS_DIR: Path = DATA_DIR / "chunks"
EMBEDDINGS_DIR: Path = DATA_DIR / "embeddings"
CHROMA_DIR: Path = Path(os.getenv("CHROMA_DIR", "db/chroma"))
REGISTRY_DB: Path = Path(os.getenv("REGISTRY_DB", "db/registry.sqlite"))
