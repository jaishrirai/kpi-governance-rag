# P1 Week 1 Brief: KPI and Governance RAG Assistant

## Summary

- **What it is:** the complete Week 1 plan for P1, the KPI and Governance RAG Assistant (a prototype on synthetic data).
- **Part A (Day 1, 4 hours):**
  - The hour-by-hour timetable.
  - The concept notes for Token, Context window and Temperature.
  - The AIF-C01 exam facts and Domain 1 terms.
  - Windows setup commands, the smoke test, the definition of done and explain-it-back questions.
- **Part B (the whole project):**
  - The 7 decisions to lock on Day 1.
  - Problem, users and scope.
  - A 50-document corpus for the fictional Kestrel Retail Group.
  - The architecture, settings for each component and the repo layout.
  - A 40-question golden set with 10 held out, and the eval plan with a 3 x 3 experiment grid.
  - A plan for each of Days 1 to 7, the cut list, risks, the design page template and the end-of-week interview line.
- **Part C (Days 2 to 7, hour by hour):** each day has a goal, a timetable with outputs, what to cover in each concept note, the exact exam topics, build steps with settings, common mistakes, a definition of done, explain-it-back questions and a commit message. It also has a 20-minute prep list for the evening before Day 1 and an end-of-week review.
- **Outputs by Day 7:**
  - An experiments table built from your own numbers.
  - Grounded answers with citations and refusals.
  - A `/ask` API for Agent A, a README draft, and Mock 1 scored.

This covers Days 1 to 7 of the 30-Day AI Upskilling Checklist, and pulls together the build plan, the cheat sheet entries and the AWS exam topics for each day. Part A is Day 1 hour by hour. Part B is the full project definition, used as the reference. Part C is Days 2 to 7 hour by hour. Together they are the Week 1 guide.

Everything here is a prototype on synthetic data. The company, people and numbers in the corpus are invented. Never use FBIN data.

---

# Part A: Day 1 in detail

## Day 1 goal

By the end of Day 1 you have a working environment that can embed text and call an LLM. You also have a one-page design committed to GitHub and the 50-document corpus list ready for Day 2.

## Day 1 timetable (4 hours)

The clock times are an example starting at 9:00 AM IST, so shift them to suit your day.

| Time | Block | What you do | Output |
| --- | --- | --- | --- |
| 9:00 to 9:30 | Concepts (30 min) | Read the 3 starred entries in S1: **Token, Context window, Temperature** (10 min). Write a 5-line note on each in your own words (10 min). Explain all three out loud once, as if to a business stakeholder (10 min). | `day-01.md` in your concepts log, with 3 notes |
| 9:30 to 10:00 | Cert (30 min) | Sign in to AWS Skill Builder (free) and enrol in the "Exam Prep Plan: AWS Certified AI Practitioner (AIF-C01)". Read the exam guide overview and Domain 1, Task 1.1. | `cert/aif-c01-notes.md` with the 5 domains and weights, plus one-line definitions of the Task 1.1 terms |
| 10:00 to 10:45 | Build: setup | Install or check Python, Git and VS Code. Create the GitHub repo, the folder skeleton, a virtual environment, `requirements.txt`, `.gitignore` and `.env.example`. First commit. | Repo on GitHub with the skeleton |
| 10:45 to 11:15 | Build: smoke test | Write `scripts/smoke_test.py`: (a) embed 2 sentences and print the vector size and cosine similarity; (b) make one LLM call at temperature 0 and one at 1, and print the token counts. | Smoke test runs; the output is pasted into the daily log |
| 11:15 to 12:30 | Build: design page | Write `docs/design.md` from the template in Part B, section 13. One page, in your own words. | Design page committed |
| 12:30 to 12:50 | Build: decisions and corpus list | Record the 7 decisions in `docs/decisions.md` (Part B, section 2). Copy the 50-document list (Part B, section 4) into `data/corpus_manifest.csv`. | Decisions file and corpus manifest |
| 12:50 to 13:00 | Close | Write the daily log (5 lines), commit and push. | Day 1 commit pushed |

## Day 1 concepts (S1)

Write each note with this 5-line template:

```text
Concept:
1. What it is (one line, my words):
2. Example (from P1 if possible):
3. Why it matters for P1:
4. LangChain name:
5. My interview line (say "I would" if I have not done it yet):
```

What each concept should cover:

- **Token:** the model reads and bills in tokens, roughly 4 characters of English each. On Day 1 your smoke test prints real token counts, so use those as your example.
- **Context window:** everything the model sees at once. P1 matters because retrieval decides which few chunks go into that window.
- **Temperature:** randomness. P1 answers run at 0 because governance answers must be repeatable. Your smoke test shows the difference between 0 and 1.

## Day 1 cert block (AIF-C01)

Exam facts to write down:

- 50 scored and 15 unscored questions, scored from 100 to 1,000, with 700 to pass.
- Question types: multiple choice, multiple response, ordering and matching.
- Check the fee and length when you book.

| Domain | Weight | When you study it |
| --- | --- | --- |
| 1. Fundamentals of AI and ML | 20% | Week 1, Days 1 to 4 |
| 2. Fundamentals of GenAI | 24% | Week 1, Days 5 to 7 |
| 3. Applications of foundation models | 28% | Week 2 |
| 4. Guidelines for responsible AI | 14% | Week 3 |
| 5. Security, compliance and governance for AI solutions | 14% | Week 3 |

Task 1.1 terms to define in one line each:

- AI, ML, deep learning, neural network
- Computer vision, NLP
- Model, algorithm, training, inferencing
- Bias, fairness, fit
- LLM, GenAI, agentic AI

Note that the current guide includes **agentic AI** and new AWS services, so older courses may miss them.

**Resources:**

