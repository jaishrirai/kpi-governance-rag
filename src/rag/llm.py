"""
Step 2.5: the only module that calls the Gemini API.

Everything else in the project calls complete(), so changing provider (or mocking the model in
tests) means touching this one function. The google-genai package is imported lazily, like the
reranker, so retrieval code and tests never need it or a network connection.

Settings come from .env (git-ignored): GEMINI_API_KEY and LLM_MODEL. The key is never printed.
Run from the repo root with PYTHONPATH=src, like the other modules.
"""
import os
import time
from dataclasses import dataclass

# Cap on output tokens. Some Gemini models spend part of this on hidden "thinking", so it is
# larger than the visible answer needs. Review after the first real runs (tokens are logged).
DEFAULT_MAX_OUTPUT_TOKENS = 800
# HTTP codes worth retrying: rate limit, server error, overloaded (the 503 seen in the smoke test).
TRANSIENT_CODES = (429, 500, 503)
# Connection-level failures (DNS lookup failed, server dropped the connection, timeout) carry no HTTP code,
# so they are recognised by class name. Matching by name keeps httpx, used inside the Gemini SDK, out of
# the imports here.
CONNECTION_ERROR_NAMES = frozenset({
    "ConnectError", "ConnectTimeout", "ReadTimeout", "WriteTimeout", "PoolTimeout", "TimeoutException",
    "RemoteProtocolError", "ReadError", "WriteError", "NetworkError",
})


class LLMError(RuntimeError):
    """The model call failed or came back empty."""


@dataclass
class LLMResult:
    text: str
    model: str
    input_tokens: int
    output_tokens: int  # visible answer tokens
    thinking_tokens: int  # hidden reasoning tokens, billed as output
    latency_ms: float


def is_transient(error):
    """True for errors worth a retry: HTTP 429, 500 or 503, or a dropped or unreachable connection."""
    if getattr(error, "code", None) in TRANSIENT_CODES:
        return True
    if isinstance(error, (ConnectionError, TimeoutError)):
        return True
    return any(cls.__name__ in CONNECTION_ERROR_NAMES for cls in type(error).__mro__)


def _load_env():
    try:
        from dotenv import load_dotenv
    except ImportError:  # .env loading is a convenience; real env vars still work
        return
    load_dotenv()


def make_client():
    """Build the Gemini client from GEMINI_API_KEY."""
    _load_env()
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise LLMError("GEMINI_API_KEY is not set. Put it in .env (never in chat or git).")
    from google import genai

    return genai.Client(api_key=key)


def complete(system, user, *, temperature=0.0, max_output_tokens=DEFAULT_MAX_OUTPUT_TOKENS,
             json_output=True, model=None, client=None, retries=2, sleep=time.sleep):
    """One model call. Returns an LLMResult.

    system: instructions (the versioned prompt). user: the question plus context.
    temperature 0 keeps governance answers repeatable. json_output asks Gemini for JSON only.
    client and sleep are injectable so tests run with no network and no waiting.
    Retries only transient errors (429, 500, 503, or a dropped or unreachable connection) with a short
    backoff; anything else is raised.
    """
    if model is None:
        _load_env()
        model = os.environ.get("LLM_MODEL")
    if not model:
        raise LLMError("LLM_MODEL is not set. Put a Gemini model ID in .env.")
    client = client or make_client()

    config = {
        "system_instruction": system,
        "temperature": temperature,
        "max_output_tokens": max_output_tokens,
    }
    if json_output:
        config["response_mime_type"] = "application/json"

    start = time.perf_counter()
    for attempt in range(retries + 1):
        try:
            response = client.models.generate_content(model=model, contents=user, config=config)
            break
        except Exception as error:  # the SDK raises its own APIError with a .code
            if is_transient(error) and attempt < retries:
                sleep(2 * (attempt + 1))
                continue
            raise
    latency_ms = (time.perf_counter() - start) * 1000

    text = response.text
    if not text:
        reason = None
        candidates = getattr(response, "candidates", None)
        if candidates:
            reason = getattr(candidates[0], "finish_reason", None)
        raise LLMError(f"Empty response from {model} (finish_reason={reason}).")

    usage = getattr(response, "usage_metadata", None)
    return LLMResult(
        text=text,
        model=model,
        input_tokens=getattr(usage, "prompt_token_count", 0) or 0,
        output_tokens=getattr(usage, "candidates_token_count", 0) or 0,
        thinking_tokens=getattr(usage, "thoughts_token_count", 0) or 0,
        latency_ms=latency_ms,
    )
