"""
Step 1.5: embed every chunk and store it in Chroma, one collection per chunking variant.

Pipeline position:  chunks_{v}.jsonl  ->  embed (bge-small, 384 numbers)  ->  Chroma kpi_{v}

Why three separate collections: V1, V2 and V3 are alternative experiments. If they shared one
collection, a search would mix chunks from different strategies and we could not tell which
strategy produced a good or bad result.

Run from the repo root:
    python -m rag.index --variant all          # build (or rebuild) the three collections
    python -m rag.index --sanity               # run the 3 sanity queries on all variants
    python -m rag.index --search "your question" --variant v2
"""
import argparse
import json
from pathlib import Path

CHUNKS_DIR = Path("data/processed")
INDEX_DIR = Path("data/index")  # git-ignored; rebuilt from chunks at any time
MODEL_NAME = "BAAI/bge-small-en-v1.5"
MODEL_TOKEN_LIMIT = 512  # bge-small cuts off anything longer, silently
BATCH_SIZE = 32
VARIANTS = ["v1", "v2", "v3"]

SANITY_QUERIES = [
    "how is churn calculated",
    "KPI-014",
    "who owns the customer 360 dashboard",
]


def collection_name(variant):
    return f"kpi_{variant}"


def load_chunks(variant, chunks_dir=CHUNKS_DIR):
    path = Path(chunks_dir) / f"chunks_{variant}.jsonl"
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def clean_metadata(chunk):
    """Chroma accepts only str, int, float and bool as metadata values.
    None values are dropped (Chroma rejects them); anything else becomes a string."""
    clean = {"doc_id": chunk["doc_id"]}
    for key, value in chunk["metadata"].items():
        if value is None:
            continue
        clean[key] = value if isinstance(value, (str, int, float, bool)) else str(value)
    return clean


def load_model():
    # Imported here so tests and other modules do not need torch just to import this file.
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(MODEL_NAME)


def make_embedder(model):
    """Wrap the model as embed(list_of_texts) -> list_of_vectors.
    normalize_embeddings=True makes every vector length 1, so dot product = cosine similarity."""

    def embed(texts):
        return model.encode(texts, normalize_embeddings=True, batch_size=BATCH_SIZE).tolist()

    return embed


def count_over_limit(texts, count_tokens, limit=MODEL_TOKEN_LIMIT):
    """How many texts are longer than the model limit (the model would silently cut their end).
    count_tokens is a function text -> number of real tokens."""
    return [i for i, text in enumerate(texts) if count_tokens(text) > limit]


def build_collection(client, variant, chunks, embed_fn):
    """Create kpi_{variant} from scratch: embed in batches and add text, vector and metadata."""
    name = collection_name(variant)
    try:
        client.delete_collection(name)  # rebuild from scratch so reruns never duplicate chunks
    except Exception:
        pass  # collection did not exist yet (the exception type differs between Chroma versions)
    # hnsw:space=cosine -> Chroma reports distance = 1 - cosine similarity (0 = identical)
    collection = client.create_collection(name=name, metadata={"hnsw:space": "cosine"})
    for start in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[start : start + BATCH_SIZE]
        texts = [c["text"] for c in batch]
        collection.add(
            ids=[c["chunk_id"] for c in batch],
            documents=texts,
            embeddings=embed_fn(texts),
            metadatas=[clean_metadata(c) for c in batch],
        )
    return collection


def search(client, variant, query, embed_fn, k=5, where=None):
    """Embed the query the same way as the chunks and return the k nearest chunks.
    where = optional metadata filter, e.g. {"certification": "Certified"}."""
    collection = client.get_collection(collection_name(variant))
    result = collection.query(
        query_embeddings=embed_fn([query]),
        n_results=k,
        where=where,
        include=["documents", "metadatas", "distances"],
    )
    hits = []
    for chunk_id, text, meta, dist in zip(
        result["ids"][0], result["documents"][0], result["metadatas"][0], result["distances"][0]
    ):
        hits.append(
            {
                "chunk_id": chunk_id,
                "doc_id": meta["doc_id"],
                "section": meta.get("section", ""),
                "certification": meta.get("certification", ""),
                "similarity": 1 - dist,  # distance -> similarity
                "text": text,
            }
        )
    return hits


def print_hits(variant, query, hits, top=3):
    print(f"\n[{variant}] {query!r}")
    for rank, h in enumerate(hits[:top], start=1):
        preview = h["text"].replace("\n", " ")[:70]
        print(f"  {rank}. {h['similarity']:.3f}  {h['chunk_id']:<22} {h['certification']:<11} {preview}")


def main():
    import chromadb

    parser = argparse.ArgumentParser(description="Build or query the Chroma index.")
    parser.add_argument("--variant", choices=VARIANTS + ["all"], default="all")
    parser.add_argument("--sanity", action="store_true", help="run the 3 sanity queries, no rebuild")
    parser.add_argument("--search", help="run one query, no rebuild")
    args = parser.parse_args()
    variants = VARIANTS if args.variant == "all" else [args.variant]

    print(f"Loading {MODEL_NAME} ...")
    model = load_model()
    embed_fn = make_embedder(model)
    client = chromadb.PersistentClient(path=str(INDEX_DIR))

    if args.sanity or args.search:
        queries = SANITY_QUERIES if args.sanity else [args.search]
        for query in queries:
            for variant in variants:
                print_hits(variant, query, search(client, variant, query, embed_fn))
        return

    def real_tokens(text):
        return len(model.tokenizer(text)["input_ids"])

    print(f"{'variant':<8}{'chunks':>8}{'stored':>8}{'over 512 tok':>14}")
    for variant in variants:
        chunks = load_chunks(variant)
        too_long = count_over_limit([c["text"] for c in chunks], real_tokens)
        collection = build_collection(client, variant, chunks, embed_fn)
        print(f"{variant:<8}{len(chunks):>8}{collection.count():>8}{len(too_long):>14}")


if __name__ == "__main__":
    main()
