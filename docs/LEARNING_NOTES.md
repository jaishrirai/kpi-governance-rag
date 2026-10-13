# KPI Governance RAG: Learning Notes (single file)

Keep every concept note here. One file, one section per topic.

Contents:
1. Steps 1.2 and 1.3: raw sources and ingestion
2. Document metadata and the manifest
3. Step 1.4: chunking (added after the run)

---

## 1. Steps 1.2 and 1.3: Raw Sources and Ingestion

### 1.1 Raw source files

The project uses synthetic documents for Kestrel Retail Group. These are the knowledge sources that the RAG system will eventually search.

| Source | Location | Purpose |
|---|---|---|
| KPI definitions | `data/raw/kpis/` | Define KPIs, formulas, filters, source tables, dashboards and caveats. |
| Data catalog | `data/raw/catalog/data_catalog.csv` | Describe dashboards and tables and identify their linked KPIs. |
| SOPs | `data/raw/sops/` | Explain processes, steps and responsible roles. |
| Policy PDFs | `data/raw/pdfs/` | Contain formal governance and policy information. |
| FAQ | `data/raw/faq/` | Provide informal answers and notes. |

The corpus contains 50 logical documents: 21 KPI documents, 15 catalog rows, 8 SOPs, 5 policy PDFs and 1 FAQ.

**Important:** 50 logical documents do not mean 50 physical files. For example, one catalog CSV contains 15 rows, and each row becomes a separate logical document during ingestion.

Two intentional conflicts are included in the corpus:
- A deprecated Churn Rate v1 document.
- An FAQ that defines Active Customer using a 90-day window, conflicting with the certified 30-day definition.

These are test cases for governance-aware retrieval.

### 1.2 The manifest

File: `data/corpus_manifest.csv`

The manifest is the master document register. It identifies documents and supplies metadata such as:
- Document ID and title.
- Document type and business domain.
- Owner and certification status.
- Version and effective date.
- Source file path.

**Purpose:** establish a reference for document identity and metadata, so the corpus can be checked for inconsistencies.

The manifest is not the actual business knowledge contained in the source documents.

In this project, the manifest was created during corpus setup and is read by `ingest.py`. The ingestion code does not update it automatically.

When documents are added or changed, the manifest and relevant duplicated metadata must be maintained consistently. The corpus checker validates selected relationships, but it does not prove every business statement is correct.

In a production system, the same responsibility could be handled by a database, metadata registry or an existing enterprise document catalog synchronized with the RAG pipeline.

### 1.3 A KPI Markdown document

Example: `data/raw/kpis/kpi-010_net_revenue_retention.md`

The file has two parts.

**A. YAML front matter: metadata**

Fields include `doc_id`, `title`, `doc_type`, `domain`, `owner`, `certification`, `version` and `effective_date`.

**B. Markdown body: business knowledge**

The seven sections are:
1. Definition
2. Formula
3. Grain and filters
4. Source tables
5. Dashboards
6. Caveats and exclusions
7. Change history

The sections make the document understandable to people and provide useful boundaries for heading-based chunking.

The change history is a human-maintained record of important changes; it is not a replacement for Git or document revision history.

### 1.4 Ingestion

File: `src/rag/ingest.py`

**Purpose:** read sources in different formats and convert them into a common representation.

The loader uses different functions because each format has a different structure:

- `read_csv(path)`: reads CSV rows as dictionaries.
- `load_markdown(path)`: removes the YAML front matter and retains the Markdown body.
- `catalog_texts(path)`: converts catalog rows into labelled text.
- `load_pdf(path)`: extracts and combines text from PDF pages.
- `pdf_page_text(page)`: reconstructs headings, paragraphs and tables from a page.
- `table_rows_as_lines(table)`: turns table rows into labelled text.
- `load_all()`: selects the appropriate reader for each manifest row and combines metadata with extracted text.
- `main()`: writes the resulting records to JSONL and prints basic diagnostic counts.

#### Why PDF extraction needs special handling

PDFs can contain headings distinguished by font size and boldness, as well as tables whose cells may be extracted separately.

The loader uses visual cues to reconstruct headings and turns table rows into labelled text, for example:

