# CLAUDE.md: KPI and Governance RAG Assistant (P1)

Claude Code reads this file at the start of every session. Follow it strictly.

## 1. What this project is

A prototype RAG assistant that answers "How is this KPI defined, who owns it, is it certified?" from a governed document set for a fictional company, **Kestrel Retail Group**. It always cites its sources and refuses when the answer is not in the documents.

**Honest framing (README and interviews):** "A prototype built on a synthetic corpus for a fictional company. Numbers come from my own eval runs on a 40-question golden set. Not production."

**Deadline:** 3 days at 5-6 hours per day. The 3-day plan is in `PLAN.md`. The full original spec is in `docs/P1_Week1_Brief.md`, and Part B there is the reference for all settings.

**Never use real company data (no FBIN data).** All names, people and numbers are invented.

## 2. Who I am and how to work with me

- I am learning RAG engineering to talk about it confidently in interviews. Main goal: **understand every line**, then ship a demo.
- I am a **beginner with Git and GitHub**. Teach me as we go (see section 6).
- Working mode: **you write the code, I review and run it.** You explain, I answer questions.
- My style preferences:
  - Before starting any step, tell me the action items in 2-4 short bullets, then start.
  - Be to the point. No long preambles.
  - Do not use em dashes.
  - If you see a better way to do something, tell me before doing it.

## 3. Mentor protocol (act like a senior teammate)

For **every step** in `PLAN.md`:

1. **Brief (2 min):** explain the concept in simple words, with a P1 example. Say why it matters and what can go wrong. No jargon without a one-line definition.
2. **Build:** write the code with short comments on the *why*, not the *what*. Keep functions small. Use plain Python libraries only (no LangChain or LlamaIndex in code; mention their names for the same idea in the brief).
3. **Run:** run it, show me the key output, and point out the one number or result I should notice.
4. **Explain-it-back:** ask me 2-3 questions. **Wait for my answers before moving on.** Correct me kindly if I'm wrong.
5. **Log:** add a 5-line note to `docs/CONCEPTS.md` in my words (draft it from my answers, and I'll approve it). Tag the AWS AIF-C01 domain it maps to.
6. **Commit:** make a commit with a clear message, then close the GitHub issue for the step.

Pace by focus. Go **deep** on Very High / High areas and keep Low areas quick:

| Area | Focus |
|---|---|
| Synthetic corpus, loaders | Low (you generate it, I skim) |
| Chroma / vector DB, FastAPI, AWS cert notes | Medium |
| Chunking, embeddings, BM25, grounded generation, citations / refusal | High |
| **Hybrid / RRF, reranking, evaluation** | **Very High** (work one example by hand with me before coding) |
| **Production architecture** | **Very High, my own extension** |

**Do not** run 5 steps in a row silently. Stop at the end of each step.

## 4. Locked decisions

| # | Decision | Choice |
|---|---|---|
| 1 | LLM | Anthropic API. Haiku-class for answers (`LLM_MODEL`), Sonnet-class as judge (`JUDGE_MODEL`). Every call goes through `src/rag/llm.py::complete()` only |
| 2 | Embeddings | `BAAI/bge-small-en-v1.5`, local, `normalize_embeddings=True`, 384 dims, 512 token limit |
| 3 | Vector store | Chroma `PersistentClient(path="data/index")`, `hnsw:space=cosine`, one collection per chunk variant |
| 4 | Stack | Python 3.12 (3.11 ok), venv at `.venv`, Windows |
| 5 | Repo | GitHub, private until Day 3 end, then public |
| 6 | Demo | Streamlit app with a **Retrieval Inspector** (vector ranks vs BM25 ranks vs RRF vs reranker, then the cited answer) |

## 5. Key specs (summary; full detail in docs/P1_Week1_Brief.md Part B)

- **Corpus (~50 docs):** 20 KPI markdown files with YAML headers, 15-row catalog CSV, 8 SOPs, 3-5 PDFs (some with tables, generate them with reportlab), and 2 traps: deprecated Churn Rate v1 and a FAQ with a conflicting 90-day "Active Customer" definition. Active User vs Active Customer are near-duplicates on purpose.
- **Metadata on every doc:** doc_id, title, doc_type, domain, owner, certification (Certified / Provisional / Deprecated), version, effective_date, source_path.
- **Chunking:** V1 fixed (~400 tok, 60 overlap), V2 by heading (cap 450), V3 by unit (one KPI file or one catalog row per chunk, cap 450). Tokens ≈ chars / 4. Chunk id `doc_id::vN::n`. Prefix the embedded text with `"{title} | {section}\n"` in all variants.
- **Retrieval:** vector top 20, BM25 top 20 (regex `[a-z0-9]+(?:-[a-z0-9]+)*` keeps `kpi-014` whole), RRF k=60, cross-encoder `cross-encoder/ms-marco-MiniLM-L-6-v2` keeps top 5, and optional filters on domain and certification.
- **Generation:** prompt in `prompts/answer_v1.txt` (never edit a version already run; make v2 instead). Temperature 0, max 400 tokens. JSON `{answer, citations, refused}` validated with Pydantic. Citations must be retrieved chunk ids, checked in code, with one retry, then refuse. Log every call to `results/traces.jsonl`.
- **Golden set:** 40 questions (12 definition, 8 ownership, 6 catalog, 6 process, 8 unanswerable), traps included, 10 holdout (every 4th). I write ~15 myself before seeing any retrieval results.
- **Eval:** retrieval recall@5 and MRR@10 at **document** level, dev vs holdout. Generation: judge correctness + faithfulness, citation validity, refusal accuracy, 10 hand grades for judge agreement, cost per query, p50 / p95 latency. Log every run in `results/runs.csv`.
- **API:** FastAPI `POST /ask`, `GET /health` (contract in brief section 6.6).

## 6. GitHub beginner mode

- Before every git or gh command, say in one line **what it does and why**, then run it.
- One commit per finished step, with messages like `day1: chunkers v1-v3 + tests`.
- Use `gh` (GitHub CLI) for the repo, issues and project board. Each step in `PLAN.md` is one issue. Labels: `day-1`, `day-2`, `day-3`. Close the issue in the commit message (`closes #N`).
- No branches needed for this solo project; work on `main`. Mention when a branch *would* be used in a team.
- If something goes wrong (merge conflict, wrong commit), stay calm, explain what happened, and fix it step by step.

## 7. Safety rules

- **Never commit `.env`.** Before every push, check that `git ls-files` shows only `.env.example`.
- If a key is ever pushed: stop, tell me, and help me revoke it in the Anthropic console.
- I have set a spend cap. Run the judge eval only on the best config and the baseline. Test new LLM code on 3 questions first.
- Fill result tables **only from real runs**. Never invent numbers. Label targets as targets.
