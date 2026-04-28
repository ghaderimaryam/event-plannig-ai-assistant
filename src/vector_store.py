"""Build and load the Chroma vector store from the markdown knowledge base."""
from __future__ import annotations

import shutil
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config import CHUNK_OVERLAP, CHUNK_SIZE, COLLECTION_NAME, MODEL_EMBED


def _embeddings() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(model=MODEL_EMBED)


def build_vectorstore(kb_path: Path, chroma_path: Path, rebuild: bool = True) -> Chroma:
    """Read all .md files under `kb_path`, chunk them, embed, and persist to Chroma."""
    kb_path = Path(kb_path)
    chroma_path = Path(chroma_path)

    md_files = sorted(kb_path.glob("*.md"))
    print(f"Found {len(md_files)} markdown files")

    documents: list[Document] = []
    for filepath in md_files:
        text = filepath.read_text(encoding="utf-8")
        documents.append(
            Document(page_content=text, metadata={"source": filepath.stem})
        )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
    )
    chunks = splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunks")

    if rebuild and chroma_path.exists():
        shutil.rmtree(chroma_path)
        print("Cleared old vector store")

    vs = Chroma.from_documents(
        documents=chunks,
        embedding=_embeddings(),
        persist_directory=str(chroma_path),
        collection_name=COLLECTION_NAME,
    )
    print(f"Vector store ready with {vs._collection.count()} vectors")
    return vs


def load_vectorstore(chroma_path: Path) -> Chroma:
    """Open an existing persisted Chroma index without rebuilding."""
    return Chroma(
        persist_directory=str(chroma_path),
        embedding_function=_embeddings(),
        collection_name=COLLECTION_NAME,
    )
