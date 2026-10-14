"""Tests for scripts/validate_golden.py."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, "scripts")
import validate_golden as vg  # noqa: E402

IDS = {"KPI-001", "KPI-002"}
TEXTS = {"KPI-001": "Net Revenue is **gross** sales minus discounts.", "KPI-002": "Gross margin."}


def make_rows(n=40, unanswerable=8):
    rows = []
    for i in range(1, n + 1):
        un = i > n - unanswerable
        rows.append({"id": f"G-{i:03d}", "author": "t", "question": f"question {i}",
                     "type": "unanswerable" if un else "definition", "answerable": not un,
                     "expected_doc_ids": [] if un else ["KPI-001"], "holdout": i % 4 == 0, "review": "",
                     "reference_answer": "ref", "key_facts": [] if un else ["gross sales minus discounts"],
                     "absent_terms": ["zebra"] if un else [],
                     "conflicting_doc_ids": [], "related_insufficient_doc_ids": []})
    return rows


def test_valid_set_has_no_errors():
    assert vg.validate(make_rows(), IDS, TEXTS) == []


def test_conflicting_doc_must_exist_and_not_overlap_expected():
    rows = make_rows()
    rows[0]["conflicting_doc_ids"] = ["NOPE-1"]
    rows[1]["related_insufficient_doc_ids"] = ["KPI-001"]
    errors = vg.validate(rows, IDS, TEXTS)
    assert any("G-001" in e and "not in the manifest" in e for e in errors)
    assert any("G-002" in e and "overlaps" in e for e in errors)


def test_reference_citing_unlisted_document_is_reported():
    rows = make_rows()
    rows[0]["reference_answer"] = "See POL-04 for the list."
    assert any("G-001" in e and "POL-04" in e for e in vg.validate(rows, IDS, TEXTS))
    rows[0]["related_insufficient_doc_ids"] = ["KPI-002"]
    rows[0]["reference_answer"] = "See SOP-01."
    assert any("SOP-01" in e for e in vg.validate(rows, IDS, TEXTS))


def test_wrong_total_is_reported():
    assert any("expected 40" in e for e in vg.validate(make_rows(39), IDS))


def test_unknown_expected_document_is_reported():
    rows = make_rows()
    rows[0]["expected_doc_ids"] = ["KPI-999"]
    assert any("KPI-999" in e for e in vg.validate(rows, IDS))


def test_holdout_must_be_every_fourth():
    rows = make_rows()
    rows[3]["holdout"] = False
    rows[4]["holdout"] = True
    assert any("holdout" in e for e in vg.validate(rows, IDS))


def test_unanswerable_must_have_no_expected_documents():
    rows = make_rows()
    rows[-1]["expected_doc_ids"] = ["KPI-001"]
    assert any("unanswerable but has" in e for e in vg.validate(rows, IDS))


def test_key_fact_missing_from_expected_documents_is_reported():
    rows = make_rows()
    rows[0]["key_facts"] = ["a fact that is not in the text"]
    assert any("key fact not found" in e for e in vg.validate(rows, IDS, TEXTS))


def test_absent_term_that_appears_in_the_corpus_is_reported():
    rows = make_rows()
    rows[-1]["absent_terms"] = ["discounts"]
    assert any("absent term appears" in e for e in vg.validate(rows, IDS, TEXTS))


@pytest.mark.skipif(not (Path(vg.GOLDEN).exists() and Path(vg.MANIFEST).exists()), reason="files missing")
def test_real_golden_set_passes():
    assert vg.validate(vg.load_rows(), vg.load_manifest_ids(), vg.load_doc_texts()) == []
