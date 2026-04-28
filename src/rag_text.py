"""Convert structured vendor rows into RAG-friendly prose paragraphs."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional

import pandas as pd
from openai import OpenAI
from tqdm.auto import tqdm

from src.config import MAX_WORKERS, MODEL_GEN

_PROMPT_TEMPLATE = """You are a technical writer converting structured data into clean, semantic text for a RAG (Retrieval-Augmented Generation) system.
Given this data record:
{row_data}
Write 2-3 paragraphs concise but informative paragraph that:
- Includes all important fields naturally in flowing prose
- Elaborates on key fields with context where useful
- Avoids repetition and filler phrases
- Is self-contained and factually complete
- Uses clear, embedding-friendly language (no markdown, no bullet points)
- Reads as a factual description, not a list
Output only the paragraph, nothing else."""

_client: Optional[OpenAI] = None


def _get_client() -> OpenAI:
    """Lazy singleton — avoids constructing an OpenAI client at import time."""
    global _client
    if _client is None:
        _client = OpenAI()
    return _client


def row_to_rag_text(row: dict) -> str:
    """Turn one row dict into a single coherent paragraph using the LLM."""
    row_data = "\n".join(f"- {k}: {v}" for k, v in row.items() if pd.notna(v))
    response = _get_client().chat.completions.create(
        model=MODEL_GEN,
        messages=[{"role": "user", "content": _PROMPT_TEMPLATE.format(row_data=row_data)}],
        temperature=0.2,
        max_tokens=600,
    )
    return response.choices[0].message.content.strip()


def generate_rag_texts(df: pd.DataFrame, max_workers: int = MAX_WORKERS) -> list[str]:
    """Generate RAG paragraphs for every row of `df` in parallel. Order preserved."""
    rows = [r.to_dict() for _, r in df.iterrows()]
    results: list[Optional[str]] = [None] * len(rows)

    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = {ex.submit(row_to_rag_text, row): i for i, row in enumerate(rows)}
        for fut in tqdm(as_completed(futures), total=len(rows), desc="Generating RAG text"):
            i = futures[fut]
            try:
                results[i] = fut.result()
            except Exception as e:  # noqa: BLE001 — log & continue, never kill the run
                print(f"⚠️  Row {i} failed: {e}")
                results[i] = ""
    return results  # type: ignore[return-value]
