# Decisions (locked Day 1)

| # | Decision | Choice | Why |
|---|---|---|---|
| 1 | LLM | Anthropic: Haiku-class for answers, Sonnet-class as judge. All calls go through `llm.complete()` | Cheap, follows instructions well. One wrapper = swap to Bedrock by changing one file |
| 2 | Embedding model | `BAAI/bge-small-en-v1.5`, local | Free, fast on CPU, 384 dims. Limit: 512 tokens per chunk |
| 3 | Vector store | Chroma, persistent on disk | Local, free, metadata filters |
| 4 | Stack | Python + plain libraries, no LangChain | I must be able to explain every line |
| 5 | Repo | Private until done, then public | Show a finished README |
| 6 | Company | "Kestrel Retail Group" (fictional) | Rich KPIs, clearly synthetic |
| 7 | Demo | Streamlit app with a Retrieval Inspector | Shows hybrid + rerank visually |
