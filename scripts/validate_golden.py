"""
Validate golden/golden_set.jsonl (Step 2.1).
Run from the repo root:  python scripts/validate_golden.py
Hard checks (exit code 1 if any fails): 40 questions, ids G-001..G-040 in order, 8 unanswerable,
holdout = every 4th question (10), answerable questions have expected docs, unanswerable have none,
every expected doc exists in the manifest, conflicting_doc_ids and related_insufficient_doc_ids
(diagnostic only, never scored), every POL/SOP/CAT/FAQ document cited in a reference answer is
expected, related or conflicting (so the answer and the labels agree), exist in the manifest and do not overlap expected_doc_ids, no duplicate questions, and the reference answers are
grounded: every key_fact of an answerable question must appear in the text of its expected
documents, and every absent_term of an unanswerable question must appear nowhere in the corpus.
The mix by type is only reported against the targets, not enforced.
"""
import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path

GOLDEN = Path("golden/golden_set.jsonl")
MANIFEST = Path("data/corpus_manifest.csv")
TOTAL, UNANSWERABLE, HOLDOUT = 40, 8, 10
TARGET_MIX = {"definition": 12, "ownership": 8, "catalog": 6, "process": 6, "unanswerable": 8}
DOCS = Path("data/processed/documents.jsonl")
REQUIRED = ["id", "author", "question", "type", "answerable", "expected_doc_ids", "holdout",
            "reference_answer", "key_facts", "absent_terms", "review",
            "conflicting_doc_ids", "related_insufficient_doc_ids"]


def load_rows(path=GOLDEN):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def load_manifest_ids(path=MANIFEST):
    with open(path, encoding="utf-8") as f:
        return {row["doc_id"] for row in csv.DictReader(f)}


def load_doc_texts(path=DOCS):
    """doc_id -> text, from the loader output. Returns None if the loader has not been run."""
    if not Path(path).exists():
        return None
    with open(path, encoding="utf-8") as f:
        return {d["doc_id"]: d["text"] for d in map(json.loads, (l for l in f if l.strip()))}


def normalize(text):
    """Lower case, drop markdown emphasis characters and collapse whitespace, so a fact can be
    compared with the document text regardless of **bold**, `code` or line breaks."""
    return " ".join(text.lower().replace("*", "").replace("`", "").split())


def validate(rows, manifest_ids, doc_texts=None):
    errors = []
    if len(rows) != TOTAL:
        errors.append(f"expected {TOTAL} questions, found {len(rows)}")
    expected_ids = [f"G-{i:03d}" for i in range(1, len(rows) + 1)]
    if [r.get("id") for r in rows] != expected_ids:
        errors.append("ids are not G-001, G-002, ... in order without gaps")
    for r in rows:
        missing = [k for k in REQUIRED if k not in r]
        if missing:
            errors.append(f"{r.get('id')}: missing fields {missing}")
            continue
        if r["answerable"] and not r["expected_doc_ids"]:
            errors.append(f"{r['id']}: answerable but no expected documents")
        if not r["answerable"] and r["expected_doc_ids"]:
            errors.append(f"{r['id']}: unanswerable but has expected documents")
        if (r["type"] == "unanswerable") != (not r["answerable"]):
            errors.append(f"{r['id']}: type and answerable disagree")
        unknown = [d for d in r["expected_doc_ids"] if d not in manifest_ids]
        if unknown:
            errors.append(f"{r['id']}: expected documents not in the manifest: {unknown}")
        if len(set(r["expected_doc_ids"])) != len(r["expected_doc_ids"]):
            errors.append(f"{r['id']}: duplicate expected documents")
        for field in ("conflicting_doc_ids", "related_insufficient_doc_ids"):
            bad = [d for d in r[field] if d not in manifest_ids]
            if bad:
                errors.append(f"{r['id']}: {field} not in the manifest: {bad}")
            overlap = set(r[field]) & set(r["expected_doc_ids"])
            if overlap:
                errors.append(f"{r['id']}: {field} overlaps expected_doc_ids: {sorted(overlap)}")
    for r in rows:
        if not all(k in r for k in REQUIRED):
            continue
        if not r["reference_answer"].strip():
            errors.append(f"{r['id']}: empty reference_answer")
        if r["answerable"] and not r["key_facts"]:
            errors.append(f"{r['id']}: answerable but no key_facts")
        if not r["answerable"] and not r["absent_terms"]:
            errors.append(f"{r['id']}: unanswerable but no absent_terms")
        cited = set(re.findall(r"\b(?:POL|SOP|CAT|FAQ)-\d+\b", r["reference_answer"]))
        known = set(r["expected_doc_ids"]) | set(r["related_insufficient_doc_ids"]) | set(r["conflicting_doc_ids"])
        if cited - known:
            errors.append(f"{r['id']}: reference answer cites documents not in expected, related or conflicting: {sorted(cited - known)}")
        if doc_texts is None:
            continue
        evidence = normalize(" ".join(doc_texts.get(d, "") for d in r["expected_doc_ids"]))
        for fact in r["key_facts"]:
            if normalize(fact) not in evidence:
                errors.append(f"{r['id']}: key fact not found in expected documents: {fact!r}")
        corpus = normalize(" ".join(doc_texts.values()))
        for term in r["absent_terms"]:
            if normalize(term) in corpus:
                errors.append(f"{r['id']}: absent term appears in the corpus: {term!r}")
    if sum(1 for r in rows if not r.get("answerable", True)) != UNANSWERABLE:
        errors.append(f"expected {UNANSWERABLE} unanswerable questions")
    holdout_ids = [r["id"] for r in rows if r.get("holdout") is True]
    every_fourth = [r["id"] for i, r in enumerate(rows, 1) if i % 4 == 0]
    if holdout_ids != every_fourth or len(holdout_ids) != HOLDOUT:
        errors.append(f"holdout must be every 4th question ({HOLDOUT}): {every_fourth}, found {holdout_ids}")
    questions = [r.get("question", "").strip().lower() for r in rows]
    if len(set(questions)) != len(questions):
        errors.append("duplicate questions")
    return errors


def main():
    rows = load_rows()
    doc_texts = load_doc_texts()
    if doc_texts is None:
        print("note: data/processed/documents.jsonl not found, answer grounding NOT checked (run python -m rag.ingest)")
    errors = validate(rows, load_manifest_ids(), doc_texts)
    mix = Counter(r["type"] for r in rows)
    print(f"questions: {len(rows)} | holdout: {sum(1 for r in rows if r.get('holdout') is True)}")
    print(f"{'type':<14}{'actual':>8}{'target':>8}")
    for t, target in TARGET_MIX.items():
        flag = "" if mix[t] == target else "   (differs from target)"
        print(f"{t:<14}{mix[t]:>8}{target:>8}{flag}")
    if errors:
        print("\nFAILED:")
        for e in errors:
            print(" -", e)
        sys.exit(1)
    print("\nOK: golden set passes all checks")


if __name__ == "__main__":
    main()
