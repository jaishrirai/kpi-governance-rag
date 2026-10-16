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

---

## Section 4: Chunking recap, embeddings and Chroma (Steps 1.4 and 1.5)

# RAG Learning Notes: Chunking, Embeddings and Vector Search

These notes cover Step 1.4 and prepare you for Step 1.5. The goal is to understand the concepts well enough to explain the design choices in an interview, not just memorize definitions.

## Part 1 — Chunking

### 1. What is chunking?

Chunking is the process of dividing a document into smaller pieces of text called chunks so that a RAG system can retrieve relevant information without always needing the entire document.

For example, a KPI document may contain its definition, formula, source tables, caveats and change history. If a user asks only for the formula, retrieving the Formula section may be sufficient.

Chunking comes after ingestion:

`Raw files → Ingestion → Normalized documents → Chunking → Embeddings → Retrieval`

- Ingestion: extracts content and metadata from Markdown, CSV and PDF files into a common document format.
- Chunking: divides that content into searchable units.
- Embeddings: represent each chunk numerically so that semantic similarity can be calculated.
- Retrieval: selects chunks relevant to the user's question.

### 2. Why is chunking necessary?

Without appropriate chunking, two problems can occur:

- Chunks that are too large: contain unnecessary information, making the relevant passage harder to isolate and potentially exceeding model input limits.
- Chunks that are too small: may lose context needed to interpret a definition, formula or business rule.

The objective is to balance focused retrieval with sufficient context.

### 3. Three chunking strategies in this project

Your `src/rag/chunking.py` implements three variants. The reported figures below are from the run results you shared.

| Feature                  | V1: Fixed-size                 | V2: Heading-based                       | V3: Document-based                                 |
| ------------------------ | ------------------------------ | --------------------------------------- | -------------------------------------------------- |
| Approach                 | Fixed text windows             | Split at `##` headings                  | Keep the document together when possible           |
| Target size              | About 400 tokens               | One chunk per section                   | One chunk per document                             |
| Overlap                  | About 60 tokens when splitting | Used if a section must be split         | Used if a document must be split                   |
| Chunks produced          | 52                             | 230                                     | 52                                                 |
| Average estimated tokens | 238                            | 55                                      | 240                                                |
| Main advantage           | Simple, consistent windows     | Preserves section meaning               | Keeps broader context together                     |
| Main risk                | Can split related content      | Related sections become separate chunks | May include irrelevant content from other sections |

The approximate token count uses `len(text) // 4`, rather than a model-specific tokenizer. The header is included in the chunk text.

Why are the averages different?

V2 creates separate chunks for individual sections, so it produces many more small chunks. V3 keeps whole documents together when they fit, so its chunks are generally larger.

V3 produces 52 chunks rather than 50 because the POL-04 glossary needs two chunks to stay within the cap.

### 4. What is overlap?

Overlap is the portion of text repeated between consecutive chunks.

Suppose the text is split into:

- Chunk 1: A, B, C, D, E
- Chunk 2: D, E, F, G, H

D and E are repeated. That repetition is overlap.

Why use it? A relevant explanation might cross a chunk boundary. Overlap gives the next chunk some of the preceding context, reducing the chance that the information becomes difficult to interpret.

In this project, V1 targets approximately 60 tokens of overlap. The implementation uses character-based splitting, so the actual overlap can vary.

Trade-off:

- More overlap means more repeated text and potentially more chunks or stored content.
- Less overlap reduces duplication but may make cross-boundary context harder to retrieve.

Reducing overlap does not necessarily reduce the chunk count. It depends on the text lengths and where the splitting function places boundaries.

### 5. How does the code preserve context?

The chunker uses several mechanisms:

- Headings: V2 identifies Markdown `##` sections such as Formula and Caveats.
- Headers: each chunk begins with the document title and section, for example `Net Revenue Retention (KPI-010) | Formula`. The document code is part of the header on purpose: in Step 1.6 we found that without it, a search for "KPI-014" could not find the KPI-014 file in V2.
- Metadata: chunks retain fields such as `doc_id`, title, domain, owner, certification, version and effective date.
- Overlap: long text split into multiple pieces can repeat some preceding content.
- Cut boundaries: the code tries to cut at line breaks first and spaces second, which can help preserve table rows.

These techniques help retain context and traceability. They do not guarantee that every chunk will be self-contained or that retrieval will always find the correct evidence.

## Part 2 — Chunking failure vs retrieval failure

This distinction is important for debugging a RAG system.

Imagine the correct answer exists in the original corpus, but the system returns three irrelevant chunks.

That does not automatically mean chunking was wrong. The failure could be in retrieval.

| What happened                                                                       | Likely problem                                                   |
| ----------------------------------------------------------------------------------- | ---------------------------------------------------------------- |
| The chunker accidentally omitted the relevant text                                  | Ingestion or chunking                                            |
| The relevant text exists in a clear, useful chunk, but retrieval does not select it | Retrieval, embedding quality, ranking or retrieval configuration |
| The text was split so that its meaning depends on missing context                   | Chunking quality, though retrieval can contribute                |
| The correct evidence was retrieved, but the LLM gave the wrong answer               | Answer generation or evidence interpretation                     |

These are diagnostic clues, not absolute rules. More than one stage can contribute to a failure.

### A practical example

