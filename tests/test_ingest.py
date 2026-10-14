"""Checks for the PDF loader. Run from the repo root:  python -m pytest -q"""
from pathlib import Path

import pytest

from rag.ingest import add_ownership, load_all, load_pdf, ownership_block, table_rows_as_lines

PDF_DIR = Path("data/raw/pdfs")
pytestmark = pytest.mark.skipif(not PDF_DIR.exists(), reason="corpus PDFs not found")


def test_table_rows_become_labelled_lines_and_wrapped_cells_are_joined():
    table = [["ID", "Owner", "Status"], ["KPI-001", "Head of Finance\nAnalytics", "Certified"]]
    assert table_rows_as_lines(table) == "ID: KPI-001 | Owner: Head of Finance Analytics | Status: Certified"


def test_pdf_headings_become_markdown_headings():
    text = load_pdf(PDF_DIR / "pol-01_data_governance_policy.pdf")
    assert text.startswith("# Kestrel Retail Group: Data Governance Policy")
    assert "\n## 1. Purpose" in text


def test_a_wrapped_pdf_title_stays_on_one_line():
    text = load_pdf(PDF_DIR / "pol-05_quarterly_kpi_review_minutes.pdf")
    assert text.splitlines()[0] == "# Kestrel Retail Group: Quarterly KPI Review Minutes (Q2 2026)"


def test_glossary_has_20_rows_each_with_owner_and_status_on_the_same_line():
    text = load_pdf(PDF_DIR / "pol-04_kpi_glossary_summary.pdf")
    rows = [line for line in text.splitlines() if line.startswith("ID: KPI-")]
    assert len(rows) == 20  # 20 current KPIs; the deprecated v1 is not listed
    for row in rows:
        assert "Owner:" in row and "Status:" in row and "Short definition:" in row
    first = next(r for r in rows if r.startswith("ID: KPI-001"))
    assert "Owner: Head of Finance Analytics" in first and "Status: Certified" in first


def test_every_pdf_table_row_keeps_all_its_columns():
    text = load_pdf(PDF_DIR / "pol-03_data_classification_standard.pdf")
    rows = [line for line in text.splitlines() if line.startswith("Level: ")]
    assert len(rows) == 4
    for row in rows:
        assert all(key in row for key in ("Description:", "Examples:", "Handling:"))


ROW = {"doc_id": "KPI-900", "doc_type": "kpi", "owner": "Head of Testing", "certification": "Provisional",
       "version": "0.7", "effective_date": "2026-05-15", "domain": "Customer"}


def test_ownership_block_states_owner_status_and_version_in_text():
    block = ownership_block(ROW)
    assert "Owner: Head of Testing" in block and "Status: Provisional" in block and "Version: 0.7" in block


def test_ownership_block_skips_empty_fields():
    assert "Version" not in ownership_block({**ROW, "version": ""})


def test_catalog_rows_get_plain_lines_and_other_documents_get_their_own_section():
    assert "##" not in add_ownership("row text", {**ROW, "doc_type": "catalog"})
    assert add_ownership("body", ROW).endswith("## Ownership and status\n" + ownership_block(ROW))


def test_every_real_document_text_states_its_owner_and_status():
    for doc in load_all():
        assert f"Owner: {doc['owner']}" in doc["text"], doc["doc_id"]
        assert f"Status: {doc['certification']}" in doc["text"], doc["doc_id"]
