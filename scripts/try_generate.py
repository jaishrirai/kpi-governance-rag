"""
Review script for Step 2.5 (not the pipeline): vector V1 top 5 -> generate() -> print.

Makes ONE real Gemini call per question. Prints the context labels, the structured answer,
tokens and latency. No scoring, no citation checks, no logging. Run from the repo root:
  $env:PYTHONPATH = "src"
  python scripts/try_generate.py "Customer churn rate - how is that calculated?"
  python scripts/try_generate.py "Who is the CEO of Kestrel Retail Group?"
"""
import sys

import chromadb

from rag import generate, index

VARIANT, K = "v1", 5


def main():
    if len(sys.argv) < 2:
        sys.exit('usage: python scripts/try_generate.py "your question"')
    question = " ".join(sys.argv[1:])
    client = chromadb.PersistentClient(path="data/index")
    embed = index.make_embedder(index.load_model())
    hits = index.search(client, VARIANT, question, embed, k=K)
    print("Retrieved:", [h["chunk_id"] for h in hits])
    result = generate.generate(question, hits)
    print(f"\nrefused:   {result.refused}")
    print(f"answer:    {result.answer}")
    print(f"citations: {result.citations}")
    print(f"model={result.model} prompt={result.prompt_version} in={result.input_tokens} "
          f"out={result.output_tokens} thinking={result.thinking_tokens} latency={result.latency_ms:.0f} ms")


if __name__ == "__main__":
    main()