- the AIF-C01 exam guide
- the Skill Builder "Exam Prep Plan"
- the free "Official Practice Question Set" (you'll use it on Day 7)

## Day 1 setup steps (Windows)

1. Check the tools. In a terminal, run `py --version` (use 3.11 or 3.12), `git --version` and `code --version`. Install anything missing from python.org, git-scm.com and code.visualstudio.com.
2. Create a GitHub repo called `kpi-governance-rag`. Keep it private until Day 7, then make it public with the README.
3. Clone it, then create the environment:
   ```text
   py -3.12 -m venv .venv
   .venv\Scripts\activate
   pip install torch --index-url https://download.pytorch.org/whl/cpu
   pip install sentence-transformers chromadb rank-bm25 pypdf pandas pyyaml fastapi uvicorn pydantic python-dotenv anthropic
   pip freeze > requirements.txt
   ```
   Installing the CPU build of torch first avoids a very large GPU download.
4. Create the folder skeleton from Part B, section 7.
5. Add the API key to `.env` (never commit it). Put `.env`, `.venv/` and `data/index/` in `.gitignore`. Commit `.env.example` with the variable name only.
6. Set a monthly spend limit of about USD 10 in the LLM provider's console before the first call.

## Day 1 smoke test (what it must show)

```python
# scripts/smoke_test.py  (write it yourself; you must be able to explain every line)
from sentence_transformers import SentenceTransformer
import numpy as np, os
from dotenv import load_dotenv
import anthropic

load_dotenv()
model = SentenceTransformer("BAAI/bge-small-en-v1.5")
a, b = model.encode(["customer churn rate", "customer attrition"], normalize_embeddings=True)
print("vector size:", len(a))                     # expect 384
print("cosine similarity:", float(np.dot(a, b)))   # normalised vectors, so dot = cosine

client = anthropic.Anthropic()
for temp in (0, 1):
    r = client.messages.create(
        model=os.environ["LLM_MODEL"], max_tokens=60, temperature=temp,
        messages=[{"role": "user", "content": "Define Net Revenue Retention in one sentence."}])
    print(temp, r.usage.input_tokens, r.usage.output_tokens, r.content[0].text)
```

Run it twice. The temperature 0 answers should be almost identical and the temperature 1 answers should vary. Paste the output into `docs/daily-log.md`.

## Day 1 definition of done

- [ ] The concepts log has 3 notes for Day 1
- [ ] `cert/aif-c01-notes.md` has the domain weights and the Task 1.1 terms
- [ ] The repo is on GitHub with the skeleton, `requirements.txt`, `.gitignore` and `.env.example` (no key committed)
- [ ] The smoke test prints size 384, a similarity score and token counts at 2 temperatures
- [ ] `docs/design.md` (1 page), `docs/decisions.md` and `data/corpus_manifest.csv` are committed
- [ ] The daily log is written and the commit is pushed

## Day 1 explain-it-back check

Answer these out loud without notes before you close the day:

1. Why does the smoke test normalise the embeddings, and what does a score of 0.8 mean?
2. What will change in your P1 cost if you send 20 chunks instead of 5?
3. Why must governance answers run at temperature 0?
4. In two sentences, what is P1 and who uses it?

---

# Part B: P1 full project definition

## 1. One-line pitch and honest framing

**Pitch:** a prototype assistant that answers "How is this KPI defined, who owns it, and is it certified?" from a governed document set, always with citations, and says "I don't know" when the answer is not there.

**Honest framing (use it in the README and in interviews):** "A prototype built on a synthetic corpus for a fictional company. The numbers come from my own eval runs on a 40-question golden set. Not production."

**Why it fits your story:** it's your KPI standards and data catalog work, applied to AI. Governance, certification levels and ownership are your home ground. This project adds the RAG engineering on top.

## 2. Decisions to lock on Day 1 (record in `docs/decisions.md`)

| # | Decision | Recommendation | Why |
| --- | --- | --- | --- |
| 1 | LLM for answers and for judging | Anthropic API: the current Haiku-class model for answers, a Sonnet-class model as the judge. Put every model call behind one function, `llm.complete()`. | Cheap, strong at following instructions. The single wrapper means Week 3 can switch to Bedrock by changing one file. |
| 2 | Embedding model | `BAAI/bge-small-en-v1.5`, run locally | Free, fast on CPU, 384 dimensions. Limit: it reads at most 512 tokens per chunk. |
| 3 | Vector store | Chroma, persistent on disk | Simple, local and free. It supports metadata filters. |
| 4 | Language and environment | Python 3.12 with a venv; plain libraries, no framework | Obeys the explain-it-back rule. LangChain names go into your notes, not your code. |
| 5 | Repo visibility | Private until Day 7, then public | You show a finished README, not a half-built repo. |
| 6 | Concepts log | A public GitHub repo, `ai-concepts-log`, with one file per day | Public proof of the daily habit. |
| 7 | Fictional company | "Kestrel Retail Group": omnichannel retail, stores plus app | Rich KPIs, and clearly not FBIN. |

## 3. Problem, users and scope

**The problem:** business users ask "How is Active Customer defined? Which dashboard shows it? Who owns it? Can I use it in a board pack?" The answers are scattered across KPI pages, a catalog, SOPs and policy PDFs. People guess, reuse old definitions, or email the data team.

**The users:**

| User | Typical question | What a good answer looks like |
| --- | --- | --- |
| Business analyst | "What is the formula for Net Revenue Retention?" | The exact formula, source table, certification level and citation |
| Data steward | "Which KPIs does the Customer domain own that are still Provisional?" | A filtered list with citations |
| Manager | "Can I use Churn Rate in the board pack?" | Certified or not, which version, and the approval SOP |

**In scope:** questions about definitions, formulas, ownership, certification, source tables, dashboards and governance process.

**Out of scope:** actual KPI values ("What was NRR in Q3?" is unanswerable by design), write actions, user login and permissions (simulated with metadata filters only).

## 4. The corpus (Day 2)

There are 50 source documents for the invented company Kestrel Retail Group. Each Markdown file starts with a YAML header holding its metadata.

| Group | Count | Format | Content |
| --- | --- | --- | --- |
| KPI definitions | 20 | Markdown, 250 to 450 words each | One file per KPI, using the template below |
| Data catalog entries | 15 | 1 CSV, with each row treated as one document | Tables and dashboards: name, type, domain, owner, certification, refresh, description, linked KPIs |
| Governance SOPs | 8 | Markdown | KPI certification process, requesting a new KPI, metric change management, data access requests, data quality incidents, dashboard publishing standard, naming conventions, data retention |
| Policy PDFs | 5 | PDF (write in Word, then Save as PDF) | Data Governance Policy, Acceptable Use of AI Tools, Data Classification Standard (with a table), KPI Glossary Summary (table-heavy), Quarterly KPI Review Minutes |
| Deliberate traps | 2 | Markdown | An old v1 of Customer Churn Rate marked Deprecated, and an informal team FAQ with a conflicting, uncertified definition of Active Customer |

**The 20 KPIs:**

| Domain | KPIs |
| --- | --- |
| Finance | Net Revenue, Gross Margin %, Days Sales Outstanding |
| Sales | Average Order Value, Conversion Rate, Basket Size, Store Footfall Conversion |
| Customer | Active Customer (30-day), Customer Churn Rate, Net Revenue Retention, Customer Lifetime Value, Repeat Purchase Rate, Net Promoter Score |
| Marketing | Customer Acquisition Cost, Marketing ROI (ROAS) |
| Operations | Inventory Turnover, Stockout Rate, On-Time Delivery %, Return Rate |
| Digital | Active User (app, 30-day) |

Active User and Active Customer are near-duplicate names on purpose, to test retrieval.

**Metadata (on every document):**

- `doc_id` (for example KPI-007, CAT-03, SOP-02, POL-04)
- `title`, `doc_type` (kpi, catalog, sop, policy, faq)
- `domain`, `owner` (an invented role, such as "Head of Customer Analytics")
- `certification` (Certified, Provisional or Deprecated)
- `version`, `effective_date`, `source_path`

**KPI template (the same headings in every file):**

```markdown
---
doc_id: KPI-007
title: Customer Churn Rate
doc_type: kpi
domain: Customer
owner: Head of Customer Analytics
certification: Certified
version: 2.0
effective_date: 2026-04-01
---
# Customer Churn Rate (KPI-007)
## Definition
## Formula
## Grain and filters
## Source tables
## Dashboards
## Caveats and exclusions
## Change history
```

**Generation rule:** use Claude to draft the documents in batches of 5, with a prompt that holds the template and the KPI list. Then skim every document and fix anything unrealistic. Keep each KPI file under about 450 tokens, because the embedding model cuts off at 512. Time-box generation to 90 minutes, since perfect documents are not the goal.

## 5. Architecture (how a question flows)

**Offline (runs when documents change):**

1. **Load:** Markdown with its YAML header, CSV rows and PDF pages become one list of documents with metadata.
2. **Chunk:** 3 variants (section 6.2).
3. **Embed:** each chunk becomes a 384-number vector.
4. **Store:** one Chroma collection per chunking variant, with metadata kept on every chunk.
5. **Build the BM25 keyword index:** one per variant.

**Online (for each question):**

1. **Filter (optional):** by domain or certification.
2. **Retrieve:** vector top 20 and BM25 top 20, merged with reciprocal rank fusion.
3. **Rerank:** a cross-encoder rescores the top 20 and keeps the best 5.
4. **Generate:** a grounded prompt with the 5 chunks, run at temperature 0, returns JSON with the answer, citations and a refused flag.
5. **Validate:** check the JSON with Pydantic and check that every citation points to a chunk that was actually retrieved.
6. **Return:** the answer, citations, latency and token usage.

## 6. Component specifications

### 6.1 Loaders (`src/rag/ingest.py`)

- **Markdown:** split the YAML header from the body with `pyyaml` and keep the header as metadata.
- **CSV:** use `pandas`. Each row becomes text such as "Asset: Customer 360 Dashboard. Type: dashboard. Domain: Customer. Owner: ... Certification: Certified. Description: ...", and the columns also go in as metadata.
- **PDF:** use `pypdf`, one document per page. Metadata comes from a small sidecar table in the manifest. Look at the text extracted from the table-heavy PDF, because this is where parsing breaks.
- **Output:** a list of `Document(text, metadata)` objects, saved to `data/processed/documents.jsonl`.

### 6.2 Chunking variants (`src/rag/chunking.py`)

| Variant | Rule | Settings | What it tests |
| --- | --- | --- | --- |
| V1 fixed | Split on a fixed size, with overlap | About 400 tokens (1,600 characters), 60-token overlap | The simple baseline |
| V2 by heading | Split at Markdown headings; PDFs by page; CSV one row per chunk | Cap of 450 tokens; if a section is longer, fall back to a fixed split | Respecting the document's structure |
| V3 by unit | One chunk per KPI file and one per catalog row; SOPs and PDFs split by heading | Cap of 450 tokens | One complete idea per chunk |

- **Chunk IDs:** `doc_id::variant::n`, for example `KPI-007::v2::3`. Every chunk keeps its document's metadata plus its section heading.
- **Token counts:** estimate with characters divided by 4, and say so in the design doc. It's an approximation, and that's fine.
- **Parent-child retrieval:** optional on Day 4 if you have time. Search on V2 chunks and pass the whole KPI file to the model.

### 6.3 Embeddings and vector store (`src/rag/index.py`)

- Use `bge-small-en-v1.5` with `normalize_embeddings=True`, so cosine similarity equals the dot product.
- For search queries, bge models work slightly better with the prefix "Represent this sentence for searching relevant passages: ". Test with and without it; it makes a good small experiment.
- Use 3 Chroma collections (`kpi_v1`, `kpi_v2`, `kpi_v3`) in `data/index/` (git-ignored). Rebuild them with one command, `python -m rag.index --variant all`.

### 6.4 Retrieval (`src/rag/retrieve.py`)

| Method | How | Settings |
| --- | --- | --- |
| Vector | Chroma query | top 20 |
| BM25 | `rank_bm25.BM25Okapi` on lowercase words, keeping codes such as KPI-007 whole | top 20 |
| Hybrid | Reciprocal rank fusion: score = sum of 1 / (60 + rank) across both lists | Top 20 after fusion |
| Rerank | Cross-encoder `cross-encoder/ms-marco-MiniLM-L-6-v2` scores each question and chunk pair | Keep the top 5 |
| Filters | Chroma `where` on domain and certification; apply the same filter to the BM25 results | Optional per query |

### 6.5 Generation (`src/rag/generate.py`)

**The system prompt (version it as `prompts/answer_v1.txt`):**

```text
You are the Kestrel KPI and Governance assistant.
Answer ONLY from the numbered context chunks below.
Every factual sentence must cite at least one chunk id in square brackets, e.g. [KPI-007::v2::3].
If the context does not contain the answer, set refused to true and answer exactly:
"I could not find this in the governed documents."
If sources conflict, prefer the Certified and most recent version, and say that a conflict exists.
Never state a KPI value; this corpus holds definitions only.
Return JSON: {"answer": str, "citations": [str], "refused": bool}
```

- **Model settings:** temperature 0 and max output of 400 tokens.
- **Checks:** validate the JSON with a Pydantic model. Reject any citation that isn't among the retrieved chunk IDs, and retry once. On a second failure, return the refusal message.
- **Logging:** record the prompt version, model ID, chunk IDs, input and output tokens and latency for every call, in `results/traces.jsonl`.

### 6.6 API (`api/app.py`), for Agent A to call on Day 9

- **`POST /ask`**
  - Request: `{"question": str, "top_k": 5, "filters": {"domain": str | null, "certification": str | null}}`
  - Response: `{"answer": str, "citations": [str], "refused": bool, "chunks": [{"id", "doc_id", "title", "score"}], "latency_ms": int, "usage": {"input_tokens", "output_tokens"}, "config": "v2+hybrid+rerank"}`
- **`GET /health`** returns `{"status": "ok"}`.
- **Run locally with** `uvicorn api.app:app --port 8000`.

## 7. Repo structure

```text
kpi-governance-rag/
  README.md
  requirements.txt  .gitignore  .env.example
  docs/        design.md  decisions.md  daily-log.md
  data/
    corpus_manifest.csv
    raw/       kpis/  sops/  pdfs/  catalog/  faq/
    processed/ documents.jsonl  chunks_v1.jsonl  chunks_v2.jsonl  chunks_v3.jsonl
    index/     (Chroma files, git-ignored)
  golden/      golden_set.jsonl
  prompts/     answer_v1.txt  judge_faithfulness_v1.txt  judge_correctness_v1.txt
  src/rag/     config.py  ingest.py  chunking.py  index.py  retrieve.py  generate.py  llm.py  pipeline.py
  eval/        retrieval_eval.py  generation_eval.py
  api/         app.py
  results/     runs.csv  experiments.md  traces.jsonl
  scripts/     smoke_test.py
  tests/       test_chunking.py  test_retrieve.py
```

## 8. Golden set (Day 4, before any tuning)

There are 40 questions in `golden/golden_set.jsonl`. Write them before you look at retrieval results, so you don't write questions your system happens to answer well.

| Category | Count | Example |
| --- | --- | --- |
| Definition or formula | 12 | "How is Net Revenue Retention calculated?" |
| Ownership and certification | 8 | "Who owns Stockout Rate and is it certified?" |
| Catalog and dashboards | 6 | "Which dashboard shows Repeat Purchase Rate?" |
| Process (SOPs and policy) | 6 | "What are the steps to certify a new KPI?" |
| Unanswerable | 8 | "What was NRR last quarter?", "Who owns Employee Attrition?" |

Also include these traps:

- 2 questions that hit the deprecated Churn v1 (the right answer uses v2)
- 2 that hit the conflicting FAQ definition of Active Customer
- 2 that use exact codes, such as "What is KPI-014?"

**Format (one JSON object per line):**

```json
{"id": "Q07", "question": "How is Net Revenue Retention calculated?", "category": "definition", "answerable": true, "expected_doc_ids": ["KPI-010"], "expected_answer": "Revenue this period from customers who existed at the start, divided by their revenue at the start, including expansion and churn.", "holdout": false}
```

**Holdout:** mark 10 questions as `holdout: true`. Tune on the other 30, then report on both groups. This stops you overfitting a small set, and it's a strong point to make in an interview.

## 9. Evaluation plan

**Retrieval metrics (no LLM needed, cheap to run):**

- **recall@5 (headline):** for each answerable question, the share of its expected `doc_ids` that appear in the top 5 documents, averaged over questions. Match on the document, not the chunk, so the 3 chunking variants are compared fairly.
- **hit@5:** 1 if any expected `doc_id` appears in the top 5 documents, else 0, averaged over questions. Reported next to recall@5. (Earlier versions of this brief called this metric "recall@5"; the conventional name for the binary metric is hit rate.)
- **MRR@10:** the average of 1 / (rank of the first correct document).

**Generation metrics (they cost tokens, so run them on the best configuration and one baseline only):**

| Metric | How it's scored |
| --- | --- |
| Correctness | A judge model compares the answer with `expected_answer` and returns correct, partly correct or wrong |
| Faithfulness | A judge checks that every claim is supported by the cited chunks (yes or no) |
| Citation validity | Code checks that the cited `doc_id` is in `expected_doc_ids` |
| Refusal accuracy | Refused on the unanswerable questions (target 8 of 8); count any answerable question wrongly refused |
| Judge agreement | You grade 10 answers by hand and check how often the judge agrees with you |
| Cost and latency | Average input and output tokens times the current price; p50 and p95 latency |

**The experiment grid (Day 5 and Day 7):**

| Run | Chunking | Retrieval | recall@5 | hit@5 | MRR | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| 1 to 3 | V1, V2, V3 | Vector |  |  |  |
| 4 to 6 | V1, V2, V3 | BM25 |  |  |  |
| 7 to 9 | V1, V2, V3 | Hybrid (RRF) |  |  |  |
| 10 to 11 | Best 2 from above | Hybrid plus reranker |  |  |  |

**Rules:**

- Fill the cells only from your own runs.
- Log every run in `results/runs.csv` with the date, configuration, git commit and metrics.
- Write targets in the design doc before you run, and label them as targets. For example: "Target: hybrid beats vector-only on recall@5, 8 of 8 correct refusals."

## 10. Day-by-day plan, Days 1 to 7

This is the overview. Part C has each day hour by hour.

Every day follows the same pattern: Concepts 30 min, Cert 30 min, Build 3 hours, then commit and log.

| Day | Concepts (starred) | Cert (30 min) | Build (3 hours) | Output and definition of done |
| --- | --- | --- | --- | --- |
| 1 | S1: Token; Context window; Temperature | Exam guide; Task 1.1 terms | Setup, smoke test, design page, decisions, corpus manifest | See Part A |
| 2 | S1: Zero-shot vs few-shot; Structured output; Hallucination | Task 1.1: types of inferencing, data types, learning types | Generate the 50 documents (90 min time-box). Write the loaders for Markdown, CSV and PDF. Save `documents.jsonl`. | 50 files in `data/raw`, the loader runs and prints a count per `doc_type`, and the PDF table text has been checked |
| 3 | S2: Embedding; Cosine similarity; Vector store | Task 1.2: use cases, when AI is not the right fit, regression, classification, clustering, AWS AI services (Transcribe, Translate, Comprehend, Lex, Polly, SageMaker AI) | Write the 3 chunkers with unit tests. Embed them and build 3 Chroma collections. Print the chunk count and average token size per variant. | 3 indexes built with one command; a table of chunk counts is in the daily log |
| 4 | S3: Chunking; Chunk overlap; Parent-child retrieval | Task 1.3: ML lifecycle, MLOps, accuracy, precision, recall, F1, business metrics | Write vector retrieval. Write the 40-question golden set, including 10 holdout. Quick baseline: recall@5 for vector on V1. | `golden_set.jsonl` committed; the first baseline number is logged |
| 5 | S2: Keyword search (BM25); Hybrid search; Reciprocal rank fusion (RRF) | Task 2.1: tokens, chunking, embeddings, transformers, diffusion, FM lifecycle, token pricing, context engineering, agentic AI and MCP | Write BM25, hybrid RRF and the metadata filters. Write `retrieval_eval.py` and run runs 1 to 9. | Runs 1 to 9 in `runs.csv`; a first draft of `experiments.md` |
| 6 | S2: Reranker; S3: Query rewriting; S3: Grounding | Task 2.2 and 2.3: GenAI strengths and limits, model selection, the AWS services (Bedrock, SageMaker JumpStart, Amazon Quick, Kiro, Strands Agents, AgentCore); a read-only walkthrough of the Bedrock console | Add the reranker (runs 10 and 11). Write the grounded prompt, JSON output, citation check and refusal. Build a CLI: `python -m rag.ask "question"`. Write `generation_eval.py` and the judge prompts. | Answers come back end to end with valid citations; the unanswerable questions are refused |
| 7 | S3: RAG vs fine-tuning; Common failure modes; Retrieval metrics | Official Practice Question Set, Domains 1 and 2; log your misses | Hour 1: run the generation eval (best configuration vs baseline), then hand-grade 10 answers. Hour 2: FastAPI, the latency and cost table, and a README draft. Hour 3: Mock 1 (RAG design and basics). | Experiments table from your own numbers, a working `/ask` endpoint, and Mock 1 scored out of 25 |

**About Bedrock in Week 1:** the AWS account is created on Day 8, so the Day 6 Bedrock "first look" is read-only, using the Skill Builder course or AWS docs. Hands-on Bedrock starts on Day 8.

## 11. If you fall behind: cut list

| Priority | Items |
| --- | --- |
| Must have by Day 7 | Corpus; 3 chunkings; vector, BM25 and hybrid retrieval; golden set; retrieval grid (runs 1 to 9); grounded answers with citations and refusal; `/ask` endpoint |
| Should have | Reranker; generation eval with the judge; 10 hand-graded answers; cost and latency table |
| Could have (Week 4 or later) | Query rewriting; parent-child retrieval; the query-prefix test; comparing a hosted embedding model; the Ragas library |

If a day overruns by more than 45 minutes, move the leftover work to the "Could" row. Protect the concepts and cert blocks.

## 12. Risks and how to handle them

| Risk | What to do |
| --- | --- |
| The torch install is huge or fails on Windows | Install the CPU wheel first (Part A). If it still fails, use Python 3.11. |
| The API key leaks to GitHub | Keep `.env` in `.gitignore` from the first commit. If a key is ever pushed, revoke it at once. |
| Spending runs away | Set a USD 10 cap before the first call. Use the cheap model for answers and run the judge on 2 configurations only. |
| Corpus generation takes all of Day 2 | Stop at 90 minutes; realistic enough is enough. |
| Golden set bias | Write the questions before looking at results. Keep a holdout set. |
| The PDF table text comes out scrambled | Document it as a failure mode. It's a good interview story. |
| Scope creep into frameworks | No LangChain in code this week; LangChain names go in your notes only. |
| Code you cannot explain | Apply the explain-it-back rule before every commit. |

## 13. Design page template (`docs/design.md`, 1 page, Day 1)

Write it in your own words and keep it to one page.

```markdown
# P1 Design: KPI and Governance RAG Assistant (prototype, synthetic data)
## 1. Problem and users
## 2. Scope (in / out)
## 3. Corpus plan (50 docs, groups, metadata, traps)
## 4. Pipeline (offline steps, online steps)
## 5. Experiments (3 chunking x 3 retrieval, plus reranker)
## 6. Eval plan and targets (metrics, golden set, holdout; targets labelled as targets)
## 7. Risks, limits and honesty statement
```

## 14. What you can say at the end of Week 1

Fill the brackets only with your own results:

> "I built a prototype RAG assistant on a synthetic, governed KPI corpus for a fictional retailer. I compared three chunking strategies and three retrieval methods on a 40-question golden set with 10 held out. Hybrid search [result from your runs] and the reranker [result]. It refused [x of 8] unanswerable questions. Cost was about [your number] per query, with p95 latency of [your number]."

Say "I would" for anything you haven't built yet, such as parent-child retrieval or query rewriting.

## 15. Daily routine checklist

- [ ] Concepts: 3 notes in `ai-concepts-log`
- [ ] Cert: 30 min, with notes in `cert/aif-c01-notes.md`
- [ ] Build: the day's tasks, with tests where it makes sense
- [ ] Explain-it-back: every changed file explained out loud
- [ ] Daily log: what I did, one number, one problem, tomorrow's first task
- [ ] Commit and push, with messages such as `day3: chunkers v1-v3 + chroma index`
- [ ] Job search: applications still running

---

# Part C: Days 2 to 7 in detail

Each day follows the Day 1 pattern: Concepts 9:00 to 9:30, Cert 9:30 to 10:00, Build 10:00 to 13:00. Shift the clock to suit you, but keep the order, because the concepts and cert blocks set up that day's build. Settings and file names come from Part B.

## Before Day 1: 20-minute prep (do it the evening before)

- [ ] A GitHub account, and a Personal Access Token or GitHub Desktop so you can push from Windows
- [ ] An LLM API account with billing on and a USD 10 spend cap; the API key saved in a password manager
- [ ] An AWS Skill Builder login (free, using an AWS Builder ID)
- [ ] About 5 GB of free disk space (torch and the models are large)
- [ ] Your job applications scheduled for the week, so the build doesn't crowd them out

---

## Day 2: Corpus and loaders

**Goal:** the 50 synthetic documents exist, they're consistent with each other, and one command loads them all into `documents.jsonl` with metadata.

### Timetable

| Time | Block | What you do | Output |
| --- | --- | --- | --- |
| 9:00 to 9:30 | Concepts | S1: Zero-shot vs few-shot; Structured output; Hallucination | 3 notes in `day-02.md` |
| 9:30 to 10:00 | Cert | Task 1.1, second half: types of inferencing, data types, learning types | Notes plus 5 self-quiz questions |
| 10:00 to 10:15 | Build | Finish the manifest: owner, certification, version and date for all 50 documents | `corpus_manifest.csv` complete |
| 10:15 to 10:30 | Build | Write one KPI file by hand (Net Revenue Retention); it becomes the example in your generation prompt | `KPI-010.md` |
| 10:30 to 11:45 | Build | Generate the rest in batches (hard stop at 11:45); make the PDFs; run the consistency checks | 50 files in `data/raw/` |
| 11:45 to 12:45 | Build | Write `src/rag/ingest.py` (loaders for Markdown, CSV and PDF) | `documents.jsonl` |
| 12:45 to 13:00 | Close | Print counts by `doc_type`, inspect the PDF table text, write the log, commit | Day 2 commit |

### Concepts: what each note should cover

- **Zero-shot vs few-shot:** the hand-written KPI file is your one-shot example today. Note what changed when the model saw an example versus when it didn't.
- **Structured output:** the YAML header on every file is structured output. Your loader will fail if the model breaks the format, so note how often that happened.
- **Hallucination:** generated documents can contradict each other, such as an owner who doesn't match the manifest. The consistency checks are how you catch that. Note one example you fixed.

### Cert: Task 1.1 (second half)

- **Types of inferencing:**
  - Batch: scoring a large set on a schedule.
  - Real-time: an answer in milliseconds.
  - Asynchronous: large requests where the result comes back later.
  - Serverless: pay per request, with no servers to manage.
- **Data types:** labelled vs unlabelled, tabular, time series, image, text, structured vs unstructured. P1 is unstructured text plus one tabular CSV.
- **Learning types:** supervised, unsupervised and reinforcement, each with one business example of your own.

### Build: step by step

**1. Manifest distribution.** Use invented owner roles only:

- **Owner roles (6):** Head of Finance Analytics, Head of Sales Analytics, Head of Customer Analytics, Head of Marketing Analytics, Head of Supply Chain Analytics, Head of Digital Product.
- **KPIs:** 15 Certified and 5 Provisional. The trap copy of Customer Churn Rate (v1) is Deprecated.
- **Catalog rows:** 10 Certified and 5 Provisional.
- **Effective dates:** spread across 2025 and 2026. Churn v1 is dated 2025-01-01 and v2 is 2026-04-01.

**2. The generation prompt.** Use it in the Claude app or through the API, 5 KPIs per batch:

```text
You are writing internal documentation for Kestrel Retail Group, a fictional omnichannel retailer (stores plus app).
Write KPI definition files in Markdown, exactly following the template and style of the EXAMPLE.
Rules:
- Keep each file between 250 and 400 words.
- Start with the YAML header exactly as given in the INPUT rows (do not change doc_id, owner, certification, version, effective_date).
- Use only these source tables: sales_orders, order_lines, customers, app_sessions, marketing_spend, inventory_snapshots, deliveries, returns, nps_responses, invoices.
- Use only these dashboards: Executive KPI Pack, Customer 360 Dashboard, Sales Performance Dashboard, Supply Chain Control Tower, Marketing Effectiveness Dashboard, Digital Engagement Dashboard.
- Formulas must be realistic and consistent with the definition. Never include actual KPI values.
- Output each file separated by a line containing only =====.
EXAMPLE:
<paste your hand-written KPI-010.md>
INPUT (one per line: doc_id | title | domain | owner | certification | version | effective_date):
<5 rows from the manifest>
```

Generate the other groups the same way:

- **SOPs:** 8 in one batch, with a numbered steps section and a roles section in each.
- **Catalog:** 15 rows of CSV with the columns `asset_id, name, asset_type, domain, owner, certification, refresh, description, linked_kpis`. Separate the `linked_kpis` values with semicolons.
- **PDFs:** generate the text, paste it into Word, add a real table to the Data Classification Standard and the KPI Glossary Summary, then use Save as PDF.
- **Traps:** Churn v1 uses a different formula and says "Deprecated, replaced by v2" in its change history. The FAQ gives an informal Active Customer definition ("anyone who bought in the last 90 days") that conflicts with the certified 30-day one.

**3. Consistency checks (15 minutes, a short script plus a skim):**

- Every `doc_id` in the manifest has exactly one file.
- Owners and certification in each YAML header match the manifest.
- Every `linked_kpis` value in the catalog exists as a KPI ID.
- Every dashboard named in a KPI file exists in the catalog.
- No KPI file is over 1,800 characters of body text (about 450 tokens).
- There are no real company or product names.

**4. Loaders (`src/rag/ingest.py`):**

```python
@dataclass
class Document:
    doc_id: str
    text: str
    metadata: dict   # title, doc_type, domain, owner, certification, version, effective_date, source_path

def load_markdown(path) -> Document   # split YAML header from body; header becomes metadata
def load_catalog_csv(path) -> list[Document]   # one Document per row; text = "Asset: ... Type: ... Owner: ..."
def load_pdfs(folder, manifest) -> list[Document]   # one Document per page; metadata from manifest; doc_id like POL-03, page stored in metadata
def load_all() -> list[Document]   # writes data/processed/documents.jsonl
```

### Common mistakes

- Spending more than 90 minutes perfecting documents.
- Chroma metadata only accepts str, int, float or bool values, so store `linked_kpis` as one string with semicolons.
- `pypdf` can return empty text from a scanned PDF. Your PDFs come from Word, so they should be fine, but check.

### Definition of done

- [ ] 50 source documents in `data/raw/`, and the consistency checks pass
- [ ] `python -m rag.ingest` writes `documents.jsonl` and prints counts: kpi 21, catalog 15, sop 8, policy (pages across 5 PDFs), faq 1
- [ ] The PDF table text has been inspected and one line about its quality is in the log
- [ ] Commit: `day2: synthetic corpus (50 docs) + loaders`

### Explain-it-back

1. Why did you write one KPI by hand before generating the rest?
2. Where does each document's metadata come from, for each of the 3 file types?
3. Which trap documents did you plant, and what should the assistant do with each?

---

## Day 3: Chunking, embeddings and the vector store

**Goal:** 3 chunking variants, each with unit tests, embedded and stored in 3 Chroma collections, which you can rebuild with one command.

### Timetable

| Time | Block | What you do | Output |
| --- | --- | --- | --- |
| 9:00 to 9:30 | Concepts | S2: Embedding; Cosine similarity; Vector store | 3 notes |
| 9:30 to 10:00 | Cert | Task 1.2: use cases, when AI is not the right fit, techniques, AWS AI services | A table of services, one line each |
| 10:00 to 11:15 | Build | Write `src/rag/chunking.py` with V1, V2 and V3 | 3 chunk files in `data/processed/` |
| 11:15 to 11:45 | Build | Write `tests/test_chunking.py` | Tests pass |
| 11:45 to 12:40 | Build | Write `src/rag/index.py`: embed and store in Chroma | 3 collections |
| 12:40 to 12:55 | Build | Sanity queries, plus a stats table per variant | Stats in the log |
| 12:55 to 13:00 | Close | Log and commit | Day 3 commit |

### Concepts: what each note should cover

- **Embedding:** today you turn every chunk into 384 numbers. Note what the model cannot see: anything past 512 tokens is cut off.
- **Cosine similarity:** Chroma reports distance, and cosine similarity is 1 minus that distance. Write down one real pair from your sanity queries.
- **Vector store:** why you use 3 collections instead of 1 (so the variants can be compared fairly), and what the metadata on each chunk is for.

### Cert: Task 1.2

- **When AI adds value:** it helps people make decisions, it scales, and it automates. **When it doesn't:** the cost outweighs the benefit, or the task needs an exact, guaranteed outcome rather than a prediction.
- **Techniques:** regression (a number), classification (a category), clustering (groups). Give a retail example of each.
- **AWS AI services:** Transcribe (speech to text), Translate, Comprehend (text insights), Lex (chatbots), Polly (text to speech), SageMaker AI (build and train models).
- **Traditional ML vs foundation models:** consider regulation, explainability and operating constraints.

### Build: step by step

**1. Shared rules for all 3 variants (so the comparison is fair):**

- Estimate tokens as characters divided by 4.
- Start every chunk's embedded text with a short header: `"{title} | {section}\n"`. The same rule applies to every variant.
- **Chunk ID:** `doc_id::variant::n`. Each chunk's metadata is its document's metadata plus `section` and `variant`.

**2. The functions:**

```python
def chunk_fixed(doc, size_tokens=400, overlap_tokens=60) -> list[Chunk]      # V1: sliding window, cut at whitespace
def chunk_by_heading(doc, cap_tokens=450) -> list[Chunk]                    # V2: split on lines starting with '#'; long sections fall back to chunk_fixed
def chunk_by_unit(doc, cap_tokens=450) -> list[Chunk]                       # V3: whole KPI file / whole catalog row; SOP and policy by heading
```

Catalog rows and PDF pages are usually short, so they pass through all 3 variants as one chunk each. Log any that exceed the cap.

**3. Tests (`tests/test_chunking.py`):**

- No chunk is over its cap.
- Chunk IDs are unique within a variant.
- Every chunk has a `doc_id` and a `section`.
- In V1, neighbouring chunks of the same document share some overlapping text.
- In V3, each KPI file becomes exactly 1 chunk.

**4. Index (`src/rag/index.py`):**

- `chromadb.PersistentClient(path="data/index")`
- `get_or_create_collection("kpi_v1", metadata={"hnsw:space": "cosine"})`, and the same for v2 and v3.
- Embed in batches of 32 with `normalize_embeddings=True`.
- On a rebuild, delete the collection first, or re-adding the same IDs will fail.
- Command: `python -m rag.index --variant all`

**5. Sanity queries:** run these 3 against each collection and look at the top 3 results:

- "how is churn calculated"
- "KPI-014"
- "who owns the customer 360 dashboard"

### Common mistakes

- Treating Chroma's distance as similarity.
- Forgetting to normalise embeddings.
- Embedding text without the title header in one variant but not the others.
- Chunks over 512 tokens being silently cut off by the embedding model.

### Definition of done

- [ ] 3 chunk files, and the tests pass
- [ ] 3 Chroma collections built with one command
- [ ] A stats table in the log: chunk count, average tokens and maximum tokens per variant
- [ ] Sanity query results noted, including one surprise
- [ ] Commit: `day3: chunkers v1-v3 + tests + chroma index`

### Explain-it-back

1. What is the trade-off between V1's overlap and storage size or duplicate results?
2. Why does V3 put each KPI in one chunk, and when would that fail?
3. What does the "hnsw:space cosine" setting do?

---

## Day 4: Vector retrieval and the golden set

**Goal:** a vector search function with filters, the 40-question golden set written before any tuning, and your first baseline number.

### Timetable

| Time | Block | What you do | Output |
| --- | --- | --- | --- |
| 9:00 to 9:30 | Concepts | S3: Chunking; Chunk overlap; Parent-child retrieval | 3 notes, using your Day 3 stats as examples |
| 9:30 to 10:00 | Cert | Task 1.3: ML lifecycle, MLOps, metrics | Notes |
| 10:00 to 10:45 | Build | `vector_search()` with metadata filters | Works from the command line |
| 10:45 to 12:15 | Build | Write the 40 golden questions (90 min, and don't run retrieval while writing) | `golden_set.jsonl` |
| 12:15 to 12:45 | Build | `eval/retrieval_eval.py`, first version: recall@5 and MRR@10 at document level | The script runs |
| 12:45 to 13:00 | Close | Baseline (V1 vector) in `runs.csv`, log, commit | Day 4 commit |

### Concepts: what each note should cover

- **Chunking and chunk overlap:** use your own Day 3 stats. How many chunks did each variant make, and how much text is repeated by overlap?
- **Parent-child retrieval:** how you would add it (search V2 sections, send the whole KPI file). Say "I would" unless you build it.

### Cert: Task 1.3

- **Pipeline stages:** data collection, exploration, preprocessing, feature engineering, training, tuning, evaluation, deployment, monitoring.
- **Where models come from:** open-source pre-trained or custom-trained. **How they're deployed:** a managed API (Bedrock) or self-hosted.
- **MLOps:** experiments, repeatable processes, scalable systems, technical debt, production readiness, monitoring, retraining. Your `runs.csv` is a small version of experiment tracking.
- **Metrics:** accuracy, precision, recall and F1; business metrics such as cost per user, development cost, feedback and ROI. AWS services in this task: Bedrock, QuickSight, SageMaker AI.

### Build: step by step

**1. `retrieve.py`:**

```python
@dataclass
class Hit:
    chunk_id: str; doc_id: str; score: float; text: str; metadata: dict

def vector_search(question, variant, k=20, filters=None) -> list[Hit]
# score = 1 - distance; filters={"domain": "Customer", "certification": "Certified"}
# build Chroma where: single key -> {"domain": "Customer"}; two keys -> {"$and": [{...}, {...}]}
```

**2. Golden set rules:**

- Write questions the way real users ask: mix formal and casual, use abbreviations ("NRR", "AOV"), and put a small typo in 2 of them.
- `expected_doc_ids` can hold more than one document for process questions.
- Write `expected_answer` in your own words, 1 or 2 sentences, from the document itself.
- Follow the category counts and traps in Part B, section 8.
- Holdout: take every 4th question (10 in total), so they spread across categories.
- Validation script: 40 lines, 8 unanswerable, 10 holdout, and every expected `doc_id` exists in the manifest.

**3. Retrieval metrics at document level:**

- Turn the ranked chunk list into a ranked list of unique document IDs, keeping the first appearance of each.
- recall@5 = expected `doc_ids` found in the top 5 documents / number of expected `doc_ids`, averaged over answerable questions (headline).
- hit@5 = 1 if any expected `doc_id` is in the top 5 documents, else 0, averaged over answerable questions.
- MRR@10 = 1 / rank of the first expected document in the top 10, or 0 if it isn't there, averaged.
- Report the dev set (30) and the holdout set (10) separately, and skip unanswerable questions for these 2 metrics.

**4. `results/runs.csv` columns:**

```text
run_id,date,git_sha,variant,retriever,rerank,fetch_depth,split,n,recall_at_5,hit_at_5,mrr_at_10,avg_latency_ms,notes
```

### Common mistakes

- Peeking at retrieval results while writing questions.
- Matching on chunk IDs, which makes the variants impossible to compare.
- Counting unanswerable questions in recall.

### Definition of done

- [ ] `vector_search` works with and without filters
- [ ] `golden_set.jsonl`: 40 questions, 8 unanswerable, 10 holdout; the validation passes
- [ ] The V1 vector baseline is in `runs.csv`, for dev and holdout
- [ ] Commit: `day4: vector retrieval + golden set (40q) + baseline`

### Explain-it-back

1. Why write the golden set before tuning, and what does the holdout protect against?
2. Work out MRR by hand for these first-correct ranks: 1, 3, missing, 2.
3. Why match on documents rather than chunks?

---

## Day 5: BM25, hybrid search and the experiment grid

**Goal:** keyword and hybrid retrieval working with filters, runs 1 to 9 in `runs.csv`, and an error analysis of the worst misses.

### Timetable

| Time | Block | What you do | Output |
| --- | --- | --- | --- |
| 9:00 to 9:30 | Concepts | S2: Keyword search (BM25); Hybrid search; Reciprocal rank fusion (RRF) | 3 notes |
| 9:30 to 10:00 | Cert | Task 2.1: GenAI concepts | Notes, with P1 as the example where you can |
| 10:00 to 10:45 | Build | BM25 index and `bm25_search()` | Works from the command line |
| 10:45 to 11:20 | Build | `rrf()` and `hybrid_search()` | Works from the command line |
| 11:20 to 11:40 | Build | Filter tests for both retrievers | Tests pass |
| 11:40 to 12:30 | Build | Run the grid (3 variants x 3 retrievers) on dev and holdout | Runs 1 to 9 logged |
| 12:30 to 13:00 | Build and close | Error analysis of the 5 worst misses; first draft of `experiments.md`; commit | Day 5 commit |

### Concepts: what each note should cover

- **BM25:** exact words and codes. Predict which golden questions BM25 will win (the KPI codes), then check tomorrow.
- **Hybrid search:** why vector search and BM25 fail on different questions.
- **RRF:** work one fusion example by hand. A chunk ranked 1st in vector search and 4th in BM25 scores 1/61 + 1/64.

### Cert: Task 2.1

- **Concepts:** tokens, chunking, embeddings, vectors, prompt engineering, transformer LLMs, foundation models, multimodal and diffusion models.
- **Use cases:** summarisation, assistants, translation, code, customer service, search, recommendations.
- **The foundation model lifecycle:** data selection, model selection, pre-training, fine-tuning, evaluation, deployment, feedback.
- **Cost and context:** token-based pricing and its effect on cost and performance; context engineering, which P1 is.
- **Agentic AI:** multi-agent systems, MCP, memory, tool use, orchestration. That's a preview of Week 2.

### Build: step by step

**1. BM25:**

- Tokenise with the lowercase regex `[a-z0-9]+(?:-[a-z0-9]+)*`, which keeps codes like "kpi-014" whole.
- Build one `BM25Okapi` per variant from the chunk file when the app starts; the corpus is small, so it fits in memory.
- `bm25_search(question, variant, k=20, filters=None)` applies the filters first, then scores.

**2. Hybrid:**

```python
def rrf(ranked_lists: list[list[str]], k: int = 60) -> list[tuple[str, float]]:
    scores = {}
    for lst in ranked_lists:
        for rank, cid in enumerate(lst, start=1):
            scores[cid] = scores.get(cid, 0) + 1 / (k + rank)
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)

def hybrid_search(question, variant, k=20, filters=None) -> list[Hit]   # fuse vector top 20 + bm25 top 20, return top k
```

**3. The grid:** `python -m eval.retrieval_eval --grid` runs all 9 combinations and appends 18 rows to `runs.csv` (9 for dev, 9 for holdout). Record the average retrieval latency too.

**4. Error analysis:** for the 5 questions where no method put the right document in the top 5, pick a cause for each from:

- vocabulary mismatch
- near-duplicate name (Active User vs Active Customer)
- trap document ranked first
- chunk cut badly
- golden set error

Write it up in `experiments.md` under "What failed and why".

### Common mistakes

- Comparing raw BM25 scores with cosine scores (RRF uses ranks for exactly this reason).
- A tokeniser that splits "KPI-014" into two words.
- Tuning anything on the holdout set.

### Definition of done

- [ ] BM25 and hybrid retrieval both work with filters, and the tests pass
- [ ] Runs 1 to 9 are in `runs.csv`, for dev and holdout
- [ ] The `experiments.md` draft has the grid table filled only from your runs, plus 3 observations and the error analysis
- [ ] Commit: `day5: bm25 + hybrid rrf + retrieval grid`

### Explain-it-back

1. Why does RRF use ranks instead of scores?
2. Which question type did BM25 win, and why?
3. Which chunking variant won, and would you trust that with 30 questions? What would you do to be surer?

---

## Day 6: Reranker, grounded answers and the judge

**Goal:** the full pipeline answers end to end with valid citations, refuses when it should, and has an eval script ready to run tomorrow.

### Timetable

| Time | Block | What you do | Output |
| --- | --- | --- | --- |
| 9:00 to 9:30 | Concepts | S2: Reranker; S3: Query rewriting; S3: Grounding | 3 notes |
| 9:30 to 10:00 | Cert | Tasks 2.2 and 2.3, plus a read-only Bedrock walkthrough | Notes |
| 10:00 to 10:40 | Build | Cross-encoder reranker; runs 10 and 11 | Runs logged, including the latency the reranker adds |
| 10:40 to 11:40 | Build | `llm.py` and `generate.py`: prompt, JSON, citation check, retry, refusal, trace log | Grounded answers |
| 11:40 to 12:10 | Build | `pipeline.py` and the command-line tool; test by hand on 6 questions; version the prompt if you change it | `python -m rag.ask` works |
| 12:10 to 12:50 | Build | `generation_eval.py` and 2 judge prompts; test on 3 questions only | The script is ready |
| 12:50 to 13:00 | Close | Log and commit | Day 6 commit |

### Concepts: what each note should cover

- **Reranker:** "retrieve wide, rerank narrow". Note the latency it added in your runs.
- **Query rewriting:** say "I would" add it for questions using abbreviations such as "NRR last qtr". It's a stretch goal, not built this week.
- **Grounding:** your refusal rule and the citation check are grounding in code. Note one answer where the refusal fired correctly.

### Cert: Tasks 2.2 and 2.3

- **Strengths of GenAI:** adaptability, responsiveness, conversation, content generation. **Limits:** hallucination, interpretability, inaccuracy, nondeterminism.
- **Choosing a model:** type, performance, capabilities, constraints, compliance, cost, latency, complexity.
- **AWS services:** Bedrock, SageMaker AI and JumpStart, Amazon Quick, Kiro, Strands Agents, AgentCore. Also: cost trade-offs (token pricing, provisioned throughput, custom models, regions).
- **Bedrock walkthrough:** read the Bedrock getting-started pages or course videos (model catalog, playground, Knowledge Bases, Guardrails). You don't need an account until Day 8.

### Build: step by step

**1. Reranker:**

- Load `CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")` once at startup.
- `rerank(question, hits, top_n=5)` scores each question and chunk pair and sorts.
- Runs 10 and 11: add the reranker to your 2 best configurations from Day 5 and log the recall, MRR and extra milliseconds.

**2. `llm.py` (the only file that knows the provider):**

```python
def complete(system: str, user: str, model: str, temperature: float = 0, max_tokens: int = 400) -> dict:
    # returns {"text": ..., "input_tokens": ..., "output_tokens": ..., "latency_ms": ...}
```

**3. `generate.py`:**

- **Context block:** number the chunks and label each with its chunk ID, title, certification and effective date:

```text
[1] id=KPI-007::v2::2 | Customer Churn Rate | Certified | 2026-04-01
<chunk text>
```

- **Parse:** strip any code fences, `json.loads`, then validate with a Pydantic `Answer(answer: str, citations: list[str], refused: bool)`.
- **Citation check:** every citation must be one of the retrieved chunk IDs. If not, retry once with the error attached. If it fails again, return the refusal message with `refused=True`.
- **Trace:** add one line per call to `results/traces.jsonl` with the question, config, prompt version, model, chunk IDs, tokens, latency and refused flag.

**4. Manual test (6 questions):**

- 2 definitions
- 1 KPI code
- the Churn v1 trap (should answer from v2 and mention the conflict)
- 2 unanswerable (should refuse)

If you change the prompt, save it as `answer_v2.txt`. Never edit a version you've already run.

**5. Judge prompts:**

`prompts/judge_correctness_v1.txt`:

```text
You grade an assistant's answer against a reference answer.
Question: {question}
Reference answer: {expected_answer}
Assistant answer: {answer}
Return JSON: {"verdict": "correct" | "partial" | "wrong", "reason": "<one sentence>"}
Grade on meaning, not wording. "partial" = right idea but a key element missing or wrong.
```

`prompts/judge_faithfulness_v1.txt`:

```text
You check whether an answer is fully supported by the given source chunks.
Answer: {answer}
Cited chunks: {cited_chunk_texts}
Return JSON: {"faithful": true | false, "unsupported_claims": ["..."]}
A claim is unsupported if the chunks do not state it or clearly imply it.
```

**6. `generation_eval.py`:**

- For each question, run the pipeline.
- Judge correctness (answerable questions only) and faithfulness (answered questions only).
- Check citation validity and refusal correctness in code.
- Write `results/generation_<config>.jsonl` and one summary row. Today, test on 3 questions only.

### Common mistakes

- The model wraps its JSON in code fences, so strip them before parsing.
- Letting the model cite IDs it wasn't given, which is why the check lives in code.
- Running the full judge eval today and burning budget before the pipeline is stable.

### Definition of done

- [ ] Runs 10 and 11 are logged, including latency
- [ ] `python -m rag.ask "..."` returns JSON with valid citations; the 2 unanswerable test questions are refused and the Churn trap is handled
- [ ] Every call is logged in `traces.jsonl`
- [ ] `generation_eval.py` runs on 3 questions
- [ ] Commit: `day6: reranker + grounded generation + judge eval script`

### Explain-it-back

1. Walk through one question end to end, naming each function it passes through.
2. Why is the citation check in code and not only in the prompt?
3. What are the known biases of an LLM judge, and how will your 10 hand grades test it?

---

## Day 7: Evaluate, ship the API, write it up, and Mock 1

**Goal:** real numbers from your own runs, a working `/ask` endpoint for Agent A, a README draft, a public repo, and Mock 1 scored.

### Timetable

| Time | Block | What you do | Output |
| --- | --- | --- | --- |
| 9:00 to 9:30 | Concepts | S3: RAG vs fine-tuning; Common failure modes; Retrieval metrics | 3 notes, using your own failures as examples |
| 9:30 to 10:00 | Cert | Official Practice Question Set: Domain 1 and 2 questions | Misses logged with the right answer and why |
| 10:00 to 10:40 | Build | Run the generation eval: best configuration and baseline (V1 vector, no reranker), all 40 questions | 2 summary rows |
| 10:40 to 11:00 | Build | Grade 10 answers by hand before reading the judge's verdicts; work out the agreement rate | Judge agreement noted |
| 11:00 to 11:30 | Build | FastAPI `/ask` and `/health`; 20 test calls for p50 and p95 latency | Endpoint works |
| 11:30 to 12:00 | Build | Final `experiments.md`, README draft, secrets check, make the repo public | Public repo |
| 12:00 to 13:00 | Mock 1 | 45-minute mock, then 15 minutes to score and log | Mock 1 scored out of 25 |

### Concepts: what each note should cover

- **RAG vs fine-tuning:** why P1 is RAG (definitions change every quarter).
- **Common failure modes:** use real cases from your Day 5 error analysis.
- **Retrieval metrics:** explain recall@5 and MRR with your own numbers, and say what they don't measure.

### Build: step by step

**1. The eval:** run `python -m eval.generation_eval --config best` and `--config baseline`. The summary row for each covers:

- correct and partly correct rates, and faithfulness rate
- citation validity
- refusals: correct refusals out of 8, and answerable questions wrongly refused
- average input and output tokens, cost per query, p50 and p95 latency

Work out cost from the provider's current price page, and write the price and date you used next to it.

**2. Hand grading:**

- Pick 10 answers at random.
- Grade each one as correct, partial or wrong before you open the judge's verdict.
- Agreement rate = matches out of 10. Write down any case where you disagree with the judge and why.

**3. API:**

- Load the models and indexes once, at startup.
- `POST /ask` and `GET /health`, following Part B, section 6.6.
- Test with the built-in `/docs` page, then make 20 calls and record p50 and p95.

**4. `experiments.md` (final):**

- the grid table (runs 1 to 11)
- the generation table (best vs baseline)
- cost and latency
- 3 to 5 findings in plain words
- what failed and why
- limits: synthetic corpus, 40 questions, a single judge model

**5. README sections:**

1. What it is, as one honest line: a prototype on synthetic data.
2. The problem and users.
3. An architecture diagram (a simple boxes-and-lines picture is fine).
4. How to run it.
5. Results (link to `experiments.md`).
6. Design choices and trade-offs.
7. Limits and next steps.

**6. Before making the repo public:**

- Check that `.env` isn't tracked (`git ls-files | findstr .env` should show only `.env.example`).
- Search the history for your key prefix.
- Then set the repo to public.

**7. Mock 1:** open a new chat and paste the prompt from the Checklist.

- Role: "Director, Data and AI Strategy". Topic: "RAG design and basics".
- Answer out loud first, then type a short version.
- Score it with the 25-point rubric, and write your top 3 gaps and 5 retest questions in the Checklist's mock table.
- Section 15.4 of the Cheat Sheet is your answer template for "design a RAG system".

### Definition of done

- [ ] 2 generation summary rows from your own runs, with cost and latency
- [ ] Judge agreement worked out from 10 hand grades
- [ ] `/ask` works and p50 and p95 are recorded
- [ ] `experiments.md` final, README draft done, repo public with no secrets
- [ ] Mock 1 scored, with the top 3 gaps logged
- [ ] Commit: `day7: generation eval + api + readme; week 1 done`

### Explain-it-back

1. What is your headline result, in one sentence with your own numbers?
2. What would you fix first with one more week, and why?
3. How will Agent A use `/ask` on Day 9?

---

## End of Week 1 review (15 minutes, after Mock 1)

Tick the Week 1 checkpoint in the Checklist, then answer these in the daily log:

1. What took longer than planned, and why?
2. Which concept can you now explain with your own numbers?
3. Which Mock 1 gap goes into next week's concept notes?
4. Is anything from the cut list worth doing in Week 4?
5. Did the job search keep running? If not, fix that before Day 8.
