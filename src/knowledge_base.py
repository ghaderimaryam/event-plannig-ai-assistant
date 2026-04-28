"""Write one markdown document per vendor record."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd

from src.config import NAME_COLUMN


def sanitize_filename(name: str) -> str:
    """Make a string safe for use as a filename across OSes."""
    return "".join(
        c if c.isalnum() or c in (" ", "-", "_") else "_" for c in str(name)
    ).strip()


def row_to_markdown(row: dict, rag_text: str) -> str:
    """Render a row + its RAG paragraph as a complete markdown document."""
    title = (
        row.get("name")
        or row.get("title")
        or row.get(NAME_COLUMN)
        or row.get("id")
        or "Record"
    )
    lines = [f"# {title}", "", "## Summary", "", rag_text, "", "## Raw Fields", ""]
    for key, value in row.items():
        if pd.notna(value):
            lines.append(f"- **{key}**: {value}")
    return "\n".join(lines)


def save_markdown_files(
    df: pd.DataFrame,
    base_path: Path,
    name_column: Optional[str] = None,
) -> None:
    """Write one .md file per dataframe row. Handles filename collisions."""
    base_path = Path(base_path)
    base_path.mkdir(parents=True, exist_ok=True)
    seen: dict[str, int] = {}

    for i, row in df.iterrows():
        row_dict = row.to_dict()
        rag_text = row_dict.pop("rag_text", "")

        if name_column and name_column in row_dict and pd.notna(row_dict[name_column]):
            base = sanitize_filename(str(row_dict[name_column]))
        else:
            base = f"record_{i:03d}"

        # If two rows sanitize to the same name, suffix with a counter.
        count = seen.get(base, 0)
        seen[base] = count + 1
        filename = f"{base}.md" if count == 0 else f"{base}_{count}.md"

        (base_path / filename).write_text(
            row_to_markdown(row_dict, rag_text), encoding="utf-8"
        )

    print(f"✅ Saved {len(df)} markdown files to: {base_path}")