Question: "What is the NRR formula, and what does it exclude?"

1. Chunking problem: the relevant formula or exclusion text was lost or separated from the context needed to interpret it.
2. Retrieval problem: the Formula and Caveats chunks exist and contain the answer, but the search returns unrelated chunks instead.
3. Generation problem: both correct chunks are retrieved, but the LLM misinterprets them.

How to answer this in an interview:

> I would trace the failure through the pipeline. First, I would verify that ingestion and chunking preserved the required evidence. Then I would check whether retrieval selected the relevant chunks. If the correct evidence was retrieved but the answer was still wrong, I would investigate the generation stage.

This is a useful debugging principle: check where the evidence was lost before changing the architecture.

## Part 3 — Step 1.5: Embeddings

### 1. What is an embedding?

An embedding is a numerical representation of text that captures aspects of its meaning.

A computer can store and compare text directly, but ordinary text comparison does not naturally recognize that different words can express similar ideas.

For example:

- "Customer churn increased."
- "Customer attrition went up."

These sentences use different words but express similar ideas. An embedding model can map them to vectors that are relatively close in the embedding space.

An embedding is not a summary, a database row, or an answer. It is a numerical representation used to compare text.

### 2. What does a vector look like?

Conceptually, a vector is a list of numbers:

```
[0.12, -0.08, 0.41, 0.03, ...]
```

The real vector from your project's model contains 384 numbers. This was established in your Step 1.1 smoke test using `BAAI/bge-small-en-v1.5` through Sentence Transformers.

You do not need to interpret each number individually. The important point is that the vector lets the system compare the representation of a question with representations of stored chunks.

### 3. How does embedding-based search work?

Consider two chunks:

- Chunk A: "Customer churn measures customers lost over a defined period."
- Chunk B: "Inventory turnover measures how frequently inventory is sold and replaced."

A user asks: "How do we measure customer attrition?"

The system embeds the question and compares it with the stored chunk vectors. Chunk A may be ranked higher because its meaning is more relevant to the question.

User question

"How do we measure customer attrition?"

Embedding model

Converts the question into a 384-dimensional vector

Similarity search

Compare the question vector with stored chunk vectors

Retrieved chunks

Return the highest-ranked relevant candidates

This is called semantic search because it searches by similarity of meaning, rather than relying only on exact word matches.

However, embeddings do not guarantee that synonyms or related concepts will always match correctly. The model can still rank an irrelevant chunk too highly or miss the best chunk.

### 4. What determines the vector's length?

This is one of Claude's prediction questions.

The embedding model determines the vector dimension.

Your configured model, `BAAI/bge-small-en-v1.5`, produces a vector with 384 dimensions. The length is not determined by the number of source documents, the number of chunks, or the number of words in a chunk.

For example:

| Input text                   | Output vector length |
| ---------------------------- | -------------------- |
| A short sentence             | 384 numbers          |
| A long KPI section           | 384 numbers          |
| A chunk containing a formula | 384 numbers          |

The numerical values change with the input text, but the output dimension remains 384 for this model.

The distinction to remember:

- Chunk size: how much text is in a chunk.
- Vector dimension: how many numbers represent that chunk.
- Number of vectors: how many chunks have been embedded.

These are three different things.

## Part 4 — What is Chroma?

### 1. The problem Chroma solves

After chunking, your project has three alternative sets of chunks:

- V1: 52 chunks
- V2: 230 chunks
- V3: 52 chunks

The chunks contain text and metadata, but they still need vector representations for semantic search.

Chroma is a vector database. In this project, it will store the chunk embeddings alongside the text, IDs and metadata so the system can search and retrieve relevant chunks.

Think of it as a searchable store for the numerical representations of your chunks, with the original evidence and its identifying information kept alongside them.

### 2. How many vectors will be stored?

Let's answer Claude's question.

52 + 230 + 52 = **334**

If you embed every chunk from all three variants, you will create 334 vector records in total, assuming each chunk is embedded once.

The important qualification is that V1, V2 and V3 are alternative experiments, not 334 unique pieces of source information. Some content will overlap across variants.

For a fair comparison, it makes sense to keep each variant in a separate Chroma collection, or reliably filter by the variant metadata. Otherwise, a search might mix chunks from multiple strategies and make the comparison difficult to interpret.

If all 334 records use the same 384-dimensional embedding model, each vector contains 384 numbers.

### 3. What does Chroma store?

Conceptually, each record contains four things:

| Field         | Purpose                                     | Example                                |
| ------------- | ------------------------------------------- | -------------------------------------- |
| ID            | Identifies the chunk                        | `KPI-010::v2::3`                       |
| Text/document | Holds the evidence                          | NRR Formula section                    |
| Embedding     | Supports semantic similarity search         | A vector of 384 numbers                |
| Metadata      | Describes the source and supports filtering | Certification, owner, version, section |

Your `chunking.py` already creates the IDs, text and metadata. Step 1.5 adds the embedding and stores these records in Chroma.

### 4. Why store metadata with vectors?

Consider two documents that mention customer churn:

- A certified, current KPI definition.
- A deprecated KPI definition.

A similarity search may consider both relevant because they discuss the same topic. Semantic similarity alone does not establish which definition is authoritative.

Metadata can help resolve this.

For example, the application can filter for certified records before or during retrieval, depending on how the retrieval pipeline is implemented.

