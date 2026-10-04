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
