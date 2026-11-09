from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from repermit.api import create_app
from repermit.documents import read_document
from repermit.llm import AssessorUnavailable, ClaudeAssessor, DocumentReading, build_document_prompt, build_prompt, usage_of
from repermit.samples import sample_document, sample_model
from tests.test_documents import PACK, reading
from tests.test_llm import FakeAssessor, review

TYPE = "owner_noc"


class PromptAssessor(FakeAssessor):
    """Remembers the review prompt, to see which document texts reached it."""

    def review(self, state, pack, passages=()):
        self.prompt = build_prompt(state, pack, passages)
        return super().review(state, pack, passages)


class FakeReader:
    model = "fake-reader"
    effort = "low"

    def __init__(self, result):
        self.result = result
        self.calls = 0

    def read_documents(self, state, pack):
        self.calls += 1
        self.prompt = build_document_prompt(state, pack)
        if isinstance(self.result, Exception):
            raise self.result
        return self.result


def reader_result(cost=0.01, **kwargs):
    result = DocumentReading(document_reviews=[reading(TYPE, **kwargs)])
    result._usage = {"model": "claude-haiku-5-5", "input_tokens": 5000, "output_tokens": 300, "cache_read_tokens": 0, "cache_write_tokens": 0, "cost_usd": cost}
    return result


def start(database_url, reader=None, **budgets):
    assessor = PromptAssessor(review("modification"))
    client = TestClient(create_app(database_url, PACK, assessor, document_reader=reader, **budgets))
    case_id = client.post("/demo/scenarios/llm_free_text").json()["case_id"]
    client.post(f"/cases/{case_id}/responses", json={"facts": {"competent_entity": "dda"}})
    client.post(f"/cases/{case_id}/models", content=sample_model("llm_free_text", "proposed"))
    case = SimpleNamespace(client=client, id=case_id, assessor=assessor, reader=reader)
    client.post(f"/cases/{case_id}/documents", params={"type": TYPE, "filename": "noc.pdf"}, content=sample_document("llm_free_text", TYPE))
    case.view = client.post(f"/cases/{case_id}/responses", json={}).json()
    return case


def history(case, kind):
    return [event["payload"] for event in case.client.get(f"/cases/{case.id}/history").json() if event["type"] == kind]


def test_reader_checks_documents_before_the_review(database_url):
    case = start(database_url, FakeReader(reader_result()))
    assert case.reader.calls == 1
    assert '"text"' in case.reader.prompt and TYPE in case.reader.prompt
    verdict = next(item for item in case.view["document_verdicts"] if item["type"] == TYPE)
    assert verdict["status"] == "complete"
    # The review gets the outcome, not the text.
    text = read_document(sample_document("llm_free_text", TYPE))["text"]
    assert text[:80] in case.reader.prompt.replace("\\n", "\n")
    assert '"assessed"' in case.assessor.prompt and text[:80] not in case.assessor.prompt.replace("\\n", "\n")
    [event] = history(case, "llm_documents_read")
    assert event["status"] == "completed" and event["model"] == "fake-reader"


def test_a_failed_reader_leaves_the_documents_to_the_review(database_url):
    case = start(database_url, FakeReader(AssessorUnavailable("rate limited")))
    [event] = history(case, "llm_documents_read")
    assert event["status"] == "unavailable"
    assert '"must_contain"' in case.assessor.prompt


def test_without_a_reader_the_review_reads_documents(database_url):
    case = start(database_url)
    assert history(case, "llm_documents_read") == []
    assert '"must_contain"' in case.assessor.prompt


def test_no_reader_call_without_new_documents(database_url):
    case = start(database_url, FakeReader(reader_result()))
    case.client.post(f"/cases/{case.id}/llm-review")
    assert case.reader.calls == 1


def test_reader_cost_counts_toward_the_budgets(database_url):
    case = start(database_url, FakeReader(reader_result(cost=0.4)))
    assert case.view["llm_cost_usd"] == pytest.approx(0.4)
    store = case.client.app.state.store
    assert store.llm_cost_since("2000-01-01") == pytest.approx(0.4)


def test_meta_shows_a_model_per_task(database_url):
    assessor = ClaudeAssessor("claude-sonnet-5-5", effort="high")
    reader = ClaudeAssessor("claude-haiku-5-5", effort="medium")
    meta = TestClient(create_app(database_url, PACK, assessor, document_reader=reader)).get("/meta").json()
    assert meta["ai"] == {"review": {"model": "claude-sonnet-5-5", "effort": "high"}, "documents": {"model": "claude-haiku-5-5", "effort": "medium"}}
    meta = TestClient(create_app(database_url, PACK, assessor)).get("/meta").json()
    assert meta["ai"]["documents"] is None


def test_unknown_effort_is_refused():
    with pytest.raises(ValueError):
        ClaudeAssessor("claude-haiku-5-5", effort="extreme")


def test_prices_per_model():
    def response(model, prompt, cache_read=0):
        usage = SimpleNamespace(input_tokens=prompt, output_tokens=100_000, cache_read_input_tokens=cache_read, cache_creation_input_tokens=0)
        return SimpleNamespace(model=model, usage=usage)

    assert usage_of(response("claude-haiku-5-5", 100_000))["cost_usd"] == pytest.approx(0.06)
    assert usage_of(response("claude-haiku-5-5", 1_000_000))["cost_usd"] == pytest.approx(0.75)
    assert usage_of(response("claude-opus-5-5", 0, cache_read=1_000_000))["cost_usd"] == pytest.approx(2.2)
