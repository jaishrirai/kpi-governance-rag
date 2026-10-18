"""validate_citations: the V1 contract, one rule per test."""
import pytest

from rag.validate import validate_citations

RETRIEVED = ["KPI-006::v1::0", "FAQ-01::v1::0", "KPI-020::v1::0"]


def test_valid_answer_with_one_citation():
    assert validate_citations(["KPI-006::v1::0"], False, RETRIEVED) == []


def test_valid_answer_with_several_citations():
    assert validate_citations(["KPI-006::v1::0", "FAQ-01::v1::0"], False, RETRIEVED) == []


def test_valid_refusal_has_no_citations():
    assert validate_citations([], True, RETRIEVED) == []


def test_unknown_chunk_id_is_reported_by_name():
    problems = validate_citations(["KPI-006::v1::0", "KPI-999::v1::0"], False, RETRIEVED)
    assert len(problems) == 1 and "KPI-999::v1::0" in problems[0]


def test_document_id_is_not_a_chunk_id():
    problems = validate_citations(["KPI-006"], False, RETRIEVED)
    assert len(problems) == 1 and "'KPI-006'" in problems[0]


@pytest.mark.parametrize("variant", ["kpi-006::v1::0", "KPI-006::v1::0 ", " KPI-006::v1::0", "KPI-006::V1::0"])
def test_match_is_exact_no_case_or_whitespace_forgiveness(variant):
    assert len(validate_citations([variant], False, RETRIEVED)) == 1


def test_refusal_with_valid_citations_is_a_problem():
    problems = validate_citations(["KPI-006::v1::0"], True, RETRIEVED)
    assert problems == ["refused=True but citations were given"]


def test_answer_without_citations_is_a_problem():
    assert validate_citations([], False, RETRIEVED) == ["refused=False but no citations were given"]


def test_duplicate_citations_are_allowed():
    assert validate_citations(["KPI-006::v1::0", "KPI-006::v1::0"], False, RETRIEVED) == []


def test_duplicate_unknown_id_is_reported_once():
    assert len(validate_citations(["X::v1::0", "X::v1::0"], False, RETRIEVED)) == 1


def test_nothing_retrieved_only_a_refusal_is_valid():
    assert validate_citations([], True, []) == []
    assert len(validate_citations([], False, [])) == 1
    assert len(validate_citations(["KPI-006::v1::0"], False, [])) == 1


def test_several_problems_are_reported_together_in_order():
    problems = validate_citations(["A::v1::0", "B::v1::0"], True, RETRIEVED)
    assert len(problems) == 3
    assert "A::v1::0" in problems[0] and "B::v1::0" in problems[1] and "refused=True" in problems[2]


def test_accepts_any_iterable_for_retrieved_ids():
    assert validate_citations(["KPI-006::v1::0"], False, (i for i in RETRIEVED)) == []


def test_inputs_are_not_mutated():
    citations, retrieved = ["KPI-006::v1::0"], list(RETRIEVED)
    validate_citations(citations, False, retrieved)
    assert citations == ["KPI-006::v1::0"] and retrieved == RETRIEVED


def test_unknown_citations_lists_only_the_unretrieved_ids_once():
    from rag.validate import unknown_citations
    assert unknown_citations(["KPI-006::v1::0", "X::v1::0", "X::v1::0", "KPI-006"], RETRIEVED) == ["X::v1::0", "KPI-006"]
    assert unknown_citations([], RETRIEVED) == []
