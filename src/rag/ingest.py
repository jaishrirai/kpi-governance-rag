"""
Loaders: turn every source file into one common shape and write data/processed/documents.jsonl.
One line per document: the 9 manifest fields + "text".
PDFs are normalised so the chunker can treat every source the same way:
  - headings become Markdown lines ("# " for the title, "## " for a section)
  - each table row becomes one labelled line: "ID: KPI-001 | Owner: ... | Status: ..."
Run from the repo root:  PYTHONPATH=src python -m rag.ingest
"""
import csv
import json
import sys
from collections import Counter
from pathlib import Path

import pdfplumber

MANIFEST = Path("data/corpus_manifest.csv")
OUT = Path("data/processed/documents.jsonl")


def read_csv(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def load_markdown(path):
    # Drop the YAML header: metadata comes from the manifest, so the text is body only
    return Path(path).read_text(encoding="utf-8").split("---", 2)[2].strip()


# Tuned to our generated PDFs (title 18pt bold, section headings 14pt bold, body 10pt).
# A production loader would use a layout-aware parser or a managed service such as Textract.
TITLE_MIN_SIZE = 16
HEADING_MIN_SIZE = 12
PARAGRAPH_GAP = 3  # points of blank space between two lines that starts a new paragraph


def pdf_heading_prefix(line):
    """'# ' for the title, '## ' for a section heading, '' for body text (uses font size and bold)."""
    first = line["chars"][0]
    if "Bold" in first["fontname"]:
        if first["size"] >= TITLE_MIN_SIZE:
            return "# "
        if first["size"] >= HEADING_MIN_SIZE:
            return "## "
    return ""


def table_rows_as_lines(table):
    """The first row holds the column names. Every later row becomes 'Name: value | Name: value'."""
    clean = lambda cell: " ".join((cell or "").split())  # joins text that wrapped inside a cell
    header = [clean(c) for c in table[0]]
    lines = []
    for row in table[1:]:
        pairs = [f"{h}: {clean(c)}" for h, c in zip(header, row) if clean(c)]
        if pairs:
            lines.append(" | ".join(pairs))
    return "\n".join(lines)


def pdf_page_text(page):
    """Read one page top to bottom: headings, paragraphs and tables, in their original order."""
    tables = page.find_tables()
    items = [(t.bbox[1], "table", t.extract()) for t in tables]
    for line in page.extract_text_lines():
        in_table = any(t.bbox[1] <= line["top"] and line["bottom"] <= t.bbox[3] for t in tables)
        if not in_table:  # the table reader already has these words
            items.append((line["top"], "line", line))

    blocks, paragraph, last_bottom, last_was_title = [], [], None, False

    def end_paragraph():
        if paragraph:
            blocks.append(" ".join(paragraph))
            paragraph.clear()

    for _, kind, item in sorted(items, key=lambda i: i[0]):
        if kind == "table":
            end_paragraph()
            blocks.append(table_rows_as_lines(item))
            last_bottom, last_was_title = None, False
            continue
        prefix = pdf_heading_prefix(item)
        if prefix or (last_bottom is not None and item["top"] - last_bottom > PARAGRAPH_GAP):
            end_paragraph()
        if prefix == "# " and last_was_title:
            blocks[-1] += " " + item["text"]  # a title that wraps onto a second line
        elif prefix:
            blocks.append(prefix + item["text"])
        else:
            paragraph.append(item["text"])
        last_bottom, last_was_title = item["bottom"], prefix == "# "
    end_paragraph()
    return "\n\n".join(b for b in blocks if b)


def load_pdf(path):
    # Pages are joined with a blank line; page numbers are not kept (limit: citations are per document)
    with pdfplumber.open(path) as pdf:
        return "\n\n".join(pdf_page_text(page) for page in pdf.pages).strip()


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
