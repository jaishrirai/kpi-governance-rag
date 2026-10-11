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

## Hallucination + consistency checks (Step 1.2)
1. What it is: when a model states something confident that is not supported by the documents. A RAG assistant can also repeat a wrong fact that is in its own documents.
2. Example from P1: the FAQ says Active Customer is 90 days, the certified KPI-006 says 30. check_corpus.py checks owners, versions and links so the documents do not contradict each other by accident.
3. Why it matters: if the corpus disagrees with itself, a wrong answer would look like a retrieval bug.
4. Industry name: grounding, data quality checks, source of truth.
5. Interview line: "Before tuning retrieval I validated the corpus, because inconsistent sources make good retrieval return bad answers."
AWS AIF-C01 domain: 2 (Fundamentals of Generative AI, hallucination), 5 (Governance)

## Structured output + single source of truth + lineage (Step 1.2)
1. What it is: data in a fixed shape (YAML header, CSV, JSON) so code can read it. A single source of truth means one place owns a fact and everything else reads from it.
2. Example from P1: version: "1.4" is quoted so YAML keeps it as text (1.10 would become 1.1 as a number). The POL-04 PDF reads owner and status from the manifest, so they cannot disagree. The checker also verifies KPI to dashboard links in both directions, a small lineage graph.
3. Why it matters: metadata is used later for filters (domain, certification) and for citations, so it must be exact.
4. Industry name: schema, metadata filtering, data contract, data lineage.
5. Interview line: "I kept metadata in one manifest, generated dependent documents from it, and checked KPI to dashboard lineage both ways, so filters and citations are reliable."
AWS AIF-C01 domain: 2 (Fundamentals of Generative AI), 5 (Governance)

## Document loaders + PDF extraction (Step 1.3)
1. What it is: code that reads each file format and turns it into one common shape (metadata + text), so later steps handle one format.
2. Example from P1: ingest.py loads markdown, CSV rows and PDFs into documents.jsonl. In POL-03, pypdf puts each table cell on its own line, so a value can sit next to the wrong label.
3. Why it matters: parsing errors are silent. The answer looks cited but maps the wrong cell, and retrieval metrics will not show it.
4. Industry name: document loaders, parsing/ingestion (Textract or Bedrock Knowledge Bases parsing on AWS).
5. Interview line: "I checked PDF table extraction first, because flattened tables break answers without any error."
AWS AIF-C01 domain: 3 (Applications of Foundation Models, RAG data preparation)

## Secrets and Git (Day 0)
1. What it is: commit = local snapshot with a message; push = upload commits to GitHub. .gitignore stops git from tracking .env.
2. Example from P1: git ls-files shows only .env.example, never .env.
3. Why it matters: bots scan GitHub for keys within minutes.
4. Industry name: secrets management (AWS Secrets Manager, Parameter Store).
5. Interview line: "If a key leaks, revoke it first, then clean history; deleting the file is not enough."
AWS AIF-C01 domain: 5 (Security, Compliance, and Governance)
