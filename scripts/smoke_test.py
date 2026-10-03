"""
Smoke test: proves the two engines of RAG work on your machine.
  Part A: EMBEDDING  -> turns text into a vector (list of 384 numbers)
  Part B: LLM CALL   -> sends text to Claude, shows token counts and the effect of temperature
Run from the repo root:  python scripts/smoke_test.py
"""
import os
import numpy as np
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import anthropic

load_dotenv()  # reads ANTHROPIC_API_KEY and LLM_MODEL from .env

# ---------- Part A: embeddings ----------
# First run downloads the model (~130 MB) and caches it.
model = SentenceTransformer("BAAI/bge-small-en-v1.5")

sentences = [
    "customer churn rate",         # A
    "customer attrition",          # B: same meaning, different words
    "inventory turnover",          # C: different meaning
]
# normalize_embeddings=True makes every vector length 1,
# so dot product == cosine similarity (a number from -1 to 1).
vecs = model.encode(sentences, normalize_embeddings=True)

print("vector size:", len(vecs[0]))  # expect 384
print(f"sim(churn, attrition)  = {np.dot(vecs[0], vecs[1]):.3f}   <- should be HIGH")
print(f"sim(churn, inventory)  = {np.dot(vecs[0], vecs[2]):.3f}   <- should be LOWER")

# ---------- Part B: LLM call ----------
client = anthropic.Anthropic()  # picks up ANTHROPIC_API_KEY from env
question = "Define Net Revenue Retention in one sentence."

for temp in (0, 0, 1, 1):  # two runs at each temperature, so you can compare
    r = client.messages.create(
        model=os.environ["LLM_MODEL"],
        max_tokens=80,
        temperature=temp,
        messages=[{"role": "user", "content": question}],
    )
    print(f"\n[temp={temp}] in={r.usage.input_tokens} tok, out={r.usage.output_tokens} tok")
    print(r.content[0].text)
