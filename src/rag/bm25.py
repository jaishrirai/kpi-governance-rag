"""
Step 1.6: BM25 keyword search over the same chunks that went into Chroma.

Why it exists: vector search matches meaning, so it can miss exact strings such as "KPI-014".
BM25 scores a chunk by the query words it contains:
  - a word that is RARE across all chunks counts a lot (kpi-014), a common one almost nothing (kpi)
  - repeating a word helps, but with diminishing returns
  - a match in a short chunk counts more than the same match in a long chunk

The tokenizer is the important part: it keeps "kpi-014" as ONE word.
There is nothing to store: the index is rebuilt from the chunk files in a fraction of a second.

Run from the repo root (PYTHONPATH=src, same as rag.index):
    python -m rag.bm25 --sanity                 # the 3 sanity queries on all variants
    python -m rag.bm25 --sanity --stem          # same, with the simple suffix stemmer
    python -m rag.bm25 --search "KPI-014" --variant v2
"""
import argparse
import re
from functools import lru_cache

from rag.index import SANITY_QUERIES, VARIANTS, clean_metadata, load_chunks

# Letters and digits, optionally joined by hyphens: "kpi-014" and "kpi-007-v1" stay whole.
TOKEN_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
SUFFIXES = ("ers", "ing", "ed", "er", "es", "s")


def tokenize(text):
    return TOKEN_RE.findall(text.lower())


def stem_word(word):
    """Very small suffix stripper so "owns", "owner" and "owned" all become "own".
    IDs (anything with a digit or hyphen) are left alone, and a stem is never shorter than 3 letters."""
    if "-" in word or any(ch.isdigit() for ch in word) or word.endswith("ss"):
        return word
    for suffix in SUFFIXES:
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            return word[: -len(suffix)]
    return word


def analyze(text, stem=False):
    tokens = tokenize(text)
    return [stem_word(t) for t in tokens] if stem else tokens


class Bm25Index:
    def __init__(self, chunks, stem=False):
        from rank_bm25 import BM25Okapi  # imported here so the module imports without the library

        self.chunks = chunks
        self.stem = stem
        self.bm25 = BM25Okapi([analyze(c["text"], stem) for c in chunks])

    def search(self, query, k=5, where=None):
        """Top k chunks for the query. where = metadata equality filter, e.g.
        {"certification": "Certified"} (same idea as the Chroma filter). Chunks with score 0
        (no query word in them) are dropped."""
        scores = self.bm25.get_scores(analyze(query, self.stem))
        ranked = sorted(zip(scores, self.chunks), key=lambda pair: pair[0], reverse=True)
        hits = []
        for score, chunk in ranked:
            if score <= 0:
                break
            meta = clean_metadata(chunk)
            if where and any(meta.get(key) != value for key, value in where.items()):
                continue
            hits.append(
                {
                    "chunk_id": chunk["chunk_id"],
                    "doc_id": chunk["doc_id"],
                    "section": meta.get("section", ""),
                    "certification": meta.get("certification", ""),
                    "score": float(score),
                    "text": chunk["text"],
                }
            )
            if len(hits) == k:
                break
        return hits


@lru_cache(maxsize=None)
def build_index(variant, stem=False):
    return Bm25Index(load_chunks(variant), stem)


def bm25_search(variant, query, k=5, where=None, stem=False):
    return build_index(variant, stem).search(query, k=k, where=where)


def print_hits(variant, query, hits, top=3):
    print(f"\n[{variant}] {query!r}")
    if not hits:
        print("  (no chunk contains any query word)")
    for rank, h in enumerate(hits[:top], start=1):
        preview = h["text"].replace("\n", " ")[:70]
        print(f"  {rank}. {h['score']:6.2f}  {h['chunk_id']:<22} {h['certification']:<11} {preview}")


def main():
    parser = argparse.ArgumentParser(description="BM25 keyword search over the chunk files.")
    parser.add_argument("--variant", choices=VARIANTS + ["all"], default="all")
    parser.add_argument("--sanity", action="store_true", help="run the 3 sanity queries")
    parser.add_argument("--search", help="run one query")
    parser.add_argument("--stem", action="store_true", help="use the simple suffix stemmer")
    args = parser.parse_args()
    if not (args.sanity or args.search):
        parser.error("give --sanity or --search")
    variants = VARIANTS if args.variant == "all" else [args.variant]
    queries = SANITY_QUERIES if args.sanity else [args.search]
    print(f"BM25, stemming {'ON' if args.stem else 'OFF'}")
    for query in queries:
        for variant in variants:
            print_hits(variant, query, bm25_search(variant, query, stem=args.stem))


if __name__ == "__main__":
    main()