Claude's interview line is directionally correct:

> "I store each vector with its metadata, so I can filter by certification before ranking."

A more precise version for your project would be:

> "I store chunk embeddings alongside their source metadata, allowing retrieval to apply filters such as certification and version so that semantically relevant but deprecated content can be excluded."

One caveat: storing metadata does not automatically enforce governance. The retrieval code must actually apply the filters, and the metadata must be trustworthy.

### 5. What are the alternatives to Chroma?

Claude listed three alternatives. You only need to understand the broad differences for now.

| Technology | What it is                  | Why it might be used                                                                     |
| ---------- | --------------------------- | ---------------------------------------------------------------------------------------- |
| Chroma     | Vector database             | Convenient for a local RAG prototype; stores vectors, documents and metadata             |
| FAISS      | Similarity-search library   | Efficient vector search; metadata and document management need additional implementation |
| pgvector   | PostgreSQL extension        | Supports vector search alongside relational data                                         |
| OpenSearch | Search and analytics engine | Supports keyword and vector search in a broader search platform                          |

The project uses Chroma to keep the local prototype manageable. The underlying ideas (embedding, indexing, similarity search and metadata filtering) transfer to other platforms.

Amazon Bedrock Knowledge Bases can use supported vector stores, including OpenSearch. The specific choice depends on the service configuration and architecture.

## Part 5 — How the pieces fit together

1. Source documents: Markdown, CSV, PDF
2. Ingestion: extract content and attach metadata
3. Chunking: create searchable units using V1, V2 or V3
4. Embedding model: convert each chunk into a 384-dimensional vector
5. Chroma: store and search the vectors, text and metadata
6. Retrieval: find and rank candidate chunks for a question

This is the core pipeline. Later steps will add keyword retrieval, hybrid ranking, reranking and grounded answer generation.

## Part 6 — Interview questions to prepare

1. What is chunking, and why is it required in RAG?

Chunking divides source documents into smaller searchable units. It balances focused retrieval against preserving enough context to answer questions accurately.

2. What is the difference between fixed-size and heading-based chunking?

Fixed-size chunking divides text into approximate windows regardless of document structure. Heading-based chunking uses section boundaries, preserving semantic organization but producing variable-sized chunks.

3. What is overlap, and why do we use it?

Overlap repeats a portion of text between consecutive chunks to reduce the loss of context at split boundaries. It increases duplication and does not guarantee retrieval success.

4. What is an embedding?

An embedding is a numerical vector representing text. The system compares the vector for a query with stored chunk vectors to identify semantically relevant candidates.

5. What determines the dimension of an embedding?

The embedding model's output architecture determines the vector dimension. In this project, BAAI/bge-small-en-v1.5 produces 384-dimensional vectors.

6. How many vectors are created if all three chunking variants are embedded?

334 in total: 52 + 230 + 52, assuming one vector per chunk and no additional records. The variants should be kept distinct when comparing retrieval performance.

7. What is Chroma's role?

Chroma stores chunk embeddings with associated text, IDs and metadata, and supports vector similarity search and metadata filtering.

8. How would you investigate a RAG system returning irrelevant chunks?

Check that ingestion and chunking preserved the evidence, then inspect retrieval candidates, similarity scores, filters and top-k settings. If correct evidence reaches generation but the answer is wrong, investigate the generation stage.

## What you should understand before coding Step 1.5

You do not need to understand vector mathematics deeply yet. You should be able to explain these five points:

1. Chunking decides what text is grouped together.
2. The embedding model converts each chunk into a vector; your current model produces 384 numbers per chunk.
3. Chroma stores the vector together with the source text and metadata.
4. Retrieval compares the question vector with stored vectors and selects candidate chunks.
5. Retrieval quality depends on more than chunking: the embedding model, search configuration, ranking, filters and quality of the source content also matter.

Open question for you: If you embed all 334 chunks using the same model, will the vectors all have the same length? And will they all contain the same numbers? Explain why or why not.

---

## Section 5: Step 1.5 revision notes (embeddings and Chroma)

Source file for these notes: `src/rag/index.py` (run with `python -m rag.index --sanity`, results in `docs/walkthroughs/M1.md`).

**Purpose:** Convert chunks into vectors and store them in a searchable index.

**Embedding model:** `BAAI/bge-small-en-v1.5`. It produces 384-dimensional vectors. The model normalizes vectors, and the index uses cosine distance.

**Storage:** Chroma stores chunk IDs, text, embeddings and metadata. Three separate collections (`kpi_v1`, `kpi_v2`, `kpi_v3`) keep the chunking experiments separate.

**Search flow:** Embed the query → search the selected collection → retrieve the nearest chunks → display their scores and metadata.

**Interpreting similarity:** A higher score indicates greater similarity under the configured metric. It is not the probability that the result is correct.

**Lessons from the sanity checks:**

- Semantic search retrieves relevant KPI definitions but can also return deprecated content.
- Exact identifiers such as `KPI-014` may need keyword or exact-match retrieval.
- A chunk mentioning a dashboard is not necessarily the best source for its owner.
- Metadata filtering can help enforce certification requirements, but it must be applied by the search code.

**Debugging principle:** Verify that the correct evidence exists in the chunks, then check whether retrieval selects it. If the correct evidence is retrieved but the generated answer is wrong, investigate answer generation.