`ID: KPI-001 | Owner: Head of Finance Analytics | Status: Certified`

This helps preserve the relationship between column names and values.

The approach is tailored to the synthetic PDFs and is not guaranteed to work perfectly on arbitrary PDF layouts.

#### Normalization

Normalization here means converting differently structured source data into a consistent representation without discarding important information.

For example, the catalog's structured CSV rows become labelled text that can later be processed alongside Markdown and PDF content.

### 1.5 The ingestion output

File: `data/processed/documents.jsonl`

Each line contains one JSON object representing one logical document. Each record contains the manifest fields plus a `text` field.

The `text` field holds the extracted or normalized content. The metadata fields identify the document and describe its properties.

JSONL means JSON Lines: one JSON object per line, not one large JSON array.

Running ingestion regenerates this processed output. It does not automatically create chunks, embeddings or a vector index.

### 1.6 How the stages differ

**Manifest:** identifies documents and supplies their metadata.

**Loader / ingestion:** extracts content from each source format and combines it with metadata.

**`documents.jsonl`:** contains the common records that downstream stages can process, with one logical document per line.

**Chunking:** divides the loaded text into smaller searchable pieces while trying to preserve enough context.

**Retrieval:** finds the pieces most relevant to a user's question.

### 1.7 The core distinction

- Ingestion preserves and standardizes the meaning and structure of source content as it is extracted.
- Chunking creates appropriately sized units for search.
- Retrieval selects relevant units for a question.

Good ingestion and chunking improve the evidence available to the RAG system. They do not, by themselves, guarantee that the final answer is correct or prevent all hallucinations.

---

## 2. Document metadata and the manifest

### 2.1 The key architectural principle

Keep document discovery, metadata management, content processing, and search indexing as distinct responsibilities. The manifest is one simple way to manage the first two in the prototype; a production system can replace it with a synchronized registry or existing enterprise catalog without changing the underlying principle.

In a real enterprise, documents are continuously created, updated, moved, retired, and sometimes deleted. A manually maintained CSV can become stale.

A manifest does not have to be static. It has to remain an accurate, authoritative record of the documents the system is allowed to process.

A manifest is a design pattern, not necessarily a CSV file.

### 2.2 Three ways to manage document metadata

**Option A: Manually maintained manifest (the prototype).** A CSV records each document and its metadata. A person edits the CSV when documents are added or changed.
- Advantages: simple, transparent, easy to inspect and validate.
- Limitations: manual work, risk of stale entries, and difficulty managing large numbers of changing documents.
- Fit for P1: appropriate for the 50-document synthetic corpus.

**Option B: Metadata registry or database.** Store document IDs, source locations, versions, ownership, certification, timestamps, and processing status in a database or metadata service. A connector or ingestion process updates the registry when it discovers changes.
- Advantages: easier to query, update, validate, and manage at scale.
- Limitations: requires infrastructure, synchronization logic, access controls, and operational maintenance.

**Option C: Synchronize with existing enterprise systems.** Treat an existing system, such as a document repository, knowledge platform, or governed data catalog, as the authoritative source. Use APIs, change notifications, or scheduled scans to synchronize relevant metadata into the RAG pipeline.
- Advantages: reduces duplicate manual maintenance and can preserve the source system's permissions and lifecycle information.
- Limitations: connectors must handle updates, deletions, permissions, failures, and differences between systems.

### 2.3 Interview line

"I separated discovery and metadata from processing and indexing. My prototype uses a manifest as the single source of truth. In production I'd sync that role from a governed catalog, so the design stays the same."

---

## 3. Step 1.4: Chunking

Status: the three variants are written and tested (18 checks pass with the loader). Numbers below are filled in from the real run.

- V1 fixed: about 400 tokens per piece, 60 tokens of overlap, cut at line breaks or spaces.
- V2 by heading: one piece per `##` section. A section over the 450-token cap is split again, and every piece keeps its heading.
- V3 by unit: one piece per document. A document over the cap is split again.
- The cap is measured on the header plus the body, because the header is embedded too.
- Table rows are kept whole: the chunker cuts at line breaks first, so one labelled row is never cut in half.

Predictions and results are recorded in the milestone walkthrough, not here.
