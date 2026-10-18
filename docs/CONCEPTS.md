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

## Chunking (Step 1.4)
1. What it is: cutting each document into pieces small enough to embed and retrieve. Too big and the match gets blurry or cut off; too small and a piece loses its context.
2. Example from P1: V1 cuts about 400 tokens (52 chunks), V2 cuts by heading (265 chunks), V3 keeps one chunk per document (52). Every chunk starts with `{title} ({doc_id}) | {section}` so the document code is inside the text.
3. Why it matters: V2 chunks of KPI-014 never contained "KPI-014", so neither BM25 nor the embedding could find the file by its code. Chunking changes what can be found.
4. Industry name: chunking strategy, document segmentation, chunk metadata.
5. Interview line: "I compared three chunkings on a golden set, and I put the document ID in every chunk header after a miss showed codes were missing."
AWS AIF-C01 domain: 3 (Applications of Foundation Models, RAG data preparation)

## Vector search + Chroma + metadata (Step 1.5)
1. What it is: each chunk becomes a vector (384 numbers) with `bge-small-en-v1.5`; a question becomes a vector too, and the closest chunks by cosine similarity are returned. Chroma stores the vectors on disk with metadata.
2. Example from P1: "how is churn calculated" finds the KPI-007 chunk by meaning, even without the exact words. Metadata (domain, certification) can filter results.
3. Why it matters: meaning-based search is the base of the system, but it can miss exact codes (KPI-010 asked by code returned SOPs).
4. Industry name: dense retrieval, embeddings, vector database, metadata filtering (OpenSearch, Pinecone, Bedrock Knowledge Bases).
5. Interview line: "Vector search finds meaning, not exact tokens, so I measured where it fails instead of assuming."
AWS AIF-C01 domain: 2 (Fundamentals of Generative AI, embeddings), 3 (RAG)

## Keyword search, BM25 (Step 1.6)
1. What it is: ranks chunks by how often and how rarely the question's words appear in them. Rare words (like KPI-014) count for more.
2. Example from P1: a tokenizer that keeps hyphenated IDs lets "KPI-014" match the right file. BM25 recall on the golden set (0.59 to 0.64) is below vector (0.81), but it is strong on exact codes.
3. Why it matters: it covers what embeddings blur (codes, names), but it also rewards chatty text such as the informal FAQ.
4. Industry name: lexical or sparse retrieval, TF-IDF, BM25 (OpenSearch).
5. Interview line: "BM25 handles exact IDs; on my golden set it was the weaker ranker overall, which is why equal-weight fusion hurt."
AWS AIF-C01 domain: 3 (Applications of Foundation Models)

## Retrieval metrics and a golden set (Steps 2.1 and 2.2)
1. What it is: a fixed list of questions with the expected documents, scored by recall@5 (share of expected documents found in the top 5), hit@5 (at least one found) and MRR@10 (how high the first expected one ranks). Dev questions drive decisions; holdout is run once.
2. Example from P1: V1 + vector scores dev 0.815 / 1.000 / 0.938 and holdout 0.729 / 0.875 / 0.646. Holdout has only 8 answerable questions, so one question moves recall by about 0.125.
3. Why it matters: it turns "it feels better" into numbers, and the sample size tells you how much to trust a change.
4. Industry name: offline evaluation, golden dataset, recall@k, MRR, held-out set.
5. Interview line: "I compared every change on the same questions, did not tune on holdout, and said 'promising, not proven' when the sample was small."
AWS AIF-C01 domain: 3 (Evaluating foundation model applications)

## Hybrid search + Reciprocal Rank Fusion (Step 2.3)
1. What it is: run vector and BM25 search, then merge the two rankings with RRF: each chunk scores the sum of 1/(60 + rank) over the lists it appears in.
2. Example from P1: rank 1 in vector and rank 4 in BM25 scores 1/61 + 1/64. Equal-weight RRF lost to vector on dev for all three chunkings, because the weaker BM25 pulled FAQ-01 into the top 5 (16 of 24 dev questions, against 7 for vector).
3. Why it matters: fusion is not free. If one ranker is weaker, an equal vote lets its mistakes in.
4. Industry name: hybrid retrieval, rank fusion, RRF (OpenSearch hybrid search).
5. Interview line: "Hybrid did not help on my corpus. I kept vector as the default and documented why, instead of tuning weights on 24 questions."
AWS AIF-C01 domain: 3 (Applications of Foundation Models, RAG)

## Reranking, cross-encoder (Step 2.4)
1. What it is: a second model that reads the question and one chunk together and gives a relevance score. More precise than comparing separate vectors, but it must run once per candidate.
2. Example from P1: reranking the vector top 50 gave a mixed dev result (recall +0.010, MRR -0.028) and a better holdout on 8 questions, at about 50 times the latency. It also ranked the informal FAQ-01 higher.
3. Why it matters: it only reorders what retrieval found, and it sees text only, so it cannot tell a certified source from a provisional one.
4. Industry name: reranker, cross-encoder, retrieve wide and rerank narrow (Cohere Rerank, Bedrock rerank).
5. Interview line: "Reranking improved some questions and hurt others; relevance is not authority, so I handled governance in generation."
AWS AIF-C01 domain: 3 (Applications of Foundation Models)

## Grounded generation, citations and refusal (Step 2.5)
1. What it is: the model answers only from retrieved chunks, returns structured JSON with citations and a refused flag, and code checks that every citation is a chunk that was actually retrieved.
2. Example from P1: asked about KPI-010 with no documents, Gemini gave a fluent but wrong definition. With context it answers from the chunk, and for "who is the CEO" it refuses with an exact sentence. When KPI-010 was not retrieved, it refused instead of inventing.
3. Why it matters: a valid citation proves a chunk was in the context, not that it supports the claim. Support is judged separately, and retrieval failures can still look like a clean refusal.
4. Industry name: grounding, RAG with citations, structured output, abstention, trace logging.
5. Interview line: "I validate citations in code and log a trace of every call, and I know that does not prove correctness, so I evaluate support separately."
AWS AIF-C01 domain: 2 (Fundamentals of Generative AI, hallucination), 4 (Responsible AI, transparency), 5 (Governance)
