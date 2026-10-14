# Decisions (locked Day 1)

| # | Decision | Choice | Why |
|---|---|---|---|
| 1 | LLM | Gemini API free tier: Flash-class for answers, strongest free-tier model as judge. All calls go through `llm.complete()` | Free, enough for the prototype. One wrapper = swap provider (Anthropic, Bedrock) by changing one file |
| 2 | Embedding model | `BAAI/bge-small-en-v1.5`, local | Free, fast on CPU, 384 dims. Limit: 512 tokens per chunk |
| 3 | Vector store | Chroma, persistent on disk | Local, free, metadata filters |
| 4 | Stack | Python + plain libraries, no LangChain | I must be able to explain every line |
| 5 | Repo | Private until done, then public | Show a finished README |
| 6 | Company | "Kestrel Retail Group" (fictional) | Rich KPIs, clearly synthetic |
| 7 | Demo | Streamlit app with a Retrieval Inspector | Shows hybrid + rerank visually |
| 8 | Chunk header | `{title} ({doc_id}) \| {section}` on every chunk, all variants | Found in Step 1.6: V2 chunks of KPI-014 never contained the text "KPI-014", so neither BM25 nor the embedding could find the file by its code. Changed 2026-10-14, before the golden-set evaluation |
| 9 | Ownership text | Loader appends Owner, Status, Version, Effective date, Domain (from the manifest) to every document's text | Found while grounding golden answers: these facts were metadata only, so no chunk could answer "who owns X / is X certified". Changed 2026-10-14, before the M2 evaluation |