**Next milestone:** Evaluate retrieval systematically using the golden questions, rather than judging the system from three sanity queries alone.

---

## Section 6: Step 1.6 notes (BM25 keyword search)

Source files: `src/rag/bm25.py` (code), `tests/test_bm25.py` (tests), results in `docs/walkthroughs/M1.md`.

### Step 1.6 — BM25 Keyword Search

Definition: BM25 is a keyword-based ranking algorithm that scores documents or chunks according to how well their terms match a query.

Why we need it: Vector search captures semantic similarity but may miss exact identifiers such as `KPI-014`. BM25 helps retrieve chunks containing exact business terms, codes and names.

Three scoring ideas:

1. Term frequency: more occurrences can increase the score, with diminishing returns.
2. Inverse document frequency: rare terms are more informative than terms appearing in most chunks.
3. Length normalization: adjusts for chunk length so longer chunks do not win merely because they contain more text.

Tokenization: The project proposes a tokenizer that preserves hyphenated identifiers such as `kpi-014` as one token. This protects the value of exact identifier matches.

Planned implementation: `src/rag/bm25.py` will contain `tokenize()` and `bm25_search()`. The search function will support variant selection, top-k results and metadata filters, returning results in a format compatible with vector search.

Vector search vs BM25:

- Vector search finds semantically similar content.
- BM25 ranks chunks based on matching terms and their statistical importance.
- Hybrid search combines evidence from both retrieval methods.

Important limitations: BM25 may miss synonyms or paraphrases. Vector search may miss exact identifiers. Neither method guarantees that the returned chunk is authoritative or sufficient to answer the question.

Planned tests: Preserve `kpi-014` as one token, verify ranking on a controlled test set, verify metadata filtering, and remove zero-score results.

Sanity-query prediction: BM25 may find `KPI-014` particularly well because it is an exact identifier. "Who owns the Customer 360 Dashboard?" also contains likely exact matches. "How is churn calculated?" may be harder if the source uses different terms such as "Formula." These are predictions to test, not confirmed results.

Interview line: "Vector search finds meaning, BM25 finds matching terms such as exact IDs, and hybrid retrieval combines both to improve coverage."

### Update after running Step 1.6 (real results)

- `bm25.py` is built: `tokenize()` keeps `kpi-014` whole, `bm25_search(variant, query, k, where, stem)` supports metadata filters and returns the same fields as the vector search (with `score` instead of `similarity`).
- "How is churn calculated" was the hardest for BM25, as predicted. The words "how", "is" and "calculated" appear in many KPI files, so Conversion Rate and Customer Lifetime Value outranked Churn Rate.
- "Who owns the Customer 360 Dashboard" was NOT easy for BM25: the words match many KPI "Dashboards" sections and every document has an Owner line, so the catalog entry CAT-02 came 3rd in V1 and V3 and was missing in V2.
- "KPI-014": BM25 surfaced the catalog rows that list it, because short chunks score higher. The KPI-014 file itself was 4th in V1 and V3.
- Bug found by this step: V2 chunks did not contain the code "KPI-014" in their text. Fix: the chunk header is now `Title (CODE) | Section`. After the fix, V2 finds KPI-014 with both BM25 and vector search.
- Lesson: a retrieval problem can really be a chunking problem. Put identifiers in the text, not only in metadata.

## Section 7: M1 notes on BM25, vector search, filtering and ranking

These notes cover the concepts in `src/rag/bm25.py`, then initial ranking versus hybrid ranking with Reciprocal Rank Fusion (RRF).

### 7.1 Tokenization in BM25

Tokenization converts text into the terms the search algorithm matches. In `bm25.py`:

```python
TOKEN_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
```

- Text is lowercased.
- Hyphenated identifiers such as KPI-014 stay one token (`kpi-014`). This is a deliberate project choice because KPI identifiers matter for exact searches.
- Why it matters: a search for KPI-014 matches the identifier reliably only if it is one token.
- Interview takeaway: our custom tokenizer keeps hyphenated KPI IDs whole so BM25 can match governance-specific IDs.

### 7.2 BM25 scoring

BM25 is a keyword-based retrieval algorithm. It scores chunks by how well their terms match the query. Three factors drive the score:

| Factor | Meaning |
|---|---|
| Term frequency (TF) | How often a query term occurs in a chunk, with diminishing returns. |
| Inverse document frequency (IDF) | How distinctive a term is across the corpus. Rare terms carry more weight. |
| Length normalization | Adjusts for chunk length so long chunks do not win just because they contain more words. |

A query containing KPI-014 favours a chunk containing that exact identifier, especially because the identifier is distinctive. BM25 scores show relative relevance within one search. They are not probabilities that a result is correct.

### 7.3 Vector search and embeddings

Vector search focuses on semantic similarity, not only exact keyword matches.

1. An embedding model converts a text chunk into a vector.
2. The same model converts the user's query into a vector.
3. The vector database compares the query vector with the stored chunk vectors.
4. Chunks with higher similarity are returned as more relevant candidates.

Example: "How is customer loss measured?" can retrieve a churn KPI even when the wording differs from the KPI definition. The model produces vectors that represent learned patterns in the text. It does not assign a human-readable meaning to each vector.

