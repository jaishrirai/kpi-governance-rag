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
