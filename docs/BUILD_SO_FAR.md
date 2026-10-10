# Build so far (plain words)

Claude adds a short entry here at the end of every step. Each entry answers: what did we make, why, and how does it connect to the next piece.

## The big picture
We are building a question-answering assistant for a fictional company, Kestrel Retail Group. You ask "How is churn defined? Who owns it? Is it certified?" and it answers from company documents, shows which document it used, and says "I don't know" if the answer is not there.

The pipeline we are building, in order:
1. Documents (the knowledge)
2. Loaders (read every document into one common format)
3. Chunking (cut documents into small pieces)
4. Embeddings + vector DB (turn pieces into numbers so we can search by meaning)
5. BM25 (a second search that matches exact words, like "KPI-014")
6. Hybrid + reranker (combine both searches, then sort the best results)
7. Generation (an AI model writes the answer using only the best pieces, with citations)
8. Evaluation (measure how good it is with 40 test questions)
9. Demo (Streamlit page)

## Step 1.1: Environment (done)
- Made: a Python environment (`.venv`) with all libraries, and `scripts/smoke_test.py`.
- Why: to check that the tool that turns text into numbers (the embedding model) works.
- Result: every text becomes 384 numbers. "churn" and "attrition" scored 0.777 (close in meaning), "churn" and "inventory" scored 0.664. The scores are all in a narrow band, so we compare by rank, not by a fixed cutoff.

## Step 1.2: Synthetic corpus (in progress)
- Made: 50 invented company documents in `data/raw/`, plus `data/corpus_manifest.csv`.
- Why: a RAG assistant needs documents to search. We use invented ones so there is no real company data.

What the 50 documents are:

| Folder | Count | What it is |
|---|---|---|
| `data/raw/kpis/` | 21 | One file per KPI (a business number like Net Revenue or Churn Rate). 20 KPIs plus the old Churn Rate v1 |
| `data/raw/catalog/` | 1 file, 15 rows | A table listing data tables and dashboards and who owns them |
| `data/raw/sops/` | 8 | Step-by-step company procedures (SOPs), for example how a KPI gets certified |
| `data/raw/pdfs/` | 5 | Policy PDFs, POL-01 to POL-05 |
| `data/raw/faq/` | 1 | A team FAQ |

The manifest is one table with a row per document: doc_id, title, type, domain, owner, certification (Certified / Provisional / Deprecated), version, date, file path. It is the single source of truth for who owns what.

Two traps, on purpose, to test whether the assistant is careful:
- **Churn Rate v1** is old and Deprecated. The assistant should prefer the current v2 (KPI-007).
- **The FAQ** says "Active Customer" means 90 days. The certified KPI-006 says 30 days. The assistant should trust the certified document.

What a KPI file looks like (example: `kpi-010_net_revenue_retention.md`):
- A header block between `---` lines (YAML) with the metadata. Here `version: "1.4"` is in quotes so it stays text. Without quotes, a computer reads it as the number 1.4, and a version like `1.10` would turn into `1.1`.
- Then sections: Definition, Formula, Grain and filters, Source tables, Dashboards, Caveats, Change history. Every KPI file has the same sections, so retrieval is predictable.

POL-04 (the question you asked):
- POL-04 is `pol-04_kpi_glossary_summary.pdf`, a policy PDF that is a glossary: a table of all 20 KPIs with one short definition each.
- `scripts/make_pdfs.py` makes the 5 PDFs. For POL-04, only the one-line definitions are typed in the script. The title, owner and certification columns are read from the manifest.
- So if the manifest says a KPI is Provisional, the PDF says Provisional too. The two cannot disagree by accident. This is what Question 2 asks about.

### Corpus checker: `scripts/check_corpus.py` (done)
- Made: a script that reads all 50 documents and reports anything that disagrees. It changes nothing.
- Why: I generated the documents, so I could have made mistakes. Wrong owners or a dashboard that does not exist would become wrong answers later, and we would blame the retrieval.
- What it checks:
  1. Every file listed in the manifest exists, and no file is missing from the manifest.
  2. Each document's YAML header (owner, version, status and so on) equals its manifest row.
  3. No KPI or SOP file is over 1,800 characters (so one file fits in one chunk later).
  4. Dashboards and source tables named in a KPI file exist in the catalog, and the catalog links back to that KPI.
  5. Catalog rows have the same owner, domain and status as their manifest rows, and their linked KPIs exist.
- Result: 50 documents, 15 catalog assets, all checks pass. The first run showed 5 false alarms from empty placeholder files (`.gitkeep`). That was a bug in the checker, not the corpus. I also broke a copy on purpose (changed an owner, renamed a dashboard) and the checker caught both, so a passing run means something.
- Not checked: the hand-typed one-line definitions in the glossary PDF (POL-04). You decided that is fine for now.

Still to do in 1.2: you skim 5 files, then the wrap-up (CONCEPTS.md note, commit, close #3).
