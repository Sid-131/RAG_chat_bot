"""
document_registry.py
---------------------
SQLite-backed registry that tracks every chunk that has been indexed.

Table: documents
  chunk_id    TEXT PRIMARY KEY
  source_url  TEXT
  scraped_at  TEXT
  vector_id   TEXT
  indexed_at  TEXT

Enables incremental re-indexing: if a source page is re-scraped, only
chunks with a newer scraped_at timestamp are re-embedded and re-indexed.
"""

import sqlite3
from pathlib import Path
from typing import Optional

DB_PATH = Path("db/registry.sqlite")


# ---------------------------------------------------------------------------
# TODO: Implement document registry
# ---------------------------------------------------------------------------

class DocumentRegistry:
    """Manages the SQLite document registry."""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        """Create the documents table if it does not exist."""
        raise NotImplementedError

    def register(self, chunk_id: str, source_url: str, scraped_at: str, vector_id: str) -> None:
        """Insert or update a chunk record."""
        raise NotImplementedError

    def exists(self, chunk_id: str) -> bool:
        """Return True if a chunk is already indexed."""
        raise NotImplementedError

    def get_all(self) -> list[dict]:
        """Return all registered chunks."""
        raise NotImplementedError
