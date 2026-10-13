"""Checks for the three chunking variants. Run from the repo root:  python -m pytest -q"""
import json
from pathlib import Path

import pytest

from rag.ingest import load_pdf
from rag.chunking import (CAP_TOKENS, CHARS_PER_TOKEN, DOCS_PATH, build_all, estimate_tokens,
                          split_sections, split_text, v1_fixed, v2_by_heading, v3_by_unit)


def fake_doc(text, doc_id="KPI-900", title="Test KPI"):
    return {"doc_id": doc_id, "title": title, "doc_type": "kpi", "domain": "Finance",
            "owner": "Head of Finance Analytics", "certification": "Certified", "version": "1.0",
            "effective_date": "2026-01-01", "source_path": "test.md", "text": text}


THREE_SECTIONS = "# Test KPI\n\n## Definition\nWhat it means.\n\n## Formula\nA / B x 100.\n\n## Caveats\nNone."


def test_split_sections_uses_heading_names_and_drops_title_line():
    sections = split_sections(THREE_SECTIONS)
    assert sections == [("Definition", "What it means."),
                        ("Formula", "A / B x 100."),
                        ("Caveats", "None.")]


def test_v2_gives_one_chunk_per_heading_with_ids_in_order():
    chunks = v2_by_heading(fake_doc(THREE_SECTIONS))
    assert [c.section for c in chunks] == ["Definition", "Formula", "Caveats"]
    assert [c.chunk_id for c in chunks] == ["KPI-900::v2::0", "KPI-900::v2::1", "KPI-900::v2::2"]


def test_every_chunk_starts_with_title_and_section_header():
    for c in v2_by_heading(fake_doc(THREE_SECTIONS)):
        assert c.text.startswith(f"Test KPI | {c.section}\n")


def test_v2_long_section_is_split_and_every_piece_keeps_its_heading():
    body = " ".join(f"word{i}" for i in range(1000))  # about 6,000 characters
    chunks = v2_by_heading(fake_doc(f"## Formula\n{body}"))
    assert len(chunks) > 1
    assert all(c.section == "Formula" for c in chunks)


def test_cap_is_measured_with_the_header_included():
    # The body alone fits the cap. Adding the header pushes it over, so it must be split.
    header_len = len("Test KPI | Formula\n")
    body = "x" * (CAP_TOKENS * CHARS_PER_TOKEN - 5)
    body = " ".join(body[i:i + 50] for i in range(0, len(body), 50))  # add spaces so it can be cut
    chunks = v2_by_heading(fake_doc(f"## Formula\n{body}"))
    assert len(chunks) > 1
    assert all(estimate_tokens(c.text) <= CAP_TOKENS for c in chunks)


def test_v1_neighbouring_pieces_share_words():
    text = " ".join(f"term{i}" for i in range(800))  # well over 400 tokens
    pieces = split_text(text, 400 * CHARS_PER_TOKEN, 60 * CHARS_PER_TOKEN)
    assert len(pieces) > 1
    for a, b in zip(pieces, pieces[1:]):
        assert set(a.split()) & set(b.split())


def test_v3_short_document_is_one_chunk():
    chunks = v3_by_unit(fake_doc("Short definition."))
    assert len(chunks) == 1
    assert chunks[0].chunk_id == "KPI-900::v3::0"


def test_chunk_ids_are_unique_within_each_variant():
    docs = [fake_doc(THREE_SECTIONS, doc_id="KPI-901"), fake_doc(THREE_SECTIONS, doc_id="KPI-902")]
    for variant, chunks in build_all(docs).items():
        ids = [c.chunk_id for c in chunks]
        assert len(ids) == len(set(ids)), variant


def test_metadata_is_copied_onto_every_chunk():
    for c in v2_by_heading(fake_doc(THREE_SECTIONS)):
        assert c.metadata["certification"] == "Certified"
        assert c.metadata["section"] == c.section
        assert c.metadata["variant"] == "v2"


@pytest.mark.skipif(not Path(DOCS_PATH).exists(), reason="run the loader first (python -m rag.ingest)")
def test_real_corpus_v2_gives_7_sections_per_kpi_file():
    docs = [json.loads(l) for l in open(DOCS_PATH, encoding="utf-8")]
    kpis = [d for d in docs if d["doc_type"] == "kpi"]
    assert len(kpis) == 21
    v2 = [c for d in kpis for c in v2_by_heading(d)]
    assert len(v2) == 147  # 21 files x 7 headings, the prediction we checked earlier


@pytest.mark.skipif(not Path(DOCS_PATH).exists(), reason="run the loader first (python -m rag.ingest)")
def test_real_corpus_v3_gives_one_chunk_per_kpi_file():
    docs = [json.loads(l) for l in open(DOCS_PATH, encoding="utf-8")]
    kpis = [d for d in docs if d["doc_type"] == "kpi"]
    assert all(len(v3_by_unit(d)) == 1 for d in kpis)


def test_split_text_cuts_at_line_breaks_so_lines_stay_whole():
    lines = [f"row {i} " + "x" * 30 for i in range(20)]
    pieces = split_text("\n".join(lines), max_chars=150, overlap_chars=40)
    assert len(pieces) > 1
    for piece in pieces:
        assert set(piece.splitlines()) <= set(lines)  # no line was cut in half


@pytest.mark.skipif(not Path("data/raw/pdfs").exists(), reason="corpus PDFs not found")
def test_glossary_table_rows_are_never_cut_in_any_variant():
    text = load_pdf("data/raw/pdfs/pol-04_kpi_glossary_summary.pdf")
    doc = fake_doc(text, doc_id="POL-04", title="KPI Glossary Summary")
    for chunker in (v1_fixed, v2_by_heading, v3_by_unit):
        chunks = chunker(doc)
        assert len(chunks) > 1  # the glossary is over the cap, so it really is split
        for chunk in chunks:
            for line in chunk.text.splitlines():
                if line.startswith("ID: KPI-"):
                    assert "Short definition:" in line, f"{chunker.__name__} cut a row: {line[:60]}"
