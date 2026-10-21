"""judge_sanity with fake judges: the case list is well formed, and a yes-man judge is caught."""
import json
from types import SimpleNamespace

from eval import judge_sanity as js

CONTEXTS = [{"chunk_id": "KPI-007::v1::0", "doc_id": "KPI-007", "certification": "Certified", "text": "180 days."}]
RECORDS = {
    "G-013": {"question": "q13", "key_facts": ["a", "b", "c"], "contexts": CONTEXTS},
    "G-018": {"question": "q18", "key_facts": ["d", "e"], "contexts": CONTEXTS},
}


def yes_man(system, user, **kwargs):
    """Says every fact is covered and every claim is supported."""
    if "key fact" in system:
        count = sum(1 for line in user.splitlines() if line[:1].isdigit() and ". " in line[:4])
        return SimpleNamespace(text=json.dumps({"facts": [{"fact": "x", "covered": True}] * count}))
    return SimpleNamespace(text=json.dumps({"claims": [{"claim": "c", "supported": True}]}))


def test_case_list_is_well_formed():
    cases = js.build_cases(RECORDS)
    assert len(cases) == 10
    for case in cases:
        if case.kind == "facts":
            assert len(case.expect) == len(case.record["key_facts"])
        else:
            assert case.expect in ("all_supported", "some_unsupported", None)
    assert sum(1 for c in cases if c.expect is None) == 1  # one INFO case


def test_a_yes_man_judge_fails_the_negative_cases_and_passes_the_positive_controls():
    results = js.run_all(js.build_cases(RECORDS), yes_man, "m", progress=lambda line: None)
    by_name = {r["case"]: r["verdict"] for r in results}
    assert by_name["facts: complete answer covers every fact (positive control)"] == "PASS"
    assert by_name["claims: faithful answer (positive control)"] == "PASS"
    assert by_name["facts: vague answer covers none"] == "FAIL"
    assert by_name["claims: invented dashboard"] == "FAIL"
    assert [r["verdict"] for r in results].count("INFO") == 1


def test_judge_errors_count_as_failures_and_do_not_stop_the_run():
    def broken(system, user, **kwargs):
        raise RuntimeError("503")

    results = js.run_all(js.build_cases(RECORDS), broken, "m", progress=lambda line: None)
    assert len(results) == 10  # every case ran: one failure did not stop the rest
    assert all(r["verdict"] == "FAIL" and "RuntimeError: 503" in r["got"] for r in results)
