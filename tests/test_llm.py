"""llm.complete with a fake client: no network, no google-genai package, no waiting."""
from types import SimpleNamespace

import pytest

from rag import llm


class FakeError(Exception):
    def __init__(self, code):
        super().__init__(f"error {code}")
        self.code = code


def fake_response(text="{}", prompt=11, out=7, thoughts=3):
    usage = SimpleNamespace(prompt_token_count=prompt, candidates_token_count=out, thoughts_token_count=thoughts)
    return SimpleNamespace(text=text, usage_metadata=usage, candidates=[])


class FakeClient:
    def __init__(self, outcomes):
        self.outcomes = list(outcomes)  # each item: a response, or an exception to raise
        self.calls = []
        self.models = SimpleNamespace(generate_content=self._generate)

    def _generate(self, **kwargs):
        self.calls.append(kwargs)
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


def no_sleep(_seconds):
    pass


def test_returns_text_model_and_token_counts():
    client = FakeClient([fake_response('{"a": 1}')])
    result = llm.complete("sys", "usr", model="m1", client=client)
    assert (result.text, result.model) == ('{"a": 1}', "m1")
    assert (result.input_tokens, result.output_tokens, result.thinking_tokens) == (11, 7, 3)
    assert result.latency_ms >= 0


def test_sends_prompt_and_json_config_at_temperature_zero():
    client = FakeClient([fake_response()])
    llm.complete("the system prompt", "the user message", model="m1", client=client)
    call = client.calls[0]
    assert call["model"] == "m1" and call["contents"] == "the user message"
    assert call["config"]["system_instruction"] == "the system prompt"
    assert call["config"]["temperature"] == 0.0
    assert call["config"]["response_mime_type"] == "application/json"
    assert call["config"]["max_output_tokens"] == llm.DEFAULT_MAX_OUTPUT_TOKENS


def test_json_output_can_be_switched_off():
    client = FakeClient([fake_response()])
    llm.complete("s", "u", model="m1", client=client, json_output=False)
    assert "response_mime_type" not in client.calls[0]["config"]


def test_retries_transient_errors_then_succeeds():
    client = FakeClient([FakeError(503), FakeError(429), fake_response("ok")])
    result = llm.complete("s", "u", model="m1", client=client, sleep=no_sleep)
    assert result.text == "ok" and len(client.calls) == 3


def test_gives_up_after_the_retry_limit():
    client = FakeClient([FakeError(503), FakeError(503), FakeError(503)])
    with pytest.raises(FakeError):
        llm.complete("s", "u", model="m1", client=client, sleep=no_sleep, retries=2)
    assert len(client.calls) == 3


def test_does_not_retry_other_errors():
    client = FakeClient([FakeError(400), fake_response()])
    with pytest.raises(FakeError):
        llm.complete("s", "u", model="m1", client=client, sleep=no_sleep)
    assert len(client.calls) == 1


def test_empty_response_raises():
    client = FakeClient([fake_response(text=None)])
    with pytest.raises(llm.LLMError, match="Empty response"):
        llm.complete("s", "u", model="m1", client=client)


def test_missing_model_setting_raises(monkeypatch):
    monkeypatch.delenv("LLM_MODEL", raising=False)
    monkeypatch.setattr(llm, "_load_env", lambda: None)
    with pytest.raises(llm.LLMError, match="LLM_MODEL"):
        llm.complete("s", "u", client=FakeClient([]))


def test_missing_api_key_raises_without_printing_it(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setattr(llm, "_load_env", lambda: None)
    with pytest.raises(llm.LLMError, match="GEMINI_API_KEY"):
        llm.make_client()