Interview takeaway: BM25 is strong for exact terms and identifiers. Vector search is strong for semantic matches when the query and the source use different wording.

### 7.4 Metadata filtering for deprecated KPIs

`search()` in `bm25.py` supports a `where` parameter, for example:

```python
where = {"certification": "Certified"}
```

- Filtering decides which results are eligible to be returned.
- Ranking decides the order of the eligible results.
- A deprecated KPI can get the highest BM25 score because its text matches the query closely. A certification filter excludes it anyway.
- The filter is implemented, but not every search applies it by default. The example shows how to use it.

### 7.5 Initial ranking versus hybrid ranking

**A. Initial ranking.** Each retrieval method ranks the chunks it finds. We have two: BM25 (keyword scores) and vector search (similarity). For the question "How is churn calculated?", an illustration (not actual project output):

| Rank | BM25 | Vector |
|---|---|---|
| 1 | Chunk A (many matching keywords) | Chunk C (semantically closest) |
| 2 | Chunk B (some matching keywords) | Chunk A (also semantically relevant) |

Each method judges relevance in its own way, so the first places differ.

**B. Hybrid ranking with RRF.** Hybrid retrieval combines the ranked lists from several retrieval methods. RRF uses each result's position in the lists, not the raw BM25 or vector scores:

RRF(d) = sum over lists r of 1 / (k + rank_r(d))

- d is a chunk, r is one ranked list (BM25 or vector), rank_r(d) is the chunk's position in that list.
- k is a constant, commonly 60.
- A chunk gets a contribution from every list it appears in. Good ranks across lists give a higher combined score.

**C. Worked example (k = 60).**

| Chunk | BM25 rank | Vector rank | RRF score |
|---|---|---|---|
| A | 1 | 2 | 1/61 + 1/62 = 0.0325 |
| C | not in top results | 1 | 1/61 = 0.0164 |
| B | 2 | not in top results | 1/62 = 0.0161 |

A wins because both methods rank it highly. The scores are illustrative.

**D. Why RRF?** BM25 scores and vector similarities are on different scales, so adding raw scores directly is not appropriate without normalization. RRF avoids the problem by combining rank positions. It does not guarantee that the top result is correct, certified or current. Excluding deprecated KPIs still needs an explicit filter or another policy control.

**E. Where this fits.**

BM25 retrieval (keyword ranking) and vector retrieval (semantic ranking) feed RRF hybrid fusion, which produces the final ranked candidates passed to later pipeline stages. Today `bm25.py` performs BM25 ranking only. RRF is planned for Step 2.3, after retrieval evaluation (Step 2.2).

### 7.6 Interview-ready recap

- Tokenization: the regex keeps hyphenated KPI IDs as single tokens for reliable exact matching.
- BM25: ranks chunks by keyword matching, term frequency, rarity and length normalization.
- Vector search: ranks chunks by semantic similarity between query and chunk embeddings.
- Metadata filtering: excludes results that fail a metadata condition.
- Initial ranking: each retrieval method produces its own ranked list.
- Hybrid ranking: combines the BM25 and vector ranked lists.
- RRF: combines rank positions, not raw scores.
- Governance safeguard: RRF improves the combination but does not replace certification filters.

### 7.7 Hand-worked RRF examples

These examples use k = 60 and the formula from 7.5. Compute each score from the ranks, then compare.

**Example 1: a document in both lists.**

| Document | Vector rank | BM25 rank | Calculation | RRF score |
|---|---|---|---|---|
| A | 1 | 4 | 1/61 + 1/64 | 0.032018 |
| B | 3 | 1 | 1/63 + 1/61 | 0.032266 |
| C | 2 | not found | 1/62 | 0.016129 |

B wins by a small margin. A ranks first in vector search, but its BM25 rank of 4 gives it less total score than B's combined ranks of 3 and 1.

**Example 2: missing documents contribute nothing.**

| Document | Vector rank | BM25 rank | Calculation | RRF score |
|---|---|---|---|---|
| X | 1 | not found | 1/61 | 0.016393 |
| Y | 3 | 2 | 1/63 + 1/62 | 0.032002 |
| Z | not found | 1 | 1/61 | 0.016393 |

Y wins with roughly twice the score of X or Z, because it appears in both lists. X and Z tie.

**Example 3: first place in both lists versus one list.**

| Document | Vector rank | BM25 rank | Calculation | RRF score |
|---|---|---|---|---|
| P | 1 | 1 | 1/61 + 1/61 | 0.032787 |
| Q | 1 | not found | 1/61 | 0.016393 |

P ranks first in both lists, so it scores twice as much as Q, which ranks first in only one.

**What the examples show.**

- Every list contributes. A document in both lists accumulates two terms.
- Higher ranks contribute more: rank 1 gives 1/61, rank 3 gives 1/63.
- A missing document contributes zero. It gets no invented rank and no negative score.
- The best single rank does not guarantee the top score. Example 1 shows this.

RRF combines positions, not raw similarity or BM25 scores. The Step 2.3 unit tests should reproduce these values.

## Section 8: Step 2.3 notes (hybrid retrieval and Reciprocal Rank Fusion)

### 8.1 What is hybrid retrieval?

Hybrid retrieval combines two retrieval methods:

- **Vector search:** finds semantically similar content using embeddings.
- **BM25 search:** finds content by lexical term matching, which suits exact terms, names and identifiers.

