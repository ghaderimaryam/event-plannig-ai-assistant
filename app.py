"""Launch the Event Planning AI Assistant chat UI.

Usage:
    python app.py

If the vector store does not exist yet, run `python build_index.py` first.
"""
from __future__ import annotations

from src import config
from src.chat_engine import build_chat_fn
from src.ui import launch_demo
from src.vector_store import load_vectorstore


def main() -> None:
    config.validate()

    if not config.CHROMA_PATH.exists():
        raise SystemExit(
            f"❌ No vector store found at {config.CHROMA_PATH}.\n"
            f"   Build it first:  python build_index.py"
        )

    vectorstore = load_vectorstore(config.CHROMA_PATH)
    chat_fn = build_chat_fn(vectorstore)
    launch_demo(chat_fn)


if __name__ == "__main__":
    main()
