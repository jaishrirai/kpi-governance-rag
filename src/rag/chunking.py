"""
Chunking: cut each document into pieces the embedding model can read.

Three variants (PLAN.md step 1.4):
  v1 fixed:      windows of about 400 tokens with 60 tokens of overlap, cut at line breaks or spaces
  v2 by heading: one chunk per '## ' section; a section over the cap is split again
  v3 by unit:    one chunk per document; if it is over the cap, it is split again

Every chunk's text starts with "{title} | {section}" so the title and section are never lost.
The 450-token cap is measured on that header plus the body, because the header is embedded too.

Run from the repo root:  PYTHONPATH=src python -m rag.chunking
"""
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

DOCS_PATH = Path("data/processed/documents.jsonl")
CHARS_PER_TOKEN = 4  # rough rule: 1 token is about 4 characters of English
FIXED_TOKENS = 400
OVERLAP_TOKENS = 60
CAP_TOKENS = 450

# Fields copied from each document onto its chunks. Chroma accepts only str, int, float or bool values.
META_FIELDS = ["title", "doc_type", "domain", "owner", "certification",
               "version", "effective_date", "source_path"]


@dataclass
class Chunk:
    chunk_id: str  # doc_id::variant::n, for example KPI-010::v2::3
    doc_id: str
    variant: str
    section: str
    text: str  # header + body: this is what gets embedded
    metadata: dict = field(default_factory=dict)


def estimate_tokens(text):
    return len(text) // CHARS_PER_TOKEN


def cut_point(text, start, end):
    """Best place to cut text[start:end]: the last line break, otherwise the last space.
    Cutting at a line break keeps a table row (one line) whole."""
    for separator in ("\n", " "):
        i = text.rfind(separator, start, end)
        if i > start:
            return i
    return end


def restart_point(text, from_pos, end):
    """Where the next piece starts: just after the first line break (or space) at or after from_pos."""
    for separator in ("\n", " "):
        i = text.find(separator, from_pos, end)
        if i != -1:
            return i + 1
    return end


def split_text(text, max_chars, overlap_chars):
    """Cut text into pieces of at most max_chars, cutting at line breaks first, then spaces.
    Each piece starts again about overlap_chars before the end of the previous one."""
    pieces = []
    start = 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        if end < len(text):
            end = cut_point(text, start, end)
        piece = text[start:end].strip()
        if piece:
            pieces.append(piece)
        if end >= len(text):
            break
        next_start = restart_point(text, end - overlap_chars, end)
        start = next_start if next_start > start else end  # always move forward
    return pieces


def split_sections(body):
    """Split Markdown at '## ' headings. Returns (heading, text) pairs.
    The '# ' title line is dropped because the header already carries the title."""
    sections = []
    heading = "intro"
    buffer = []

    def flush():
        text = "\n".join(l for l in buffer if not l.startswith("# ")).strip()
        if text:
            sections.append((heading, text))

    for line in body.splitlines():
        if line.startswith("## "):
            flush()
            heading = line[3:].strip()
            buffer = []
        else:
            buffer.append(line)
    flush()
    return sections


def make_chunk(doc, variant, n, section, body):
    header = f"{doc['title']} | {section}\n"
    return Chunk(
        chunk_id=f"{doc['doc_id']}::{variant}::{n}",
        doc_id=doc["doc_id"],
        variant=variant,
        section=section,
        text=header + body,
        metadata={**{k: doc[k] for k in META_FIELDS}, "section": section, "variant": variant},
    )


def pieces_for_section(doc, section, body):
    """Return the body as one piece if header + body fits the cap, otherwise split it."""
    header = f"{doc['title']} | {section}\n"
    if estimate_tokens(header + body) <= CAP_TOKENS:
        return [body]
    max_chars = CAP_TOKENS * CHARS_PER_TOKEN - len(header)
    return split_text(body, max_chars, OVERLAP_TOKENS * CHARS_PER_TOKEN)


def v1_fixed(doc):
    pieces = split_text(doc["text"], FIXED_TOKENS * CHARS_PER_TOKEN, OVERLAP_TOKENS * CHARS_PER_TOKEN)
    return [make_chunk(doc, "v1", n, f"part {n + 1}", p) for n, p in enumerate(pieces)]


def v2_by_heading(doc):
    chunks = []
    for section, body in split_sections(doc["text"]):
        for piece in pieces_for_section(doc, section, body):
            chunks.append(make_chunk(doc, "v2", len(chunks), section, piece))
    return chunks


def v3_by_unit(doc):
    pieces = pieces_for_section(doc, "full document", doc["text"])
    return [make_chunk(doc, "v3", n, "full document", p) for n, p in enumerate(pieces)]


VARIANTS = {"v1": v1_fixed, "v2": v2_by_heading, "v3": v3_by_unit}


def load_docs(path=DOCS_PATH):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def build_all(docs):
    return {variant: [c for d in docs for c in fn(d)] for variant, fn in VARIANTS.items()}


def main():
    chunks_by_variant = build_all(load_docs())
    print(f"{'variant':<8}{'chunks':>8}{'avg tok':>10}{'max tok':>10}")
    for variant, chunks in chunks_by_variant.items():
        tokens = [estimate_tokens(c.text) for c in chunks]
        print(f"{variant:<8}{len(chunks):>8}{sum(tokens) / len(tokens):>10.0f}{max(tokens):>10}")
        out = Path(f"data/processed/chunks_{variant}.jsonl")
        with open(out, "w", encoding="utf-8") as f:
            for c in chunks:
                f.write(json.dumps(asdict(c), ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