The aim is to combine their complementary strengths. Combining retrieval methods does not guarantee better results.

### 8.2 How Reciprocal Rank Fusion (RRF) works

RRF combines ranked lists without requiring their original scores to be on the same scale.

RRF(d) = sum over ranked lists r of 1 / (k + rank_r(d))

- d is a document or chunk.
- r is one ranked result list (here, vector or BM25).
- rank_r(d) is the item's 1-based position in that list.
- k is a constant; this project uses 60.

An item near the top of both lists accumulates score from both. An item in only one list receives a contribution from that list only.

**Important:** RRF combines ranking positions, not relevance judgments or source authority. It does not know whether a document is certified, deprecated or contradictory.

### 8.3 Implementation decisions

- RRF is a pure function in `src/rag/fusion.py`.
- Hybrid retrieval is in `src/rag/hybrid.py`. It runs vector and BM25 search with the same chunking variant and metadata filter, then fuses the results.
- Fusion happens at the **chunk level**. Results are collapsed into unique documents afterwards, for evaluation.
- Each retriever fetches 50 candidate chunks; the fused list returns up to 50 chunks before document-level evaluation.
- The evaluation runner explicitly requests `k=FETCH_DEPTH` from hybrid retrieval. Returning only five chunks before document collapse would make the evaluation inconsistent with the existing runner.
- Unit tests and mocked runner tests cover fusion behaviour, duplicate handling, rank tracking, filter arguments and evaluation fetch depth.

### 8.4 Experimental setup

- Dataset: 40 questions, 30 development and 10 holdout overall.
- Eight unanswerable questions are excluded from retrieval metrics, leaving 24 answerable development questions and 8 answerable holdout questions.
- Compared V1, V2 and V3 chunking with vector, BM25 and hybrid retrieval.
- Metrics:
  - **Recall@5:** fraction of expected documents retrieved in the top five.
  - **Hit@5:** whether at least one expected document appears in the top five.
  - **MRR@10:** rewards retrieving the first expected document at a higher rank within the top ten.
- The hybrid runs were repeated after committing the implementation. Runs 18 to 20 reproduced runs 15 to 17 to four decimal places for the metrics; latency varied.

### 8.5 Key experimental findings

Development set:

| Variant | Retriever | Recall@5 | Hit@5 | MRR@10 |
|---|---|---:|---:|---:|
| V1 | Vector | 0.815 | 1.000 | 0.938 |
| V1 | Hybrid | 0.758 | 0.958 | 0.758 |
| V2 | Vector | 0.805 | 1.000 | 0.927 |
| V2 | Hybrid | 0.706 | 0.917 | 0.783 |
| V3 | Vector | 0.812 | 1.000 | 0.917 |
| V3 | Hybrid | 0.758 | 0.958 | 0.753 |

Hybrid was worse than vector on all three metrics for all three variants on the development set.

Holdout set:

| Variant | Retriever | Recall@5 | Hit@5 | MRR@10 |
|---|---|---:|---:|---:|
| V1 | Vector | 0.729 | 0.875 | 0.646 |
| V1 | Hybrid | 0.708 | 0.875 | 0.708 |
| V2 | Vector | 0.646 | 0.750 | 0.650 |
| V2 | Hybrid | 0.708 | 0.875 | 0.729 |
| V3 | Vector | 0.708 | 0.875 | 0.649 |
| V3 | Hybrid | 0.708 | 0.875 | 0.708 |

Holdout results were mixed. V2 hybrid improved on V2 vector, but the hit-rate increase is one additional question out of eight. The holdout sample is too small to establish a general improvement.

### 8.6 Error analysis and governance findings

**Hybrid can push relevant evidence out of the top five.** For V1, question G-025 had `CAT-08` in the vector top five, but hybrid pushed it to rank 9. This accounts for a substantial part of the recall reduction. For G-015 (V1 and V3), hybrid brought the expected glossary document `POL-04` into the top five, but `CAT-01` dropped out. Recall stayed unchanged while MRR decreased. Average metrics should be supplemented with question-level analysis.

**RRF can amplify a weak retriever's distractions.** For V1 on the development set:

- `FAQ-01` appeared in the top five for 16 questions with hybrid, versus 7 with vector.
- `KPI-007-V1`, the deprecated KPI, appeared in 6 hybrid top-five lists, versus 4 with vector.

BM25 also retrieved `FAQ-01` frequently. A plausible explanation is that equal-weight RRF lets BM25's highly ranked but distracting results compete with vector results. The counts support investigating this explanation but do not prove causation.

**Retrieval relevance is not source authority.** RRF ranks items by position in retrieval lists. It does not enforce governance rules. A production-style KPI governance system may need explicit metadata filters or other controls to keep deprecated or non-authoritative sources out of certified answers. Reranking can improve ordering but is not a substitute for such controls.

### 8.7 Fetch-depth validation

The fused top 50 contained enough distinct documents for document-level evaluation:

- V1: 48 to 49 distinct documents per question.
- V2: 20 to 38 distinct documents per question.
- V3: 48 to 49 distinct documents per question.

Every variant returned at least 10 distinct documents. V2 produced fewer because its chunking differs; this was not a failure of the depth check.

### 8.8 Engineering decision

**Decision:** keep vector retrieval as the reference baseline and keep hybrid retrieval as a documented comparison.

