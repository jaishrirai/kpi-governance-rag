"""handgrade: item selection, a sheet that leaks nothing, grade parsing and judge agreement."""
import pytest

from eval import handgrade as hg

CTX = [{"chunk_id": "K::v1::0", "doc_id": "K", "certification": "Certified", "text": "Some chunk text."}]


def rec(qid, version, trap=False, refused=False, facts=("f1", "f2")):
    return {"id": qid, "question": f"question {qid}", "answer": f"answer text {qid}", "answerable": True,
            "refused": refused, "error": None, "key_facts": list(facts), "contexts": CTX, "prompt_version": version,
            "conflicting_doc_ids": ["X"] if trap else []}


def runs(n=14, traps=5, refused=("Q03",)):
    ids = [f"Q{i:02d}" for i in range(1, n + 1)]
    mk = lambda v: {i: rec(i, v, trap=k < traps, refused=i in refused) for k, i in enumerate(ids)}
    return mk("answer_v1"), mk("answer_v2")


def test_pick_items_mix_and_determinism():
    v1, v2 = runs()
    items = hg.pick_items(v1, v2)
    assert len(items) == 10 and len({i["id"] for i in items}) == 10
    assert sum(1 for i in items if i["record"]["conflicting_doc_ids"]) == 3
    assert sorted(i["version"] for i in items).count("answer_v1") == 5
    assert "Q03" not in {i["id"] for i in items}  # refused in both versions: not gradable
    assert [(i["id"], i["version"]) for i in items] == [(i["id"], i["version"]) for i in hg.pick_items(v1, v2)]


def test_sheet_and_template_do_not_leak_the_version():
    items = hg.pick_items(*runs())
    sheet = hg.sheet_markdown(items)
    csv_rows = hg.template_rows(items)
    assert "answer_v1" not in sheet and "answer_v2" not in sheet and "prompt_version" not in sheet
    assert "judge" not in sheet.lower().replace("the judge uses", "")
    assert len(csv_rows) == 10 * 3  # two key facts plus one faithfulness row per answer
    assert all(r["answer"] == "" for r in csv_rows)
    assert "Some chunk text." in sheet and "H01" in sheet


def test_read_grades_parses_and_rejects_blanks(tmp_path):
    path = tmp_path / "g.csv"
    rows = [{"code": "H01", "kind": "fact", "item": "f1", "answer": "Y", "notes": ""},
            {"code": "H01", "kind": "fact", "item": "f2", "answer": "n", "notes": ""},
            {"code": "H01", "kind": "faithful", "item": hg.FAITH_TEXT, "answer": "y", "notes": ""}]
    hg.write_csv(path, rows)
    assert hg.read_grades(path) == {"H01": {"facts": [True, False], "faithful": True}}
    rows[1]["answer"] = ""
    hg.write_csv(path, rows)
    with pytest.raises(ValueError, match="H01 fact"):
        hg.read_grades(path)


def test_kappa():
    assert hg.kappa([(True, True), (False, False), (True, True), (False, False)]) == 1.0
    assert hg.kappa([(True, False), (False, True)]) == -1.0
    assert hg.kappa([(True, True), (True, True)]) is None  # all one value: chance agreement is total


def judged_for(items, judge_facts, judge_claims_ok=True):
    out = {"answer_v1": {}, "answer_v2": {}}
    for item in items:
        record = dict(item["record"])
        record["judge"] = {"errors": [], "key_facts": list(judge_facts),
                           "claims": [{"claim": "c", "supported": judge_claims_ok}]}
        out[item["version"]][item["id"]] = record
    return out


def test_compare_counts_agreement_and_lists_disagreements():
    items = hg.pick_items(*runs())
    judged = judged_for(items, [True, False])
    grades = {i["code"]: {"facts": [True, False], "faithful": True} for i in items}
    result = hg.compare(items, grades, judged)
    assert result["fact_agreement"] == 1.0 and result["faith_agree"] == 10 and result["meets_bar"] is True
    grades["H01"] = {"facts": [True, True], "faithful": False}  # one fact and one faithfulness disagreement
    result = hg.compare(items, grades, judged)
    assert result["fact_agreement"] == pytest.approx(19 / 20) and result["human_no_judge_yes"] == 0
    assert result["human_yes_judge_no"] == 1 and result["faith_agree"] == 9 and result["meets_bar"] is True
    assert sum("H01" in line for line in result["disagreements"]) == 2


def test_bar_is_missed_and_judge_errors_are_not_compared():
    items = hg.pick_items(*runs())
    judged = judged_for(items, [True, False])
    grades = {i["code"]: {"facts": [False, True], "faithful": True} for i in items}  # fully opposite on facts
    assert hg.compare(items, grades, judged)["meets_bar"] is False
    first = items[0]
    judged[first["version"]][first["id"]]["judge"]["errors"] = ["key facts: boom"]
    grades = {i["code"]: {"facts": [True, False], "faithful": True} for i in items}
    result = hg.compare(items, grades, judged)
    assert result["answers_compared"] == 9 and result["meets_bar"] is False  # needs all 10 compared
    assert any("not compared" in line for line in result["disagreements"])
