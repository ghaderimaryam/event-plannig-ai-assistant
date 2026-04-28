"""Project configuration. Loads from environment / .env file."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# ─── Paths ─────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR      = Path(os.getenv("DATA_DIR",      str(PROJECT_ROOT / "data")))
CSV_PATH      = Path(os.getenv("CSV_PATH",      str(DATA_DIR / "vendors.csv")))
KB_PATH       = Path(os.getenv("KB_PATH",       str(DATA_DIR / "knowledge_base")))
CHROMA_PATH   = Path(os.getenv("CHROMA_PATH",   str(DATA_DIR / "chroma_db")))
RAG_CACHE_CSV = Path(os.getenv("RAG_CACHE_CSV", str(DATA_DIR / "rag_ready.csv")))
CHUNKS_JSON   = Path(os.getenv("CHUNKS_JSON",   str(DATA_DIR / "chunks.json")))

# ─── Models ────────────────────────────────────────────────────────────────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_GEN      = os.getenv("MODEL_GEN", "gpt-4o-mini")
MODEL_EMBED    = os.getenv("MODEL_EMBED", "text-embedding-3-small")

# ─── Behavior ──────────────────────────────────────────────────────────────
NAME_COLUMN     = os.getenv("NAME_COLUMN", "vendor_name")
MAX_WORKERS     = int(os.getenv("MAX_WORKERS", "8"))
COLLECTION_NAME = "vendors"
CHUNK_SIZE      = 1000
CHUNK_OVERLAP   = 200
TOP_K           = 5


def validate() -> None:
    """Fail fast if critical config is missing."""
    if not OPENAI_API_KEY:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Copy .env.example to .env and add your key."
        )