- V1 and V3 vector were very similar on the development metrics.
- Equal-weight RRF did not show an overall improvement on this corpus.
- Do not tune RRF weights against the small development set just to force a hybrid win.
- Carry the governance-document problem into the next stage of the project.

### 8.9 Lessons learned

1. Combining retrieval methods is an experiment, not an automatic upgrade.
2. Rank fusion avoids comparing incompatible raw scores, but equal rank positions do not mean equal relevance.
3. Evaluate at the level the application uses: chunk retrieval and document-level evidence are not interchangeable.
4. Aggregate metrics can hide important individual failures; inspect representative questions.
5. Small holdout sets give unstable estimates, so avoid strong claims based on one or two questions.
6. Reproducibility needs the code version, configuration, labels version and results recorded.
7. Governance constraints such as certification and deprecation need explicit handling, not just better semantic similarity.
8. A negative result is valuable when the implementation is tested, the comparison is fair and the decision is documented.

### 8.10 Next step

Step 2.4: evaluate reranking on the vector V1 reference configuration. Compare with the existing vector baseline, inspect question-level changes, and keep source-authority controls as a separate concern for grounded generation.

## Section 9: Step 2.4 notes (cross-encoder reranking)

**Bi-encoder vs cross-encoder.** The embedding model (bge-small) encodes the query and each chunk separately, so chunk vectors are precomputed and search is fast. A cross-encoder reads the query and one chunk together and outputs one relevance score. It is more precise but must run once per candidate at query time, so it only suits a short candidate list. Here: 50 chunks per query, about 3 s on CPU against about 45 ms for vector search.

**What reranking can and cannot do.** It reorders candidates; it cannot find a chunk retrieval missed. It judges text only, so it does not know a document is deprecated, uncertified or conflicting. In this project FAQ-01 (conflicting Active Customer definition) went from the top 5 on 7 dev questions to 11 after reranking, because it reads like a good answer.

**Evaluation protocol.** All 50 candidates are rescored and returned, so document-level metrics use the same fetch depth and cutoff as before. Nothing about the protocol changed, which keeps runs comparable.

**Results.** Dev: recall@5 0.815 to 0.826, hit@5 unchanged, MRR@10 0.938 to 0.910. Holdout: recall 0.729 to 0.875, MRR 0.646 to 0.917, with only 8 questions. Per question: 7 improved, 4 regressed, 1 mixed, 20 unchanged. A sign test on the 11 decided questions gives p about 0.27 one-sided, so it is not evidence of a win. The honest statement is "promising, not proven".

**Reading small samples.** One question on 8 moves holdout recall by about 0.125. Dev's +0.010 recall is a quarter of a question. When dev and holdout disagree, report both and do not pick the flattering one.

**Run hygiene.** Run 21 was logged before the code was committed, so its sha was `7395aef+dirty`. Run 22 is the clean rerun with identical metrics. Keep the dirty row, mark the rerun, trust the clean one.

**Interview line.** "I tested a cross-encoder reranker on top of vector retrieval. Dev was mixed, holdout improved on 8 questions, latency was about 50 times higher, and it did not enforce source authority, so I kept it optional and plan to settle it by end-to-end answer quality."

**Check yourself.** Why can reranking not fix a retrieval miss? Why does a text-only scorer promote FAQ-01? What would you need to see to call reranking a win?

## Section 10: Wrap-up of Steps 2.3 and 2.4 and what comes next

**What we did.** Step 2.3 added hybrid retrieval: `rrf()` (k=60) fuses the vector and BM25 chunk rankings, then chunks collapse to documents. Step 2.4 added a cross-encoder reranker over the vector top 50, behind a `--rerank` flag. Both were evaluated on the same 40-question golden set (dev for decisions, holdout run once), with every run logged in `results/runs.csv`.

**What we found.**
- Hybrid with equal-weight RRF lost to vector on dev in all three chunkings. BM25 is the weaker retriever here, and RRF counted its ranks equally, so FAQ-01 reached the top 5 on 16 of 24 dev questions (vector: 7).
- Reranking was mixed on dev (recall +0.010, MRR -0.028) and better on holdout (recall +0.146, MRR +0.271) but only 8 questions. 7 questions improved, 4 regressed, 1 mixed, 20 unchanged. A sign test gave p about 0.27. It cost about 50 times the latency and put FAQ-01 in the dev top 5 on 11 questions.
- Neither method looks at certification or currentness. Retrieval quality and source authority are separate problems.

**Decision (pending your review).** Vector V1 stays the default, reranking stays optional, and conflicts are handled in generation through metadata and the prompt.

**Lessons to keep.**
1. Predict before you run, then compare. Several of my expectations were wrong, and that is the learning.
2. A small test set limits what you can claim. Say "promising, not proven".
3. Log runs only on a clean commit, keep dirty runs, and mark reruns (runs 15 to 17 became 18 to 20, run 21 became 22).
4. Do not tune on holdout, and do not change labels or metrics after seeing results.
5. A citation proves a chunk was retrieved, not that it supports the claim. Validity and support are checked separately.

**Preview of Step 2.5 concepts.** Grounding (answer only from the context), structured output (JSON checked with Pydantic), abstention (an explicit refusal instead of a guess), and metadata-based governance (label sources, let Certified govern). Think about: why does temperature 0 matter for governance answers, and why keep Deprecated chunks in context instead of deleting them?

