# Concepts log

Template (5 lines each):
1. What it is (my words):
2. Example from P1:
3. Why it matters for P1:
4. LangChain / industry name:
5. My interview line:
AWS AIF-C01 domain:

---

## Token + Context window (Step 1.1)
1. What it is: a token is the unit an LLM reads and bills by, about 4 characters. The context window is the max tokens per call (prompt + answer).
2. Example from P1: we estimate chunk size as chars / 4; a 1,800-char KPI file is about 450 tokens.
3. Why it matters: we can't paste all 50 docs into every call, so we retrieve only the few relevant chunks.
4. Industry name: "context length", "token budget".
5. Interview line: "RAG keeps the prompt small and focused, which cuts cost and stops the model from missing the one relevant line."
AWS AIF-C01 domain: 2 (Fundamentals of Generative AI)

## Temperature (Step 1.1)
1. What it is: how random the model's word choice is. 0 means less randomness, so answers stay very similar across runs (near-deterministic, not guaranteed).
2. Example from P1: answers use temperature 0 so "How is Churn Rate defined?" gives the same definition every time.
3. Why it matters: a governance assistant must be consistent; creativity is a risk here.
4. Industry name: inference parameter (with top_p, top_k).
5. Interview line: "I use temperature 0 for factual, cited answers and higher values only for creative tasks like drafting variations."
AWS AIF-C01 domain: 3 (Applications of Foundation Models, inference parameters)

## Embedding + Cosine similarity (Step 1.1)
1. What it is: an embedding model turns text into a vector (384 numbers for bge-small). Cosine similarity compares two vectors by angle; with normalized vectors (length 1) it is just the dot product, so the denominator is skipped.
2. Example from P1: churn vs attrition = 0.777, churn vs inventory = 0.664.
3. Why it matters: bge scores sit in a narrow band, so a fixed cutoff like 0.7 can drop relevant chunks. Rank, rerank, then drop.
4. Industry name: dense retrieval, semantic search, bi-encoder.
5. Interview line: "Similarity scores are for ranking, not yes/no decisions; I retrieve wide, rerank, then keep the top 5."
AWS AIF-C01 domain: 2 (Fundamentals of Generative AI), 3 (vector stores for RAG)

## Secrets and Git (Day 0)
1. What it is: commit = local snapshot with a message; push = upload commits to GitHub. .gitignore stops git from tracking .env.
2. Example from P1: git ls-files shows only .env.example, never .env.
3. Why it matters: bots scan GitHub for keys within minutes.
4. Industry name: secrets management (AWS Secrets Manager, Parameter Store).
5. Interview line: "If a key leaks, revoke it first, then clean history; deleting the file is not enough."
AWS AIF-C01 domain: 5 (Security, Compliance, and Governance)
