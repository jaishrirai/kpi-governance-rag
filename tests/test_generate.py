"""generate.py with a fake model: prompt, context formatting, parsing and the no-hits shortcut."""
import json
from types import SimpleNamespace

import pytest

from rag import generate as g

HITS = [
    {"chunk_id": "KPI-007::v1::0", "doc_id": "KPI-007", "certification": "Certified",
     "text": "Customer Churn Rate (KPI-007) | part 1\nChurn is customers with no purchase for 180 days.\n"},
    {"chunk_id": "FAQ-01::v1::0", "doc_id": "FAQ-01", "certification": "Provisional", "text": "Informal note."},
]


def fake_llm(reply, calls=None):
    def complete(system, user):
        if calls is not None:
            calls.append((system, user))
        return SimpleNamespace(text=reply, model="fake-model", input_tokens=100, output_tokens=20,
                               thinking_tokens=5, latency_ms=12.5)
    return complete


GOOD = json.dumps({"answer": "Churn uses 180 days [KPI-007::v1::0].", "citations": ["KPI-007::v1::0"], "refused": False})


def test_prompt_file_has_the_rules_the_code_relies_on():
    prompt = g.load_prompt()
    assert g.REFUSAL_MESSAGE in prompt          # exact refusal sentence
    assert "JSON" in prompt and "citations" in prompt and "refused" in prompt
    assert "ONLY" in prompt                     # grounding rule


def test_format_context_labels_each_chunk_and_keeps_order():
    context = g.format_context(HITS)
    assert context.startswith("[KPI-007::v1::0] KPI-007 | Certified\nCustomer Churn Rate")
    assert "[FAQ-01::v1::0] FAQ-01 | Provisional\nInformal note." in context
    assert context.index("KPI-007::v1::0") < context.index("FAQ-01::v1::0")


def test_format_context_handles_missing_certification():
    hit = {"chunk_id": "X::v1::0", "doc_id": "X", "text": "t"}
    assert g.format_context([hit]).startswith("[X::v1::0] X | unknown status")


def test_user_message_has_question_and_context():
    message = g.build_user_message("What is churn?", HITS)
    assert message.startswith("Question: What is churn?")
    assert "[KPI-007::v1::0]" in message


def test_parse_answer_happy_path():
    assert g.parse_answer(GOOD) == ("Churn uses 180 days [KPI-007::v1::0].", ["KPI-007::v1::0"], False)


def test_parse_answer_accepts_code_fences():
    assert g.parse_answer("```json\n" + GOOD + "\n```")[2] is False


@pytest.mark.parametrize("bad", [
    "not json at all",
    "[1, 2]",
    json.dumps({"answer": 5, "citations": [], "refused": False}),
    json.dumps({"answer": "a", "citations": "KPI-007", "refused": False}),
    json.dumps({"answer": "a", "citations": [1], "refused": False}),
    json.dumps({"answer": "a", "citations": [], "refused": "no"}),
    json.dumps({"answer": "a", "citations": []}),
])
def test_parse_answer_rejects_wrong_shape(bad):
    with pytest.raises(g.GenerationError):
        g.parse_answer(bad)


def test_generate_sends_prompt_and_context_and_returns_structured_result():
    calls = []
    result = g.generate("What is churn?", HITS, complete_fn=fake_llm(GOOD, calls))
    system, user = calls[0]
    assert system == g.load_prompt() and "Question: What is churn?" in user and "[FAQ-01::v1::0]" in user
    assert (result.answer, result.citations, result.refused) == ("Churn uses 180 days [KPI-007::v1::0].", ["KPI-007::v1::0"], False)
    assert result.chunk_ids == ["KPI-007::v1::0", "FAQ-01::v1::0"]
    assert (result.model, result.input_tokens, result.output_tokens, result.thinking_tokens) == ("fake-model", 100, 20, 5)
    assert result.prompt_version == "answer_v1" and result.raw_text == GOOD


def test_generate_passes_a_model_refusal_through():
    refusal = json.dumps({"answer": g.REFUSAL_MESSAGE, "citations": [], "refused": True})
    result = g.generate("CEO?", HITS, complete_fn=fake_llm(refusal))
    assert result.refused is True and result.citations == [] and result.answer == g.REFUSAL_MESSAGE


def test_generate_with_no_hits_refuses_without_calling_the_model():
    calls = []
    result = g.generate("anything", [], complete_fn=fake_llm(GOOD, calls))
    assert calls == [] and result.refused is True and result.answer == g.REFUSAL_MESSAGE
    assert result.citations == [] and result.chunk_ids == []


def test_generate_raises_on_a_malformed_reply():
    with pytest.raises(g.GenerationError):
        g.generate("q", HITS, complete_fn=fake_llm("sorry, I cannot do that"))


def test_build_correction_names_rejected_and_allowed_ids_exactly():
    text = g.build_correction(["KPI-999::v1::0"], ["KPI-006::v1::0", "FAQ-01::v1::0"])
    assert text == ("These citation IDs were invalid: [KPI-999::v1::0].\n"
                    "You may cite only these retrieved IDs: [KPI-006::v1::0, FAQ-01::v1::0].")


def test_build_correction_says_none_and_adds_the_consistency_rule_when_needed():
    text = g.build_correction([], ["KPI-006::v1::0"], consistency=True)
    assert text.startswith("These citation IDs were invalid: [none].")
    assert "Your refused flag and citations did not agree." in text


def test_user_message_has_correction_only_when_given():
    assert "These citation IDs" not in g.build_user_message("q", HITS)
    assert g.build_user_message("q", HITS, "CORRECTION").endswith("\n\nCORRECTION")


def test_generate_sends_the_correction_to_the_model():
    calls = []
    g.generate("q", HITS, complete_fn=fake_llm(GOOD, calls), correction="CORRECTION")
    assert calls[0][1].endswith("\n\nCORRECTION")


def test_v2_prompt_is_v1_plus_exactly_one_completeness_rule():
    rule = next(line for line in g.load_prompt("answer_v2").splitlines() if line.startswith("6. State every key fact"))
    v1, v2 = g.load_prompt("answer_v1"), g.load_prompt("answer_v2")
    assert v2.count(rule) == 1
    assert v2.replace(rule + "\n", "") == v1
    assert "Completeness" not in v1 and "State every key fact" not in v1
