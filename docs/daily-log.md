# Daily log

## 2026-10-03 / 2026-10-04: Day 0 + Day 1 (Steps 1.1, part of 1.2)

**What we did**
- Day 0: installed GitHub CLI, set git name and email, `git init`, private repo `jaishrirai/kpi-governance-rag`, labels day-0 to day-3, 18 issues (one per PLAN step), Project board "P1 KPI Governance RAG" (To do / Doing / Done). Issue #1 closed.
- Plan change: LLM switched from Anthropic to Gemini free tier; split build mode added (I write the core logic in "You build" steps). Learning-visibility rules added to CLAUDE.md section 3.
- Step 1.1: `.venv` on Python 3.11.7, torch CPU 2.14.1, all requirements installed. Smoke test Part A: 384 dims, sim(churn, attrition) = 0.777, sim(churn, inventory) = 0.664. Lesson: bge scores sit in a narrow band, so rank instead of using a fixed cutoff. CONCEPTS.md notes added. Issue #2 closed.
- Step 1.2 (in progress): manifest with 50 docs; 21 KPI files (incl. Churn v1 trap), 15-row catalog CSV, 8 SOPs, FAQ trap (90-day Active Customer), 5 policy PDFs from `scripts/make_pdfs.py` (POL-03, POL-04, POL-05 have tables).

**Mistakes and fixes**
- Created the project board twice (output-filter bug); deleted the empty duplicate.
- Ran `make_pdfs.py` before showing it to me; this led to the new rule 4 (show any multi-file script before running it).

**Where we stopped**
- Step 1.2, issue #3 (board: Doing). Waiting on my answers to 2 questions: why `version: "1.4"` is quoted in YAML, and what building the glossary table from the manifest prevents.

**Next step**
1. Answer the 2 questions; open `kpi-010_net_revenue_retention.md` and `make_pdfs.py` in VS Code.
2. Claude shows `scripts/check_corpus.py` before running it, then runs the consistency checks.
3. I skim 10 files and fix anything odd; explain-it-back; CONCEPTS.md note (Hallucination, Structured output); commit with `closes #3`.

## 2026-10-09: Back after a 5-day break, plan cut to 2 days

**What we decided**
- Only 2 days (5-6h each) are left, so `PLAN.md` was rewritten as a 2-day plan. Day 1: steps 1.2 to 1.7 plus 2.1. Day 2: 2.2 to 2.5, 3.1, 3.3, 3.5. Day 2 is a stretch (about 6h20 planned).
- Cuts: FastAPI (3.2) moved to the agents project; production architecture doc (3.4) written by me outside Claude Code (README links to it); I write 10 golden questions and Claude drafts 30; generation eval on 20 questions; corpus skim is 5 files.
- Kept: every [YOU BUILD] step, the reranker, the 9-run retrieval grid, the Streamlit demo.
- Order change: I skim the 5 files first, then write my 10 golden questions, with no searches before the questions exist.
- Explain-it-back is 1 question on Low and Medium steps. Batched CONCEPTS.md notes are required in every wrap-up, before the commit.
- Cut order if behind: demo video, then judge faithfulness, then Streamlit extras.
- GitHub: issues #15 (FastAPI) and #17 (production architecture) closed with comments.

**Also done today**
- Added `GEMINI_API_KEY`, `LLM_MODEL`, `JUDGE_MODEL` to `.env` (checked: ignored by git, not tracked, values not read). The key is not tested until Step 2.5.
- Answered the YAML and single-source-of-truth questions. Chose not to add a check on the hand-typed glossary definitions in POL-04.
- New CLAUDE.md rule 5: recap in simple words before questions, saved in `docs/BUILD_SO_FAR.md`.
- Wrote and ran `scripts/check_corpus.py` (all checks pass; tested on a broken copy). I skimmed 5 files.
- Wrote 11 golden questions (G-001 to G-011) before any search was run. Expected doc ids were drafted by Claude and reviewed by me; G-005 key is POL-04 only.
- Step 1.2 wrap-up: CONCEPTS.md notes added, issue #3 closed by the commit.

- Step 1.3: wrote `src/rag/ingest.py` and ran it: 50 documents (21 kpi, 15 catalog, 8 sop, 5 policy, 1 faq), no empty texts.
- PDF quality note: pypdf puts each table cell on its own line, so table rows lose their structure and wrapped cells split mid-sentence. Words are intact (keyword search is fine), but column meaning is guessed. PDF headings have no markdown marker, which matters for the V2 chunker.

**Where we stopped**
- Step 1.3 code is written and run. Waiting on my answer to the 1 question, then the day-end wrap-up (CONCEPTS.md notes, commit). Next is Step 1.4 (chunking).

## 2026-10-13 to 2026-10-16: Steps 1.4 to 2.5 (chunking to grounded answers)

**What we did**
- 1.4 to 1.6: three chunkings (V1 52 chunks, V2 265, V3 52), Chroma index with `bge-small-en-v1.5`, BM25 with a code-preserving tokenizer. Found and fixed: the document code was missing from V2 chunks, so a chunk header `{title} ({doc_id}) | {section}` was added (decision 8) and owner, status and version were appended to every document (decision 9).
- Golden set: 40 questions: 30 dev (24 answerable, 6 unanswerable), 10 holdout (8 answerable, 2 unanswerable). Audited, labels v2.
- 2.2 retrieval eval: recall@5 (fractional, headline), hit@5, MRR@10 at document level; baseline runs 1 to 14 (runs 1 and 2 dirty, repeated clean as runs 3 and 4). V1 + vector: dev 0.815 / 1.000 / 0.938.
- 2.3 hybrid (RRF k=60): lost to vector on dev for V1, V2 and V3. 2.4 cross-encoder rerank: dev mixed, holdout better on 8 questions, about 50x slower. Retrieval phase closed; vector V1 is the default, hybrid and rerank are optional (decisions 10 to 12).
- 2.5 grounded generation: `llm.py`, `generate.py`, `prompts/answer_v1.txt`, `validate.py` (my own pseudo-logic matched the final design: provenance and consistency), `pipeline.py`, `python -m rag.ask`, `results/traces.jsonl`. Six hand tests recorded in `results/step2_5_hand_tests.md`.

**What I learned or decided**
- Fusion can hurt when one ranker is weaker; a small test set limits the claim; relevance is not authority (a text-only reranker promoted the informal FAQ).
- Ungrounded Gemini answered KPI-010 fluently and wrongly; with retrieved context and a refusal rule it either answered from the chunk or refused.
- Findings carried to Step 3.1: vector search missed KPI-010 when asked by code; answers are accurate but sometimes drop key facts. Not patched; to be measured first.
- Process: predict before running, log runs on a clean commit, never tune on holdout.

**Where we stopped**
- The Step 2.3 to 2.5 commits are local and not pushed. Pending decisions: the one retry on citation failure, and the Step 2.6 governance step. Then Step 3.1.

## 2026-10-18: Wrap-up housekeeping

**What we did**
- Added `LEARNING_NOTES.md` Section 13 (line-by-line walkthrough of `pipeline.py`) and Section 14 (my review of the pipeline tests, with small additions).
- Brought `PLAN.md`, `decisions.md` (10 to 18), this log and `CONCEPTS.md` up to date through Step 2.5.

**Where we stopped**
- Review the diff, then commit locally. Push only when I ask. Next: decide the retry, Step 2.6, then Step 3.1.
