"""
Smoke test: proves the two engines of RAG work on your machine.
  Part A: EMBEDDING  -> turns text into a vector (list of 384 numbers)
  Part B: LLM CALL   -> added at Step 2.5 (Gemini)
Run from the repo root:  python scripts/smoke_test.py
"""
import os
import numpy as np
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()  # reads GEMINI_API_KEY and LLM_MODEL from .env (used from Step 2.5)

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
# Added at Step 2.5 (Gemini free tier). Not needed for retrieval work.