**Interview line.** "I tested hybrid and cross-encoder reranking against a vector baseline with a dev and holdout split. Neither was a clear win, neither handled source authority, so I kept vector as the default and handled governance in the generation step using certification metadata."

## Section 11: Complete findings from Steps 2.3 and 2.4 (hybrid retrieval and reranking)

**The question we asked.** Can two common upgrades beat plain vector search on a governed KPI corpus: (a) hybrid retrieval that fuses vector and BM25 with RRF, and (b) a cross-encoder reranker on top of vector results?

**Results at a glance** (V1, recall@5 / hit@5 / MRR@10).

| Config | Dev (n=24) | Holdout (n=8) |
|---|---|---|
| Vector | 0.815 / 1.000 / 0.938 | 0.729 / 0.875 / 0.646 |
| Hybrid | 0.758 / 0.958 / 0.758 | 0.708 / 0.875 / 0.708 |
| Vector + rerank | 0.826 / 1.000 / 0.910 | 0.875 / 1.000 / 0.917 |

**1. Did hybrid and RRF help?** No. Hybrid lost to vector on dev for V1, V2 and V3 (recall down 0.05 to 0.10, MRR@10 down 0.14 to 0.18). Holdout was about equal. RRF was implemented and tested correctly, so this is a result about the recipe, not a bug.

**2. Why it lost (hypotheses backed by counts).**
- RRF adds 1/(k + rank) from each list, so it treats both rankers as equally trustworthy. BM25 is the weaker one here (dev recall 0.59 to 0.64 against 0.81), so its mistakes get a full vote.
- BM25 rewards shared words. FAQ-01 is chatty and word-rich, so it reached the dev top 5 on 16 of 24 questions (vector: 7). It displaced correct hits (G-025, G-007, G-014).
- With 52 chunks in V1 and V3, vector search at depth 50 already ranks almost everything. Fusion has little new to add.
- BM25's best skill is exact IDs and rare terms. Most golden questions are plain natural language, so they rarely reward it.
- RRF did win some questions (G-031 on dev, G-028 on holdout). It lost more than it won.

**3. Did reranking help?** Mixed. Dev recall +0.010 (a quarter of one question), hit@5 unchanged, MRR@10 down 0.028. Holdout improved a lot but has 8 questions, and one question moves holdout recall by about 0.125. Of 32 answerable questions: 7 improved, 4 regressed, 1 mixed, 20 unchanged. A sign test on the 11 decided gave p about 0.27. Latency rose from about 45 ms to several seconds per query on CPU.

**4. What the cross-encoder can and cannot do.** It reads query and chunk together, so it is more precise than comparing separate vectors. But it only reorders the candidates it is given, it cannot find a missed chunk, and it sees text only. POL-04 appears in both gains (G-015, G-004) and losses (G-006, G-027), so no simple "document type" story holds.

**5. The deeper lesson: relevance is not authority.** FAQ-01 (Provisional, informal) reads like a perfect answer to "what is an active customer" and beat the certified KPI-006 more often after reranking (FAQ-01 in the dev top 5 on 11 questions, up from 7). No retrieval score knows about certification, version or deprecation. That has to come from metadata and rules, which is why governance moves into generation (Step 2.5).

**6. Retrieval is near its ceiling here.** Vector hit@5 is 1.000 on dev: every dev question has at least one expected document in the top 5. What is left are multi-document questions where part of the expected set is missing. More ranking tricks were unlikely to fix that, and the next gains are more likely to come from how the answer step uses and labels the sources.

**7. Process lessons.**
- Predict before running, then compare. My expectation that hybrid would lift G-015 and G-006 was wrong, and that is useful.
- Keep dev for decisions and run holdout once. Never tune on holdout.
- Report small samples honestly. Write "promising, not proven", and give the per-question picture, not only averages.
- Log runs only on a clean commit. Keep dirty runs (15 to 17, 21) and mark the reruns (18 to 20, 22).
- Do not change labels, metrics or baselines after seeing results.
- A simple baseline that holds up is a good outcome. Complexity must earn its place.

**8. Decision and direction.** Vector V1 is the default and reference. Hybrid and rerank stay as optional code with documented results. No tuning of RRF weights or the reranker on 24 dev questions, since that would fit noise. Handle governance in generation with certification labels, ordering and prompt rules. Judge rerank by end-to-end answer quality in Step 3.1. Reopen retrieval only if a larger golden set or an end-to-end gain justifies it.

**9. Interview answers.**
- "Did hybrid search help?" "Not on this corpus. Equal-weight RRF let a weaker BM25 ranker pull an informal FAQ into the top 5, and dev recall dropped 0.05 to 0.10. I kept vector as the default and documented why."
- "Why not tune the weights?" "With 24 dev questions I would be fitting noise, and holdout is only 8 answerable questions."
- "What does a reranker not solve?" "Source authority. A text-only scorer can prefer an informal FAQ over the certified definition, so I labelled sources with certification metadata at generation time."

**Check yourself.** Why can fusion hurt when one ranker is weaker? Why does a small holdout limit the claim? Why can a reranker not fix a retrieval miss? What does hit@5 = 1.0 tell you about where the remaining problem is?
