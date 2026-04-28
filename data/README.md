# `data/` directory

Runtime artifacts live here. Everything in this folder is **gitignored** except this README and `.gitkeep`.

## Expected layout after running the pipeline

```
data/
├── vendors.csv          # ← you provide this (the source vendor catalog)
├── rag_ready.csv        # generated: cached LLM-rewritten paragraphs
├── chunks.json          # generated: same content as JSON
├── knowledge_base/      # generated: one .md file per vendor
│   ├── Vendor_A.md
│   └── ...
└── chroma_db/           # generated: persisted Chroma vector index
```

## Required input

Drop your `vendors.csv` in this folder, or point the pipeline at a different file via `CSV_PATH` in `.env`.

The CSV can have any columns — the pipeline reads them all dynamically. The column name used to label files is set by `NAME_COLUMN` (defaults to `vendor_name`).
