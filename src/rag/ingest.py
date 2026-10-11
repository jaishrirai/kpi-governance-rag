"""
Loaders: turn every source file into one common shape and write data/processed/documents.jsonl.
One line per document: the 9 manifest fields + "text".
Run from the repo root:  PYTHONPATH=src python -m rag.ingest
"""
import csv
import json
import sys
from collections import Counter
from pathlib import Path

from pypdf import PdfReader

MANIFEST = Path("data/corpus_manifest.csv")
OUT = Path("data/processed/documents.jsonl")


def read_csv(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def load_markdown(path):
    # Drop the YAML header: metadata comes from the manifest, so the text is body only
    return Path(path).read_text(encoding="utf-8").split("---", 2)[2].strip()


def load_pdf(path):
    # Pages are joined with a blank line; page numbers are not kept (limit: citations are per document)
    return "\n\n".join(page.extract_text() for page in PdfReader(path).pages).strip()


def catalog_texts(path):
    # One catalog row = one document. "key: value" lines keep the row readable as free text
    return {
        r["asset_id"]: (
            f"{r['name']} ({r['asset_type']})\n"
            f"Description: {r['description']}\n"
            f"Refresh: {r['refresh']}\n"
            f"Linked KPIs: {r['linked_kpis'].replace(';', ', ')}"
        )
        for r in read_csv(path)
    }


def load_all():
    catalog = catalog_texts("data/raw/catalog/data_catalog.csv")
    docs = []
    for row in read_csv(MANIFEST):
        suffix = Path(row["source_path"]).suffix
        if row["doc_type"] == "catalog":
            text = catalog[row["doc_id"]]
        elif suffix == ".pdf":
            text = load_pdf(row["source_path"])
        else:
            text = load_markdown(row["source_path"])
        docs.append({**row, "text": text})
    return docs


def main():
    sys.stdout.reconfigure(encoding="utf-8")  # Windows console default cannot print every character
    docs = load_all()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        for d in docs:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")

    print(f"Wrote {len(docs)} documents to {OUT}")
    counts = Counter(d["doc_type"] for d in docs)
    for doc_type, n in counts.items():
        sizes = [len(d["text"]) for d in docs if d["doc_type"] == doc_type]
        print(f"  {doc_type:8} {n:3} docs, chars min {min(sizes)} / max {max(sizes)}")
    empty = [d["doc_id"] for d in docs if len(d["text"]) < 50]
    print("Empty or tiny texts:", empty or "none")


if __name__ == "__main__":
    main()
