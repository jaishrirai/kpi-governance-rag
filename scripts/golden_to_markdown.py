"""
Write docs/GOLDEN_SET_REVIEW.md from golden/golden_set.jsonl, so the golden set can be read and
reviewed as a normal document. The JSONL file stays the single source of truth.
Run from the repo root:  python scripts/golden_to_markdown.py
"""
import json
from pathlib import Path

SRC = Path("golden/golden_set.jsonl")
OUT = Path("docs/GOLDEN_SET_REVIEW.md")


def main():
    rows = [json.loads(line) for line in open(SRC, encoding="utf-8") if line.strip()]
    lines = [
        "# Golden set review",
        "",
        "Generated from `golden/golden_set.jsonl` by `scripts/golden_to_markdown.py`. Edit the JSONL, not this file.",
        "",
        "Each question has two kinds of ground truth:",
        "",
        "- **Expected documents**: used to score retrieval (recall@5, MRR@10). Document level, so it works for V1, V2 and V3.",
        "- **Reference answer**: used to score the generated answer in Step 3.1. Every key fact in it is checked by `scripts/validate_golden.py` against the expected documents.",
        "",
        "H = holdout (never tuned against). Author `human` = your question, `claude` = drafted by Claude.",
        "",
    ]
    for r in rows:
        tag = " (H)" if r["holdout"] else ""
        lines += [
            f"## {r['id']}{tag} | {r['type']} | author: {r['author']}",
            "",
            f"**Question:** {r['question']}",
            "",
            f"**Expected documents:** {', '.join(r['expected_doc_ids']) if r['expected_doc_ids'] else 'none (should refuse)'}",
            "",
            f"**Conflicting (trap) documents:** {', '.join(r['conflicting_doc_ids']) or 'none'}",
            "",
            f"**Related but not sufficient:** {', '.join(r['related_insufficient_doc_ids']) or 'none'}",
            "",
            f"**Reference answer:** {r['reference_answer']}",
            "",
            f"**Notes:** {r['review']}",
            "",
        ]
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT} ({len(rows)} questions)")


if __name__ == "__main__":
    main()
