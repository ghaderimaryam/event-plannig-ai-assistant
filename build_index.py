"""Build the vendor knowledge base and vector store from the source CSV.

Usage:
    python build_index.py
"""
from __future__ import annotations

import json

import pandas as pd

from src import config
from src.knowledge_base import save_markdown_files
from src.rag_text import generate_rag_texts
from src.vector_store import build_vectorstore


def main() -> None:
    config.validate()

    if not config.CSV_PATH.exists():
        raise FileNotFoundError(
            f"CSV not found at {config.CSV_PATH}. "
            f"Place your vendor CSV there or override CSV_PATH in .env."
        )

    df = pd.read_csv(config.CSV_PATH)
    print(f"Loaded {len(df)} rows from {config.CSV_PATH}")

    config.DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Cache: reuse generated paragraphs if the row count still matches.
    if config.RAG_CACHE_CSV.exists():
        cached = pd.read_csv(config.RAG_CACHE_CSV)
        if len(cached) == len(df) and "rag_text" in cached.columns:
            print(f"♻️  Reusing cached rag_text from {config.RAG_CACHE_CSV}")
            df["rag_text"] = cached["rag_text"].values
        else:
            df["rag_text"] = generate_rag_texts(df)
    else:
        df["rag_text"] = generate_rag_texts(df)

    # Persist intermediate artifacts.
    df[["rag_text"]].to_csv(config.RAG_CACHE_CSV, index=False)
    config.CHUNKS_JSON.write_text(json.dumps(df["rag_text"].tolist(), indent=2))

    # Markdown knowledge base.
    save_markdown_files(df, base_path=config.KB_PATH, name_column=config.NAME_COLUMN)

    # Vector store.
    build_vectorstore(config.KB_PATH, config.CHROMA_PATH, rebuild=True)
    print("\n✅ Index build complete. Run `python app.py` to launch the chat UI.")


if __name__ == "__main__":
    main()
